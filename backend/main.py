from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncpg
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.v1 import api_v1_router
from core.config import get_settings
from core.errors import SafeSesiError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safesesi")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager untuk mengelola asyncpg connection pool."""
    settings = get_settings()
    pool: asyncpg.Pool | None = None

    if settings.DATABASE_URL:
        try:
            logger.info("Menginisialisasi connection pool asyncpg...")
            # statement_cache_size=0 diatur untuk kompatibilitas penuh dengan Supabase Transaction Pooler
            pool = await asyncio.wait_for(
                asyncpg.create_pool(
                    dsn=settings.DATABASE_URL,
                    statement_cache_size=0,
                    min_size=1,
                    max_size=10,
                ),
                timeout=3.0,
            )
            app.state.db_pool = pool
            logger.info("Connection pool asyncpg berhasil diinisialisasi.")
        except Exception as exc:
            logger.warning("Gagal menginisialisasi connection pool asyncpg: %s", exc)
            app.state.db_pool = None
    else:
        logger.info("DATABASE_URL kosong. db_pool disetel ke None.")
        app.state.db_pool = None

    yield

    if pool is not None:
        logger.info("Menutup connection pool asyncpg...")
        await pool.close()
        logger.info("Connection pool asyncpg telah ditutup.")


settings = get_settings()

app = FastAPI(
    title="SafeSesi Backend API",
    description="Backend simulasi klien virtual konseling Motivational Interviewing (MI) SafeSesi.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SafeSesiError)
async def safesesi_error_handler(request: Request, exc: SafeSesiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


# Registrasi router sistem dan API v1
app.include_router(api_v1_router, prefix="")
app.include_router(api_v1_router, prefix="/api/v1")
