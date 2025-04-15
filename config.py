import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "geobookrsupersecretkey")
    JWT_ALGORITHM: str = "HS256"

    PROJECT_NAME: str = "JourneyBookingService"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    RABBITMQ_URL: str = os.getenv(
        "RABBITMQ_URL", "amqp://guest:guest@localhost/")

    class Config:
        env_file = ".env"


settings = Settings()
