"""ML endpoints для обучения и прогнозирования."""

import logging
import pickle
from contextlib import contextmanager
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


@contextmanager
def suppress_logs():
    """Подавляет многословные логи Prophet"""
    prophet_logger = logging.getLogger("prophet")
    old_level = prophet_logger.level
    prophet_logger.setLevel(logging.WARNING)
    try:
        yield
    finally:
        prophet_logger.setLevel(old_level)


@router.post("/train", response_model=TrainResponse)
async def train_model():
    """Обучение модели Prophet на данных из Django."""
    try:
        logger.info("🎓 Начало обучения модели...")

        # ✅ Получаем ВСЕ данные со всех страниц
        all_sales_data = []
        page = 1
        while True:
            url = f"{settings.DJANGO_API_URL}/api/sales/?page={page}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            response_data = response.json()

            if not response_data["results"]:
                break

            all_sales_data.extend(response_data["results"])
            logger.info(f"📥 Страница {page}: {len(response_data['results'])} записей")

            if not response_data.get("next"):
                break
            page += 1

        if not all_sales_data:
            raise HTTPException(status_code=400, detail="Нет данных для обучения")

        logger.info(f"📊 Всего получено {len(all_sales_data)} записей")

        # Преобразуем в DataFrame
        df = pd.DataFrame(all_sales_data)
        logger.info(f"📋 Доступные колонки: {df.columns.tolist()}")

        # Проверяем наличие необходимых полей
        if "date" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Колонка 'date' отсутствует! Доступные: {df.columns.tolist()}",
            )
        if "amount" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Колонка 'amount' отсутствует. Доступные: {df.columns.tolist()}",
            )

        # Подготовка данных для Prophet
        prophet_df = pd.DataFrame(
            {
                "ds": pd.to_datetime(df["date"]),
                "y": pd.to_numeric(
                    df["amount"], errors="coerce"
                ),  # ✅ На случай ошибок
            }
        )

        # ✅ Удаляем NaN значения
        prophet_df = prophet_df.dropna(subset=["y"])

        # Агрегируем продажи по дням
        prophet_df = prophet_df.groupby("ds").agg({"y": "sum"}).reset_index()
        prophet_df = prophet_df.sort_values("ds")  # ✅ Важно для Prophet

        logger.info(f"📊 Подготовлено {len(prophet_df)} дней для обучения")
        logger.info(
            f"📈 Диапазон дат: {prophet_df['ds'].min()} - {prophet_df['ds'].max()}"
        )
        logger.info(
            f"💰 Сумма: min={prophet_df['y'].min()}, max={prophet_df['y'].max()}, avg={prophet_df['y'].mean():.2f}"
        )

        # ✅ Проверка минимального размера датасета
        if len(prophet_df) < 30:  # Prophet работает лучше с >30 наблюдениями
            logger.warning(f"⚠️ Мало данных: {len(prophet_df)} дней")

        # Обучаем модель
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=(
                True if len(prophet_df) > 365 else False  # noqa: SIM210
            ),  # ✅ Для года нужен год данных
            changepoint_prior_scale=0.05,
            interval_width=0.95,
        )

        logger.info("🔄 Начинаю обучение Prophet...")
        with suppress_logs():  # ✅ Подавляет многословные логи Prophet  # noqa: F821
            model.fit(prophet_df)
        logger.info("✅ Обучение завершено")

        # Сохраняем модель
        model_path = Path("model_store/prophet_model.pkl")
        model_path.parent.mkdir(parents=True, exist_ok=True)

        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        logger.info(f"💾 Модель сохранена в {model_path}")

        return TrainResponse(
            message="Модель успешно обучена",
            training_samples=len(prophet_df),
            date_range={
                "start": prophet_df["ds"].min().isoformat(),
                "end": prophet_df["ds"].max().isoformat(),
            },
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка запроса к Django: {e}")
        raise HTTPException(  # noqa: B904
            status_code=503, detail=f"Ошибка подключения к Django: {str(e)}"
        ) from e

    except KeyError as e:
        logger.error(f"❌ Отсутствует колонка: {e}")
        raise HTTPException(
            status_code=400, detail=f"Отсутствует необходимое поле: {str(e)}"
        ) from e

    except Exception as e:
        logger.error(f"❌ Ошибка обучения: {e}", exc_info=True)
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
