# UAT Checklist

Use this checklist before accepting a release of SCM Analytics Studio.

## Environment Acceptance

| Scenario | Steps | Expected Result |
|---|---|---|
| Install dependencies | Create a virtual environment and run `pip install -r requirements.txt`. | Dependencies install without internet use after packages are available locally/cached. |
| Start UI | Run `python cli.py serve`. | Streamlit starts on `http://localhost:3000`. |
| Health check | Open `http://localhost:3000` or run a localhost health check. | App responds and shows SCM Analytics Studio. |
| Offline mode | Disconnect internet after install and run the app. | Uploads, sample data, dashboards, exports, CLI, SQLite, and charts continue to work. |

## Data Loading Acceptance

| Scenario | Steps | Expected Result |
|---|---|---|
| Load sample workbook | Enable `Use bundled sample data`. | Integrated sample data loads without errors. |
| Upload CSV | Upload a clean CSV from `tests/fixtures/scm_analytics_studio_fixtures/01_happy_path/`. | Preview, mapping, filters, KPIs, and charts render. |
| Upload XLSX | Upload a fixture XLSX from the fixture pack. | Sheet selector appears and selected sheet loads. |
| Multi-sheet workbook | Choose `Combine all sheets`. | Sheets combine and dashboard still renders. |
| Empty/header-only sheet | Upload empty/header-only fixture. | Friendly guidance appears; app does not crash. |
| Messy headers | Upload mixed-case/spaced/snake/camel header fixtures. | Auto mapping detects common SCM columns. |

## Cleaning And Mapping Acceptance

| Scenario | Steps | Expected Result |
|---|---|---|
| Normalize headers | Toggle `Normalize column names`. | Columns become easier to map and dashboard remains stable. |
| Convert types | Toggle `Auto-convert dates and numbers`. | Dates and numeric strings parse correctly. |
| Missing values | Try each missing-value strategy. | Data preview updates and empty-data warning appears if all rows are removed. |
| Duplicate rows | Toggle `Drop duplicate rows`. | Duplicate count and row count update. |
| Save mapping | Change mappings and click `Save mapping`. | Profile appears in saved mapping dropdown in a later run. |
| Import mapping template | Export a mapping template, then import it. | Mapping dropdowns are populated from the JSON template. |

## Dashboard Acceptance

| Workspace | Checks |
|---|---|
| Data | Preview, column types, numeric/categorical summaries, missing values, validation report, mapping confidence, business calendar, audit log, and formula glossary render. |
| Planning | Control tower, demand/sales, forecast accuracy, forecast generation, inventory, inventory risk, inventory aging, and scenario planning render or show clear missing-field guidance. |
| Operations | Procurement, PO aging, supplier scorecard, contracts, logistics, carrier/lane, warehouse, warehouse productivity, warehouse process, production, production performance, and MRP-lite render or show clear missing-field guidance. |
| Finance | Cost/profitability, finance bridge, and landed cost render or show clear missing-field guidance. |
| Exports | Cleaned data, KPI table, PDF, workbook, chart ZIP, glossary, failed rows, mapping template, PPTX, and SQLite save are available. |

## Filter Acceptance

| Filter Type | Expected Result |
|---|---|
| Date range | All dashboard row counts and charts update. |
| Product/SKU/Supplier/Customer/Region/Warehouse | Selected values filter every workspace. |
| Carrier/Route/Origin/Destination | Logistics and carrier/lane views update. |
| Status filters | PO, order, and shipment status filters narrow records. |
| Lot/batch | Inventory aging and detail rows update. |
| Currency/UOM/Incoterm | Finance/logistics detail updates. |
| ABC/XYZ class | Inventory risk rows filter to selected segment. |
| Stockout risk only | Inventory-related rows narrow to risk items. |

## Export Acceptance

| Scenario | Steps | Expected Result |
|---|---|---|
| Cleaned CSV/XLSX | Use Export Center buttons. | Files download and reopen with filtered rows. |
| KPI CSV/XLSX | Use KPI export buttons. | KPI table exports with module/metric/value columns. |
| PDF summary | Download dashboard PDF. | PDF opens offline and includes quality/KPI summaries. |
| Full workbook | Download full dashboard workbook. | Workbook contains dashboard sheets, mapping, validation, failed rows, and advanced tables. |
| Chart ZIP | Download chart bundle ZIP. | ZIP opens and contains chart images. |
| PowerPoint | Download PowerPoint summary. | PPTX opens offline. |
| Mapping template | Download mapping template JSON. | JSON can be imported in a new session. |
| SQLite backup | Download SQLite backup. | Backup file exists and can be restored with CLI. |

## CLI Acceptance

| Command | Expected Result |
|---|---|
| `python cli.py analyze --output-dir exports/uat_cli` | Generates cleaned data, KPI tables, quality JSON, mapping JSON, charts, and PDF. |
| `python cli.py analyze --validation-only` | Prints validation result JSON without full exports. |
| `python cli.py test-fixtures --output-dir exports/uat_fixtures` | Processes current fixture suite and writes a pass/fail report. |
| `python cli.py check-fixture-accuracy --output exports/uat_fixture_accuracy.json` | Produces fixture accuracy JSON and passes golden KPI checks. |
| `python cli.py list-tools` | Lists local workflow tools. |
| `python cli.py list-skills` | Lists built-in and custom skills. |
| `python cli.py run-tool --tool forecast --input tests/fixtures/scm_analytics_studio_fixtures/01_happy_path/full_integrated_dataset.csv` | Writes forecast tool outputs. |
| `python cli.py run-skill --skill inventory_planner --input tests/fixtures/scm_analytics_studio_fixtures/01_happy_path/full_integrated_dataset.csv` | Writes skill outputs. |

## Integration Acceptance

| Scenario | Steps | Expected Result |
|---|---|---|
| API health | Run `python cli.py api-server` and call `/health`. | JSON health response returns `ok`. |
| API tool call | POST `/run-tool` with a fixture path and tool name. | Tool result JSON is returned. |
| MCP startup | Run `python cli.py mcp-server`. | Server accepts local stdio JSON requests. |
| Tool/skill catalog | Use API or MCP catalog calls. | Available tools and skills match the app's Workflow Assistant. |

## UX Acceptance

| Scenario | Expected Result |
|---|---|
| Light panel hover | Hover metric cards, tabs, expanders, secondary buttons, or workspace headers. | Light surfaces keep dark readable text, gain stronger focus shadow, and grow slightly. |
| Dark header hover | Hover the top control header. | Dark surface keeps light readable text, gains stronger focus shadow, and grows slightly. |
| Sidebar readability | Inspect sidebar labels and controls. | Text remains readable on dark background; input values remain dark on light controls. |
| Missing fields | Open modules with unmapped required fields. | User receives clear guidance instead of a crash. |
| Large fixture | Load large fixture files. | App remains responsive enough for manual review; CLI regression still completes. |

## Acceptance Decision

A build is acceptable when:

- The app starts at `localhost:3000`.
- Fixture regression has no failures for the current fixture pack.
- Fixture accuracy has zero tabular failures and golden KPI checks pass.
- Pytest passes.
- Streamlit smoke test passes.
- Exports open offline.
- SQLite save/load works.
- Hover contrast and grow behavior is readable in every workspace.
