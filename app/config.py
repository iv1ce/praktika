from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./praktika.db"
    DB_HOST: str | None = None
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "praktika"
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

    @property
    def db_url(self) -> str:
        if self.DB_HOST:
            pw = quote_plus(self.DB_PASSWORD)
            return f"postgresql://{self.DB_USER}:{pw}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return self.DATABASE_URL


settings = Settings()
BASE_DIR = Path(__file__).resolve().parent.parent
