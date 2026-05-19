from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Sign College API"
    version: str = "0.1.0"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(default="change-me-in-local-env", min_length=12)
    access_token_expire_minutes: int = 120
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/sign_college"
    backend_cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
