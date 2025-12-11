#!/bin/bash
set -e

# Функция для graceful shutdown
cleanup() {
    echo "🛑 Получен сигнал остановки, завершаем работу..."
    pkill -TERM -P $$
    wait
    echo "✅ Остановка завершена"
    exit 0
}

# Перехватываем сигналы
trap cleanup SIGTERM SIGINT SIGQUIT

echo "🚀 Запуск FastAPI ML сервиса..."
echo "📦 Окружение: ${ENVIRONMENT:-production}"

# Выбор команды в зависимости от окружения
if [ "$ENVIRONMENT" = "development" ]; then
echo "🔧 Режим разработки: --reload включен"
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8001 \
        --reload \
        --reload-dir /app/app &
else
    echo "🏭 Режим продакшена: multi-worker"
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8001 \
        --workers 2 \
        --timeout-keep-alive 30 &
fi

# Ждем завершения процесса
wait $!
