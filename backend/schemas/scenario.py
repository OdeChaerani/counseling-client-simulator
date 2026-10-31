from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class Persona(BaseModel):
    """Profil internal persona klien (10 isian spesifikasi SafeSesi)."""

    name: str = Field(..., description="Nama atau nama fiktif klien")
    age: int = Field(..., ge=10, le=120, description="Usia klien dalam tahun")
    gender: str = Field(..., description="Jenis kelamin klien")
    education: str | None = Field(default=None, description="Jenjang dan latar pendidikan")
    occupation: str | None = Field(default=None, description="Pekerjaan atau kegiatan utama")
    marital_status: str | None = Field(default=None, description="Status pernikahan")
    family_background: str | None = Field(default=None, description="Latar belakang keluarga")
    personality: str = Field(..., description="Karakteristik kepribadian konkret (tanpa Big Five)")
    communication_style: str = Field(..., description="Gaya komunikasi verbal klien")
    additional_background: str | None = Field(default=None, description="Latar tambahan relevan")


class HiddenFact(BaseModel):
    """Informasi tersembunyi yang diungkap bertahap (H1, H2, dst.)."""

    code: str = Field(..., description="Kode fakta tersembunyi (H1, H2, dst.)")
    short_title: str = Field(..., description="Judul singkat fakta (menjadi nama topik)")
    fact: str = Field(..., description="Uraian isi fakta tersembunyi")
    sort_order: int = Field(default=0, description="Urutan penyajian")


class Case(BaseModel):
    """Kasus klien (5 isian spesifikasi SafeSesi)."""

    main_problem: str = Field(..., description="Permasalahan utama yang dirasakan klien")
    history_impact: str | None = Field(default=None, description="Riwayat dan dampak masalah")
    expectation_change_context: str = Field(..., description="Harapan klien dan konteks perubahan perilaku")
    health_condition: str | None = Field(default=None, description="Kondisi kesehatan fisik/mental relevan")


class InitialState(BaseModel):
    """Kondisi awal klien virtual sebelum sesi dimulai (sesuai tabel scenario_initial_states)."""

    emotion_type: str = Field(..., description="Perasaan awal klien (mis. Cemas dan kewalahan)")
    emotion_cause: str | None = Field(default=None, description="Kausa/alasan emosi awal")
    disclosure_level: str = Field(..., description="Tingkat keterbukaan awal: guarded | medium | high")
    disclosure_trigger: str | None = Field(default=None, description="Pemicu keterbukaan awal")
    reasons_to_change: str | None = Field(default=None, description="Alasan ingin berubah")
    reasons_to_maintain: str | None = Field(default=None, description="Alasan mempertahankan keadaan saat ini")
    ambivalence_lean: str = Field(..., description="Kecenderungan awal: toward_change | toward_status_quo | both")
    discord_present: bool = Field(default=False, description="Ketegangan hubungan (default false)")
    discord_context: str | None = Field(default=None, description="Konteks ketegangan")
    discord_response: str | None = Field(default=None, description="Bentuk respons ketegangan")


class ScenarioHeader(BaseModel):
    """Informasi metadata skenario konseling."""

    id: int
    title: str
    visibility: str = "class"
    review_status: str = "draft"
    change_target: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ScenarioSnapshot(BaseModel):
    """Snapshot lengkap skenario yang dibekukan saat sesi dibuat (keluaran SQL build_scenario_snapshot)."""

    scenario: dict[str, Any]
    persona: Persona
    case: Case
    initial_state: InitialState
    hidden_facts: list[HiddenFact] = []
