# Handles application settings from environment variables.

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    virustotal_api_key: str
    CLERK_WEBHOOK_SIGNING_SECRET: str
    NEXT_PUBLIC_API_URL: str

    class Config:
        env_file = ".env"


settings = Settings()