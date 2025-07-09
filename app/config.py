from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Project Archive"
    app_version: str = "1.0.0"
    secret_key: str
    database_url: str

    # Email Config
    email_host: str
    email_port: int
    email_username: str
    email_password: str

    model_config = SettingsConfigDict(
        env_file=".env" if Path(".env").exists() else ".env.example"
    )


settings = Settings()