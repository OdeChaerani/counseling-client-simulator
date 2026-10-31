from __future__ import annotations

import asyncio
from typing import Any

# Registry lock per sesi untuk serialisasi pemrosesan turn dalam satu sesi
_SESSION_LOCKS: dict[int, asyncio.Lock] = {}
_GLOBAL_LOCK = asyncio.Lock()


async def get_session_lock(session_id: int) -> asyncio.Lock:
    """Mengembalikan asyncio.Lock untuk session_id guna mencegah pemrosesan turn konkuren dalam sesi yang sama."""
    async with _GLOBAL_LOCK:
        if session_id not in _SESSION_LOCKS:
            _SESSION_LOCKS[session_id] = asyncio.Lock()
        return _SESSION_LOCKS[session_id]

