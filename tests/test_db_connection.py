from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from inspector.config import ConnectionConfig
from inspector.db.connection import SessionProvider
from tests.conftest import MockSessionProvider


class TestSessionProvider:
    def test_get_engine_returns_none_when_not_initialized(self) -> None:
        provider = SessionProvider()
        assert provider.get_engine() is None

    @pytest.mark.asyncio
    async def test_create_engine_sets_and_returns_engine(
        self, connection_config: ConnectionConfig
    ) -> None:
        mock_engine = AsyncMock()
        mock_session_factory = MagicMock()
        provider = SessionProvider()
        with patch(
            "inspector.db.connection.create_async_engine", return_value=mock_engine
        ) as create_engine_mock:
            with patch(
                "inspector.db.connection.async_sessionmaker",
                return_value=mock_session_factory,
            ):
                engine = await provider.create_engine(connection_config)
        assert engine is mock_engine
        assert provider.get_engine() is mock_engine
        create_engine_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_engine_disposes_and_clears_engine(
        self, connection_config: ConnectionConfig
    ) -> None:
        mock_engine = AsyncMock()
        provider = SessionProvider()
        with patch("inspector.db.connection.create_async_engine", return_value=mock_engine):
            with patch("inspector.db.connection.async_sessionmaker"):
                await provider.create_engine(connection_config)
        assert provider.get_engine() is mock_engine
        await provider.close_engine()
        assert provider.get_engine() is None
        mock_engine.dispose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_engine_idempotent(self) -> None:
        provider = SessionProvider()
        await provider.close_engine()
        assert provider.get_engine() is None

    @pytest.mark.asyncio
    async def test_open_raises_when_engine_missing(self) -> None:
        provider = SessionProvider()
        with pytest.raises(RuntimeError, match="configuration is not set"):
            async with provider.open():
                pass

    @pytest.mark.asyncio
    async def test_open_lazily_creates_engine_with_config(
        self, connection_config: ConnectionConfig
    ) -> None:
        mock_engine = MagicMock()
        mock_session = AsyncMock()

        class _SessionContext:
            async def __aenter__(self):
                return mock_session

            async def __aexit__(self, exc_type, exc, tb):
                return False

        session_factory = MagicMock(return_value=_SessionContext())
        provider = SessionProvider(config=connection_config)
        with patch(
            "inspector.db.connection.create_async_engine", return_value=mock_engine
        ):
            with patch(
                "inspector.db.connection.async_sessionmaker",
                return_value=session_factory,
            ):
                async with provider.open() as session:
                    assert session is mock_session

    @pytest.mark.asyncio
    async def test_open_yields_session(
        self, mock_engine: MagicMock, mock_session: AsyncMock
    ) -> None:
        provider = MockSessionProvider(mock_engine, mock_session)
        async with provider.open() as session:
            assert session is mock_session
