from pydantic import BaseModel, Field

from inspector.db.connection import get_pool


class SchemaInfo(BaseModel):
    name: str = Field(..., description="Schema name")


class TableInfo(BaseModel):
    schema_name: str = Field(..., description="Schema name")
    table_name: str = Field(..., description="Table name")


class ColumnInfo(BaseModel):
    column_name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Data type")
    is_nullable: str = Field(..., description="YES or NO")


async def list_columns(schema_name: str, table_name: str) -> list[ColumnInfo]:
    pool = get_pool()
    if pool is None:
        return []
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
            """,
            schema_name,
            table_name,
        )
    return [ColumnInfo.model_validate(dict(r)) for r in rows]


async def list_schemas() -> list[SchemaInfo]:
    pool = get_pool()
    if pool is None:
        return []
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT schema_name AS name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('pg_toast', 'pg_temp_1', 'pg_toast_temp_1')
            ORDER BY schema_name
            """
        )
    return [SchemaInfo.model_validate(dict(r)) for r in rows]


async def list_tables(schema_name: str) -> list[TableInfo]:
    pool = get_pool()
    if pool is None:
        return []
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT table_schema AS schema_name, table_name AS table_name
            FROM information_schema.tables
            WHERE table_schema = $1 AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            schema_name,
        )
    return [TableInfo.model_validate(dict(r)) for r in rows]
