import pytest
from pydantic import ValidationError

from inspector.config import ConnectionConfig, PgInspectorSettings


class TestConnectionConfig:
    @pytest.mark.parametrize(
        "url",
        [
            "postgresql+asyncpg://localhost/db",
            "postgresql+asyncpg://user:pass@host:5432/mydb",
        ],
    )
    def test_valid_url(self, url: str) -> None:
        config = ConnectionConfig(url=url)
        assert config.url == url

    @pytest.mark.parametrize(
        "url",
        [
            "postgres://localhost/db",
            "postgresql://localhost/db",
            "sqlite+aiosqlite:///tmp/test.db",
        ],
    )
    def test_invalid_non_asyncpg_url_raises(self, url: str) -> None:
        with pytest.raises(ValidationError):
            ConnectionConfig(url=url)

    def test_missing_url_raises(self) -> None:
        with pytest.raises(ValidationError):
            ConnectionConfig()

    def test_none_url_raises(self) -> None:
        with pytest.raises(ValidationError):
            ConnectionConfig(url=None)


class TestPgInspectorSettings:
    def test_database_url_default_none(self) -> None:
        settings = PgInspectorSettings.model_construct()
        assert settings.database_url is None

    @pytest.mark.parametrize(
        "url",
        [
            "postgresql+asyncpg://localhost/db",
            "postgresql+asyncpg://u:p@h:5432/d",
        ],
    )
    def test_database_url_from_validation_alias(
        self, url: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("DATABASE_URL", url)
        settings = PgInspectorSettings()
        assert settings.database_url == url
