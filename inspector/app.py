from textual.app import App, ComposeResult
from textual.containers import Container

from inspector.config import ConnectionConfig
from inspector.db.database import DatabaseProvider, QueryRow
from inspector.tui.screens.schema_browser import SchemaBrowserScreen


class PgInspectorApp(App[None]):
    CSS = """
    #browser-layout {
        width: 100%;
        height: 100%;
    }
    #schema-panel {
        width: 30%;
        min-width: 20;
        height: 100%;
        border-right: solid primary;
    }
    #content-panel {
        width: 1fr;
        height: 100%;
    }
    .panel-title {
        text-style: bold;
        padding: 1;
    }
    #table-container {
        height: 100%;
        padding: 1;
    }
    #query-container {
        height: 100%;
        padding: 1;
    }
    """

    def __init__(
        self,
        config: ConnectionConfig,
        database_provider: DatabaseProvider,
    ) -> None:
        super().__init__()
        self._config = config
        self._database_provider = database_provider
        self._current_schema: str | None = None
        self._current_table: str | None = None
        self._query_text: str = ""
        self._result_columns: list[str] = []
        self._result_rows: list[QueryRow] = []

    @property
    def config(self) -> ConnectionConfig:
        return self._config

    def on_mount(self) -> None:
        self.push_screen(
            SchemaBrowserScreen(
                database_provider=self._database_provider,
            )
        )

    def compose(self) -> ComposeResult:
        yield Container()
