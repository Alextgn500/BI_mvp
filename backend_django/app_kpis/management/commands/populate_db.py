"""Файл для создания демо данных платформы BI_mvp"""

# pylint: disable=no-member
# pylint: disable=no-member,undefined-variable
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from app_kpis.models import CustomerMetrics, Sale, Shop, ShopMetrics, Transaction


class Command(BaseCommand):
    """Наполняет БД тестовыми данными для демонстрации BI_mvp"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Количество дней для генерации данных (по умолчанию 90)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить существующие данные перед генерацией",
        )

    def handle(self, *args, **options):
        days = options["days"]
        clear = options["clear"]

        self.stdout.write(
            self.style.NOTICE(f"🚀 Начинаем генерацию данных за {days} дней...")
        )

        # Очистка данных если указан флаг --clear
        if clear:
            self.stdout.write(self.style.NOTICE("⚠️ Очистка существующих данных..."))
            Sale.objects.all().delete()
            Transaction.objects.all().delete()
            ShopMetrics.objects.all().delete()
            CustomerMetrics.objects.all().delete()
            Shop.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Данные очищены"))

        # 1. Создаём магазины
        shops = self.create_shops()
        self.stdout.write(self.style.SUCCESS(f"✅ Создано {len(shops)} магазинов"))

        # 2. Генерируем продажи
        sales_count = self.create_sales(shops, days)
        self.stdout.write(self.style.SUCCESS(f"✅ Создано {sales_count} продаж"))

        # 3. Генерируем транзакции
        transactions_count = self.create_transactions(days)
        self.stdout.write(
            self.style.SUCCESS(f"✅ Создано {transactions_count} транзакций")
        )

        # 4. Генерируем метрики магазинов
        metrics_count = self.create_shop_metrics(shops, days)
        self.stdout.write(
            self.style.SUCCESS(f"✅ Создано {metrics_count} записей метрик магазинов")
        )

        # 5. Генерируем метрики клиентов
        customer_metrics_count = self.create_customer_metrics(days)
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Создано {customer_metrics_count} записей метрик клиентов"
            )
        )

        self.stdout.write(self.style.SUCCESS("\n🎉 База данных успешно наполнена!"))
        self.print_statistics()

    def create_shops(self):
        """Создание магазинов"""
        shops_data = [
            {
                "name": "Магазин Центр",
                "location": "Москва, Тверская 1",
                "is_active": True,
                "opened_date": timezone.now().date() - timedelta(days=730),
            },
            {
                "name": "Магазин Запад",
                "location": "Москва, Кутузовский 15",
                "is_active": True,
                "opened_date": timezone.now().date() - timedelta(days=550),
            },
            {
                "name": "Магазин Восток",
                "location": "Москва, Энтузиастов 50",
                "is_active": True,
                "opened_date": timezone.now().date() - timedelta(days=365),
            },
            {
                "name": "Магазин Север",
                "location": "Москва, Дмитровское 200",
                "is_active": True,
                "opened_date": timezone.now().date() - timedelta(days=180),
            },
            {
                "name": "Магазин Юг (закрыт)",
                "location": "Москва, Варшавское 100",
                "is_active": False,
                "opened_date": timezone.now().date() - timedelta(days=500),
            },
        ]

        shops = []
        for shop_data in shops_data:
            shop, _ = Shop.objects.get_or_create(
                name=shop_data["name"], defaults=shop_data
            )
            shops.append(shop)

        return shops

    def create_sales(self, shops, days):
        """Генерация продаж"""
        sales = []

        for shop in shops:
            for day_offset in range(days):
                # Дата продажи
                sale_date = timezone.now().date() - timedelta(days=day_offset)

                # Генерируем 10-50 продаж в день для каждого магазина
                daily_sales_count = random.randint(10, 50)

                for _ in range(daily_sales_count):
                    # Генерируем сумму продажи от 100 до 5000 рублей
                    amount = round(random.uniform(100, 5000), 2)

                    sale = Sale(shop=shop, date=sale_date, amount=amount)
                    sales.append(sale)

        # Массовое создание записей
        Sale.objects.bulk_create(sales, batch_size=1000)
        return len(sales)

    def create_shop_metrics(self, shops, days):
        """Создание метрик магазинов"""
        metrics = []

        for shop in shops:
            for day_offset in range(days):
                date = timezone.now().date() - timedelta(days=day_offset)

                # Генерируем данные согласно реальной модели
                transactions_count = random.randint(50, 200)
                customers_count = random.randint(30, 150)
                revenue = Decimal(random.uniform(10000, 50000)).quantize(
                    Decimal("0.01")
                )
                avg_check = (revenue / transactions_count).quantize(Decimal("0.01"))

                metric = ShopMetrics(
                    shop=shop,
                    date=date,
                    revenue=revenue,
                    transactions_count=transactions_count,
                    customers_count=customers_count,
                    avg_check=avg_check,
                )

                metrics.append(metric)

        ShopMetrics.objects.bulk_create(metrics, batch_size=1000)
        return len(metrics)

    def create_transactions(self, days):
        """Создание транзакций"""
        categories = ["sales", "refund", "expense", "commission"]
        transactions = []

        for _ in range(days):
            # Создаём 20-100 транзакций в день
            daily_count = random.randint(20, 100)

            for _ in range(daily_count):
                category = random.choice(categories)

                # Разные диапазоны сумм для разных категорий
                if category == "sales":
                    amount = Decimal(random.uniform(100, 5000))
                elif category == "refund":
                    amount = Decimal(random.uniform(-500, -50))
                elif category == "expense":
                    amount = Decimal(random.uniform(-1000, -100))
                else:  # commission
                    amount = Decimal(random.uniform(50, 500))

                transaction = Transaction(
                    amount=amount.quantize(Decimal("0.01")),
                    category=category,
                    source="demoloader",
                )
                transactions.append(transaction)

        Transaction.objects.bulk_create(transactions, batch_size=1000)
        return len(transactions)

    def create_customer_metrics(self, days):
        """Создание метрик клиентов"""
        metrics = []

        for day_offset in range(days):
            date = timezone.now().date() - timedelta(days=day_offset)

            # Генерируем реалистичные данные
            new_customers = random.randint(10, 50)
            active_customers = random.randint(100, 500)
            marketing_spend = Decimal(random.uniform(5000, 20000)).quantize(
                Decimal("0.01")
            )

            # CAC = Marketing Spend / New Customers
            cac = (marketing_spend / new_customers).quantize(Decimal("0.01"))

            # ARPU = средний доход на пользователя
            arpu = Decimal(random.uniform(500, 2000)).quantize(Decimal("0.01"))

            # LTV = ARPU * средний срок жизни клиента (например, 12 месяцев)
            ltv = (arpu * Decimal(random.uniform(10, 15))).quantize(Decimal("0.01"))

            # Churn Rate = процент оттока (обычно 2-10%)
            churn_rate = Decimal(random.uniform(2, 10)).quantize(Decimal("0.01"))

            metric = CustomerMetrics(
                date=date,
                cac=cac,
                ltv=ltv,
                arpu=arpu,
                churn_rate=churn_rate,
                new_customers=new_customers,
                active_customers=active_customers,
                marketing_spend=marketing_spend,
            )
            metrics.append(metric)

        CustomerMetrics.objects.bulk_create(metrics, ignore_conflicts=True)
        return len(metrics)

    def print_statistics(self):
        """Вывод статистики по созданным данным"""
        self.stdout.write(self.style.SUCCESS("\n📊 Статистика созданных данных:"))
        self.stdout.write(f"   — Магазинов: {Shop.objects.count()}")
        self.stdout.write(f"   — Продаж: {Sale.objects.count()}")
        self.stdout.write(f"   — Транзакций: {Transaction.objects.count()}")
        self.stdout.write(f"   — Метрик магазинов: {ShopMetrics.objects.count()}")
        self.stdout.write(f"   — Метрик клиентов: {CustomerMetrics.objects.count()}")

        # Исправлено: используем поле amount вместо quantity * price
        total_revenue = Sale.objects.aggregate(total=models.Sum("amount"))["total"] or 0

        self.stdout.write(f"   — Общая выручка: {total_revenue:,.2f} руб.")
