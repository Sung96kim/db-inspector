from unittest.mock import AsyncMock, patch

import pytest

from inspector.config import ConnectionConfig
from inspector.db import connection as conn_module
from inspector.db.connection import close_pool, create_pool, get_pool


@pytest.fixture(autouse=True)
def reset_pool() -> None:
    conn_module._pool = None
    yield
    conn_module._pool = None


class TestGetPool:
    def test_returns_none_when_no_pool(self) -> None:
        assert get_pool() is None


class TestCreatePoolAndClosePool:
    @pytest.mark.asyncio
    async def test_create_pool_sets_global_and_returns_pool(
        self, connection_config: ConnectionConfig
    ) -> None:
        mock_pool = AsyncMock()
        with patch.object(conn_module, "asyncpg") as mock_asyncpg:
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
            pool = await create_pool(connection_config)
        assert pool is mock_pool
        assert get_pool() is mock_pool
        mock_asyncpg.create_pool.assert_awaited_once_with(
            connection_config.url, min_size=1, max_size=4
        )

    @pytest.mark.asyncio
    async def test_close_pool_clears_global(
        self, connection_config: ConnectionConfig
    ) -> None:
        mock_pool = AsyncMock()
        with patch.object(conn_module, "asyncpg") as mock_asyncpg:
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
            await create_pool(connection_config)
        assert get_pool() is mock_pool
        await close_pool()
        assert get_pool() is None
        mock_pool.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_pool_idempotent_when_no_pool(self) -> None:
        await close_pool()
        assert get_pool() is None
