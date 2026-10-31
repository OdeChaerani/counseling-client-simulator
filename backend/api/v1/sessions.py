from __future__ import annotations

from typing import Any
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_current_user, get_db, verify_session_ownership
from core.errors import LLMServiceError
from repositories.client_state import get_latest_client_state, save_client_state
from repositories.scenarios import (
    build_scenario_snapshot,
    get_scenario_by_id,
    validate_class_access,
)
from repositories.sessions import create_session, end_session, get_session_by_id
from repositories.topics import (
    copy_topic_notes_from_parent,
    create_session_topics_from_snapshot,
    get_latest_topic_notes,
    save_topic_note,
)
from repositories.turns import get_session_turns
from schemas.session import (
    CreateSessionRequest,
    CreateTurnRequest,
    EndSessionResponse,
    SessionResponse,
    TurnResponse,
)
from services.simulation.orchestrator import get_session_lock, process_turn

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_session(
    payload: CreateSessionRequest,
    user: dict[str, Any] = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> Any:
    """Membuat sesi simulasi konseling baru (new, repeat, atau continue) dalam SATU transaksi atomik."""
    async with conn.transaction():
        # 1. Validasi Keberadaan Skenario
        scenario = await get_scenario_by_id(conn, payload.scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skenario dengan ID {payload.scenario_id} tidak ditemukan.",
            )

        # 1a. Validasi Akses Latihan Mandiri vs Latihan Kelas
        if payload.class_id is None:
            # Latihan mandiri: skenario harus berkatalog umum
            if scenario["visibility"] != "catalog":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Latihan mandiri hanya diizinkan untuk skenario yang tersedia di katalog umum.",
                )
        else:
            # Latihan kelas: periksa keanggotaan kelas dan penugasan skenario
            has_access = await validate_class_access(
                conn, payload.scenario_id, payload.class_id, user["id"]
            )
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Anda tidak memiliki izin untuk mengakses skenario pada kelas ini.",
                )

        # 1b. Validasi Khusus Mode Continue
        if payload.mode == "continue":
            if not payload.parent_session_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="parent_session_id wajib disertakan untuk mode continue.",
                )
            parent_session = await get_session_by_id(conn, payload.parent_session_id)
            if not parent_session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sesi sebelumnya (parent session) tidak ditemukan.",
                )
            if parent_session["student_id"] != user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Sesi lanjutan harus melanjutkan sesi milik Anda sendiri.",
                )
            if parent_session["scenario_id"] != payload.scenario_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Skenario pada sesi lanjutan harus identik dengan sesi sebelumnya.",
                )

        # 2. Ambil Snapshot Skenario yang Dibekukan
        snapshot = await build_scenario_snapshot(conn, payload.scenario_id)
        if not snapshot:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal menyusun snapshot skenario dari database.",
            )

        # 3. Buat Rekaman Sesi Baru
        parent_id = payload.parent_session_id if payload.mode == "continue" else None
        session_record = await create_session(
            conn=conn,
            student_id=user["id"],
            scenario_id=payload.scenario_id,
            scenario_snapshot=snapshot,
            class_id=payload.class_id,
            parent_session_id=parent_id,
        )
        new_session_id = session_record["id"]

        # 4. Inisialisasi Topik Pembahasan (session_topics)
        created_topics = await create_session_topics_from_snapshot(
            conn, new_session_id, snapshot
        )

        # 5. Isi State Awal dan Catatan Topik Awal
        if payload.mode in ("new", "repeat"):
            initial_state = snapshot["initial_state"]
            await save_client_state(conn, new_session_id, turn_id=None, state=initial_state)
            for topic in created_topics:
                await save_topic_note(conn, topic["id"], turn_id=None, description="")
        elif payload.mode == "continue":
            assert payload.parent_session_id is not None
            # Salin state akhir milik parent session
            parent_latest_state = await get_latest_client_state(conn, payload.parent_session_id)
            if not parent_latest_state:
                parent_latest_state = snapshot["initial_state"]
            await save_client_state(conn, new_session_id, turn_id=None, state=parent_latest_state)

            # Salin catatan topik terakhir dari parent session
            await copy_topic_notes_from_parent(conn, payload.parent_session_id, new_session_id)

        return session_record


@router.get("/{session_id}")
async def get_session_detail(
    session_id: int,
    user: dict[str, Any] = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    """Mengambil detail sesi konseling, riwayat turns, dan topik pembahasan."""
    session = await get_session_by_id(conn, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sesi dengan ID {session_id} tidak ditemukan.",
        )

    verify_session_ownership(session, user)

    turns = await get_session_turns(conn, session_id)
    topics = await get_latest_topic_notes(conn, session_id)

    return {
        **session,
        "turns": turns,
        "topics": topics,
    }


@router.post("/{session_id}/turns", response_model=TurnResponse)
async def send_counselor_turn(
    session_id: int,
    payload: CreateTurnRequest,
    user: dict[str, Any] = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> Any:
    """Mengirim giliran ucapan konselor dan menerima respons klien virtual."""
    session = await get_session_by_id(conn, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sesi dengan ID {session_id} tidak ditemukan.",
        )

    verify_session_ownership(session, user)

    if session["status"] == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sesi latihan ini sudah selesai dan tidak dapat menerima giliran percakapan baru.",
        )

    lock = await get_session_lock(session_id)
    async with lock:
        # Validasi ulang status sesi setelah memperoleh lock
        current_session = await get_session_by_id(conn, session_id)
        if current_session and current_session["status"] == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sesi latihan ini sudah selesai dan tidak dapat menerima giliran percakapan baru.",
            )

        try:
            return await process_turn(
                conn=conn,
                session=session,
                counselor_utterance=payload.content,
                start_ms=payload.start_ms,
                end_ms=payload.end_ms,
            )
        except LLMServiceError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Layanan simulasi sedang mengalami kendala teknis: {exc}",
            ) from exc


@router.post("/{session_id}/end", response_model=EndSessionResponse)
async def end_active_session(
    session_id: int,
    user: dict[str, Any] = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> Any:
    """Mengakhiri sesi konseling (status='completed', mencatat ended_at dan duration_seconds)."""
    session = await get_session_by_id(conn, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sesi dengan ID {session_id} tidak ditemukan.",
        )

    verify_session_ownership(session, user)

    if session["status"] == "completed":
        return {
            "id": session["id"],
            "status": session["status"],
            "duration_seconds": session["duration_seconds"],
            "ended_at": session["ended_at"] or session["started_at"],
        }

    updated = await end_session(conn, session_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memperbarui status sesi menjadi selesai.",
        )

    return {
        "id": updated["id"],
        "status": updated["status"],
        "duration_seconds": updated["duration_seconds"],
        "ended_at": updated["ended_at"],
    }
