from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Jalur berkas .env di direktori backend
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Konfigurasi global backend SafeSesi menggunakan pydantic-settings."""

    DATABASE_URL: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_STATE: str = "gemini-2.5-flash"
    GEMINI_MODEL_RESPONDER: str = "gemini-2.5-flash"
    GEMINI_MODEL_NOTES: str = "gemini-2.5-flash"

    NOTES_UPDATE_MODE: str = "inline"  # inline | background
    GREETING_SHORTCUT_ENABLED: bool = True
    DEBUG_INCLUDE_INTERNAL: bool = False

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            if v.strip().startswith("["):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Mengembalikan singleton instance Settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

