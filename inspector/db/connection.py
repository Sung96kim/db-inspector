from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from inspector.config import ConnectionConfig


class SessionProvider:
    def __init__(
        self,
        config: ConnectionConfig | None = None,
        pool_size: int = 4,
        max_overflow: int = 8,
    ) -> None:
        self._config = config
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def create_engine(self, config: ConnectionConfig | None = None) -> AsyncEngine:
        if config is not None:
            self._config = config
        if self._config is None:
            raise RuntimeError("Database configuration is not set.")
        self._engine = create_async_engine(
            self._config.url,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        return self._engine

    async def close_engine(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    def get_engine(self) -> AsyncEngine | None:
        return self._engine

    @asynccontextmanager
    async def open(self) -> AsyncIterator[AsyncSession]:
        if self._session_factory is None:
            await self.create_engine()
        if self._session_factory is None:
            raise RuntimeError("Database session factory is not initialized.")
        async with self._session_factory() as session:
            yield session
