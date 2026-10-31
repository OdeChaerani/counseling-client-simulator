from __future__ import annotations

from fastapi import APIRouter
from api.v1.sessions import router as sessions_router
from api.v1.system import router as system_router

api_v1_router = APIRouter()
api_v1_router.include_router(system_router)
api_v1_router.include_router(sessions_router)

__all__ = ["api_v1_router"]
