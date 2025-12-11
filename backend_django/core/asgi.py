"""
ASGI-конфигурация для проекта Django.

Этот модуль определяет переменную application, используемую ASGI-серверами
(например, Daphne, Uvicorn) для обслуживания проекта. Настройка загружает
Django settings через django.core.asgi.getasgiapplication().
"""

import os

from django.core.asgi import get_asgi_application

# Установить переменную окружения DJANGOSETTINGSMODULE на модуль настроек проекта.
# Измените 'core.settings' на путь к вашему модулю настроек, если он отличается.
os.environ.setdefault("DJANGOSETTINGSMODULE", "core.settings")

application = get_asgi_application()
