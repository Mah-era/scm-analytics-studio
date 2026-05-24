"""Reusable SCM KPI calculations."""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd


def safe_div(numerator, denominator, default=0.0):
    try:
        if denominator is None or float(denominator) == 0:
            return default
        return float(numerator) / float(denominator)
    except Exception:
        return default


def pct(value) -> float:
    return float(value) * 100


def col(df: pd.DataFrame, name: Optional[str]) -> pd.Series:
    if name and name in df.columns:
        return df[name]
    return pd.Series(dtype="float64")


def num_col(df: pd.DataFrame, name: Optional[str]) -> pd.Series:
    s = col(df, name)
    return pd.to_numeric(s, errors="coerce") if not s.empty else pd.Series(dtype="float64")


def date_col(df: pd.DataFrame, name: Optional[str]) -> pd.Series:
    s = col(df, name)
    return pd.to_datetime(s, errors="coerce") if not s.empty else pd.Series(dtype="datetime64[ns]")


def safe_sum(df: pd.DataFrame, name: Optional[str]) -> float:
    s = num_col(df, name)
    return float(s.fillna(0).sum()) if not s.empty else 0.0


def safe_mean(df: pd.DataFrame, name: Optional[str]) -> float:
    s = num_col(df, name)
    return float(s.dropna().mean()) if not s.empty and s.dropna().shape[0] else 0.0


def top_category(df: pd.DataFrame, category_col: Optional[str], value_col: Optional[str], ascending=False) -> str:
    if not category_col or not value_col or category_col not in df.columns or value_col not in df.columns:
        return "N/A"
    tmp = df[[category_col, value_col]].copy()
    tmp[value_col] = pd.to_numeric(tmp[value_col], errors="coerce")
    tmp = tmp.dropna(subset=[value_col])
    if tmp.empty:
        return "N/A"
    tmp = tmp.groupby(category_col, dropna=False)[value_col].sum().sort_values(ascending=ascending)
    if tmp.empty:
        return "N/A"
    return str(tmp.index[0])


def inventory_turnover(cogs: float, average_inventory: float) -> float:
    return safe_div(cogs, average_inventory)


def days_inventory_outstanding(turnover: float) -> float:
    return safe_div(365, turnover)


def fill_rate(fulfilled_orders: float, total_orders: float) -> float:
    return safe_div(fulfilled_orders, total_orders)


def stockout_rate(stockout_events: float, total_demand_events: float) -> float:
    return safe_div(stockout_events, total_demand_events)


def on_time_delivery_rate(on_time_deliveries: float, total_deliveries: float) -> float:
    return safe_div(on_time_deliveries, total_deliveries)


def supplier_defect_rate(defective_units: float, total_units_supplied: float) -> float:
    return safe_div(defective_units, total_units_supplied)


def forecast_accuracy(actual: pd.Series, forecast: pd.Series) -> float:
    actual = pd.to_numeric(actual, errors="coerce")
    forecast = pd.to_numeric(forecast, errors="coerce")
    valid = actual.replace(0, np.nan).notna() & forecast.notna()
    if valid.sum() == 0:
        return 0.0
    acc = 1 - (actual[valid] - forecast[valid]).abs() / actual[valid].replace(0, np.nan)
    return float(acc.clip(lower=0, upper=1).mean())


def capacity_utilization(actual_output: float, max_capacity: float) -> float:
    return safe_div(actual_output, max_capacity)


def gross_margin(revenue: float, cost: float) -> float:
    return float(revenue) - float(cost)


def gross_margin_pct(revenue: float, cost: float) -> float:
    return safe_div(gross_margin(revenue, cost), revenue)
