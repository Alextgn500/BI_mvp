"""
URL конфигурация для приложения app_kpis.

В этом модуле определяется маршрут для получения ежедневной агрегации сумм продаж.
GET /daily-agg/  -> вызывает метод daily_agg у SaleViewSet и возвращает агрегацию сумм по дням.
"""

from django.urls import path
from .views import SaleViewSet

urlpatterns = [
    path(
        "daily-agg/",
        SaleViewSet.as_view({"get": "daily_agg"}),
        name="daily_agg",
    ),
]
