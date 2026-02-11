from typing import Any

from inspector.db.connection import get_pool

QueryRow = dict[str, Any]
QueryResult = tuple[list[str], list[QueryRow]]


async def run_query(sql: str) -> QueryResult:
    pool = get_pool()
    if pool is None:
        return [], []
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql)
    if not rows:
        return [], []
    columns = list(rows[0].keys())
    data = [dict(r) for r in rows]
    return columns, data
