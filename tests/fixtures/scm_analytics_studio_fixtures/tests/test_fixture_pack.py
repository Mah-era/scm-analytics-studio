"""
Fixture-level tests for SCM Analytics Studio.

These tests validate the fixture pack itself and provide examples for app-level TDD.
Set SCM_FIXTURES_DIR to the fixture root, or run pytest from inside the fixture pack.
"""

from pathlib import Path
import csv
import json
import os
import sqlite3
import struct

import pytest

FIXTURES = Path(os.environ.get("SCM_FIXTURES_DIR", Path(__file__).resolve().parents[1]))

def read_csv_dicts(relpath: str):
    with (FIXTURES / relpath).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def test_manifest_paths_exist():
    manifest_path = FIXTURES / "00_manifest" / "manifest.csv"
    assert manifest_path.exists()
    with manifest_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 30
    missing = [r["file"] for r in rows if not (FIXTURES / r["file"]).exists()]
    assert not missing

def test_clean_integrated_golden_kpis_match_fixture():
    rows = read_csv_dicts("01_happy_path/full_integrated_dataset.csv")
    expected = json.loads((FIXTURES / "13_cli_export/golden_kpis.json").read_text(encoding="utf-8"))["expected"]

    demand = sum(float(r["demand_qty"]) for r in rows)
    sales = sum(float(r["sales_qty"]) for r in rows)
    delivered = [r for r in rows if r["shipment_status"] == "Delivered"]
    on_time = [r for r in delivered if r["actual_delivery_date"] <= r["promised_delivery_date"]]
    wape = sum(abs(float(r["demand_qty"]) - float(r["forecast_qty"])) for r in rows) / demand
    inventory_turnover = sum(float(r["cogs"]) for r in rows) / (
        sum(float(r["inventory_qty"]) * float(r["unit_cost"]) for r in rows) / len(rows)
    )
    supplier_defect_rate = sum(float(r["defect_qty"]) for r in rows) / sum(float(r["received_qty"]) for r in rows)

    actual = {
        "fill_rate": sales / demand,
        "on_time_delivery_rate": len(on_time) / len(delivered),
        "forecast_wape": wape,
        "inventory_turnover": inventory_turnover,
        "supplier_defect_rate": supplier_defect_rate,
    }

    for metric, value in actual.items():
        assert round(value, 6) == expected[metric]

def test_expected_validation_rules_are_present():
    spec = json.loads((FIXTURES / "13_cli_export/expected_validation_output.json").read_text(encoding="utf-8"))
    assert spec["expected_error_count_min"] >= len(spec["expected_rules"])
    rules = {(r["rule_id"], r["row_id"], r["field"]) for r in spec["expected_rules"]}
    assert ("NEGATIVE_QUANTITY", "BAD-001", "quantity") in rules
    assert ("MISSING_CURRENCY", "BAD-002", "currency") in rules

def test_legacy_xls_is_binary_biff2():
    data = (FIXTURES / "02_file_formats/legacy_xls_upload.xls").read_bytes()
    opcode, length, version, doc_type = struct.unpack("<HHHH", data[:8])
    assert opcode == 0x0009
    assert version == 0x0002
    assert doc_type == 0x0010

@pytest.mark.excel
def test_xlsx_workbook_has_expected_sheets():
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.load_workbook(FIXTURES / "01_happy_path/clean_multisheet_scm.xlsx", read_only=True, data_only=True)
    assert {"Orders", "Demand", "Inventory", "Procurement", "Shipments", "Production"}.issubset(set(wb.sheetnames))

def test_duplicate_ambiguous_headers_preserved():
    with (FIXTURES / "04_mapping/duplicate_ambiguous_headers.csv").open(encoding="utf-8") as f:
        header = f.readline().strip().split(",")
    assert header.count("sku") == 2

def test_sqlite_seed_has_expected_tables():
    db = FIXTURES / "13_cli_export/sqlite_seed.db"
    conn = sqlite3.connect(db)
    try:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"demand", "inventory", "kpi_expected"}.issubset(tables)
        assert conn.execute("SELECT COUNT(*) FROM kpi_expected").fetchone()[0] >= 5
    finally:
        conn.close()

def test_fixture_pack_contains_no_remote_paths_in_manifest():
    manifest = (FIXTURES / "00_manifest/manifest.csv").read_text(encoding="utf-8").lower()
    assert "https://" not in manifest
    assert "http://" not in manifest
