# SCM Analytics Studio: Complete Project Report Dossier

Last updated: 2026-05-14

## Instruction For The Report-Writing LLM

This pickup file is the source document for writing a full academic project report on **SCM Analytics Studio**.

This is a **project report**, not a company internship placement report. The final report must not invent company background, office duties, organization history, workplace activity, or internship experience. It should use placeholders for missing academic details and focus on the project itself: the problem, motivation, objectives, system design, implementation, analytics depth, business usefulness, testing, limitations, and future roadmap.

Use these placeholders unless the student provides real details:

| Field | Placeholder |
|---|---|
| Student name | `[Student Name]` |
| Student ID / Registration no. | `[Student ID]` |
| Department | `[Department Name]` |
| University / Institution | `[University Name]` |
| Course / Subject | `[Course Name]` |
| Supervisor / Faculty | `[Supervisor Name]` |
| Submission date | `[Submission Date]` |

The final report should be a polished academic document of about **30-50 pages when formatted**, with title page, abstract, acknowledgement, table of contents, chapters, references, appendices, tables, diagrams, and screenshot placeholders. It should convert this dossier into paragraphs, not leave the whole report as bullet points.

## Project Identity

| Item | Details |
|---|---|
| Project name | SCM Analytics Studio |
| Subtitle | Offline Supply Chain Management Analytics Application |
| Project type | Academic software project |
| Main interface | Streamlit local web application |
| Secondary interface | Python CLI |
| Integration interfaces | Local HTTP API and MCP-style stdio server |
| Local app URL | `http://localhost:3000` |
| Project directory | `/Users/apple/scm maker/scm_analytics_studio` |
| Core language | Python |
| Data model style | Pandas dataframe analytics with optional SQLite persistence |
| Internet requirement | No external APIs are required for normal operation after dependencies are installed |

SCM Analytics Studio is a fully offline Supply Chain Management analytics application built with Python. It transforms spreadsheet-based supply chain data into decision-ready dashboards, KPI tables, charts, validation reports, and exportable summaries. The application supports CSV, XLSX, and legacy XLS files, handles multi-sheet Excel workbooks, cleans and maps messy SCM columns, calculates operational and financial KPIs, and exports results in offline formats such as CSV, Excel, PDF, PowerPoint, chart HTML/PNG, chart ZIP bundles, and SQLite backups.

The project is designed as a local SCM analytics command center. It sits between manual Excel reporting and expensive enterprise BI/ERP analytics platforms. It gives students, analysts, planners, and small or medium organizations a practical way to perform SCM analytics on local files without cloud dependency, paid dashboards, or sensitive data uploads.

## Project Vision

Supply chain data often arrives as spreadsheets from different departments, suppliers, warehouses, logistics teams, and finance teams. The same concept may appear under many different column names, such as `order_qty`, `demand_qty`, `sales_qty`, `shipment_cost`, `freight_cost`, `vendor`, `supplier`, `warehouse`, or `location`. In many organizations, analysts spend more time cleaning and reconciling files than interpreting the supply chain.

SCM Analytics Studio was created to solve that gap. Its vision is to convert messy operational files into a repeatable offline analytics workflow:

1. Load local CSV/XLSX/XLS files.
2. Clean and validate data.
3. Map inconsistent columns into standard SCM fields.
4. Apply filters and business logic.
5. Generate dashboards, KPIs, charts, and exception tables.
6. Export reports and reusable analysis artifacts.
7. Repeat the same workflow through UI, CLI, tools, skills, API, or MCP-style integration.

The project is visionary because it treats offline analytics as a first-class product requirement. Many analytics products assume cloud upload, user accounts, external APIs, or enterprise system access. SCM Analytics Studio demonstrates that a local-first Python application can still provide modern analytics features: dashboards, KPI engines, file ingestion, validation, storage, export automation, guided workflows, and integration endpoints.

## Business Importance

SCM Analytics Studio is useful because supply chain decisions are time-sensitive and data-heavy. Poor visibility can cause overstock, stockouts, late deliveries, supplier underperformance, high freight cost, weak production planning, and margin leakage. A local analytics studio reduces the delay between receiving raw operational data and making decisions.

The project helps the business in these ways:

| Business Need | How SCM Analytics Studio Helps |
|---|---|
| Faster reporting | Uploads and cleans spreadsheet files, then generates dashboards and exports without manually rebuilding reports. |
| Better visibility | Shows demand, inventory, procurement, logistics, warehouse, production, and finance KPIs in one app. |
| Fewer manual errors | Uses reusable mapping, validation rules, and fixture-tested calculations instead of ad hoc spreadsheet formulas. |
| Local data control | Keeps uploaded data in local memory unless users choose to save or export it. |
| Repeatable analysis | Saved mappings, CLI runs, SQLite snapshots, and report exports support repeatable workflows. |
| Better planning | Inventory risk, safety stock, reorder point, ABC/XYZ, forecasting, PO aging, and MRP-lite outputs support proactive decisions. |
| Lower tool barrier | Provides an alternative to expensive BI tools for students, SMEs, and offline users. |
| Stronger quality assurance | Fixture regression, UAT checklist, validation reports, and failed-row quarantine improve confidence in outputs. |

## User Groups And Value

| User Group | Value Provided |
|---|---|
| Executive dashboard user | Sees high-level control tower metrics such as revenue, cost, gross margin, OTIF, fill rate, perfect order rate, backorder rate, and defects. Exports PDF/PPTX summaries for fast review. |
| Supply chain analyst | Uses upload, cleaning, mapping, filters, dashboards, smart charts, and exports to reduce manual spreadsheet work. |
| Inventory planner | Reviews stockout risk, excess inventory, ABC/XYZ segmentation, safety stock, reorder point, inventory aging, dead stock, and scenario planning. |
| Procurement manager | Analyzes supplier performance, supplier scorecards, purchase cost, lead time, PO aging, contract analytics, PPV, and off-contract spend. |
| Logistics manager | Tracks carrier/lane performance, route cost, freight cost, delivery lead time, late shipment count, cost per shipment, cost per kg, and cost per mile. |
| Warehouse manager | Studies stock by location, inbound/outbound movement, storage utilization, pick accuracy, picks per hour, dock-to-stock time, process flow, and SLA breach. |
| Production planner | Reviews production volume, planned vs actual output, downtime, capacity utilization, OEE-style metrics, yield, scrap rate, schedule adherence, and MRP-lite shortage signals. |
| Finance/cost analyst | Reviews SCM cost, cost breakdown, product/supplier cost, gross margin, GMROI, landed cost, cost-to-serve, and finance margin bridge. |
| Data engineer | Uses column mapping, validation, local SQLite, CLI workflows, mapping templates, API/MCP interfaces, and export artifacts. |
| QA/test user | Uses fixture packs, offline feature checks, pytest coverage, UAT checklist, validation outputs, and regression reports. |
| Offline/local user | Can analyze local files without mandatory cloud upload or external API calls. |

## Core Objectives Achieved

SCM Analytics Studio achieves the following project objectives:

| Objective | Implementation In The Project |
|---|---|
| Build an offline SCM analytics tool | The app runs locally with Streamlit and Python, with no mandatory external API dependency. |
| Support common spreadsheet inputs | CSV, XLSX, XLS, and multi-sheet Excel workbooks are supported through Pandas, OpenPyXL, and xlrd. |
| Provide a non-technical interface | Streamlit UI presents sidebar controls, workspaces, tabs, metrics, charts, dataframes, and download buttons. |
| Provide a technical automation interface | CLI supports batch analysis, validation-only mode, exports, fixture testing, tools, skills, API server, and MCP server. |
| Clean and validate SCM data | Data cleaning normalizes headers, converts types, handles missing values, detects duplicates, and generates validation reports. |
| Solve inconsistent column naming | Auto mapping and manual mapping convert source columns into canonical SCM fields. |
| Preserve repeatability | Mapping profiles, dashboard templates, SQLite snapshots, audit logs, and CLI commands support reusable analysis. |
| Cover major SCM functions | Dashboards cover demand, inventory, procurement, logistics, warehouse, production, cost, finance, and executive views. |
| Export results offline | Exports include CSV, XLSX, PDF, PPTX, HTML, PNG, ZIP, JSON, SQLite, calendar, audit, glossary, and validation files. |
| Support testing and quality | Offline feature checks, pytest tests, UAT checklist, fixture packs, regression reports, and export validation artifacts exist. |
| Demonstrate extensibility | Local tools, JSON skills, workflow assistant, local API, and MCP-style server reuse the same analytics functions. |

## System Architecture

SCM Analytics Studio has a modular local architecture. The application is centered around Pandas dataframes and shared analytics modules. Different entry points use the same underlying logic:

- The **Streamlit UI** in `app.py` gives users an interactive local web application.
- The **CLI** in `cli.py` supports batch analysis, export automation, fixture testing, tool execution, and skill execution.
- The **local HTTP API** in `api_server.py` exposes selected operations to local clients.
- The **MCP-style stdio server** in `mcp_server.py` exposes tool and skill capabilities through JSON-RPC-style messages.
- The **modules package** contains reusable logic for loading, cleaning, mapping, KPIs, dashboards, charts, storage, reporting, tools, skills, and integrations.

The system follows this data flow:

```text
CSV/XLSX/XLS/Sample/SQLite source
        |
        v
Data loading and sheet selection
        |
        v
Cleaning: normalize headers, parse dates/numbers, handle missing values, duplicates
        |
        v
Column mapping: auto detection, manual mapping, saved profiles, templates
        |
        v
Filters: date, fiscal period, product, SKU, supplier, warehouse, statuses, ABC/XYZ, risk
        |
        v
Analytics modules: KPIs, dashboards, forecasts, risk tables, scorecards, validation
        |
        v
Charts, tables, workflow tools, skills, exports, SQLite snapshots, reports
```

The same cleaned and mapped dataframe is reused across UI tabs, CLI commands, local tools, workflow skills, API calls, and MCP-style calls. This design avoids duplicating business logic and makes the project easier to extend.

## Project File And Folder Inventory

| File / Folder | Purpose |
|---|---|
| `app.py` | Main Streamlit application. It controls page layout, sidebar data loading, cleaning settings, mapping UI, filters, workspaces, charts, feedback form, export UI, and dashboard rendering. |
| `cli.py` | Command-line interface for serving the app, analyzing files, exporting reports, validating data, generating samples, backing up/restoring SQLite, running fixture tests, running tools, running skills, and launching API/MCP servers. |
| `api_server.py` | Lightweight local HTTP API server. It exposes health, catalog, inspect, tool, and skill endpoints for local clients. |
| `mcp_server.py` | MCP-style stdio server. It exposes a local JSON-RPC-style interface for catalog, dataset inspection, tool execution, and skill execution. |
| `README.md` | Main documentation for installation, usage, CLI examples, offline use, data, dashboards, and features. |
| `docs/PICKUP.md` | This project dossier for another LLM to write a full academic project report. |
| `requirements.txt` | Python dependency list including Streamlit, Pandas, NumPy, Plotly, OpenPyXL, xlrd, Matplotlib, ReportLab, pytest/API-related dependencies where present. |
| `pytest.ini` | Pytest configuration. |
| `.streamlit/config.toml` | Streamlit configuration. It sets the app to run locally at `localhost:3000` and disables usage stat gathering. |
| `config/mcp_client_config.example.json` | Example configuration for connecting local clients to the MCP-style server. |
| `modules/data_loader.py` | Reads CSV, XLSX, and XLS files; loads sample workbooks; combines sheets; infers column types for preview. |
| `modules/data_cleaner.py` | Normalizes column names, detects date/numeric-like columns, converts types, handles missing values, drops duplicates, and summarizes data quality. |
| `modules/column_mapper.py` | Defines canonical SCM fields and keyword-based auto-mapping from uploaded columns to standard fields. |
| `modules/kpi_calculator.py` | Provides reusable KPI helper functions such as safe division, safe sums, forecast accuracy, inventory turnover, DIO, fill rate, stockout rate, supplier defect rate, capacity utilization, gross margin, and gross margin percentage. |
| `modules/chart_generator.py` | Builds Plotly charts and offline Matplotlib PNG exports. Supports line, bar, pie, scatter, histogram, box, heatmap, area, treemap, and Pareto charts. |
| `modules/reporting.py` | Builds Excel byte exports, KPI dataframes, grouped KPI dictionaries, and PDF dashboard summaries with ReportLab. |
| `modules/local_storage.py` | Manages SQLite storage for mapping profiles, dataset snapshots, audit log, dashboard templates, and user feedback. |
| `modules/advanced_features.py` | Contains advanced SCM features: executive control tower, forecast accuracy/generation, inventory risk, ABC/XYZ, inventory aging, PO aging, supplier scorecard, contract analytics, carrier/lane, warehouse process, OEE-style production, finance bridge, scenario planning, landed cost, MRP-lite, validation, glossary, and advanced exports. |
| `modules/demand_analysis.py` | Demand and sales dashboard: total demand, average demand, product/region/customer demand, volatility, actual vs forecast, moving average trends. |
| `modules/inventory_analysis.py` | Inventory dashboard: inventory value, stock level, turnover, stockout frequency, overstock count, DIO, SKU stock, Pareto/ABC, slow/dead stock. |
| `modules/procurement_analysis.py` | Procurement and supplier dashboard: procurement cost, lead time, supplier on-time rate, supplier defect rate, purchase cost trends, supplier scorecard. |
| `modules/logistics_analysis.py` | Logistics dashboard: logistics cost, delivery time, on-time delivery, late shipments, route cost, carrier performance, freight trend, shipment heatmap. |
| `modules/warehouse_analysis.py` | Warehouse dashboard: warehouse stock, inbound/outbound movement, picking accuracy, storage utilization, productivity trend. |
| `modules/production_analysis.py` | Production dashboard: production volume, average production, efficiency, defect rate, downtime, capacity utilization, planned vs actual. |
| `modules/cost_analysis.py` | Cost and profitability dashboard: total SCM cost, cost per unit, highest/lowest cost product, gross margin, cost breakdown, logistics vs procurement cost. |
| `modules/tool_registry.py` | Local tool registry. Defines callable analytics tools such as data quality, KPI snapshot, forecast, inventory risk, ABC/XYZ, aging, supplier contracts, landed cost, warehouse process, MRP-lite, calendar, and failed rows. |
| `modules/skill_registry.py` | Plugin-style skill registry. Defines guided workflows such as data quality command center, inventory planner, demand forecaster, procurement manager, and operations control tower. Loads custom JSON skills from `skills/`. |
| `modules/workflow_assistant.py` | Streamlit workflow assistant UI. Lets users run local tools and skills against the current dataframe and optionally summarize results when LLM configuration exists. |
| `modules/integration_gateway.py` | Shared helper layer for API/MCP integration. Loads datasets, applies mapping templates, serializes tool outputs, and exposes inspect/tool/skill operations. |
| `modules/fixture_accuracy.py` | Fixture accuracy and golden-metric support for checking expected outputs against generated calculations. |
| `modules/llm_client.py` | Optional local LLM summary support. Base app remains useful without LLM/API configuration. |
| `sample_data/` | Built-in sample and training datasets for demonstration and first tests. |
| `skills/inventory_exception_review.json` | Example custom skill that combines inventory risk, ABC/XYZ, and failed-row review. |
| `docs/PROJECT_REPORT.md` | Existing capability report summarizing architecture, features, workspaces, tests, UI improvements, and storage. |
| `docs/PROJECT_STRUCTURE.md` | Organized file/folder layout and project organization rules. |
| `docs/STORAGE_MAP.md` | Explains where uploads, mappings, snapshots, audit log, feedback, exports, samples, and fixtures are stored. |
| `docs/UAT_PLAN.md` | User Acceptance Testing plan for app, CLI, API, MCP, storage, exports, offline behavior, and error handling. |
| `docs/USER_GUIDE.md` | Frontend navigation guide for using the app. |
| `tests/regression/offline_feature_check.py` | Broad offline regression check for core modules, charts, exports, SQLite, and CLI commands. |
| `tests/unit/test_advanced_features.py` | Pytest coverage for advanced analytics and export parity. |
| `tests/uat/UAT_CHECKLIST.md` | Manual UAT checklist for verifying user-facing behavior. |
| `tests/fixtures/legacy/` | Original fixture pack retained for compatibility and older edge-case coverage. |
| `tests/fixtures/scm_analytics_studio_fixtures/` | Current organized fixture pack covering happy path, file formats, cleaning, mapping, forecasting, inventory, procurement, logistics, warehouse, production/MRP, finance, validation, CLI/export, and offline deployment. |
| `data/` | Runtime local storage. Includes SQLite database and local rendering cache. User data is stored here only when saved by the user. |
| `exports/` | Generated output artifacts such as cleaned data, KPI tables, PDFs, PPTX files, chart bundles, validation files, fixture reports, and SQLite backups. |

Generated artifacts such as `__pycache__/`, `.pytest_cache/`, `.DS_Store`, `.venv/`, generated export files, and runtime SQLite/cache files are not part of the source design. They are runtime, environment, or output artifacts.

## User Interface Design

The Streamlit interface is organized into workspaces instead of one long dashboard list. This makes the app easier to navigate and gives each user group a natural place to work.

| Workspace | Purpose |
|---|---|
| Data | Data preview, quality checks, mapping confidence, validation, settings, glossary, calendar, audit log, feedback, smart chart, and assistant. |
| Planning | Executive control tower, demand/sales, forecast accuracy, forecast generation, inventory, inventory risk, inventory aging, and scenario planning. |
| Operations | Procurement, PO aging, supplier scorecard, contracts, logistics, carrier/lane, warehouse, warehouse productivity, warehouse process, production, production performance, and MRP-lite. |
| Finance | Cost/profitability, finance bridge, landed cost, cost-to-serve, GMROI, and margin analysis. |
| Exports | Cleaned data, KPI tables, dashboard reports, chart bundles, workbook exports, SQLite saves, smart chart, and assistant access. |

The UI uses a dark sidebar and light dashboard body to create a control-room style interface. Sidebar filters affect all modules. Missing data states show user-friendly messages rather than hard failures.

## Data Loading And Cleaning Implementation

The loading layer accepts three file formats:

- CSV files through Pandas CSV reading.
- XLSX files through Pandas/OpenPyXL.
- Legacy XLS files through Pandas/xlrd where supported.

Excel workbooks are loaded as a dictionary of sheet name to dataframe. The user can analyze one sheet or combine all sheets. Combining sheets adds a source-sheet indicator so the origin remains visible.

Cleaning is implemented as a configurable pipeline:

- Column names are trimmed and normalized.
- Date-like columns are detected through dtype, column name keywords, and sample parsing.
- Numeric-like columns are detected through dtype, column name keywords, and sample conversion.
- Currency and percentage-like symbols are cleaned where possible.
- Missing values can be kept, dropped, filled with zero, forward/back filled, or filled with median/mode.
- Duplicate rows can be dropped when the user enables that option.
- Data quality summaries count rows, columns, duplicates, missing values, date columns, numeric columns, categorical columns, and date ranges.

This design gives non-technical users control over cleaning decisions while still automating repetitive preparation tasks.

## Column Mapping Implementation

SCM Analytics Studio uses a canonical field model. Uploaded files may use different column names, but dashboards need standard meanings such as Date, Product, SKU, Supplier, Demand, Forecast, Inventory, Cost, Revenue, Delivery Date, Carrier, Warehouse, Production Quantity, and many more.

The mapping system contains:

- A long list of expected SCM fields.
- Keyword and synonym matching for auto-mapping.
- Manual Streamlit select boxes grouped by business domain.
- Saved mapping profiles in SQLite.
- Mapping template JSON import/export.
- Mapping confidence output to show how well fields were recognized.

This system is important because real SCM data rarely follows one perfect schema. The mapping layer makes the app flexible enough to work with different suppliers, warehouses, or departments.

## Filter Implementation

Filters are applied after cleaning and mapping so every dashboard uses the same active dataset. Supported filters include:

- Date range.
- Fiscal period.
- Product and SKU.
- Supplier.
- Region.
- Warehouse.
- Customer.
- Carrier and route.
- Category.
- Lot and batch.
- Origin and destination.
- Incoterm.
- Currency.
- UOM.
- PO status.
- Order status.
- Shipment status.
- Plant and site.
- Planner and buyer.
- Stockout risk only.
- ABC/XYZ class.

This gives users a consistent drill-down experience across dashboards.

## Analytics Workspaces And Features

### Executive Control Tower

The executive control tower summarizes high-level business performance. It calculates revenue, SCM cost, gross margin percentage, OTIF, fill rate, perfect order rate, backorder rate, and supplier defect rate where mapped data exists. It also shows visual summaries such as revenue by region and cost by category.

This helps leadership see whether the supply chain is serving customers on time, controlling cost, and protecting margin.

### Demand And Sales Analytics

Demand and sales analytics include total demand, average demand, highest and lowest demand products, demand growth, monthly and weekly demand trends, product-wise demand, region-wise demand, customer-wise demand, demand volatility, actual vs forecast, and moving average demand.

This helps planners understand demand patterns and detect changes in product, region, or customer behavior.

### Forecast Generation And Forecast Accuracy

Forecast accuracy uses actual demand or sales and forecast columns to calculate MAPE, WAPE, bias, actual totals, forecast totals, and item-level error views.

Forecast generation supports offline forecasting methods:

- Moving average.
- Seasonal naive.
- Exponential smoothing.

These methods provide lightweight forecasting capability without cloud services or advanced external forecasting platforms.

### Inventory Analytics

Inventory analytics includes total inventory value, average stock level, turnover ratio, stockout frequency, overstock count, days inventory remaining/outstanding, inventory trends, SKU-wise stock, ABC/Pareto analysis, slow-moving inventory scatter, and dead-stock candidates.

Inventory risk analysis adds:

- Safety stock.
- Reorder point.
- Net stock.
- Open supply.
- Days until stockout.
- Stockout risk.
- Excess units.
- Excess value.
- ABC/XYZ segmentation.

Inventory aging uses lot, batch, receipt, last movement, quantity, and cost fields to identify aging buckets and obsolete candidates.

### Procurement And Supplier Analytics

Procurement analytics includes total procurement cost, average lead time, best/worst supplier based on on-time delivery, on-time delivery percentage, supplier defect rate, average purchase price, supplier purchase volume, supplier purchase cost, lead time comparison, supplier on-time delivery, defect rate, and supplier scorecard.

Advanced procurement features include:

- PO aging and open commitment analysis.
- Supplier scorecard heatmap.
- Contract analytics.
- Purchase Price Variance.
- Off-contract spend.

These outputs help procurement teams control supplier performance, price variance, and late purchase orders.

### Logistics And Carrier/Lane Analytics

Logistics analytics includes total logistics cost, average delivery time, on-time delivery rate, late shipment count, average cost per shipment, delivery time trends, transportation cost per route, carrier performance, freight cost over time, late delivery analysis, cost per shipment, and shipment volume heatmap.

Carrier/lane analytics adds:

- Shipments by carrier and route.
- On-time percentage by lane.
- Cost per kg.
- Cost per mile.
- Freight cost by lane.

This helps logistics managers compare carrier reliability and cost efficiency.

### Warehouse Analytics

Warehouse analytics includes total warehouse stock value, space utilization, picking accuracy, inbound stock, outbound stock, net inbound/outbound movement, stock by warehouse, inbound vs outbound movement, picking accuracy, storage utilization, and productivity trends.

Warehouse process analytics adds:

- Dock-to-stock flow.
- Putaway flow.
- Pick-pack-ship process.
- SLA breach identification.
- Picks per hour and pick accuracy.

These metrics help warehouse managers see both inventory position and process performance.

### Production And MRP-Lite Analytics

Production analytics includes total production volume, average production, production efficiency, defect rate, downtime, production volume over time, product-wise production, downtime trends, capacity utilization, defect trends, and planned vs actual production.

Production performance adds:

- Availability percentage.
- Yield percentage.
- Scrap rate.
- Schedule adherence.
- OEE-style performance.

MRP-lite creates a simple net-requirements shortage plan using mapped product/SKU, demand, inventory, open supply, and lead time fields. It is not a full ERP-grade MRP engine, but it demonstrates how shortage planning can be introduced into a local SCM analytics tool.

### Cost, Finance, Landed Cost, And Cost-To-Serve

Cost analysis includes total SCM cost, average cost per unit, highest/lowest cost product, gross margin, gross margin percentage, cost over time, cost breakdown, product-wise cost, supplier-wise cost, procurement vs logistics cost, and gross margin trends.

Finance bridge adds:

- Gross margin.
- Margin after freight.
- GMROI.
- Inventory working capital.
- Cash-to-cash indicator.

Landed cost and cost-to-serve allocate freight and logistics-related costs to products/orders using methods such as units, weight, volume, or revenue where fields are available. This makes margin analysis more realistic than using product cost alone.

### Scenario Planning

Scenario planning lets users test assumptions such as:

- Demand change percentage.
- Lead-time multiplier.
- Cost change percentage.
- Service-level assumptions.

The app compares base and what-if scenarios using risk items, excess value, and margin. This gives users an offline planning lab for exploring operational changes.

## KPI And Formula Source Material

| KPI / Formula | Business Meaning | Typical Data Needed | Use Case |
|---|---|---|---|
| OTIF | Orders delivered on time and in full | Ordered qty, shipped qty, delivery date, promised date | Executive service performance |
| Fill Rate | Fulfilled or shipped quantity divided by ordered quantity | Order qty, shipped/fulfilled qty | Customer service and supply reliability |
| Perfect Order Rate | On-time, in-full, defect-free orders | Dates, quantities, defect units | End-to-end order quality |
| Backorder Rate | Backordered quantity divided by ordered quantity | Backorder qty, order qty | Demand fulfillment risk |
| MAPE | Mean absolute percentage error | Actual demand, forecast | Forecast accuracy |
| WAPE | Total absolute error divided by total actual demand | Actual demand, forecast | Weighted forecast accuracy |
| Forecast Bias | Forecast minus actual divided by actual | Actual demand, forecast | Over/under forecasting tendency |
| ABC Segmentation | SKU classification by value contribution | SKU, demand/sales, cost/revenue | Inventory prioritization |
| XYZ Segmentation | SKU classification by demand variability | SKU, demand history | Planning stability |
| Safety Stock | Buffer stock for demand/lead-time uncertainty | Demand variability, lead time, service level | Inventory protection |
| Reorder Point | Demand during lead time plus safety stock | Average demand, lead time, safety stock | Replenishment trigger |
| Inventory Turnover | COGS divided by average inventory | COGS, average inventory | Inventory efficiency |
| DIO / Days Inventory | Days inventory remains based on turnover | Inventory turnover | Working capital analysis |
| Stockout Risk | Whether net stock is below reorder point | Inventory, open supply, demand, ROP | Shortage prevention |
| Excess Inventory | Stock above expected need threshold | Net stock, ROP, unit cost | Overstock control |
| Supplier Defect Rate | Defective units divided by total supplied units | Defective units, total units | Supplier quality |
| On-Time Delivery | Deliveries made on or before promised date | Delivery date, promised date | Supplier/logistics service |
| PPV | Actual price variance against standard/contract price | Actual price, standard/contract price, quantity | Procurement savings/leakage |
| Off-Contract Spend | Spend outside contract price/terms | Contract price, actual price, quantity | Contract compliance |
| Landed Cost | Product cost plus allocated freight/logistics cost | Product cost, freight, weight/volume/units/revenue | True product cost |
| Cost-To-Serve | Cost assigned to serving customer/product/order | Logistics, warehouse, customer/order data | Profitability analysis |
| Gross Margin | Revenue minus cost | Revenue, cost | Profitability |
| GMROI | Gross margin divided by inventory investment | Margin, inventory value | Inventory return |
| OEE-Style Performance | Availability x performance/schedule x quality | Planned time, run time, output, good qty, scrap | Production performance |
| Yield | Good quantity divided by total output | Good qty, production qty | Manufacturing quality |
| Scrap Rate | Scrap divided by output plus scrap | Scrap qty, output | Waste control |
| Schedule Adherence | Output divided by scheduled/planned quantity | Actual output, planned output | Production planning |
| Cash-To-Cash Indicator | Inventory days plus receivable days minus payable days | DIO, DSO, DPO fields or assumptions | Working capital cycle |

Some formulas are simplified or adapted for an academic offline analytics project. KPI accuracy depends on correct column mapping, available data columns, and input data quality.

## Local Storage Design

SQLite is used for local persistence. The app stores data only when users choose to save or export. Uploaded files remain in Streamlit session memory during normal use.

Local SQLite stores:

- Mapping profiles in `mapping_profiles`.
- Dataset snapshot metadata in `dataset_snapshots`.
- Saved cleaned data tables with safe table names.
- Audit history in `audit_log`.
- Dashboard templates in `dashboard_templates`.
- User feedback in `user_feedback`.

This storage approach supports privacy and repeatability. Users can save mappings for vendor/customer files, keep cleaned snapshots, export backups, and review past app actions without using a remote database.

## Workflow Assistant, Tools, And Skills

The Workflow Assistant is a local productivity layer built on top of reusable tools and skills.

Local tools include:

- `data_quality`: validation and data quality summary.
- `kpi_snapshot`: KPI table across SCM modules.
- `forecast`: generated demand forecast.
- `inventory_risk`: stockout, safety stock, reorder point, and excess risk.
- `abc_xyz`: SKU segmentation by value and variability.
- `inventory_aging`: aging and obsolete inventory analysis.
- `supplier_contracts`: PPV and contract compliance.
- `landed_cost`: landed margin and cost-to-serve allocation.
- `warehouse_process`: dock-to-stock, pick flow, and SLA breach analytics.
- `mrp_lite`: simple shortage planning.
- `business_calendar`: local business/fiscal calendar.
- `failed_rows`: invalid numeric/date row quarantine.

Built-in skills combine tools into guided workflows:

- Data Quality Command Center.
- Inventory Planner.
- Demand Forecaster.
- Procurement Manager.
- Operations Control Tower.

Custom skills can be added as JSON files under `skills/`, such as `inventory_exception_review.json`. This makes the project extensible without rewriting core code.

## Local API And MCP-Style Integration

The local API and MCP-style server show that the project is not only a Streamlit dashboard. The same local analytics engine can be exposed to other local clients.

The HTTP API supports:

- `/health`
- `/catalog`
- `/tools`
- `/skills`
- `/inspect`
- `/run-tool`
- `/run-skill`

The MCP-style server provides stdio JSON-RPC-style access to catalog, inspect, tool, and skill capabilities. This architecture makes the project ready for local automation, integration with other tools, and future AI-assisted workflows without requiring cloud services.

## CLI Capabilities

The CLI supports repeatable batch workflows. Representative commands:

```bash
python cli.py serve
python cli.py analyze --input sample_data/integrated_scm_data.csv --output-dir exports/my_run
python cli.py analyze --input sample_data/integrated_scm_data.csv --validation-only
python cli.py analyze --input sample_data/integrated_scm_data.csv --output-dir exports/latest_verify --export-workbook --export-glossary --export-audit --export-chart-zip --export-calendar --export-scenario --export-formula-audit --export-mapping-template --export-failed-rows --export-pptx
python cli.py generate-sample --output exports/generated_sample.xlsx
python cli.py backup-sqlite --output exports/scm_backup.sqlite
python cli.py restore-sqlite --input exports/scm_backup.sqlite
python cli.py test-fixtures --output-dir exports/fixture_regression
python cli.py check-fixture-accuracy --output exports/fixture_accuracy_report.json
python cli.py list-tools
python cli.py list-skills
python cli.py run-tool --tool forecast --input sample_data/integrated_scm_data.csv
python cli.py run-skill --skill inventory_planner --input sample_data/integrated_scm_data.csv
python cli.py api-server
python cli.py mcp-server
```

CLI outputs can include:

- Cleaned data CSV/XLSX.
- KPI CSV/XLSX.
- Data quality JSON.
- Column mapping JSON.
- Validation report CSV.
- Chart HTML/PNG.
- Dashboard PDF.
- Dashboard workbook.
- PowerPoint summary.
- Chart bundle ZIP.
- Metric/formula glossary.
- Audit log.
- Business calendar.
- Scenario forecast.
- Scenario landed cost.
- Mapping template.
- Failed-row quarantine.
- SQLite backup.
- Fixture regression reports.

## Export System

The export system is a major project strength. It makes the dashboards useful outside the app and supports academic demonstration, business reporting, and repeatable analysis.

Supported exports include:

- Cleaned dataset as CSV.
- Cleaned dataset as Excel.
- KPI table as CSV.
- KPI table as Excel.
- PDF dashboard summary.
- PowerPoint summary.
- Full dashboard workbook.
- Plotly chart HTML.
- Matplotlib chart PNG.
- Chart bundle ZIP.
- Metric glossary.
- Validation issue report.
- Failed-row quarantine.
- Mapping template JSON.
- Business calendar CSV.
- Audit log CSV.
- SQLite backup.
- Scenario outputs.

This matters because real analytics work rarely ends at a dashboard. Users need shareable reports, audit artifacts, validation files, and portable data extracts.

## Validation And Data Quality

The validation layer checks operational data before users trust KPIs. It detects or supports detection of:

- Missing mapped fields.
- Missing required module fields.
- Duplicate business keys.
- Invalid numeric tokens.
- Negative quantities or costs where invalid.
- Receipt before order date.
- Ship/delivery before order date.
- Late deliveries.
- Impossible lead times.
- Actual before planned production dates.
- Missing currency on cost rows.
- Mixed currency.
- Mixed UOM.
- Inconsistent SKU/product IDs.
- Blank dates in time-series modules.
- Divide-by-zero KPI inputs.
- Header-only or empty datasets.
- Failed rows for quarantine export.

This improves report trust. A dashboard without validation can hide serious data problems. SCM Analytics Studio shows both the analytics output and the quality condition of the input data.

## Testing And Quality Evidence

SCM Analytics Studio includes automated and manual quality evidence.

| Test Asset | Purpose |
|---|---|
| `tests/regression/offline_feature_check.py` | Broad offline regression check. It loads sample data, runs SCM module KPIs, creates charts, exports Excel/PDF, tests SQLite mapping/dataframe persistence, tests sparse/wrong-type data, and runs CLI commands. |
| `tests/unit/test_advanced_features.py` | Pytest coverage for advanced features and CLI/export parity. |
| `tests/uat/UAT_CHECKLIST.md` | Manual UAT checklist for app startup, upload, cleaning, mapping, filters, dashboards, exports, SQLite, CLI, API, MCP, offline behavior, and error handling. |
| `tests/fixtures/legacy/` | Original fixture pack for compatibility and edge-case checks. |
| `tests/fixtures/scm_analytics_studio_fixtures/` | Current organized fixture pack with wide coverage across file formats, analytics modules, validation, CLI/export, and offline deployment. |
| `exports/*fixture_regression*` | Generated fixture validation outputs and regression reports. |
| `exports/latest_verify/` | Example output folder containing full export artifacts such as workbook, PDF, PPTX, chart ZIP, mapping template, calendar, validation, and KPI files. |

Fixture categories include:

- Clean integrated SCM data.
- Multi-sheet workbooks.
- CSV/XLSX/XLS formats.
- Messy data.
- Mixed dates, numbers, and currencies.
- Missing and duplicate fields.
- Mapping synonyms.
- Forecasting datasets.
- Inventory risk and aging.
- Procurement and supplier scorecard data.
- Logistics shipment data.
- Warehouse operation data.
- Production and MRP data.
- Cost/finance and landed cost data.
- Bad validation data.
- CLI smoke data.
- Large datasets.
- Offline deployment and path-safety cases.

## Documentation Assets

The project includes multiple documentation files:

- `README.md` documents installation, offline use, run commands, features, CLI examples, and training data.
- `docs/PROJECT_REPORT.md` summarizes the project implementation and capabilities.
- `docs/PROJECT_STRUCTURE.md` explains file organization.
- `docs/STORAGE_MAP.md` explains where data, exports, mappings, feedback, and logs live.
- `docs/UAT_PLAN.md` defines acceptance testing.
- `docs/USER_GUIDE.md` explains frontend navigation.
- `docs/PICKUP.md` provides this LLM-ready project report dossier.

These documents show that the project was not only coded but organized, explainable, testable, and ready for academic reporting.

## Technical Stack And Rationale

| Technology | Role | Why It Fits |
|---|---|---|
| Python | Main programming language | Strong ecosystem for data analytics, automation, and local applications. |
| Streamlit | Web UI | Fast local dashboard development with forms, tabs, metrics, charts, and downloads. |
| Pandas | Data processing | Ideal for CSV/Excel ingestion, cleaning, grouping, aggregation, and KPI calculations. |
| NumPy | Numeric support | Supports efficient numeric formulas and array operations. |
| Plotly | Interactive charts | Provides dashboard-quality interactive visualizations. |
| Matplotlib | Static PNG export | Works offline as a fallback for downloadable chart images. |
| OpenPyXL | XLSX support | Enables Excel reading/writing through Pandas. |
| xlrd | Legacy XLS support | Supports older Excel file workflows where available. |
| SQLite | Local persistence | Lightweight file-based database for offline mappings, snapshots, audit logs, templates, and feedback. |
| ReportLab | PDF generation | Creates offline PDF summaries without cloud services. |
| argparse | CLI commands | Provides structured command-line workflows. |
| pytest | Automated testing | Supports repeatable verification of advanced features and exports. |
| FastAPI/Uvicorn or local HTTP server components | Local integration | Enables local API style access where configured. |

## Why The Project Is Visionary

SCM Analytics Studio is important beyond being a dashboard assignment. It demonstrates a product direction: local-first analytics for operational decision-making.

The visionary aspects are:

- **Offline-first analytics:** Sensitive supply chain data can stay on the user’s machine.
- **Spreadsheet-to-dashboard bridge:** Users can move from messy spreadsheet reporting to structured analytics without enterprise BI setup.
- **Modular SCM intelligence:** Demand, inventory, procurement, logistics, warehouse, production, and finance are connected in one local analytics environment.
- **Reusable workflows:** Mappings, CLI commands, templates, tools, skills, and exports make analysis repeatable.
- **Accessible decision support:** Students, SMEs, and non-enterprise users can experience control-tower style analytics without cloud platforms.
- **Extensible architecture:** The same analytics layer supports UI, CLI, workflow assistant, local API, and MCP-style integrations.
- **Future AI readiness:** Local tools and skill registries create a foundation for AI-assisted analytics while keeping the core app useful without LLM dependency.

This project shows how Python can turn scattered SCM spreadsheets into a practical analytics product.

## Limitations

The project has realistic limitations:

- It is primarily a local single-user application.
- It is not a full ERP, WMS, TMS, APS, or enterprise MRP replacement.
- KPI accuracy depends on input data quality and correct column mapping.
- Some formulas are simplified for academic/offline project scope.
- Large dataset performance depends on local hardware.
- Offline use still requires Python dependencies to be installed.
- Real-time system integration is outside the core scope.
- MCP/API integration is local and lightweight, not a full enterprise integration platform.
- Optional LLM summaries require explicit configuration and are not part of the base offline requirement.

## Future Roadmap

Future improvements can include:

- Desktop installer for easier non-technical deployment.
- Stronger relational multi-table model across orders, suppliers, products, shipments, inventory, BOM, and finance.
- More advanced forecasting models and forecast comparison.
- ERP/WMS/TMS import templates.
- Scheduled report generation.
- Role-based dashboard presets.
- More formula governance and formula audit controls.
- More complete BOM-based MRP.
- Multi-user support and access control.
- More anomaly detection.
- Stronger browser/UI automation tests.
- More polished AI workflow assistant.
- Integration adapters for common SCM systems.

## Suggested Final Academic Report Structure

The final report should use this structure:

1. Title Page.
2. Abstract.
3. Acknowledgement.
4. Table of Contents.
5. Chapter 1: Introduction.
6. Chapter 2: Problem Statement.
7. Chapter 3: Project Objectives.
8. Chapter 4: Requirement Analysis.
9. Chapter 5: System Design.
10. Chapter 6: Technology Stack.
11. Chapter 7: Implementation.
12. Chapter 8: KPI And Formula Coverage.
13. Chapter 9: Testing And Validation.
14. Chapter 10: Results And Discussion.
15. Chapter 11: Business Impact And Visionary Importance.
16. Chapter 12: Limitations.
17. Chapter 13: Future Improvements.
18. Chapter 14: Conclusion.
19. References.
20. Appendices.

Screenshot placeholders for the final report:

- Data upload and source selection.
- Data preview and quality summary.
- Column mapping interface.
- Mapping confidence and validation report.
- Executive control tower.
- Demand and forecast dashboard.
- Inventory risk dashboard.
- Inventory aging table.
- Supplier scorecard.
- Contract analytics or PO aging.
- Logistics carrier/lane dashboard.
- Warehouse productivity/process dashboard.
- Production performance dashboard.
- MRP-lite shortage plan.
- Finance bridge or landed cost dashboard.
- Export center.
- Workflow assistant.
- CLI output.
- Fixture regression report.

## Final Prompt To Use With Another LLM

Copy this prompt into another LLM, then paste this entire pickup file below it:

```text
You are an academic project report writer and technical documentation specialist.

Write a complete, submit-ready academic project report for the project described in the pickup file below.

Important rules:
- This is a project report, not a company internship placement report.
- Do not invent company details, office duties, organization background, or workplace experience.
- Use placeholders for student, university, supervisor, course, and submission date.
- Use a formal academic tone.
- Convert the dossier facts into polished paragraphs, tables, and report sections.
- Do not leave the report as bullet points only.
- Cover both business value and technical implementation.
- Emphasize offline-first design, local data privacy, SCM analytics, dashboards, exports, testing, business impact, and future roadmap.
- Include title page, abstract, acknowledgement, table of contents, chapters, references, appendices, KPI explanations, diagram descriptions, and screenshot placeholders.
- The final report should be detailed enough for academic submission, approximately 30-50 pages when formatted.

Now write the report using the pickup file:
```
