# Docker Compose запуск для BI_MVP

Write-Host "🚀 Запуск BI_MVP контейнеров..." -ForegroundColor Green

# Проверка наличия .env
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  Файл .env не найден. Копирую из .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Файл .env создан. Настройте переменные перед запуском!" -ForegroundColor Cyan
    exit 1
}

# Остановка и удаление старых контейнеров
Write-Host "🛑 Остановка старых контейнеров..." -ForegroundColor Yellow
docker-compose down

# Сборка и запуск
Write-Host "🔨 Сборка образов..." -ForegroundColor Cyan
docker-compose build

Write-Host "▶️  Запуск сервисов..." -ForegroundColor Green
docker-compose up -d

# Показываем статус
Start-Sleep -Seconds 5
Write-Host "`n📊 Статус контейнеров:" -ForegroundColor Magenta
docker-compose ps

Write-Host "`n✅ Сервисы запущены!" -ForegroundColor Green
Write-Host "📡 Backend Django:    http://localhost:8000" -ForegroundColor Cyan
Write-Host "🤖 FastAPI ML:        http://localhost:8001" -ForegroundColor Cyan
Write-Host "🌐 Streamlit UI:      http://localhost:8501" -ForegroundColor Cyan
Write-Host "`n📋 Логи: docker-compose logs -f [service_name]" -ForegroundColor Yellow
