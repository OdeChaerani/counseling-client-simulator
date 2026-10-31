from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ClientState(BaseModel):
    """Representasi Client State SafeSesi (kolom sama persis dengan tabel client_state_log)."""

    id: int | None = Field(default=None, description="Primary key log")
    session_id: int | None = Field(default=None, description="ID sesi terkait")
    turn_id: int | None = Field(default=None, description="ID turn klien terkait (NULL untuk initial state)")
    emotion_type: str = Field(..., description="Jenis emosi yang dirasakan klien")
    emotion_cause: str | None = Field(default=None, description="Penyebab atau konteks emosi")
    disclosure_level: str = Field(..., description="Tingkat keterbukaan: guarded | medium | high")
    disclosure_trigger: str | None = Field(default=None, description="Pemicu perubahan keterbukaan")
    reasons_to_change: str | None = Field(default=None, description="Alasan klien ingin berubah")
    reasons_to_maintain: str | None = Field(default=None, description="Alasan klien mempertahankan keadaan")
    ambivalence_lean: str = Field(..., description="Kecenderungan ambivalensi: toward_change | toward_status_quo | both")
    discord_present: bool = Field(default=False, description="Apakah ketegangan hubungan tampak")
    discord_context: str | None = Field(default=None, description="Konteks pemicu ketegangan hubungan")
    discord_response: str | None = Field(default=None, description="Bentuk respons ketidaknyamanan klien")
    created_at: datetime | None = Field(default=None, description="Waktu pencatatan state")
