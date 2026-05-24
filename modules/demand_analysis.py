"""Demand and Sales dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .analysis_common import field, has_cols, show_fig, show_kpis
from .chart_generator import empty_figure, grouped_bar, time_series
from .kpi_calculator import forecast_accuracy, safe_mean, safe_sum, top_category


def build_kpis(df: pd.DataFrame, mapping: dict) -> dict:
    date = field(mapping, "Date")
    demand = field(mapping, "Demand")
    product = field(mapping, "Product")
    forecast = field(mapping, "Forecast")

    total_demand = safe_sum(df, demand)
    avg_demand = safe_mean(df, demand)
    high_product = top_category(df, product, demand, ascending=False)
    low_product = top_category(df, product, demand, ascending=True)

    growth = 0.0
    if date and demand and date in df.columns and demand in df.columns:
        tmp = df.copy()
        tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
        tmp = tmp.dropna(subset=[date]).sort_values(date)
        if not tmp.empty:
            monthly = tmp.groupby(tmp[date].dt.to_period("M"))[demand].sum()
            if len(monthly) >= 2 and monthly.iloc[0] != 0:
                growth = (monthly.iloc[-1] - monthly.iloc[0]) / monthly.iloc[0] * 100

    kpis = {
        "Total Demand": total_demand,
        "Average Demand": avg_demand,
        "Highest Demand Product": high_product,
        "Lowest Demand Product": low_product,
        "Demand Growth %": growth,
    }

    if demand and forecast and demand in df.columns and forecast in df.columns:
        kpis["Forecast Accuracy %"] = forecast_accuracy(df[demand], df[forecast]) * 100

    return kpis


def render(df: pd.DataFrame, mapping: dict):
    st.subheader("Demand & Sales Analysis")
    show_kpis(build_kpis(df, mapping), columns=5)

    date = field(mapping, "Date")
    demand = field(mapping, "Demand")
    forecast = field(mapping, "Forecast")
    product = field(mapping, "Product")
    region = field(mapping, "Region")
    customer = field(mapping, "Customer")

    c1, c2 = st.columns(2)
    with c1:
        show_fig(time_series(df, date, demand, "M", "Monthly Demand Trend") if has_cols(df, date, demand) else empty_figure(), "demand_monthly")
    with c2:
        show_fig(time_series(df, date, demand, "W", "Weekly Demand Trend") if has_cols(df, date, demand) else empty_figure(), "demand_weekly")

    c3, c4 = st.columns(2)
    with c3:
        show_fig(grouped_bar(df, product, demand, "Product-wise Demand") if has_cols(df, product, demand) else empty_figure(), "demand_product")
    with c4:
        show_fig(grouped_bar(df, region, demand, "Region-wise Demand") if has_cols(df, region, demand) else empty_figure(), "demand_region")

    c5, c6 = st.columns(2)
    with c5:
        show_fig(grouped_bar(df, customer, demand, "Customer-wise Demand") if has_cols(df, customer, demand) else empty_figure(), "demand_customer")
    with c6:
        if has_cols(df, date, demand):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp["Period"] = tmp[date].dt.to_period("M").dt.to_timestamp()
            vol = tmp.groupby("Period")[demand].std().reset_index().fillna(0)
            fig = px.line(vol, x="Period", y=demand, markers=True, title="Demand Volatility")
            show_fig(fig, "demand_volatility")
        else:
            show_fig(empty_figure(), "demand_volatility_empty")

    c7, c8 = st.columns(2)
    with c7:
        if has_cols(df, date, demand, forecast):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp["Period"] = tmp[date].dt.to_period("M").dt.to_timestamp()
            monthly = tmp.groupby("Period")[[demand, forecast]].sum().reset_index()
            fig = px.line(monthly, x="Period", y=[demand, forecast], markers=True, title="Actual vs Forecasted Demand")
            show_fig(fig, "actual_vs_forecast")
        else:
            show_fig(empty_figure("Map Date, Demand, and Forecast for actual vs forecast."), "actual_vs_forecast_empty")
    with c8:
        if has_cols(df, date, demand):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp = tmp.dropna(subset=[date]).sort_values(date)
            daily = tmp.groupby(date)[demand].sum().reset_index()
            daily["Moving Average"] = daily[demand].rolling(window=7, min_periods=1).mean()
            fig = px.line(daily, x=date, y=[demand, "Moving Average"], title="Moving Average Demand Trend")
            show_fig(fig, "moving_average_demand")
        else:
            show_fig(empty_figure(), "moving_average_empty")
