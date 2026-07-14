# To read environment variables from .env
# Validate data types

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn # imports a Pydantic type for validating PostgreSQL URLs

# creating a configuration class
class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    ENVIRONMENT: str # Stores the application environment development/production

    # configures Pydantic to read from a .env file if it exists
    model_config = SettingsConfigDict(
        env_file=".env", # look for a file named .env
        env_file_encoding="utf-8",
        extra="ignore" # if the .env file has extra variables that are not defined in this class, ignore them
    )

settings = Settings() # loads the configuration