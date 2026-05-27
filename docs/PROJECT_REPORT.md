# Project Report

## Overview

SCM Analytics Studio is a fully offline Supply Chain Management analytics application built as a single Streamlit app with CLI, local API, and MCP-style integration entry points. It accepts CSV, XLSX, and legacy XLS files, cleans and maps SCM data, calculates KPIs, renders interactive Plotly charts, exports offline reports, and optionally stores reusable mappings and cleaned snapshots in local SQLite.

The application is designed for a clean corporate operations control-room experience. It groups functionality into Data, Planning, Operations, Finance, and Exports workspaces so users do not have to navigate one long dashboard strip.

## Technology Stack

| Area | Implementation |
|---|---|
| UI | Streamlit |
| Data handling | Pandas |
| Interactive charts | Plotly |
| Static chart export | Matplotlib fallback via `modules/chart_generator.py` |
| Excel processing | OpenPyXL through Pandas; xlrd included for legacy XLS |
| Local storage | SQLite in `data/scm_analytics_studio.sqlite` |
| PDF export | ReportLab |
| PowerPoint export | Offline PPTX ZIP writer in `modules/advanced_features.py` |
| CLI | Python argparse in `cli.py` |
| Local API | `api_server.py` |
| MCP-style tool access | `mcp_server.py` |
| Offline skills/tools | `modules/tool_registry.py`, `modules/skill_registry.py`, `modules/workflow_assistant.py` |

## Organized File Structure

| Folder/File | Purpose |
|---|---|
| `app.py` | Main Streamlit app at `localhost:3000`. |
| `cli.py` | Offline batch analysis, fixture runner, exports, tools, skills, API/MCP launch commands. |
| `api_server.py` | Local HTTP API for offline interconnection. |
| `mcp_server.py` | Stdio MCP-style server for local clients. |
| `modules/` | App logic split by data loading, cleaning, mapping, KPIs, charts, storage, reporting, and domain dashboards. |
| `sample_data/` | Normal demo/training datasets used by the app. |
| `tests/fixtures/scm_analytics_studio_fixtures/` | Current TDD and regression fixture pack. |
| `tests/fixtures/legacy/` | Original fixture pack retained for compatibility checks. |
| `tests/uat/` | User Acceptance Testing checklist and scenarios. |
| `docs/` | Project structure, storage map, user guide, UAT plan, and this report. |
| `skills/` | Local plugin-style JSON skills. |
| `config/` | MCP client configuration example. |
| `data/` | Runtime SQLite and local rendering cache. |
| `exports/` | Generated user exports and CLI reports. |

Generated caches and runtime outputs are ignored with `.gitignore`, including `.venv/`, `__pycache__/`, `.pytest_cache/`, `.DS_Store`, SQLite runtime files, and export outputs.

## Data Pipeline

1. A user uploads a file, selects a saved SQLite dataset, or chooses bundled sample data.
2. CSV/XLS/XLSX sheets are normalized into a common sheet dictionary.
3. The user selects one sheet or combines all sheets.
4. Cleaning options normalize headers, parse dates/numbers, remove duplicates, and handle missing values.
5. Auto column mapping proposes SCM fields from source columns.
6. The user can manually adjust mappings and save them locally.
7. Sidebar filters produce the active filtered dataset.
8. Dashboards, KPIs, charts, validations, exports, tools, and skills all use the same filtered view.

## Implemented Workspaces

### Data Workspace

- Data preview.
- Column type detection.
- Numeric and categorical summaries.
- Missing value summary.
- Duplicate-row count.
- Date range summary.
- Mapping confidence table.
- Data validation report.
- Business calendar with working-day and fiscal-period flags.
- Audit log viewer and export.
- Local user feedback form, feedback review table, and feedback CSV export.
- SQLite backup download.
- Formula glossary.
- Saved dashboard template support.
- Smart Chart Generator.
- Workflow Assistant.

### Planning Workspace

- Executive control tower.
- Demand and sales analysis.
- Forecast accuracy.
- Forecast generation.
- Inventory dashboard.
- Inventory risk dashboard.
- Inventory aging.
- Scenario planning.

### Operations Workspace

- Procurement analytics.
- PO aging.
- Supplier scorecards.
- Contract analytics and purchase price variance.
- Logistics analytics.
- Carrier/lane scorecards.
- Warehouse analytics.
- Warehouse productivity.
- Warehouse process analytics.
- Production analytics.
- Production performance.
- MRP Lite shortage planning.

### Finance Workspace

- Cost and profitability analysis.
- Finance bridge.
- Landed cost and cost-to-serve allocation.

### Exports Workspace

- Cleaned CSV/XLSX.
- KPI CSV/XLSX.
- PDF dashboard summary.
- Full dashboard workbook.
- Chart bundle ZIP.
- Metric glossary CSV.
- Failed-row quarantine CSV.
- Mapping template JSON.
- Business calendar export.
- Audit log export.
- PowerPoint summary.
- SQLite dataset save and backup.

## SCM Modules

| Module | File | Highlights |
|---|---|---|
| Demand & Sales | `modules/demand_analysis.py` | Monthly/weekly trends, product/region/customer demand, volatility, actual vs forecast, moving average. |
| Inventory | `modules/inventory_analysis.py` | Inventory trend, SKU stock, ABC/Pareto, turnover, stockout, slow-moving and dead stock. |
| Procurement | `modules/procurement_analysis.py` | Supplier purchase volume/cost, lead time, on-time delivery, price trends, defects, scorecard. |
| Logistics | `modules/logistics_analysis.py` | Delivery time, route cost, carrier performance, freight trend, late deliveries, shipment cost. |
| Warehouse | `modules/warehouse_analysis.py` | Location stock, inbound/outbound, picking accuracy, storage utilization, productivity. |
| Production | `modules/production_analysis.py` | Production volume, product output, downtime, capacity, defects, planned vs actual. |
| Cost | `modules/cost_analysis.py` | SCM cost trend, category breakdown, product/supplier cost, gross margin. |
| Advanced SCM | `modules/advanced_features.py` | Forecasting, ABC/XYZ, safety stock, ROP, aging, PPV, landed cost, warehouse process, OEE-style metrics, MRP-lite, validations, exports. |

## KPI And Formula Coverage

Implemented or supported through mapped fields:

- OTIF.
- Fill rate.
- Perfect order rate.
- Backorder rate.
- Forecast accuracy, MAPE, WAPE, bias, and tracking signal style checks.
- Inventory turnover.
- Days inventory on hand/outstanding.
- GMROI.
- Safety stock.
- Reorder point.
- EOQ inputs.
- Lead-time variability.
- Supplier defect rate.
- Purchase price variance.
- Off-contract spend.
- Landed cost.
- Cost-to-serve allocation.
- Freight cost per unit/kg/mile where fields exist.
- Dock-to-stock time.
- Pick accuracy.
- Cycle count accuracy.
- Capacity utilization.
- OEE-style availability/performance/quality.
- Yield.
- Scrap rate.
- Schedule adherence.
- Cash-to-cash and working-capital inventory indicators.
- Gross margin.

## Smart Chart Generator

Users can choose:

- Line.
- Bar.
- Pie.
- Scatter.
- Histogram.
- Box.
- Heatmap.
- Area.
- Treemap.
- Pareto.

Controls include X-axis, Y-axis, category/color, and aggregation method: sum, average, count, min, and max. Charts can be exported as HTML and, where rendering support is available, PNG.

## Filters

Implemented filters include:

- Date range.
- Fiscal period.
- Product, SKU, supplier, customer, region, warehouse, category.
- Carrier and route.
- Origin and destination.
- Incoterm.
- Currency.
- UOM.
- Lot and batch.
- Plant and site.
- Planner and buyer.
- PO/order/shipment status.
- ABC/XYZ class.
- Stockout risk.

## Validation Rules

The validation layer checks for:

- Missing required mapped columns.
- Duplicate business keys.
- Negative quantities where invalid.
- Impossible date order such as receipt before order or ship date before order.
- Impossible lead times.
- Actual before planned dates.
- Unit price and numeric outliers.
- Missing or mixed currency.
- Mixed UOM.
- Inconsistent SKU/product IDs.
- Blank dates in time-series modules.
- Divide-by-zero KPI inputs.
- Failed rows for quarantine export.
- Header-only or empty datasets via loader/fixture checks.

## Offline Integrations

### CLI

`cli.py` supports:

- Serving the Streamlit app at port 3000.
- Batch analysis.
- Mapping apply/save/import/export.
- Cleaning and validation-only mode.
- KPI generation.
- Chart export.
- PDF/PPTX/workbook exports.
- SQLite backup and restore.
- Sample data generation.
- Fixture regression suite.
- Fixture accuracy checks.
- Local tool calls.
- Local skill calls.

### Local API

`api_server.py` exposes:

- `/health`
- `/catalog`
- `/tools`
- `/skills`
- `/inspect`
- `/run-tool`
- `/run-skill`

### MCP-Style Server

`mcp_server.py` provides stdio JSON-RPC style access to the same catalog, inspect, tool, and skill capabilities for local clients.

### Skills And Tool Calling

Built-in tools include data quality, KPI snapshot, forecast, inventory risk, ABC/XYZ, aging, supplier contracts, landed cost, warehouse process, MRP-lite, business calendar, and failed rows.

Built-in skills include data quality command center, inventory planner, demand forecaster, procurement manager, and operations control tower. Custom JSON skills can be added under `skills/`.

## Fixture And Test Assets

The current fixture suite is under:

```text
tests/fixtures/scm_analytics_studio_fixtures/
```

It covers happy path files, CSV/XLSX/XLS formats, cleaning edge cases, mapping synonyms, demand forecasting, inventory, procurement, logistics, warehouse, production/MRP, cost/finance, validation bad data, CLI/export, and offline deployment scenarios.

The legacy fixture pack is under:

```text
tests/fixtures/legacy/
```

It is retained for older edge cases and compatibility checks.

## UAT Coverage

User Acceptance Testing scenarios live at:

```text
tests/uat/UAT_CHECKLIST.md
```

They cover installation, app startup, file upload, cleaning, mapping, filters, workspaces, dashboards, exports, SQLite storage, CLI, API, MCP, offline operation, and error handling.

## UI Improvements Completed

- Grouped workspaces replace the long horizontal module strip.
- Dark sidebar/light content control-room theme.
- Explicit readable text colors for dark and light backgrounds.
- Hover grow behavior for buttons, tabs, metric panels, expanders, and workspace headers while preserving readable contrast.
- Dashboard descriptions are short and operational.
- Filters are consolidated in the sidebar and update every module.
- Missing data states show user-friendly messages instead of hard failures.

## Storage Summary

The app stores data only when the user chooses to save or export:

- SQLite database: `data/scm_analytics_studio.sqlite`.
- User feedback table: `user_feedback` inside `data/scm_analytics_studio.sqlite`.
- Generated exports: `exports/`.
- Built-in app demo data: `sample_data/`.
- Test/QA fixture data: `tests/fixtures/`.
- Custom skills: `skills/`.
- Integration examples: `config/`.

See `docs/STORAGE_MAP.md` for the complete storage table.

## Current Status

The project now contains the requested offline app, SCM modules, advanced planning/analytics features, CLI batch workflow, local API, MCP-style tool calling, local skills, fixture packs, organized documentation, UAT checklist, and local storage documentation.

The latest verification commands are listed in the README and UAT checklist so future changes can be checked consistently.
