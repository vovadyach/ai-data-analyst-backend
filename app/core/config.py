from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Data Analyst API"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # CORS (frontend URL)
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Future
    # GEMINI_API_KEY: str
    # JWT_SECRET: str
    # JWT_EXPIRATION_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
