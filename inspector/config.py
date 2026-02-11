from pydantic import BaseModel, Field
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
