from unittest.mock import AsyncMock

import pytest

from inspector.db import connection as conn_module
from inspector.db.metadata import (
    ColumnInfo,
    SchemaInfo,
    TableInfo,
    list_columns,
    list_schemas,
    list_tables,
)


@pytest.fixture(autouse=True)
def reset_pool() -> None:
    conn_module._pool = None
    yield
    conn_module._pool = None


class TestListSchemas:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_pool(self) -> None:
        result = await list_schemas()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_schemas_from_pool(
        self, mock_pool: object, sample_schema_rows: list[dict]
    ) -> None:
        conn_module._pool = mock_pool
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch = AsyncMock(return_value=sample_schema_rows)
        result = await list_schemas()
        assert result == [SchemaInfo.model_validate(r) for r in sample_schema_rows]
        mock_conn.fetch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_filters_and_orders_schema_names(
        self, mock_pool: object, sample_schema_rows: list[dict]
    ) -> None:
        conn_module._pool = mock_pool
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch = AsyncMock(return_value=sample_schema_rows)
        result = await list_schemas()
        assert [r.name for r in result] == ["public", "information_schema"]


class TestListTables:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_pool(self) -> None:
        result = await list_tables("public")
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_tables_for_schema(
        self, mock_pool: object, sample_table_rows: list[dict]
    ) -> None:
        conn_module._pool = mock_pool
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch = AsyncMock(return_value=sample_table_rows)
        result = await list_tables("public")
        assert result == [TableInfo.model_validate(r) for r in sample_table_rows]
        mock_conn.fetch.assert_awaited_once_with(
            """
            SELECT table_schema AS schema_name, table_name AS table_name
            FROM information_schema.tables
            WHERE table_schema = $1 AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            "public",
        )


class TestListColumns:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_pool(self) -> None:
        result = await list_columns("public", "users")
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_columns_for_table(
        self, mock_pool: object, sample_column_rows: list[dict]
    ) -> None:
        conn_module._pool = mock_pool
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch = AsyncMock(return_value=sample_column_rows)
        result = await list_columns("public", "users")
        assert result == [ColumnInfo.model_validate(r) for r in sample_column_rows]
        mock_conn.fetch.assert_awaited_once_with(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
            """,
            "public",
            "users",
        )
