# pylint: disable=unused-argument
"""Sales endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db  # pylint: disable=import-error

router = APIRouter()


@router.get("/")
async def get_sales(db: Session = Depends(get_db)):  # noqa: B008
    """Получить все продажи."""
    return {"message": "Список продаж"}


@router.post("/")
async def create_sale(db: Session = Depends(get_db)):  # noqa: B008
    """Создать новую продажу."""
    return {"message": "Продажа создана"}
