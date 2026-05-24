"""Production and operations dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .analysis_common import field, has_cols, show_fig, show_kpis
from .chart_generator import empty_figure, grouped_bar, time_series
from .kpi_calculator import safe_div, safe_mean, safe_sum


def build_kpis(df: pd.DataFrame, mapping: dict) -> dict:
    production = field(mapping, "Production Quantity")
    capacity = field(mapping, "Capacity") or field(mapping, "Maximum Capacity")
    defective = field(mapping, "Defective Units")
    total_units = field(mapping, "Total Units")
    downtime = field(mapping, "Downtime")

    return {
        "Total Production Volume": safe_sum(df, production),
        "Average Production": safe_mean(df, production),
        "Production Efficiency %": safe_div(safe_sum(df, production), safe_sum(df, capacity)) * 100,
        "Defect Rate %": safe_div(safe_sum(df, defective), safe_sum(df, total_units)) * 100,
        "Downtime Hours": safe_sum(df, downtime),
    }


def render(df: pd.DataFrame, mapping: dict):
    st.subheader("Production / Operations Analysis")
    show_kpis(build_kpis(df, mapping), columns=5)

    date = field(mapping, "Date")
    production = field(mapping, "Production Quantity")
    planned = field(mapping, "Planned Production")
    product = field(mapping, "Product")
    downtime = field(mapping, "Downtime")
    capacity = field(mapping, "Capacity") or field(mapping, "Maximum Capacity")
    defective = field(mapping, "Defective Units")
    total_units = field(mapping, "Total Units")

    c1, c2 = st.columns(2)
    with c1:
        show_fig(time_series(df, date, production, "M", "Production Volume Over Time") if has_cols(df, date, production) else empty_figure(), "production_time")
    with c2:
        show_fig(grouped_bar(df, product, production, "Product-wise Production") if has_cols(df, product, production) else empty_figure(), "product_production")

    c3, c4 = st.columns(2)
    with c3:
        show_fig(time_series(df, date, downtime, "M", "Machine Downtime Trend") if has_cols(df, date, downtime) else empty_figure(), "downtime_trend")
    with c4:
        if has_cols(df, product, production, capacity):
            tmp = df.groupby(product).agg({production: "sum", capacity: "sum"}).reset_index()
            tmp["Capacity Utilization %"] = tmp[production] / tmp[capacity].replace(0, pd.NA) * 100
            fig = px.bar(tmp, x=product, y="Capacity Utilization %", title="Capacity Utilization")
            show_fig(fig, "capacity_util")
        else:
            show_fig(empty_figure("Map Product, Production Quantity, and Capacity."), "capacity_empty")

    c5, c6 = st.columns(2)
    with c5:
        if has_cols(df, date, defective, total_units):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp["Period"] = tmp[date].dt.to_period("M").dt.to_timestamp()
            grouped = tmp.groupby("Period").agg({defective: "sum", total_units: "sum"}).reset_index()
            grouped["Defect Rate %"] = grouped[defective] / grouped[total_units].replace(0, pd.NA) * 100
            fig = px.line(grouped, x="Period", y="Defect Rate %", markers=True, title="Defect Rate Trend")
            show_fig(fig, "defect_rate_trend")
        else:
            show_fig(empty_figure("Map Date, Defective Units, and Total Units."), "defect_empty")
    with c6:
        if has_cols(df, product, planned, production):
            tmp = df.groupby(product)[[planned, production]].sum().reset_index()
            fig = px.bar(tmp, x=product, y=[planned, production], barmode="group", title="Planned vs Actual Production")
            show_fig(fig, "planned_actual_prod")
        else:
            show_fig(empty_figure("Map Product, Planned Production, and Production Quantity."), "planned_actual_empty")
