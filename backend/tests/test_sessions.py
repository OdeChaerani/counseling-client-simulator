from __future__ import annotations

from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from api.v1.sessions import create_new_session, end_active_session, get_session_detail
from schemas.session import CreateSessionRequest
from tests.base import BaseTestCase


class TestSessions(BaseTestCase):
    """Pengujian Unit & Integrasi Siklus Hidup Sesi Konseling (Sessions API)."""

    def setUp(self):
        super().setUp()
        self.mock_user = self.get_sample_user(user_id=10, role="student")
        self.mock_conn = self.create_mock_connection()
        self.snapshot = self.get_sample_snapshot()

    @patch("api.v1.sessions.get_scenario_by_id")
    @patch("api.v1.sessions.build_scenario_snapshot")
    @patch("api.v1.sessions.create_session")
    @patch("api.v1.sessions.create_session_topics_from_snapshot")
    @patch("api.v1.sessions.save_client_state")
    @patch("api.v1.sessions.save_topic_note")
    def test_create_session_success(
        self,
        mock_save_note,
        mock_save_state,
        mock_create_topics,
        mock_create_sess,
        mock_build_snap,
        mock_get_scen,
    ):
        """Memastikan pembuatan sesi latihan mandiri baru menginisialisasi snapshot, topik, dan initial state."""
        mock_get_scen.return_value = {
            "id": 1,
            "scenario_code": "SS-NAD-01",
            "visibility": "catalog",
        }
        mock_build_snap.return_value = self.snapshot
        mock_create_sess.return_value = {
            "id": 101,
            "student_id": 10,
            "scenario_id": 1,
            "class_id": None,
            "parent_session_id": None,
            "scenario_snapshot": self.snapshot,
            "status": "in_progress",
            "started_at": "2026-10-31T10:00:00Z",
            "ended_at": None,
            "duration_seconds": None,
        }
        mock_create_topics.return_value = [
            {"id": 1, "name": "Permasalahan utama"},
            {"id": 2, "name": "Riwayat dan dampak"},
        ]

        payload = CreateSessionRequest(scenario_id=1, mode="new")
        res = self.run_async(
            create_new_session(
                payload=payload,
                user=self.mock_user,
                conn=self.mock_conn,
            )
        )

        self.assertEqual(res["id"], 101)
        self.assertEqual(res["status"], "in_progress")
        mock_save_state.assert_called_once_with(
            self.mock_conn, 101, turn_id=None, state=self.snapshot["initial_state"]
        )
        self.assertEqual(mock_save_note.call_count, 2)

    @patch("api.v1.sessions.get_scenario_by_id")
    def test_create_session_catalog_access_denied(self, mock_get_scen):
        """Memastikan latihan mandiri ditolak jika skenario bukan berstatus katalog umum."""
        mock_get_scen.return_value = {
            "id": 1,
            "scenario_code": "SS-NAD-01",
            "visibility": "class",
        }

        payload = CreateSessionRequest(scenario_id=1, mode="new")
        with self.assertRaises(HTTPException) as ctx:
            self.run_async(
                create_new_session(
                    payload=payload,
                    user=self.mock_user,
                    conn=self.mock_conn,
                )
            )
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("katalog", ctx.exception.detail)

    @patch("api.v1.sessions.get_scenario_by_id")
    @patch("api.v1.sessions.get_session_by_id")
    @patch("api.v1.sessions.build_scenario_snapshot")
    @patch("api.v1.sessions.create_session")
    @patch("api.v1.sessions.create_session_topics_from_snapshot")
    @patch("api.v1.sessions.get_latest_client_state")
    @patch("api.v1.sessions.save_client_state")
    @patch("api.v1.sessions.copy_topic_notes_from_parent")
    def test_create_session_continue_mode_inheritance(
        self,
        mock_copy_notes,
        mock_save_state,
        mock_get_latest_state,
        mock_create_topics,
        mock_create_sess,
        mock_build_snap,
        mock_get_parent_sess,
        mock_get_scen,
    ):
        """Memastikan mode continue mewarisi kondisi akhir dan catatan topik dari sesi sebelumnya."""
        parent_final_state = {
            "emotion_type": "Lega",
            "disclosure_level": "medium",
            "ambivalence_lean": "toward_change",
            "discord_present": False,
        }

        mock_get_scen.return_value = {
            "id": 1,
            "scenario_code": "SS-NAD-01",
            "visibility": "catalog",
        }
        mock_get_parent_sess.return_value = {
            "id": 101,
            "student_id": 10,
            "scenario_id": 1,
            "status": "completed",
        }
        mock_build_snap.return_value = self.snapshot
        mock_create_sess.return_value = {
            "id": 102,
            "student_id": 10,
            "scenario_id": 1,
            "class_id": None,
            "parent_session_id": 101,
            "scenario_snapshot": self.snapshot,
            "status": "in_progress",
            "started_at": "2026-10-31T11:00:00Z",
            "ended_at": None,
            "duration_seconds": None,
        }
        mock_create_topics.return_value = [{"id": 1, "name": "Topik 1"}]
        mock_get_latest_state.return_value = parent_final_state

        payload = CreateSessionRequest(
            scenario_id=1, mode="continue", parent_session_id=101
        )
        res = self.run_async(
            create_new_session(
                payload=payload,
                user=self.mock_user,
                conn=self.mock_conn,
            )
        )

        self.assertEqual(res["id"], 102)
        self.assertEqual(res["parent_session_id"], 101)
        mock_save_state.assert_called_once_with(
            self.mock_conn, 102, turn_id=None, state=parent_final_state
        )
        mock_copy_notes.assert_called_once_with(self.mock_conn, 101, 102)

    @patch("api.v1.sessions.get_session_by_id")
    @patch("api.v1.sessions.get_session_turns")
    @patch("api.v1.sessions.get_latest_topic_notes")
    def test_get_session_detail_success(
        self, mock_get_notes, mock_get_turns, mock_get_sess
    ):
        """Memastikan detail sesi mengembalikan data sesi beserta riwayat turns dan topik."""
        mock_sess = self.get_sample_session(session_id=101, student_id=10)
        mock_get_sess.return_value = mock_sess
        mock_get_turns.return_value = [
            {"id": 1, "turn_no": 1, "speaker": "counselor", "content": "Halo"},
            {"id": 2, "turn_no": 2, "speaker": "client", "content": "Hai"},
        ]
        mock_get_notes.return_value = [
            {"topic_name": "Permasalahan utama", "description": "Catatan..."}
        ]

        detail = self.run_async(
            get_session_detail(session_id=101, user=self.mock_user, conn=self.mock_conn)
        )

        self.assertEqual(detail["id"], 101)
        self.assertEqual(len(detail["turns"]), 2)
        self.assertEqual(len(detail["topics"]), 1)

    @patch("api.v1.sessions.get_session_by_id")
    @patch("api.v1.sessions.end_session")
    def test_end_session_success(self, mock_end_sess, mock_get_sess):
        """Memastikan pengakhiran sesi mengupdate status menjadi completed dan menghitung durasi."""
        mock_sess = self.get_sample_session(
            session_id=101, student_id=10, status="in_progress"
        )
        mock_get_sess.return_value = mock_sess
        mock_end_sess.return_value = {
            "id": 101,
            "status": "completed",
            "duration_seconds": 540,
            "ended_at": "2026-10-31T10:45:00Z",
        }

        res = self.run_async(
            end_active_session(
                session_id=101, user=self.mock_user, conn=self.mock_conn
            )
        )

        self.assertEqual(res["id"], 101)
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["duration_seconds"], 540)

