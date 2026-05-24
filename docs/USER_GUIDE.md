# Frontend User Guide

## Start The App

Run either command from the project folder:

```bash
python cli.py serve
```

or:

```bash
streamlit run app.py
```

The app opens at:

```text
http://localhost:3000
```

## Sidebar Workflow

### 1. Load Data

- `Upload CSV/XLSX/XLS`: loads your own SCM file into the current session.
- `Saved SQLite dataset`: loads a dataset you previously saved locally.
- `Use bundled sample data`: loads the offline sample workbook when no user file is selected.
- `Sheet`: appears for Excel files. Choose one sheet or `Combine all sheets`.

Uploaded files are session-only until you export or save them to SQLite.

### 2. Clean Data

- `Normalize column names`: standardizes headers so mapping and formulas work better.
- `Auto-convert dates and numbers`: parses dates, currency-like numbers, percentages, and numeric text.
- `Drop duplicate rows`: removes exact duplicate rows.
- `Missing value strategy`: keeps missing values, drops rows, fills zeroes, forward-fills, or fills median/mode.

If cleaning removes every row, the app stops with guidance so you can adjust the options.

### 3. Column Mapping

Open `Column Mapping` near the top of the page.

- Each dropdown maps your source columns to standard SCM fields.
- `Core` contains Date, Product, SKU, Supplier, Customer, Region, and Warehouse.
- Domain groups contain demand, inventory, procurement, logistics, warehouse, production, cost, planning, and advanced fields.
- `Mapping profile name` names the reusable mapping.
- `Save mapping` stores the mapping locally in SQLite.
- `Import mapping template JSON` loads a previously exported mapping template.

The app still works when some fields are missing. Each module shows friendly messages when a required metric cannot be calculated.

### 4. Filters

Filters update every dashboard:

- Date range and fiscal period.
- Product, SKU, supplier, customer, region, warehouse, category.
- Carrier, route, origin, destination, incoterm, currency, UOM.
- PO status, order status, shipment status.
- Plant/site, lot/batch, planner/buyer.
- ABC/XYZ class and stockout-risk-only filter when the required fields are mapped.

### Send Feedback

Open `Send Feedback` in the sidebar.

- `Name`: optional user name.
- `Email or contact`: optional contact detail.
- `Feedback type`: General, Bug, Feature request, Data issue, Dashboard issue, or Export issue.
- `Rating`: 1 to 5.
- `Feedback`: required message.
- `Submit feedback`: saves the entry locally.

Feedback is stored offline in `data/scm_analytics_studio.sqlite`, table `user_feedback`. It can be reviewed and exported from `Data > Settings > User Feedback`.

## Main Workspaces

### Data

Use this workspace to inspect data health before making decisions.

- `Quality`: preview rows, column types, numeric summary, categorical summary, missing values, duplicates, and date ranges.
- `Settings`: mapping confidence, validation report, business calendar, audit log, user feedback, SQLite backup, saved dashboard templates, and formula glossary.
- `Smart Chart`: choose chart type, X-axis, Y-axis, color/category, and aggregation.
- `Assistant`: run local tools and guided skills on the filtered dataset.

### Planning

Use this workspace for demand, forecasting, inventory policy, and scenario work.

- `Control Tower`: executive KPIs such as OTIF, fill rate, backorders, defect rate, revenue, cost, and margin.
- `Demand & Sales`: monthly/weekly demand, product demand, region/customer demand, volatility, actual vs forecast, moving averages.
- `Forecast Accuracy`: MAPE, WAPE, bias, and forecast quality tables/charts.
- `Forecast Generation`: offline moving average, seasonal naive, and exponential smoothing forecast generation.
- `Inventory`: stock levels, ABC/Pareto, turnover, stockout frequency, slow-moving and dead-stock views.
- `Inventory Risk`: safety stock, reorder point, days remaining, excess risk, stockout risk, and ABC/XYZ segmentation.
- `Inventory Aging`: lot or SKU aging buckets, obsolete quantity, and obsolete value.
- `Scenario`: what-if sliders for service level, demand uplift, lead-time factor, and cost assumptions.

### Operations

Use this workspace for procurement, supplier, logistics, warehouse, production, and MRP execution.

- `Procurement`: supplier purchase volume, cost, lead time, on-time delivery, price trends, defects, and supplier performance.
- `PO Aging`: open commitment value, late POs, aging buckets, due dates, and PO status.
- `Supplier Scorecard`: supplier score heatmap using on-time, lead time, cost, and quality signals.
- `Contracts`: purchase price variance, contract compliance, off-contract spend, and benchmark price checks.
- `Logistics`: delivery time, freight cost, route cost, late delivery, cost per shipment, and shipment volume.
- `Carrier / Lane`: carrier scorecards, lane cost, cost/kg, cost/mile, and on-time service.
- `Warehouse`: stock by location, inbound vs outbound, picking accuracy, storage utilization, and productivity trend.
- `Warehouse Productivity`: picks/hour, accuracy, activity, worker/team productivity where fields exist.
- `Warehouse Process`: dock-to-stock, putaway, pick-pack-ship flow, SLA breach flags, and cycle timings.
- `Production`: production volume, product-wise output, downtime, capacity, defects, and planned vs actual.
- `Production Performance`: OEE-style availability/performance/quality, yield, scrap, schedule adherence.
- `MRP Lite`: basic material shortage plan from demand, inventory, open supply, and lead time.

### Finance

Use this workspace for cost and margin analytics.

- `Cost & Profitability`: total SCM cost, cost/category, product cost, supplier cost, gross margin trend.
- `Finance Bridge`: revenue, cost, freight, inventory value, GMROI, cash-to-cash inputs, and margin bridge.
- `Landed Cost`: freight allocation by units, revenue, weight, or volume and landed margin by item/customer/order.

### Exports

Use this workspace to extract offline outputs.

- `Cleaned CSV`: downloads the filtered cleaned data.
- `Cleaned Excel`: downloads the filtered cleaned data as XLSX.
- `Dashboard PDF`: downloads a PDF summary.
- `KPI CSV` / `KPI Excel`: downloads KPI tables.
- `Save cleaned data to local SQLite`: stores the current filtered dataset inside `data/scm_analytics_studio.sqlite`.
- `Download full dashboard workbook`: exports multi-sheet workbook with KPIs, mapping, validation, failed rows, and advanced tables.
- `Download chart bundle ZIP`: exports chart images as a ZIP.
- `Download metric glossary CSV`: exports KPI/formula definitions.
- `Download failed-row quarantine CSV`: exports validation issue rows.
- `Download mapping template JSON`: exports the current mapping for reuse.
- `Download PowerPoint summary`: exports a lightweight offline PPTX summary.

## Hover And Contrast Behavior

The interface uses a corporate control-room style:

- Dark sidebar and header surfaces use light text.
- Light content surfaces use dark text.
- Hovering buttons, tabs, metric panels, expanders, and workspace headers makes the target grow slightly and adds a stronger focus shadow.
- Hover states keep the same readable contrast family: dark surfaces keep light text, and light surfaces keep dark text.

This keeps text readable in both normal and hover states.
