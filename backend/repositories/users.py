from __future__ import annotations

from typing import Any
import asyncpg


async def get_user_by_id(conn: asyncpg.Connection, user_id: int) -> dict[str, Any] | None:
    """Mengambil data pengguna aktif berdasarkan ID."""
    row = await conn.fetchrow(
        """
        SELECT id, name, email, role, activated_at, created_at
        FROM users
        WHERE id = $1 AND deleted_at IS NULL
        """,
        user_id,
    )
    return dict(row) if row else None

