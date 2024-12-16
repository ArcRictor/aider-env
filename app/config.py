from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Email Manager"
    OPENROUTER_API_KEY: str = ""
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    EMAIL_CHECK_INTERVAL: int = 300  # 5 minutes in seconds

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()