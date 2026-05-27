"""Warehouse dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .analysis_common import field, has_cols, show_fig, show_kpis
from .chart_generator import empty_figure, grouped_bar, time_series
from .kpi_calculator import safe_div, safe_mean, safe_sum


def build_kpis(df: pd.DataFrame, mapping: dict) -> dict:
    warehouse = field(mapping, "Warehouse")
    inventory = field(mapping, "Inventory")
    cost = field(mapping, "Cost")
    used = field(mapping, "Space Used")
    capacity = field(mapping, "Space Capacity")
    picks = field(mapping, "Picks")
    accurate = field(mapping, "Accurate Picks")
    inbound = field(mapping, "Inbound Quantity")
    outbound = field(mapping, "Outbound Quantity")

    stock_value = safe_sum(df, inventory) * (safe_mean(df, cost) if cost and cost in df.columns else 1)
    util = safe_div(safe_sum(df, used), safe_sum(df, capacity)) * 100
    picking = safe_div(safe_sum(df, accurate), safe_sum(df, picks)) * 100

    return {
        "Total Warehouse Stock Value": stock_value,
        "Space Utilization %": util,
        "Picking Accuracy %": picking,
        "Inbound Stock": safe_sum(df, inbound),
        "Outbound Stock": safe_sum(df, outbound),
        "Net Inbound - Outbound": safe_sum(df, inbound) - safe_sum(df, outbound),
    }


def render(df: pd.DataFrame, mapping: dict):
    st.subheader("Warehouse Analysis")
    show_kpis(build_kpis(df, mapping), columns=6)

    warehouse = field(mapping, "Warehouse")
    inventory = field(mapping, "Inventory")
    inbound = field(mapping, "Inbound Quantity")
    outbound = field(mapping, "Outbound Quantity")
    picks = field(mapping, "Picks")
    accurate = field(mapping, "Accurate Picks")
    used = field(mapping, "Space Used")
    capacity = field(mapping, "Space Capacity")
    date = field(mapping, "Date")

    c1, c2 = st.columns(2)
    with c1:
        show_fig(grouped_bar(df, warehouse, inventory, "Warehouse Stock by Location") if has_cols(df, warehouse, inventory) else empty_figure(), "warehouse_stock")
    with c2:
        if has_cols(df, date, inbound, outbound):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp["Period"] = tmp[date].dt.to_period("M").dt.to_timestamp()
            grouped = tmp.groupby("Period")[[inbound, outbound]].sum().reset_index()
            fig = px.bar(grouped, x="Period", y=[inbound, outbound], barmode="stack", title="Inbound vs Outbound Movement")
            show_fig(fig, "inbound_outbound")
        else:
            show_fig(empty_figure("Map Date, Inbound Quantity, and Outbound Quantity."), "inbound_outbound_empty")

    c3, c4 = st.columns(2)
    with c3:
        if has_cols(df, warehouse, picks, accurate):
            tmp = df.groupby(warehouse).agg({picks: "sum", accurate: "sum"}).reset_index()
            tmp["Picking Accuracy %"] = tmp[accurate] / tmp[picks].replace(0, pd.NA) * 100
            fig = px.bar(tmp, x=warehouse, y="Picking Accuracy %", title="Picking Accuracy")
            show_fig(fig, "picking_accuracy")
        else:
            show_fig(empty_figure("Map Warehouse, Picks, and Accurate Picks."), "picking_empty")
    with c4:
        if has_cols(df, warehouse, used, capacity):
            tmp = df.groupby(warehouse).agg({used: "sum", capacity: "sum"}).reset_index()
            tmp["Storage Utilization %"] = tmp[used] / tmp[capacity].replace(0, pd.NA) * 100
            fig = px.bar(tmp, x=warehouse, y="Storage Utilization %", title="Storage Utilization")
            show_fig(fig, "storage_util")
        else:
            show_fig(empty_figure("Map Warehouse, Space Used, and Space Capacity."), "storage_empty")

    if has_cols(df, date, picks):
        show_fig(time_series(df, date, picks, "M", "Warehouse Productivity Trend"), "warehouse_productivity")
