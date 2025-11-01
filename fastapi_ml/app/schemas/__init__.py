"""Pydantic схемы (фасад для удобства импорта)."""

# KPI схемы
# ML схемы
from ..ml import (
    PredictRequest,
    PredictResponse,
    TrainRequest,
    TrainResponse,
)
from .kpis import (
    SaleAggregated,
    SaleBase,
    SaleCreate,
    SaleResponse,
    TransactionBase,
    TransactionCreate,
    TransactionResponse,
)

__all__ = [
    "PredictRequest",
    "PredictResponse",
    "TrainRequest",
    "TrainResponse",
    "SaleAggregated",
    "SaleBase",
    "SaleCreate",
    "SaleResponse",
    "TransactionBase",
    "TransactionCreate",
    "TransactionResponse",
]
