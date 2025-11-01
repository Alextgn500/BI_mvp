"""
Главное приложение FastAPI с ML-сервисом.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# pylint: disable=import-error
from app.api.v1 import api_router
from app.config import settings
from app.logger import logger

# pylint: disable=import-error


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):  # pylint: disable=redefined-outer-name,unused-argument
    """Lifecycle events для FastAPI."""
    logger.info("🚀 Запуск FastAPI ML Service...")
    logger.info(f"📊 База данных: {settings.DATABASE_URL}")
    logger.info(f"🤖 Хранилище моделей: {settings.MODEL_STORE_PATH}")
    yield
    logger.info("🛑 Остановка FastAPI ML Service...")


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
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
