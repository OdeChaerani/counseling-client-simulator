from __future__ import annotations

from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from api.v1.sessions import send_counselor_turn
from core.errors import LLMServiceError
from schemas.client_state import ClientState
from schemas.session import CreateTurnRequest
from services.simulation.notes_updater import TopicNoteUpdate
from services.simulation.orchestrator import get_session_lock
from services.simulation.responder import generate_client_response_llm
from tests.base import BaseTestCase


class TestTurns(BaseTestCase):
    """Pengujian Unit & Integrasi Alur Giliran Percakapan (Turns Conversation Pipeline)."""

    def setUp(self):
        super().setUp()
        self.mock_user = self.get_sample_user(user_id=10, role="student")
        self.mock_conn = self.create_mock_connection()
        self.mock_session = self.get_sample_session(session_id=100, student_id=10)

    def test_empty_content_validation(self):
        """Memastikan CreateTurnRequest menolak konten kosong atau hanya spasi."""
        with self.assertRaises(ValueError):
            CreateTurnRequest(content="   ")

    def test_session_lock_serialization(self):
        """Memastikan get_session_lock mengembalikan lock yang sama untuk sesi yang sama."""
        lock1 = self.run_async(get_session_lock(100))
        lock2 = self.run_async(get_session_lock(100))
        lock3 = self.run_async(get_session_lock(200))

        self.assertIs(lock1, lock2)
        self.assertIsNot(lock1, lock3)

    @patch("services.simulation.orchestrator.get_latest_client_state")
    @patch("services.simulation.orchestrator.get_latest_topic_notes")
    @patch("services.simulation.orchestrator.get_session_turns")
    @patch("services.simulation.orchestrator.save_turn")
    @patch("services.simulation.orchestrator.save_client_state")
    @patch("services.simulation.orchestrator.get_next_turn_no")
    def test_greeting_shortcut_bypasses_llm(
        self,
        mock_get_next_no,
        mock_save_state,
        mock_save_turn,
        mock_get_turns,
        mock_get_notes,
        mock_get_state,
    ):
        """Memastikan shortcut sapaan langsung membalas sapaan tanpa memanggil LLM."""
        self.mock_conn.fetchrow.return_value = self.mock_session
        mock_get_state.return_value = self.mock_session["scenario_snapshot"][
            "initial_state"
        ]
        mock_get_notes.return_value = []
        mock_get_turns.return_value = []
        mock_get_next_no.return_value = 1
        mock_save_turn.side_effect = [1, 2]

        payload = CreateTurnRequest(
            content="Halo selamat pagi Nadia, apa kabar hari ini?"
        )
        res = self.run_async(
            send_counselor_turn(
                session_id=100,
                payload=payload,
                user=self.mock_user,
                conn=self.mock_conn,
            )
        )

        self.assertEqual(res.turn_no, 2)
        self.assertIn("Nadia", res.content)
        self.assertIsNone(res.internal_state)
        self.assertEqual(mock_save_turn.call_count, 2)
        mock_save_state.assert_called_once()

    @patch("services.simulation.orchestrator.update_client_state_llm")
    @patch("services.simulation.orchestrator.generate_client_response_llm")
    @patch("services.simulation.orchestrator.update_topic_notes_llm")
    @patch("services.simulation.orchestrator.get_latest_client_state")
    @patch("services.simulation.orchestrator.get_latest_topic_notes")
    @patch("services.simulation.orchestrator.get_session_turns")
    @patch("services.simulation.orchestrator.save_turn")
    @patch("services.simulation.orchestrator.save_client_state")
    @patch("services.simulation.orchestrator.save_topic_note")
    @patch("services.simulation.orchestrator.get_next_turn_no")
    def test_substantive_turn_orchestration(
        self,
        mock_get_next_no,
        mock_save_note,
        mock_save_state,
        mock_save_turn,
        mock_get_turns,
        mock_get_notes,
        mock_get_state,
        mock_notes_llm,
        mock_resp_llm,
        mock_state_llm,
    ):
        """Memastikan aliran turn substantif memanggil Peran A, B, C dan mengosongkan hidden facts saat guarded."""
        self.mock_conn.fetchrow.return_value = self.mock_session
        mock_get_state.return_value = self.mock_session["scenario_snapshot"][
            "initial_state"
        ]
        mock_get_notes.return_value = [
            {
                "session_topic_id": 501,
                "topic_name": "Permasalahan utama",
                "description": "",
            }
        ]
        mock_get_turns.return_value = []
        mock_get_next_no.return_value = 1
        mock_save_turn.side_effect = [10, 11]

        updated_state = ClientState(
            emotion_type="Cemas",
            emotion_cause="Tenggat kuliah mendekat",
            disclosure_level="guarded",
            disclosure_trigger="Pertanyaan konselor",
            reasons_to_change="Ingin lega",
            reasons_to_maintain="Takut dinilai",
            ambivalence_lean="both",
            discord_present=False,
        )
        mock_state_llm.return_value = updated_state
        mock_resp_llm.return_value = (
            "Iya, tugas kuliah dan kegiatan himpunan menyita waktu."
        )
        mock_notes_llm.return_value = [
            TopicNoteUpdate(
                topic_name="Permasalahan utama",
                description="Klien mengonfirmasi kesibukan tugas dan kegiatan.",
            )
        ]

        payload = CreateTurnRequest(
            content="Bisa ceritakan apa yang paling membebani pikiranmu saat ini?"
        )
        res = self.run_async(
            send_counselor_turn(
                session_id=100,
                payload=payload,
                user=self.mock_user,
                conn=self.mock_conn,
            )
        )

        self.assertEqual(res.turn_no, 2)
        self.assertIn("tugas kuliah", res.content)
        self.assertIsNone(res.internal_state)
        mock_state_llm.assert_called_once()
        mock_resp_llm.assert_called_once()
        self.assertEqual(mock_save_turn.call_count, 2)
        mock_save_state.assert_called_once()
        mock_save_note.assert_called_once()

    def test_responder_code_level_boundary_guarded(self):
        """Memastikan responder.py memfilter hidden facts menjadi kosong jika disclosure_level == 'guarded'."""
        guarded_state = ClientState(
            emotion_type="Ragu",
            disclosure_level="guarded",
            ambivalence_lean="both",
            discord_present=False,
        )
        hidden_facts = [{"code": "H1", "description": "Fakta sensitif"}]

        with patch("services.simulation.responder.get_gemini_client") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.generate_text.return_value = "Saya rasa biasa saja."
            mock_get_llm.return_value = mock_llm

            self.run_async(
                generate_client_response_llm(
                    persona=self.mock_session["scenario_snapshot"]["persona"],
                    case_data=self.mock_session["scenario_snapshot"]["case"],
                    new_state=guarded_state,
                    topic_notes=[],
                    transcript_history=[],
                    counselor_utterance="Ada yang disembunyikan?",
                    hidden_facts=hidden_facts,
                )
            )

            sent_prompt = mock_llm.generate_text.call_args.kwargs["user_prompt"]
            self.assertIn("Keterbukaan masih 'guarded'", sent_prompt)
            self.assertNotIn("Fakta sensitif", sent_prompt)

    def test_turn_fails_on_completed_session(self):
        """Memastikan giliran ditolak (HTTP 400) jika status sesi sudah completed."""
        self.mock_conn.fetchrow.return_value = {
            **self.mock_session,
            "status": "completed",
        }
        payload = CreateTurnRequest(content="Halo Nadia")

        with self.assertRaises(HTTPException) as ctx:
            self.run_async(
                send_counselor_turn(
                    session_id=100,
                    payload=payload,
                    user=self.mock_user,
                    conn=self.mock_conn,
                )
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("selesai", ctx.exception.detail)

    @patch("services.simulation.orchestrator.get_latest_client_state")
    @patch("services.simulation.orchestrator.get_latest_topic_notes")
    @patch("services.simulation.orchestrator.get_session_turns")
    @patch("services.simulation.orchestrator.update_client_state_llm")
    def test_atomic_rollback_on_llm_failure(
        self,
        mock_state_llm,
        mock_turns,
        mock_notes,
        mock_state,
    ):
        """Memastikan kegagalan LLM membatalkan transaksi dan mengembalikan HTTP 503."""
        self.mock_conn.fetchrow.return_value = self.mock_session
        mock_state.return_value = self.mock_session["scenario_snapshot"][
            "initial_state"
        ]
        mock_notes.return_value = []
        mock_turns.return_value = []
        mock_state_llm.side_effect = LLMServiceError("Koneksi Gemini gagal.")

        payload = CreateTurnRequest(content="Bisa ceritakan masalahmu?")
        with self.assertRaises(HTTPException) as ctx:
            self.run_async(
                send_counselor_turn(
                    session_id=100,
                    payload=payload,
                    user=self.mock_user,
                    conn=self.mock_conn,
                )
            )
        self.assertEqual(ctx.exception.status_code, 503)
        self.assertIn("Layanan simulasi", ctx.exception.detail)

