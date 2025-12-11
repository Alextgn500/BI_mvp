"""
Главное приложение FastAPI с ML-сервисом.
"""

import signal
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# pylint: disable=import-error
from app.api.v1 import health, ml
from app.config import settings
from app.logger import logger

# Создаём директорию для моделей при запуске
MODEL_PATH = Path(settings.MODEL_STORE_PATH)
MODEL_PATH.mkdir(parents=True, exist_ok=True)


# === ОБРАБОТКА GRACEFUL SHUTDOWN ===
def handle_shutdown(signum, _frame):
    """Корректная обработка сигналов остановки (Docker и локальный запуск)"""
    signal_name = signal.Signals(signum).name
    logger.info(f"🛑 Получен сигнал {signum} ({signal_name}), завершаем работу...")

    # Для локального запуска — принудительная остановка
    if settings.ENVIRONMENT == "development":
        logger.info("💻 Режим разработки: принудительная остановка")
        sys.exit(0)

    # Для Docker — позволяем uvicorn корректно завершиться
    logger.info("🐳 Режим Docker: ожидание завершения uvicorn")


# Регистрируем обработчики сигналов ДО создания приложения
signal.signal(signal.SIGTERM, handle_shutdown)  # Docker stop
signal.signal(signal.SIGINT, handle_shutdown)  # Ctrl+C (локальный запуск)

# Для Windows: дополнительная обработка Ctrl+Break
if sys.platform == "win32":
    try:
        signal.signal(signal.SIGBREAK, handle_shutdown)  # Ctrl+Break
        logger.info("✅ Обработчик Ctrl+Break зарегистрирован (Windows)")
    except AttributeError:
        pass

logger.info("✅ Обработчики сигналов остановки зарегистрированы")


@asynccontextmanager
async def lifespan(
    app: FastAPI,  # pylint: disable=redefined-outer-name,unused-argument
):
    """Lifecycle events для FastAPI."""
    logger.info("🚀 Запуск FastAPI ML Service...")
    logger.info(f"🌍 Окружение: {settings.ENVIRONMENT}")
    logger.info(f"📊 База данных: {settings.DATABASE_URL}")
    logger.info(f"🤖 Хранилище моделей: {settings.MODEL_STORE_PATH}")

    # Проверяем наличие обученной модели
    model_file = MODEL_PATH / "sales_prophet.pkl"
    if model_file.exists():
        logger.info(f"✅ Найдена обученная модель: {model_file}")
    else:
        logger.warning("⚠️ Обученная модель не найдена. Требуется обучение.")

    yield

    # Cleanup при остановке приложения
    logger.info("🛑 Остановка FastAPI ML Service...")
    logger.info("🧹 Cleanup ресурсов завершён")


# Создаём приложение
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI сервис для ML прогнозирования продаж",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы (favicon)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем API v1
app.include_router(ml.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """
    Проверка здоровья сервиса (используется Docker healthcheck).

    Returns:
        dict: Статус сервиса и версия
    """
    return {
        "status": "healthy",
        "service": "fastapi_ml",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
