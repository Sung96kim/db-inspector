import pytest

from inspector.db.database import run_query


class TestRunQuery:
    @pytest.mark.asyncio
    async def test_returns_columns_and_rows(
        self,
        mock_session: object,
        mock_result: object,
        sample_query_rows: list[dict],
    ) -> None:
        mock_result.keys.return_value = ["id", "name"]
        mock_result.returns_rows = True
        mock_result.mappings.return_value.all.return_value = sample_query_rows
        columns, data = await run_query(mock_session, "SELECT id, name FROM t")
        assert columns == ["id", "name"]
        assert data == sample_query_rows
        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_empty_columns_and_data_when_no_rows(
        self,
        mock_session: object,
        mock_result: object,
    ) -> None:
        mock_result.keys.return_value = ["id"]
        mock_result.returns_rows = True
        mock_result.mappings.return_value.all.return_value = []
        columns, data = await run_query(mock_session, "SELECT 1 WHERE FALSE")
        assert columns == ["id"]
        assert data == []

    @pytest.mark.asyncio
    async def test_raises_for_mutating_statement(
        self,
        mock_session: object,
    ) -> None:
        with pytest.raises(ValueError, match="read-only"):
            await run_query(mock_session, "CREATE TABLE t(id int)")
        mock_session.execute.assert_not_called()
