"""
Pydantic схемы для Sale и Transaction.
Используются для валидации и сериализации данных API.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleBase(BaseModel):
    """Базовая схема для Sale"""

    date: date
    shop: str = Field(..., max_length=100)
    amount: float = Field(..., gt=0, description="Сумма продажи (должна быть > 0)")


class SaleCreate(SaleBase):
    """Схема для создания Sale"""

    pass


class SaleResponse(SaleBase):
    """Схема ответа для Sale"""

    id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
    """Базовая схема для Transaction"""

    amount: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    category: str = Field(..., max_length=100)
    source: str | None = Field(None, max_length=100)


class TransactionCreate(TransactionBase):
    """Схема для создания Transaction"""

    pass


class TransactionResponse(TransactionBase):
    """Схема ответа для Transaction"""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SaleAggregated(BaseModel):
    """Схема для агрегированных данных по продажам"""

    day: date
    total: float
    count: int = Field(..., description="Количество продаж за день")
