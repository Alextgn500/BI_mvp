"""Пример модели продаж"""

from django.db import models


class Sale(models.Model):
    """Класс, представляющий продажу товара"""

    date = models.DateField()
    shop = models.ForeignKey(
        "Shop",
        on_delete=models.CASCADE,
        related_name="sales",
        db_column="shop_id",  # явное имя колонки в БД
    )
    amount = models.FloatField()

    def __str__(self):
        return f"{self.shop.name} {self.date} {self.amount}"

    class Meta:
        """Метаданные класса продаж"""

        db_table = "sales"
        ordering = ["-date"]


class Transaction(models.Model):
    """
    Представляет транзакцию/операцию в бизнесе, используемую для аналитики.
    Хранит сумму, категорию и источник данных; создаётся при загрузке или импорте
    исходных данных (в демо — генератором).

    Поля:
    - created_at: дата и время создания записи.
    - amount: суммарная величина операции.
    - category: тип операции (например, 'sales', 'refund', 'expense').
    - source: источник загрузки/генерации записи (например, 'demoloader').
    """

    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    source = models.CharField(max_length=100, blank=True, null=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Настройки метаданных модели Transaction.
        - db_table: явное имя таблицы в БД ('transaction'), чтобы FastAPI мог напрямую
          делать запросы к таблице.
        - ordering: по умолчанию сортировка по дате создания (по убыванию),
          что упрощает просмотр последних операций.
        - verbosename / verbosenameplural: читабельные названия для админки.
        """

        db_table = "transaction"


class Shop(models.Model):
    """Модель магазина"""

    # id создаётся автоматически Django (AutoField/BigAutoField)
    name = models.CharField(max_length=200, verbose_name="Название магазина")
    location = models.CharField(max_length=200, verbose_name="Адрес")
    opened_date = models.DateField(verbose_name="Дата открытия")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        """Метаданные модели для админ-панели Django."""

        db_table = "shop"
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"

    def __str__(self):
        return f"{self.name}"


class ShopMetrics(models.Model):
    """Метрики магазина"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="metrics")
    date = models.DateField(verbose_name="Дата")
    revenue = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Выручка"
    )
    transactions_count = models.IntegerField(verbose_name="Количество транзакций")
    customers_count = models.IntegerField(verbose_name="Количество клиентов")
    avg_check = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Средний чек"
    )

    class Meta:
        """Метаданные модели."""

        db_table = "shop_metrics"
        verbose_name = "Метрика магазина"
        verbose_name_plural = "Метрики магазинов"
        unique_together = ["shop", "date"]
        ordering = ["-date"]


class CustomerMetrics(models.Model):
    """Метрики клиентов (unit-экономика)"""

    date = models.DateField(verbose_name="Дата", unique=True)
    cac = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="CAC")
    ltv = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="LTV")
    arpu = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ARPU")
    churn_rate = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Churn Rate %"
    )

    # Дополнительные метрики
    new_customers = models.IntegerField(verbose_name="Новых клиентов")
    active_customers = models.IntegerField(verbose_name="Активных клиентов")
    marketing_spend = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Затраты на маркетинг"
    )

    class Meta:
        """Метаданные модели."""

        db_table = "customer_metrics"
        verbose_name = "Метрика клиентов"
        verbose_name_plural = "Метрики клиентов"
        ordering = ["-date"]
