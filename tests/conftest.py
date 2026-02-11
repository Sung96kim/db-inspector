from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from inspector.config import ConnectionConfig


@pytest.fixture
def connection_config() -> ConnectionConfig:
    return ConnectionConfig(url="postgres://user:pass@localhost:5432/testdb")


@pytest.fixture
def mock_conn() -> AsyncMock:
    conn = AsyncMock()
    return conn


@pytest.fixture
def mock_pool(mock_conn: AsyncMock) -> MagicMock:
    pool = MagicMock()
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    ctx.__aexit__ = AsyncMock(return_value=None)
    pool.acquire = MagicMock(return_value=ctx)
    return pool


@pytest.fixture
def sample_schema_rows() -> list[dict[str, Any]]:
    return [{"name": "public"}, {"name": "information_schema"}]


@pytest.fixture
def sample_table_rows() -> list[dict[str, Any]]:
    return [
        {"schema_name": "public", "table_name": "users"},
        {"schema_name": "public", "table_name": "posts"},
    ]


@pytest.fixture
def sample_column_rows() -> list[dict[str, Any]]:
    return [
        {"column_name": "id", "data_type": "integer", "is_nullable": "NO"},
        {"column_name": "name", "data_type": "text", "is_nullable": "YES"},
    ]


@pytest.fixture
def sample_query_rows() -> list[dict[str, Any]]:
    return [
        {"id": 1, "name": "a"},
        {"id": 2, "name": "b"},
    ]
