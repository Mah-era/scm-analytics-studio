"""Local tool registry for SCM Analytics Studio workflows.

Tools are plain Python callables that operate on the current dataframe and
column mapping. They are intentionally local-first so the app remains useful
without network access or external services.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict

import pandas as pd

from .advanced_features import (
    abc_xyz,
    business_calendar_table,
    contract_analytics_table,
    failed_row_quarantine,
    generated_forecast_table,
    inventory_aging_table,
    inventory_risk_table,
    landed_cost_table,
    mrp_lite_table,
    validation_report,
    warehouse_process_table,
)
from .data_cleaner import data_quality_summary
from .reporting import get_all_kpis


ToolResult = Dict[str, Any]
ToolCallable = Callable[[pd.DataFrame, dict, dict | None], ToolResult]


@dataclass(frozen=True)
class LocalTool:
    name: str
    category: str
    description: str
    run: ToolCallable


def _table_result(title: str, table: pd.DataFrame, summary: dict | None = None) -> ToolResult:
    return {
        "title": title,
        "summary": summary or {},
        "table": table,
        "row_count": int(len(table)) if isinstance(table, pd.DataFrame) else 0,
    }


def _data_quality(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    quality = data_quality_summary(df)
    validation = validation_report(df, mapping)
    return _table_result("Data quality and validation", validation, quality)


def _kpi_snapshot(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    rows = []
    for module, metrics in get_all_kpis(df, mapping).items():
        for metric, value in metrics.items():
            rows.append({"Module": module, "Metric": metric, "Value": value})
    return _table_result("KPI snapshot", pd.DataFrame(rows), {"modules": len(set(row["Module"] for row in rows)) if rows else 0})


def _forecast(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    params = params or {}
    table = generated_forecast_table(
        df,
        mapping,
        method=params.get("method", "Moving average"),
        periods=int(params.get("periods", 6)),
        window=int(params.get("window", 3)),
        alpha=float(params.get("alpha", 0.3)),
    )
    return _table_result("Generated forecast", table, {"total_forecast": float(table["Forecast"].sum()) if not table.empty else 0})


def _inventory_risk(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    table = inventory_risk_table(df, mapping)
    return _table_result("Inventory risk", table, {"risk_items": int(table["stockout_risk"].sum()) if not table.empty else 0})


def _abc_xyz(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    table = abc_xyz(df, mapping)
    return _table_result("ABC/XYZ segmentation", table, {"classes": int(table["ABC/XYZ"].nunique()) if not table.empty else 0})


def _inventory_aging(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    table = inventory_aging_table(df, mapping)
    obsolete = float(table.loc[table["Obsolete Candidate"], "Inventory Value"].sum()) if not table.empty else 0
    return _table_result("Inventory aging", table, {"obsolete_value": obsolete})


def _supplier_contracts(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    table = contract_analytics_table(df, mapping)
    return _table_result("Contract analytics", table, {"total_ppv": float(table["PPV"].sum()) if not table.empty else 0})


def _landed_cost(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    method = (params or {}).get("method", "Units")
    table = landed_cost_table(df, mapping, method=method)
    return _table_result("Landed cost", table, {"allocation_method": method})


def _warehouse_process(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    table = warehouse_process_table(df, mapping, float((params or {}).get("sla_hours", 24)))
    return _table_result("Warehouse process analytics", table, {"sla_breaches": int(table["SLA Breach"].sum()) if not table.empty else 0})


def _mrp_lite(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    table = mrp_lite_table(df, mapping)
    return _table_result("MRP-lite shortage plan", table, {"shortage_components": int(table["Shortage Risk"].sum()) if not table.empty else 0})


def _business_calendar(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    table = business_calendar_table(df, mapping)
    return _table_result("Business calendar", table, {"working_days": int(table["Working Day"].sum()) if not table.empty else 0})


def _failed_rows(df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    table = failed_row_quarantine(df, mapping)
    return _table_result("Failed-row quarantine", table, {"failed_rows": len(table)})


TOOLS: dict[str, LocalTool] = {
    "data_quality": LocalTool("data_quality", "Data Quality", "Validate data and summarize quality issues.", _data_quality),
    "kpi_snapshot": LocalTool("kpi_snapshot", "Executive", "Create a KPI table across all SCM modules.", _kpi_snapshot),
    "forecast": LocalTool("forecast", "Demand", "Generate an offline demand forecast.", _forecast),
    "inventory_risk": LocalTool("inventory_risk", "Inventory", "Calculate stockout, safety stock, reorder point, and excess risk.", _inventory_risk),
    "abc_xyz": LocalTool("abc_xyz", "Inventory", "Segment SKUs by value and demand variability.", _abc_xyz),
    "inventory_aging": LocalTool("inventory_aging", "Inventory", "Age inventory by lot/batch and value obsolete candidates.", _inventory_aging),
    "supplier_contracts": LocalTool("supplier_contracts", "Procurement", "Calculate PPV and contract compliance.", _supplier_contracts),
    "landed_cost": LocalTool("landed_cost", "Finance", "Allocate freight and compute landed margin/cost-to-serve.", _landed_cost),
    "warehouse_process": LocalTool("warehouse_process", "Warehouse", "Analyze dock-to-stock, pick flow, and SLA breaches.", _warehouse_process),
    "mrp_lite": LocalTool("mrp_lite", "Production", "Build a simple net-requirements shortage plan.", _mrp_lite),
    "business_calendar": LocalTool("business_calendar", "Settings", "Create a local business/fiscal calendar.", _business_calendar),
    "failed_rows": LocalTool("failed_rows", "Data Quality", "Return rows with invalid numeric/date values.", _failed_rows),
}


def list_tools() -> list[dict[str, str]]:
    return [
        {"name": tool.name, "category": tool.category, "description": tool.description}
        for tool in sorted(TOOLS.values(), key=lambda item: (item.category, item.name))
    ]


def run_tool(name: str, df: pd.DataFrame, mapping: dict, params: dict | None = None) -> ToolResult:
    if name not in TOOLS:
        raise ValueError(f"Unknown tool '{name}'. Available tools: {', '.join(sorted(TOOLS))}")
    return TOOLS[name].run(df, mapping, params or {})
