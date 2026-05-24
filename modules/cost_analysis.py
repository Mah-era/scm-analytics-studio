"""Cost and profitability dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .analysis_common import field, has_cols, show_fig, show_kpis
from .chart_generator import empty_figure, grouped_bar, time_series
from .kpi_calculator import gross_margin, gross_margin_pct, safe_mean, safe_sum, top_category


def build_kpis(df: pd.DataFrame, mapping: dict) -> dict:
    cost = field(mapping, "Cost")
    revenue = field(mapping, "Revenue")
    product = field(mapping, "Product")
    units = field(mapping, "Total Units") or field(mapping, "Sales")

    total_cost = safe_sum(df, cost)
    return {
        "Total SCM Cost": total_cost,
        "Average Cost per Unit": total_cost / max(1, safe_sum(df, units)),
        "Highest Cost Product": top_category(df, product, cost, ascending=False),
        "Lowest Cost Product": top_category(df, product, cost, ascending=True),
        "Gross Margin": gross_margin(safe_sum(df, revenue), total_cost),
        "Gross Margin %": gross_margin_pct(safe_sum(df, revenue), total_cost) * 100,
    }


def render(df: pd.DataFrame, mapping: dict):
    st.subheader("Cost & Profitability Analysis")
    show_kpis(build_kpis(df, mapping), columns=6)

    date = field(mapping, "Date")
    cost = field(mapping, "Cost")
    category = field(mapping, "Cost Category") or field(mapping, "Category")
    product = field(mapping, "Product")
    supplier = field(mapping, "Supplier")
    procurement = field(mapping, "Procurement Cost")
    logistics = field(mapping, "Logistics Cost")
    revenue = field(mapping, "Revenue")

    c1, c2 = st.columns(2)
    with c1:
        show_fig(time_series(df, date, cost, "M", "Total SCM Cost Over Time") if has_cols(df, date, cost) else empty_figure(), "cost_time")
    with c2:
        if has_cols(df, category, cost):
            tmp = df.groupby(category)[cost].sum().reset_index()
            fig = px.pie(tmp, names=category, values=cost, title="Cost Breakdown by Category")
            show_fig(fig, "cost_breakdown")
        else:
            show_fig(empty_figure("Map Cost Category/Category and Cost."), "cost_breakdown_empty")

    c3, c4 = st.columns(2)
    with c3:
        show_fig(grouped_bar(df, product, cost, "Product-wise Cost") if has_cols(df, product, cost) else empty_figure(), "product_cost")
    with c4:
        show_fig(grouped_bar(df, supplier, cost, "Supplier-wise Cost") if has_cols(df, supplier, cost) else empty_figure(), "supplier_cost_ca")

    c5, c6 = st.columns(2)
    with c5:
        if has_cols(df, date, procurement, logistics):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp["Period"] = tmp[date].dt.to_period("M").dt.to_timestamp()
            grouped = tmp.groupby("Period")[[procurement, logistics]].sum().reset_index()
            fig = px.bar(grouped, x="Period", y=[procurement, logistics], barmode="stack", title="Logistics vs Procurement Cost")
            show_fig(fig, "logistics_vs_procurement")
        else:
            show_fig(empty_figure("Map Date, Logistics Cost, and Procurement Cost."), "log_proc_empty")
    with c6:
        if has_cols(df, date, revenue, cost):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp["Period"] = tmp[date].dt.to_period("M").dt.to_timestamp()
            grouped = tmp.groupby("Period")[[revenue, cost]].sum().reset_index()
            grouped["Gross Margin"] = grouped[revenue] - grouped[cost]
            fig = px.line(grouped, x="Period", y="Gross Margin", markers=True, title="Gross Margin Trend")
            show_fig(fig, "gross_margin_trend")
        else:
            show_fig(empty_figure("Map Date, Revenue, and Cost."), "gross_margin_empty")
