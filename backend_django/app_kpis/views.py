"""Представления для приложения sales и метрик"""

from datetime import datetime, timedelta

from django.db.models import Avg, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import CustomerMetrics, Sale, Shop, ShopMetrics, Transaction
from .serializers import (
    CustomerMetricsSerializer,
    SaleSerializer,
    ShopMetricsSerializer,
    ShopSerializer,
    TransactionSerializer,
)


# pylint: disable=no-member
class StandardResultsSetPagination(PageNumberPagination):
    """Пагинация: 10 элементов на страницу, максимум 100."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра списка и деталей магазинов."""

    # queryset = Shop.objects.all()  # pylint: disable=no-member
    serializer_class = ShopSerializer

    def get_queryset(self):
        return Shop.objects.all()


class SaleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра данных о продажах."""

    serializer_class = SaleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["shop"]
    ordering_fields = ["date", "amount"]

    def get_queryset(self):
        return Sale.objects.select_related("shop").order_by("-date")


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра транзакций."""

    serializer_class = TransactionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "source"]

    def get_queryset(self):
        return Transaction.objects.order_by("-created_at")


class ShopMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра метрик магазинов."""

    serializer_class = ShopMetricsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["shop", "date"]
    ordering_fields = ["date", "revenue", "order_count"]

    def get_queryset(self):
        queryset = ShopMetrics.objects.select_related("shop").order_by("-date")

        # Фильтры по диапазону дат
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset

    @action(detail=False, methods=["get"])
    def latest(self, request):  # pylint: disable=unused-argument
        """Последние метрики по всем магазинам"""
        try:
            latest_date = ShopMetrics.objects.latest("date").date
            metrics = ShopMetrics.objects.filter(date=latest_date).select_related(
                "shop"
            )
            serializer = self.get_serializer(metrics, many=True)
            return Response(serializer.data)
        except ShopMetrics.DoesNotExist:
            return Response({"detail": "Данные не найдены"}, status=404)


class CustomerMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра метрик покупателей."""

    serializer_class = CustomerMetricsSerializer

    def get_queryset(self):
        return CustomerMetrics.objects.all()


class SummaryViewSet(viewsets.ViewSet):
    """Эндпойнт /summary/ — сводная аналитика"""

    def list(self, request):
        """GET /api/summary/ — общая сводка"""
        try:
            start_date, end_date = self._get_date_range(request)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Общие KPI
        shop_metrics = ShopMetrics.objects.filter(
            date__gte=start_date, date__lte=end_date
        )

        kpi_aggregated = shop_metrics.aggregate(
            total_revenue=Sum("revenue"),
            total_transactions=Sum("transactions_count"),
            avg_check=Avg("avg_check"),
        )

        active_shops = Shop.objects.filter(is_active=True).count()

        # Unit-экономика
        customer_metrics = CustomerMetrics.objects.filter(
            date__gte=start_date, date__lte=end_date
        ).aggregate(
            avg_cac=Avg("cac"),
            avg_ltv=Avg("ltv"),
            avg_arpu=Avg("arpu"),
            avg_churn_rate=Avg("churn_rate"),
        )

        # Топ-3 магазина
        top_shops_data = (
            shop_metrics.select_related("shop")
            .values("shop__id", "shop__name", "shop__location")
            .annotate(
                total_revenue=Sum("revenue"),
                total_transactions=Sum("transactions_count"),
                avg_check=Avg("avg_check"),
            )
            .order_by("-total_revenue")[:3]
        )

        period_days = max((end_date - start_date).days, 1)

        top_shops = [
            {
                "shop_id": shop["shop__id"],
                "shop_name": shop["shop__name"],
                "location": shop["shop__location"],
                "total_revenue": shop["total_revenue"],
                "total_transactions": shop["total_transactions"],
                "avg_check": shop["avg_check"],
                "revenue_per_day": (shop["total_revenue"] or 0) / period_days,
            }
            for shop in top_shops_data
        ]

        # Расчёт дополнительных метрик
        ltv_cac_ratio = 0
        if customer_metrics["avg_ltv"] and customer_metrics["avg_cac"]:
            ltv_cac_ratio = round(
                customer_metrics["avg_ltv"] / customer_metrics["avg_cac"], 2
            )

        return Response(
            {
                "status": "success",
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": period_days,
                },
                "kpi": {
                    **kpi_aggregated,
                    "active_shops": active_shops,
                },
                "unit_economics": {
                    **customer_metrics,
                    "ltv_cac_ratio": ltv_cac_ratio,
                },
                "top_shops": top_shops,
            }
        )

    def retrieve(self, request, pk=None):
        """GET /api/summary/{shop_id}/ — сводка по конкретному магазину"""
        try:
            shop = Shop.objects.get(pk=pk, is_active=True)
        except Shop.DoesNotExist:
            return Response(
                {"error": "Магазин не найден"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            start_date, end_date = self._get_date_range(request)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # KPI конкретного магазина
        shop_metrics = ShopMetrics.objects.filter(
            shop=shop, date__gte=start_date, date__lte=end_date
        ).aggregate(
            total_revenue=Sum("revenue"),
            total_transactions=Sum("transactions_count"),
            avg_check=Avg("avg_check"),
        )

        # Unit-экономика магазина
        customer_metrics = CustomerMetrics.objects.filter(
            shop=shop, date__gte=start_date, date__lte=end_date
        ).aggregate(
            avg_cac=Avg("cac"),
            avg_ltv=Avg("ltv"),
            avg_arpu=Avg("arpu"),
            avg_churn_rate=Avg("churn_rate"),
        )

        ltv_cac_ratio = 0
        if customer_metrics["avg_ltv"] and customer_metrics["avg_cac"]:
            ltv_cac_ratio = round(
                customer_metrics["avg_ltv"] / customer_metrics["avg_cac"], 2
            )

        period_days = max((end_date - start_date).days, 1)

        return Response(
            {
                "status": "success",
                "shop": {
                    "id": shop.id,
                    "name": shop.name,
                    "location": shop.location,
                },
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": period_days,
                },
                "kpi": shop_metrics,
                "unit_economics": {
                    **customer_metrics,
                    "ltv_cac_ratio": ltv_cac_ratio,
                },
            }
        )

    @action(detail=False, methods=["get"])
    def trends(self, request):
        """GET /api/summary/trends/ — динамика по дням"""
        try:
            start_date, end_date = self._get_date_range(request)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        daily_trends = (
            ShopMetrics.objects.filter(date__gte=start_date, date__lte=end_date)
            .values("date")
            .annotate(
                total_revenue=Sum("revenue"),
                total_transactions=Sum("transactions_count"),
                avg_check=Avg("avg_check"),
            )
            .order_by("date")
        )

        return Response(
            {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                },
                "trends": list(daily_trends),
            }
        )

    # ========== Вспомогательные методы ==========
    def _get_date_range(self, request):
        """Валидация и парсинг диапазона дат"""
        end_date_str = request.query_params.get("end_date")
        start_date_str = request.query_params.get("start_date")

        try:
            end_date = (
                datetime.strptime(end_date_str, "%Y-%m-%d").date()
                if end_date_str
                else timezone.now().date()
            )
            start_date = (
                datetime.strptime(start_date_str, "%Y-%m-%d").date()
                if start_date_str
                else end_date - timedelta(days=30)
            )
        except ValueError as exc:
            raise ValueError("Неверный формат даты. Используйте YYYY-MM-DD") from exc

        if start_date > end_date:
            raise ValueError("start_date не может быть позже end_date")

        return start_date, end_date
