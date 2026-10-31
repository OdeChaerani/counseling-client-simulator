from __future__ import annotations

from typing import Any, AsyncGenerator
import asyncpg
from fastapi import Header, HTTPException, Request, status

from repositories.users import get_user_by_id


async def get_db(request: Request) -> AsyncGenerator[asyncpg.Connection, None]:
    """Dependency untuk meminjam koneksi PostgreSQL dari pool aplikasi."""
    pool: asyncpg.Pool = request.app.state.db_pool
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection pool belum siap.",
        )
    async with pool.acquire() as connection:
        yield connection


async def get_current_user(
    request: Request,
    x_dev_user_id: int | None = Header(default=None, alias="X-Dev-User-Id"),
) -> dict[str, Any]:
    """Dependency autentikasi dev: membaca header X-Dev-User-Id lalu mengambil user dari DB.

    TODO: JWT - Ganti dengan verifikasi Bearer JWT token untuk produksi.
    """
    if x_dev_user_id is None:
        # Default fallback untuk dev jika header tidak dikirim (misal ID 1)
        x_dev_user_id = 1

    pool: asyncpg.Pool = request.app.state.db_pool
    if pool is None:
        # Fallback dummy user jika pool belum tersedia (misal saat standalone test)
        return {"id": x_dev_user_id, "name": "Dev User", "role": "student"}

    async with pool.acquire() as conn:
        user = await get_user_by_id(conn, x_dev_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Pengguna dengan ID {x_dev_user_id} tidak ditemukan.",
            )
        return user


def verify_session_ownership(session: dict[str, Any], user: dict[str, Any]) -> None:
    """Memeriksa kepemilikan sesi: mahasiswa hanya boleh mengakses sesinya sendiri."""
    user_role = user.get("role")
    # Admin dan dosen pembimbing memiliki hak akses peninjauan
    if user_role in ("admin", "lecturer"):
        return

    if session.get("student_id") != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk mengakses sesi simulasi ini.",
        )
