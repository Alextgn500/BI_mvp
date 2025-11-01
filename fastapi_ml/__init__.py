"""
FastAPI ML микросервис для BI MVP Platform.

Предоставляет REST API для:
- Интеграции с Claude AI
- Машинного обучения и предсказаний
- Обработки данных и аналитики
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "FastAPI ML Service for BI MVP"

# Экспортируем основные компоненты
try:
    from .app.config import settings
    from .app.logger import logger
    from .app.main import app

    __all__ = [
        "app",
        "settings",
        "logger",
        "__version__",
        "__description__",
    ]
except ImportError:
    # Если импорты не работают (например, при установке пакета)
    __all__ = ["__version__", "__description__"]
