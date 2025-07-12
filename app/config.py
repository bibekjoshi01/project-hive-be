from pathlib import Path
from pydantic import EmailStr
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Project Archive"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str
    database_url: str
    allowed_cors_origins: List[str] = []
    allowed_hosts: List[str] = []
    otp_lifetime: int = 10

    # Email Config
    email_host: str
    email_port: int
    email_username: EmailStr
    email_password: str

    model_config = SettingsConfigDict(
        env_file=".env" if Path(".env").exists() else ".env.example",
        env_parse_json=True,
    )


settings = Settings()
