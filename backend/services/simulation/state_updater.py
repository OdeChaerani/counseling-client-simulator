from __future__ import annotations

import json
import logging
from typing import Any
from core.config import get_settings
from prompts.prompt_a_state import PROMPT_A_VERSION, SYSTEM_INSTRUCTION_A
from schemas.client_state import ClientState
from services.llm.gemini_client import get_gemini_client

logger = logging.getLogger("safesesi.simulation.state")


async def update_client_state_llm(
    counselor_utterance: str,
    current_state: dict[str, Any],
    persona: dict[str, Any],
    case_data: dict[str, Any],
    transcript_history: list[dict[str, Any]],
    topic_notes: list[dict[str, Any]] | None = None,
) -> ClientState:
    """Peran A: State Updater (menghasilkan pembaruan ClientState menggunakan LLM).

    Dilengkapi mekanisme retry 1x jika pemanggilan model atau parsing gagal.
    """
    settings = get_settings()
    llm = get_gemini_client()

    notes_section = ""
    if topic_notes:
        notes_section = f"""
### Catatan Perkembangan Topik:
{json.dumps([{"topik": t.get("topic_name"), "catatan": t.get("description")} for t in topic_notes], indent=2, ensure_ascii=False)}
"""

    user_prompt = f"""
### Konteks Skenario:
- Nama Klien: {persona.get('name')}
- Usia / Gender: {persona.get('age')} tahun, {persona.get('gender')}
- Kepribadian: {persona.get('personality')}
- Gaya Komunikasi: {persona.get('communication_style')}
- Permasalahan Kasus: {case_data.get('main_problem')}
- Riwayat & Dampak: {case_data.get('history_impact')}
- Konteks Perubahan: {case_data.get('expectation_change_context')}
{notes_section}
### Kondisi Klien Saat Ini (Sebelum Giliran Konselor Terkini):
{json.dumps(current_state, indent=2, ensure_ascii=False)}

### Riwayat Percakapan Terakhir:
{json.dumps([{"speaker": t.get("speaker"), "content": t.get("content")} for t in transcript_history[-8:]], indent=2, ensure_ascii=False)}

### Ucapan Konselor Terkini:
"{counselor_utterance}"

Analisis ucapan konselor terkini di atas dan tentukan pembaruan kondisi klien (Client State).
Keluarkan JSON yang mematuhi skema ClientState.
""".strip()

    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            return await llm.generate_json(
                model=settings.GEMINI_MODEL_STATE,
                system_instruction=SYSTEM_INSTRUCTION_A,
                user_prompt=user_prompt,
                response_schema=ClientState,
                temperature=0.2,
            )
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "Percobaan %d pembaruan State Updater gagal: %s", attempt + 1, exc
            )

    raise last_exc or RuntimeError("Gagal memperbarui status klien setelah 2 percobaan.")
