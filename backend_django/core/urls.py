"""
URL-конфигурация проекта core.
Подключает Django Admin и REST API приложения app_kpis.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_kpis.views import (
    SaleViewSet,
    TransactionViewSet,
    ShopViewSet,
    CustomerMetricsViewSet,
    ShopMetricsViewSet,
    SummaryViewSet,
)

# ========== DRF Router (основной способ) ==========
router = DefaultRouter()
router.register(r"sales", SaleViewSet, basename="sales")
router.register(r"transactions", TransactionViewSet, basename="transactions")
router.register(r"shops", ShopViewSet, basename="shops")
router.register(r"shop_metrics", ShopMetricsViewSet, basename="shop_metrics")
router.register(
    r"customer_metrics", CustomerMetricsViewSet, basename="customer_metrics"
)
router.register(r"summary", SummaryViewSet, basename="summary")

# ========== URL Patterns ==========
urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    # API через роутер (включает все CRUD + custom actions)
    path("api/", include(router.urls)),
]

# ========== Ожидаемые URL ==========
# Sales:
#   GET/POST     /api/sales/
#   GET/PUT/PATCH/DELETE  /api/sales/{id}/
#   GET          /api/sales/daily_agg/        (если есть @action)
#
# Transactions:
#   GET/POST     /api/transactions/
#   GET/PUT/PATCH/DELETE  /api/transactions/{id}/
#   GET          /api/transactions/by_category/  (если есть @action)
#
# Shops:
#   GET/POST     /api/shops/
#   GET/PUT/PATCH/DELETE  /api/shops/{id}/
#
# Metrics (ReadOnly):
#   GET          /api/metrics/
#   GET          /api/metrics/{id}/
#
# Summary:
#   (зависит от методов ViewSet)
