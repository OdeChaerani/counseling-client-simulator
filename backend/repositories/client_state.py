from __future__ import annotations

from typing import Any
import asyncpg


async def save_client_state(
    conn: asyncpg.Connection,
    session_id: int,
    turn_id: int | None,
    state: dict[str, Any],
) -> int:
    """Menyimpan record ke tabel client_state_log. turn_id NULL untuk initial state."""
    state_id = await conn.fetchval(
        """
        INSERT INTO client_state_log (
            session_id, turn_id, emotion_type, emotion_cause, disclosure_level,
            disclosure_trigger, reasons_to_change, reasons_to_maintain,
            ambivalence_lean, discord_present, discord_context, discord_response
        ) VALUES (
            $1, $2, $3, $4, $5::disclosure_level,
            $6, $7, $8,
            $9::ambivalence_lean, $10, $11, $12
        )
        RETURNING id
        """,
        session_id,
        turn_id,
        state["emotion_type"],
        state.get("emotion_cause"),
        state["disclosure_level"],
        state.get("disclosure_trigger"),
        state.get("reasons_to_change"),
        state.get("reasons_to_maintain"),
        state["ambivalence_lean"],
        bool(state.get("discord_present", False)),
        state.get("discord_context"),
        state.get("discord_response"),
    )
    return int(state_id)


async def get_latest_client_state(
    conn: asyncpg.Connection, session_id: int
) -> dict[str, Any] | None:
    """Mengambil record Client State paling mutakhir dari session_id."""
    row = await conn.fetchrow(
        """
        SELECT id, session_id, turn_id, emotion_type, emotion_cause,
               disclosure_level, disclosure_trigger, reasons_to_change,
               reasons_to_maintain, ambivalence_lean, discord_present,
               discord_context, discord_response, created_at
        FROM client_state_log
        WHERE session_id = $1
        ORDER BY (turn_id IS NOT NULL) ASC, id DESC
        LIMIT 1
        """,
        session_id,
    )
    return dict(row) if row else None

