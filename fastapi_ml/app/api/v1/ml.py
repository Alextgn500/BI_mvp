"""ML endpoints для обучения и прогнозирования."""

from pathlib import Path

import joblib
import pandas as pd
import requests
from fastapi import APIRouter, HTTPException
from prophet import Prophet
from pydantic import BaseModel

from app.config import settings  # pylint: disable=import-error
from app.logger import logger  # pylint: disable=import-error

router = APIRouter(prefix="/ml", tags=["ML"])

# Путь для сохранения модели
MODEL_PATH = Path(settings.MODEL_STORE_PATH) / "sales_prophet.pkl"

# URL Django API
DJANGO_API = getattr(settings, "DJANGO_API_URL", "http://localhost:8000/api/")


class PredictionResponse(BaseModel):
    """Ответ с прогнозом."""

    forecast_dates: list[str]
    forecast_values: list[float]
    lower_bound: list[float]
    upper_bound: list[float]
    model_trained: bool


class TrainResponse(BaseModel):
    """Ответ после обучения."""

    message: str
    training_samples: int
    date_range: dict


@router.post("/train", response_model=TrainResponse)
async def train_model():
    """Обучение модели Prophet на данных из Django."""
    try:
        logger.info("🎓 Начало обучения модели...")

        # Получаем данные из Django
        response = requests.get(f"{settings.DJANGO_API_URL}/api/sales/", timeout=10)
        response.raise_for_status()
        sales_data = response.json()

        if not sales_data:
            raise HTTPException(status_code=400, detail="Нет данных для обучения")

        logger.info(f"📊 Получено {len(sales_data)} записей продаж")

        # Добавляем логирование типа данных
        logger.info(f"🔍 Тип данных: {type(sales_data)}")

        # Логируем все записи
        for i, record in enumerate(sales_data):
            logger.info(f"📝 Запись {i}: {record}")
            logger.info(
                f"🔑 Ключи записи {i}: {list(record.keys()) if isinstance(record, dict) else 'НЕ СЛОВАРЬ!'}"
            )

        # Преобразуем в DataFrame
        df = pd.DataFrame(sales_data)
        logger.info(f"📋 Колонки DataFrame: {df.columns.tolist()}")
        logger.info(f"📄 Первые строки:\n{df.head()}")

        # Проверяем наличие 'date'
        if 'date' not in df.columns:
            logger.error(
                f"❌ Колонка 'date' отсутствует! Доступные: {df.columns.tolist()}"
            )
            raise KeyError("date")

        df["date"] = pd.to_datetime(df["date"])
        logger.info(f"✅ Дата преобразована: {df['date'].dtype}")

        # Агрегируем продажи по дням
        daily_sales = df.groupby("date")["amount"].sum().reset_index()
        daily_sales.columns = ["ds", "y"]

        logger.info(f"📈 Подготовлено {len(daily_sales)} дней для обучения")

        # Обучаем модель
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            seasonality_mode="multiplicative",
            interval_width=0.95,
            changepoint_prior_scale=0.05,
        )
        model.fit(daily_sales)

        # Сохраняем модель
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        logger.info(f"💾 Модель сохранена: {MODEL_PATH}")

        return TrainResponse(
            message="Модель успешно обучена",
            training_samples=len(daily_sales),
            date_range={
                "start": daily_sales["ds"].min().strftime("%Y-%m-%d"),
                "end": daily_sales["ds"].max().strftime("%Y-%m-%d"),
            },
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка подключения к Django: {e}")
        raise HTTPException(  # noqa: B904
            status_code=503, detail=f"Ошибка подключения к Django: {str(e)}"
        ) from e

    except HTTPException:
        # Пробрасываем HTTPException без изменений
        raise

    except Exception as e:
        logger.error(f"❌ Ошибка обучения: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обучения: {str(e)}") from e


@router.post("/predict", response_model=PredictionResponse)
async def predict_sales(days: int = 30):
    """Прогноз продаж на N дней вперед."""
    try:
        # Проверяем наличие модели
        if not MODEL_PATH.exists():
            raise HTTPException(
                status_code=400,
                detail="Модель не обучена. Сначала выполните /api/v1/ml/train",
            )

        logger.info(f"🔮 Создание прогноза на {days} дней...")

        # Загружаем модель
        model = joblib.load(MODEL_PATH)

        # Создаем даты для прогноза
        future = model.make_future_dataframe(periods=days)

        # Делаем прогноз
        forecast = model.predict(future)

        # Ограничиваем отрицательные значения (продажи не могут быть < 0)
        forecast["yhat"] = forecast["yhat"].clip(lower=0)
        forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
        forecast["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)

        # Берем только будущие даты
        forecast_future = forecast.tail(days)

        logger.info("✅ Прогноз создан успешно")

        return PredictionResponse(
            forecast_dates=forecast_future["ds"].dt.strftime("%Y-%m-%d").tolist(),
            forecast_values=forecast_future["yhat"].round(2).tolist(),
            lower_bound=forecast_future["yhat_lower"].round(2).tolist(),
            upper_bound=forecast_future["yhat_upper"].round(2).tolist(),
            model_trained=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка прогноза: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка прогноза: {str(e)}") from e


@router.get("/status")
async def model_status():
    """Статус модели."""
    model_exists = MODEL_PATH.exists()
    return {
        "model_trained": model_exists,
        "model_path": str(MODEL_PATH),
        "model_size_mb": (
            round(MODEL_PATH.stat().st_size / (1024 * 1024), 2) if model_exists else 0
        ),
    }
