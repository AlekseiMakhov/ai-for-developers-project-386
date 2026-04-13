from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:password@db:5432/booking"
    secret_key: str = "supersecretkey-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    frontend_url: str = "http://localhost:5173"
    slot_generation_days: int = 14

    class Config:
        env_file = ".env"


settings = Settings()
