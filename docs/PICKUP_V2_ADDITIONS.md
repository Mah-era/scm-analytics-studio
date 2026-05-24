# SCM Analytics Studio Report Additions Pickup V2

Last updated: 2026-05-14

## Purpose

This file contains the missing technical and business details that another LLM needs in order to strengthen the project report for **SCM Analytics Studio**. Use it to add new report sections or expand weak sections in `SCM_Analytics_Studio_Final_Report_v2.docx`.

This is a **project report**, not a company internship placement report. Do not invent company background, workplace duties, office experience, organization history, or supervisor/company details.

The additions below are written as factual report-ready content. The report writer should convert them into polished academic prose, tables, diagrams, appendices, and screenshot placeholders.

## 1. Conceptual Data Model / Schema Explanation

SCM Analytics Studio is implemented mainly through Pandas dataframes rather than a fixed relational database schema. However, the application is built around a conceptual SCM data model. Explaining this model makes the project easier to understand because the dashboards, filters, mappings, KPIs, validation rules, and exports are all based on these business entities.

| Conceptual Entity | Meaning In The Project | Typical Columns / Fields | Related Features |
|---|---|---|---|
| Orders | Customer or demand-side order records used to measure demand, fulfillment, service, revenue, and late delivery behavior. | `Order ID`, `SO Number`, `Order Date`, `Date`, `Customer`, `Region`, `Order Quantity`, `Shipped Quantity`, `Fulfilled Orders`, `Total Orders`, `Order Status`, `Backorder Quantity`, `Revenue` | Demand dashboard, executive control tower, fill rate, OTIF, perfect order rate, backorder rate, revenue and margin analysis. |
| Products / SKU | Product master or item-level identity used to aggregate demand, stock, cost, production, and profitability. | `Product`, `SKU`, `Category`, `UOM`, `Unit Price`, `Unit Cost`, `Standard Cost` | Product demand, SKU stock, ABC/XYZ, stockout risk, landed cost, product cost, product profitability. |
| Suppliers | Procurement-side party data used to analyze purchase cost, lead time, on-time delivery, quality, contract performance, and defects. | `Supplier`, `Buyer`, `PO Number`, `Procurement Cost`, `Actual Price`, `Standard Price`, `Contract Price`, `Defective Units`, `Total Units`, `Lead Time`, `Received Date` | Supplier scorecard, supplier defect rate, PO aging, PPV, off-contract spend, procurement dashboard. |
| Inventory | Current or historical stock quantities and inventory value data. | `Inventory`, `Average Inventory`, `COGS`, `Open Supply`, `Open PO Quantity`, `Stockout Event`, `Last Movement Date`, `Service Level`, `Holding Cost Rate`, `Order Cost` | Inventory turnover, DIO, safety stock, reorder point, stockout risk, excess inventory, inventory aging, GMROI. |
| Shipments | Logistics movement data used to measure route, carrier, cost, and delivery performance. | `Shipment ID`, `Carrier`, `Route`, `Origin`, `Destination`, `Delivery Date`, `Promised Delivery Date`, `Shipment Status`, `Shipment Cost`, `Logistics Cost`, `Weight`, `Volume`, `Distance`, `Incoterm` | Logistics dashboard, carrier/lane scorecard, freight cost, late shipment count, cost per shipment, cost per kg, cost per mile. |
| Warehouse | Warehouse location and operational movement data used to analyze stock, storage, picking, receiving, and process flow. | `Warehouse`, `Inbound Quantity`, `Outbound Quantity`, `Space Used`, `Space Capacity`, `Picks`, `Accurate Picks`, `Worker`, `Team`, `Activity`, `Start Time`, `End Time`, `Dock Time`, `Putaway Time`, `Cycle Count Quantity`, `System Quantity` | Warehouse stock, inbound/outbound movement, storage utilization, picking accuracy, warehouse productivity, dock-to-stock, SLA breach, cycle count accuracy. |
| Production | Manufacturing or operations records used to compare planned output, actual output, capacity, downtime, scrap, and quality. | `Production Quantity`, `Planned Production`, `Capacity`, `Maximum Capacity`, `Downtime`, `Scrap Quantity`, `Good Quantity`, `Planned Time`, `Run Time`, `Schedule Quantity`, `Actual Start Date`, `Actual End Date` | Production dashboard, capacity utilization, downtime trend, OEE-style metrics, yield, scrap rate, schedule adherence. |
| Costs / Finance | Cost and revenue records used to evaluate margin, working capital, cost structure, landed cost, and cost-to-serve. | `Cost`, `Cost Category`, `Revenue`, `COGS`, `Procurement Cost`, `Logistics Cost`, `Shipment Cost`, `Average Inventory`, `Inventory`, `Currency`, `Payment Date`, `Invoice Date`, `Collection Date` | Cost dashboard, gross margin, finance bridge, GMROI, landed cost, cost-to-serve, cash-to-cash indicator. |
| Forecasts | Planning values used to compare expected demand with actual demand or sales. | `Forecast`, `Demand`, `Sales`, `Date`, `Product`, `SKU`, `Region`, `Customer` | Forecast accuracy, MAPE, WAPE, bias, actual vs forecast chart, generated forecast table. |
| Mapping Profiles | Saved reusable mappings that connect uploaded file headers to canonical SCM fields. | `name`, `source_name`, `columns_json`, `mapping_json`, `created_at`, `updated_at` in SQLite table `mapping_profiles` | Reusable column mapping, faster repeat analysis, CLI mapping profile use. |
| Dataset Snapshots | Optional saved cleaned datasets stored locally after user action. | SQLite table name, display name, row count, column count, timestamps in `dataset_snapshots`; actual cleaned table stored under a safe table name. | Saved SQLite dataset selection, offline persistence, repeatable analysis. |
| Audit Records | Local record of app and CLI actions. | `action`, `detail_json`, `created_at` in SQLite table `audit_log` | Audit trail, export history, debugging, reproducibility evidence. |
| Dashboard Templates | Saved local dashboard/template preferences. | `name`, `config_json`, `updated_at` in SQLite table `dashboard_templates` | Role preset/template reuse. |
| User Feedback | Offline feedback submitted through the sidebar form. | `name`, `contact`, `category`, `rating`, `message`, `context_json`, `created_at` in SQLite table `user_feedback` | Local product feedback, UAT improvement loop, feedback export. |

### How To Explain The Data Model In The Report

The report should state that the application uses a flexible dataframe-based design instead of forcing every user into one rigid database schema. This is appropriate because SCM source files vary widely. The canonical mapping layer acts like a semantic schema: it maps user columns into standard SCM concepts such as order, SKU, supplier, inventory, shipment, warehouse, production, and cost. SQLite is then used for local persistence of reusable metadata and optional cleaned datasets, not as the only analytics engine.

### Data Model Diagram Description

Use this diagram description in the report:

```text
Uploaded SCM Files
  -> Orders / Products / Suppliers / Inventory / Shipments / Warehouse / Production / Costs / Forecasts
  -> Canonical Column Mapping
  -> Cleaned Active Dataframe
  -> Dashboards, KPIs, Validation, Tools, Skills, Exports
  -> Optional SQLite Persistence: mappings, snapshots, audit, templates, feedback
```

## 2. UI / UX Design Rationale

The user interface is designed for a non-technical SCM analyst or planner who may be comfortable with spreadsheets but not with Python code. Streamlit was chosen because it allows Python data workflows to be converted into a local web interface with forms, sidebars, tabs, dataframes, metrics, charts, and download buttons.

| UI Element | Design Rationale | Project Use |
|---|---|---|
| Sidebar workflow | Keeps file loading, cleaning settings, mapping profiles, filters, and feedback controls in one consistent control area. | Users can load data, clean it, select mappings, apply filters, and send feedback without searching across dashboards. |
| Workspace grouping | Reduces clutter by grouping screens into Data, Planning, Operations, Finance, and Exports. | Users enter the workspace that matches their job role instead of scrolling through a long list of dashboards. |
| Tabs inside workspaces | Organizes related analytics screens under each workspace. | Planning contains demand, forecast, inventory risk, inventory aging, and scenario tabs; Operations contains procurement, logistics, warehouse, production, and MRP tabs. |
| KPI cards | Highlights important numeric indicators before charts and detailed tables. | Executives and managers can quickly read revenue, cost, margin, OTIF, fill rate, defect rate, inventory value, or risk count. |
| Filters | Gives a consistent drill-down experience across all dashboards. | Users can filter by date, fiscal period, product, SKU, supplier, warehouse, customer, carrier, route, status, lot, batch, UOM, currency, and risk class. |
| Download buttons | Makes the dashboard actionable outside the app. | Users can export CSV, Excel, PDF, PPTX, chart bundles, glossary, calendar, audit logs, mapping templates, and SQLite backup. |
| Smart chart controls | Gives users flexible exploratory analysis beyond predefined dashboards. | Users choose chart type, X-axis, Y-axis, color/category, and aggregation. |
| Local feedback form | Captures user feedback inside the local Streamlit app. | Feedback is stored locally in SQLite and can be reviewed/exported later. |
| Missing-data messages | Prevents confusing crashes when a module lacks required fields. | Empty/no-data states guide users to map the needed columns. |

### Suggested UI/UX Paragraph

SCM Analytics Studio uses a workspace-based interface because supply chain analytics is cross-functional. A procurement user should not have to search through production charts, and a finance user should not have to navigate warehouse process details first. The sidebar handles global workflow controls, while the central workspace area shows role-specific dashboards. KPI cards provide fast decision signals, Plotly charts support interactive exploration, and download buttons turn analysis into portable business artifacts. This UI design supports both quick executive review and deeper analyst investigation.

## 3. Deployment / Installation Details

The project is deployed as a local Python application. It does not require a hosted web server, SaaS account, cloud API, or external database for normal use after dependencies are installed.

| Deployment Item | Project Detail |
|---|---|
| Python environment | The app is designed for Python 3.10 or newer. A virtual environment is recommended. |
| Dependency file | `requirements.txt` lists required Python packages: Streamlit, Pandas, NumPy, Plotly, OpenPyXL, xlrd, Matplotlib, ReportLab, Kaleido, and pytest. |
| Streamlit config | `.streamlit/config.toml` sets server address to `localhost`, port to `3000`, and disables browser usage stats. |
| Local URL | The Streamlit UI runs at `http://localhost:3000`. |
| CLI serving | `python cli.py serve` starts the app through the CLI. |
| Direct Streamlit serving | `streamlit run app.py` can also start the app. |
| Local API serving | `python cli.py api-server` starts the local HTTP API, defaulting to `localhost:8765`. |
| MCP serving | `python cli.py mcp-server` starts the stdio MCP-style integration server. |
| Offline use | After package installation, the normal analytics workflow works without mandatory internet access or external APIs. |
| Future installer | A desktop installer or packaged executable would reduce setup friction for non-technical users. |

### Installation Command Sequence

Use this in the report as an example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python cli.py serve
```

On Windows, the activation command would be:

```bash
.venv\Scripts\activate
```

### Deployment Explanation Paragraph

SCM Analytics Studio is deployed as a local Python/Streamlit application. This deployment style fits the offline-first design because the user can run the app on a personal computer without publishing data to a remote server. The project includes `requirements.txt` for reproducible dependency installation and `.streamlit/config.toml` for a predictable local port. The CLI adds a second deployment path because it can launch the UI, run batch analysis, start the local API, or start the MCP-style server. A future desktop installer would make this setup easier for users who are not comfortable with Python environments.

## 4. Performance Considerations

SCM Analytics Studio uses Pandas for dataframe processing, which is appropriate for small to medium spreadsheet-based SCM datasets. This matches the project’s target use case: offline CSV/Excel analysis for students, analysts, and small or medium operational teams.

| Performance Area | Current Project Position | Future Improvement |
|---|---|---|
| File size | Pandas handles normal CSV/XLSX files and medium-size datasets well on typical local machines. | Add chunked CSV processing for very large files. |
| Large dataset behavior | Fixture pack includes large datasets such as `large_6000_rows.csv` and `large_memory_pressure_20000_rows.csv`. | Add streaming, incremental aggregation, or DuckDB/SQLite-backed analytics. |
| Dashboard responsiveness | Streamlit and Pandas are suitable for interactive dashboards when row counts are moderate. | Add caching for repeated transformations and chart-ready aggregates. |
| Export performance | CSV/XLSX/PDF/PPTX/chart exports depend on local CPU, memory, and rendering libraries. | Add progress indicators, export queues, and optional background export jobs. |
| Memory usage | Dataframes are held in memory during interactive analysis. | Add file-size warnings and memory-budget checks. |
| Chart rendering | Plotly is interactive; Matplotlib/Kaleido supports offline image generation. | Add blank-chart visual checks and optimized chart aggregation for large categories. |

### Performance Paragraph

The application is intentionally designed for local spreadsheet analytics rather than enterprise-scale distributed processing. Pandas provides a strong balance between simplicity, speed, and expressiveness for the target dataset sizes. The fixture pack includes large-file tests to make sure the system can handle more demanding cases, but very large enterprise datasets would require future optimizations such as chunked processing, database-backed analytics, caching, or pre-aggregation.

## 5. Error Handling And User Feedback

The app includes error handling and user-friendly states so that incomplete or messy data does not immediately break the workflow.

| Error / Edge Case | Current Handling Approach | Report Explanation |
|---|---|---|
| Unsupported file type | Loader accepts only CSV, XLSX, and XLS; unsupported extensions raise a clear error. | Protects the app from trying to parse non-tabular files. |
| Empty sheet or empty data after cleaning | App stops the dashboard flow and warns the user that the selected data is empty. | Prevents misleading blank dashboards. |
| Missing columns | Validation report and no-data chart messages tell users which mappings are missing. | Helps users correct column mapping instead of debugging code. |
| Invalid date values | Date conversion coerces invalid values and validation checks flag impossible date relationships. | Prevents bad dates from silently corrupting lead time or delivery KPIs. |
| Invalid numeric values | Numeric conversion coerces invalid tokens; validation and failed-row quarantine identify problem rows. | Makes bad numeric input visible. |
| Wrong mappings | Mapping editor allows manual override; mapping confidence highlights weak mappings. | Reduces risk from inconsistent source headers. |
| No-data chart states | Chart generator returns empty figures with explanatory messages. | Keeps the UI stable when fields are unavailable. |
| Export failures | Export logic catches unsupported PNG/chart selections where applicable and reports unavailable exports. | Helps users understand export limitations. |
| SQLite save/load issues | Saved dataset and mapping actions are wrapped in user-facing success/error messages. | Protects local persistence workflows. |
| Legacy XLS limitations | XLS support depends on local xlrd/Pandas compatibility. | The fixture runner can record failures cleanly in regression reports. |

### Error Handling Paragraph

Error handling is especially important in SCM Analytics Studio because uploaded spreadsheets may be incomplete, inconsistent, or incorrectly formatted. Instead of assuming perfect data, the application uses validation reports, missing-field messages, failed-row quarantine, safe division, no-data chart states, and manual mapping controls. This design supports gradual correction: users can load imperfect data, see what is wrong, fix mappings or cleaning options, and still analyze the usable parts of the dataset.

## 6. Formula Assumptions And Caveats

The report should avoid overclaiming formula precision. Some KPIs are direct calculations, while others depend on mapped columns, optional fields, or simplified assumptions suitable for an academic offline analytics project.

| Formula / KPI Group | Status | Data Dependency | Caveat To State In Report |
|---|---|---|---|
| Revenue, cost, gross margin | Mostly direct | `Revenue`, `Cost`, `COGS`, `Procurement Cost`, `Logistics Cost` | Accuracy depends on whether source costs are complete and consistently mapped. |
| Fill rate | Direct when order and shipped quantities exist | `Order Quantity`, `Shipped Quantity`, `Fulfilled Orders`, `Total Orders` | Falls back to available mapped quantity fields. |
| OTIF | Direct/simplified | `Delivery Date`, `Promised Delivery Date`, ordered quantity, shipped quantity | Assumes mapped dates and quantities represent final delivery performance. |
| Perfect order rate | Simplified | OTIF fields plus `Defective Units` | True perfect order may also require damage, documentation, invoice, and claim data that may not exist. |
| Backorder rate | Direct if backorder quantity exists | `Backorder Quantity`, ordered quantity | Cannot be meaningful if backorder field is absent. |
| MAPE/WAPE/Bias | Direct with forecast and actual demand | `Demand` or `Sales`, `Forecast` | Zero actual demand must be handled carefully for percentage error. |
| Forecast generation | Simplified offline methods | Historical date/demand data | Moving average, seasonal naive, and exponential smoothing are lightweight methods, not enterprise demand planning models. |
| ABC/XYZ | Implemented from value and variability | SKU/Product, demand/sales, cost/revenue | Classification thresholds are standard/simple and depend on available value fields. |
| Safety stock and reorder point | Simplified planning formula | Demand, lead time, service level, inventory | Assumes demand variability and lead time are represented in the uploaded dataset. |
| Inventory turnover / DIO | Direct if COGS and average inventory exist | `COGS`, `Average Inventory`, `Inventory` | May use available inventory fields when average inventory is missing. |
| Supplier defect rate | Direct | `Defective Units`, `Total Units` | Requires supplier quality fields. |
| PPV and off-contract spend | Direct if price fields exist | `Actual Price`, `Standard Price`, `Contract Price`, quantity | Depends on correct contract/standard price data. |
| Landed cost | Allocation-based | Product cost, freight/logistics cost, units/weight/volume/revenue | Allocation method changes result; the report should state selected method. |
| Cost-to-serve | Allocation-based | Customer/order, logistics, warehouse, cost data | Simplified if full service-cost structure is unavailable. |
| Warehouse productivity/process | Direct if timestamps exist | Picks, accurate picks, start/end/dock/putaway times | Some process metrics require optional timestamp fields. |
| OEE-style production | Simplified | Planned time, run time, output, good quantity, scrap, schedule quantity | Called OEE-style because full manufacturing OEE may need more detailed downtime and ideal cycle-time data. |
| MRP-lite | Simplified shortage logic | SKU/product, demand, inventory, open supply, lead time, BOM-like fields where available | Not a full ERP-grade MRP engine; suitable for shortage signal demonstration. |
| Cash-to-cash indicator | Simplified | Inventory, COGS, payment/invoice/collection dates where available | Full C2C requires DIO, DSO, and DPO data; fallback assumptions may be used. |

### Formula Governance Paragraph

The report should state that SCM Analytics Studio includes a formula glossary and validation layer to reduce misuse. KPI values are decision-support indicators, not guaranteed ERP-certified accounting records. The quality of each KPI depends on the availability and correctness of mapped source columns. This transparency is important because supply chain dashboards can influence operational and financial decisions.

## 7. Appendix Material To Add

The final report should add or expand appendices so the project looks complete and verifiable.

### Appendix: Full CLI Command List

```bash
python cli.py serve
python cli.py analyze --input sample_data/integrated_scm_data.csv --output-dir exports/my_run
python cli.py analyze --input sample_data/integrated_scm_data.csv --validation-only
python cli.py analyze --input sample_data/integrated_scm_data.csv --output-dir exports/latest_verify --chart-formats html,png --export-workbook --export-pptx --export-glossary --export-audit --export-chart-zip --export-calendar --export-scenario --export-formula-audit --export-mapping-template --export-failed-rows
python cli.py analyze --input sample_data/integrated_scm_data.csv --save-sqlite cleaned_snapshot
python cli.py analyze --sqlite-table cleaned_snapshot --output-dir exports/sqlite_run
python cli.py analyze --input sample_data/integrated_scm_data.csv --save-mapping sample_profile
python cli.py analyze --input sample_data/integrated_scm_data.csv --mapping-profile sample_profile
python cli.py analyze --input sample_data/integrated_scm_data.csv --mapping-template exports/latest_verify/mapping_template.json
python cli.py analyze --input sample_data/integrated_scm_data.csv --map Demand=demand_qty --map Date=order_date
python cli.py list-saved
python cli.py generate-sample --output exports/generated_sample.xlsx
python cli.py backup-sqlite --output exports/scm_backup.sqlite
python cli.py restore-sqlite --input exports/scm_backup.sqlite
python cli.py test-fixtures --manifest tests/fixtures/scm_analytics_studio_fixtures/00_manifest/manifest.csv --output-dir exports/fixture_regression
python cli.py test-fixtures --manifest tests/fixtures/scm_analytics_studio_fixtures/00_manifest/manifest.csv --output-dir exports/fixture_regression --strict
python cli.py check-fixture-accuracy --fixture-root tests/fixtures/scm_analytics_studio_fixtures --output exports/fixture_accuracy_report.json
python cli.py list-tools
python cli.py list-skills
python cli.py run-tool --tool forecast --input sample_data/integrated_scm_data.csv --output-dir exports/tool_run
python cli.py run-tool --tool inventory_risk --input sample_data/integrated_scm_data.csv --output-dir exports/tool_run
python cli.py run-skill --skill inventory_planner --input sample_data/integrated_scm_data.csv --output-dir exports/skill_run
python cli.py api-server --host localhost --port 8765
python cli.py mcp-server
```

### Appendix: Full Export Artifact List

- `cleaned_scm_data.csv`
- `cleaned_scm_data.xlsx`
- `scm_kpi_table.csv`
- `scm_kpi_table.xlsx`
- `scm_dashboard_summary.pdf`
- `scm_summary.pptx`
- `scm_dashboard_workbook.xlsx`
- `chart_bundle.zip`
- Individual chart `.html` files.
- Individual chart `.png` files.
- `data_quality_summary.json`
- `data_quality_issue_report.csv`
- `failed_row_quarantine.csv`
- `metric_glossary.csv`
- `mapping_template.json`
- `column_mapping.json`
- `business_calendar.csv`
- `audit_log.csv`
- `scenario_forecast.csv`
- `scenario_landed_cost.csv`
- SQLite backup files.
- Fixture regression validation CSV files.
- Fixture regression summary reports.
- Tool/skill output CSV files.

### Appendix: Full Fixture Category List

| Fixture Category | Example Files | Purpose |
|---|---|---|
| Manifest | `00_manifest/manifest.csv`, `manifest.json`, `pack_summary.json` | Defines fixture pack coverage and metadata. |
| Happy path | `clean_integrated_scm.csv`, `clean_multisheet_scm.xlsx`, `full_integrated_dataset.csv` | Clean baseline data for dashboard smoke tests. |
| File formats | `clean_csv_upload.csv`, `multi_sheet_workbook.xlsx`, `legacy_xls_upload.xls`, `empty_sheet_workbook.xlsx`, `header_only_sheet.xlsx` | Verifies supported file formats and empty/edge workbook behavior. |
| Data cleaning | `mixed_dates_numbers_currency.csv`, `invalid_numeric_tokens.csv`, `missing_duplicate_space_case.csv`, `blank_required_fields.csv` | Tests cleaning and validation of messy data. |
| Mapping | `standard_columns.csv`, `synonym_columns.csv`, `duplicate_ambiguous_headers.csv`, `invalid_mapping_scenario.csv`, `mapping_template.json` | Tests auto mapping, manual mapping needs, and template use. |
| Demand forecasting | `seasonal_demand.csv`, `sparse_demand.csv`, `volatile_demand_forecast_bias.csv`, `actual_vs_forecast_metrics.csv` | Tests forecast accuracy and demand patterns. |
| Inventory | `inventory_risk_abc_xyz.csv`, `inventory_aging_lots.csv`, `stockout_overstock_slow_dead.csv` | Tests ABC/XYZ, safety stock, reorder point, aging, stockout and excess risk. |
| Procurement | `procurement_pos_supplier_scorecard.csv`, `po_aging_statuses.csv`, `off_contract_ppv.csv` | Tests supplier scorecards, PO aging, PPV, and off-contract spend. |
| Logistics | `shipments_carrier_lane.csv`, `incoterm_currency_mixed.csv` | Tests carrier/lane, freight, incoterm, and currency cases. |
| Warehouse | `warehouse_locations_stock.csv`, `warehouse_ops_sla_cycle_count.csv` | Tests warehouse stock, process SLA, picking, and cycle count data. |
| Production/MRP | `production_oee.csv`, `bom_mrp_shortage.csv` | Tests OEE-style production and shortage planning. |
| Cost/finance | `cost_finance_landed.csv`, `freight_allocation_methods.csv`, `mixed_currency_costs.csv` | Tests margin, GMROI, landed cost, cost-to-serve, and currency cases. |
| Validation bad data | `bad_data_validation.csv`, `divide_by_zero_inputs.csv`, `invalid_ids_mixed_uom.csv`, `orphan_rows_multisheet.xlsx` | Tests validation rules and bad input resilience. |
| CLI/export | `cli_smoke_small.csv`, `large_6000_rows.csv`, `export_roundtrip.csv`, `golden_kpis.json`, `sqlite_seed.db`, `batch_regression_set.json` | Tests CLI, export, golden KPIs, SQLite backup/restore, and batch regression. |
| Offline deployment | `large_memory_pressure_20000_rows.csv`, `cross_platform_path_safe.csv`, `local_paths_unicode.csv`, `weird filename with spaces & unicode Ω.csv` | Tests large files, path safety, Unicode filenames, and offline deployment robustness. |

### Appendix: Full Module List

- Root entry points: `app.py`, `cli.py`, `api_server.py`, `mcp_server.py`.
- Data modules: `data_loader.py`, `data_cleaner.py`, `column_mapper.py`.
- Analytics modules: `demand_analysis.py`, `inventory_analysis.py`, `procurement_analysis.py`, `logistics_analysis.py`, `warehouse_analysis.py`, `production_analysis.py`, `cost_analysis.py`, `advanced_features.py`.
- Supporting modules: `kpi_calculator.py`, `chart_generator.py`, `reporting.py`, `local_storage.py`.
- Integration/workflow modules: `tool_registry.py`, `skill_registry.py`, `workflow_assistant.py`, `integration_gateway.py`, `fixture_accuracy.py`, `llm_client.py`.

### Appendix: Screenshot Catalogue

The report should add screenshots for:

- App startup at `localhost:3000`.
- Sidebar data loading controls.
- Data preview and quality summary.
- Column mapping editor.
- Mapping confidence table.
- Validation report and failed-row quarantine.
- Executive control tower.
- Demand and forecast dashboard.
- Inventory risk and ABC/XYZ dashboard.
- Inventory aging table.
- Supplier scorecard.
- Contract analytics / PPV.
- PO aging.
- Logistics carrier/lane dashboard.
- Warehouse productivity and process dashboard.
- Production performance dashboard.
- MRP-lite shortage plan.
- Finance bridge.
- Landed cost / cost-to-serve.
- Scenario planning.
- Export center.
- Workflow Assistant.
- CLI `analyze` output.
- CLI `test-fixtures` output.
- Local API request/response example.
- MCP-style command or JSON example.
- SQLite saved dataset/mapping evidence.

### Appendix: UAT Checklist Summary

The UAT appendix should summarize:

- Environment setup.
- App startup.
- Sample data load.
- CSV/XLSX/XLS upload.
- Multi-sheet workbook selection.
- Cleaning options.
- Manual and auto mapping.
- Saved mapping profile.
- Filters.
- Data workspace.
- Planning workspace.
- Operations workspace.
- Finance workspace.
- Export center.
- Workflow assistant.
- CLI commands.
- API server.
- MCP server.
- SQLite save/backup/restore.
- Offline behavior.
- Error handling.

### Appendix: Known Limitations Table

| Limitation | Impact | Mitigation / Future Work |
|---|---|---|
| Local single-user design | Not suitable as a multi-user enterprise platform yet. | Add authentication, roles, and shared database support. |
| Dependency setup | Non-technical users must install Python packages. | Build desktop installer or packaged executable. |
| Large datasets | Very large data may strain memory. | Add chunking, caching, DuckDB/SQLite analytics, or database-backed aggregation. |
| Formula simplification | Some KPIs are planning approximations rather than ERP-certified calculations. | Add formula audit, configuration, and stronger source-data requirements. |
| Mapping dependency | Wrong mapping can produce wrong KPIs. | Use mapping confidence, manual review, saved profiles, and validation. |
| Legacy XLS variability | Old `.xls` parsing depends on local engine compatibility. | Keep clear error handling and support conversion to XLSX/CSV. |
| No real-time ERP integration | Current workflow is file-based/local. | Add ERP/WMS/TMS import connectors or adapters. |
| Optional LLM boundary | AI summaries require explicit configuration. | Keep base app fully useful without LLM; add local model support later. |

## 8. Risk And Mitigation Table

| Risk | Why It Matters | Mitigation In Current Project | Future Improvement |
|---|---|---|---|
| Wrong column mapping | KPIs and dashboards depend on correct semantic field mapping. | Auto mapping, manual mapping editor, mapping confidence, saved profiles, mapping templates. | Add stronger semantic validation and warning scores. |
| Bad data quality | Invalid dates/numbers or missing fields can mislead decisions. | Data quality summary, validation report, failed-row quarantine, missing-field guidance. | Add row-level correction workflow. |
| Large files | Memory and dashboard responsiveness may degrade. | Fixture pack includes large-file tests; Pandas handles medium-size files well. | Chunked processing, caching, database-backed analytics. |
| Dependency setup friction | Python setup can be difficult for non-technical users. | `requirements.txt`, Streamlit config, CLI serve command. | Desktop installer. |
| Formula misuse | Users may over-trust simplified KPIs. | Formula glossary, validation, caveat wording, mapped-column dependency. | Formula audit dashboard and configurable assumptions. |
| Export failure | Reports may be needed outside the app. | Multiple export formats, export validation fixtures, CLI export options. | Add export health checks and visual report QA. |
| Privacy concern | SCM data can contain sensitive supplier/customer/cost data. | Offline-first design, local memory/session handling, local SQLite only when user saves. | Add encryption or password protection for saved SQLite backups. |
| Real-time expectations | Users may expect live ERP updates. | Report clearly states file-based local scope. | Future ERP/WMS/TMS adapters. |

## 9. Security And Privacy Section

SCM Analytics Studio is designed around local-first privacy. Uploaded files remain in Streamlit session memory during normal use. Data is written to disk only when the user chooses to save a cleaned dataset, save a mapping, submit feedback, export a file, or create a SQLite backup. No mandatory cloud upload is required for core analysis.

Sensitive SCM data can include supplier names, purchase prices, customer demand, warehouse stock, logistics costs, production output, and margin data. A local-first architecture reduces exposure because the data does not need to leave the user’s machine. SQLite persistence is local, exports are user-initiated, and optional LLM summaries are not required for the base application.

Privacy-related design choices:

- Local app URL: `localhost:3000`.
- Local SQLite database: `data/scm_analytics_studio.sqlite`.
- User-controlled exports in `exports/` or browser download location.
- No external APIs required by default.
- Optional LLM summaries only when explicitly configured.
- Local API and MCP-style server are intended for local clients, not public internet deployment.

## 10. System And Data-Flow Diagram Notes

### System Architecture Diagram

```text
User
  |
  +--> Streamlit UI (app.py)
  |
  +--> CLI (cli.py)
  |
  +--> Local API (api_server.py)
  |
  +--> MCP-style Server (mcp_server.py)
          |
          v
Shared Modules
  - data_loader.py
  - data_cleaner.py
  - column_mapper.py
  - kpi_calculator.py
  - chart_generator.py
  - advanced_features.py
  - reporting.py
  - local_storage.py
  - tool_registry.py
  - skill_registry.py
          |
          v
Outputs
  - Dashboards
  - Charts
  - KPI tables
  - Validation reports
  - CSV/XLSX/PDF/PPTX/ZIP exports
  - SQLite mappings/snapshots/audit/feedback
```

### Data Flow Diagram

```text
Input file / sample data / SQLite table
        |
        v
Read CSV/XLSX/XLS and choose sheet
        |
        v
Clean dataframe
        |
        v
Auto-map and manually map canonical SCM fields
        |
        v
Apply sidebar/CLI filters
        |
        v
Calculate KPIs, validation, charts, tools, skills
        |
        v
Display dashboards and generate exports
        |
        v
Optional local SQLite save / backup / audit trail
```

### CLI/API/MCP Integration Diagram

```text
CLI command / HTTP request / MCP JSON message
        |
        v
integration_gateway.py
        |
        v
load_dataset() -> clean_data() -> auto_map_columns()
        |
        v
run_tool() or run_skill()
        |
        v
serialized table preview + summary output
```

## 11. Algorithm Pseudocode

### Data Loading And Analysis Pipeline

```text
function analyze_source(source):
    sheets = read_file(source)
    selected_data = choose_sheet_or_combine(sheets)
    cleaned = clean_data(selected_data, cleaning_options)
    mapping = auto_map_columns(cleaned)
    mapping = apply_saved_profile_or_manual_overrides(mapping)
    filtered = apply_filters(cleaned, mapping)
    validation = validation_report(filtered, mapping)
    kpis = get_all_kpis(filtered, mapping)
    charts = build_dashboard_charts(filtered, mapping)
    exports = generate_selected_exports(filtered, mapping, kpis, validation)
    return dashboard_outputs, exports
```

### Auto Column Mapping

```text
function auto_map_columns(dataframe):
    for expected_field in canonical_scm_fields:
        candidates = field_name_keywords(expected_field)
        if exact normalized column match exists:
            map expected_field to column
        else if partial keyword match exists:
            map expected_field to closest column
        else:
            leave expected_field unmapped
    return mapping
```

### Validation Report

```text
function validation_report(dataframe, mapping):
    issues = []
    check missing required mapped fields
    check duplicate business keys
    check negative quantities or costs where invalid
    check invalid numeric tokens
    check impossible date order
    check missing or mixed currency
    check mixed UOM
    check SKU/product inconsistency
    check divide-by-zero KPI inputs
    return issues as dataframe
```

### Forecast Generation

```text
function generated_forecast_table(dataframe, method):
    aggregate historical demand by date or period
    if method is moving average:
        forecast next periods using rolling average
    if method is seasonal naive:
        forecast using same prior seasonal period
    if method is exponential smoothing:
        forecast using weighted smoothing parameter alpha
    return forecast table
```

### Inventory Risk

```text
function inventory_risk_table(dataframe):
    group data by SKU or Product
    calculate average demand
    calculate demand standard deviation
    calculate average lead time
    safety_stock = service_z * std_demand * sqrt(lead_time)
    reorder_point = average_demand * lead_time + safety_stock
    net_stock = inventory + open_supply
    stockout_risk = net_stock < reorder_point
    excess_units = max(net_stock - 2 * reorder_point, 0)
    return item-level risk table
```

### Landed Cost Allocation

```text
function landed_cost_table(dataframe, method):
    choose allocation basis: units, weight, volume, or revenue
    calculate each line share of total basis
    allocated_freight = total_freight * line_share
    landed_cost = product_cost + allocated_freight
    landed_margin = revenue - landed_cost
    return line-level landed cost table
```

### MRP-Lite Shortage Planning

```text
function mrp_lite_table(dataframe):
    group by SKU or component
    gross_requirement = demand or planned production requirement
    available_supply = inventory + open_supply
    net_shortage = max(gross_requirement - available_supply, 0)
    shortage_risk = net_shortage > 0
    return shortage plan
```

## 12. CLI/API/MCP Examples For Report

### CLI Analyze Example

```bash
python cli.py analyze --input sample_data/integrated_scm_data.csv --output-dir exports/my_run
```

Expected output description:

```text
The command loads the input dataset, cleans it, auto-maps columns, calculates KPIs, creates validation outputs, exports charts, and writes files into exports/my_run.
```

### CLI Tool Example

```bash
python cli.py run-tool --tool inventory_risk --input sample_data/integrated_scm_data.csv --output-dir exports/tool_run
```

Expected output description:

```text
The command runs only the inventory risk tool and exports a focused table with safety stock, reorder point, days until stockout, stockout risk, and excess value.
```

### Local API Example

Example request concept:

```text
POST /run-tool
{
  "input_path": "sample_data/integrated_scm_data.csv",
  "tool": "forecast",
  "params": {"method": "Moving average", "periods": 6}
}
```

Expected response concept:

```text
{
  "title": "Generated forecast",
  "summary": {"total_forecast": "..."},
  "columns": ["Period", "Forecast"],
  "preview": [...]
}
```

### MCP-Style Example

Example message concept:

```text
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "run_tool",
    "arguments": {
      "input_path": "sample_data/integrated_scm_data.csv",
      "tool_name": "data_quality"
    }
  }
}
```

Expected response concept:

```text
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "title": "Data quality and validation",
    "summary": {...},
    "preview": [...]
  }
}
```

## 13. Actual Test Result Evidence To Add

The report should include a small evidence table. If using the latest known project state, word it as follows:

| Verification Item | Evidence To State |
|---|---|
| Offline feature check | `tests/regression/offline_feature_check.py` verifies module KPIs, charts, Excel/PDF exports, SQLite save/load, sparse data handling, wrong-type chart handling, and CLI smoke commands. |
| Pytest coverage | `tests/unit/test_advanced_features.py` provides automated tests for advanced features and export parity. |
| Fixture regression | `python cli.py test-fixtures --manifest tests/fixtures/scm_analytics_studio_fixtures/00_manifest/manifest.csv --output-dir exports/fixture_regression` generates fixture validation outputs and a regression report. |
| Fixture accuracy | `python cli.py check-fixture-accuracy --fixture-root tests/fixtures/scm_analytics_studio_fixtures --output exports/fixture_accuracy_report.json` compares calculated metrics with golden fixture expectations. |
| Advanced export verification | CLI advanced export command generates workbook, PDF, PPTX, chart ZIP, glossary, audit log, calendar, scenario outputs, mapping template, and failed-row quarantine. |
| UAT evidence | `tests/uat/UAT_CHECKLIST.md` defines manual acceptance scenarios for app startup, data load, cleaning, mapping, workspaces, exports, CLI, API, MCP, SQLite, offline behavior, and error handling. |

Avoid inventing exact pass counts unless the current run result is available. If exact results are available, include them as factual lines such as “pytest completed with X passed” or “offline feature check passed.”

## 14. Final Instruction For The LLM Updating The Report

Use this pickup file to add missing detail to the existing v2 report. The report should not merely list these items; it should convert them into polished academic paragraphs, clear tables, diagrams, and appendices. The strongest additions should be:

1. Conceptual data model/schema explanation.
2. UI/UX design rationale.
3. Deployment and installation details.
4. Performance considerations.
5. Error handling.
6. Formula assumptions and caveats.
7. Full appendices for CLI, exports, fixtures, modules, screenshots, UAT, and limitations.
8. Risk and mitigation table.
9. Security and privacy section.
10. System/data-flow diagrams.
11. Algorithm pseudocode.
12. CLI/API/MCP examples.
13. Actual test evidence table.
