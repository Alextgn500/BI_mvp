# pylint: disable=broad-except
# pylint: disable=logging-fstring-interpolation

"""API Client для взаимодействия с бэкендом Django REST API.

Модуль предоставляет функции для получения данных о продажах из Django REST API
и их преобразования в формат, удобный для визуализации в Streamlit.

Основные возможности:
— Получение данных о продажах с фильтрацией по датам и магазинам
— Получение сводной статистики (общая сумма, количество продаж, средний чек)
— Получение топ магазинов по продажам
— Автоматическая обработка ошибок и возврат безопасных значений по умолчанию
— Преобразование данных в pandas DataFrame для аналитики

Модель Sale:
    date: DateField — дата продажи
    shop: CharField(max_length=100) — название магазина
    amount: FloatField — сумма продажи
"""

import logging
import os
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import streamlit as st

# Настройка логирования
logger = logging.getLogger(__name__)


class DjangoAPIClient:
    """Клиент для запросов к Django REST API"""

    def __init__(self, base_url: Optional[str] = None):
        """Инициализация клиента

        Args:
            base_url: Базовый URL Django API (по умолчанию из переменной окружения)
        """
        self.base_url = (
            base_url or os.getenv("DJANGO_API_URL") or "http://localhost:8000"
        ).rstrip("/")
        self.timeout = int(os.getenv("API_TIMEOUT", "10"))

    def _build_url(self, endpoint: str) -> str:
        """Построение полного URL для эндпоинта

        Args:
            endpoint: Название эндпоинта (например, 'sales')

        Returns:
            Полный URL с /api/ префиксом
        """
        endpoint = endpoint.strip("/")
        return f"{self.base_url}/api/{endpoint}/"

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Выполнение GET запроса к API

        Args:
            endpoint: Название эндпоинта
            params: Параметры запроса

        Returns:
            JSON ответ от API

        Raises:
            requests.exceptions.RequestException: При ошибке запроса
        """
        url = self._build_url(endpoint)
        logger.info(f"📡 GET запрос к Django: {url}")
        logger.debug(f"Параметры запроса: {params}")

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка запроса к {url}: {e}")
            raise


# Приватная переменная для кэширования экземпляра
_django_api: Optional[DjangoAPIClient] = None


@st.cache_resource
def get_django_api() -> DjangoAPIClient:
    """Получить экземпляр Django API клиента (singleton)

    Returns:
        DjangoAPIClient: Глобальный экземпляр клиента
    """
    logger.info("✅ Django API client инициализирован")
    return DjangoAPIClient()


def get_sales(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    shop: Optional[str] = None,
) -> pd.DataFrame:
    """Получение данных о продажах с фильтрацией

    Args:
        start_date: Начальная дата (строка 'YYYY-MM-DD' или date объект)
        end_date: Конечная дата (строка 'YYYY-MM-DD' или date объект)
        shop: Название магазина для фильтрации

    Returns:
        DataFrame с колонками: id, date, shop, amount
        Пустой DataFrame при ошибке
    """
    try:
        params = {}

        # Обработка start_date
        if start_date:
            params["start_date"] = (
                start_date.strftime("%Y-%m-%d")
                if hasattr(start_date, "strftime")
                else str(start_date)
            )

        # Обработка end_date
        if end_date:
            params["end_date"] = (
                end_date.strftime("%Y-%m-%d")
                if hasattr(end_date, "strftime")
                else str(end_date)
            )

        # Фильтр по магазину
        if shop:
            params["shop"] = shop

        api = get_django_api()
        data = api.get("sales", params=params)
        df = pd.DataFrame(data)

        # Преобразование date в datetime
        if "date" in df.columns and len(df) > 0:
            df["date"] = pd.to_datetime(df["date"])

        logger.info(f"✅ Получено {len(df)} записей о продажах")
        return df

    except Exception as e:
        logger.error(f"❌ Ошибка получения данных о продажах: {e}")
        st.error(f"❌ Ошибка при получении данных: {e}")
        return pd.DataFrame()


def get_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    shop: Optional[str] = None,
) -> Dict[str, Any]:
    """Получение сводной статистики по продажам

    Args:
        start_date: Начальная дата фильтра
        end_date: Конечная дата фильтра
        shop: Название магазина для фильтрации

    Returns:
        Словарь со статистикой:
        - total_amount: общая сумма продаж
        - total_sales: количество продаж
        - avg_amount: средний чек
        - unique_shops: количество уникальных магазинов
    """
    try:
        df = get_sales(start_date, end_date, shop)

        if df.empty:
            return {
                "total_amount": 0.0,
                "total_sales": 0,
                "avg_amount": 0.0,
                "unique_shops": 0,
            }

        stats = {
            "total_amount": float(df["amount"].sum()),
            "total_sales": len(df),
            "avg_amount": float(df["amount"].mean()),
            "unique_shops": df["shop"].nunique(),
        }

        logger.info(f"✅ Статистика рассчитана: {stats}")
        return stats

    except Exception as e:
        logger.error(f"❌ Ошибка расчета статистики: {e}")
        st.error(f"❌ Ошибка при расчете статистики: {e}")
        return {
            "total_amount": 0.0,
            "total_sales": 0,
            "avg_amount": 0.0,
            "unique_shops": 0,
        }


def get_top_shops(
    limit: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """Получение топ магазинов по сумме продаж

    Args:
        limit: Количество магазинов в топе (по умолчанию 10)
        start_date: Начальная дата фильтра
        end_date: Конечная дата фильтра

    Returns:
        DataFrame с колонками: shop, total_amount, sales_count, avg_amount
        Отсортирован по total_amount (убывание)
    """
    try:
        df = get_sales(start_date, end_date)

        if df.empty:
            return pd.DataFrame(
                columns=["shop", "total_amount", "sales_count", "avg_amount"]
            )

        # Группировка по магазинам
        top_shops = (
            df.groupby("shop")
            .agg(
                total_amount=("amount", "sum"),
                sales_count=("amount", "count"),
                avg_amount=("amount", "mean"),
            )
            .reset_index()
        )

        # Сортировка и ограничение
        top_shops = top_shops.sort_values("total_amount", ascending=False).head(limit)

        logger.info(f"✅ Топ {len(top_shops)} магазинов получен")
        return top_shops

    except Exception as e:
        logger.error(f"❌ Ошибка получения топ магазинов: {e}")
        st.error(f"❌ Ошибка при получении топ магазинов: {e}")
        return pd.DataFrame(
            columns=["shop", "total_amount", "sales_count", "avg_amount"]
        )


def get_sales_by_date(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    shop: Optional[str] = None,
) -> pd.DataFrame:
    """Получение продаж, сгруппированных по датам

    Args:
        start_date: Начальная дата фильтра
        end_date: Конечная дата фильтра
        shop: Название магазина для фильтрации

    Returns:
        DataFrame с колонками: date, total_amount, sales_count
        Отсортирован по date
    """
    try:
        df = get_sales(start_date, end_date, shop)

        if df.empty:
            return pd.DataFrame(columns=["date", "total_amount", "sales_count"])

        # Группировка по датам
        sales_by_date = (
            df.groupby("date")
            .agg(total_amount=("amount", "sum"), sales_count=("amount", "count"))
            .reset_index()
        )

        # Сортировка по дате
        sales_by_date = sales_by_date.sort_values("date")

        logger.info(f"✅ Получено {len(sales_by_date)} дат с продажами")
        return sales_by_date

    except Exception as e:
        logger.error(f"❌ Ошибка группировки по датам: {e}")
        st.error(f"❌ Ошибка при группировке по датам: {e}")
        return pd.DataFrame(columns=["date", "total_amount", "sales_count"])


def get_unique_shops() -> List[str]:
    """Получение списка уникальных магазинов

    Returns:
        Список названий магазинов (отсортирован по алфавиту)
    """
    try:
        df = get_sales()

        if df.empty:
            return []

        shops = sorted(df["shop"].unique().tolist())
        logger.info(f"✅ Получено {len(shops)} уникальных магазинов")
        return shops

    except Exception as e:
        logger.error(f"❌ Ошибка получения списка магазинов: {e}")
        st.error(f"❌ Ошибка при получении списка магазинов: {e}")
        return []


def get_date_range() -> Dict[str, Any]:
    """Получение диапазона дат в данных

    Returns:
        Словарь с ключами:
        - min_date: минимальная дата
        - max_date: максимальная дата
        - None если данных нет
    """
    try:
        df = get_sales()

        if df.empty or "date" not in df.columns:
            return {"min_date": None, "max_date": None}

        date_range = {"min_date": df["date"].min(), "max_date": df["date"].max()}

        logger.info(
            f"✅ Диапазон дат: {date_range['min_date']} - {date_range['max_date']}"
        )
        return date_range

    except Exception as e:
        logger.error(f"❌ Ошибка получения диапазона дат: {e}")
        return {"min_date": None, "max_date": None}
