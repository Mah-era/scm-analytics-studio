# SCM Maker | SCM Analytics Studio

A self-initiated local-first Supply Chain Management analytics prototype built with Python, Streamlit, Pandas, Plotly, OpenPyXL, SQLite local storage, local API/MCP-style integration entry points, plugin-style skills/tools, and PDF/export tools.

This is a local/prototype project intended to demonstrate SCM analytics, digital operations, and decision-support system thinking.

**Live Demo:** https://scm-analytics-studio.onrender.com/

This package includes:
- A Streamlit app for uploading CSV/XLSX/XLS supply chain data.
- Auto column detection and manual column mapping.
- Data cleaning and data quality reporting.
- SCM dashboards for demand, sales, inventory, procurement, logistics, warehouse, production, and cost/profitability.
- Advanced dashboards for executive control tower, forecast generation, forecast accuracy, inventory risk, inventory aging, contract analytics, supplier scorecards, PO aging, carrier/lane performance, warehouse process flow, warehouse productivity, production performance, MRP-lite planning, finance margin bridge, landed cost/cost-to-serve, scenario planning, and data quality command center.
- Smart chart generator with multiple chart types.
- KPI formulas for common SCM metrics including OTIF, fill rate, perfect order rate, backorder rate, forecast MAPE/WAPE/bias, ABC/XYZ, safety stock, reorder point, GMROI, PPV-ready columns, landed-cost-ready columns, OEE, yield, scrap, capacity, and cash-to-cash indicators.
- Local export options for cleaned data, KPI tables, chart HTML, chart PNG, PDF summary reports, and PowerPoint summaries.
- Extended local exports for full dashboard workbook, chart bundle ZIP, validation issue reports, failed-row quarantine, metric/formula glossary, mapping template import/export, calendar export, audit log export, and SQLite backup.
- Local sidebar feedback form stored in SQLite, with feedback review/export in the Data workspace.
- CLI workflow for serving, analyzing, validation-only runs, fixture regression checks, sample generation, SQLite backup/restore, saved mapping use, mapping templates, filters, and local batch-style exports.
- Workflow Assistant with local tool calling, plugin-style skills, CLI skill/tool execution, and optional LLM summaries when explicitly configured.
- MCP-style stdio server and local HTTP API for connecting the same local tools to other clients.
- Sample/training datasets containing clean, messy, missing, duplicate, delayed, stockout, dead-stock, forecast-variance, supplier-defect, downtime, and cost-overrun situations.

## Folder Structure

```text
scm_analytics_studio/
├── app.py
├── cli.py
├── api_server.py
├── mcp_server.py
├── config/
│   └── mcp_client_config.example.json
├── docs/
│   ├── PROJECT_STRUCTURE.md
│   ├── PROJECT_REPORT.md
│   ├── PICKUP.md
│   ├── STORAGE_MAP.md
│   ├── UAT_PLAN.md
│   └── USER_GUIDE.md
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── data/
├── exports/
├── modules/
│   ├── data_loader.py
│   ├── data_cleaner.py
│   ├── column_mapper.py
│   ├── kpi_calculator.py
│   ├── chart_generator.py
│   ├── demand_analysis.py
│   ├── inventory_analysis.py
│   ├── procurement_analysis.py
│   ├── logistics_analysis.py
│   ├── warehouse_analysis.py
│   ├── production_analysis.py
│   ├── cost_analysis.py
│   ├── advanced_features.py
│   ├── local_storage.py
│   ├── reporting.py
│   ├── tool_registry.py
│   ├── skill_registry.py
│   ├── workflow_assistant.py
│   └── llm_client.py
├── skills/
│   └── inventory_exception_review.json
├── sample_data/
│   ├── sample_scm_data.xlsx
│   ├── integrated_scm_data.csv
│   ├── messy_scm_training_data.csv
│   └── training_situations_catalog.csv
├── tests/
│   ├── fixtures/
│   │   ├── legacy/
│   │   │   ├── FIXTURE_MANIFEST.csv
│   │   │   ├── sample_data/
│   │   │   ├── csv/
│   │   │   ├── excel/
│   │   │   ├── cli/
│   │   │   ├── export_validation/
│   │   │   └── sqlite/
│   │   └── scm_analytics_studio_fixtures/
│   │       ├── 00_manifest/
│   │       ├── 01_happy_path/
│   │       └── ...
│   ├── regression/
│   │   └── offline_feature_check.py
│   ├── unit/
│   │   └── test_advanced_features.py
│   └── uat/
│       └── UAT_CHECKLIST.md
```

## User Modules And Features

### Data Workspace

- Data preview, inferred data types, missing values, duplicates, date ranges, numeric summaries, and categorical summaries.
- Mapping confidence and manual column mapping for standard SCM fields.
- Validation report for bad dates, invalid numeric inputs, missing required fields, mixed currency/UOM, duplicate business keys, and KPI divide-by-zero risks.
- Business calendar with fiscal period and working-day flags.
- Audit log, user feedback review/export, SQLite backup, saved dashboard templates, formula glossary, Smart Chart Generator, and Workflow Assistant.
- Sidebar `Send Feedback` form stores user feedback locally.

### Planning Workspace

- Executive control tower for OTIF, fill rate, perfect order rate, backorder rate, defects, revenue, cost, and margin.
- Demand and sales charts for monthly/weekly demand, product/region/customer demand, volatility, actual vs forecast, and moving average trends.
- Forecast accuracy with MAPE, WAPE, and bias.
- Forecast generation using offline moving average, seasonal naive, and exponential smoothing.
- Inventory analysis, ABC/XYZ segmentation, safety stock, reorder point, days remaining, stockout risk, excess risk, and inventory aging.
- Scenario planning for demand uplift, lead-time changes, service level, and cost assumptions.

### Operations Workspace

- Procurement analytics, PO aging, supplier scorecards, contract analytics, PPV, and off-contract spend.
- Logistics analytics, carrier/lane scorecards, route cost, freight cost, delivery performance, and late shipment analysis.
- Warehouse stock, inbound/outbound movement, picking accuracy, utilization, productivity, dock-to-stock, putaway, and pick-pack-ship flow.
- Production analytics, capacity utilization, downtime, defect trends, OEE-style performance, yield, scrap, schedule adherence, and MRP-lite shortage planning.

### Finance Workspace

- SCM cost trend, cost breakdown, product/supplier cost, gross margin trend, finance bridge, GMROI, landed cost, and cost-to-serve allocation.

### Exports Workspace

- Cleaned CSV/XLSX, KPI CSV/XLSX, PDF summary, PowerPoint summary, full dashboard workbook, chart bundle ZIP, metric glossary, failed-row quarantine, mapping template JSON, audit log, business calendar, and SQLite dataset save/backup.

## Frontend Navigation Guide

The full user guide is in:

```text
docs/USER_GUIDE.md
```

It explains every workspace, sidebar control, button, export, filter, mapping control, and dashboard area.

## Data Storage Locations

The complete storage map is in:

```text
docs/STORAGE_MAP.md
```

Short version:

- Uploaded files stay in Streamlit session memory unless you export or save.
- Saved mappings, cleaned SQLite snapshots, audit log, and dashboard templates are stored in `data/scm_analytics_studio.sqlite`.
- User feedback is stored in `data/scm_analytics_studio.sqlite` table `user_feedback`.
- User-generated files from CLI runs are stored in `exports/<run_name>/`.
- Browser download buttons let you choose where downloaded files land on your machine.
- Built-in sample files live in `sample_data/`.
- QA/TDD files live in `tests/fixtures/`.

## UAT

The UAT plan and checklist are stored in:

```text
docs/UAT_PLAN.md
tests/uat/UAT_CHECKLIST.md
```

They cover app startup, data import, cleaning, mapping, filters, all dashboards, exports, SQLite storage, CLI workflows, local API, MCP-style server, offline behavior, and hover contrast/grow acceptance.

## Installation

1. Install Python 3.10 or newer.
2. Open a terminal inside this folder.
3. Create a virtual environment:

```bash
python -m venv .venv
```

4. Activate it:

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Run the app:

```bash
streamlit run app.py
```

The bundled Streamlit config runs the app at:

```text
http://localhost:3000
```

You can also run the app from the CLI:

```bash
python cli.py serve
```

## Local Use

After the dependencies are installed, the core app runs locally. It does not require cloud APIs or external services for normal analysis workflows.

## Recommended First Test

Open the app and use:

```text
sample_data/sample_scm_data.xlsx
```

Try the `Integrated_SCM_Data` sheet first because it contains columns for all dashboards.

You can also run the local feature check:

```bash
python tests/regression/offline_feature_check.py
```

Run the pytest suite:

```bash
python -m pytest -q
```

## CLI Analysis

Run the full local analysis with the bundled sample workbook:

```bash
python cli.py analyze --output-dir exports/cli_sample
```

Run it with your own file:

```bash
python cli.py analyze --input path/to/your_file.xlsx --sheet Integrated_SCM_Data --output-dir exports/my_run
```

Useful CLI options:

```bash
python cli.py analyze --input data.csv --map Date=Order_Date --map Demand=Quantity --save-mapping my_profile
python cli.py analyze --mapping-profile my_profile --date-start 2026-01-01 --date-end 2026-03-31
python cli.py analyze --save-sqlite cleaned_snapshot
python cli.py list-saved
python cli.py analyze --validation-only
python cli.py test-fixtures --manifest "tests/fixtures/scm_analytics_studio_fixtures/00_manifest/manifest.csv" --output-dir exports/fixture_regression
python cli.py analyze --input data.csv --export-workbook --export-chart-zip --export-calendar --export-pptx
python cli.py analyze --input data.csv --export-mapping-template
python cli.py analyze --input data.csv --mapping-template exports/cli_sample/mapping_template.json
python cli.py generate-sample --output exports/generated_sample.xlsx
python cli.py backup-sqlite --output exports/scm_backup.sqlite
python cli.py restore-sqlite --input exports/scm_backup.sqlite
```

CLI outputs include cleaned data, KPI tables, data quality JSON, column mapping JSON, chart HTML/PNG files, and a PDF summary.

## Workflow Assistant, Skills, And Tool Calling

The app includes a dedicated `Workflow Assistant` tab. It can run local tools and guided skills against the currently filtered dataset.

Built-in tools include:

- `data_quality`
- `kpi_snapshot`
- `forecast`
- `inventory_risk`
- `abc_xyz`
- `inventory_aging`
- `supplier_contracts`
- `landed_cost`
- `warehouse_process`
- `mrp_lite`
- `business_calendar`
- `failed_rows`

Built-in skills include:

- `data_quality_command_center`
- `inventory_planner`
- `demand_forecaster`
- `procurement_manager`
- `operations_control_tower`

Custom plugin-style skills can be added as JSON files in:

```text
skills/
```

Example skill format:

```json
{
  "name": "inventory_exception_review",
  "title": "Inventory Exception Review",
  "category": "Inventory",
  "description": "Review stockout risk, SKU segmentation, and failed rows.",
  "tools": ["inventory_risk", "abc_xyz", "failed_rows"],
  "prompts": ["Review inventory exceptions"],
  "params": {}
}
```

CLI tool and skill commands:

```bash
python cli.py list-tools
python cli.py list-skills
python cli.py run-tool --input "tests/fixtures/scm_analytics_studio_fixtures/01_happy_path/full_integrated_dataset.csv" --tool forecast --params "{\"periods\": 3}" --output-dir exports/tool_run
python cli.py run-skill --input "tests/fixtures/scm_analytics_studio_fixtures/01_happy_path/full_integrated_dataset.csv" --skill inventory_planner --output-dir exports/skill_run
python cli.py api-server --host localhost --port 8765
python cli.py mcp-server
```

Local HTTP API endpoints:

- `GET /health`
- `GET /catalog`
- `GET /tools`
- `GET /skills`
- `POST /inspect`
- `POST /run-tool`
- `POST /run-skill`

Example HTTP tool call:

```bash
curl -X POST http://localhost:8765/run-tool \
  -H "Content-Type: application/json" \
  -d '{"input_path":"tests/fixtures/scm_analytics_studio_fixtures/01_happy_path/full_integrated_dataset.csv","tool":"forecast","params":{"periods":2}}'
```

MCP client configuration example:

```text
config/mcp_client_config.example.json
```

Optional LLM summaries are off by default. To enable them in CLI/environment-aware contexts:

```bash
export SCM_ENABLE_LLM=1
export OPENAI_API_KEY="your-key"
export SCM_LLM_MODEL="gpt-4o-mini"
```

The Streamlit assistant also has an optional LLM checkbox and API-key field. If disabled, it uses local deterministic summaries only.

## Training Data Included

The sample files include these data situations:
- Complete SCM transaction rows.
- Demand, forecast, and sales.
- Inventory levels, stockouts, slow-moving stock, and dead stock.
- Supplier lead time, purchase cost, on-time delivery, and defect rate.
- Logistics cost, carrier, route, promised delivery, actual delivery, and late deliveries.
- Warehouse inbound/outbound movements, space utilization, and picking accuracy.
- Production quantity, planned production, capacity, downtime, and defect tracking.
- SCM cost categories, procurement/logistics split, revenue, cost, and gross margin.
- Missing values, duplicate rows, inconsistent labels, mixed date formats, currency-like numeric strings, percentage strings, and text notes.

## Notes

- Chart PNG export uses Matplotlib so it works offline without a browser or cloud service.
- PDF export uses ReportLab.
- Excel upload/export uses OpenPyXL through Pandas, with xlrd included for legacy `.xls` files.
- SQLite stores reusable column mapping profiles and can optionally store cleaned data snapshots when you choose to save them.
