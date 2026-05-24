const EXPECTED_FIELDS = [
  "Date", "Product", "SKU", "Category", "Supplier", "Customer", "Region", "Warehouse",
  "Demand", "Forecast", "Sales", "Revenue", "Cost", "COGS", "Average Inventory",
  "Inventory", "Lead Time", "Order Date", "Delivery Date", "Promised Delivery Date",
  "Received Date", "Defective Units", "Total Units", "Shipment Cost", "Carrier", "Route",
  "Shipment ID", "Production Quantity", "Planned Production", "Capacity", "Maximum Capacity",
  "Downtime", "Inbound Quantity", "Outbound Quantity", "Space Used", "Space Capacity",
  "Picks", "Accurate Picks", "Stockout Event", "Fulfilled Orders", "Total Orders",
  "Cost Category", "Procurement Cost", "Logistics Cost", "Last Movement Date",
  "Order ID", "Order Quantity", "Shipped Quantity", "Open Quantity", "PO Status",
  "Order Status", "Shipment Status", "Due Date", "Standard Price", "Contract Price",
  "Actual Price", "Unit Price", "Weight", "Volume", "Distance", "Origin", "Destination",
  "Incoterm", "Currency", "Plant", "Site", "Lot", "Batch", "Planner", "Buyer",
  "Customer Segment", "UOM", "Open Supply", "Backorder Quantity"
];

const KEYWORDS = {
  "Date": ["date", "transaction_date", "period"],
  "Product": ["product", "parent_sku", "product_name", "item", "material"],
  "SKU": ["sku", "component_sku", "item_code", "material_code"],
  "Category": ["category", "segment"],
  "Supplier": ["supplier", "vendor"],
  "Customer": ["customer", "client"],
  "Region": ["region", "area", "zone", "location"],
  "Warehouse": ["warehouse", "warehouse_location", "wh", "depot"],
  "Demand": ["demand", "demand_qty", "order_qty", "qty_ordered"],
  "Forecast": ["forecast", "forecasted"],
  "Sales": ["sales", "sold", "sales_qty"],
  "Revenue": ["revenue", "income", "sales_value"],
  "Cost": ["cost", "total_cost", "unit_cost", "holding_cost"],
  "COGS": ["cogs", "cost_of_goods"],
  "Average Inventory": ["average_inventory", "avg_inventory"],
  "Inventory": ["inventory", "inventory_qty", "stock", "stock_level", "on_hand"],
  "Lead Time": ["lead_time", "lead_time_days", "leadtime", "delivery_time"],
  "Order Date": ["order_date", "ordered_date"],
  "Delivery Date": ["delivery_date", "actual_delivery_date", "ship_date"],
  "Promised Delivery Date": ["promised_delivery", "promised_date", "eta", "due_date"],
  "Received Date": ["received_date", "receipt_date"],
  "Defective Units": ["defective", "defects", "defective_units", "defect_qty"],
  "Total Units": ["total_units", "units_supplied", "received_qty"],
  "Shipment Cost": ["shipment_cost", "freight", "freight_cost", "transport_cost"],
  "Carrier": ["carrier", "transporter"],
  "Route": ["route", "lane"],
  "Shipment ID": ["shipment_id", "shipment"],
  "Production Quantity": ["production_quantity", "production_qty", "actual_output"],
  "Planned Production": ["planned_production", "planned_units"],
  "Capacity": ["capacity", "available_capacity"],
  "Maximum Capacity": ["maximum_capacity", "max_capacity"],
  "Downtime": ["downtime", "downtime_hours"],
  "Inbound Quantity": ["inbound", "inbound_qty", "received_qty"],
  "Outbound Quantity": ["outbound", "outbound_qty", "dispatched_qty"],
  "Space Used": ["space_used", "used_space"],
  "Space Capacity": ["space_capacity", "capacity_space"],
  "Picks": ["picks", "picked_orders"],
  "Accurate Picks": ["accurate_picks", "correct_picks"],
  "Stockout Event": ["stockout", "stockout_flag"],
  "Fulfilled Orders": ["fulfilled_orders", "fulfilled"],
  "Total Orders": ["total_orders", "orders"],
  "Cost Category": ["cost_category", "expense_category"],
  "Procurement Cost": ["procurement_cost", "purchase_cost"],
  "Logistics Cost": ["logistics_cost", "transportation_cost"],
  "Last Movement Date": ["last_movement", "last_sold", "last_issue"],
  "Order ID": ["order_id", "order_number"],
  "Order Quantity": ["order_quantity", "ordered_qty", "order_qty"],
  "Shipped Quantity": ["shipped_quantity", "shipped_qty", "ship_qty"],
  "Open Quantity": ["open_quantity", "open_qty"],
  "PO Status": ["po_status", "purchase_order_status"],
  "Order Status": ["order_status"],
  "Shipment Status": ["shipment_status", "status"],
  "Due Date": ["due_date"],
  "Standard Price": ["standard_price", "std_price"],
  "Contract Price": ["contract_price"],
  "Actual Price": ["actual_price", "po_price"],
  "Unit Price": ["unit_price", "price"],
  "Weight": ["weight", "kg"],
  "Volume": ["volume", "cube", "cbm"],
  "Distance": ["distance", "km", "miles"],
  "Origin": ["origin", "ship_from"],
  "Destination": ["destination", "ship_to"],
  "Incoterm": ["incoterm"],
  "Currency": ["currency"],
  "Plant": ["plant"],
  "Site": ["site"],
  "Lot": ["lot"],
  "Batch": ["batch"],
  "Planner": ["planner"],
  "Buyer": ["buyer"],
  "Customer Segment": ["customer_segment"],
  "UOM": ["uom", "unit_of_measure"],
  "Open Supply": ["open_supply", "open_po_qty", "inbound_qty"],
  "Backorder Quantity": ["backorder_quantity", "backorder_qty"]
};

const state = {
  sourceName: "",
  sheets: {},
  activeSheet: "",
  rawRows: [],
  rows: [],
  columns: [],
  mapping: {},
  workspace: "planning"
};

const $ = (id) => document.getElementById(id);
const nf = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });

function cleanKey(text) {
  return String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

function normalizeColumnName(text) {
  return String(text || "").trim().replace(/\s+/g, "_").replace(/^_+|_+$/g, "");
}

function parseNumber(value) {
  if (value === null || value === undefined || value === "") return NaN;
  if (typeof value === "number") return Number.isFinite(value) ? value : NaN;
  let text = String(value).trim();
  const negative = /^\(.*\)$/.test(text);
  text = text.replace(/^\((.*)\)$/, "$1")
    .replace(/[$,৳%]/g, "")
    .replace(/\b(bdt|usd|eur|gbp|inr|tk)\b/ig, "")
    .replace(/\s+/g, "");
  const parsed = Number(text);
  return Number.isFinite(parsed) ? (negative ? -parsed : parsed) : NaN;
}

function parseDate(value) {
  if (value instanceof Date && !Number.isNaN(value.getTime())) return value;
  if (typeof value === "number" && value > 20000 && value < 80000 && window.XLSX) {
    const parsed = XLSX.SSF.parse_date_code(value);
    if (parsed) return new Date(parsed.y, parsed.m - 1, parsed.d);
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function sum(rows, col) {
  if (!col) return 0;
  return rows.reduce((total, row) => {
    const value = parseNumber(row[col]);
    return total + (Number.isFinite(value) ? value : 0);
  }, 0);
}

function mean(rows, col) {
  if (!col) return 0;
  const values = rows.map((row) => parseNumber(row[col])).filter(Number.isFinite);
  return values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
}

function safeDiv(a, b) {
  return b ? a / b : 0;
}

function field(name) {
  const col = state.mapping[name];
  return col && state.columns.includes(col) ? col : null;
}

function hasCols(...cols) {
  return cols.every((col) => col && state.columns.includes(col));
}

function topCategory(rows, category, value, ascending = false) {
  if (!category || !value) return "N/A";
  const grouped = groupSum(rows, category, value);
  if (!grouped.length) return "N/A";
  grouped.sort((a, b) => ascending ? a.value - b.value : b.value - a.value);
  return grouped[0].key;
}

function groupSum(rows, keyCol, valueCol) {
  const map = new Map();
  rows.forEach((row) => {
    const key = String(row[keyCol] ?? "Blank");
    const value = valueCol ? parseNumber(row[valueCol]) : 1;
    map.set(key, (map.get(key) || 0) + (Number.isFinite(value) ? value : 0));
  });
  return Array.from(map, ([key, value]) => ({ key, value })).filter((d) => d.value !== 0);
}

function groupAgg(rows, keyCol, valueCol, agg) {
  const map = new Map();
  rows.forEach((row) => {
    const key = String(row[keyCol] ?? "Blank");
    const value = valueCol ? parseNumber(row[valueCol]) : 1;
    if (!map.has(key)) map.set(key, []);
    if (Number.isFinite(value)) map.get(key).push(value);
  });
  return Array.from(map, ([key, values]) => {
    let value = values.length;
    if (agg === "sum") value = values.reduce((a, b) => a + b, 0);
    if (agg === "average") value = values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    if (agg === "min") value = values.length ? Math.min(...values) : 0;
    if (agg === "max") value = values.length ? Math.max(...values) : 0;
    return { key, value };
  }).sort((a, b) => b.value - a.value).slice(0, 18);
}

function autoMapColumns(columns) {
  const cleaned = new Map(columns.map((col) => [cleanKey(col), col]));
  const mapping = {};
  EXPECTED_FIELDS.forEach((fieldName) => {
    const candidates = [cleanKey(fieldName), ...(KEYWORDS[fieldName] || []).map(cleanKey)];
    let match = candidates.find((candidate) => cleaned.has(candidate));
    if (match) {
      mapping[fieldName] = cleaned.get(match);
      return;
    }
    match = columns.find((col) => candidates.some((candidate) => candidate && cleanKey(col).includes(candidate)));
    mapping[fieldName] = match || "";
  });
  return mapping;
}

function cleanRows(rawRows) {
  const normalize = $("normalizeColumns").checked;
  const dropDupes = $("dropDuplicates").checked;
  const missing = $("missingStrategy").value;
  let rows = rawRows.map((row) => {
    const out = {};
    Object.entries(row).forEach(([key, value]) => {
      out[normalize ? normalizeColumnName(key) : key] = value;
    });
    return out;
  });
  let columns = Array.from(new Set(rows.flatMap((row) => Object.keys(row))));

  if ($("convertTypes").checked) {
    rows = rows.map((row) => {
      const out = { ...row };
      columns.forEach((col) => {
        const key = cleanKey(col);
        const value = out[col];
        if (value === "" || value === undefined) return;
        if (/date|day|month|year|received|ordered|promised|movement/.test(key)) {
          const date = parseDate(value);
          if (date) out[col] = date.toISOString().slice(0, 10);
        } else if (/qty|quantity|demand|sales|revenue|cost|price|inventory|stock|lead|time|defect|unit|capacity|downtime|orders|shipment|space|picks|cogs|forecast|fulfilled/.test(key) && !/id|sku|code/.test(key)) {
          const num = parseNumber(value);
          if (Number.isFinite(num)) out[col] = num;
        }
      });
      return out;
    });
  }

  if (dropDupes) {
    const seen = new Set();
    rows = rows.filter((row) => {
      const sig = JSON.stringify(row);
      if (seen.has(sig)) return false;
      seen.add(sig);
      return true;
    });
  }

  if (missing === "drop_rows") {
    rows = rows.filter((row) => columns.every((col) => row[col] !== null && row[col] !== undefined && row[col] !== ""));
  } else if (missing !== "keep") {
    const fill = {};
    columns.forEach((col) => {
      const values = rows.map((row) => row[col]).filter((v) => v !== null && v !== undefined && v !== "");
      if (missing === "fill_zero") fill[col] = 0;
      if (missing === "fill_forward") fill[col] = values[0] ?? "";
      if (missing === "fill_median_mode") {
        const nums = values.map(parseNumber).filter(Number.isFinite).sort((a, b) => a - b);
        fill[col] = nums.length ? nums[Math.floor(nums.length / 2)] : mode(values);
      }
    });
    rows = rows.map((row) => {
      const out = { ...row };
      columns.forEach((col) => {
        if (out[col] === null || out[col] === undefined || out[col] === "") out[col] = fill[col];
      });
      return out;
    });
  }

  return { rows, columns };
}

function mode(values) {
  const counts = new Map();
  values.forEach((value) => counts.set(value, (counts.get(value) || 0) + 1));
  return Array.from(counts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "";
}

function qualitySummary(rows, columns) {
  const missingByColumn = {};
  columns.forEach((col) => {
    missingByColumn[col] = rows.filter((row) => row[col] === null || row[col] === undefined || row[col] === "").length;
  });
  const duplicateRows = rows.length - new Set(rows.map((row) => JSON.stringify(row))).size;
  const numericColumns = columns.filter((col) => rows.some((row) => Number.isFinite(parseNumber(row[col]))));
  const dateColumns = columns.filter((col) => rows.some((row) => parseDate(row[col])));
  return {
    rows: rows.length,
    columns: columns.length,
    duplicateRows,
    totalMissing: Object.values(missingByColumn).reduce((a, b) => a + b, 0),
    missingByColumn,
    numericColumns,
    dateColumns
  };
}

function buildKpis(rows) {
  const demand = field("Demand");
  const forecast = field("Forecast");
  const product = field("Product");
  const inventory = field("Inventory");
  const cost = field("Cost");
  const cogs = field("COGS");
  const avgInv = field("Average Inventory");
  const stockout = field("Stockout Event");
  const supplier = field("Supplier");
  const delivery = field("Delivery Date");
  const promised = field("Promised Delivery Date") || field("Due Date");
  const defective = field("Defective Units");
  const totalUnits = field("Total Units");
  const revenue = field("Revenue");
  const procCost = field("Procurement Cost") || cost;
  const shipCost = field("Shipment Cost") || field("Logistics Cost");
  const production = field("Production Quantity");
  const capacity = field("Capacity") || field("Maximum Capacity");
  const picks = field("Picks");
  const accurate = field("Accurate Picks");
  const spaceUsed = field("Space Used");
  const spaceCapacity = field("Space Capacity");
  const inbound = field("Inbound Quantity");
  const outbound = field("Outbound Quantity");

  const onTime = hasCols(delivery, promised)
    ? rows.filter((row) => {
        const a = parseDate(row[delivery]);
        const p = parseDate(row[promised]);
        return a && p && a <= p;
      }).length
    : 0;

  const ordered = sum(rows, field("Order Quantity") || demand || "Total Orders");
  const shipped = sum(rows, field("Shipped Quantity") || field("Fulfilled Orders") || field("Sales"));
  const totalCost = sum(rows, cost);
  const totalRevenue = sum(rows, revenue);
  const turnover = safeDiv(sum(rows, cogs), mean(rows, avgInv) || mean(rows, inventory));

  return {
    planning: {
      "Total Demand": sum(rows, demand),
      "Average Demand": mean(rows, demand),
      "Forecast Accuracy %": forecastAccuracy(rows, demand, forecast) * 100,
      "Fill Rate %": safeDiv(shipped, ordered) * 100,
      "Stockout Frequency %": stockout ? safeDiv(sum(rows, stockout), Math.max(1, rows.length)) * 100 : 0,
      "Inventory Turnover": turnover,
      "High Demand Product": topCategory(rows, product, demand, false),
      "Low Demand Product": topCategory(rows, product, demand, true)
    },
    operations: {
      "Procurement Cost": sum(rows, procCost),
      "Average Lead Time": mean(rows, field("Lead Time")),
      "On-time Delivery %": safeDiv(onTime, rows.length) * 100,
      "Supplier Defect %": safeDiv(sum(rows, defective), sum(rows, totalUnits)) * 100,
      "Logistics Cost": sum(rows, shipCost),
      "Warehouse Utilization %": safeDiv(sum(rows, spaceUsed), sum(rows, spaceCapacity)) * 100,
      "Picking Accuracy %": safeDiv(sum(rows, accurate), sum(rows, picks)) * 100,
      "Production Efficiency %": safeDiv(sum(rows, production), sum(rows, capacity)) * 100
    },
    finance: {
      "Revenue": totalRevenue,
      "SCM Cost": totalCost,
      "Gross Margin": totalRevenue - totalCost,
      "Gross Margin %": safeDiv(totalRevenue - totalCost, totalRevenue) * 100,
      "Average Cost per Unit": safeDiv(totalCost, sum(rows, field("Total Units") || field("Sales"))),
      "Highest Cost Product": topCategory(rows, product, cost, false),
      "Procurement Cost": sum(rows, field("Procurement Cost")),
      "Logistics Cost": sum(rows, field("Logistics Cost"))
    },
    data: {
      "Rows": rows.length,
      "Columns": state.columns.length,
      "Mapped Fields": Object.values(state.mapping).filter(Boolean).length,
      "Numeric Columns": qualitySummary(rows, state.columns).numericColumns.length,
      "Date Columns": qualitySummary(rows, state.columns).dateColumns.length,
      "Missing Values": qualitySummary(rows, state.columns).totalMissing
    },
    exports: {
      "Cleaned Rows": rows.length,
      "KPI Groups": 3,
      "Mapped Fields": Object.values(state.mapping).filter(Boolean).length,
      "Available Sheets": Object.keys(state.sheets).length
    }
  };
}

function forecastAccuracy(rows, actualCol, forecastCol) {
  if (!actualCol || !forecastCol) return 0;
  const values = rows.map((row) => {
    const actual = parseNumber(row[actualCol]);
    const forecast = parseNumber(row[forecastCol]);
    if (!actual || !Number.isFinite(actual) || !Number.isFinite(forecast)) return null;
    return Math.max(0, Math.min(1, 1 - Math.abs(actual - forecast) / actual));
  }).filter((value) => value !== null);
  return values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
}

function validationReport(rows) {
  const issues = [];
  ["Date", "Product", "Demand", "Inventory", "Supplier", "Cost"].forEach((name) => {
    if (!field(name)) issues.push({ Severity: "Medium", Issue: `Missing mapped field: ${name}`, Rows: 1, Detail: "Map this field for richer dashboards." });
  });
  ["Demand", "Sales", "Inventory", "Cost", "Shipment Cost", "Production Quantity"].forEach((name) => {
    const col = field(name);
    if (!col) return;
    const invalid = rows.filter((row) => row[col] !== "" && row[col] !== null && row[col] !== undefined && !Number.isFinite(parseNumber(row[col]))).length;
    const negative = rows.filter((row) => parseNumber(row[col]) < 0).length;
    if (invalid) issues.push({ Severity: "High", Issue: `Invalid numeric token in ${name}`, Rows: invalid, Detail: col });
    if (negative) issues.push({ Severity: "High", Issue: `Negative ${name}`, Rows: negative, Detail: col });
  });
  const delivery = field("Delivery Date");
  const promised = field("Promised Delivery Date") || field("Due Date");
  if (delivery && promised) {
    const late = rows.filter((row) => {
      const a = parseDate(row[delivery]);
      const p = parseDate(row[promised]);
      return a && p && a > p;
    }).length;
    if (late) issues.push({ Severity: "Medium", Issue: "Late delivery", Rows: late, Detail: `${delivery} > ${promised}` });
  }
  return issues.length ? issues : [{ Severity: "Info", Issue: "No validation issues detected", Rows: 0, Detail: "" }];
}

function formatValue(value) {
  if (typeof value === "number" && Number.isFinite(value)) return nf.format(value);
  return String(value ?? "N/A");
}

function csvParse(text) {
  const rows = [];
  let row = [];
  let cell = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    const next = text[i + 1];
    if (ch === '"' && quoted && next === '"') {
      cell += '"';
      i += 1;
    } else if (ch === '"') {
      quoted = !quoted;
    } else if (ch === "," && !quoted) {
      row.push(cell);
      cell = "";
    } else if ((ch === "\n" || ch === "\r") && !quoted) {
      if (ch === "\r" && next === "\n") i += 1;
      row.push(cell);
      if (row.some((v) => v !== "")) rows.push(row);
      row = [];
      cell = "";
    } else {
      cell += ch;
    }
  }
  row.push(cell);
  if (row.some((v) => v !== "")) rows.push(row);
  const headers = rows.shift()?.map((h) => h.trim()) || [];
  return rows.map((values) => Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ""])));
}

async function loadFile(file) {
  state.sourceName = file.name;
  const ext = file.name.split(".").pop().toLowerCase();
  if (ext === "csv") {
    const text = await file.text();
    state.sheets = { CSV_Data: csvParse(text) };
  } else {
    const buffer = await file.arrayBuffer();
    const workbook = XLSX.read(buffer, { type: "array", cellDates: true });
    state.sheets = {};
    workbook.SheetNames.forEach((name) => {
      state.sheets[name] = XLSX.utils.sheet_to_json(workbook.Sheets[name], { defval: "" });
    });
  }
  populateSheets();
}

function populateSheets() {
  const names = Object.keys(state.sheets);
  const select = $("sheetSelect");
  select.innerHTML = "";
  if (names.length > 1) select.append(new Option("Combine all sheets", "__combine__"));
  names.forEach((name) => select.append(new Option(name, name)));
  const preferred = names.includes("Integrated_SCM_Data") ? "Integrated_SCM_Data" : (names.length > 1 ? "__combine__" : names[0]);
  select.value = preferred;
  applyCurrentSheet();
}

function applyCurrentSheet() {
  const selected = $("sheetSelect").value;
  state.activeSheet = selected === "__combine__" ? "Combine all sheets" : selected;
  state.rawRows = selected === "__combine__"
    ? Object.entries(state.sheets).flatMap(([sheet, rows]) => rows.map((row) => ({ ...row, source_sheet: sheet })))
    : (state.sheets[selected] || []);
  recalculate();
}

function recalculate() {
  const cleaned = cleanRows(state.rawRows);
  state.rows = cleaned.rows;
  state.columns = cleaned.columns;
  state.mapping = { ...autoMapColumns(state.columns), ...readMappingOverrides() };
  renderAll();
}

function readMappingOverrides() {
  const overrides = {};
  document.querySelectorAll("[data-map-field]").forEach((select) => {
    overrides[select.dataset.mapField] = select.value;
  });
  return overrides;
}

function renderAll() {
  $("emptyState").classList.toggle("hidden", state.rows.length > 0);
  $("appShell").classList.toggle("hidden", state.rows.length === 0);
  if (!state.rows.length) return;

  const quality = qualitySummary(state.rows, state.columns);
  $("sourceSummary").textContent = `${state.sourceName || "Current dataset"} | ${state.activeSheet} | ${nf.format(state.rows.length)} rows | ${nf.format(state.columns.length)} columns`;
  renderWorkspaceTitle();
  renderMetrics();
  renderMapping();
  renderChartControls();
  renderSmartChart();
  renderQuality(quality);
  renderValidation();
  renderDetails();
  renderPreview();
}

function renderWorkspaceTitle() {
  const titles = {
    planning: ["Planning Workspace", "Executive control, demand, inventory policy, and scenario signals."],
    operations: ["Operations Workspace", "Procurement, supplier, logistics, warehouse, and production execution."],
    finance: ["Finance Workspace", "SCM cost, margin, landed-cost, and profitability bridge."],
    data: ["Data Workspace", "Quality, mapping confidence, and chart exploration."],
    exports: ["Exports Workspace", "Portable data extracts and mapping handoff files."]
  };
  $("workspaceTitle").textContent = titles[state.workspace][0];
  $("workspaceDescription").textContent = titles[state.workspace][1];
}

function renderMetrics() {
  const metrics = buildKpis(state.rows)[state.workspace] || {};
  $("metricGrid").innerHTML = Object.entries(metrics).slice(0, 8).map(([label, value]) => `
    <div class="metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(formatValue(value))}</strong></div>
  `).join("");
}

function renderMapping() {
  const panel = $("mappingPanel");
  const options = [`<option value="">-- Not mapped --</option>`, ...state.columns.map((col) => `<option value="${escapeAttr(col)}">${escapeHtml(col)}</option>`)].join("");
  panel.innerHTML = EXPECTED_FIELDS.map((fieldName) => `
    <label>${escapeHtml(fieldName)}
      <select data-map-field="${escapeAttr(fieldName)}">${options}</select>
    </label>
  `).join("");
  panel.querySelectorAll("[data-map-field]").forEach((select) => {
    select.value = state.mapping[select.dataset.mapField] || "";
    select.addEventListener("change", () => {
      state.mapping[select.dataset.mapField] = select.value;
      renderAll();
    });
  });
}

function renderChartControls() {
  const x = $("chartX");
  const y = $("chartY");
  x.innerHTML = state.columns.map((col) => `<option value="${escapeAttr(col)}">${escapeHtml(col)}</option>`).join("");
  y.innerHTML = [`<option value="">Count rows</option>`, ...state.columns.filter((col) => state.rows.some((row) => Number.isFinite(parseNumber(row[col])))).map((col) => `<option value="${escapeAttr(col)}">${escapeHtml(col)}</option>`)].join("");
  x.value = field("Date") || field("Product") || state.columns[0] || "";
  y.value = field("Demand") || field("Revenue") || field("Cost") || "";
}

function renderSmartChart() {
  const type = $("chartType").value;
  const x = $("chartX").value || state.columns[0];
  const y = $("chartY").value;
  const agg = $("chartAgg").value;
  let data = groupAgg(state.rows, x, y, agg);
  if (type === "pareto") {
    data = groupAgg(state.rows, x, y, "sum");
    renderPareto(data, "smartChart");
  } else if (type === "pie") {
    renderPie(data.slice(0, 10), "smartChart");
  } else if (type === "line") {
    renderLine(data.reverse(), "smartChart");
  } else if (type === "scatter") {
    renderScatter(state.rows, x, y, "smartChart");
  } else {
    renderBar(data, "smartChart");
  }
}

function renderQuality(quality) {
  const rows = [
    { Metric: "Rows", Value: quality.rows },
    { Metric: "Columns", Value: quality.columns },
    { Metric: "Duplicate rows", Value: quality.duplicateRows },
    { Metric: "Missing values", Value: quality.totalMissing },
    { Metric: "Numeric columns", Value: quality.numericColumns.join(", ") || "None" },
    { Metric: "Date columns", Value: quality.dateColumns.join(", ") || "None" }
  ];
  $("qualityTable").innerHTML = table(rows);
}

function renderValidation() {
  const rows = validationReport(state.rows).map((row) => ({
    Severity: `<span class="badge ${row.Severity === "High" ? "danger" : row.Severity === "Medium" ? "warn" : ""}">${row.Severity}</span>`,
    Issue: row.Issue,
    Rows: row.Rows,
    Detail: row.Detail
  }));
  $("validationTable").innerHTML = table(rows, true);
}

function renderDetails() {
  const title = $("detailTitle");
  const content = $("detailContent");
  const product = field("Product") || field("SKU");
  const supplier = field("Supplier");
  const warehouse = field("Warehouse");
  const route = field("Route") || field("Carrier");
  const cost = field("Cost");
  const demand = field("Demand") || field("Sales");
  const inventory = field("Inventory");
  let cards = [];

  if (state.workspace === "planning") {
    title.textContent = "Planning Details";
    cards = [
      ["ABC / XYZ Signals", abcXyz(product, demand, cost).slice(0, 8)],
      ["Inventory Risk", inventoryRisk(product, demand, inventory).slice(0, 8)],
      ["Demand by Product", groupAgg(state.rows, product, demand, "sum").slice(0, 8)]
    ];
  } else if (state.workspace === "operations") {
    title.textContent = "Operations Details";
    cards = [
      ["Supplier Spend", groupAgg(state.rows, supplier, field("Procurement Cost") || cost, "sum").slice(0, 8)],
      ["Warehouse Stock", groupAgg(state.rows, warehouse, inventory, "sum").slice(0, 8)],
      ["Route Cost", groupAgg(state.rows, route, field("Shipment Cost") || field("Logistics Cost"), "sum").slice(0, 8)]
    ];
  } else if (state.workspace === "finance") {
    title.textContent = "Finance Details";
    cards = [
      ["Cost by Category", groupAgg(state.rows, field("Cost Category") || field("Category"), cost, "sum").slice(0, 8)],
      ["Revenue by Product", groupAgg(state.rows, product, field("Revenue"), "sum").slice(0, 8)],
      ["Supplier Cost", groupAgg(state.rows, supplier, cost, "sum").slice(0, 8)]
    ];
  } else if (state.workspace === "exports") {
    title.textContent = "Export Details";
    cards = [
      ["Available Downloads", [{ key: "Cleaned CSV", value: state.rows.length }, { key: "KPI CSV", value: Object.keys(flatKpis()).length }, { key: "Mapping JSON", value: Object.values(state.mapping).filter(Boolean).length }]],
      ["Loaded Sheets", Object.entries(state.sheets).map(([key, rows]) => ({ key, value: rows.length }))],
      ["Current View", [{ key: state.activeSheet, value: state.rows.length }]]
    ];
  } else {
    title.textContent = "Data Details";
    cards = [
      ["Missing Values", Object.entries(qualitySummary(state.rows, state.columns).missingByColumn).map(([key, value]) => ({ key, value })).sort((a, b) => b.value - a.value).slice(0, 10)],
      ["Numeric Summary", numericSummary().slice(0, 8)],
      ["Categorical Summary", categoricalSummary().slice(0, 8)]
    ];
  }

  content.innerHTML = `<div class="detail-grid">${cards.map(([name, rows]) => `<div class="mini-card"><h4>${escapeHtml(name)}</h4>${tableLikeList(rows)}</div>`).join("")}</div>`;
}

function renderPreview() {
  $("previewTable").innerHTML = table(state.rows.slice(0, 100));
}

function abcXyz(itemCol, demandCol, costCol) {
  if (!itemCol || !demandCol) return [];
  const byItem = new Map();
  state.rows.forEach((row) => {
    const key = String(row[itemCol] ?? "Blank");
    const demand = parseNumber(row[demandCol]) || 0;
    const cost = costCol ? (parseNumber(row[costCol]) || 1) : 1;
    if (!byItem.has(key)) byItem.set(key, []);
    byItem.get(key).push({ demand, value: demand * cost });
  });
  const rows = Array.from(byItem, ([key, values]) => {
    const totalDemand = values.reduce((a, b) => a + b.demand, 0);
    const value = values.reduce((a, b) => a + b.value, 0);
    const avg = totalDemand / Math.max(1, values.length);
    const std = Math.sqrt(values.reduce((a, b) => a + Math.pow(b.demand - avg, 2), 0) / Math.max(1, values.length));
    return { key, value, totalDemand, cv: safeDiv(std, avg) };
  }).sort((a, b) => b.value - a.value);
  const total = rows.reduce((a, b) => a + b.value, 0);
  let cum = 0;
  return rows.map((row) => {
    cum += row.value;
    const pct = safeDiv(cum, total) * 100;
    const abc = pct <= 80 ? "A" : pct <= 95 ? "B" : "C";
    const xyz = row.cv <= 0.5 ? "X" : row.cv <= 1 ? "Y" : "Z";
    return { key: row.key, value: `${abc}${xyz}` };
  });
}

function inventoryRisk(itemCol, demandCol, invCol) {
  if (!itemCol || !demandCol || !invCol) return [];
  const demandByItem = groupAgg(state.rows, itemCol, demandCol, "average");
  const invByItem = new Map(groupAgg(state.rows, itemCol, invCol, "sum").map((d) => [d.key, d.value]));
  return demandByItem.map((d) => {
    const inv = invByItem.get(d.key) || 0;
    const days = safeDiv(inv, d.value);
    return { key: d.key, value: days < 14 ? `Risk (${nf.format(days)} days)` : `${nf.format(days)} days` };
  }).sort((a, b) => String(a.value).includes("Risk") ? -1 : 1);
}

function numericSummary() {
  return state.columns.filter((col) => state.rows.some((row) => Number.isFinite(parseNumber(row[col])))).map((col) => {
    const values = state.rows.map((row) => parseNumber(row[col])).filter(Number.isFinite);
    return { key: col, value: `avg ${nf.format(values.reduce((a, b) => a + b, 0) / values.length)}` };
  });
}

function categoricalSummary() {
  return state.columns.filter((col) => !state.rows.some((row) => Number.isFinite(parseNumber(row[col])))).map((col) => {
    const values = state.rows.map((row) => row[col]).filter((v) => v !== "" && v !== null && v !== undefined);
    return { key: col, value: `${new Set(values).size} unique` };
  });
}

function tableLikeList(rows) {
  if (!rows || !rows.length) return "<p>Map the required columns to unlock this view.</p>";
  return `<table><tbody>${rows.map((row) => `<tr><td>${escapeHtml(row.key)}</td><td>${escapeHtml(formatValue(row.value))}</td></tr>`).join("")}</tbody></table>`;
}

function table(rows, allowHtml = false) {
  if (!rows || !rows.length) return "<p>No rows to display.</p>";
  const headers = Object.keys(rows[0]);
  return `<div class="table-wrap"><table><thead><tr>${headers.map((h) => `<th>${escapeHtml(h)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${headers.map((h) => `<td>${allowHtml ? row[h] : escapeHtml(formatValue(row[h]))}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function renderBar(data, target) {
  if (!data.length) return emptyChart(target);
  const width = 920, height = 320, pad = 42;
  const max = Math.max(...data.map((d) => d.value), 1);
  const barW = (width - pad * 2) / data.length;
  $(target).innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img">
    <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#cad3df"/>
    ${data.map((d, i) => {
      const h = (height - pad * 2) * d.value / max;
      const x = pad + i * barW + 5;
      const y = height - pad - h;
      return `<rect x="${x}" y="${y}" width="${Math.max(6, barW - 10)}" height="${h}" fill="#0f766e"/><text x="${x}" y="${height - 18}" font-size="10" fill="#475467" transform="rotate(35 ${x} ${height - 18})">${escapeHtml(shortLabel(d.key))}</text>`;
    }).join("")}
  </svg>`;
}

function renderLine(data, target) {
  if (!data.length) return emptyChart(target);
  const width = 920, height = 320, pad = 42;
  const max = Math.max(...data.map((d) => d.value), 1);
  const step = (width - pad * 2) / Math.max(1, data.length - 1);
  const points = data.map((d, i) => `${pad + i * step},${height - pad - ((height - pad * 2) * d.value / max)}`).join(" ");
  $(target).innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img">
    <polyline fill="none" stroke="#1d4ed8" stroke-width="3" points="${points}"/>
    ${data.map((d, i) => `<circle cx="${pad + i * step}" cy="${height - pad - ((height - pad * 2) * d.value / max)}" r="4" fill="#0f766e"/>`).join("")}
  </svg>`;
}

function renderPie(data, target) {
  if (!data.length) return emptyChart(target);
  const total = data.reduce((a, b) => a + b.value, 0) || 1;
  let offset = 0;
  const colors = ["#0f766e", "#1d4ed8", "#b45309", "#475467", "#047857", "#7c3aed", "#be123c", "#0369a1", "#65a30d", "#334155"];
  $(target).innerHTML = `<svg viewBox="0 0 920 320" role="img">
    <circle cx="210" cy="160" r="105" fill="none" stroke="#e6ebf2" stroke-width="90"/>
    ${data.map((d, i) => {
      const dash = d.value / total * 659.7;
      const seg = `<circle cx="210" cy="160" r="105" fill="none" stroke="${colors[i % colors.length]}" stroke-width="90" stroke-dasharray="${dash} 659.7" stroke-dashoffset="${-offset}" transform="rotate(-90 210 160)"/>`;
      offset += dash;
      return seg;
    }).join("")}
    ${data.map((d, i) => `<rect x="390" y="${54 + i * 24}" width="12" height="12" fill="${colors[i % colors.length]}"/><text x="410" y="${65 + i * 24}" font-size="13" fill="#344054">${escapeHtml(shortLabel(d.key))}: ${nf.format(d.value)}</text>`).join("")}
  </svg>`;
}

function renderScatter(rows, xCol, yCol, target) {
  if (!xCol || !yCol) return emptyChart(target);
  const points = rows.map((row) => ({ x: parseNumber(row[xCol]), y: parseNumber(row[yCol]) })).filter((p) => Number.isFinite(p.x) && Number.isFinite(p.y)).slice(0, 500);
  if (!points.length) return emptyChart(target);
  const width = 920, height = 320, pad = 42;
  const maxX = Math.max(...points.map((p) => p.x), 1);
  const maxY = Math.max(...points.map((p) => p.y), 1);
  $(target).innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img">
    <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#cad3df"/>
    <line x1="${pad}" y1="${pad}" x2="${pad}" y2="${height - pad}" stroke="#cad3df"/>
    ${points.map((p) => `<circle cx="${pad + (width - pad * 2) * p.x / maxX}" cy="${height - pad - (height - pad * 2) * p.y / maxY}" r="3" fill="#0f766e" opacity="0.75"/>`).join("")}
  </svg>`;
}

function renderPareto(data, target) {
  if (!data.length) return emptyChart(target);
  const total = data.reduce((a, b) => a + b.value, 0) || 1;
  let running = 0;
  const rows = data.map((d) => {
    running += d.value;
    return { key: d.key, value: d.value, pct: running / total * 100 };
  });
  renderBar(rows, target);
}

function emptyChart(target) {
  $(target).innerHTML = `<div class="empty"><h2>No chart available</h2><p>Choose mapped columns with numeric values.</p></div>`;
}

function shortLabel(text) {
  const value = String(text ?? "");
  return value.length > 16 ? `${value.slice(0, 15)}...` : value;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}

function toCsv(rows) {
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  const line = (values) => values.map((value) => {
    const text = String(value ?? "");
    return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  }).join(",");
  return [line(headers), ...rows.map((row) => line(headers.map((h) => row[h])))].join("\n");
}

function flatKpis() {
  const groups = buildKpis(state.rows);
  const out = {};
  Object.entries(groups).forEach(([group, metrics]) => {
    Object.entries(metrics).forEach(([metric, value]) => {
      out[`${group} - ${metric}`] = value;
    });
  });
  return out;
}

function download(filename, text, mime = "text/plain") {
  const blob = new Blob([text], { type: mime });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function wireEvents() {
  $("fileInput").addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) loadFile(file).catch((error) => alert(`Could not load file: ${error.message}`));
  });
  $("sampleBtn").addEventListener("click", async () => {
    try {
      const response = await fetch("assets/integrated_scm_data.csv");
      const text = await response.text();
      state.sourceName = "integrated_scm_data.csv";
      state.sheets = { Integrated_SCM_Data: csvParse(text) };
      populateSheets();
    } catch (error) {
      alert("Sample data could not be opened from this browser context. Upload a local CSV or Excel file instead.");
    }
  });
  $("sheetSelect").addEventListener("change", applyCurrentSheet);
  ["normalizeColumns", "convertTypes", "dropDuplicates", "missingStrategy"].forEach((id) => $(id).addEventListener("change", recalculate));
  ["chartType", "chartX", "chartY", "chartAgg"].forEach((id) => $(id).addEventListener("change", renderSmartChart));
  $("toggleMapping").addEventListener("click", () => {
    $("mappingPanel").classList.toggle("hidden");
    $("toggleMapping").textContent = $("mappingPanel").classList.contains("hidden") ? "Show mapping" : "Hide mapping";
  });
  $("workspaceTabs").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-workspace]");
    if (!button) return;
    state.workspace = button.dataset.workspace;
    document.querySelectorAll("#workspaceTabs button").forEach((btn) => btn.classList.toggle("active", btn === button));
    renderAll();
  });
  $("exportCleanBtn").addEventListener("click", () => download("cleaned_scm_data.csv", toCsv(state.rows), "text/csv"));
  $("exportKpiBtn").addEventListener("click", () => {
    const rows = Object.entries(buildKpis(state.rows)).flatMap(([module, metrics]) => Object.entries(metrics).map(([metric, value]) => ({ Module: module, Metric: metric, Value: value })));
    download("scm_kpi_table.csv", toCsv(rows), "text/csv");
  });
  $("exportMappingBtn").addEventListener("click", () => download("column_mapping.json", JSON.stringify(state.mapping, null, 2), "application/json"));
}

wireEvents();
