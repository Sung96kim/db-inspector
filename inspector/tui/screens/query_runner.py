from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static, TextArea

from inspector.db.database import DatabaseProvider
from inspector.tui.widgets.table_helpers import populate_data_table


class QueryRunnerScreen(Screen[None]):
    BINDINGS = [
        ("ctrl+enter", "run_query", "Run"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, database_provider: DatabaseProvider) -> None:
        super().__init__()
        self._database_provider = database_provider

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("SQL (Ctrl+Enter to run)", id="query-label"),
            TextArea(id="query-input"),
            Static("Results", id="results-label"),
            DataTable(id="query-results", cursor_type="row"),
            Static("", id="query-status"),
            id="query-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#query-input", TextArea).focus()

    def action_run_query(self) -> None:
        ta = self.query_one("#query-input", TextArea)
        sql = (ta.text or "").strip()
        if not sql:
            return
        self.run_worker(self._execute(sql), exclusive=True)

    async def _execute(self, sql: str) -> None:
        status = self.query_one("#query-status", Static)
        status.update("Running...")
        try:
            columns, rows = await self._database_provider.run_query(sql)
            table = self.query_one("#query-results", DataTable)
            populate_data_table(table, columns, rows)
            status.update(f"Rows: {len(rows)}")
        except Exception as e:  # noqa: BLE001
            status.update(f"Error: {e!s}")

    def action_back(self) -> None:
        self.app.pop_screen()
