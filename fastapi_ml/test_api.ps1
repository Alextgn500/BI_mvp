# Скрипт проверки FastAPI сервера

# ===== 1. ROOT ENDPOINT =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "1. Проверка ROOT endpoint" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method Get
    Write-Host " Статус: SUCCESS" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host " Ошибка: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 1


# ===== 2. HEALTH CHECK =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "2. Health Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
    Write-Host " Статус: SUCCESS" -ForegroundColor Green
    $health | ConvertTo-Json -Depth 3
} catch {
    Write-Host " Ошибка: $($_.Exception.Message)" -ForegroundColor Red
}Start-Sleep -Seconds 1


# ===== 3. СПИСОК МОДЕЛЕЙ =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "3. Список загруженных моделей" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    $models = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/ml/models" -Method Get
    Write-Host " Статус: SUCCESS" -ForegroundColor Green

    if ($models.Count -eq 0) {
        Write-Host " Моделей не загружено" -ForegroundColor Yellow
    } else {
        Write-Host "Загружено моделей: $($models.Count)" -ForegroundColor Green
        $models | ConvertTo-Json -Depth 3
    }
} catch {
    Write-Host " Ошибка: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 1


# ===== 4. API ДОКУМЕНТАЦИЯ =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "4. Ссылки на документацию" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "Swagger UI:   http://127.0.0.1:8000/docs" -ForegroundColor Blue
Write-Host "ReDoc:        http://127.0.0.1:8000/redoc" -ForegroundColor Blue
Write-Host "OpenAPI JSON: http://127.0.0.1:8000/openapi.json" -ForegroundColor Blue


# ===== 5. ИТОГИ =====
Write-Host "`n========================================" -ForegroundColor Green
Write-Host " ПРОВЕРКА ЗАВЕРШЕНА" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
