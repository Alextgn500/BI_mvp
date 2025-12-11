"""
Файл для тестирования подключения БД
"""

import os
import dj_database_url
import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgres://postgres:000@localhost:5432/bi_mvp"
)
print("DATABASE_URL repr:", repr(DATABASE_URL))

cfg = dj_database_url.parse(DATABASE_URL)
print("cfg repr:", repr(cfg))

# Собираем простую DSN-строку
dsn = (
    f"host={cfg.get('HOST')} "
    f"port={cfg.get('PORT')} "
    f"dbname={cfg.get('NAME')} "
    f"user={cfg.get('USER')} "
    f"password={cfg.get('PASSWORD')}"
)
print("DSN repr:", repr(dsn))

# Попытка установить соединение через DSN-строку
try:
    conn = psycopg2.connect(dsn)
    print("Connected via DSN")
    conn.close()
except psycopg2.Error as e:
    print("psycopg2 error:", e)
