"""Procurement and supplier performance dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .analysis_common import field, has_cols, show_fig, show_kpis
from .chart_generator import empty_figure, grouped_bar, time_series
from .kpi_calculator import safe_div, safe_mean, safe_sum


def build_kpis(df: pd.DataFrame, mapping: dict) -> dict:
    supplier = field(mapping, "Supplier")
    cost = field(mapping, "Procurement Cost") or field(mapping, "Cost")
    lead = field(mapping, "Lead Time")
    delivery = field(mapping, "Delivery Date")
    promised = field(mapping, "Promised Delivery Date")
    defective = field(mapping, "Defective Units")
    total_units = field(mapping, "Total Units")

    on_time_pct = 0.0
    best_supplier = "N/A"
    worst_supplier = "N/A"

    if has_cols(df, supplier, delivery, promised):
        actual = pd.to_datetime(df[delivery], errors="coerce")
        due = pd.to_datetime(df[promised], errors="coerce")
        on_time = actual <= due
        on_time_pct = on_time.mean() * 100
        tmp = df.copy()
        tmp["_on_time"] = on_time.astype(int)
        score = tmp.groupby(supplier)["_on_time"].mean().sort_values(ascending=False)
        if not score.empty:
            best_supplier = str(score.index[0])
            worst_supplier = str(score.index[-1])

    defect_rate = safe_div(safe_sum(df, defective), safe_sum(df, total_units)) * 100

    return {
        "Total Procurement Cost": safe_sum(df, cost),
        "Average Lead Time": safe_mean(df, lead),
        "Best Supplier": best_supplier,
        "Worst Supplier": worst_supplier,
        "On-time Delivery %": on_time_pct,
        "Supplier Defect Rate %": defect_rate,
        "Average Purchase Price": safe_mean(df, cost),
    }


def render(df: pd.DataFrame, mapping: dict):
    st.subheader("Procurement & Supplier Performance")
    show_kpis(build_kpis(df, mapping), columns=4)

    supplier = field(mapping, "Supplier")
    qty = field(mapping, "Total Units") or field(mapping, "Demand")
    cost = field(mapping, "Procurement Cost") or field(mapping, "Cost")
    lead = field(mapping, "Lead Time")
    date = field(mapping, "Date")
    defective = field(mapping, "Defective Units")
    total_units = field(mapping, "Total Units")
    delivery = field(mapping, "Delivery Date")
    promised = field(mapping, "Promised Delivery Date")

    c1, c2 = st.columns(2)
    with c1:
        show_fig(grouped_bar(df, supplier, qty, "Supplier-wise Purchase Volume") if has_cols(df, supplier, qty) else empty_figure(), "supplier_volume")
    with c2:
        show_fig(grouped_bar(df, supplier, cost, "Supplier-wise Purchase Cost") if has_cols(df, supplier, cost) else empty_figure(), "supplier_cost")

    c3, c4 = st.columns(2)
    with c3:
        show_fig(grouped_bar(df, supplier, lead, "Supplier Lead Time Comparison") if has_cols(df, supplier, lead) else empty_figure(), "supplier_lead")
    with c4:
        if has_cols(df, supplier, delivery, promised):
            tmp = df.copy()
            tmp["_on_time"] = (pd.to_datetime(tmp[delivery], errors="coerce") <= pd.to_datetime(tmp[promised], errors="coerce")).astype(int)
            grouped = tmp.groupby(supplier)["_on_time"].mean().reset_index()
            grouped["On-time %"] = grouped["_on_time"] * 100
            fig = px.bar(grouped, x=supplier, y="On-time %", title="Supplier On-time Delivery Rate")
            show_fig(fig, "supplier_on_time")
        else:
            show_fig(empty_figure("Map Supplier, Delivery Date, and Promised Delivery Date for on-time rate."), "supplier_on_time_empty")

    c5, c6 = st.columns(2)
    with c5:
        show_fig(time_series(df, date, cost, "M", "Purchase Price / Cost Trend") if has_cols(df, date, cost) else empty_figure(), "purchase_price_trend")
    with c6:
        if has_cols(df, supplier, defective, total_units):
            tmp = df.groupby(supplier).agg({defective: "sum", total_units: "sum"}).reset_index()
            tmp["Defect Rate %"] = tmp[defective] / tmp[total_units].replace(0, pd.NA) * 100
            fig = px.pie(tmp, names=supplier, values="Defect Rate %", title="Supplier Defect Rate")
            show_fig(fig, "supplier_defect_rate")
        else:
            show_fig(empty_figure("Map Supplier, Defective Units, and Total Units for defect rate."), "supplier_defect_empty")

    if has_cols(df, supplier, lead, cost):
        score = df.groupby(supplier).agg({lead: "mean", cost: "sum"}).reset_index()
        fig = px.imshow(score.set_index(supplier).T, text_auto=True, aspect="auto", title="Supplier Performance Scorecard")
        show_fig(fig, "supplier_scorecard")
