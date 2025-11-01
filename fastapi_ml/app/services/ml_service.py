"""
Работа с ML-моделями: обучение, сохранение, загрузка и предсказание.
"""

import pickle
from collections.abc import Sequence
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from app.logger import logger

# ==================== СТАРЫЕ ФУНКЦИИ (совместимость) ====================

# ✅ Путь к папке model_store в корне проекта
# app/services/ml_models.py -> app/services -> app -> fastapi_ml
BASE_DIR = Path(__file__).parent.parent.parent  # Поднимаемся 3 уровня
MODEL_DIR = BASE_DIR / "model_store"
MODEL_PATH = MODEL_DIR / "model.pkl"

# ✅ Временная проверка (ПОСЛЕ определения переменных)
print(f"🔍 Текущий файл: {__file__}")
print(f"🔍 BASE_DIR: {BASE_DIR}")
print(f"🔍 MODEL_DIR: {MODEL_DIR}")
print(f"🔍 MODEL_PATH: {MODEL_PATH}")
print(f"🔍 Модель существует: {MODEL_PATH.exists()}")


def train_dummy_model(_epochs: int = 1) -> Any:
    """
    Тренирует простую линейную модель на синтетических данных.
    """
    feature_matrix = np.arange(10).reshape(-1, 1)
    y = 2.0 * feature_matrix.ravel() + 1.0
    model = LinearRegression()
    model.fit(feature_matrix, y)
    return model


def save_model(model: Any) -> None:
    """
    Сохраняет модель в локальное файловое хранилище (pickle).
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"✅ Модель сохранена: {MODEL_PATH}")


def load_model() -> Any:
    """
    Загружает модель из локального хранилища.
    """
    if not MODEL_PATH.exists():
        logger.warning(f"⚠️ Модель не найдена: {MODEL_PATH}, создаём новую")
        model = train_dummy_model()
        save_model(model)
        return model

    with open(MODEL_PATH, "rb") as f:
        logger.info(f"✅ Модель загружена: {MODEL_PATH}")
        return pickle.load(f)


def predict_from_model(model: Any, features: Sequence[float]) -> float:
    """
    Получает предсказание из модели.
    """
    if not features:
        raise ValueError("features is empty")

    feature_matrix = np.array(features).reshape(1, -1)
    pred = model.predict(feature_matrix)

    try:
        return float(pred[0])
    except Exception as e:
        raise ValueError(f"Unexpected prediction output: {pred!r}") from e


# ==================== НОВАЯ МОДЕЛЬ ДЛЯ ПРОГНОЗА ПРОДАЖ ====================


class SalesForecastModel:
    """
    Продвинутая модель прогнозирования продаж на основе Random Forest.

    Использует:
    - Временные признаки (день недели, месяц, день месяца)
    - Информацию о магазинах
    - Исторические тренды
    """

    def __init__(self):
        """Инициализация модели."""
        self.model = None
        self.shop_encoder = LabelEncoder()

        # ✅ Пути для сохранения в model_store
        base_dir = Path(__file__).parent.parent.parent
        model_store = base_dir / "model_store"

        self.model_path = model_store / "sales_rf_model.joblib"
        self.encoder_path = model_store / "shop_encoder.joblib"
        self.metadata_path = model_store / "model_metadata.joblib"

        # Список признаков
        self.feature_columns = [
            "day_of_week",
            "day_of_month",
            "month",
            "shop_encoded",
            "days_since_start",
        ]

        self.start_date = None
        self.train_date = None

    def prepare_features(
        self, df: pd.DataFrame, fit_encoder: bool = False
    ) -> pd.DataFrame:
        """
            Подготовка признаков для ML модели.

            Args:
        df: DataFrame с колонками [date, shop, amount]
                fit_encoder: Обучить ли энкодер магазинов (True при обучении)

            Returns:
                DataFrame с подготовленными признаками
        """
        df = df.copy()

        # Преобразуем date в datetime
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"])

        # Временные признаки
        df["day_of_week"] = df["date"].dt.dayofweek
        df["day_of_month"] = df["date"].dt.day
        df["month"] = df["date"].dt.month

        # Кодирование магазинов
        if fit_encoder:
            df["shop_encoded"] = self.shop_encoder.fit_transform(df["shop"])
        else:
            # При предсказании используем уже обученный энкодер
            df["shop_encoded"] = self.shop_encoder.transform(df["shop"])

        # Дни с начала наблюдений
        if self.start_date is None:
            self.start_date = df["date"].min()

        df["days_since_start"] = (df["date"] - self.start_date).dt.days

        return df

    def train(
        self,
        df: pd.DataFrame,
        n_estimators: int = 100,
        max_depth: int = 10,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> dict[str, Any]:
        """
        Обучение модели Random Forest.

        Args:
            df: DataFrame с колонками [date, shop, amount]
            n_estimators: Количество деревьев
            max_depth: Максимальная глубина дерева
            test_size: Доля тестовой выборки
            random_state: Seed для воспроизводимости

        Returns:
            Словарь с метриками качества
        """
        logger.info("🚀 Начинаем обучение модели прогнозирования продаж")

        # Подготовка признаков
        df_features = self.prepare_features(df, fit_encoder=True)

        # Разделение на X и y
        X = df_features[self.feature_columns]
        y = df_features["amount"]

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Обучение модели
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
        )

        self.model.fit(X_train, y_train)

        # Оценка качества
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        # Важность признаков
        feature_importance = dict(
            zip(self.feature_columns, self.model.feature_importances_, strict=False)
        )

        self.train_date = datetime.now()

        metrics = {
            "train_r2": float(train_score),
            "test_r2": float(test_score),
            "feature_importance": feature_importance,
            "n_train_samples": len(X_train),
            "n_test_samples": len(X_test),
            "train_date": self.train_date.isoformat(),
        }

        logger.info(
            f"✅ Модель обучена | R² train: {train_score:.3f} | R² test: {test_score:.3f}"
        )

        return metrics

    def predict(
        self, shop: str, target_date: date | str, days_ahead: int = 7
    ) -> list[dict[str, Any]]:
        """
        Прогноз продаж на будущее.

        Args:
            shop: Название магазина
            target_date: Дата начала прогноза
            days_ahead: Количество дней для прогноза

        Returns:
            Список прогнозов [{date, shop, predicted_amount}, ...]
        """
        if self.model is None:
            raise ValueError("Модель не обучена! Вызовите train() или load_model()")

        # Преобразуем строку в date
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

        # Создаём DataFrame для прогноза
        dates = [target_date + timedelta(days=i) for i in range(days_ahead)]
        df_predict = pd.DataFrame({"date": dates, "shop": shop})

        # Подготавливаем признаки
        df_features = self.prepare_features(df_predict, fit_encoder=False)
        X = df_features[self.feature_columns]

        # Предсказание
        predictions = self.model.predict(X)

        # Формируем результат
        results = []
        for i, pred_date in enumerate(dates):
            results.append(
                {
                    "date": pred_date.isoformat(),
                    "shop": shop,
                    "predicted_amount": float(predictions[i]),
                }
            )

        return results

    def save_model(self) -> None:
        """Сохранение модели и метаданных."""
        if self.model is None:
            raise ValueError("Нет модели для сохранения")

        # Создаём папку если не существует
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        # Сохраняем модель
        joblib.dump(self.model, self.model_path)

        # Сохраняем энкодер
        joblib.dump(self.shop_encoder, self.encoder_path)

        # Сохраняем метаданные
        metadata = {
            "start_date": self.start_date,
            "train_date": self.train_date,
            "feature_columns": self.feature_columns,
        }
        joblib.dump(metadata, self.metadata_path)

        logger.info(f"✅ Модель сохранена: {self.model_path}")

    def load_model(self) -> bool:
        """
        Загрузка модели и метаданных.

        Returns:
            True если модель успешно загружена, False если файлы не найдены
        """
        if not self.model_path.exists():
            logger.warning(f"⚠️ Модель не найдена: {self.model_path}")
            return False

        # Загружаем модель
        self.model = joblib.load(self.model_path)

        # Загружаем энкодер
        self.shop_encoder = joblib.load(self.encoder_path)

        # Загружаем метаданные
        metadata = joblib.load(self.metadata_path)
        self.start_date = metadata["start_date"]
        self.train_date = metadata["train_date"]
        self.feature_columns = metadata["feature_columns"]

        logger.info(f"✅ Модель загружена: {self.model_path}")
        return True
