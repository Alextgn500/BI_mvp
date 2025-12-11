"""Вспомогательный скрипт для вывода списка установленных приложений Django."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.conf import settings  # noqa: E402

print("\n".join(settings.INSTALLED_APPS))
