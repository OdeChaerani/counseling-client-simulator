from __future__ import annotations

import json
from typing import Any
from pydantic import BaseModel, Field
from core.config import get_settings
from prompts.prompt_c_notes import SYSTEM_INSTRUCTION_C
from services.llm.gemini_client import get_gemini_client


class TopicNoteUpdate(BaseModel):
    topic_name: str = Field(..., description="Nama topik yang diperbarui")
    description: str = Field(..., description="Deskripsi rangkuman faktual yang diucapkan klien")


class NotesUpdateResult(BaseModel):
    updated_topics: list[TopicNoteUpdate] = Field(
        default_factory=list,
        description="Daftar topik yang mengalami pembaruan pembahasan pada giliran ini",
    )


async def update_topic_notes_llm(
    current_topic_notes: list[dict[str, Any]],
    counselor_utterance: str,
    actual_client_response: str,
) -> list[TopicNoteUpdate]:
    """Peran C: Notes Updater (memperbarui catatan perkembangan topik setelah respons klien terbentuk)."""
    settings = get_settings()
    llm = get_gemini_client()

    user_prompt = f"""
### Daftar Topik & Catatan Saat Ini:
{json.dumps([{"nama_topik": t.get("topic_name"), "catatan_saat_ini": t.get("description")} for t in current_topic_notes], indent=2, ensure_ascii=False)}

### Dialog Giliran Ini:
- Konselor: "{counselor_utterance}"
- Klien: "{actual_client_response}"

Periksa informasi nyata apa saja yang baru disampaikan oleh klien pada giliran ini.
Hanya kembalikan topik yang mengalami pembaruan deskripsi. Jika tidak ada perubahan, kembalikan list kosong.
""".strip()

    result = await llm.generate_json(
        model=settings.GEMINI_MODEL_NOTES,
        system_instruction=SYSTEM_INSTRUCTION_C,
        user_prompt=user_prompt,
        response_schema=NotesUpdateResult,
        temperature=0.2,
    )
    return result.updated_topics

