from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    """Membersihkan teks dan normalisasi spasi."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def classify_greeting(text: str) -> bool:
    """Mendeteksi apakah ucapan konselor merupakan sapaan pembuka/basa-basi standar tanpa substansi konseling."""
    norm = normalize_text(text)
    words = norm.split()
    if not words:
        return False

    # Jika ucapan konselor terlalu panjang, kemungkinan sudah masuk ke substansi kasus
    if len(words) > 10:
        return False

    # Pola sapaan pembuka umum
    greeting_patterns = [
        r"^(halo|hai|hi|hey)\b",
        r"^selamat (pagi|siang|sore|malam)\b",
        r"^assalamu ?[\w]*\b",
        r"^(apa kabar|bagaimana kabarnya|gimana kabarnya)\b",
    ]
    return any(re.search(pat, norm) for pat in greeting_patterns)


def generate_greeting_response(client_name: str = "klien") -> str:
    """Menghasilkan respon sapaan sopan klien virtual tanpa memanggil LLM."""
    clean_name = client_name.split()[0] if client_name else "klien"
    return f"Halo, selamat pagi. Terima kasih sudah meluangkan waktu untuk mengobrol dengan saya."

