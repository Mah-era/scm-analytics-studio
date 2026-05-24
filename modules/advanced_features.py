"""Advanced offline SCM planning, validation, glossary, and export features."""
from __future__ import annotations

import json
import sqlite3
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from .analysis_common import field, has_cols, show_fig, show_kpis
from .chart_generator import chart_png_bytes, empty_figure, grouped_bar, make_chart, pareto_chart
from .kpi_calculator import safe_div, safe_mean, safe_sum
from .local_storage import list_audit_events, list_dashboard_templates, list_feedback, save_dashboard_template
from .reporting import to_excel_bytes


METRIC_GLOSSARY = {
    "OTIF": "On-time and in-full orders / total orders.",
    "Fill Rate": "Fulfilled or shipped quantity / ordered quantity.",
    "Perfect Order Rate": "Orders delivered on time, in full, with no defects.",
    "Backorder Rate": "Backordered quantity / ordered quantity.",
    "MAPE": "Average absolute forecast error as a percentage of actual demand.",
    "WAPE": "Absolute forecast error total / actual demand total.",
    "Forecast Bias": "(Forecast - Actual) / Actual.",
    "Tracking Signal": "Cumulative forecast error / mean absolute deviation.",
    "Safety Stock": "Z-score x demand standard deviation x square root of lead time.",
    "Reorder Point": "Average demand during lead time + safety stock.",
    "EOQ": "Square root of (2 x annual demand x order cost / holding cost).",
    "GMROI": "Gross margin / average inventory value.",
    "PPV": "(Actual price - standard or contract price) x purchased quantity.",
    "Landed Cost": "Product cost + allocated freight/logistics cost.",
    "OEE": "Availability x performance x quality.",
    "Yield": "Good quantity / total production quantity.",
    "Cash-to-Cash": "DIO + DSO - DPO.",
}


def num(df: pd.DataFrame, col: Optional[str]) -> pd.Series:
    if col and col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(dtype="float64")


def dates(df: pd.DataFrame, col: Optional[str]) -> pd.Series:
    if col and col in df.columns:
        return pd.to_datetime(df[col], errors="coerce")
    return pd.Series(dtype="datetime64[ns]")


def cat(df: pd.DataFrame, col: Optional[str]) -> pd.Series:
    if col and col in df.columns:
        return df[col].astype(str)
    return pd.Series(dtype="object")


def infer_on_time(df: pd.DataFrame, mapping: dict) -> pd.Series:
    actual = dates(df, field(mapping, "Delivery Date"))
    promised = dates(df, field(mapping, "Promised Delivery Date") or field(mapping, "Due Date"))
    if actual.empty or promised.empty:
        return pd.Series(False, index=df.index)
    return (actual <= promised).fillna(False)


def ordered_quantity(df: pd.DataFrame, mapping: dict) -> pd.Series:
    for name in ["Order Quantity", "Demand", "Total Orders", "Total Units"]:
        col = field(mapping, name)
        if col and col in df.columns:
            return num(df, col).fillna(0)
    return pd.Series(1, index=df.index, dtype="float64")


def shipped_quantity(df: pd.DataFrame, mapping: dict) -> pd.Series:
    for name in ["Shipped Quantity", "Fulfilled Orders", "Sales", "Outbound Quantity"]:
        col = field(mapping, name)
        if col and col in df.columns:
            return num(df, col).fillna(0)
    return ordered_quantity(df, mapping)


def forecast_metrics(df: pd.DataFrame, mapping: dict, group_col: Optional[str] = None) -> pd.DataFrame:
    actual_col = field(mapping, "Demand") or field(mapping, "Sales")
    forecast_col = field(mapping, "Forecast")
    if not has_cols(df, actual_col, forecast_col):
        return pd.DataFrame()
    tmp = df.copy()
    tmp["_actual"] = num(tmp, actual_col)
    tmp["_forecast"] = num(tmp, forecast_col)
    tmp = tmp.dropna(subset=["_actual", "_forecast"])
    if tmp.empty:
        return pd.DataFrame()
    tmp["_error"] = tmp["_forecast"] - tmp["_actual"]
    tmp["_abs_error"] = tmp["_error"].abs()
    tmp["_ape"] = np.where(tmp["_actual"].replace(0, np.nan).notna(), tmp["_abs_error"] / tmp["_actual"].replace(0, np.nan), np.nan)
    groups = [group_col] if group_col and group_col in tmp.columns else []
    if groups:
        out = tmp.groupby(groups).agg(actual=("_actual", "sum"), forecast=("_forecast", "sum"), abs_error=("_abs_error", "sum"), error=("_error", "sum"), mape=("_ape", "mean")).reset_index()
    else:
        out = pd.DataFrame([{
            "actual": tmp["_actual"].sum(),
            "forecast": tmp["_forecast"].sum(),
            "abs_error": tmp["_abs_error"].sum(),
            "error": tmp["_error"].sum(),
            "mape": tmp["_ape"].mean(),
        }])
    out["WAPE %"] = out["abs_error"] / out["actual"].replace(0, np.nan) * 100
    out["MAPE %"] = out["mape"] * 100
    out["Bias %"] = out["error"] / out["actual"].replace(0, np.nan) * 100
    return out.fillna(0)


def abc_xyz(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    sku = field(mapping, "SKU") or field(mapping, "Product")
    demand = field(mapping, "Demand") or field(mapping, "Sales")
    cost = field(mapping, "Cost") or field(mapping, "Unit Price") or field(mapping, "Revenue")
    if not has_cols(df, sku, demand):
        return pd.DataFrame()
    tmp = df[[sku]].copy()
    tmp["_demand"] = num(df, demand).fillna(0)
    tmp["_cost"] = num(df, cost).fillna(1) if cost and cost in df.columns else 1
    tmp["_value"] = tmp["_demand"] * tmp["_cost"]
    grouped = tmp.groupby(sku).agg(demand=("_demand", "sum"), value=("_value", "sum"), mean_demand=("_demand", "mean"), std_demand=("_demand", "std")).reset_index()
    grouped = grouped.sort_values("value", ascending=False)
    total = grouped["value"].sum()
    grouped["cum_value_pct"] = grouped["value"].cumsum() / total * 100 if total else 0
    grouped["ABC"] = np.select([grouped["cum_value_pct"] <= 80, grouped["cum_value_pct"] <= 95], ["A", "B"], default="C")
    grouped["cv"] = grouped["std_demand"].fillna(0) / grouped["mean_demand"].replace(0, np.nan)
    grouped["XYZ"] = np.select([grouped["cv"] <= 0.5, grouped["cv"] <= 1.0], ["X", "Y"], default="Z")
    grouped["ABC/XYZ"] = grouped["ABC"] + grouped["XYZ"]
    return grouped.fillna(0)


def inventory_risk_table(df: pd.DataFrame, mapping: dict, service_z: float = 1.65, demand_uplift: float = 0.0, lead_time_factor: float = 1.0) -> pd.DataFrame:
    sku = field(mapping, "SKU") or field(mapping, "Product")
    demand = field(mapping, "Demand") or field(mapping, "Sales")
    inv = field(mapping, "Inventory")
    lead = field(mapping, "Lead Time")
    cost = field(mapping, "Cost") or field(mapping, "Unit Price")
    open_supply = field(mapping, "Open Supply") or field(mapping, "Open PO Quantity") or field(mapping, "Inbound Quantity")
    if not has_cols(df, sku, demand, inv):
        return pd.DataFrame()
    tmp = pd.DataFrame({
        "Item": cat(df, sku),
        "Demand": num(df, demand).fillna(0) * (1 + demand_uplift / 100),
        "Inventory": num(df, inv).fillna(0),
        "Lead Time": (num(df, lead).fillna(1) if lead and lead in df.columns else 1) * lead_time_factor,
        "Unit Cost": num(df, cost).fillna(1) if cost and cost in df.columns else 1,
        "Open Supply": num(df, open_supply).fillna(0) if open_supply and open_supply in df.columns else 0,
    })
    grouped = tmp.groupby("Item").agg(
        avg_demand=("Demand", "mean"),
        std_demand=("Demand", "std"),
        total_demand=("Demand", "sum"),
        inventory=("Inventory", "sum"),
        lead_time=("Lead Time", "mean"),
        unit_cost=("Unit Cost", "mean"),
        open_supply=("Open Supply", "sum"),
    ).reset_index()
    grouped["safety_stock"] = service_z * grouped["std_demand"].fillna(0) * np.sqrt(grouped["lead_time"].clip(lower=1))
    grouped["reorder_point"] = grouped["avg_demand"] * grouped["lead_time"] + grouped["safety_stock"]
    grouped["net_stock"] = grouped["inventory"] + grouped["open_supply"]
    grouped["days_until_stockout"] = grouped["net_stock"] / grouped["avg_demand"].replace(0, np.nan)
    grouped["stockout_risk"] = grouped["net_stock"] < grouped["reorder_point"]
    grouped["excess_units"] = (grouped["net_stock"] - grouped["reorder_point"] * 2).clip(lower=0)
    grouped["excess_value"] = grouped["excess_units"] * grouped["unit_cost"]
    return grouped.fillna(0).sort_values(["stockout_risk", "excess_value"], ascending=[False, False])


def validation_report(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    issues = []

    def add(issue: str, severity: str, count: int, detail: str) -> None:
        if count:
            issues.append({"Severity": severity, "Issue": issue, "Rows": int(count), "Detail": detail})

    for field_name in ["Date", "Product", "Demand", "Inventory", "Supplier", "Cost"]:
        col = field(mapping, field_name)
        add(f"Missing mapped field: {field_name}", "Medium", 1 if not col else 0, "Map this field for richer dashboards.")

    order_id = field(mapping, "Order ID")
    if order_id and order_id in df.columns:
        add("Duplicate business key", "High", int(df[order_id].duplicated().sum()), order_id)

    for label in ["Demand", "Sales", "Inventory", "Cost", "Shipment Cost", "Production Quantity"]:
        col = field(mapping, label)
        if col and col in df.columns:
            values = num(df, col)
            invalid_tokens = df[col].notna() & values.isna()
            add(f"Invalid numeric token in {label}", "High", int(invalid_tokens.sum()), col)
            add(f"Negative {label}", "High", int((values < 0).sum()), col)

    order_date = field(mapping, "Order Date")
    receipt_date = field(mapping, "Received Date") or field(mapping, "Receipt Date")
    delivery_date = field(mapping, "Delivery Date")
    promised = field(mapping, "Promised Delivery Date") or field(mapping, "Due Date")
    if order_date and receipt_date and has_cols(df, order_date, receipt_date):
        add("Receipt before order date", "High", int((dates(df, receipt_date) < dates(df, order_date)).sum()), f"{receipt_date} < {order_date}")
    if order_date and delivery_date and has_cols(df, order_date, delivery_date):
        add("Ship/delivery before order date", "High", int((dates(df, delivery_date) < dates(df, order_date)).sum()), f"{delivery_date} < {order_date}")
    if promised and delivery_date and has_cols(df, promised, delivery_date):
        add("Late delivery", "Medium", int((dates(df, delivery_date) > dates(df, promised)).sum()), f"{delivery_date} > {promised}")

    lead = field(mapping, "Lead Time")
    if lead and lead in df.columns:
        lead_values = num(df, lead)
        add("Impossible lead time", "High", int(((lead_values < 0) | (lead_values > 365)).sum()), "Lead time outside 0-365 days.")

    planned = field(mapping, "Promised Delivery Date") or field(mapping, "Due Date")
    actual = field(mapping, "Delivery Date") or field(mapping, "Actual End Date")
    if planned and actual and has_cols(df, planned, actual):
        add("Actual before planned date", "Medium", int((dates(df, actual) < dates(df, planned)).sum()), f"{actual} < {planned}")

    currency = field(mapping, "Currency")
    cost = field(mapping, "Cost")
    if cost and cost in df.columns:
        add("Missing currency on cost rows", "Medium", int(df[currency].isna().sum()) if currency and currency in df.columns else 0, currency or "Currency")
    if currency and currency in df.columns:
        add("Mixed currency", "Medium", 1 if df[currency].dropna().astype(str).nunique() > 1 else 0, currency)

    uom = field(mapping, "UOM")
    if uom and uom in df.columns:
        add("Mixed UOM", "Medium", 1 if df[uom].dropna().astype(str).nunique() > 1 else 0, uom)

    sku = field(mapping, "SKU")
    product = field(mapping, "Product")
    if sku and product and has_cols(df, sku, product):
        combos = df.groupby(sku)[product].nunique(dropna=True)
        add("SKU mapped to multiple product names", "Medium", int((combos > 1).sum()), "Check master data consistency.")

    return pd.DataFrame(issues) if issues else pd.DataFrame([{"Severity": "Info", "Issue": "No validation issues detected", "Rows": 0, "Detail": ""}])


def relationship_health(sheets: Dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    if not sheets:
        return pd.DataFrame([{"Check": "Multi-table model", "Status": "Single table loaded", "Detail": "Upload a multi-sheet workbook to inspect relationship coverage."}])
    rows = []
    keys = ["SKU", "Supplier", "Warehouse", "Order_ID", "PO_Number", "Shipment_ID"]
    for key in keys:
        present = [name for name, sheet in sheets.items() if key in sheet.columns]
        if len(present) >= 2:
            rows.append({"Check": key, "Status": "Join key available", "Detail": ", ".join(present)})
    return pd.DataFrame(rows) if rows else pd.DataFrame([{"Check": "Relationship keys", "Status": "Limited", "Detail": "No shared common keys detected across loaded sheets."}])


def render_executive_control_tower(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Executive Control Tower")
    on_time = infer_on_time(df, mapping)
    ordered = ordered_quantity(df, mapping)
    shipped = shipped_quantity(df, mapping)
    defects = num(df, field(mapping, "Defective Units")).fillna(0)
    total_units = num(df, field(mapping, "Total Units")).fillna(0)
    revenue = safe_sum(df, field(mapping, "Revenue"))
    cost = safe_sum(df, field(mapping, "Cost"))
    kpis = {
        "Revenue": revenue,
        "SCM Cost": cost,
        "Gross Margin %": safe_div(revenue - cost, revenue) * 100,
        "OTIF %": safe_div(((on_time) & (shipped >= ordered)).sum(), len(df)) * 100,
        "Fill Rate %": safe_div(shipped.sum(), ordered.sum()) * 100,
        "Perfect Order %": safe_div(((on_time) & (shipped >= ordered) & (defects <= 0)).sum(), len(df)) * 100,
        "Backorder Rate %": safe_div(num(df, field(mapping, "Backorder Quantity")).sum(), ordered.sum()) * 100,
        "Supplier Defect %": safe_div(defects.sum(), total_units.sum()) * 100,
    }
    show_kpis(kpis, columns=4)
    c1, c2 = st.columns(2)
    with c1:
        show_fig(grouped_bar(df, field(mapping, "Region"), field(mapping, "Revenue"), "Revenue by Region") if has_cols(df, field(mapping, "Region"), field(mapping, "Revenue")) else empty_figure(), "exec_region_revenue")
    with c2:
        show_fig(grouped_bar(df, field(mapping, "Category"), field(mapping, "Cost"), "Cost by Category") if has_cols(df, field(mapping, "Category"), field(mapping, "Cost")) else empty_figure(), "exec_category_cost")


def render_forecast_accuracy(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Forecast Accuracy")
    product = field(mapping, "Product") or field(mapping, "SKU")
    metrics = forecast_metrics(df, mapping, product)
    if metrics.empty:
        st.info("Map Demand or Sales plus Forecast to calculate MAPE, WAPE, bias, and tracking signal.")
        return
    overall = forecast_metrics(df, mapping)
    show_kpis({
        "MAPE %": float(overall["MAPE %"].iloc[0]),
        "WAPE %": float(overall["WAPE %"].iloc[0]),
        "Bias %": float(overall["Bias %"].iloc[0]),
        "Actual": float(overall["actual"].iloc[0]),
        "Forecast": float(overall["forecast"].iloc[0]),
    }, columns=5)
    c1, c2 = st.columns(2)
    with c1:
        show_fig(px.bar(metrics.sort_values("WAPE %", ascending=False).head(20), x=product, y="WAPE %", title="WAPE by Item"), "wape_item")
    with c2:
        show_fig(px.bar(metrics.sort_values("Bias %").head(20), x=product, y="Bias %", title="Forecast Bias by Item"), "bias_item")
    st.dataframe(metrics, width="stretch")


def render_inventory_risk(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Inventory Risk, ABC/XYZ, Safety Stock & Reorder Points")
    c1, c2, c3 = st.columns(3)
    service = c1.slider("Service level", 0.80, 0.99, 0.95, 0.01)
    z_lookup = {0.80: 0.84, 0.85: 1.04, 0.90: 1.28, 0.95: 1.65, 0.98: 2.05, 0.99: 2.33}
    z = z_lookup.get(round(service, 2), 1.65)
    demand_uplift = c2.slider("Demand uplift %", -50, 100, 0)
    lead_factor = c3.slider("Lead-time factor", 0.5, 3.0, 1.0, 0.1)
    risk = inventory_risk_table(df, mapping, z, demand_uplift, lead_factor)
    segments = abc_xyz(df, mapping)
    if risk.empty:
        st.info("Map SKU/Product, Demand/Sales, and Inventory for inventory risk.")
    else:
        show_kpis({
            "Stockout Risk Items": int(risk["stockout_risk"].sum()),
            "Excess Value": float(risk["excess_value"].sum()),
            "Avg Days Until Stockout": float(risk["days_until_stockout"].replace([np.inf, -np.inf], np.nan).mean()),
            "Total Safety Stock": float(risk["safety_stock"].sum()),
        }, columns=4)
        st.dataframe(risk.head(100), width="stretch")
    if not segments.empty:
        c4, c5 = st.columns(2)
        with c4:
            show_fig(px.scatter(segments, x="value", y="cv", color="ABC/XYZ", hover_name=segments.columns[0], title="ABC/XYZ Segmentation"), "abc_xyz_scatter")
        with c5:
            matrix = segments.pivot_table(index="ABC", columns="XYZ", values=segments.columns[0], aggfunc="count", fill_value=0)
            show_fig(px.imshow(matrix, text_auto=True, aspect="auto", title="ABC/XYZ Matrix"), "abc_xyz_matrix")


def render_po_aging(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("PO Aging & Open Commitments")
    po = field(mapping, "PO Number") or field(mapping, "Order ID")
    supplier = field(mapping, "Supplier")
    due = field(mapping, "Due Date") or field(mapping, "Promised Delivery Date")
    cost = field(mapping, "Procurement Cost") or field(mapping, "Cost")
    status = field(mapping, "PO Status") or field(mapping, "Order Status")
    if not has_cols(df, due, supplier):
        st.info("Map Supplier plus Due Date or Promised Delivery Date for PO aging.")
        return
    tmp = df.copy()
    tmp["_due"] = dates(tmp, due)
    tmp["_age_days"] = (pd.Timestamp.today().normalize() - tmp["_due"]).dt.days
    tmp["_open_value"] = num(tmp, cost).fillna(0) if cost and cost in tmp.columns else 0
    if status and status in tmp.columns:
        tmp = tmp[~tmp[status].astype(str).str.lower().isin(["closed", "complete", "completed", "received"])]
    tmp["Aging Bucket"] = pd.cut(tmp["_age_days"], bins=[-99999, 0, 7, 30, 60, 99999], labels=["Not due", "1-7", "8-30", "31-60", "60+"])
    show_kpis({"Open POs": int(tmp[po].nunique()) if po and po in tmp.columns else len(tmp), "Late POs": int((tmp["_age_days"] > 0).sum()), "Open Value": float(tmp["_open_value"].sum())}, columns=3)
    show_fig(px.bar(tmp.groupby("Aging Bucket", observed=False)["_open_value"].sum().reset_index(), x="Aging Bucket", y="_open_value", title="Open Commitment Aging"), "po_aging")
    st.dataframe(tmp[[c for c in [po, supplier, due, status, cost, "_age_days", "Aging Bucket"] if c and c in tmp.columns]].head(200), width="stretch")


def render_supplier_scorecard(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Supplier Scorecard")
    supplier = field(mapping, "Supplier")
    if not supplier or supplier not in df.columns:
        st.info("Map Supplier to build scorecards.")
        return
    tmp = df.copy()
    tmp["_on_time"] = infer_on_time(tmp, mapping).astype(float)
    tmp["_lead"] = num(tmp, field(mapping, "Lead Time"))
    tmp["_defect_rate"] = safe_div(num(tmp, field(mapping, "Defective Units")).sum(), num(tmp, field(mapping, "Total Units")).sum()) * 100
    tmp["_cost"] = num(tmp, field(mapping, "Procurement Cost") or field(mapping, "Cost"))
    score = tmp.groupby(supplier).agg(on_time=("_on_time", "mean"), lead=("_lead", "mean"), cost=("_cost", "sum")).reset_index().fillna(0)
    score["On-time %"] = score["on_time"] * 100
    score["Lead Score"] = 100 - score["lead"].rank(pct=True) * 100
    score["Cost Score"] = 100 - score["cost"].rank(pct=True) * 100
    score["Supplier Score"] = score[["On-time %", "Lead Score", "Cost Score"]].mean(axis=1)
    show_fig(px.imshow(score.set_index(supplier)[["On-time %", "Lead Score", "Cost Score", "Supplier Score"]].T, text_auto=True, aspect="auto", title="Supplier Scorecard Heatmap"), "supplier_scorecard_advanced")
    st.dataframe(score.sort_values("Supplier Score", ascending=False), width="stretch")


def render_carrier_lane(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Carrier / Lane Performance")
    carrier = field(mapping, "Carrier")
    route = field(mapping, "Route") or field(mapping, "Destination")
    cost = field(mapping, "Shipment Cost") or field(mapping, "Logistics Cost")
    weight = field(mapping, "Weight")
    distance = field(mapping, "Distance")
    if not has_cols(df, carrier, route):
        st.info("Map Carrier and Route/Destination for lane scorecards.")
        return
    tmp = df.copy()
    tmp["_on_time"] = infer_on_time(tmp, mapping).astype(float)
    tmp["_cost"] = num(tmp, cost).fillna(0) if cost and cost in tmp.columns else 0
    tmp["_weight"] = num(tmp, weight).replace(0, np.nan) if weight and weight in tmp.columns else np.nan
    tmp["_distance"] = num(tmp, distance).replace(0, np.nan) if distance and distance in tmp.columns else np.nan
    lane = tmp.groupby([carrier, route]).agg(shipments=(carrier, "count"), on_time=("_on_time", "mean"), cost=("_cost", "sum"), weight=("_weight", "sum"), distance=("_distance", "sum")).reset_index()
    lane["On-time %"] = lane["on_time"] * 100
    lane["Cost / kg"] = lane["cost"] / lane["weight"].replace(0, np.nan)
    lane["Cost / mile"] = lane["cost"] / lane["distance"].replace(0, np.nan)
    c1, c2 = st.columns(2)
    with c1:
        show_fig(px.scatter(lane, x="Cost / kg", y="On-time %", size="shipments", color=carrier, hover_name=route, title="Carrier / Lane Cost vs Service"), "carrier_lane_scatter")
    with c2:
        show_fig(px.bar(lane.sort_values("cost", ascending=False).head(20), x=route, y="cost", color=carrier, title="Freight Cost by Lane"), "lane_cost")
    st.dataframe(lane.fillna(0), width="stretch")


def render_warehouse_productivity(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Warehouse Productivity")
    warehouse = field(mapping, "Warehouse")
    picks = field(mapping, "Picks")
    accurate = field(mapping, "Accurate Picks")
    start = field(mapping, "Start Time")
    end = field(mapping, "End Time")
    if not warehouse or warehouse not in df.columns:
        st.info("Map Warehouse for productivity analysis.")
        return
    tmp = df.copy()
    tmp["_picks"] = num(tmp, picks).fillna(0) if picks and picks in tmp.columns else 0
    tmp["_accurate"] = num(tmp, accurate).fillna(0) if accurate and accurate in tmp.columns else 0
    if start and end and has_cols(tmp, start, end):
        tmp["_hours"] = (dates(tmp, end) - dates(tmp, start)).dt.total_seconds() / 3600
    else:
        tmp["_hours"] = 1
    prod = tmp.groupby(warehouse).agg(picks=("_picks", "sum"), accurate=("_accurate", "sum"), hours=("_hours", "sum")).reset_index()
    prod["Picks / Hour"] = prod["picks"] / prod["hours"].replace(0, np.nan)
    prod["Pick Accuracy %"] = prod["accurate"] / prod["picks"].replace(0, np.nan) * 100
    show_fig(px.bar(prod, x=warehouse, y=["Picks / Hour", "Pick Accuracy %"], barmode="group", title="Warehouse Productivity"), "warehouse_productivity_adv")
    st.dataframe(prod.fillna(0), width="stretch")


def render_production_performance(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Production Performance, OEE, Yield & Schedule Adherence")
    product = field(mapping, "Product")
    output = field(mapping, "Production Quantity")
    good = field(mapping, "Good Quantity") or output
    scrap = field(mapping, "Scrap Quantity") or field(mapping, "Defective Units")
    planned_time = field(mapping, "Planned Time") or field(mapping, "Capacity")
    run_time = field(mapping, "Run Time")
    scheduled = field(mapping, "Schedule Quantity") or field(mapping, "Planned Production")
    if not has_cols(df, product, output):
        st.info("Map Product and Production Quantity for production performance.")
        return
    tmp = pd.DataFrame({
        "Product": cat(df, product),
        "Output": num(df, output).fillna(0),
        "Good": num(df, good).fillna(0),
        "Scrap": num(df, scrap).fillna(0) if scrap and scrap in df.columns else 0,
        "Planned Time": num(df, planned_time).fillna(0) if planned_time and planned_time in df.columns else 0,
        "Run Time": num(df, run_time).fillna(0) if run_time and run_time in df.columns else num(df, planned_time).fillna(0),
        "Scheduled": num(df, scheduled).fillna(0) if scheduled and scheduled in df.columns else 0,
    })
    perf = tmp.groupby("Product").sum(numeric_only=True).reset_index()
    perf["Availability %"] = perf["Run Time"] / perf["Planned Time"].replace(0, np.nan) * 100
    perf["Yield %"] = perf["Good"] / perf["Output"].replace(0, np.nan) * 100
    perf["Scrap Rate %"] = perf["Scrap"] / (perf["Output"] + perf["Scrap"]).replace(0, np.nan) * 100
    perf["Schedule Adherence %"] = perf["Output"] / perf["Scheduled"].replace(0, np.nan) * 100
    perf["OEE %"] = (perf["Availability %"].clip(0, 100) / 100) * (perf["Schedule Adherence %"].clip(0, 100) / 100) * (perf["Yield %"].clip(0, 100) / 100) * 100
    show_fig(px.bar(perf, x="Product", y=["OEE %", "Yield %", "Scrap Rate %"], barmode="group", title="OEE / Yield / Scrap"), "prod_oee")
    st.dataframe(perf.fillna(0), width="stretch")


def render_finance_bridge(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Finance Margin Bridge, GMROI & Cash-to-Cash")
    revenue = safe_sum(df, field(mapping, "Revenue"))
    cost = safe_sum(df, field(mapping, "Cost"))
    freight = safe_sum(df, field(mapping, "Shipment Cost") or field(mapping, "Logistics Cost"))
    inv_value = safe_sum(df, field(mapping, "Inventory")) * (safe_mean(df, field(mapping, "Cost")) or 1)
    cogs = safe_sum(df, field(mapping, "COGS")) or cost
    turnover = safe_div(cogs, inv_value)
    dio = safe_div(365, turnover)
    dso = 30.0
    dpo = 30.0
    show_kpis({
        "Gross Margin": revenue - cost,
        "Margin After Freight": revenue - cost - freight,
        "GMROI": safe_div(revenue - cost, inv_value),
        "Inventory Working Capital": inv_value,
        "Cash-to-Cash Days": dio + dso - dpo,
    }, columns=5)
    bridge = pd.DataFrame({"Step": ["Revenue", "Product Cost", "Freight", "Margin After Freight"], "Value": [revenue, -cost, -freight, revenue - cost - freight]})
    show_fig(px.bar(bridge, x="Step", y="Value", title="Margin Bridge"), "finance_bridge")


def render_planning_lab(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Scenario / What-if Planning Lab")
    c1, c2, c3, c4 = st.columns(4)
    demand_uplift = c1.slider("Demand change %", -50, 100, 10, key="scenario_demand")
    lead_factor = c2.slider("Lead-time multiplier", 0.5, 3.0, 1.2, 0.1, key="scenario_lead")
    cost_uplift = c3.slider("Cost change %", -50, 100, 5, key="scenario_cost")
    service = c4.slider("Service Z", 0.8, 2.4, 1.65, 0.05, key="scenario_service")
    base = inventory_risk_table(df, mapping)
    scenario = inventory_risk_table(df, mapping, service, demand_uplift, lead_factor)
    revenue = safe_sum(df, field(mapping, "Revenue"))
    cost = safe_sum(df, field(mapping, "Cost"))
    comparison = pd.DataFrame([
        {"Scenario": "Base", "Risk Items": int(base["stockout_risk"].sum()) if not base.empty else 0, "Excess Value": float(base["excess_value"].sum()) if not base.empty else 0, "Margin": revenue - cost},
        {"Scenario": "What-if", "Risk Items": int(scenario["stockout_risk"].sum()) if not scenario.empty else 0, "Excess Value": float(scenario["excess_value"].sum()) if not scenario.empty else 0, "Margin": revenue - cost * (1 + cost_uplift / 100)},
    ])
    st.dataframe(comparison, width="stretch")
    show_fig(px.bar(comparison, x="Scenario", y=["Risk Items", "Excess Value", "Margin"], barmode="group", title="Scenario Comparison"), "scenario_compare")


def generated_forecast_table(df: pd.DataFrame, mapping: dict, method: str = "Moving average", periods: int = 6, window: int = 3, alpha: float = 0.3) -> pd.DataFrame:
    date_col = field(mapping, "Date")
    actual_col = field(mapping, "Demand") or field(mapping, "Sales")
    sku_col = field(mapping, "SKU") or field(mapping, "Product")
    if not has_cols(df, date_col, actual_col):
        return pd.DataFrame()
    tmp = pd.DataFrame({
        "Date": dates(df, date_col),
        "Actual": num(df, actual_col),
        "Item": cat(df, sku_col) if sku_col and sku_col in df.columns else "All Items",
    }).dropna(subset=["Date", "Actual"])
    if tmp.empty:
        return pd.DataFrame()
    tmp["Period"] = tmp["Date"].dt.to_period("M").dt.to_timestamp()
    history = tmp.groupby(["Item", "Period"], as_index=False)["Actual"].sum().sort_values(["Item", "Period"])
    rows = []
    for item, group in history.groupby("Item"):
        values = list(group["Actual"].astype(float))
        periods_index = list(group["Period"])
        last_period = periods_index[-1]
        future_periods = pd.date_range(last_period + pd.offsets.MonthBegin(1), periods=periods, freq="MS")
        for future in future_periods:
            if method == "Seasonal naive" and len(values) >= 12:
                forecast = values[-12]
            elif method == "Exponential smoothing":
                level = values[0]
                for value in values[1:]:
                    level = alpha * value + (1 - alpha) * level
                forecast = level
            else:
                forecast = np.mean(values[-max(1, window):])
            values.append(float(forecast))
            rows.append({"Item": item, "Period": future, "Forecast": float(forecast), "Method": method})
    return pd.DataFrame(rows)


def inventory_aging_table(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    item = field(mapping, "SKU") or field(mapping, "Product")
    lot = field(mapping, "Lot") or field(mapping, "Batch")
    age_date = field(mapping, "Last Movement Date") or field(mapping, "Issue Date") or field(mapping, "Receipt Date") or field(mapping, "Received Date") or field(mapping, "Date")
    qty = field(mapping, "Lot Quantity") or field(mapping, "Inventory")
    cost = field(mapping, "Cost") or field(mapping, "Unit Price") or field(mapping, "Standard Cost")
    if not has_cols(df, item, age_date, qty):
        return pd.DataFrame()
    tmp = pd.DataFrame({
        "Item": cat(df, item),
        "Lot/Batch": cat(df, lot) if lot and lot in df.columns else "Unspecified",
        "Age Date": dates(df, age_date),
        "Quantity": num(df, qty).fillna(0),
        "Unit Cost": num(df, cost).fillna(1) if cost and cost in df.columns else 1,
    }).dropna(subset=["Age Date"])
    tmp["Age Days"] = (pd.Timestamp.today().normalize() - tmp["Age Date"]).dt.days.clip(lower=0)
    tmp["Inventory Value"] = tmp["Quantity"] * tmp["Unit Cost"]
    tmp["Aging Bucket"] = pd.cut(tmp["Age Days"], bins=[-1, 30, 60, 90, 180, 99999], labels=["0-30", "31-60", "61-90", "91-180", "180+"])
    tmp["Obsolete Candidate"] = tmp["Age Days"] >= 180
    return tmp.sort_values("Age Days", ascending=False)


def contract_analytics_table(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    supplier = field(mapping, "Supplier")
    sku = field(mapping, "SKU") or field(mapping, "Product")
    actual = field(mapping, "Actual Price") or field(mapping, "Unit Price") or field(mapping, "Cost")
    benchmark = field(mapping, "Contract Price") or field(mapping, "Standard Price") or field(mapping, "Standard Cost")
    qty = field(mapping, "Order Quantity") or field(mapping, "Total Units") or field(mapping, "Demand")
    if not has_cols(df, supplier, sku, actual, benchmark):
        return pd.DataFrame()
    tmp = pd.DataFrame({
        "Supplier": cat(df, supplier),
        "Item": cat(df, sku),
        "Actual Price": num(df, actual),
        "Contract/Standard Price": num(df, benchmark),
        "Quantity": num(df, qty).fillna(1) if qty and qty in df.columns else 1,
    }).dropna(subset=["Actual Price", "Contract/Standard Price"])
    tmp["PPV"] = (tmp["Actual Price"] - tmp["Contract/Standard Price"]) * tmp["Quantity"]
    tmp["Off-contract Spend"] = np.where(tmp["Actual Price"] > tmp["Contract/Standard Price"], tmp["PPV"], 0)
    tmp["Compliance %"] = np.where(tmp["Actual Price"] <= tmp["Contract/Standard Price"], 100, 0)
    return tmp.groupby(["Supplier", "Item"], as_index=False).agg({"Quantity": "sum", "PPV": "sum", "Off-contract Spend": "sum", "Compliance %": "mean"})


def landed_cost_table(df: pd.DataFrame, mapping: dict, method: str = "Units") -> pd.DataFrame:
    sku = field(mapping, "SKU") or field(mapping, "Product")
    customer = field(mapping, "Customer")
    order = field(mapping, "Order ID") or field(mapping, "Shipment ID")
    qty = field(mapping, "Order Quantity") or field(mapping, "Shipped Quantity") or field(mapping, "Demand")
    revenue = field(mapping, "Revenue")
    product_cost = field(mapping, "Cost") or field(mapping, "COGS") or field(mapping, "Unit Price")
    freight = field(mapping, "Shipment Cost") or field(mapping, "Logistics Cost")
    weight = field(mapping, "Weight")
    volume = field(mapping, "Volume")
    if not has_cols(df, sku):
        return pd.DataFrame()
    tmp = pd.DataFrame({
        "Item": cat(df, sku),
        "Customer": cat(df, customer) if customer and customer in df.columns else "Unspecified",
        "Order": cat(df, order) if order and order in df.columns else df.index.astype(str),
        "Units": num(df, qty).fillna(1) if qty and qty in df.columns else 1,
        "Revenue": num(df, revenue).fillna(0) if revenue and revenue in df.columns else 0,
        "Product Cost": num(df, product_cost).fillna(0) if product_cost and product_cost in df.columns else 0,
        "Freight Pool": num(df, freight).fillna(0) if freight and freight in df.columns else 0,
        "Weight": num(df, weight).fillna(0) if weight and weight in df.columns else 0,
        "Volume": num(df, volume).fillna(0) if volume and volume in df.columns else 0,
    })
    basis_map = {"Units": "Units", "Weight": "Weight", "Volume": "Volume", "Revenue": "Revenue"}
    basis = basis_map.get(method, "Units")
    denom = tmp[basis].sum()
    tmp["Allocated Freight"] = tmp["Freight Pool"].sum() * tmp[basis] / denom if denom else 0
    tmp["Landed Cost"] = tmp["Product Cost"] + tmp["Allocated Freight"]
    tmp["Landed Margin"] = tmp["Revenue"] - tmp["Landed Cost"]
    return tmp


def warehouse_process_table(df: pd.DataFrame, mapping: dict, sla_hours: float = 24.0) -> pd.DataFrame:
    warehouse = field(mapping, "Warehouse")
    dock = field(mapping, "Dock Time") or field(mapping, "Received Date")
    putaway = field(mapping, "Putaway Time")
    start = field(mapping, "Start Time")
    end = field(mapping, "End Time")
    worker = field(mapping, "Worker") or field(mapping, "Team")
    picks = field(mapping, "Picks")
    if not has_cols(df, warehouse):
        return pd.DataFrame()
    tmp = pd.DataFrame({
        "Warehouse": cat(df, warehouse),
        "Worker/Team": cat(df, worker) if worker and worker in df.columns else "Unspecified",
        "Dock": dates(df, dock) if dock and dock in df.columns else pd.NaT,
        "Putaway": dates(df, putaway) if putaway and putaway in df.columns else pd.NaT,
        "Pick Start": dates(df, start) if start and start in df.columns else pd.NaT,
        "Pick End": dates(df, end) if end and end in df.columns else pd.NaT,
        "Picks": num(df, picks).fillna(1) if picks and picks in df.columns else 1,
    })
    tmp["Dock-to-Stock Hours"] = (tmp["Putaway"] - tmp["Dock"]).dt.total_seconds() / 3600
    tmp["Pick-Pack-Ship Hours"] = (tmp["Pick End"] - tmp["Pick Start"]).dt.total_seconds() / 3600
    tmp["Picks / Hour"] = tmp["Picks"] / tmp["Pick-Pack-Ship Hours"].replace(0, np.nan)
    tmp["SLA Breach"] = tmp["Dock-to-Stock Hours"] > sla_hours
    return tmp.fillna(0)


def mrp_lite_table(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    parent = field(mapping, "Product")
    component = field(mapping, "SKU")
    demand = field(mapping, "Demand") or field(mapping, "Sales") or field(mapping, "Order Quantity")
    inventory = field(mapping, "Inventory")
    open_supply = field(mapping, "Open Supply") or field(mapping, "Open PO Quantity")
    lead = field(mapping, "Lead Time")
    if not has_cols(df, component, demand):
        return pd.DataFrame()
    tmp = pd.DataFrame({
        "Parent": cat(df, parent) if parent and parent in df.columns else cat(df, component),
        "Component": cat(df, component),
        "Required": num(df, demand).fillna(0),
        "Available": num(df, inventory).fillna(0) if inventory and inventory in df.columns else 0,
        "Open Supply": num(df, open_supply).fillna(0) if open_supply and open_supply in df.columns else 0,
        "Lead Time": num(df, lead).fillna(0) if lead and lead in df.columns else 0,
    })
    plan = tmp.groupby(["Parent", "Component"], as_index=False).agg({"Required": "sum", "Available": "sum", "Open Supply": "sum", "Lead Time": "mean"})
    plan["Net Requirement"] = (plan["Required"] - plan["Available"] - plan["Open Supply"]).clip(lower=0)
    plan["Shortage Risk"] = plan["Net Requirement"] > 0
    return plan.sort_values(["Shortage Risk", "Net Requirement"], ascending=[False, False])


def mapping_confidence_table(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    rows = []
    for scm_field, col in mapping.items():
        if not col or col not in df.columns:
            rows.append({"SCM Field": scm_field, "Mapped Column": "", "Confidence": "Unavailable", "Reason": "No column selected"})
            continue
        clean_field = scm_field.lower().replace(" ", "_")
        clean_col = str(col).lower()
        confidence = "High" if clean_field in clean_col or clean_col in clean_field else "Medium"
        rows.append({"SCM Field": scm_field, "Mapped Column": col, "Confidence": confidence, "Reason": "Auto/manual mapping can be reviewed in Column Mapping"})
    return pd.DataFrame(rows)


def business_calendar_table(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    date_col = field(mapping, "Date")
    if not date_col or date_col not in df.columns:
        return pd.DataFrame()
    d = dates(df, date_col).dropna()
    if d.empty:
        return pd.DataFrame()
    calendar = pd.DataFrame({"Date": pd.date_range(d.min(), d.max(), freq="D")})
    calendar["Is Weekend"] = calendar["Date"].dt.weekday >= 5
    calendar["Fiscal Period"] = calendar["Date"].dt.to_period("M").astype(str)
    calendar["Working Day"] = ~calendar["Is Weekend"]
    return calendar


def failed_row_quarantine(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    mask = pd.Series(False, index=df.index)
    reasons = pd.Series("", index=df.index, dtype="object")
    for label in ["Demand", "Sales", "Inventory", "Cost", "Shipment Cost", "Order Quantity"]:
        col = field(mapping, label)
        if col and col in df.columns:
            invalid = df[col].notna() & pd.to_numeric(df[col], errors="coerce").isna()
            neg = pd.to_numeric(df[col], errors="coerce") < 0
            flag = invalid | neg
            mask |= flag.fillna(False)
            reasons = reasons.where(~flag.fillna(False), reasons + f"{label}; ")
    for label in ["Date", "Order Date", "Delivery Date", "Received Date"]:
        col = field(mapping, label)
        if col and col in df.columns:
            invalid = df[col].notna() & pd.to_datetime(df[col], errors="coerce").isna()
            mask |= invalid.fillna(False)
            reasons = reasons.where(~invalid.fillna(False), reasons + f"{label}; ")
    out = df[mask].copy()
    if not out.empty:
        out.insert(0, "Quarantine Reason", reasons[mask].str.strip("; "))
    return out


def full_dashboard_workbook_bytes(df: pd.DataFrame, mapping: dict, kpis: dict, quality: dict) -> bytes:
    workbook = BytesIO()
    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Filtered_Data", index=False)
        pd.DataFrame([quality]).to_excel(writer, sheet_name="Data_Quality", index=False)
        pd.DataFrame([{"Field": k, "Column": v} for k, v in mapping.items()]).to_excel(writer, sheet_name="Column_Mapping", index=False)
        pd.DataFrame([{"Metric": k, "Definition": v} for k, v in METRIC_GLOSSARY.items()]).to_excel(writer, sheet_name="Metric_Glossary", index=False)
        validation_report(df, mapping).to_excel(writer, sheet_name="Validation_Report", index=False)
        failed_row_quarantine(df, mapping).to_excel(writer, sheet_name="Failed_Rows", index=False)
        for sheet, table in {
            "Forecast": generated_forecast_table(df, mapping),
            "Inventory_Aging": inventory_aging_table(df, mapping),
            "Contract_Analytics": contract_analytics_table(df, mapping),
            "Landed_Cost": landed_cost_table(df, mapping),
            "MRP_Lite": mrp_lite_table(df, mapping),
        }.items():
            table.to_excel(writer, sheet_name=sheet[:31], index=False)
        for module, metrics in kpis.items():
            pd.DataFrame([{"Metric": k, "Value": v} for k, v in metrics.items()]).to_excel(writer, sheet_name=module[:31], index=False)
    return workbook.getvalue()


def chart_bundle_zip_bytes(df: pd.DataFrame, mapping: dict) -> bytes:
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, chart_type, x, y, color in [
            ("demand_by_product", "bar", field(mapping, "Product"), field(mapping, "Demand"), None),
            ("cost_over_time", "line", field(mapping, "Date"), field(mapping, "Cost"), None),
            ("inventory_pareto", "pareto", field(mapping, "SKU") or field(mapping, "Product"), field(mapping, "Inventory"), None),
            ("supplier_ppv", "bar", "Supplier", "PPV", None),
        ]:
            source = df
            if name == "supplier_ppv":
                source = contract_analytics_table(df, mapping)
            if x and x in source.columns:
                fig = make_chart(source, chart_type, x, y if y in source.columns else None, color, "sum", name.replace("_", " ").title())
                archive.writestr(f"{name}.html", fig.to_html(include_plotlyjs=True))
                try:
                    archive.writestr(f"{name}.png", chart_png_bytes(source, chart_type, x, y if y in source.columns else None, color, "sum", name))
                except Exception:
                    pass
    return zip_buffer.getvalue()


def powerpoint_summary_bytes(kpis: dict, quality: dict) -> bytes:
    """Create a tiny offline PPTX without external services or extra engines."""
    rows = []
    rows.append(("SCM Analytics Studio", f"Rows: {quality.get('rows', 0):,} | Columns: {quality.get('columns', 0):,}"))
    for module, metrics in list(kpis.items())[:5]:
        text = "\n".join(f"{key}: {value}" for key, value in list(metrics.items())[:6])
        rows.append((module, text or "No KPI available"))

    def slide_xml(title: str, body: str) -> str:
        safe_title = str(title).replace("&", "&amp;").replace("<", "&lt;")
        safe_body = str(body).replace("&", "&amp;").replace("<", "&lt;").replace("\n", "&#10;")
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr><p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr sz="3600" b="1"/><a:t>{safe_title}</a:t></a:r></a:p></p:txBody></p:sp><p:sp><p:nvSpPr><p:cNvPr id="3" name="Body"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="900000" y="1800000"/><a:ext cx="7600000" cy="4200000"/></a:xfrm></p:spPr><p:txBody><a:bodyPr wrap="square"/><a:lstStyle/><a:p><a:r><a:rPr sz="2000"/><a:t>{safe_body}</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"""

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>""" + "".join(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, len(rows)+1)) + "</Types>")
        z.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>""")
        rels = "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>' for i in range(1, len(rows)+1))
        z.writestr("ppt/_rels/presentation.xml.rels", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        sld_ids = "".join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1, len(rows)+1))
        z.writestr("ppt/presentation.xml", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldIdLst>{sld_ids}</p:sldIdLst><p:sldSz cx="9144000" cy="5143500" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>')
        for i, (title, body) in enumerate(rows, 1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide_xml(title, body))
    return buf.getvalue()


def render_forecast_generation(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Forecast Generation")
    c1, c2, c3, c4 = st.columns(4)
    method = c1.selectbox("Method", ["Moving average", "Seasonal naive", "Exponential smoothing"])
    periods = c2.number_input("Forecast periods", min_value=1, max_value=24, value=6)
    window = c3.number_input("Moving average window", min_value=1, max_value=12, value=3)
    alpha = c4.slider("Smoothing alpha", 0.05, 0.95, 0.30, 0.05)
    forecast = generated_forecast_table(df, mapping, method, int(periods), int(window), float(alpha))
    if forecast.empty:
        st.info("Map Date and Demand or Sales to generate an offline forecast.")
        return
    show_kpis({"Forecast Items": forecast["Item"].nunique(), "Forecast Periods": forecast["Period"].nunique(), "Total Forecast": float(forecast["Forecast"].sum())}, columns=3)
    show_fig(px.line(forecast, x="Period", y="Forecast", color="Item", title="Generated Forecast"), "generated_forecast")
    st.dataframe(forecast, width="stretch")


def render_inventory_aging(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Inventory Aging by Lot")
    aging = inventory_aging_table(df, mapping)
    if aging.empty:
        st.info("Map SKU/Product, receipt or last movement date, quantity, and optional lot/cost for aging.")
        return
    show_kpis({"Obsolete Value": float(aging.loc[aging["Obsolete Candidate"], "Inventory Value"].sum()), "Obsolete Lots": int(aging["Obsolete Candidate"].sum()), "Inventory Value": float(aging["Inventory Value"].sum())}, columns=3)
    bucket = aging.groupby("Aging Bucket", observed=False)["Inventory Value"].sum().reset_index()
    show_fig(px.bar(bucket, x="Aging Bucket", y="Inventory Value", title="Inventory Aging Value"), "inventory_aging")
    st.dataframe(aging.head(300), width="stretch")


def render_procurement_contracts(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Procurement Contract Analytics")
    table = contract_analytics_table(df, mapping)
    if table.empty:
        st.info("Map Supplier, SKU/Product, Actual Price, Contract or Standard Price, and quantity for PPV.")
        return
    show_kpis({"Total PPV": float(table["PPV"].sum()), "Off-contract Spend": float(table["Off-contract Spend"].sum()), "Avg Compliance %": float(table["Compliance %"].mean())}, columns=3)
    show_fig(px.bar(table.sort_values("PPV", ascending=False).head(20), x="Supplier", y="PPV", color="Item", title="Purchase Price Variance"), "contract_ppv")
    st.dataframe(table, width="stretch")


def render_landed_cost(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Landed Cost / Cost-to-Serve")
    method = st.selectbox("Freight allocation method", ["Units", "Weight", "Volume", "Revenue"])
    table = landed_cost_table(df, mapping, method)
    if table.empty:
        st.info("Map SKU/Product plus optional freight, cost, revenue, customer, weight, and volume.")
        return
    summary = table.groupby(["Item", "Customer"], as_index=False).agg({"Revenue": "sum", "Landed Cost": "sum", "Landed Margin": "sum", "Allocated Freight": "sum"})
    show_kpis({"Allocated Freight": float(table["Allocated Freight"].sum()), "Landed Margin": float(table["Landed Margin"].sum()), "Cost-to-Serve": float(table["Landed Cost"].sum())}, columns=3)
    show_fig(px.bar(summary.sort_values("Landed Margin").head(25), x="Item", y="Landed Margin", color="Customer", title="Landed Margin by Item / Customer"), "landed_margin")
    st.dataframe(summary, width="stretch")


def render_warehouse_process(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Warehouse Process Analytics")
    sla = st.slider("Dock-to-stock SLA hours", 1, 168, 24)
    table = warehouse_process_table(df, mapping, float(sla))
    if table.empty:
        st.info("Map Warehouse and process timestamps such as Dock Time, Putaway Time, Start Time, and End Time.")
        return
    show_kpis({"Avg Dock-to-Stock Hours": float(pd.to_numeric(table["Dock-to-Stock Hours"], errors="coerce").mean()), "SLA Breaches": int(table["SLA Breach"].sum()), "Avg Picks / Hour": float(pd.to_numeric(table["Picks / Hour"], errors="coerce").replace([np.inf, -np.inf], np.nan).mean())}, columns=3)
    agg = table.groupby("Warehouse", as_index=False).agg({"Dock-to-Stock Hours": "mean", "Pick-Pack-Ship Hours": "mean", "SLA Breach": "sum"})
    show_fig(px.bar(agg, x="Warehouse", y=["Dock-to-Stock Hours", "Pick-Pack-Ship Hours"], barmode="group", title="Warehouse Milestone Cycle Time"), "warehouse_process")
    st.dataframe(table, width="stretch")


def render_mrp_lite(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Production Planning / MRP-lite")
    plan = mrp_lite_table(df, mapping)
    if plan.empty:
        st.info("Map SKU/Product, demand, inventory, and optional open supply/lead time for MRP-lite.")
        return
    show_kpis({"Shortage Components": int(plan["Shortage Risk"].sum()), "Net Requirements": float(plan["Net Requirement"].sum()), "Avg Lead Time": float(plan["Lead Time"].mean())}, columns=3)
    show_fig(px.bar(plan.head(30), x="Component", y="Net Requirement", color="Parent", title="Material Shortage Plan"), "mrp_shortage")
    st.dataframe(plan, width="stretch")


def render_settings_help(df: pd.DataFrame, mapping: dict, db_path: Path) -> None:
    st.subheader("Settings, Data Dictionary, Validation & Audit")
    st.markdown("#### Workflow Checklist")
    checklist = pd.DataFrame([
        {"Step": "Load data", "Status": "Complete" if not df.empty else "Needs attention"},
        {"Step": "Map columns", "Status": "Complete" if any(mapping.values()) else "Needs attention"},
        {"Step": "Review validation", "Status": "Complete"},
        {"Step": "Export or save", "Status": "Optional"},
    ])
    st.dataframe(checklist, width="stretch")
    st.markdown("#### Mapping Confidence")
    st.dataframe(mapping_confidence_table(df, mapping), width="stretch")
    st.markdown("#### Metric Definitions")
    st.dataframe(pd.DataFrame([{"Metric": k, "Definition": v} for k, v in METRIC_GLOSSARY.items()]), width="stretch")
    st.download_button("Download metric glossary JSON", json.dumps(METRIC_GLOSSARY, indent=2).encode("utf-8"), "metric_glossary.json", "application/json")
    st.markdown("#### Data Validation Report")
    report = validation_report(df, mapping)
    st.dataframe(report, width="stretch")
    st.download_button("Download validation report CSV", report.to_csv(index=False).encode("utf-8"), "data_quality_issue_report.csv", "text/csv")
    st.markdown("#### Business Calendar")
    calendar = business_calendar_table(df, mapping)
    if not calendar.empty:
        st.dataframe(calendar.head(366), width="stretch")
        st.download_button("Download local calendar CSV", calendar.to_csv(index=False).encode("utf-8"), "business_calendar.csv", "text/csv")
    st.markdown("#### SQLite Backup")
    if Path(db_path).exists():
        st.download_button("Download SQLite backup", Path(db_path).read_bytes(), "scm_analytics_studio.sqlite", "application/octet-stream")
    st.markdown("#### Audit Trail")
    audit = pd.DataFrame(list_audit_events(db_path))
    st.dataframe(audit, width="stretch")
    if not audit.empty:
        st.download_button("Download audit log CSV", audit.to_csv(index=False).encode("utf-8"), "audit_log.csv", "text/csv")
    st.markdown("#### User Feedback")
    feedback = pd.DataFrame(list_feedback(db_path))
    st.dataframe(feedback, width="stretch")
    if not feedback.empty:
        st.download_button("Download feedback CSV", feedback.to_csv(index=False).encode("utf-8"), "user_feedback.csv", "text/csv")
    st.markdown("#### Dashboard Templates")
    preset = st.selectbox("Role preset", ["Executive", "Inventory Planner", "Procurement Manager", "Logistics Manager", "Warehouse Manager", "Production Planner", "Finance Analyst"])
    template_name = st.text_input("Template name", value=f"{preset.lower().replace(' ', '_')}_template")
    if st.button("Save dashboard template", width="stretch"):
        save_dashboard_template(db_path, template_name, {"preset": preset, "mapping": mapping})
        st.success(f"Saved template: {template_name}")
    templates = pd.DataFrame(list_dashboard_templates(db_path))
    st.dataframe(templates, width="stretch")
    if not templates.empty:
        chosen = st.selectbox("Apply saved template preview", templates["name"].tolist())
        if st.button("Apply template to this session", width="stretch"):
            st.session_state["active_template"] = chosen
            st.success(f"Template selected for this session: {chosen}")


def render_extra_exports(df: pd.DataFrame, mapping: dict, kpis: dict, quality: dict) -> None:
    st.markdown("#### Extended Exports")
    st.download_button("Download full dashboard workbook", full_dashboard_workbook_bytes(df, mapping, kpis, quality), "scm_dashboard_workbook.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Download chart bundle ZIP", chart_bundle_zip_bytes(df, mapping), "chart_bundle.zip", "application/zip")
    st.download_button("Download PowerPoint summary", powerpoint_summary_bytes(kpis, quality), "scm_summary.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
    st.download_button("Download failed-row quarantine CSV", failed_row_quarantine(df, mapping).to_csv(index=False).encode("utf-8"), "failed_row_quarantine.csv", "text/csv")
    st.download_button("Download mapping template JSON", json.dumps(mapping, indent=2).encode("utf-8"), "mapping_template.json", "application/json")
