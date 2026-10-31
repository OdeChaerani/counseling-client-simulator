from __future__ import annotations

import unittest
from services.simulation.intent import classify_greeting, generate_greeting_response


class TestIntentService(unittest.TestCase):
    def test_greeting_detection(self):
        self.assertTrue(classify_greeting("Halo Nadia, selamat pagi"))
        self.assertTrue(classify_greeting("Hai apa kabar?"))
        self.assertTrue(classify_greeting("Assalamu'alaikum"))
        self.assertTrue(classify_greeting("Selamat siang"))

    def test_substantive_not_greeting(self):
        self.assertFalse(
            classify_greeting("Bagaimana perasaanmu menghadapi tenggat organisasi dan tugas kuliah yang bertumpuk?")
        )
        self.assertFalse(
            classify_greeting("Kamu merasa terjepit antara tanggung jawab tugas dan menjaga pertemanan.")
        )

    def test_greeting_response(self):
        resp = generate_greeting_response("Nadia Maharani")
        self.assertIn("Halo", resp)

