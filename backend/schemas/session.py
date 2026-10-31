from __future__ import annotations

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

from schemas.client_state import ClientState
from schemas.scenario import ScenarioSnapshot


class CreateSessionRequest(BaseModel):
    """Permintaan pembuatan sesi simulasi konseling baru."""

    scenario_id: int = Field(..., description="ID skenario yang dipilih")
    class_id: int | None = Field(default=None, description="ID kelas jika latihan kelas (NULL untuk latihan mandiri)")
    mode: Literal["new", "repeat", "continue"] = Field(default="new", description="Mode latihan: new | repeat | continue")
    parent_session_id: int | None = Field(default=None, description="ID sesi sebelumnya jika mode continue")


class SessionResponse(BaseModel):
    """Respon data sesi konseling."""

    id: int
    student_id: int
    scenario_id: int
    class_id: int | None = None
    parent_session_id: int | None = None
    scenario_snapshot: ScenarioSnapshot
    status: str
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: int | None = None


class CreateTurnRequest(BaseModel):
    """Permintaan pengiriman giliran ucapan konselor."""

    content: str = Field(..., min_length=1, description="Teks ucapan konselor")
    start_ms: int = Field(default=0, ge=0, description="Waktu awal bicara dalam milidetik")
    end_ms: int = Field(default=0, ge=0, description="Waktu akhir bicara dalam milidetik")


class TurnResponse(BaseModel):
    """Respon giliran dari klien virtual."""

    turn_no: int = Field(..., description="Nomor urut respon klien")
    content: str = Field(..., description="Teks respons klien virtual dalam Bahasa Indonesia")
    internal_state: ClientState | None = Field(
        default=None,
        description="State internal klien (HANYA dikembalikan jika DEBUG_INCLUDE_INTERNAL=true)",
    )


class EndSessionResponse(BaseModel):
    """Respon penyelesaian sesi konseling."""

    id: int
    status: str
    duration_seconds: int | None
    ended_at: datetime
