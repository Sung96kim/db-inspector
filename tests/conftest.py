from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from inspector.config import ConnectionConfig
from inspector.db.connection import SessionProvider


@pytest.fixture
def connection_config() -> ConnectionConfig:
    return ConnectionConfig(url="postgresql+asyncpg://user:pass@localhost:5432/testdb")


@pytest.fixture
def mock_engine() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_result() -> MagicMock:
    result = MagicMock()
    result.returns_rows = True
    result.keys.return_value = []
    mappings = MagicMock()
    mappings.all.return_value = []
    result.mappings.return_value = mappings
    return result


@pytest.fixture
def mock_session(mock_result: MagicMock) -> AsyncMock:
    session = AsyncMock()
    session.execute = AsyncMock(return_value=mock_result)
    session.commit = AsyncMock()
    return session


class MockSessionProvider(SessionProvider):
    def __init__(self, engine: object | None, session: object) -> None:
        super().__init__()
        self._mock_engine = engine
        self._mock_session = session

    async def create_engine(self, config: ConnectionConfig | None = None) -> object:
        return self._mock_engine

    async def close_engine(self) -> None:
        self._mock_engine = None

    def get_engine(self) -> object | None:
        return self._mock_engine

    @asynccontextmanager
    async def open(self) -> AsyncIterator[object]:
        if self._mock_engine is None:
            raise RuntimeError("Database engine is not initialized.")
        yield self._mock_session


@pytest.fixture
def mock_session_provider(
    mock_engine: MagicMock, mock_session: AsyncMock
) -> MockSessionProvider:
    return MockSessionProvider(mock_engine, mock_session)


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
