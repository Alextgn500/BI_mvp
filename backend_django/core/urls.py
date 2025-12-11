"""
URL-конфигурация проекта core.
Подключает Django Admin и REST API приложения app_kpis.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_kpis.views import SaleViewSet, TransactionViewSet

# DRF router для стандартных CRUD-роутов
router = DefaultRouter()
router.register(r"sales", SaleViewSet, basename="sale")
router.register(r"transactions", TransactionViewSet, basename="transaction")

# Явные пути для API (включая специальные действия)
api_explicit_patterns = [
# Sales
path("sales/", SaleViewSet.as_view({"get": "list", "post": "create"}), name="sale-list"),
path("sales/<int:pk>/", SaleViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}), name="sale-detail"),
# Спец-экшен SaleViewSet (предполагается @action(detail=False, methods=["get"]))
path("sales/daily_agg/", SaleViewSet.as_view({"get": "daily_agg"}), name="sale-daily-agg"),
# Transactions
path("transactions/", TransactionViewSet.as_view({"get": "list", "post": "create"}), name="transaction-list"),
path("transactions/<int:pk>/", TransactionViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}), name="transaction-detail"),
# Спец-экшен TransactionViewSet (предполагается @action(detail=False, methods=["get"]))
path("transactions/by_category/", TransactionViewSet.as_view({"get": "by_category"}), name="transaction-by-category"),

]

urlpatterns = [
# Django Admin
path("admin/", admin.site.urls),
# Явные маршруты API
path("api/", include((api_explicit_patterns, "api"), namespace="api")),

# Роутер DRF (дополнительно к явным — не конфликтует, но обеспечивает совместимость)
path("api/", include(router.urls)),

]


# Ожидаемые URL:
# - /admin/
# - /api/sales/  (GET, POST)
# - /api/sales/<id>/  (GET, PUT, PATCH, DELETE)
# - /api/sales/daily_agg/  (GET)
# - /api/transactions/  (GET, POST)
# - /api/transactions/<id>/  (GET, PUT, PATCH, DELETE)
# - /api/transactions/by_category/  (GET)
