from __future__ import annotations

import json
import logging
from typing import Any
from core.config import get_settings
from prompts.prompt_b_responder import PROMPT_B_VERSION, SYSTEM_INSTRUCTION_B
from schemas.client_state import ClientState
from services.llm.gemini_client import get_gemini_client

logger = logging.getLogger("safesesi.simulation.responder")


async def generate_client_response_llm(
    persona: dict[str, Any],
    case_data: dict[str, Any],
    new_state: ClientState | dict[str, Any],
    topic_notes: list[dict[str, Any]],
    transcript_history: list[dict[str, Any]],
    counselor_utterance: str,
    hidden_facts: list[dict[str, Any]],
) -> str:
    """Peran B: Client Responder (menghasilkan ucapan respon klien virtual).

    PEMBATASAN DI LEVEL KODE:
    Hidden facts HANYA dikirimkan ke prompt jika disclosure_level bukan 'guarded'.
    Jika 'guarded', list hidden facts dikosongkan.
    Dilengkapi mekanisme retry 1x.
    """
    settings = get_settings()
    llm = get_gemini_client()

    state_dict = (
        new_state.model_dump() if isinstance(new_state, ClientState) else new_state
    )
    current_disclosure = state_dict.get("disclosure_level", "guarded")

    # Code-level boundary enforcement based on system specification
    filtered_hidden_facts = hidden_facts if current_disclosure != "guarded" else []

    user_prompt = f"""
### Profil Persona Anda:
- Nama: {persona.get('name')}
- Usia / Gender: {persona.get('age')} tahun, {persona.get('gender')}
- Pekerjaan: {persona.get('occupation')}
- Latar Belakang: {persona.get('family_background')}
- Kepribadian Konkret: {persona.get('personality')}
- Gaya Komunikasi: {persona.get('communication_style')}

### Kasus & Masalah Anda:
- Permasalahan Utama: {case_data.get('main_problem')}
- Riwayat & Dampak: {case_data.get('history_impact')}
- Harapan & Konteks Perubahan: {case_data.get('expectation_change_context')}

### Informasi Tersembunyi (Boleh Diungkap Bertahap HANYA JIKA Konteks Sangat Mendukung):
{json.dumps(filtered_hidden_facts, indent=2, ensure_ascii=False) if filtered_hidden_facts else "[] (Keterbukaan masih 'guarded', tidak ada fakta tersembunyi yang diungkapkan)"}

### Kondisi Emosi & Keterbukaan Anda Saat Ini:
- Emosi: {state_dict.get('emotion_type')} ({state_dict.get('emotion_cause')})
- Tingkat Keterbukaan: {state_dict.get('disclosure_level')}
- Ambivalensi: {state_dict.get('ambivalence_lean')} (Ingin Berubah: {state_dict.get('reasons_to_change')} | Bertahan: {state_dict.get('reasons_to_maintain')})
- Ketegangan Hubungan (Discord): {'ADA' if state_dict.get('discord_present') else 'Tidak Tampak'} {f"- Catatan: {state_dict.get('discord_context')}" if state_dict.get('discord_present') else ''}

### Catatan Pembahasan Topik Sejauh Ini:
{json.dumps([{"topik": t.get("topic_name"), "catatan": t.get("description")} for t in topic_notes], indent=2, ensure_ascii=False)}

### Percakapan Terakhir:
{json.dumps([{"speaker": t.get("speaker"), "content": t.get("content")} for t in transcript_history[-8:]], indent=2, ensure_ascii=False)}

### Ucapan Konselor Terkini:
"{counselor_utterance}"

Bicaralah sebagai klien virtual dengan menghayati persona dan kondisi di atas.
Tanggapi ucapan konselor secara wajar dan ringkas (1–3 kalimat) dalam Bahasa Indonesia.
""".strip()

    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            return await llm.generate_text(
                model=settings.GEMINI_MODEL_RESPONDER,
                system_instruction=SYSTEM_INSTRUCTION_B,
                user_prompt=user_prompt,
                temperature=0.7,
            )
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "Percobaan %d pembuatan Client Responder gagal: %s", attempt + 1, exc
            )

    raise last_exc or RuntimeError("Gagal menghasilkan respons klien setelah 2 percobaan.")
