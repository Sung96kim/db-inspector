import asyncpg

from inspector.config import ConnectionConfig

_pool: asyncpg.Pool | None = None


async def create_pool(config: ConnectionConfig) -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(config.url, min_size=1, max_size=4)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool | None:
    return _pool
