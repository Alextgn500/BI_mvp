"""
WSGI-конфигурация для проекта Django.

Этот модуль определяет переменную application, используемую WSGI-серверами
(например, Gunicorn, uWSGI) для обслуживания проекта. Настройка загружает
Django settings через django.core.wsgi.getwsgiapplication().
"""

import os

from django.core.wsgi import get_wsgi_application

# Установить переменную окружения DJANGOSETTINGSMODULE на модуль настроек проекта.
# Измените 'core.settings' на путь к вашему модулю настроек, если он отличается.
os.environ.setdefault("DJANGOSETTINGSMODULE", "core.settings")

application = get_wsgi_application()
