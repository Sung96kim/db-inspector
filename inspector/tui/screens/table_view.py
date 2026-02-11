from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from inspector.db.database import DatabaseProvider
from inspector.tui.screens.query_runner import QueryRunnerScreen
from inspector.tui.widgets.table_helpers import populate_data_table

PAGE_SIZE = 100


def _quote_identifier(identifier: str) -> str:
    escaped = identifier.replace('"', '""')
    return f'"{escaped}"'


def _format_status(offset: int, loaded_rows: int) -> str:
    if loaded_rows == 0:
        return f"Rows 0 (offset {offset}, limit {PAGE_SIZE})"
    start = offset + 1
    end = offset + loaded_rows
    return f"Rows {start}-{end} (limit {PAGE_SIZE})"


class TableViewScreen(Screen[None]):
    BINDINGS = [
        ("n", "next_page", "Next page"),
        ("p", "prev_page", "Prev page"),
        ("q", "query", "Query"),
        ("escape", "back", "Back"),
    ]

    def __init__(
        self,
        schema_name: str,
        table_name: str,
        database_provider: DatabaseProvider,
    ) -> None:
        super().__init__()
        self._schema_name = schema_name
        self._table_name = table_name
        self._database_provider = database_provider
        self._offset = 0
        self._total_loaded = 0

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(f"Table: {self._schema_name}.{self._table_name}", id="table-header"),
            DataTable(id="table-data", cursor_type="row"),
            Static("", id="table-status"),
            id="table-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_initial_view(), exclusive=True)

    async def _load_initial_view(self) -> None:
        status = self.query_one("#table-status", Static)
        status.update("Loading...")
        await self._database_provider.list_columns(self._schema_name, self._table_name)
        await self._load_page()

    def _build_page_query(self) -> str:
        quoted_schema = _quote_identifier(self._schema_name)
        quoted_table = _quote_identifier(self._table_name)
        return (
            f"SELECT * FROM {quoted_schema}.{quoted_table} "
            f"LIMIT {PAGE_SIZE} OFFSET {self._offset}"
        )

    def action_next_page(self) -> None:
        self._offset += PAGE_SIZE
        self.run_worker(self._load_page(), exclusive=True)

    def action_prev_page(self) -> None:
        if self._offset > 0:
            self._offset = max(0, self._offset - PAGE_SIZE)
            self.run_worker(self._load_page(), exclusive=True)

    async def _load_page(self) -> None:
        sql = self._build_page_query()
        cols, rows = await self._database_provider.run_query(sql)
        self._total_loaded = len(rows)
        table = self.query_one("#table-data", DataTable)
        populate_data_table(table, cols, rows)
        status = self.query_one("#table-status", Static)
        status.update(_format_status(self._offset, self._total_loaded))

    def action_query(self) -> None:
        self.app.push_screen(QueryRunnerScreen(database_provider=self._database_provider))

    def action_back(self) -> None:
        self.app.pop_screen()
