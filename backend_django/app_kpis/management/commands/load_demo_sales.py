"""
Команда для загрузки демо-данных продаж в таблицу sale.
"""

import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from app_kpis.models import Sale


class Command(BaseCommand):
    """Создаёт демонстрационные данные продаж.

    Использование:
        python manage.py load_demo_sales --count 100 --days 90
    """

    help = "Загружает демо-данные продаж"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=100, help="Количество записей для создания"
        )
        parser.add_argument(
            "--days", type=int, default=90, help="Распределить данные за N дней назад"
        )

    def handle(self, *args, **options):
        count = options["count"]
        days = options["days"]

        # Список магазинов
        shops = [
            "Магазин Центр",
            "Магазин Север",
            "Магазин Юг",
            "Магазин Восток",
            "Магазин Запад",
            "Онлайн-магазин",
        ]

        self.stdout.write("Начинаем создание продаж...")

        # Очистка старых демо-данных (опционально)
        old_count = Sale.objects.count()  # pylint: disable=no-member
        if old_count > 0:
            self.stdout.write(
                self.style.WARNING( # pylint: disable=no-member
                    f"В таблице уже есть {old_count} записей. Они будут сохранены."
                )
            )

        # Создаём список объектов для bulk_create
        sales_to_create = []
        start_date = datetime.now().date()

        for i in range(count):
            # Случайная дата за последние N дней
            random_days_ago = random.randint(0, days)
            sale_date = start_date - timedelta(days=random_days_ago)

            # Случайная сумма продажи (от 100 до 50000)
            amount = round(random.uniform(100.0, 50000.0), 2)

            sales_to_create.append(
                Sale(date=sale_date, shop=random.choice(shops), amount=amount)
            )

            # Прогресс каждые 20 записей
            if (i + 1) % 20 == 0:
                self.stdout.write(f"  Подготовлено {i + 1}/{count} записей...")

        # Массовая вставка в БД
        Sale.objects.bulk_create( # pylint: disable=no-member
            sales_to_create, batch_size=500
        )  # pylint: disable=no-member

        created_count = len(sales_to_create)
        total_count = Sale.objects.count()  # pylint: disable=no-member

        self.stdout.write(
            self.style.SUCCESS(  # pylint: disable=no-member
                f"✅ Успешно создано {created_count} записей продаж!\n"
                f"   Всего в таблице: {total_count} записей"
            )
        )

        # Статистика
        self.stdout.write("\n📊 Статистика:")
        for shop in shops:
            shop_count = Sale.objects.filter(  # pylint: disable=no-member
                shop=shop
            ).count()
            self.stdout.write(f"  {shop}: {shop_count} записей")
