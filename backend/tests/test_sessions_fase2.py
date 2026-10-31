from __future__ import annotations

import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from schemas.session import CreateSessionRequest


class MockTx:
    """Mock asynchronous context manager untuk conn.transaction()."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def run_coro(coro):
    """Menjalankan coroutine murni berbasis mock tanpa menginisialisasi loop socket sistem operasi."""
    stack = [coro]
    val = None
    while stack:
        try:
            curr = stack[-1]
            sub_res = curr.send(val)
            val = None
            if hasattr(sub_res, "send"):
                stack.append(sub_res)
        except StopIteration as e:
            stack.pop()
            val = e.value
    return val


class TestSessionsFase2Unit(unittest.TestCase):
    def setUp(self):
        self.mock_user = {"id": 10, "name": "Mahasiswa Test", "role": "student"}
        self.mock_snapshot = {
            "scenario": {"id": 1, "title": "SS-NAD-01 Nadia Maharani"},
            "persona": {
                "name": "Nadia Maharani",
                "age": 19,
                "gender": "Perempuan",
                "personality": "Menjaga komitmen",
                "communication_style": "Berhati-hati",
            },
            "case": {
                "main_problem": "Nadia kewalahan membagi tanggung jawab.",
                "history_impact": "Tenggat berdekatan, tidur berkurang.",
                "expectation_change_context": "Membagi atau membatasi tanggung jawab tambahan.",
            },
            "initial_state": {
                "emotion_type": "Cemas dan kewalahan",
                "emotion_cause": "Tenggat kuliah dan organisasi",
                "disclosure_level": "guarded",
                "disclosure_trigger": "Awal sesi",
                "reasons_to_change": "Beban berkurang",
                "reasons_to_maintain": "Tetap aktif di organisasi",
                "ambivalence_lean": "both",
                "discord_present": False,
            },
            "hidden_facts": [
                {
                    "code": "H1",
                    "short_title": "Kekhawatiran terhadap penilaian teman",
                    "fact": "Takut dianggap tidak serius.",
                    "sort_order": 1,
                }
            ],
        }

    def test_session_creation_flow_logic(self):
        from api.v1.sessions import create_new_session

        mock_conn = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=MockTx())

        with patch("api.v1.sessions.get_scenario_by_id", new_callable=AsyncMock) as mock_get_scenario, \
             patch("api.v1.sessions.build_scenario_snapshot", new_callable=AsyncMock) as mock_snapshot_fn, \
             patch("api.v1.sessions.create_session", new_callable=AsyncMock) as mock_create_sess, \
             patch("api.v1.sessions.create_session_topics_from_snapshot", new_callable=AsyncMock) as mock_topics, \
             patch("api.v1.sessions.save_client_state", new_callable=AsyncMock) as mock_save_state, \
             patch("api.v1.sessions.save_topic_note", new_callable=AsyncMock) as mock_save_note:

            mock_get_scenario.return_value = {
                "id": 1,
                "title": "SS-NAD-01 Nadia Maharani",
                "visibility": "catalog",
            }
            mock_snapshot_fn.return_value = self.mock_snapshot
            mock_create_sess.return_value = {
                "id": 101,
                "student_id": 10,
                "scenario_id": 1,
                "class_id": None,
                "parent_session_id": None,
                "scenario_snapshot": self.mock_snapshot,
                "status": "in_progress",
                "started_at": datetime.now(),
                "ended_at": None,
                "duration_seconds": None,
            }
            mock_topics.return_value = [
                {"id": 1, "name": "Permasalahan utama"},
                {"id": 2, "name": "Riwayat dan dampak masalah"},
                {"id": 3, "name": "Harapan dan arah perubahan"},
                {"id": 4, "name": "Kekhawatiran terhadap penilaian teman"},
            ]

            payload = CreateSessionRequest(scenario_id=1, mode="new")
            result = run_coro(create_new_session(payload=payload, user=self.mock_user, conn=mock_conn))

            self.assertEqual(result["id"], 101)
            self.assertEqual(result["status"], "in_progress")
            # Pastikan snapshot diambil dan sesi dibuat
            mock_snapshot_fn.assert_awaited_once_with(mock_conn, 1)
            mock_create_sess.assert_awaited_once()
            # Pastikan 4 catatan topik awal dibuat
            self.assertEqual(mock_save_note.await_count, 4)
            # Pastikan baris awal state disimpan dengan turn_id=None
            mock_save_state.assert_awaited_once_with(
                mock_conn, 101, turn_id=None, state=self.mock_snapshot["initial_state"]
            )

    def test_session_continue_mode_logic(self):
        from api.v1.sessions import create_new_session

        mock_conn = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=MockTx())

        parent_latest_state = {
            "emotion_type": "Cemas tetapi lebih terarah",
            "disclosure_level": "medium",
            "ambivalence_lean": "both",
            "discord_present": False,
        }

        with patch("api.v1.sessions.get_scenario_by_id", new_callable=AsyncMock) as mock_get_scenario, \
             patch("api.v1.sessions.get_session_by_id", new_callable=AsyncMock) as mock_get_parent, \
             patch("api.v1.sessions.build_scenario_snapshot", new_callable=AsyncMock) as mock_snapshot_fn, \
             patch("api.v1.sessions.create_session", new_callable=AsyncMock) as mock_create_sess, \
             patch("api.v1.sessions.create_session_topics_from_snapshot", new_callable=AsyncMock) as mock_topics, \
             patch("api.v1.sessions.get_latest_client_state", new_callable=AsyncMock) as mock_get_state, \
             patch("api.v1.sessions.save_client_state", new_callable=AsyncMock) as mock_save_state, \
             patch("api.v1.sessions.copy_topic_notes_from_parent", new_callable=AsyncMock) as mock_copy_notes:

            mock_get_scenario.return_value = {
                "id": 1,
                "title": "SS-NAD-01 Nadia Maharani",
                "visibility": "catalog",
            }
            mock_get_parent.return_value = {
                "id": 101,
                "student_id": 10,
                "scenario_id": 1,
                "status": "completed",
            }
            mock_snapshot_fn.return_value = self.mock_snapshot
            mock_create_sess.return_value = {
                "id": 102,
                "student_id": 10,
                "scenario_id": 1,
                "class_id": None,
                "parent_session_id": 101,
                "scenario_snapshot": self.mock_snapshot,
                "status": "in_progress",
                "started_at": datetime.now(),
                "ended_at": None,
                "duration_seconds": None,
            }
            mock_topics.return_value = [{"id": 1, "name": "Permasalahan utama"}]
            mock_get_state.return_value = parent_latest_state

            payload = CreateSessionRequest(scenario_id=1, mode="continue", parent_session_id=101)
            result = run_coro(create_new_session(payload=payload, user=self.mock_user, conn=mock_conn))

            self.assertEqual(result["id"], 102)
            self.assertEqual(result["parent_session_id"], 101)
            # Pastikan state akhir parent disalin ke sesi baru
            mock_save_state.assert_awaited_once_with(
                mock_conn, 102, turn_id=None, state=parent_latest_state
            )
            # Pastikan catatan topik disalin dari parent session 101 ke 102
            mock_copy_notes.assert_awaited_once_with(mock_conn, 101, 102)

    def test_end_session_logic(self):
        from api.v1.sessions import end_active_session

        mock_conn = AsyncMock()

        with patch("api.v1.sessions.get_session_by_id", new_callable=AsyncMock) as mock_get_sess, \
             patch("api.v1.sessions.end_session", new_callable=AsyncMock) as mock_end_sess:

            mock_get_sess.return_value = {
                "id": 101,
                "student_id": 10,
                "status": "in_progress",
                "started_at": datetime.now(),
                "ended_at": None,
                "duration_seconds": None,
            }
            mock_end_sess.return_value = {
                "id": 101,
                "status": "completed",
                "duration_seconds": 620,
                "ended_at": datetime.now(),
            }

            result = run_coro(end_active_session(session_id=101, user=self.mock_user, conn=mock_conn))
            self.assertEqual(result["id"], 101)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["duration_seconds"], 620)
            mock_end_sess.assert_awaited_once_with(mock_conn, 101)
