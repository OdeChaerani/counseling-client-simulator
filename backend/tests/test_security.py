from __future__ import annotations

from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from api.v1.sessions import get_session_detail, send_counselor_turn
from schemas.session import CreateTurnRequest
from tests.base import BaseTestCase


class TestSecurity(BaseTestCase):
    """Pengujian Keamanan, Hak Akses Multi-Tenant, dan Perlindungan Kerahasiaan State."""

    def setUp(self):
        super().setUp()
        self.student_a = self.get_sample_user(
            user_id=101, role="student", name="Mahasiswa A"
        )
        self.student_b = self.get_sample_user(
            user_id=102, role="student", name="Mahasiswa B"
        )
        self.lecturer = self.get_sample_user(
            user_id=201, role="lecturer", name="Dosen Pembimbing"
        )
        self.mock_conn = self.create_mock_connection()
        self.session_a = self.get_sample_session(session_id=501, student_id=101)

    def test_student_cannot_access_other_student_session(self):
        """Memastikan Mahasiswa B ditolak (HTTP 403) saat membaca sesi Mahasiswa A."""
        self.mock_conn.fetchrow.return_value = self.session_a

        with self.assertRaises(HTTPException) as ctx:
            self.run_async(
                get_session_detail(
                    session_id=501,
                    user=self.student_b,
                    conn=self.mock_conn,
                )
            )
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("izin", ctx.exception.detail)

    def test_student_cannot_post_turn_to_other_student_session(self):
        """Memastikan Mahasiswa B ditolak (HTTP 403) saat mengirim giliran ke sesi Mahasiswa A."""
        self.mock_conn.fetchrow.return_value = self.session_a
        payload = CreateTurnRequest(content="Halo Nadia")

        with self.assertRaises(HTTPException) as ctx:
            self.run_async(
                send_counselor_turn(
                    session_id=501,
                    payload=payload,
                    user=self.student_b,
                    conn=self.mock_conn,
                )
            )
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("izin", ctx.exception.detail)

    @patch("api.v1.sessions.get_session_turns")
    @patch("api.v1.sessions.get_latest_topic_notes")
    def test_lecturer_review_access_permitted(self, mock_notes, mock_turns):
        """Memastikan Dosen/Admin diizinkan meninjau sesi mahasiswa (Review access)."""
        self.mock_conn.fetchrow.return_value = self.session_a
        mock_turns.return_value = []
        mock_notes.return_value = []

        res = self.run_async(
            get_session_detail(
                session_id=501,
                user=self.lecturer,
                conn=self.mock_conn,
            )
        )
        self.assertEqual(res["id"], 501)
        self.assertEqual(res["student_id"], 101)

