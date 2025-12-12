# 📊 BI Platform MVP

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.108-teal?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red?logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Современная платформа бизнес-аналитики с микросервисной архитектурой**

Полнофункциональная система для анализа продаж, прогнозирования и визуализации KPI с использованием машинного обучения.

---

## 🎯 Возможности

✅ **REST API Backend** — Django REST Framework для управления данными
✅ **ML Микросервис** — FastAPI + Prophet для прогнозирования продаж
✅ **Интерактивный Dashboard** — Streamlit с графиками и метриками
✅ **Docker Compose** — Запуск всей инфраструктуры одной командой
✅ **Автоматическая генерация данных** — Демо-данные для тестирования
✅ **API Documentation** — Swagger UI и ReDoc из коробки

---

## 🏗️ Архитектура

┌─────────────────────────────────────────────────────────────┐
│                     ПОЛЬЗОВАТЕЛЬ                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Streamlit Dashboard   │
            │  (Port 8501)           │
            │  • Визуализация        │
            │  • Метрики KPI         │
            │  • Интерактивность     │
            └─────┬──────────────┬───┘
                  │              │
        ┌─────────▼─────┐   ┌────▼─────────────┐
        │ Django API    │   │ FastAPI ML       │
        │ (Port 8000)   │   │ (Port 8001)      │
        │ • REST API    │   │ • Прогнозы       │
        │ • CRUD Sales  │   │ • Prophet        │
        │ • PostgreSQL  │   │ • ML Pipeline    │
        └───────┬───────┘   └──────────────────┘
                │
                ▼
        ┌───────────────┐
        │  PostgreSQL   │
        │  (Port 5432)  │
        │  • Sales Data │
        │  • KPIs       │
        └───────────────┘

### Микросервисы

**1. Backend Django** (`backend_django/`)
— Django 5.0 + Django REST Framework
— PostgreSQL база данных
— API для управления продажами и KPI
— Автоматическая генерация демо-данных

**2. ML Service** (`fastapi_ml/`)
— FastAPI для высокой производительности
— Prophet для временных рядов
— Прогнозирование продаж на 30 дней
— Health check endpoints

**3. Frontend Dashboard** (`frontend_streamlit/`)
— Streamlit для быстрой разработки UI
— Интерактивные графики (Plotly)
— Метрики в реальном времени
— Мультистраничное приложение

---


## 🚀 Быстрый старт

### Требования

— **Docker** 20.10+
— **Docker Compose** 2.0+
— **Git**

### Установка за 3 шага

**1. Клонируйте репозиторий**

git clone https://github.com/Alextgn500/BI_mvp.git
cd BI_mvp

**2. Настройте переменные окружения**

# Скопируйте пример конфигурации
cp .env.example .env

**3. Запустите все сервисы**

docker-compose up --build


### ✅ Готово! Откройте в браузере:

— **Dashboard:** http://localhost:8501
— **Django API:** http://localhost:8000/api/
— **FastAPI Docs:** http://localhost:8001/docs
— **Django Admin:** http://localhost:8000/admin/

### Демо-данные

Cлучайные данные для демонстрации работы загружаются запуском файлов:
 -backend_django/app_kpis/management/commands/load_demo_sales.py;
 -backend_django/app_kpis/management/commands/load_demo_data.py;


## 📁 Структура проекта

BI_mvp/
├── backend_django/         # Django REST API
│   ├── app_kpis/           # Приложение для KPI и продаж
│   │   ├── models.py       # Модели Sale, Transaction
│   │   ├── serializers.py  # DRF сериализаторы
│   │   ├── views.py        # API endpoints
│   │   └── management/     # Django команды
│   ├── core/               # Настройки Django
│   ├── Dockerfile
│   └── requirements.txt
│
├── fastapi_ml/             # FastAPI ML сервис
│   ├── app/
│   │   ├── main.py        # Точка входа FastAPI
│   │   ├── api/v1/        # API endpoints
│   │   ├── django_client.py  # Клиент для Django API
│   │   └── ml/            # ML модели
│   ├── model_store/       # Обученные модели
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend_streamlit/     # Streamlit Dashboard
│   ├── app.py             # Главная страница
│   ├── pages/              # Дополнительные страницы
│   │   ├── sales.py        # Анализ продаж
│   │   └── transactions.py # Список транзакций
│   ├── utils/             # Утилиты
│   │   ├── api_client.py   # HTTP клиент
│   │   ├── charts.py       # Графики
│   │   └── metrics.py      # KPI метрики
│   ├── Dockerfile
│   └── requirements.txt
│
├── infra/ docker-compose.yml   # Оркестрация сервисов
├── .env.example                # Пример конфигурации
├── .gitignore
|__ .dockerignore
└── README.md


---

## 🔧 Конфигурация

### Переменные окружения (`.env`)

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=bi_platform
POSTGRES_USER=bi_user
POSTGRES_PASSWORD=bi_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# FastAPI
FASTAPI_ML_HOST=fastapi_ml
FASTAPI_ML_PORT=8001

# Django Backend
DJANGO_HOST=backend_django
DJANGO_PORT=8000

---

## 🛠️ Разработка

### Запуск без Docker (для разработки)

**1. Backend Django**

cd backend_django
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Настройте PostgreSQL или используйте SQLite (settings.py)
python manage.py migrate
python manage.py load_demo_sales
python manage.py runserver 8000

**2. FastAPI ML**

cd fastapi_ml
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

**3. Streamlit Dashboard**

cd frontend_streamlit
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

streamlit run app.py

### Полезные команды

# Пересборка контейнеров
docker-compose up --build

# Просмотр логов
docker-compose logs -f

# Остановка всех сервисов
docker-compose down

# Очистка volumes (удалит БД!)
docker-compose down -v

# Выполнение команды в контейнере
docker-compose exec backend_django python manage.py shell

### Django Management команды

# Загрузить демо-данные
docker-compose exec backend_django python manage.py load_demo_sales

# Создать суперпользователя
docker-compose exec backend_django python manage.py createsuperuser

# Применить миграции
docker-compose exec backend_django python manage.py migrate

---

## 📊 API Документация

### Django REST API

**Base URL:** `http://localhost:8000/api/`

**Endpoints:**

GET    /api/sales/              - Список всех продаж
GET    /api/transactions/       - Список всех сделок

**Пример запроса:**

curl http://localhost:8000/api/sales/

**Пример ответа:**

 {
    "id": 45,
    "date": "2025-09-11",
    "shop": "Магазин Юг",
    "amount": 6461.66
  }


### FastAPI ML Service

**Base URL:** `http://localhost:8001/`

**Endpoints:**

```
GET  /health                 - Health check
GET  /api/v1/health          - Detailed health
POST /api/v1/ml/train        - Обучение модели
 Пример ответа:

Response body

{
  "message": "Модель успешно обучена",
  "training_samples": 60,
  "date_range": {
    "start": "2025-09-11",
    "end": "2025-12-10"
  }
}
POST /api/v1/predict/sales   - Прогноз продаж

**Пример запроса:**

curl -X POST http://localhost:8001/api/v1/predict/sales \
  -H "Content-Type: application/json" \
  -d '{"periods": 30}'

**Swagger UI:** http://localhost:8001/docs

---

## 🧪 Тестирование


# Backend Django
docker-compose exec backend_django pytest

# FastAPI ML
docker-compose exec fastapi_ml pytest

# Линтинг
docker-compose exec backend_django ruff
docker-compose exec fastapi_ml ruff

---

## 📈 Roadmap

### ✅ Версия 1.0 (Текущая)
— Микросервисная архитектура
— Django REST API
— FastAPI ML сервис с Prophet
— Streamlit Dashboard
— Docker Compose оркестрация
— Демо-данные

### 🚧 Версия 1.1 (В разработке)
— Аутентификация пользователей (JWT)
— Настройка прав доступа
— Экспорт отчётов в PDF/Excel
— Email уведомления

### 🔮 Версия 2.0 (Планируется)
— Дополнительные ML модели (ARIMA, LSTM)
— Real-time данные через WebSocket
— Кеширование (Redis)
— Фоновые задачи (Celery)
— CI/CD pipeline (GitHub Actions)
— Kubernetes deployment

### 🌟 Версия 3.0 (Будущее)
— Multi-tenancy поддержка
— Advanced analytics (RFM, Cohort)
— Интеграции (Tableau, Power BI)
— Mobile приложение
— Масштабирование на кластер

---

## 👤 Автор

**AlexTgn500**

 — GitHub: [@Alextgn500](https://github.com/Alextgn500)
 — Проект: [BI_mvp](https://github.com/Alextgn500/BI_mvp)
