from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from inspector.db.connection import SessionProvider
from inspector.db.metadata import MetadataProvider

QueryRow = dict[str, Any]
QueryResult = tuple[list[str], list[QueryRow]]

_MUTATING_SQL_PREFIXES = {
    "ALTER",
    "COMMENT",
    "CREATE",
    "DELETE",
    "DROP",
    "GRANT",
    "INSERT",
    "REVOKE",
    "TRUNCATE",
    "UPDATE",
}


def _is_mutating_sql(sql: str) -> bool:
    normalized = sql.lstrip()
    if not normalized:
        return False
    first_token = normalized.split(maxsplit=1)[0].upper()
    return first_token in _MUTATING_SQL_PREFIXES


async def run_query(session: AsyncSession, sql: str) -> QueryResult:
    if _is_mutating_sql(sql):
        raise ValueError("Only read-only queries are allowed in inspector mode.")

    result = await session.execute(text(sql))

    if not result.returns_rows:
        return [], []

    columns = list(result.keys())
    rows = result.mappings().all()
    if not rows:
        return columns, []

    return columns, [dict(r) for r in rows]


class DatabaseProvider:
    def __init__(
        self,
        session_provider: SessionProvider,
        metadata_provider: MetadataProvider | None = None,
    ) -> None:
        self._session_provider = session_provider
        self._metadata_provider = metadata_provider or MetadataProvider()

    async def list_schemas(self):
        async with self._session_provider.open() as session:
            return await self._metadata_provider.list_schemas(session)

    async def list_tables(self, schema_name: str):
        async with self._session_provider.open() as session:
            return await self._metadata_provider.list_tables(session, schema_name)

    async def list_columns(self, schema_name: str, table_name: str):
        async with self._session_provider.open() as session:
            return await self._metadata_provider.list_columns(
                session, schema_name, table_name
            )

    async def run_query(self, sql: str) -> QueryResult:
        async with self._session_provider.open() as session:
            return await run_query(session, sql)

    def clear_metadata_cache(self) -> None:
        self._metadata_provider.clear_cache()
