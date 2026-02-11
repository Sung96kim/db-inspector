from typing import TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SchemaInfo(BaseModel):
    name: str = Field(..., description="Schema name")


class TableInfo(BaseModel):
    schema_name: str = Field(..., description="Schema name")
    table_name: str = Field(..., description="Table name")


class ColumnInfo(BaseModel):
    column_name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Data type")
    is_nullable: str = Field(..., description="YES or NO")


_ModelT = TypeVar("_ModelT", bound=BaseModel)


class MetadataProvider:
    def __init__(self) -> None:
        self._schema_cache: tuple[SchemaInfo, ...] | None = None
        self._table_cache: dict[str, tuple[TableInfo, ...]] = {}
        self._column_cache: dict[tuple[str, str], tuple[ColumnInfo, ...]] = {}

    def _copy_models(self, rows: tuple[_ModelT, ...]) -> list[_ModelT]:
        return [row.model_copy(deep=True) for row in rows]

    def _reset_caches(self) -> None:
        self._schema_cache = None
        self._table_cache.clear()
        self._column_cache.clear()

    def clear_cache(self) -> None:
        self._reset_caches()

    async def list_columns(
        self, session: AsyncSession, schema_name: str, table_name: str
    ) -> list[ColumnInfo]:
        key = (schema_name, table_name)
        cached = self._column_cache.get(key)
        if cached is not None:
            return self._copy_models(cached)
        result = await session.execute(
            text(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = :schema_name AND table_name = :table_name
                ORDER BY ordinal_position
                """
            ),
            {"schema_name": schema_name, "table_name": table_name},
        )
        rows = result.mappings().all()
        parsed = tuple(ColumnInfo.model_validate(dict(r)) for r in rows)
        self._column_cache[key] = parsed
        return self._copy_models(parsed)

    async def list_schemas(self, session: AsyncSession) -> list[SchemaInfo]:
        if self._schema_cache is not None:
            return self._copy_models(self._schema_cache)
        result = await session.execute(
            text(
                """
                SELECT schema_name AS name
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_toast', 'pg_temp_1', 'pg_toast_temp_1')
                ORDER BY schema_name
                """
            )
        )
        rows = result.mappings().all()
        parsed = tuple(SchemaInfo.model_validate(dict(r)) for r in rows)
        self._schema_cache = parsed
        return self._copy_models(parsed)

    async def list_tables(self, session: AsyncSession, schema_name: str) -> list[TableInfo]:
        cached = self._table_cache.get(schema_name)
        if cached is not None:
            return self._copy_models(cached)
        result = await session.execute(
            text(
                """
                SELECT table_schema AS schema_name, table_name AS table_name
                FROM information_schema.tables
                WHERE table_schema = :schema_name AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            ),
            {"schema_name": schema_name},
        )
        rows = result.mappings().all()
        parsed = tuple(TableInfo.model_validate(dict(r)) for r in rows)
        self._table_cache[schema_name] = parsed
        return self._copy_models(parsed)
