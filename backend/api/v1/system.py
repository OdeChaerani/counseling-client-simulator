from __future__ import annotations

from typing import Any
import asyncpg
from fastapi import APIRouter, Request

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check(request: Request) -> dict[str, Any]:
    """Pemeriksaan kesehatan server dan koneksi PostgreSQL."""
    pool: asyncpg.Pool | None = getattr(request.app.state, "db_pool", None)
    if not pool:
        return {
            "status": "ok",
            "database": {
                "connected": False,
                "status": "uninitialized",
                "message": "Database pool belum diinisialisasi",
            },
        }

    try:
        async with pool.acquire() as conn:
            val = await conn.fetchval("SELECT 1")
            return {
                "status": "ok",
                "database": {
                    "connected": val == 1,
                    "status": "ready" if val == 1 else "error",
                    "message": "Berhasil terhubung ke database SafeSesi PostgreSQL",
                },
            }
    except Exception as exc:
        return {
            "status": "ok",
            "database": {
                "connected": False,
                "status": "error",
                "message": f"Koneksi database gagal: {exc}",
            },
        }


@router.get("/api/data")
async def read_root() -> dict[str, str]:
    """Sanity check endpoint."""
    return {"message": "Halo dari Counseling Client Simulator API!"}
