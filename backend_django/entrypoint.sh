#!/bin/bash
set -e

echo "⏳ Ожидание PostgreSQL..."

# ✅ Правильный bash-синтаксис для переменных окружения
POSTGRES_HOST=${POSTGRES_HOST:-postgres}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_DB=${POSTGRES_DB:-bi_mvp}
POSTGRES_USER=${POSTGRES_USER:-postgres}

echo "🔍 Проверяем подключение к $POSTGRES_HOST:$POSTGRES_PORT"

# Ждем пока PostgreSQL будет доступен
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  echo "Ожидание PostgreSQL на $POSTGRES_HOST:$POSTGRES_PORT..."
  sleep 1
done

echo "✅ PostgreSQL готов на $POSTGRES_HOST:$POSTGRES_PORT"

# Применяем миграции
echo "🔄 Применяем миграции..."
python manage.py migrate --noinput

# Собираем статику
echo "📦 Собираем статические файлы..."
python manage.py collectstatic --noinput --clear || true

# Запускаем команду из CMD (gunicorn)
echo "🚀 Запускаем Django сервер..."
exec "$@"


