from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:password@db:5432/booking"

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        # Render (and Heroku) provide postgresql:// — asyncpg needs postgresql+asyncpg://
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    secret_key: str = "supersecretkey-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    frontend_url: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [url.strip() for url in self.frontend_url.split(",") if url.strip()]
    slot_generation_days: int = 14

    class Config:
        env_file = ".env"


settings = Settings()
