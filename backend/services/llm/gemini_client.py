from __future__ import annotations

import json
import logging
from typing import TypeVar
from google import genai
from google.genai import types
from pydantic import BaseModel

from core.config import get_settings
from core.errors import LLMServiceError

logger = logging.getLogger("safesesi.llm")

T = TypeVar("T", bound=BaseModel)


class GeminiAsyncClient:
    """Wrapper async untuk Google Gemini SDK (google-genai)."""

    def __init__(self, api_key: str | None = None) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            if not self._api_key:
                raise LLMServiceError("GEMINI_API_KEY belum dikonfigurasi di environment.")
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    async def generate_json(
        self,
        model: str,
        system_instruction: str,
        user_prompt: str,
        response_schema: type[T],
        temperature: float = 0.2,
    ) -> T:
        """Menghasilkan structured output JSON yang tervalidasi dengan skema Pydantic."""
        client = self._get_client()
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                response_mime_type="application/json",
                response_schema=response_schema,
            )
            response = await client.aio.models.generate_content(
                model=model,
                contents=user_prompt,
                config=config,
            )
            raw_text = response.text or "{}"
            data = json.loads(raw_text)
            return response_schema.model_validate(data)
        except Exception as exc:
            logger.exception("Gagal menghasilkan JSON terstruktur dari Gemini: %s", exc)
            raise LLMServiceError(f"Gagal memproses respons AI terstruktur: {exc}") from exc

    async def generate_text(
        self,
        model: str,
        system_instruction: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """Menghasilkan teks natural dalam Bahasa Indonesia."""
        client = self._get_client()
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
            )
            response = await client.aio.models.generate_content(
                model=model,
                contents=user_prompt,
                config=config,
            )
            return (response.text or "").strip()
        except Exception as exc:
            logger.exception("Gagal menghasilkan teks dari Gemini: %s", exc)
            raise LLMServiceError(f"Gagal menghasilkan ucapan klien: {exc}") from exc


_gemini_client: GeminiAsyncClient | None = None


def get_gemini_client() -> GeminiAsyncClient:
    """Mengembalikan singleton instance GeminiAsyncClient."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiAsyncClient()
    return _gemini_client

