"""ML endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/train")
async def train_model():
    """Обучить модель."""
    return {"message": "Модель обучена"}


@router.post("/predict")
async def predict():
    """Получить прогноз."""
    return {"message": "Прогноз"}
