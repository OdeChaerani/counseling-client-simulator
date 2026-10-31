from __future__ import annotations

from typing import Any
import asyncpg


async def create_session_topics_from_snapshot(
    conn: asyncpg.Connection, session_id: int, snapshot: dict[str, Any]
) -> list[dict[str, Any]]:
    """Membuat daftar session_topics tetap di awal sesi dari isi kasus dan hidden facts."""
    topics_to_insert: list[tuple[int, str, str, str | None]] = []
    order = 1

    case_info = snapshot.get("case", {})
    # 1. Permasalahan utama
    if case_info.get("main_problem"):
        topics_to_insert.append((order, "Permasalahan utama", "main_problem", None))
        order += 1

    # 2. Riwayat dan dampak masalah
    if case_info.get("history_impact"):
        topics_to_insert.append((order, "Riwayat dan dampak masalah", "history_impact", None))
        order += 1

    # 3. Harapan dan arah perubahan
    if case_info.get("expectation_change_context"):
        topics_to_insert.append((order, "Harapan dan arah perubahan", "expectation_change_context", None))
        order += 1

    # 4. Hidden facts (satu topik per hidden fact dengan judul singkat)
    hidden_facts = snapshot.get("hidden_facts", [])
    for hf in hidden_facts:
        short_title = hf.get("short_title", hf.get("code", f"Fakta {order}"))
        topics_to_insert.append((order, short_title, "hidden_fact", hf.get("code")))
        order += 1

    created_topics = []
    for sort_order, name, source, code in topics_to_insert:
        row = await conn.fetchrow(
            """
            INSERT INTO session_topics (
                session_id, sort_order, name, source, hidden_fact_code
            ) VALUES (
                $1, $2, $3, $4::topic_source, $5
            )
            RETURNING id, session_id, sort_order, name, source, hidden_fact_code
            """,
            session_id,
            sort_order,
            name,
            source,
            code,
        )
        created_topics.append(dict(row))

    return created_topics


async def get_session_topics(
    conn: asyncpg.Connection, session_id: int
) -> list[dict[str, Any]]:
    """Mengambil daftar topik tetap dari session_id."""
    rows = await conn.fetch(
        """
        SELECT id, session_id, sort_order, name, source, hidden_fact_code
        FROM session_topics
        WHERE session_id = $1
        ORDER BY sort_order ASC
        """,
        session_id,
    )
    return [dict(r) for r in rows]


async def save_topic_note(
    conn: asyncpg.Connection,
    session_topic_id: int,
    turn_id: int | None,
    description: str,
) -> int:
    """Menyimpan catatan pembaruan topik ke topic_notes_log."""
    note_id = await conn.fetchval(
        """
        INSERT INTO topic_notes_log (
            session_topic_id, turn_id, description
        ) VALUES (
            $1, $2, $3
        )
        RETURNING id
        """,
        session_topic_id,
        turn_id,
        description,
    )
    return int(note_id)


async def get_latest_topic_notes(
    conn: asyncpg.Connection, session_id: int
) -> list[dict[str, Any]]:
    """Mengambil catatan deskripsi terkini per topik (baris terbaru per topic_id)."""
    rows = await conn.fetch(
        """
        SELECT DISTINCT ON (st.id)
            st.id AS session_topic_id,
            st.sort_order,
            st.name AS topic_name,
            st.source,
            st.hidden_fact_code,
            COALESCE(tnl.description, '') AS description,
            tnl.turn_id
        FROM session_topics st
        LEFT JOIN topic_notes_log tnl ON tnl.session_topic_id = st.id
        WHERE st.session_id = $1
        ORDER BY st.id, tnl.id DESC NULLS LAST
        """,
        session_id,
    )
    # Urutkan berdasarkan sort_order untuk pembacaan LLM yang konsisten
    sorted_rows = sorted(rows, key=lambda r: r["sort_order"])
    return [dict(r) for r in sorted_rows]


async def copy_topic_notes_from_parent(
    conn: asyncpg.Connection, parent_session_id: int, new_session_id: int
) -> None:
    """Menyalin catatan deskripsi topik terakhir dari parent session ke sesi baru (mode continue)."""
    parent_notes = await get_latest_topic_notes(conn, parent_session_id)
    new_topics = await get_session_topics(conn, new_session_id)

    # Petakan nama topik ke session_topic_id di sesi baru
    new_topic_map = {t["name"]: t["id"] for t in new_topics}
    copied_topic_ids = set()

    for note in parent_notes:
        topic_name = note["topic_name"]
        new_topic_id = new_topic_map.get(topic_name)
        if new_topic_id:
            desc = note.get("description", "")
            await save_topic_note(conn, new_topic_id, turn_id=None, description=desc)
            copied_topic_ids.add(new_topic_id)

    # Jika ada topik di sesi baru yang belum ada di parent (misal skenario diperluas), isi dengan string kosong
    for topic in new_topics:
        if topic["id"] not in copied_topic_ids:
            await save_topic_note(conn, topic["id"], turn_id=None, description="")
