# Pytest Test Plan for SCM Analytics Studio Fixtures

## Scope

This plan covers unit, integration, CLI, regression, validation-only, export, SQLite backup/restore, and offline deployment testing.

## Fixture groups and intended assertions

| Group | Fixtures | Main assertions |
|---|---|---|
| Happy path | `01_happy_path/*` | Clean CSV/XLSX load, standard auto-mapping, integrated dashboard KPIs |
| File formats | `02_file_formats/*` | CSV/XLSX/XLS parsing, sheet selection, empty/header-only handling, irrelevant sheet skipping |
| Cleaning | `03_data_cleaning/*` | trimming, case normalization, missing values, duplicate detection, date/numeric parsing |
| Mapping | `04_mapping/*` | synonyms, snake/camel/spaced headers, required fields, ambiguous/duplicate headers |
| Forecasting | `05_demand_forecasting/*` | seasonality, sparsity, volatility, bias, WAPE/MAPE/tracking signal |
| Inventory | `06_inventory/*` | ABC/XYZ, safety stock, reorder point, aging, stockout/overstock/slow/dead stock |
| Procurement | `07_procurement_suppliers/*` | PO aging, PPV, off-contract spend, supplier OTD, supplier defect rate |
| Logistics | `08_logistics_transportation/*` | carrier/lane performance, late shipments, cost per kg/mile, incoterms/currency |
| Warehouse | `09_warehouse/*` | productivity, SLA breaches, location utilization, cycle count variance |
| Production/MRP | `10_production_mrp/*` | schedule adherence, OEE-style metrics, BOM requirements, shortages |
| Finance | `11_cost_finance/*` | gross margin, GMROI, landed cost, cost-to-serve, mixed currency warnings |
| Bad data | `12_validation_bad_data/*` | row-level validation errors, orphan rows, invalid IDs, divide-by-zero safety |
| CLI/export | `13_cli_export/*` | batch analysis, validation-only, golden-output compare, export roundtrip, SQLite backup/restore |
| Offline | `14_offline_deployment/*` | local-only paths, Unicode, weird filenames, large file memory pressure, no-network behavior |

## Suggested test layers

### 1. Loader tests

- `test_csv_loader_preserves_columns`
- `test_xlsx_loader_lists_sheets`
- `test_xls_loader_accepts_or_returns_supported_error`
- `test_empty_sheet_skipped`
- `test_header_only_sheet_warns_without_crash`

### 2. Cleaning tests

- `test_trim_whitespace_and_normalize_case`
- `test_mixed_date_formats_parse_or_flag`
- `test_currency_percentage_thousands_parse`
- `test_parentheses_negative_parse`
- `test_invalid_numeric_tokens_reported`

### 3. Mapping tests

- `test_standard_headers_auto_map`
- `test_synonym_headers_auto_map`
- `test_snake_camel_spaced_headers_normalize`
- `test_missing_required_fields_block_dashboard`
- `test_duplicate_ambiguous_headers_require_manual_mapping`

### 4. KPI tests

Use `13_cli_export/golden_kpis.json` as the source of truth.

- Fill rate: `sum(sales_qty) / sum(demand_qty)`
- On-time delivery rate: delivered shipments on/before promised date divided by delivered shipments
- Forecast WAPE: `sum(abs(actual - forecast)) / sum(actual)`
- Inventory turnover: `sum(cogs) / average(inventory_qty * unit_cost)`
- Supplier defect rate: `sum(defect_qty) / sum(received_qty)`

### 5. Validation tests

- `test_negative_quantities_invalid`
- `test_receipt_before_order_invalid`
- `test_ship_before_order_invalid`
- `test_actual_before_planned_invalid`
- `test_missing_currency_invalid`
- `test_invalid_master_ids_invalid`
- `test_orphan_cross_sheet_rows_invalid`
- `test_divide_by_zero_safe`

### 6. CLI tests

Run CLI commands from `docs/cli_regression_commands.md` in CI. Capture JSON output and compare normalized results to `golden_kpis.json` and `expected_validation_output.json`.

### 7. Offline tests

- Monkeypatch `socket.socket`, `requests`, or app-specific HTTP clients to raise exceptions.
- Verify local path fields remain strings and are never opened unless selected by user.
- Run large-file tests under a memory/time budget.

## CI recommendation

Use markers:

```bash
pytest -m "smoke"
pytest -m "not slow"
pytest -m "slow" --maxfail=1
```

Recommended pytest markers:

```ini
[pytest]
markers =
    smoke: fast core tests
    excel: workbook parsing tests
    cli: subprocess CLI tests
    slow: large fixture and memory pressure tests
    offline: network-disabled tests
```
