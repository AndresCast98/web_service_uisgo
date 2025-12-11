from __future__ import annotations
from pathlib import Path
from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

def find_env(start: Path, max_up: int = 6) -> Path | None:
    cur = start
    for _ in range(max_up):
        candidate = cur / ".env"
        if candidate.exists():
            return candidate
        cur = cur.parent
    return None

HERE = Path(__file__).resolve()
ENV_PATH = find_env(HERE)
if ENV_PATH:
    load_dotenv(ENV_PATH)  
else:
    pass

class Settings(BaseSettings):
    APP_NAME: str = "UISGo API"
    DATABASE_URL: str | None = None
    DATABASE_HOST: str | None = None
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str | None = None
    DATABASE_USER: str | None = None
    DATABASE_PASSWORD: str | None = None
    JWT_SECRET: str = "dev"
    JWT_AUDIENCE: str = "app"
    JWT_ISSUER: str = "uisgo-api"
    JWT_EXPIRES_MIN: int = 60
    PASSWORD_RESET_TOKEN_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: str | None = None
    OPENAI_API_KEY: str = ""
    ADMIN_WEB_BASE_URL: str = "http://localhost:5173"
    DEEP_LINK_PREFIX: str = "uisgo://join?code="

    model_config = SettingsConfigDict(
        env_file=None,  
        case_sensitive=False,
    )

    def model_post_init(self, __context: Any) -> None:  # type: ignore[override]
        if not self.DATABASE_URL:
            if all(
                [
                    self.DATABASE_HOST,
                    self.DATABASE_NAME,
                    self.DATABASE_USER,
                    self.DATABASE_PASSWORD,
                ]
            ):
                self.DATABASE_URL = (
                    f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                    f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
                )
            else:
                raise ValueError(
                    "DATABASE_URL or DATABASE_HOST/DATABASE_NAME/DATABASE_USER/DATABASE_PASSWORD deben estar configurados"
                )

    def get_cors_origins(self) -> list[str]:
        if not self.BACKEND_CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
