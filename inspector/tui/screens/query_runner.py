from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static, TextArea

from inspector.db.query import run_query


def _cell(val: object) -> str:
    if val is None:
        return ""
    return str(val)


class QueryRunnerScreen(Screen[None]):
    BINDINGS = [
        ("ctrl+enter", "run_query", "Run"),
        ("escape", "back", "Back"),
    ]

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
            columns, rows = await run_query(sql)
            table = self.query_one("#query-results", DataTable)
            table.clear(columns=True)
            if columns:
                table.add_columns(*columns)
                for row in rows:
                    table.add_row(*[_cell(row.get(c)) for c in columns])
            status.update(f"Rows: {len(rows)}")
        except Exception as e:  # noqa: BLE001
            status.update(f"Error: {e!s}")

    def action_back(self) -> None:
        self.app.pop_screen()
