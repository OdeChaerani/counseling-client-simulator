from __future__ import annotations

import unittest
from schemas.client_state import ClientState
from schemas.scenario import (
    Case,
    HiddenFact,
    InitialState,
    Persona,
    ScenarioSnapshot,
)
from schemas.session import (
    CreateSessionRequest,
    CreateTurnRequest,
    TurnResponse,
)


class TestSchemas(unittest.TestCase):
    def test_persona_ten_fields(self):
        persona = Persona(
            name="Nadia Maharani",
            age=19,
            gender="Perempuan",
            education="Mahasiswi psikologi semester 3.",
            occupation="Mahasiswi penuh waktu.",
            marital_status="Belum menikah.",
            family_background="Tinggal bersama orang tua dan adik.",
            personality="Menjaga komitmen, sulit menolak permintaan.",
            communication_style="Pada awal pertemuan menjawab singkat dan berhati-hati.",
            additional_background="Pertemanan dan organisasi penting baginya.",
        )
        self.assertEqual(persona.name, "Nadia Maharani")
        self.assertEqual(persona.age, 19)

    def test_case_and_hidden_facts(self):
        case_obj = Case(
            main_problem="Nadia kewalahan membagi tanggung jawab.",
            history_impact="Tenggat berdekatan, tidur berkurang.",
            expectation_change_context="Membagi atau membatasi tanggung jawab tambahan.",
            health_condition=None,
        )
        fact = HiddenFact(
            code="H1",
            short_title="Kekhawatiran terhadap penilaian teman",
            fact="Nadia takut dianggap tidak serius atau tidak dapat diandalkan.",
            sort_order=1,
        )
        self.assertEqual(case_obj.main_problem, "Nadia kewalahan membagi tanggung jawab.")
        self.assertEqual(fact.code, "H1")

    def test_client_state_matches_db_columns(self):
        state = ClientState(
            emotion_type="Cemas dan kewalahan",
            emotion_cause="Tenggat kuliah dan kegiatan organisasi bertumpuk",
            disclosure_level="guarded",
            disclosure_trigger="Awal sesi konseling",
            reasons_to_change="Beban berkurang agar kuliah tidak keteteran",
            reasons_to_maintain="Ingin tetap terlibat dalam kegiatan bermakna",
            ambivalence_lean="both",
            discord_present=False,
        )
        self.assertEqual(state.disclosure_level, "guarded")
        self.assertEqual(state.ambivalence_lean, "both")
        self.assertFalse(state.discord_present)

    def test_scenario_snapshot_structure(self):
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
                main_problem="Kewalahan",
                expectation_change_context="Membagi tugas",
            ),
            initial_state=InitialState(
                emotion_type="Cemas",
                disclosure_level="guarded",
                ambivalence_lean="both",
                discord_present=False,
            ),
            hidden_facts=[
                HiddenFact(code="H1", short_title="Takut dinilai", fact="Takut...")
            ],
        )
        self.assertEqual(snapshot.persona.name, "Nadia Maharani")
        self.assertEqual(len(snapshot.hidden_facts), 1)

    def test_turn_request_and_response(self):
        req = CreateTurnRequest(content="Halo Nadia, apa yang membawamu kemari?")
        self.assertEqual(req.content, "Halo Nadia, apa yang membawamu kemari?")
        self.assertEqual(req.start_ms, 0)

        res = TurnResponse(turn_no=1, content="Halo, terima kasih sudah menerima saya.")
        self.assertEqual(res.turn_no, 1)
        self.assertIsNone(res.internal_state)

