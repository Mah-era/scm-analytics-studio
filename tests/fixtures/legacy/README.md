# SCM Analytics Studio Fixture Pack

This pack contains **30 primary spreadsheet test files** for SCM Analytics Studio:

- 10 CSV files
- 10 XLSX files
- 10 XLS files

The files are split between `sample_data/` for demo/happy-path datasets and typed QA folders.
A machine-readable manifest is included as `FIXTURE_MANIFEST.csv` and `FIXTURE_MANIFEST.json`.

## Folder layout

```text
sample_data/
  clean_integrated_scm.csv
  multi_sheet_scm_workbook.xlsx
  legacy_clean_orders.xls

csv/
excel/
cli/
sqlite/
export_validation/
```

## Minimum essential fixtures

Use these in every smoke/regression run:

1. `sample_data/clean_integrated_scm.csv`
2. `sample_data/multi_sheet_scm_workbook.xlsx`
3. `csv/messy_scm_data.csv`
4. `csv/missing_required_columns.csv`
5. `csv/missing_values_sparse.csv`
6. `csv/duplicate_rows.csv`
7. `csv/invalid_dates.csv`
8. `csv/mixed_numeric_formats.csv`
9. `csv/currency_percentage_strings.csv`
10. `excel/column_mapping_synonyms.xlsx`
11. `excel/empty_workbook_sheets.xlsx`
12. `excel/non_scm_irrelevant_columns.xlsx`
13. `cli/cli_orders_input.csv`
14. `sqlite/sqlite_seed_data.xls`
15. `export_validation/export_roundtrip_validation.xlsx`
16. `sample_data/legacy_clean_orders.xls`

## Nice-to-have stress/domain fixtures

Use these in nightly or extended QA runs:

- `csv/large_scm_dataset_5000_rows.csv`
- `excel/supplier_scorecards.xlsx`
- `excel/logistics_shipments.xlsx`
- `excel/warehouse_inventory.xlsx`
- `excel/production_runs.xlsx`
- `excel/cost_finance_scm.xlsx`
- Legacy `.xls` domain equivalents under `excel/`

## SQLite reference

`sqlite/expected_persistence_reference.sqlite` is included as an ancillary reference database for persistence assertions. It is not counted among the 30 primary CSV/XLSX/XLS files.
