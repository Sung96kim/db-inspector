from textual.widgets import DataTable

from inspector.db.database import QueryRow


def cell_to_text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def populate_data_table(
    table: DataTable, columns: list[str], rows: list[QueryRow]
) -> None:
    table.clear(columns=True)
    if not columns:
        return
    table.add_columns(*columns)
    for row in rows:
        table.add_row(*[cell_to_text(row.get(column)) for column in columns])
