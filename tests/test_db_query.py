from unittest.mock import AsyncMock

import pytest

from inspector.db import connection as conn_module
from inspector.db.query import run_query


@pytest.fixture(autouse=True)
def reset_pool() -> None:
    conn_module._pool = None
    yield
    conn_module._pool = None


class TestRunQuery:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_pool(self) -> None:
        columns, data = await run_query("SELECT 1")
        assert columns == []
        assert data == []

    @pytest.mark.asyncio
    async def test_returns_columns_and_rows(
        self, mock_pool: object, sample_query_rows: list[dict]
    ) -> None:
        conn_module._pool = mock_pool
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch = AsyncMock(return_value=sample_query_rows)
        columns, data = await run_query("SELECT id, name FROM t")
        assert columns == ["id", "name"]
        assert data == sample_query_rows
        mock_conn.fetch.assert_awaited_once_with("SELECT id, name FROM t")

    @pytest.mark.asyncio
    async def test_returns_empty_columns_and_data_when_no_rows(
        self, mock_pool: object
    ) -> None:
        conn_module._pool = mock_pool
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch = AsyncMock(return_value=[])
        columns, data = await run_query("SELECT 1 WHERE FALSE")
        assert columns == []
        assert data == []
