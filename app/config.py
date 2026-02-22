from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # AI
    OPENAI_API_KEY: str = ""
    AI_MODE: str = "live"  # "stub" or "live"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # App
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()