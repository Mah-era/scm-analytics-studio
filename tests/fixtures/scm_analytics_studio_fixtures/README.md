# SCM Analytics Studio — Offline TDD Fixture Pack

This pack contains synthetic, realistic, offline-only fixtures for a Python Streamlit app called **SCM Analytics Studio**.

## What is included

- **60 manifest entries**
- CSV, XLSX, binary legacy XLS, JSON, Markdown, shell, pytest, and SQLite files
- Small fixtures for fast unit tests
- Large fixtures with **6,000 rows** and **20,000 rows**
- Multi-sheet Excel workbooks
- Dirty data, mapping, validation, forecasting, inventory, procurement, logistics, warehouse, production, finance, CLI/export, SQLite, and offline deployment cases
- Golden KPI expectations for fill rate, on-time delivery rate, WAPE, inventory turnover, and supplier defect rate
- Pytest test plan and CLI regression commands

## Folder structure

```text
scm_analytics_studio_fixtures/
├── 00_manifest/
├── 01_happy_path/
├── 02_file_formats/
├── 03_data_cleaning/
├── 04_mapping/
├── 05_demand_forecasting/
├── 06_inventory/
├── 07_procurement_suppliers/
├── 08_logistics_transportation/
├── 09_warehouse/
├── 10_production_mrp/
├── 11_cost_finance/
├── 12_validation_bad_data/
├── 13_cli_export/
├── 14_offline_deployment/
├── docs/
├── scripts/
└── tests/
```

## Priority guide

- **P0**: must pass before release
- **P1**: important regression coverage
- **P2**: edge/robustness coverage

## Golden KPI expectations

Source file: `13_cli_export/golden_kpis.json` using `01_happy_path/full_integrated_dataset.csv`.

| Metric | Expected |
|---|---:|
| fill_rate | 0.981903 |
| on_time_delivery_rate | 0.833333 |
| forecast_wape | 0.055684 |
| inventory_turnover | 5.548615 |
| supplier_defect_rate | 0.003251 |

## Direct CSV content examples

### `01_happy_path/clean_integrated_scm.csv`

```csv
order_id,order_date,ship_date,demand_date,sku,product,category,customer_id,customer,region,supplier_id,supplier,warehouse_id,warehouse,inventory_qty,demand_qty,sales_qty,forecast_qty,unit_price,unit_cost,revenue,cogs,po_id,order_qty,received_qty,defect_qty,lead_time_days,promised_delivery_date,actual_delivery_date,shipment_id,carrier,route,origin,destination,shipment_status,freight_cost,weight_kg,volume_cbm,distance_miles,incoterm,currency,production_qty,planned_production_qty,good_qty,scrap_qty,capacity_hours,max_capacity_hours,downtime_hours,receipt_date,last_movement_date
SO-2026-1000,2026-01-05,2026-01-08,2026-01-06,SKU-1001,AeroBlend Mixer,Appliances,CUST-001,NorthMart,North,SUP-ALPHA,Alpha Components,WH-DHK,Dhaka DC,250,80,80,85,72.0,42.0,5760.0,3360.0,PO-2026-2000,92,92,2,6,2026-01-11,2026-01-11,SHP-2026-3000,Redline Freight,DHK-CTG,Dhaka,Chattogram,Delivered,156.58,36.0,1.44,155,FOB,BDT,80,80,77,3,8.0,10.0,0.0,2025-12-16,2026-01-05
SO-2026-1001,2026-01-08,2026-01-10,2026-01-09,SKU-1002,Nimbus Rice Cooker,Appliances,CUST-002,MetroBazaar,Central,SUP-BETA,Beta Home Goods,WH-CTG,Chattogram DC,287,95,95,87,55.0,31.5,5225.0,2992.5,PO-2026-2001,109,109,0,5,2026-01-13,2026-01-13,SHP-2026-3001,BlueRiver Logistics,DHK-KHL,Dhaka,Khulna,Delivered,203.95,54.15,2.09,260,CIF,BDT,100,95,100,0,8.0,10.0,0.2,2025-12-18,2026-01-07
SO-2026-1002,2026-01-11,2026-01-13,2026-01-12,SKU-1003,Luna Desk Lamp,Home,CUST-003,Sunrise Retail,South,SUP-CITY,Cityline Electrical,WH-KHL,Khulna Forward Stock,324,110,110,122,24.0,12.0,2640.0,1320.0,PO-2026-2002,126,126,0,5,2026-01-16,2026-01-16,SHP-2026-3002,NorthStar Transport,CTG-SYL,Dhaka,Sylhet,Delivered,174.26,75.9,2.86,180,EXW,BDT,120,110,120,0,8.0,10.0,0.4,2025-12-20,2026-01-09
SO-2026-1003,2026-01-14,2026-01-17,2026-01-15,SKU-1004,Terra Storage Bin,Home,CUST-004,Unicode ক্রেতা,East,SUP-DELTA,Delta Plastics,WH-DHK,Dhaka DC,361,125,112,119,11.5,5.4,1288.0,604.8,PO-2026-2003,143,143,0,6,2026-01-20,2026-01-20,SHP-2026-3003,Redline Freight,DHK-RAJ,Dhaka,Rajshahi,Delivered,189.53,90.72,3.36,210,FOB,BDT,127,125,127,0,8.0,10.0,0.6,2025-12-22,2026-01-11
```

### `05_demand_forecasting/actual_vs_forecast_metrics.csv`

```csv
date,sku,product,customer,region,demand_qty,sales_qty,forecast_qty
2026-01-01,SKU-1001,AeroBlend Mixer,NorthMart,North,100,96,110
2026-01-02,SKU-1001,AeroBlend Mixer,NorthMart,North,120,118,100
2026-01-03,SKU-1002,Nimbus Rice Cooker,MetroBazaar,Central,80,80,84
2026-01-04,SKU-1002,Nimbus Rice Cooker,MetroBazaar,Central,0,0,20
```

### `12_validation_bad_data/bad_data_validation.csv`

```csv
row_id,order_id,sku,supplier_id,warehouse_id,order_date,ship_date,planned_date,actual_date,received_date,quantity,unit_price,currency,uom
BAD-001,SO-BAD-1,SKU-1001,SUP-ALPHA,WH-DHK,2026-01-10,2026-01-09,2026-01-12,2026-01-11,2026-01-08,-5,72,BDT,EA
BAD-002,SO-BAD-2,SKU-9999,SUP-BOGUS,WH-XXX,2026-02-01,2026-02-03,2026-02-05,2026-02-08,2026-02-20,100,999999,,CASE
BAD-003,SO-BAD-3,SKU-1003,SUP-CITY,WH-KHL,2026-03-01,2026-03-05,2026-03-07,2026-03-06,2026-04-30,0,0,BDT,EA
```

## Recommended first TDD loop

1. Start with `13_cli_export/cli_smoke_small.csv`.
2. Add clean parser tests with `01_happy_path/clean_integrated_scm.csv`.
3. Add Excel sheet detection tests with `01_happy_path/clean_multisheet_scm.xlsx`.
4. Add mapper tests with `04_mapping/*.csv` and `04_mapping/mapping_template.json`.
5. Add KPI regression tests with `13_cli_export/golden_kpis.json`.
6. Add validation-only failures with `12_validation_bad_data/bad_data_validation.csv`.
7. Add batch/performance tests with `13_cli_export/large_6000_rows.csv` and `14_offline_deployment/large_memory_pressure_20000_rows.csv`.

## Offline-only assumptions

Fixtures do not require external APIs. Tests should disable network access or monkeypatch network libraries so any accidental call fails fast.
