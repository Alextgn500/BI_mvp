# pylint: disable=import-error
"""
Конфигурация логирования для приложения: получение уровня логов по имени и
настройка логгера "app" с консольным и опциональным ротационным файловым обработчиком.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings


def _configure_logger(
    name: str = "app",
    level: str | None = None,
    log_file: Path | None = None,
) -> logging.Logger:
    """
    Конфигурирует и возвращает логгер с заданными параметрами.

    Args:
        name: Имя логгера
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу логов (если None, логи только в консоль)

    Returns:
        Настроенный объект логгера
    """
    # Получаем уровень логирования из настроек или параметров
    log_file = settings.LOG_FILE
    log_level = level or settings.LOG_LEVEL
    log_level_value = getattr(logging, log_level.upper(), logging.INFO)

    # Создаём логгер
    app_logger = logging.getLogger(name)
    app_logger.setLevel(log_level_value)

    # Удаляем существующие обработчики (если есть)
    app_logger.handlers.clear()

    # Формат логов
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Консольный обработчик (всегда включён)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_value)
    console_handler.setFormatter(formatter)
    app_logger.addHandler(console_handler)

    # Файловый обработчик (если указан путь)
    file_path = log_file or settings.LOG_FILE
    if file_path:
        try:
            # Создаём папку для логов, если её нет
            log_dir = Path(file_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)

            # Rotating file handler (максимум 10 МБ, 5 файлов)
            fh = RotatingFileHandler(
                str(file_path),
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            fh.setLevel(log_level_value)
            fh.setFormatter(formatter)
            app_logger.addHandler(fh)

        except (OSError, PermissionError) as e:
            app_logger.error("Failed to configure file logger: %s", e)

    return app_logger


# ✅ Глобальный экземпляр логгера (имя не конфликтует)
logger = _configure_logger()
