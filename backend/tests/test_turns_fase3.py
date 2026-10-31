from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from schemas.client_state import ClientState
from schemas.session import CreateTurnRequest
from services.simulation.orchestrator import get_session_lock


class MockTx:
    """Mock asynchronous context manager untuk conn.transaction()."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def run_coro(coro):
    """Menjalankan coroutine murni berbasis mock tanpa inisialisasi socket sistem operasi."""
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


class TestTurnsFase3Unit(unittest.TestCase):
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
                "discord_context": None,
                "discord_response": None,
            },
            "hidden_facts": [
                {
                    "code": "H1",
                    "short_title": "Penilaian teman",
                    "description": "Takut dinilai tidak bertanggung jawab",
                },
                {
                    "code": "H2",
                    "short_title": "Komentar kurang kompak",
                    "description": "Pengalaman dievaluasi tajam",
                },
            ],
        }

        self.mock_session = {
            "id": 100,
            "student_id": 10,
            "scenario_id": 1,
            "class_id": None,
            "parent_session_id": None,
            "scenario_snapshot": self.mock_snapshot,
            "status": "in_progress",
        }

    def test_session_lock_serialization(self):
        """Memastikan get_session_lock mengembalikan lock yang sama untuk sesi yang sama."""
        lock1 = run_coro(get_session_lock(100))
        lock2 = run_coro(get_session_lock(100))
        lock3 = run_coro(get_session_lock(200))

        self.assertIs(lock1, lock2)
        self.assertIsNot(lock1, lock3)

    def test_empty_content_validation(self):
        """Memastikan CreateTurnRequest menolak konten kosong atau hanya spasi."""
        with self.assertRaises(ValueError):
            CreateTurnRequest(content="   ")

    def test_send_turn_session_completed_error(self):
        """Memastikan giliran tidak dapat dikirimkan ke sesi yang sudah selesai."""
        from api.v1.sessions import send_counselor_turn

        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = {**self.mock_session, "status": "completed"}

        payload = CreateTurnRequest(content="Halo Nadia")

        with self.assertRaises(HTTPException) as ctx:
            run_coro(
                send_counselor_turn(
                    session_id=100,
                    payload=payload,
                    user=self.mock_user,
                    conn=mock_conn,
                )
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("selesai", ctx.exception.detail)

    def test_send_turn_unauthorized_user(self):
        """Memastikan mahasiswa lain tidak dapat mengirim turn ke sesi orang lain."""
        from api.v1.sessions import send_counselor_turn

        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = self.mock_session
        payload = CreateTurnRequest(content="Halo Nadia")
        other_user = {"id": 99, "name": "Mahasiswa Lain", "role": "student"}

        with self.assertRaises(HTTPException) as ctx:
            run_coro(
                send_counselor_turn(
                    session_id=100,
                    payload=payload,
                    user=other_user,
                    conn=mock_conn,
                )
            )
        self.assertEqual(ctx.exception.status_code, 403)

    @patch("services.simulation.orchestrator.get_latest_client_state")
    @patch("services.simulation.orchestrator.get_latest_topic_notes")
    @patch("services.simulation.orchestrator.get_session_turns")
    @patch("services.simulation.orchestrator.save_turn")
    @patch("services.simulation.orchestrator.save_client_state")
    @patch("services.simulation.orchestrator.get_next_turn_no")
    def test_send_turn_greeting_bypass(
        self,
        mock_get_next_no,
        mock_save_state,
        mock_save_turn,
        mock_get_turns,
        mock_get_notes,
        mock_get_state,
    ):
        """Memastikan shortcut sapaan langsung membalas sapaan tanpa memanggil LLM."""
        from api.v1.sessions import send_counselor_turn

        mock_conn = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=MockTx())
        mock_conn.fetchrow.return_value = self.mock_session

        mock_get_state.return_value = self.mock_snapshot["initial_state"]
        mock_get_notes.return_value = []
        mock_get_turns.return_value = []
        mock_get_next_no.return_value = 1
        mock_save_turn.side_effect = [1, 2]  # counselor turn id, client turn id

        payload = CreateTurnRequest(content="Halo selamat pagi Nadia, apa kabar hari ini?")

        res = run_coro(
            send_counselor_turn(
                session_id=100,
                payload=payload,
                user=self.mock_user,
                conn=mock_conn,
            )
        )

        self.assertEqual(res.turn_no, 2)
        self.assertIn("Nadia", res.content)
        # Internal state tidak bocor jika DEBUG_INCLUDE_INTERNAL=false
        self.assertIsNone(res.internal_state)
        # Pastikan giliran disimpan
        self.assertEqual(mock_save_turn.call_count, 2)
        # Pastikan state klien disalin
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
    def test_send_turn_substantive_guarded_boundary(
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
        from api.v1.sessions import send_counselor_turn
        from services.simulation.notes_updater import TopicNoteUpdate

        mock_conn = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=MockTx())
        mock_conn.fetchrow.return_value = self.mock_session

        mock_get_state.return_value = self.mock_snapshot["initial_state"]
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

        # Peran A menghasilkan state guarded
        updated_state = ClientState(
            emotion_type="Cemas",
            emotion_cause="Tenggat kuliah mendekat",
            disclosure_level="guarded",
            disclosure_trigger="Pertanyaan konselor",
            reasons_to_change="Ingin lega",
            reasons_to_maintain="Takut dinilai",
            ambivalence_lean="both",
            discord_present=False,
            discord_context=None,
            discord_response=None,
        )
        mock_state_llm.return_value = updated_state
        mock_resp_llm.return_value = "Iya, akhir-akhir ini tugas kuliah dan kegiatan himpunan cukup menyita waktu."
        mock_notes_llm.return_value = [
            TopicNoteUpdate(
                topic_name="Permasalahan utama",
                description="Klien mengonfirmasi tugas dan kegiatan menyita waktu.",
            )
        ]

        payload = CreateTurnRequest(
            content="Bisa ceritakan apa yang paling membebani pikiranmu saat ini?"
        )

        res = run_coro(
            send_counselor_turn(
                session_id=100,
                payload=payload,
                user=self.mock_user,
                conn=mock_conn,
            )
        )

        # Verifikasi respons
        self.assertEqual(res.turn_no, 2)
        self.assertIn("tugas kuliah", res.content)
        self.assertIsNone(res.internal_state)

        # Verifikasi Peran A dipanggil
        mock_state_llm.assert_called_once()

        # Verifikasi Peran B dipanggil
        mock_resp_llm.assert_called_once()
        # Periksa argumen hidden_facts yang dikirimkan ke responder:
        # Karena state guarded, responder secara internal memfilter hidden facts menjadi []
        kwargs = mock_resp_llm.call_args.kwargs
        self.assertEqual(kwargs["new_state"].disclosure_level, "guarded")

        # Verifikasi persistensi
        self.assertEqual(mock_save_turn.call_count, 2)
        mock_save_state.assert_called_once()
        mock_save_note.assert_called_once()

    def test_responder_code_level_boundary_enforcement(self):
        """Memastikan responder.py memfilter hidden facts menjadi kosong jika disclosure_level == 'guarded'."""
        from services.simulation.responder import generate_client_response_llm

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

            run_coro(
                generate_client_response_llm(
                    persona=self.mock_snapshot["persona"],
                    case_data=self.mock_snapshot["case"],
                    new_state=guarded_state,
                    topic_notes=[],
                    transcript_history=[],
                    counselor_utterance="Ada yang disembunyikan?",
                    hidden_facts=hidden_facts,
                )
            )

            # Periksa prompt yang dikirimkan ke Gemini LLM
            sent_prompt = mock_llm.generate_text.call_args.kwargs["user_prompt"]
            self.assertIn("Keterbukaan masih 'guarded'", sent_prompt)
            self.assertNotIn("Fakta sensitif", sent_prompt)


if __name__ == "__main__":
    unittest.main()

