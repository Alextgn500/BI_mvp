"""Клиент для работы с Django API"""

from typing import Any  # noqa: UP035

import requests

from .config import settings
from .logger import logger


class DjangoClient:
    """Клиент для запросов к Django API"""

    BASE_URL = settings.DJANGO_API_URL
    TIMEOUT = 10

    @classmethod
    def get(cls, endpoint: str, params: dict | None = None) -> Any:
        """
        Выполнить GET запрос к Django API

        Args:
            endpoint: Endpoint без /api (например: 'sales', 'products')
            params: Query параметры

        Returns:
            Распарсенный JSON ответ
        """
        # Автоматически добавляем /api/ и убираем лишние слеши
        endpoint = endpoint.strip("/")
        url = f"{cls.BASE_URL}/api/{endpoint}/"

        logger.info(f"📡 GET запрос к Django: {url}")  # pylint: disable=logging-fstring-interpolation

        try:
            response = requests.get(url, params=params, timeout=cls.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка запроса к Django: {e}")  # pylint: disable=logging-fstring-interpolation
            raise

    @classmethod
    def post(cls, endpoint: str, data: dict) -> Any:
        """POST запрос к Django API"""
        endpoint = endpoint.strip("/")
        url = f"{cls.BASE_URL}/api/{endpoint}/"

        logger.info(f"📤 POST запрос к Django: {url}")  # pylint: disable=logging-fstring-interpolation

        try:
            response = requests.post(url, json=data, timeout=cls.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка запроса к Django: {e}")  # pylint: disable=logging-fstring-interpolation
            raise


# Алиас для удобства
django_api = DjangoClient()
