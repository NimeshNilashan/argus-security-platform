# Handles application settings from environment variables.

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    virustotal_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()