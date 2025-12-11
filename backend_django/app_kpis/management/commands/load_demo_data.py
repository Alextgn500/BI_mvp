"""Команда для загрузки демо-данных в таблицу transaction."""

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from django.utils import timezone

from app_kpis.models import Transaction


class Command(BaseCommand):
    """Создаёт демонстрационные данные транзакций."""

    help = "Загружает демо-данные транзакций"

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки."""
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Количество записей для создания",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Распределить данные за N дней",
        )

    def handle(self, *args, **options):
        """Обработчик команды."""
        count = options["count"]
        days = options["days"]

        categories = ["sales", "refund", "expense", "income", "transfer"]

        self.stdout.write("Начинаем создание транзакций...")

        old_count = Transaction.objects.count()
        if old_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"В таблице уже есть {old_count} записей. Они будут сохранены."
                )
            )

        now = timezone.now()
        created_count = 0

        for i in range(count):
            # Случайная дата за последние N дней
            random_seconds_ago = random.randint(0, days * 24 * 3600)
            trans_datetime = now - timedelta(seconds=random_seconds_ago)

            # Случайная категория
            category = random.choice(categories)

            # Сумма зависит от категории
            if category == "expense":
                amount = Decimal(str(round(random.uniform(50.0, 5000.0), 2)))
            elif category == "refund":
                amount = Decimal(str(-round(random.uniform(10.0, 1000.0), 2)))
            else:
                amount = Decimal(str(round(random.uniform(100.0, 10000.0), 2)))

            # Создаём запись с явной датой
            transaction = Transaction(
                amount=amount, category=category, source="demo_loader"
            )
            # Переопределяем auto_now_add
            transaction.save()
            Transaction.objects.filter(pk=transaction.pk).update(
                created_at=trans_datetime
            )

            created_count += 1

            # Прогресс каждые 10 записей
            if (i + 1) % 10 == 0:
                self.stdout.write(f"  Создано {i + 1}/{count} записей...")

        total_count = Transaction.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Успешно создано {created_count} транзакций!\n"
                f"   Всего в таблице: {total_count} записей"
            )
        )

        self._show_statistics(categories)

    def _show_statistics(self, categories):
        """Выводит статистику по категориям транзакций."""
        self.stdout.write("\n📊 Статистика по категориям:")
        for category in categories:
            cat_stats = Transaction.objects.filter(category=category).aggregate(
                count=Count("id"), total=Sum("amount")
            )
            cat_count = cat_stats["count"] or 0
            cat_sum = cat_stats["total"] or Decimal("0")

            if cat_count > 0:
                self.stdout.write(
                    f"   {category}: {cat_count} записей, сумма: {cat_sum:.2f}"
                )
