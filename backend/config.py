from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    ENVIRONMENT: str = "development"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    GROQ_API_KEY: str
    GMAIL_SENDER: str   
    GMAIL_APP_PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()