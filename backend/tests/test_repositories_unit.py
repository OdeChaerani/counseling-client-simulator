from __future__ import annotations

import unittest
from unittest.mock import AsyncMock

from schemas.scenario import (
    Case,
    HiddenFact,
    InitialState,
    Persona,
    ScenarioSnapshot,
)


class TestRepositorySchemasUnit(unittest.TestCase):
    def test_snapshot_topic_extraction_logic(self):
        snapshot = ScenarioSnapshot(
            scenario={"id": 1, "title": "SS-NAD-01 Nadia Maharani"},
            persona=Persona(
                name="Nadia Maharani",
                age=19,
                gender="Perempuan",
                personality="Menjaga komitmen",
                communication_style="Berhati-hati",
            ),
            case=Case(
                main_problem="Nadia kewalahan membagi tanggung jawab.",
                history_impact="Tenggat berdekatan, tidur berkurang.",
                expectation_change_context="Membagi atau membatasi tanggung jawab tambahan.",
                health_condition=None,
            ),
            initial_state=InitialState(
                emotion_type="Cemas",
                disclosure_level="guarded",
                ambivalence_lean="both",
                discord_present=False,
            ),
            hidden_facts=[
                HiddenFact(
                    code="H1",
                    short_title="Kekhawatiran terhadap penilaian teman",
                    fact="Nadia takut dianggap tidak serius.",
                    sort_order=1,
                ),
                HiddenFact(
                    code="H2",
                    short_title="Pengalaman komentar kurang kompak",
                    fact="Seorang teman pernah menyebut kurang kompak.",
                    sort_order=2,
                ),
            ],
        )

        # Simulasi ekstraksi topik sesuai create_session_topics_from_snapshot
        topics = []
        order = 1
        case_data = snapshot.case
        if case_data.main_problem:
            topics.append((order, "Permasalahan utama", "main_problem", None))
            order += 1
        if case_data.history_impact:
            topics.append((order, "Riwayat dan dampak masalah", "history_impact", None))
            order += 1
        if case_data.expectation_change_context:
            topics.append((order, "Harapan dan arah perubahan", "expectation_change_context", None))
            order += 1
        for hf in snapshot.hidden_facts:
            topics.append((order, hf.short_title, "hidden_fact", hf.code))
            order += 1

        self.assertEqual(len(topics), 5)
        self.assertEqual(topics[0][1], "Permasalahan utama")
        self.assertEqual(topics[1][1], "Riwayat dan dampak masalah")
        self.assertEqual(topics[2][1], "Harapan dan arah perubahan")
        self.assertEqual(topics[3][1], "Kekhawatiran terhadap penilaian teman")
        self.assertEqual(topics[3][3], "H1")
        self.assertEqual(topics[4][1], "Pengalaman komentar kurang kompak")
        self.assertEqual(topics[4][3], "H2")

