from unittest.mock import MagicMock

import pytest

from inspector.db.metadata import ColumnInfo, MetadataProvider, SchemaInfo, TableInfo


@pytest.fixture
def metadata_provider() -> MetadataProvider:
    return MetadataProvider()


class TestListSchemas:
    @pytest.mark.asyncio
    async def test_returns_schemas_from_session(
        self,
        metadata_provider: MetadataProvider,
        mock_session: object,
        mock_result: MagicMock,
        sample_schema_rows: list[dict],
    ) -> None:
        mock_result.mappings.return_value.all.return_value = sample_schema_rows
        result = await metadata_provider.list_schemas(mock_session)
        assert result == [SchemaInfo.model_validate(r) for r in sample_schema_rows]
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uses_cache_for_subsequent_calls(
        self,
        metadata_provider: MetadataProvider,
        mock_session: object,
        mock_result: MagicMock,
        sample_schema_rows: list[dict],
    ) -> None:
        mock_result.mappings.return_value.all.return_value = sample_schema_rows
        first = await metadata_provider.list_schemas(mock_session)
        second = await metadata_provider.list_schemas(mock_session)
        assert first == second
        mock_session.execute.assert_awaited_once()


class TestListTables:
    @pytest.mark.asyncio
    async def test_returns_tables_for_schema(
        self,
        metadata_provider: MetadataProvider,
        mock_session: object,
        mock_result: MagicMock,
        sample_table_rows: list[dict],
    ) -> None:
        mock_result.mappings.return_value.all.return_value = sample_table_rows
        result = await metadata_provider.list_tables(mock_session, "public")
        assert result == [TableInfo.model_validate(r) for r in sample_table_rows]
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uses_schema_scoped_cache(
        self,
        metadata_provider: MetadataProvider,
        mock_session: object,
        mock_result: MagicMock,
        sample_table_rows: list[dict],
    ) -> None:
        mock_result.mappings.return_value.all.return_value = sample_table_rows
        first = await metadata_provider.list_tables(mock_session, "public")
        second = await metadata_provider.list_tables(mock_session, "public")
        assert first == second
        mock_session.execute.assert_awaited_once()


class TestListColumns:
    @pytest.mark.asyncio
    async def test_returns_columns_for_table(
        self,
        metadata_provider: MetadataProvider,
        mock_session: object,
        mock_result: MagicMock,
        sample_column_rows: list[dict],
    ) -> None:
        mock_result.mappings.return_value.all.return_value = sample_column_rows
        result = await metadata_provider.list_columns(mock_session, "public", "users")
        assert result == [ColumnInfo.model_validate(r) for r in sample_column_rows]
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uses_table_scoped_cache(
        self,
        metadata_provider: MetadataProvider,
        mock_session: object,
        mock_result: MagicMock,
        sample_column_rows: list[dict],
    ) -> None:
        mock_result.mappings.return_value.all.return_value = sample_column_rows
        first = await metadata_provider.list_columns(mock_session, "public", "users")
        second = await metadata_provider.list_columns(mock_session, "public", "users")
        assert first == second
        mock_session.execute.assert_awaited_once()
