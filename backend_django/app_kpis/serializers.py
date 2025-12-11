"""Сериализаторы для приложения sales"""

from rest_framework import serializers
from .models import Sale, Transaction


class SaleSerializer(serializers.ModelSerializer):
    """Класс SaleSerializer для сериализации модели Sale"""

    class Meta:
        """Метаданные сериализатора.
        model - модель с которой работает сериализатор;
        fields - все поля модели"""

        model = Sale
        fields = ['id', 'date', 'shop', 'amount']


class TransactionSerializer(serializers.ModelSerializer):
    """Класс TransactionSerializer для сериализации модели Transaction"""

    class Meta:
        model = Transaction
        fields = "__all__"
