"""Пример модели продаж"""

from django.db import models


class Sale(models.Model):
    """Класс, представляющий продажу товара"""

    date = models.DateField()
    shop = models.CharField(max_length=100)
    amount = models.FloatField()

    def __str__(self):
        return f"{self.shop} {self.date} {self.amount}"

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Настройки метаданных модели Sale.
          - db_table: явное имя таблицы в БД ('sale'), чтобы FastAPI мог напрямую
            делать запросы к таблице.
          - ordering: по умолчанию сортировка по дате создания (по убыванию),
            что упрощает просмотр последних операций.
          - verbosename / verbosenameplural: читабельные названия для админки.
        """

        db_table = "sale"


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
