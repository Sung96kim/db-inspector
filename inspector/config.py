from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PgInspectorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str | None = Field(
        default=None,
        description="PostgreSQL connection URL",
        validation_alias="DATABASE_URL",
    )


class ConnectionConfig(BaseModel):
    url: str = Field(..., description="PostgreSQL connection URL")

    @field_validator("url")
    @classmethod
    def validate_asyncpg_sqlalchemy_url(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "Connection URL must use SQLAlchemy asyncpg format: "
                "'postgresql+asyncpg://...'"
            )
        return value
