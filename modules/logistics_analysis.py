"""Logistics and transportation dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .analysis_common import field, has_cols, show_fig, show_kpis
from .chart_generator import empty_figure, grouped_bar, time_series
from .kpi_calculator import safe_mean, safe_sum


def build_kpis(df: pd.DataFrame, mapping: dict) -> dict:
    cost = field(mapping, "Shipment Cost") or field(mapping, "Logistics Cost")
    delivery_time = field(mapping, "Lead Time")
    delivery = field(mapping, "Delivery Date")
    promised = field(mapping, "Promised Delivery Date")
    shipment = field(mapping, "Shipment ID")

    total_deliveries = len(df)
    on_time_rate = 0.0
    late_count = 0
    if has_cols(df, delivery, promised):
        on_time = pd.to_datetime(df[delivery], errors="coerce") <= pd.to_datetime(df[promised], errors="coerce")
        on_time_rate = on_time.mean() * 100
        late_count = int((~on_time).sum())

    shipments = df[shipment].nunique() if shipment and shipment in df.columns else len(df)
    shipments = max(1, int(shipments))

    return {
        "Total Logistics Cost": safe_sum(df, cost),
        "Average Delivery Time": safe_mean(df, delivery_time),
        "On-time Delivery Rate %": on_time_rate,
        "Late Shipment Count": late_count,
        "Average Cost per Shipment": safe_sum(df, cost) / shipments,
    }


def render(df: pd.DataFrame, mapping: dict):
    st.subheader("Logistics & Transportation Analysis")
    show_kpis(build_kpis(df, mapping), columns=5)

    date = field(mapping, "Date")
    lead = field(mapping, "Lead Time")
    route = field(mapping, "Route")
    cost = field(mapping, "Shipment Cost") or field(mapping, "Logistics Cost")
    carrier = field(mapping, "Carrier")
    delivery = field(mapping, "Delivery Date")
    promised = field(mapping, "Promised Delivery Date")
    region = field(mapping, "Region")
    warehouse = field(mapping, "Warehouse")
    shipment = field(mapping, "Shipment ID")

    c1, c2 = st.columns(2)
    with c1:
        show_fig(time_series(df, date, lead, "M", "Delivery Time Trend") if has_cols(df, date, lead) else empty_figure(), "delivery_time_trend")
    with c2:
        show_fig(grouped_bar(df, route, cost, "Transportation Cost per Route") if has_cols(df, route, cost) else empty_figure(), "route_cost")

    c3, c4 = st.columns(2)
    with c3:
        if has_cols(df, carrier, lead, cost):
            fig = px.scatter(df, x=lead, y=cost, color=carrier, title="Carrier-wise Performance")
            show_fig(fig, "carrier_performance")
        else:
            show_fig(empty_figure("Map Carrier, Lead Time, and Cost for carrier performance."), "carrier_perf_empty")
    with c4:
        show_fig(time_series(df, date, cost, "M", "Freight Cost Over Time") if has_cols(df, date, cost) else empty_figure(), "freight_cost_time")

    c5, c6 = st.columns(2)
    with c5:
        if has_cols(df, date, delivery, promised):
            tmp = df.copy()
            tmp[date] = pd.to_datetime(tmp[date], errors="coerce")
            tmp["_late"] = (pd.to_datetime(tmp[delivery], errors="coerce") > pd.to_datetime(tmp[promised], errors="coerce")).astype(int)
            tmp["Period"] = tmp[date].dt.to_period("M").dt.to_timestamp()
            grouped = tmp.groupby("Period")["_late"].sum().reset_index()
            fig = px.line(grouped, x="Period", y="_late", markers=True, title="Late Delivery Analysis")
            show_fig(fig, "late_delivery")
        else:
            show_fig(empty_figure("Map Date, Delivery Date, and Promised Delivery Date for late delivery analysis."), "late_delivery_empty")
    with c6:
        show_fig(grouped_bar(df, shipment or route, cost, "Cost per Shipment") if has_cols(df, shipment or route, cost) else empty_figure(), "cost_per_shipment")

    if has_cols(df, region, warehouse, shipment or cost):
        val = cost if cost and cost in df.columns else shipment
        pivot = df.pivot_table(index=warehouse, columns=region, values=val, aggfunc="count" if val == shipment else "sum", fill_value=0)
        fig = px.imshow(pivot, text_auto=True, aspect="auto", title="Shipment Volume by Location")
        show_fig(fig, "shipment_heatmap")
