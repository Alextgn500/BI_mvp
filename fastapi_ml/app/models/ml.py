"""
Pydantic схемы для валидации запросов и ответов API.
"""

# from datetime import datetime
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Запрос на прогноз на основе транзакций"""

    category: str | None = Field(
        None,
        description="Фильтр по категории (sales, refund, expense). Если None - все категории",
        example="sales",
    )

    days_history: int = Field(
        default=30,
        ge=7,
        le=365,
        description="Количество дней исторических данных для анализа",
    )

    forecast_days: int = Field(
        default=7, ge=1, le=90, description="Количество дней для прогноза"
    )

    source: str | None = Field(
        None, description="Фильтр по источнику данных", example="demo_loader"
    )


class PredictResponse(BaseModel):
    """Ответ с прогнозом"""

    category: str | None = Field(..., description="Категория транзакций")

    historical_data: list[float] = Field(
        ..., description="Исторические данные (суммы по дням)"
    )

    forecast: list[float] = Field(..., description="Прогнозируемые значения")

    forecast_dates: list[str] = Field(..., description="Даты прогноза")

    total_transactions: int = Field(..., description="Количество транзакций в выборке")

    model_used: str = Field(
        default="simple_average", description="Использованная модель"
    )


class TrainRequest(BaseModel):
    """Запрос на обучение модели"""

    epochs: int = Field(
        default=10, ge=1, le=1000, description="Количество эпох обучения"
    )


class TrainResponse(BaseModel):
    """Ответ после обучения"""

    message: str = Field(..., description="Статус обучения")
    epochs: int = Field(..., description="Количество эпох")
