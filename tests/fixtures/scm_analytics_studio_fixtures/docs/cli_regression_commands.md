# CLI Regression Commands

Assumed CLI entrypoint:

```bash
SCM="python -m scm_analytics_studio.cli"
export SCM_OFFLINE=1
mkdir -p out
```

Adjust `SCM` if your actual command differs.

## 1. Smoke

```bash
$SCM analyze fixtures/13_cli_export/cli_smoke_small.csv --offline --output out/smoke
$SCM validate fixtures/13_cli_export/cli_smoke_small.csv --offline --validation-only --output out/smoke_validation.json
```

## 2. Happy path integrated data

```bash
$SCM analyze fixtures/01_happy_path/clean_integrated_scm.csv --offline --module all --output out/happy_csv
$SCM analyze fixtures/01_happy_path/full_integrated_dataset.csv --offline --module all --export-format json --output out/full_integrated
$SCM analyze fixtures/01_happy_path/clean_multisheet_scm.xlsx --offline --sheet Orders --module all --output out/happy_xlsx
```

## 3. File format coverage

```bash
$SCM inspect fixtures/02_file_formats/multi_sheet_workbook.xlsx --offline --list-sheets
$SCM analyze fixtures/02_file_formats/clean_csv_upload.csv --offline --output out/format_csv
$SCM analyze fixtures/02_file_formats/legacy_xls_upload.xls --offline --output out/format_xls
$SCM validate fixtures/02_file_formats/empty_sheet_workbook.xlsx --offline --validation-only --output out/empty_sheet_validation.json
$SCM validate fixtures/02_file_formats/header_only_sheet.xlsx --offline --validation-only --output out/header_only_validation.json
$SCM analyze fixtures/02_file_formats/irrelevant_sheets.xlsx --offline --sheet Demand_Data --output out/irrelevant_skipped
$SCM validate fixtures/02_file_formats/merged_header_like_issues.xlsx --offline --header-row 3 --output out/merged_header_validation.json
```

## 4. Cleaning and validation

```bash
$SCM validate fixtures/03_data_cleaning/missing_duplicate_space_case.csv --offline --validation-only --output out/cleaning_missing_duplicate.json
$SCM clean fixtures/03_data_cleaning/mixed_dates_numbers_currency.csv --offline --output out/cleaned_mixed_dates.csv
$SCM validate fixtures/03_data_cleaning/invalid_numeric_tokens.csv --offline --validation-only --output out/invalid_numeric.json
$SCM validate fixtures/03_data_cleaning/blank_required_fields.csv --offline --validation-only --output out/blank_required.json
```

## 5. Column mapping

```bash
$SCM map fixtures/04_mapping/standard_columns.csv --offline --template fixtures/04_mapping/mapping_template.json --output out/map_standard.json
$SCM map fixtures/04_mapping/synonym_columns.csv --offline --template fixtures/04_mapping/mapping_template.json --output out/map_synonyms.json
$SCM map fixtures/04_mapping/snake_camel_spaced_headers.csv --offline --template fixtures/04_mapping/mapping_template.json --output out/map_header_styles.json
$SCM validate fixtures/04_mapping/missing_required_module_fields.csv --offline --validation-only --module demand --output out/missing_required_mapping.json
$SCM map fixtures/04_mapping/duplicate_ambiguous_headers.csv --offline --require-manual-on-ambiguous --output out/duplicate_ambiguous_mapping.json
$SCM map fixtures/04_mapping/invalid_mapping_scenario.csv --offline --output out/invalid_mapping.json
```

## 6. Forecasting

```bash
$SCM forecast fixtures/05_demand_forecasting/seasonal_demand.csv --offline --output out/forecast_seasonal
$SCM forecast fixtures/05_demand_forecasting/sparse_demand.csv --offline --output out/forecast_sparse
$SCM forecast fixtures/05_demand_forecasting/volatile_demand_forecast_bias.csv --offline --output out/forecast_volatile
$SCM kpi fixtures/05_demand_forecasting/actual_vs_forecast_metrics.csv --offline --metrics forecast_wape,mape,bias,tracking_signal --output out/forecast_metrics.json
```

## 7. Inventory

```bash
$SCM inventory fixtures/06_inventory/inventory_risk_abc_xyz.csv --offline --output out/inventory_risk
$SCM inventory-aging fixtures/06_inventory/inventory_aging_lots.csv --offline --as-of 2026-05-11 --output out/inventory_aging
$SCM inventory fixtures/06_inventory/stockout_overstock_slow_dead.csv --offline --output out/inventory_flags
```

## 8. Procurement and suppliers

```bash
$SCM procurement fixtures/07_procurement_suppliers/procurement_pos_supplier_scorecard.csv --offline --output out/procurement_scorecard
$SCM po-aging fixtures/07_procurement_suppliers/po_aging_statuses.csv --offline --as-of 2026-05-11 --output out/po_aging
$SCM procurement fixtures/07_procurement_suppliers/off_contract_ppv.csv --offline --metrics ppv,off_contract_spend --output out/off_contract_ppv
```

## 9. Logistics and warehouse

```bash
$SCM logistics fixtures/08_logistics_transportation/shipments_carrier_lane.csv --offline --output out/logistics_lane
$SCM logistics fixtures/08_logistics_transportation/incoterm_currency_mixed.csv --offline --output out/logistics_currency
$SCM warehouse fixtures/09_warehouse/warehouse_ops_sla_cycle_count.csv --offline --output out/warehouse_ops
$SCM warehouse fixtures/09_warehouse/warehouse_locations_stock.csv --offline --output out/warehouse_locations
```

## 10. Production, MRP, finance

```bash
$SCM production fixtures/10_production_mrp/production_oee.csv --offline --output out/production_oee
$SCM mrp fixtures/10_production_mrp/bom_mrp_shortage.csv --offline --output out/mrp_shortage
$SCM finance fixtures/11_cost_finance/cost_finance_landed.csv --offline --output out/finance_cost
$SCM landed-cost fixtures/11_cost_finance/freight_allocation_methods.csv --offline --output out/freight_allocation
$SCM finance fixtures/11_cost_finance/mixed_currency_costs.csv --offline --output out/mixed_currency
```

## 11. Bad data and golden regression

```bash
$SCM validate fixtures/12_validation_bad_data/bad_data_validation.csv --offline --validation-only --output out/bad_data_validation.json
$SCM validate fixtures/12_validation_bad_data/orphan_rows_multisheet.xlsx --offline --validation-only --output out/orphan_rows.json
$SCM validate fixtures/12_validation_bad_data/divide_by_zero_inputs.csv --offline --validation-only --output out/divide_by_zero.json
$SCM validate fixtures/12_validation_bad_data/invalid_ids_mixed_uom.csv --offline --validation-only --output out/invalid_ids_mixed_uom.json

$SCM kpi fixtures/01_happy_path/full_integrated_dataset.csv --offline --expected fixtures/13_cli_export/golden_kpis.json --output out/golden_kpi_actual.json
```

## 12. Large, export, SQLite, batch regression

```bash
$SCM analyze fixtures/13_cli_export/large_6000_rows.csv --offline --output out/large_6000
$SCM export fixtures/13_cli_export/export_roundtrip.csv --offline --format xlsx --output out/export_roundtrip.xlsx
$SCM validate out/export_roundtrip.xlsx --offline --validation-only --output out/export_roundtrip_validation.json

$SCM sqlite restore fixtures/13_cli_export/sqlite_seed.db --offline --output out/restored.sqlite
$SCM sqlite backup out/restored.sqlite --offline --output out/backup.sqlite

$SCM fixture-regression fixtures/13_cli_export/batch_regression_set.json --offline --manifest fixtures/13_cli_export/fixture_manifest.json --output out/batch_regression
```

## 13. Offline deployment

```bash
$SCM validate fixtures/14_offline_deployment/local_paths_unicode.csv --offline --validation-only --output out/local_paths_unicode.json
$SCM analyze "fixtures/14_offline_deployment/weird filename with spaces & unicode Ω.csv" --offline --output out/weird_filename
$SCM analyze fixtures/14_offline_deployment/cross_platform_path_safe.csv --offline --output out/path_safe
$SCM analyze fixtures/14_offline_deployment/large_memory_pressure_20000_rows.csv --offline --chunk-size 5000 --output out/memory_pressure
```
