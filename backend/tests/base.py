from __future__ import annotations

import unittest
from typing import Any, Coroutine
from unittest.mock import AsyncMock, MagicMock


class MockTx:
    """Mock asynchronous context manager untuk conn.transaction()."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """Menjalankan coroutine murni berbasis mock tanpa overhead socket sistem operasi."""
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


class BaseTestCase(unittest.TestCase):
    """Base class untuk pengujian unit & integrasi backend SafeSesi."""

    def run_async(self, coro: Coroutine[Any, Any, Any]) -> Any:
        return run_async(coro)

    def create_mock_connection(self) -> AsyncMock:
        """Membuat mock database connection dengan transaction context manager siap pakai."""
        mock_conn = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=MockTx())
        return mock_conn

    def get_sample_user(
        self, user_id: int = 10, role: str = "student", name: str = "Mahasiswa Test"
    ) -> dict[str, Any]:
        return {"id": user_id, "name": name, "role": role}

    def get_sample_snapshot(self) -> dict[str, Any]:
        return {
            "scenario": {
                "id": 1,
                "scenario_code": "SS-NAD-01",
                "title": "Nadia Maharani",
            },
            "persona": {
                "name": "Nadia Maharani",
                "age": 19,
                "gender": "Perempuan",
                "occupation": "Mahasiswi Psikologi Semester 3",
                "personality": "Menjaga komitmen, berhati-hati",
                "communication_style": "Cenderung berhati-hati dan sopan",
            },
            "case": {
                "main_problem": "Nadia kewalahan membagi tanggung jawab kuliah dan organisasi.",
                "history_impact": "Tenggat berdekatan, tidur berkurang, kuliah mulai keteteran.",
                "expectation_change_context": "Membagi atau membatasi tanggung jawab tambahan.",
            },
            "initial_state": {
                "emotion_type": "Cemas dan kewalahan",
                "emotion_cause": "Tenggat kuliah dan kegiatan organisasi bertumpuk",
                "disclosure_level": "guarded",
                "disclosure_trigger": "Awal sesi",
                "reasons_to_change": "Beban berkurang agar kuliah tidak terganggu",
                "reasons_to_maintain": "Tetap aktif di organisasi dan menjaga komitmen",
                "ambivalence_lean": "both",
                "discord_present": False,
                "discord_context": None,
                "discord_response": None,
            },
            "hidden_facts": [
                {
                    "code": "H1",
                    "short_title": "Penilaian teman",
                    "description": "Kekhawatiran terhadap penilaian teman bila membatasi tugas",
                },
                {
                    "code": "H2",
                    "short_title": "Komentar kurang kompak",
                    "description": "Pengalaman di masa lalu disebut kurang kompak saat tidak bisa membantu",
                },
            ],
        }

    def get_sample_session(
        self, session_id: int = 100, student_id: int = 10, status: str = "in_progress"
    ) -> dict[str, Any]:
        return {
            "id": session_id,
            "student_id": student_id,
            "scenario_id": 1,
            "class_id": None,
            "parent_session_id": None,
            "scenario_snapshot": self.get_sample_snapshot(),
            "status": status,
        }

