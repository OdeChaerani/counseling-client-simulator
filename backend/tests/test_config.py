from __future__ import annotations

import unittest
from core.config import Settings


class TestConfig(unittest.TestCase):
    def test_default_settings(self):
        settings = Settings(
            DATABASE_URL="postgresql://user:pass@localhost:6543/postgres",
            GEMINI_API_KEY="test_key",
        )
        self.assertEqual(settings.NOTES_UPDATE_MODE, "inline")
        self.assertTrue(settings.GREETING_SHORTCUT_ENABLED)
        self.assertFalse(settings.DEBUG_INCLUDE_INTERNAL)
        self.assertIn("http://localhost:5173", settings.CORS_ORIGINS)

    def test_cors_origins_parsing(self):
        settings = Settings(
            DATABASE_URL="postgresql://user:pass@localhost:6543/postgres",
            CORS_ORIGINS='["https://safesesi.ac.id", "http://localhost:3000"]',
        )
        self.assertIn("https://safesesi.ac.id", settings.CORS_ORIGINS)
        self.assertIn("http://localhost:3000", settings.CORS_ORIGINS)

