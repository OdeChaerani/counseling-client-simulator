from __future__ import annotations

from typing import Any
import asyncpg


async def get_next_turn_no(conn: asyncpg.Connection, session_id: int) -> int:
    """Mengambil nomor urut turn berikutnya untuk session_id."""
    val = await conn.fetchval(
        """
        SELECT COALESCE(MAX(turn_no), 0) + 1
        FROM turns
        WHERE session_id = $1
        """,
        session_id,
    )
    return int(val)


async def save_turn(
    conn: asyncpg.Connection,
    session_id: int,
    turn_no: int,
    speaker: str,  # 'counselor' | 'client'
    content: str,
    start_ms: int = 0,
    end_ms: int = 0,
) -> int:
    """Menyimpan satu giliran percakapan ke tabel turns."""
    turn_id = await conn.fetchval(
        """
        INSERT INTO turns (
            session_id, turn_no, speaker, content, start_ms, end_ms
        ) VALUES (
            $1, $2, $3::speaker, $4, $5, $6
        )
        RETURNING id
        """,
        session_id,
        turn_no,
        speaker,
        content,
        start_ms,
        end_ms,
    )
    return int(turn_id)


async def get_session_turns(conn: asyncpg.Connection, session_id: int) -> list[dict[str, Any]]:
    """Mengambil riwayat percakapan sesi konseling secara berurutan."""
    rows = await conn.fetch(
        """
        SELECT id, session_id, turn_no, speaker, content, start_ms, end_ms, created_at
        FROM turns
        WHERE session_id = $1
        ORDER BY turn_no ASC
        """,
        session_id,
    )
    return [dict(r) for r in rows]

