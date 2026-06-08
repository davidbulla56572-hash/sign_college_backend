from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Sign College API"
    version: str = "0.1.0"
    environment: str = "local"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(default="change-me-in-local-env", min_length=12)
    access_token_expire_minutes: int = 120
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/sign_college"
    )
    backend_cors_origins: list[str] = ["http://localhost:5173"]
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_fallback_to_mock: bool = True
    upload_max_bytes: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
