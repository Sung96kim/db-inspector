import asyncio
from typing import Annotated

import typer

from inspector.app import PgInspectorApp
from inspector.config import ConnectionConfig, PgInspectorSettings
from inspector.db.connection import SessionProvider
from inspector.db.database import DatabaseProvider

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
    session_provider = SessionProvider(config=config)
    database_provider = DatabaseProvider(session_provider)
    await session_provider.create_engine(config)
    try:
        inspector_app = PgInspectorApp(config, database_provider)
        inspector_app.run()
    finally:
        await session_provider.close_engine()


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
