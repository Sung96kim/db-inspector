import asyncio
from typing import Annotated

import typer

from inspector.app import PgInspectorApp
from inspector.config import ConnectionConfig, PgInspectorSettings
from inspector.db.connection import close_pool, create_pool

app = typer.Typer(help="PostgreSQL CLI visual inspector.")


def _get_connection_config(
    connection: str | None,
) -> ConnectionConfig:
    settings = PgInspectorSettings()
    url = connection or settings.database_url
    if not url:
        typer.echo("Error: Set DATABASE_URL or pass -c/--connection.", err=True)
        raise typer.Exit(1)
    return ConnectionConfig(url=url)


async def _run_tui(config: ConnectionConfig) -> None:
    await create_pool(config)
    try:
        inspector_app = PgInspectorApp(config)
        inspector_app.run()
    finally:
        await close_pool()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    connection: Annotated[
        str | None,
        typer.Option("--connection", "-c", help="PostgreSQL connection URL."),
    ] = None,
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    config = _get_connection_config(connection)
    asyncio.run(_run_tui(config))


if __name__ == "__main__":
    app()
