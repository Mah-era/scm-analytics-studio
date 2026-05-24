"""Fixture-pack processing and golden KPI accuracy checks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .column_mapper import auto_map_columns
from .data_cleaner import clean_data
from .data_loader import combine_sheets, read_file
from .kpi_calculator import safe_div


TABULAR_SUFFIXES = {".csv", ".xlsx", ".xls"}


def compute_golden_metrics(df: pd.DataFrame, mapping: dict) -> dict[str, float]:
    demand = mapping.get("Demand")
    sales = mapping.get("Sales")
    forecast = mapping.get("Forecast")
    delivery = mapping.get("Delivery Date")
    promised = mapping.get("Promised Delivery Date")
    cogs = mapping.get("COGS")
    inventory = mapping.get("Inventory")
    cost = mapping.get("Cost")
    defective = mapping.get("Defective Units")
    total_units = mapping.get("Total Units")

    demand_s = pd.to_numeric(df[demand], errors="coerce").fillna(0) if demand in df.columns else pd.Series(dtype="float64")
    sales_s = pd.to_numeric(df[sales], errors="coerce").fillna(0) if sales in df.columns else pd.Series(dtype="float64")
    forecast_s = pd.to_numeric(df[forecast], errors="coerce").fillna(0) if forecast in df.columns else pd.Series(dtype="float64")
    actual_delivery = pd.to_datetime(df[delivery], errors="coerce") if delivery in df.columns else pd.Series(dtype="datetime64[ns]")
    promised_delivery = pd.to_datetime(df[promised], errors="coerce") if promised in df.columns else pd.Series(dtype="datetime64[ns]")
    cogs_s = pd.to_numeric(df[cogs], errors="coerce").fillna(0) if cogs in df.columns else pd.Series(dtype="float64")
    inv_s = pd.to_numeric(df[inventory], errors="coerce").fillna(0) if inventory in df.columns else pd.Series(dtype="float64")
    cost_s = pd.to_numeric(df[cost], errors="coerce").fillna(0) if cost in df.columns else pd.Series(dtype="float64")
    defect_s = pd.to_numeric(df[defective], errors="coerce").fillna(0) if defective in df.columns else pd.Series(dtype="float64")
    total_s = pd.to_numeric(df[total_units], errors="coerce").fillna(0) if total_units in df.columns else pd.Series(dtype="float64")

    on_time_mask = (actual_delivery <= promised_delivery).fillna(False) if not actual_delivery.empty and not promised_delivery.empty else pd.Series(dtype="bool")
    inventory_value = inv_s * cost_s if len(inv_s) and len(cost_s) else pd.Series(dtype="float64")

    return {
        "fill_rate": round(safe_div(sales_s.sum(), demand_s.sum()), 6),
        "on_time_delivery_rate": round(safe_div(on_time_mask.sum(), len(on_time_mask)), 6),
        "forecast_wape": round(safe_div((demand_s - forecast_s).abs().sum(), demand_s.sum()), 6),
        "inventory_turnover": round(safe_div(cogs_s.sum(), inventory_value.mean()), 6),
        "supplier_defect_rate": round(safe_div(defect_s.sum(), total_s.sum()), 6),
    }


def fixture_pack_report(root: Path) -> dict[str, Any]:
    manifest = root / "00_manifest" / "manifest.csv"
    golden = root / "13_cli_export" / "golden_kpis.json"
    if not manifest.exists():
        raise FileNotFoundError(manifest)
    manifest_df = pd.read_csv(manifest)
    rows = []
    for _, item in manifest_df.iterrows():
        source = root / str(item["file"])
        if source.suffix.lower() not in TABULAR_SUFFIXES:
            rows.append({"file": str(item["file"]), "status": "SKIP", "mapped_fields": 0, "rows": 0, "detail": "Non-tabular fixture"})
            continue
        try:
            sheets = read_file(source)
            raw = combine_sheets(sheets) if len(sheets) > 1 else next(iter(sheets.values()))
            df = clean_data(raw)
            mapping = auto_map_columns(df)
            rows.append({
                "file": str(item["file"]),
                "status": "PASS" if not df.empty else "FAIL",
                "mapped_fields": sum(1 for value in mapping.values() if value),
                "rows": int(len(df)),
                "detail": "" if not df.empty else "No rows after cleaning",
            })
        except Exception as exc:
            rows.append({"file": str(item["file"]), "status": "FAIL", "mapped_fields": 0, "rows": 0, "detail": str(exc)})

    golden_result = {}
    if golden.exists():
        payload = json.loads(golden.read_text(encoding="utf-8"))
        source = root / payload["source_file"]
        sheets = read_file(source)
        df = clean_data(next(iter(sheets.values())))
        mapping = auto_map_columns(df)
        actual = compute_golden_metrics(df, mapping)
        expected = {key: round(float(value), 6) for key, value in payload["expected"].items()}
        golden_result = {
            "source_file": payload["source_file"],
            "expected": expected,
            "actual": actual,
            "passed": all(abs(actual.get(key, 0) - expected.get(key, 0)) <= 0.0001 for key in expected),
        }

    report_df = pd.DataFrame(rows)
    return {
        "fixture_root": str(root),
        "total_manifest_entries": int(len(report_df)),
        "tabular_passed": int((report_df["status"] == "PASS").sum()),
        "tabular_failed": int((report_df["status"] == "FAIL").sum()),
        "skipped": int((report_df["status"] == "SKIP").sum()),
        "average_mapped_fields": round(float(report_df.loc[report_df["status"] == "PASS", "mapped_fields"].mean() or 0), 2),
        "golden_kpis": golden_result,
        "details": rows,
    }
