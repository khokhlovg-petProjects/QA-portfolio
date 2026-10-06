"""Single source of configuration for the whole suite.

Values resolve in the usual precedence order: real environment variables win,
then `.env`, then the defaults below. Keeping defaults here means a fresh clone
runs green without any local setup, while CI can still point the suite at a
different environment through env vars alone.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ui_base_url: str = "https://www.saucedemo.com"
    api_base_url: str = "https://dummyjson.com"

    ui_username: str = "standard_user"
    ui_password: str = "secret_sauce"

    api_username: str = "emilys"
    api_password: str = "emilyspass"

    http_timeout: float = Field(default=15.0, gt=0)

    # Playwright's web-first assertions retry until this many milliseconds pass.
    expect_timeout_ms: int = Field(default=10_000, gt=0)


settings = Settings()
