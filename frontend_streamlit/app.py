"""Главный модуль BI_mvp — аналитическая платформа для малого бизнеса.

Приложение предоставляет веб-интерфейс для анализа бизнес-данных:
— Загрузка и обработка данных из различных источников
— Интерактивные дашборды и визуализации
— Автоматическая генерация отчётов и инсайтов
— Прогнозирование ключевых метрик

Запуск:
    streamlit run frontend_streamlit/app.py
"""

import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# URLs для API
DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://localhost:8000")
FASTAPI_ML_URL = os.getenv("FASTAPI_ML_URL", "http://localhost:8001")

st.set_page_config(page_title="BI Dashboard", layout="wide")

# ============================================
# ЗАГОЛОВОК
# ============================================
st.title("📊 BI Dashboard - Аналитика продаж")

# ============================================
# ПОЛУЧЕНИЕ ДАННЫХ ИЗ DJANGO API
# ============================================
try:
    response = requests.get(f"{DJANGO_API_URL}/api/sales/", timeout=10)
    response.raise_for_status()
    sales_data = response.json()

    if sales_data and "результаты" in sales_data:
        df = pd.DataFrame(sales_data["результаты"])  # Берем список из 'результаты'

        # Приводим названия колонок к английским (если нужно)
        column_mapping = {"дата": "date", "магазин": "shop", "сумма": "amount"}

        df.rename(columns=column_mapping, inplace=True)

        # Конвертируем дату
        df["date"] = pd.to_datetime(df["date"])

        # ----------------------------------------
        # ФИЛЬТРЫ
        # ----------------------------------------
        st.sidebar.header("Фильтры")

        # Даты
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        date_from = st.sidebar.date_input("Дата от", min_date)
        date_to = st.sidebar.date_input("Дата до", max_date)

        # Магазины
        shops = ["Все"] + sorted(df["shop"].unique().tolist())
        selected_shop = st.sidebar.selectbox("Магазин", shops)

        # Фильтрация
        mask = (df["date"].dt.date >= date_from) & (df["date"].dt.date <= date_to)
        if selected_shop != "Все":
            mask = mask & (df["shop"] == selected_shop)
        filtered_df = df[mask]

        # ----------------------------------------
        # МЕТРИКИ
        # ----------------------------------------
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Общая выручка", f"{filtered_df['amount'].sum():,.0f} ₽")
        with col2:
            st.metric("📦 Количество продаж", len(filtered_df))
        with col3:
            st.metric("📈 Средний чек", f"{filtered_df['amount'].mean():,.0f} ₽")

        # ----------------------------------------
        # ГРАФИК ПРОДАЖ ПО ДНЯМ
        # ----------------------------------------
        st.subheader("📊 Динамика продаж")
        daily_sales = filtered_df.groupby("date")["amount"].sum().reset_index()
        fig = px.line(
            daily_sales,
            x="date",
            y="amount",
            title="Продажи по дням",
            labels={"date": "Дата", "amount": "Выручка (₽)"},
        )
        st.plotly_chart(fig, use_container_width=True)

        # ----------------------------------------
        # ГРАФИК ПО МАГАЗИНАМ
        # ----------------------------------------
        st.subheader("🏪 Продажи по магазинам")
        shop_sales = filtered_df.groupby("shop")["amount"].sum().reset_index()
        fig2 = px.bar(
            shop_sales,
            x="shop",
            y="amount",
            title="Выручка по магазинам",
            labels={"shop": "Магазин", "amount": "Выручка (₽)"},
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ----------------------------------------
        # ТАБЛИЦА ДАННЫХ
        # ----------------------------------------
        st.subheader("📋 Данные продаж")
        st.dataframe(
            filtered_df.sort_values("date", ascending=False),
            use_container_width=True,
        )

except requests.exceptions.RequestException as e:
    if isinstance(e, requests.exceptions.ConnectionError):
        st.error(
            "❌ Ошибка подключения к Django API. Убедитесь, что сервер запущен на http://localhost:8000"
        )
    else:
        st.error(f"❌ Ошибка запроса: {str(e)}")
# ============================================
# МАШИННОЕ ОБУЧЕНИЕ
# ============================================
st.divider()
st.header("🤖 Машинное обучение")

# ----------------------------------------
# 1. СТАТУС МОДЕЛИ
# ----------------------------------------
st.subheader("📊 Статус модели")

model_trained = False  # pylint: disable=invalid-name
model_status = {}

try:
    status_response = requests.get(f"{FASTAPI_ML_URL}/api/v1/ml/status", timeout=10)
    if status_response.status_code == 200:
        model_status = status_response.json()
        model_trained = model_status.get("model_trained", False)

        if model_trained:
            col1, col2 = st.columns(2)
            with col1:
                st.success("✅ Модель обучена и готова к работе")
                st.info(
                    f"🕒 Последнее обучение: {model_status.get('last_trained', 'Неизвестно')}"
                )
            with col2:
                if model_status.get("metrics"):
                    metrics = model_status["metrics"]
                    st.metric("📊 MAE", f"{metrics.get('mae', 0):.2f}")
                    st.metric("📈 R²", f"{metrics.get('r2', 0):.3f}")
        else:
            st.warning("⚠️ Модель не обучена")
    else:
        st.error("❌ Не удалось получить статус модели")
except requests.exceptions.RequestException as e:
    st.error(f"❌ Ошибка при получении статуса: {str(e)}")

# ----------------------------------------
# 2. ОБУЧЕНИЕ МОДЕЛИ
# ----------------------------------------
st.divider()
st.subheader("🎓 Обучение модели")

if model_trained:
    st.info("ℹ️ Модель уже обучена. Вы можете переобучить её, нажав кнопку ниже.")

col1, col2 = st.columns([3, 1])
with col2:
    train_button = st.button(
        "🚀 Обучить модель", type="primary", use_container_width=True
    )

if train_button:
    with st.spinner("⏳ Обучение модели... Это может занять несколько минут."):
        try:
            train_response = requests.post(f"{FASTAPI_ML_URL}/api/v1/ml/train", timeout=120)

            if train_response.status_code == 200:
                result = train_response.json()
                st.success("✅ Модель успешно обучена!")

                # Показываем метрики
                if result.get("metrics"):
                    st.subheader("📊 Метрики модели")
                    metrics = result["metrics"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "MAE (Средняя абсолютная ошибка)",
                            f"{metrics.get('mae', 0):.2f}",
                        )
                    with col2:
                        st.metric(
                            "RMSE (Среднеквадратичная ошибка)",
                            f"{metrics.get('rmse', 0):.2f}",
                        )
                    with col3:
                        st.metric(
                            "R² (Коэффициент детерминации)",
                            f"{metrics.get('r2', 0):.3f}",
                        )

                st.info("ℹ️ Обновите страницу для просмотра актуального статуса")

            elif train_response.status_code == 400:
                error_data = train_response.json()
                st.error(
                    f"❌ Ошибка обучения: {error_data.get('detail', 'Неизвестная ошибка')}"
                )
            else:
                st.error(f"❌ Ошибка сервера: {train_response.status_code}")
                st.code(train_response.text)

        except requests.exceptions.Timeout:
            st.error(
                "❌ Превышено время ожидания. Обучение может продолжаться на сервере."
            )
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Ошибка при обучении модели: {str(e)}")

# ----------------------------------------
# 3. ПРОГНОЗИРОВАНИЕ
# ----------------------------------------
st.divider()
st.subheader("📈 Прогноз продаж")

if model_trained:
    # Выбор периода прогноза
    col1, col2 = st.columns([3, 1])
    with col1:
        days = st.slider(
            "Период прогноза (дней)",
            min_value=7,
            max_value=90,
            value=30,
            step=7,
            help="Выберите количество дней для прогноза",
        )
    with col2:
        predict_button = st.button(
            "📊 Получить прогноз", type="primary", use_container_width=True
        )

    if predict_button:
        with st.spinner(f"⏳ Формирование прогноза на {days} дней..."):
            try:
                predict_response = requests.post(
                    f"{FASTAPI_ML_URL}/api/v1/ml/predict?days={days}", timeout=30
                )

                if predict_response.status_code == 200:
                    forecast_data = predict_response.json()

                    # Преобразование в DataFrame
                    df_forecast = pd.DataFrame(forecast_data)

                    # Переименовываем колонки для удобства
                    df_forecast = df_forecast.rename(
                        columns={
                            "forecast_dates": "date",
                            "forecast_values": "predicted_sales",
                            "lower_bound": "lower_bound",
                            "upper_bound": "upper_bound",
                        }
                    )

                    # Удаляем колонку 'model_trained' (она не нужна в прогнозе)
                    if "model_trained" in df_forecast.columns:
                        df_forecast = df_forecast.drop(columns=["model_trained"])

                    # Преобразуем дату в datetime
                    df_forecast["date"] = pd.to_datetime(df_forecast["date"])

                    # Статистика прогноза
                    st.subheader("📊 Статистика прогноза")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "💰 Прогнозируемая выручка",
                            f"{df_forecast['predicted_sales'].sum():,.0f} ₽",
                        )
                    with col2:
                        st.metric(
                            "📈 Средний дневной прогноз",
                            f"{df_forecast['predicted_sales'].mean():,.0f} ₽",
                        )
                    with col3:
                        st.metric("📅 Период прогноза", f"{days} дней")

                    # График прогноза
                    st.subheader("📈 График прогноза")
                    fig_forecast = go.Figure()

                    # Добавляем исторические данные
                    if "filtered_df" in locals():
                        historical = (
                            filtered_df.groupby("date")["amount"].sum().reset_index()
                        )
                        fig_forecast.add_trace(
                            go.Scatter(
                                x=historical["date"],
                                y=historical["amount"],
                                mode="lines",
                                name="Исторические данные",
                                line=dict(color="blue"),
                            )
                        )

                    # Добавляем прогноз
                    fig_forecast.add_trace(
                        go.Scatter(
                            x=df_forecast["date"],
                            y=df_forecast["predicted_sales"],
                            mode="lines",
                            name="Прогноз",
                            line=dict(color="red", dash="dash"),
                        )
                    )

                    # Добавляем доверительный интервал
                    fig_forecast.add_trace(
                        go.Scatter(
                            x=df_forecast["date"],
                            y=df_forecast["upper_bound"],
                            mode="lines",
                            name="Верхняя граница",
                            line=dict(width=0),
                            showlegend=False,
                        )
                    )

                    fig_forecast.add_trace(
                        go.Scatter(
                            x=df_forecast["date"],
                            y=df_forecast["lower_bound"],
                            mode="lines",
                            name="Нижняя граница",
                            line=dict(width=0),
                            fillcolor="rgba(255, 0, 0, 0.2)",
                            fill="tonexty",
                            showlegend=True,
                        )
                    )

                    fig_forecast.update_layout(
                        title="Прогноз продаж с доверительным интервалом",
                        xaxis_title="Дата",
                        yaxis_title="Выручка (₽)",
                        hovermode="x unified",
                    )

                    st.plotly_chart(fig_forecast, use_container_width=True)

                    # Таблица прогноза
                    st.subheader("📋 Детальный прогноз")
                    st.dataframe(
                        df_forecast.rename(
                            columns={
                                "date": "Дата",
                                "predicted_sales": "Прогноз продаж (₽)",
                                "lower_bound": "Нижняя граница (₽)",
                                "upper_bound": "Верхняя граница (₽)",
                            }
                        ),
                        use_container_width=True,
                    )

                    # Кнопка скачивания
                    csv = df_forecast.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Скачать прогноз (CSV)",
                        data=csv,
                        file_name=f"forecast_{days}_days.csv",
                        mime="text/csv",
                    )

                else:
                    st.error(f"Ошибка API: {predict_response.status_code}")
                    st.write(predict_response.text)

            except requests.exceptions.RequestException as e:
                # Закрываем блок try
                st.error(f"❌ Ошибка при получении прогноза: {str(e)}")

else:
    # Закрываем блок if model_trained
    st.warning("⚠️ Сначала необходимо обучить модель")
    st.info(
        "ℹ️ Перейдите к разделу 'Обучение модели' выше и нажмите кнопку 'Обучить модель'"
    )

# ----------------------------------------
# КНОПКА НАВИГАЦИИ
# ----------------------------------------
st.divider()
if st.button("⬆️ Перейти к началу страницы"):
    st.rerun()
