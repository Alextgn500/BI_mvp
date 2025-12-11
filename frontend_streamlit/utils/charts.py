"""Модуль визуализации данных для аналитической платформы BI_mvp.

Этот модуль предоставляет функции для создания интерактивных графиков
и диаграмм с использованием библиотеки Plotly для отображения в Streamlit.

Модуль является частью frontend-слоя проекта BI_mvp — аналитической
платформы для малого бизнеса, предназначенной для визуализации данных
о продажах, товарах и регионах.
"""

from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_sales_trend_chart(trend_data: List[Dict]) -> go.Figure:
    """
    Создаёт график тренда продаж по времени

    Args:
        trend_data: список словарей с полями 'period' и 'total_sales'

    Returns:
        Plotly Figure объект
    """
    if not trend_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных для отображения",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    df = pd.DataFrame(trend_data)

    fig = px.line(
        df,
        x="period",
        y="total_sales",
        title="📈 Тренд продаж",
        labels={"period": "Период", "total_sales": "Выручка (₽)"},
        markers=True,
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Период",
        yaxis_title="Выручка (₽)",
        template="plotly_white",
    )

    return fig


def create_region_chart(region_data: List[Dict]) -> go.Figure:
    """
    Создаёт круговую диаграмму продаж по регионам

    Args:
        region_data: список словарей с полями 'region' и 'total_sales'

    Returns:
        Plotly Figure объект
    """
    if not region_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных для отображения",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    df = pd.DataFrame(region_data)

    fig = px.pie(
        df,
        values="total_sales",
        names="region",
        title="🌍 Продажи по регионам",
        hole=0.4,  # делаем диаграмму в виде пончика
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Выручка: ₽%{value:,.0f}<br>Доля: %{percent}<extra></extra>",
    )

    return fig


def create_top_products_chart(products_data: List[Dict]) -> go.Figure:
    """
    Создаёт горизонтальный столбчатый график топ товаров

    Args:
        products_data: список словарей с полями 'product_name' и 'total_sales'

    Returns:
        Plotly Figure объект
    """
    if not products_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных для отображения",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    df = pd.DataFrame(products_data)

    # Сортируем по убыванию выручки
    df = df.sort_values("total_sales", ascending=True)

    fig = px.bar(
        df,
        x="total_sales",
        y="product_name",
        orientation="h",
        title="🏆 Топ товаров по выручке",
        labels={"total_sales": "Выручка (₽)", "product_name": "Товар"},
        text="total_sales",
    )

    fig.update_traces(
        texttemplate="₽%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Выручка: ₽%{x:,.0f}<extra></extra>",
    )

    fig.update_layout(
        xaxis_title="Выручка (₽)",
        yaxis_title="Товар",
        template="plotly_white",
        height=400
        + len(df) * 30,  # динамическая высота в зависимости от количества товаров
    )

    return fig


def create_sales_by_category_chart(category_data: List[Dict]) -> go.Figure:
    """
    Создаёт столбчатый график продаж по категориям

    Args:
        category_data: список словарей с полями 'category' и 'total_sales'

    Returns:
        Plotly Figure объект
    """
    if not category_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных для отображения",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    df = pd.DataFrame(category_data)
    df = df.sort_values("total_sales", ascending=False)

    fig = px.bar(
        df,
        x="category",
        y="total_sales",
        title="📦 Продажи по категориям",
        labels={"category": "Категория", "total_sales": "Выручка (₽)"},
        text="total_sales",
        color="total_sales",
        color_continuous_scale="Blues",
    )

    fig.update_traces(
        texttemplate="₽%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Выручка: ₽%{y:,.0f}<extra></extra>",
    )

    fig.update_layout(
        xaxis_title="Категория",
        yaxis_title="Выручка (₽)",
        template="plotly_white",
        showlegend=False,
    )

    return fig
