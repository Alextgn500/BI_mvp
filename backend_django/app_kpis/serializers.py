"""Сериализаторы для приложения sales"""

from rest_framework import serializers
from .models import Sale, Transaction
from .models import Shop, ShopMetrics, CustomerMetrics


class SaleSerializer(serializers.ModelSerializer):
    """Класс SaleSerializer для сериализации модели Sale"""

    class Meta:
        """Метаданные сериализатора.
        model - модель с которой работает сериализатор;
        fields - все поля модели"""

        model = Sale
        fields = ["id", "date", "shop", "amount"]


class TransactionSerializer(serializers.ModelSerializer):
    """Класс TransactionSerializer для сериализации модели Transaction"""

    class Meta:
        """Метаданные сериализатора"""

        model = Transaction
        fields = "__all__"


class ShopSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Shop.

    Преобразует данные магазина в JSON и обратно.
    """

    class Meta:
        """Метаданные сериализатора"""

        model = Shop
        fields = "__all__"


class ShopMetricsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShopMetrics"""

    shop_name = serializers.CharField(source="shop.name", read_only=True)

    class Meta:
        """Метаданные сериализатора"""

        model = ShopMetrics
        fields = "__all__"


class ShopAnalyticsSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Сериализатор аналитики магазина
    Только для чтения - используется в API для передачи статистики
    """

    shop_id = serializers.IntegerField()
    shop_name = serializers.CharField()
    location = serializers.CharField()

    # Агрегированные показатели
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transactions = serializers.IntegerField()
    avg_daily_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_check = serializers.DecimalField(max_digits=10, decimal_places=2)

    # Динамика
    revenue_growth = serializers.DecimalField(
        max_digits=5, decimal_places=2, allow_null=True
    )
    transactions_growth = serializers.DecimalField(
        max_digits=5, decimal_places=2, allow_null=True
    )


class CustomerMetricsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CustomerMetrics"""

    ltv_cac_ratio = serializers.SerializerMethodField()

    class Meta:
        """Метаданные сериализатора"""

        model = CustomerMetrics
        fields = "__all__"

    def get_ltv_cac_ratio(self, obj):
        """Вычисляет отношение LTV к CAC."""
        if obj.cac and obj.cac > 0:
            return round(float(obj.ltv / obj.cac), 2)
        return None


class SummarySerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Сериализатор для общей сводки"""

    period_start = serializers.DateField()
    period_end = serializers.DateField()

    # KPI
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_transactions = serializers.IntegerField()
    active_shops = serializers.IntegerField()
    avg_check = serializers.DecimalField(max_digits=10, decimal_places=2)

    # Unit-экономика
    avg_cac = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_ltv = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_arpu = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_churn_rate = serializers.DecimalField(max_digits=5, decimal_places=2)

    # Топ магазины
    top_shops = ShopAnalyticsSerializer(many=True)
