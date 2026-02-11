from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static, Tree
from textual.widgets.tree import TreeNode

from inspector.db.database import DatabaseProvider
from inspector.tui.screens.query_runner import QueryRunnerScreen
from inspector.tui.screens.table_view import TableViewScreen


class SchemaBrowserScreen(Screen[None]):
    BINDINGS = [
        ("q", "query", "Query"),
        ("escape", "back", "Back"),
    ]

    def __init__(
        self,
        database_provider: DatabaseProvider,
    ) -> None:
        super().__init__()
        self._database_provider = database_provider

    def compose(self) -> ComposeResult:
        tree = Tree("Schemas", id="schema-tree")
        tree.show_root = True
        tree.root.expand()
        yield Horizontal(
            Vertical(
                Static("Schemas & Tables", classes="panel-title"),
                tree,
                id="schema-panel",
            ),
            Vertical(
                Static("Select a table (Enter) or open Query (q)", id="schema-hint"),
                id="content-panel",
            ),
            id="browser-layout",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_schemas(), exclusive=True)

    async def _load_schemas(self) -> None:
        tree = self.query_one("#schema-tree", Tree)
        schemas = await self._database_provider.list_schemas()
        for s in schemas:
            tree.root.add(s.name, expand=False)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        node = event.node
        if not node.children:
            schema_name = str(node.label).strip()
            self.run_worker(self._load_tables(node, schema_name), exclusive=False)

    async def _load_tables(self, schema_node: TreeNode, schema_name: str) -> None:
        tables = await self._database_provider.list_tables(schema_name)
        for t in tables:
            schema_node.add_leaf(t.table_name)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        tree = self.query_one("#schema-tree", Tree)
        if (
            node.parent is not None
            and node.parent is not tree.root
            and not node.allow_expand
        ):
            schema_name = str(node.parent.label).strip()
            table_name = str(node.label).strip()
            self.app.push_screen(
                TableViewScreen(
                    schema_name=schema_name,
                    table_name=table_name,
                    database_provider=self._database_provider,
                )
            )

    def action_query(self) -> None:
        self.app.push_screen(QueryRunnerScreen(database_provider=self._database_provider))

    def action_back(self) -> None:
        self.app.exit()
