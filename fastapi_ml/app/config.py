"""Конфигурация приложения."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # ← ИГНОРИРОВАТЬ ЛИШНИЕ ПОЛЯ
    )

    # Основные настройки
    APP_NAME: str = "FastAPI ML Service"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # База данных
    DATABASE_URL: str = "postgresql://postgres:000@localhost:5432/bi_mvp"

    # ML модель
    MODEL_STORE_PATH: str = "./model_store"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app/logs/app.log"


# Пути к файлам (вне класса Settings)
BASE_DIR: Path = Path(__file__).parent.parent
MODEL_STORE_PATH: Path = BASE_DIR / "model_store"

settings = Settings()
