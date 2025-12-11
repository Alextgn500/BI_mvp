"""Представления для приложения sales"""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.db.models import Sum
from django.db.models.functions import TruncDate
from .models import Sale, Transaction
from .serializers import SaleSerializer, TransactionSerializer

# pylint: disable=no-member


class SaleViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Sale."""

    queryset = Sale.objects.all().order_by("date")
    serializer_class = SaleSerializer
    pagination_class = None

    @action(detail=False, methods=["get"])
    def daily_agg(self, _request):
        """Возвращает агрегацию сумм продаж по дням"""
        qs = (
            Sale.objects.annotate(day=TruncDate("date"))
            .values("day")
            .annotate(total=Sum("amount"))
            .order_by("day")
        )
        return Response(qs)


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Transaction."""

    queryset = Transaction.objects.all().order_by("-created_at")
    serializer_class = TransactionSerializer

    @action(detail=False, methods=["get"])
    def by_category(self, _request):
        """Возвращает агрегацию транзакций по категориям"""
        qs = (
            Transaction.objects.values("category")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )
        return Response(qs)
