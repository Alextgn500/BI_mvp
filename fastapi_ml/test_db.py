"""Тест подключения к БД"""

from app.db import check_connection

if __name__ == "__main__":
    print(check_connection())
