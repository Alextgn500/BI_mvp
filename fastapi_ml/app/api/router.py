"""
Главный роутер API.
"""

from fastapi import APIRouter

from app.api.endpoints import health, ml

router = APIRouter()

# Подключаем эндпоинты
router.include_router(health.router)
router.include_router(ml.router)
