from __future__ import annotations

# TODO: JWT - Implementasi hashing password (argon2/bcrypt) dan JWT token untuk produksi
# Saat ini menggunakan header dev X-Dev-User-Id sesuai ketentuan Fase 1


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    """Stub verifikasi password."""
    if not hashed_password:
        return False
    return plain_password == hashed_password

