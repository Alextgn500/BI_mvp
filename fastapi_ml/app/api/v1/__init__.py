"""API v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, ml, sales

api_router = APIRouter()

# Подключаем все эндпоинты
api_router.include_router(health.router, tags=["health"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
