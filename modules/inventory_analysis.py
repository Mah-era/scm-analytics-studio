"""Inventory dashboard."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from .analysis_common import field, has_cols, show_fig, show_kpis
from .chart_generator import empty_figure, grouped_bar, pareto_chart, time_series
from .kpi_calculator import days_inventory_outstanding, inventory_turnover, safe_div, safe_mean, safe_sum


def build_kpis(df: pd.DataFrame, mapping: dict) -> dict:
    inventory = field(mapping, "Inventory")
    cost = field(mapping, "Cost")
    cogs = field(mapping, "COGS")
    avg_inv = field(mapping, "Average Inventory")
    stockout = field(mapping, "Stockout Event")
    demand = field(mapping, "Demand")

    inv_units = safe_sum(df, inventory)
    inv_value = inv_units * (safe_mean(df, cost) if cost else 1)
    turnover = inventory_turnover(safe_sum(df, cogs), safe_mean(df, avg_inv) or safe_mean(df, inventory))
    stockout_rate = safe_div(safe_sum(df, stockout), max(1, len(df))) * 100 if stockout else 0.0

    overstock_count = 0
    if inventory and inventory in df.columns:
        s = pd.to_numeric(df[inventory], errors="coerce")
        overstock_count = int((s > s.quantile(0.9)).sum()) if s.notna().any() else 0

    return {
        "Total Inventory Value": inv_value,
        "Average Stock Level": safe_mean(df, inventory),
        "Inventory Turnover Ratio": turnover,
        "Stockout Frequency %": stockout_rate,
        "Overstock Count": overstock_count,
        "Days Inventory Remaining": days_inventory_outstanding(turnover),
    }


def render(df: pd.DataFrame, mapping: dict):
    st.subheader("Inventory Analysis")
    show_kpis(build_kpis(df, mapping), columns=6)

    date = field(mapping, "Date")
    sku = field(mapping, "SKU")
    inventory = field(mapping, "Inventory")
    cogs = field(mapping, "COGS")
    avg_inv = field(mapping, "Average Inventory")
    stockout = field(mapping, "Stockout Event")
    product = field(mapping, "Product")
    last_movement = field(mapping, "Last Movement Date")
    demand = field(mapping, "Demand")

    c1, c2 = st.columns(2)
    with c1:
        show_fig(time_series(df, date, inventory, "M", "Inventory Levels Over Time") if has_cols(df, date, inventory) else empty_figure(), "inventory_time")
    with c2:
        show_fig(grouped_bar(df, sku, inventory, "SKU-wise Stock Levels") if has_cols(df, sku, inventory) else empty_figure(), "sku_stock")

    c3, c4 = st.columns(2)
    with c3:
        show_fig(pareto_chart(df, sku or product, inventory, "ABC / Pareto Inventory Analysis") if has_cols(df, sku or product, inventory) else empty_figure(), "abc_pareto")
    with c4:
        if has_cols(df, date, cogs, avg_inv):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp["Period"] = tmp[date].dt.to_period("M").dt.to_timestamp()
            grouped = tmp.groupby("Period").agg({cogs: "sum", avg_inv: "mean"}).reset_index()
            grouped["Inventory Turnover"] = grouped[cogs] / grouped[avg_inv].replace(0, pd.NA)
            fig = px.bar(grouped, x="Period", y="Inventory Turnover", title="Inventory Turnover Over Time")
            show_fig(fig, "inventory_turnover")
        else:
            show_fig(empty_figure("Map Date, COGS, and Average Inventory for turnover."), "inventory_turnover_empty")

    c5, c6 = st.columns(2)
    with c5:
        if has_cols(df, date, stockout):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp["Period"] = tmp[date].dt.to_period("M").dt.to_timestamp()
            grouped = tmp.groupby("Period")[stockout].sum().reset_index()
            fig = px.line(grouped, x="Period", y=stockout, markers=True, title="Stockout Frequency")
            show_fig(fig, "stockout_frequency")
        else:
            show_fig(empty_figure("Map Date and Stockout Event for stockout frequency."), "stockout_empty")
    with c6:
        if has_cols(df, inventory, demand, sku or product):
            fig = px.scatter(df, x=inventory, y=demand, color=sku or product, title="Slow-moving Inventory Scatter")
            show_fig(fig, "slow_moving_scatter")
        else:
            show_fig(empty_figure("Map Inventory, Demand, and SKU/Product for slow-moving inventory."), "slow_moving_empty")

    if has_cols(df, last_movement, inventory, sku or product):
        tmp = df.copy()
        tmp[last_movement] = pd.to_datetime(tmp[last_movement], errors="coerce")
        cutoff = pd.Timestamp.today() - pd.Timedelta(days=90)
        dead = tmp[(tmp[last_movement] < cutoff) & (pd.to_numeric(tmp[inventory], errors="coerce") > 0)]
        st.markdown("#### Dead Stock Candidates")
        st.dataframe(dead[[sku or product, inventory, last_movement]].head(50), width="stretch")
