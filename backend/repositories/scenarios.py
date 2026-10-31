from __future__ import annotations

import json
from typing import Any
import asyncpg


async def get_scenario_by_id(conn: asyncpg.Connection, scenario_id: int) -> dict[str, Any] | None:
    """Mengambil metadata skenario yang belum dihapus."""
    row = await conn.fetchrow(
        """
        SELECT id, title, owner_id, visibility, review_status, change_target, created_at, updated_at
        FROM scenarios
        WHERE id = $1 AND deleted_at IS NULL
        """,
        scenario_id,
    )
    return dict(row) if row else None


async def build_scenario_snapshot(conn: asyncpg.Connection, scenario_id: int) -> dict[str, Any] | None:
    """Memanggil fungsi SQL build_scenario_snapshot(:scenario_id) untuk menghasilkan snapshot JSONB."""
    val = await conn.fetchval(
        "SELECT build_scenario_snapshot($1)",
        scenario_id,
    )
    if not val:
        return None
    if isinstance(val, str):
        return json.loads(val)
    return dict(val)


async def validate_catalog_access(conn: asyncpg.Connection, scenario_id: int) -> bool:
    """Validasi apakah skenario tersedia di katalog umum untuk latihan mandiri."""
    row = await conn.fetchrow(
        """
        SELECT 1 FROM scenarios
        WHERE id = $1 AND visibility = 'catalog' AND deleted_at IS NULL
        """,
        scenario_id,
    )
    return row is not None


async def validate_class_access(
    conn: asyncpg.Connection, scenario_id: int, class_id: int, student_id: int
) -> bool:
    """Validasi apakah skenario ditugaskan pada kelas dan mahasiswa terdaftar di kelas tersebut."""
    row = await conn.fetchrow(
        """
        SELECT 1
        FROM class_scenarios cs
        JOIN class_members cm ON cm.class_id = cs.class_id
        JOIN classes cl ON cl.id = cs.class_id
        JOIN scenarios sc ON sc.id = cs.scenario_id
        WHERE cs.scenario_id = $1
          AND cs.class_id = $2
          AND cm.user_id = $3
          AND cl.deleted_at IS NULL
          AND sc.deleted_at IS NULL
        """,
        scenario_id,
        class_id,
        student_id,
    )
    return row is not None

