"""
SQLAlchemy модели для таблиц Sale и Transaction.
Зеркалируют Django модели из app_kpis.
Структура основана на реальной схеме БД PostgreSQL.
"""

from sqlalchemy import BigInteger, Column, Date, DateTime, Float, Numeric, String, func

from app.database import Base


class Sale(Base):
    """
    Модель продажи (зеркало Django модели Sale).
    Таблица: sale

    Поля:
    - id: Уникальный идентификатор (автоинкремент)
    - date: Дата продажи
    - shop: Название магазина/точки продаж
    - amount: Сумма продажи (float)
    """

    __tablename__ = "sale"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    shop = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Sale(id={self.id}, date={self.date}, shop='{self.shop}', amount={self.amount})>"


class Transaction(Base):
    """
    Модель транзакции (зеркало Django модели Transaction).
    Таблица: transaction

    Поля:
    - id: Уникальный идентификатор (автоинкремент)
    - created_at: Дата и время создания (с timezone)
    - amount: Сумма транзакции (Decimal 10,2)
    - category: Категория транзакции
    - source: Источник транзакции (опционально)
    """

    __tablename__ = "transaction"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, category='{self.category}')>"
