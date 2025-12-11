"""API v1 роутеры."""

from fastapi import APIRouter

from .health import router as health_router
from .ml import router as ml_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(ml_router)
