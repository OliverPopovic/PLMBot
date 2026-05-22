from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/plmbot")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4.1-mini")


settings = Settings()
