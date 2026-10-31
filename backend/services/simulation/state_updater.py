from __future__ import annotations

import json
from typing import Any
from core.config import get_settings
from prompts.prompt_a_state import SYSTEM_INSTRUCTION_A
from schemas.client_state import ClientState
from services.llm.gemini_client import get_gemini_client


async def update_client_state_llm(
    counselor_utterance: str,
    current_state: dict[str, Any],
    persona: dict[str, Any],
    case_data: dict[str, Any],
    transcript_history: list[dict[str, Any]],
) -> ClientState:
    """Peran A: State Updater (menghasilkan pembaruan ClientState menggunakan LLM)."""
    settings = get_settings()
    llm = get_gemini_client()

    user_prompt = f"""
### Konteks Skenario:
- Nama Klien: {persona.get('name')}
- Usia / Gender: {persona.get('age')} tahun, {persona.get('gender')}
- Kepribadian: {persona.get('personality')}
- Gaya Komunikasi: {persona.get('communication_style')}
- Permasalahan Kasus: {case_data.get('main_problem')}
- Riwayat & Dampak: {case_data.get('history_impact')}
- Konteks Perubahan: {case_data.get('expectation_change_context')}

### Kondisi Klien Saat Ini (Sebelum Giliran Konselor Terkini):
{json.dumps(current_state, indent=2, ensure_ascii=False)}

### Riwayat Percakapan Terakhir:
{json.dumps([{"speaker": t.get("speaker"), "content": t.get("content")} for t in transcript_history[-8:]], indent=2, ensure_ascii=False)}

### Ucapan Konselor Terkini:
"{counselor_utterance}"

Analisis ucapan konselor terkini di atas dan tentukan pembaruan kondisi klien (Client State).
Keluarkan JSON yang mematuhi skema ClientState.
""".strip()

    return await llm.generate_json(
        model=settings.GEMINI_MODEL_STATE,
        system_instruction=SYSTEM_INSTRUCTION_A,
        user_prompt=user_prompt,
        response_schema=ClientState,
        temperature=0.2,
    )

