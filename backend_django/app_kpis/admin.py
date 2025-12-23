"""
Регистрация моделей в Django Admin для удобного управления данными.
"""

from django.contrib import admin
from .models import Sale, Transaction, Shop, ShopMetrics, CustomerMetrics


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Регистрация SaleAdmin для удобного управления данными"""

    list_display = ("id", "shop", "date", "amount")
    list_filter = ("date", "shop")
    search_fields = ("shop__name",)
    date_hierarchy = "date"
    ordering = ("-date",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Регистрация TransactionAdmin для удобного управления данными"""

    list_display = ("id", "created_at", "amount", "category", "source")
    list_filter = ("created_at", "category", "source")
    search_fields = ("category", "source")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """Регистрация ShopAdmin для удобного управления данными"""

    list_display = ("id", "name", "location", "opened_date", "is_active")
    list_filter = ("is_active", "opened_date", "location")
    search_fields = ("name", "location")
    ordering = ("name",)


@admin.register(ShopMetrics)
class ShopMetricsAdmin(admin.ModelAdmin):
    """Регистрация ShopMetricsAdmin для удобного управления данными"""

    list_display = (
        "id",
        "shop",
        "date",
        "revenue",
        "transactions_count",
        "customers_count",
        "avg_check",
    )
    list_filter = ("date", "shop")
    search_fields = ("shop__name",)
    date_hierarchy = "date"
    ordering = ("-date",)


@admin.register(CustomerMetrics)
class CustomerMetricsAdmin(admin.ModelAdmin):
    """Регистрация CustomerMetricsAdmin для удобного управления данными"""

    list_display = ("id",)  # добавь поля из модели CustomerMetrics
    list_filter = ()  # добавь фильтры
    search_fields = ()  # добавь поиск

    # Группировка полей в админке для удобства
    fieldsets = (
        ("Основная информация", {"fields": ("date",)}),
        ("Unit-экономика", {"fields": ("cac", "ltv", "arpu", "churn_rate")}),
        ("Клиенты", {"fields": ("new_customers", "active_customers")}),
        ("Маркетинг", {"fields": ("marketing_spend",)}),
    )
