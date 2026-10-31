from __future__ import annotations

import json
from typing import Any
import asyncpg


async def create_session(
    conn: asyncpg.Connection,
    student_id: int,
    scenario_id: int,
    scenario_snapshot: dict[str, Any] | str,
    class_id: int | None = None,
    parent_session_id: int | None = None,
) -> dict[str, Any]:
    """Menyimpan sesi konseling baru ke tabel sessions."""
    snapshot_json = (
        scenario_snapshot
        if isinstance(scenario_snapshot, str)
        else json.dumps(scenario_snapshot)
    )

    row = await conn.fetchrow(
        """
        INSERT INTO sessions (
            student_id, scenario_id, class_id, parent_session_id, scenario_snapshot, status, started_at
        ) VALUES (
            $1, $2, $3, $4, $5::jsonb, 'in_progress', now()
        )
        RETURNING id, student_id, scenario_id, class_id, parent_session_id, scenario_snapshot, status, started_at, ended_at, duration_seconds
        """,
        student_id,
        scenario_id,
        class_id,
        parent_session_id,
        snapshot_json,
    )
    result = dict(row)
    if isinstance(result["scenario_snapshot"], str):
        result["scenario_snapshot"] = json.loads(result["scenario_snapshot"])
    return result


async def get_session_by_id(conn: asyncpg.Connection, session_id: int) -> dict[str, Any] | None:
    """Mengambil data sesi berdasarkan ID."""
    row = await conn.fetchrow(
        """
        SELECT id, student_id, scenario_id, class_id, parent_session_id, scenario_snapshot, status, started_at, ended_at, duration_seconds
        FROM sessions
        WHERE id = $1
        """,
        session_id,
    )
    if not row:
        return None
    res = dict(row)
    if isinstance(res["scenario_snapshot"], str):
        res["scenario_snapshot"] = json.loads(res["scenario_snapshot"])
    return res


async def end_session(conn: asyncpg.Connection, session_id: int) -> dict[str, Any] | None:
    """Mengakhiri sesi konseling: status='completed', ended_at=now(), hitung duration_seconds."""
    row = await conn.fetchrow(
        """
        UPDATE sessions
        SET status = 'completed',
            ended_at = now(),
            duration_seconds = GREATEST(0, EXTRACT(EPOCH FROM (now() - started_at))::integer)
        WHERE id = $1 AND status = 'in_progress'
        RETURNING id, student_id, scenario_id, class_id, parent_session_id, scenario_snapshot, status, started_at, ended_at, duration_seconds
        """,
        session_id,
    )
    if not row:
        return None
    res = dict(row)
    if isinstance(res["scenario_snapshot"], str):
        res["scenario_snapshot"] = json.loads(res["scenario_snapshot"])
    return res

