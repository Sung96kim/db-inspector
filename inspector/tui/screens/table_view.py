from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from inspector.db.metadata import list_columns
from inspector.db.query import QueryRow, run_query
from inspector.tui.screens.query_runner import QueryRunnerScreen

PAGE_SIZE = 100


def _cell(val: object) -> str:
    if val is None:
        return ""
    return str(val)


def _add_row(table: DataTable, cols: list[str], row: QueryRow) -> None:
    table.add_row(*[_cell(row.get(c)) for c in cols])


class TableViewScreen(Screen[None]):
    BINDINGS = [
        ("n", "next_page", "Next page"),
        ("p", "prev_page", "Prev page"),
        ("q", "query", "Query"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, schema_name: str, table_name: str) -> None:
        super().__init__()
        self._schema_name = schema_name
        self._table_name = table_name
        self._offset = 0
        self._columns: list[str] = []
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
        self.run_worker(self._load_metadata_and_data(), exclusive=True)

    async def _load_metadata_and_data(self) -> None:
        status = self.query_one("#table-status", Static)
        status.update("Loading...")
        await list_columns(self._schema_name, self._table_name)
        quoted_schema = f'"{self._schema_name}"'
        quoted_table = f'"{self._table_name}"'
        sql = f"SELECT * FROM {quoted_schema}.{quoted_table} LIMIT {PAGE_SIZE} OFFSET {self._offset}"
        cols, rows = await run_query(sql)
        self._columns = cols
        self._total_loaded = len(rows)
        table = self.query_one("#table-data", DataTable)
        table.clear(columns=True)
        if cols:
            table.add_columns(*cols)
            for row in rows:
                _add_row(table, cols, row)
        status.update(
            f"Rows {self._offset + 1}-{self._offset + self._total_loaded} "
            f"(limit {PAGE_SIZE})"
        )

    def action_next_page(self) -> None:
        self._offset += PAGE_SIZE
        self.run_worker(self._load_page(), exclusive=True)

    def action_prev_page(self) -> None:
        if self._offset > 0:
            self._offset = max(0, self._offset - PAGE_SIZE)
            self.run_worker(self._load_page(), exclusive=True)

    async def _load_page(self) -> None:
        quoted_schema = f'"{self._schema_name}"'
        quoted_table = f'"{self._table_name}"'
        sql = f"SELECT * FROM {quoted_schema}.{quoted_table} LIMIT {PAGE_SIZE} OFFSET {self._offset}"
        cols, rows = await run_query(sql)
        self._total_loaded = len(rows)
        table = self.query_one("#table-data", DataTable)
        table.clear(columns=True)
        if cols:
            table.add_columns(*cols)
            for row in rows:
                _add_row(table, cols, row)
        status = self.query_one("#table-status", Static)
        status.update(
            f"Rows {self._offset + 1}-{self._offset + self._total_loaded} "
            f"(limit {PAGE_SIZE})"
        )

    def action_query(self) -> None:
        self.app.push_screen(QueryRunnerScreen())

    def action_back(self) -> None:
        self.app.pop_screen()
