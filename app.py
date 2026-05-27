from __future__ import annotations

from pathlib import Path
from typing import Dict
import json

import pandas as pd
import streamlit as st

from modules import (
    advanced_features,
    cost_analysis,
    demand_analysis,
    inventory_analysis,
    logistics_analysis,
    procurement_analysis,
    production_analysis,
    warehouse_analysis,
)
from modules.chart_generator import chart_png_bytes, make_chart, suggest_charts
from modules.column_mapper import EXPECTED_FIELDS, auto_map_columns
from modules.data_cleaner import categorical_summary, clean_data, data_quality_summary, numeric_summary
from modules.data_loader import combine_sheets, infer_column_types, load_sample_workbook, read_file
from modules.local_storage import (
    init_storage,
    list_dataframes,
    list_mappings,
    load_dataframe,
    load_mapping,
    log_audit_event,
    save_dataframe,
    save_feedback,
    save_mapping,
)
from modules.reporting import create_pdf_report, get_all_kpis, kpis_to_frame, to_excel_bytes
from modules.workflow_assistant import render_workflow_assistant


APP_DIR = Path(__file__).resolve().parent
SAMPLE_WORKBOOK = APP_DIR / "sample_data" / "sample_scm_data.xlsx"
DB_PATH = APP_DIR / "data" / "scm_analytics_studio.sqlite"


st.set_page_config(
    page_title="SCM Analytics Studio",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def css():
    st.markdown(
        """
        <style>
        :root {
            --scm-bg: #f0f4f9;
            --scm-surface: #ffffff;
            --scm-surface-2: #eef3f8;
            --scm-shell: #0b1320;
            --scm-shell-2: #111c2e;
            --scm-text: #0f1923;
            --scm-text-inverse: #f1f5f9;
            --scm-muted: #4b5563;
            --scm-muted-inverse: #94a3b8;
            --scm-border: #d0d9e6;
            --scm-accent: #0f766e;
            --scm-accent-2: #1d4ed8;
            --scm-accent-light: #e6f4f3;
            --scm-warn: #b45309;
            --scm-danger: #b91c1c;
            --scm-success: #15803d;
            --radius-sm: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --shadow-sm: 0 1px 3px rgba(15,23,42,0.08);
            --shadow-md: 0 4px 12px rgba(15,23,42,0.12);
            --shadow-lg: 0 12px 32px rgba(15,23,42,0.16);
            --transition: 130ms ease;
        }
        /* ── Layout ─────────────────────────────────── */
        .stApp { background: var(--scm-bg); color: var(--scm-text); }
        .block-container {
            padding-top: 0.75rem;
            padding-bottom: 2rem;
            max-width: 1560px;
            color: var(--scm-text);
        }
        /* ── Sidebar ─────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a1220 0%, #101b2e 60%, #0d1e30 100%);
            color: var(--scm-text-inverse);
            border-right: 1px solid rgba(255,255,255,0.06);
            box-shadow: 4px 0 24px rgba(0,0,0,0.18);
        }
        section[data-testid="stSidebar"] * { color: var(--scm-text-inverse); }
        section[data-testid="stSidebar"] div[data-baseweb="select"] *,
        section[data-testid="stSidebar"] div[data-baseweb="input"] *,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] input { color: var(--scm-text); }
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span { color: var(--scm-muted-inverse); }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 { color: var(--scm-text-inverse); letter-spacing: 0.01em; }
        /* sidebar section divider */
        section[data-testid="stSidebar"] hr {
            border: none;
            border-top: 1px solid rgba(255,255,255,0.08);
            margin: 10px 0;
        }
        /* sidebar radio/checkbox labels */
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stCheckbox label { font-size: 0.9rem; }
        /* ── Typography ──────────────────────────────── */
        h1, h2, h3, h4, h5, h6, p, label { color: var(--scm-text); }
        h2 { font-size: 1.25rem; font-weight: 700; }
        h3 { font-size: 1.05rem; font-weight: 650; }
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stCaptionContainer"],
        .small-note { color: var(--scm-muted); }
        /* ── Control header banner ───────────────────── */
        .control-header {
            background: linear-gradient(120deg, #0a1220 0%, #122440 55%, #0f766e 130%);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: var(--radius-lg);
            padding: 16px 22px;
            margin: 0 0 14px 0;
            box-shadow: var(--shadow-lg);
        }
        .control-header h1 {
            color: var(--scm-text-inverse);
            font-size: 1.65rem;
            margin: 0;
            line-height: 1.2;
            letter-spacing: -0.01em;
        }
        .control-header p {
            color: var(--scm-muted-inverse);
            margin: 5px 0 0 0;
            font-size: 0.9rem;
        }
        /* ── Workspace title bar ─────────────────────── */
        .workspace-title {
            background: var(--scm-surface);
            border: 1px solid var(--scm-border);
            border-left: 4px solid var(--scm-accent);
            border-radius: var(--radius-md);
            padding: 10px 14px;
            margin: 2px 0 12px 0;
            box-shadow: var(--shadow-sm);
        }
        .workspace-title h2 { font-size: 1.05rem; margin: 0; color: var(--scm-text); }
        .workspace-title p { color: var(--scm-muted); margin: 3px 0 0 0; font-size: 0.84rem; }
        /* ── Metrics ─────────────────────────────────── */
        div[data-testid="stMetric"] {
            background: var(--scm-surface);
            border: 1px solid var(--scm-border);
            padding: 12px 14px;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            transition: box-shadow var(--transition), transform var(--transition);
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }
        div[data-testid="stMetric"] * { color: var(--scm-text); }
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] { color: var(--scm-muted) !important; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-weight: 700; color: var(--scm-text) !important; }
        /* ── DataFrames ──────────────────────────────── */
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--scm-border);
            border-radius: var(--radius-md);
            overflow: hidden;
            background: var(--scm-surface);
            box-shadow: var(--shadow-sm);
        }
        /* ── Buttons ─────────────────────────────────── */
        button,
        button[kind="primary"],
        div[data-testid="stDownloadButton"] button {
            border-radius: var(--radius-sm);
            font-weight: 600;
            transition: box-shadow var(--transition), transform var(--transition), background var(--transition);
        }
        button:not([kind="primary"]),
        div[data-testid="stDownloadButton"] button {
            background: var(--scm-surface);
            color: var(--scm-text);
            border: 1px solid var(--scm-border);
        }
        button:not([kind="primary"]):hover,
        div[data-testid="stDownloadButton"] button:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
            border-color: #a0b0c4;
        }
        button[kind="primary"] {
            background: var(--scm-shell);
            color: var(--scm-text-inverse);
            border: 1px solid var(--scm-shell);
        }
        button[kind="primary"]:hover {
            background: #1a2f4a;
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }
        button:focus-visible,
        div[data-testid="stDownloadButton"] button:focus-visible {
            outline: 2px solid var(--scm-accent);
            outline-offset: 2px;
        }
        /* ── Tabs ────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            border-bottom: 2px solid var(--scm-border);
            background: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background: #e4ecf5;
            border: 1px solid var(--scm-border);
            border-bottom: 0;
            border-radius: 6px 6px 0 0;
            color: var(--scm-muted);
            padding: 7px 13px;
            font-size: 0.88rem;
            font-weight: 500;
            transition: background var(--transition), color var(--transition), box-shadow var(--transition);
        }
        .stTabs [data-baseweb="tab"]:hover {
            background: #d8e5f2;
            color: var(--scm-text);
        }
        .stTabs [aria-selected="true"] {
            background: var(--scm-surface);
            color: var(--scm-accent);
            font-weight: 700;
            border-bottom-color: var(--scm-surface);
        }
        /* ── Inputs / selects ────────────────────────── */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        textarea {
            background: #ffffff;
            color: var(--scm-text);
            border-color: var(--scm-border);
            border-radius: var(--radius-sm) !important;
        }
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="input"] > div:focus-within,
        textarea:focus {
            border-color: var(--scm-accent) !important;
            box-shadow: 0 0 0 3px rgba(15,118,110,0.15) !important;
        }
        /* ── Expanders ───────────────────────────────── */
        div[data-testid="stExpander"] {
            background: var(--scm-surface);
            border: 1px solid var(--scm-border);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            transition: box-shadow var(--transition);
        }
        div[data-testid="stExpander"]:hover { box-shadow: var(--shadow-md); }
        /* ── Alerts ──────────────────────────────────── */
        div[data-testid="stAlert"] { border-radius: var(--radius-md); }
        /* ── Scrollbar ───────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #c1cdd9; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #8fa3b8; }
        /* ── Misc ────────────────────────────────────── */
        h1, h2, h3 { letter-spacing: -0.01em; color: var(--scm-text); }
        .small-note { font-size: 0.88rem; }
        .stProgress > div > div { background-color: var(--scm-accent); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def mapping_editor(
    df: pd.DataFrame,
    initial_mapping: Dict[str, str | None] | None = None,
    key_suffix: str = "auto",
) -> Dict[str, str | None]:
    auto = auto_map_columns(df)
    if initial_mapping:
        for field, col in initial_mapping.items():
            if col in df.columns:
                auto[field] = col
    columns = ["-- Not mapped --"] + list(df.columns)

    st.markdown("Map your uploaded columns to standard SCM fields. Auto-detected matches are preselected.")
    mapping = {}
    field_groups = {
        "Core": ["Date", "Product", "SKU", "Category", "Supplier", "Customer", "Region", "Warehouse"],
        "Demand / Sales": ["Demand", "Forecast", "Sales", "Revenue"],
        "Inventory": ["Inventory", "COGS", "Average Inventory", "Stockout Event", "Last Movement Date"],
        "Procurement": ["Order Date", "Received Date", "Lead Time", "Defective Units", "Total Units", "Procurement Cost"],
        "Logistics": ["Delivery Date", "Promised Delivery Date", "Shipment Cost", "Carrier", "Route", "Shipment ID", "Logistics Cost"],
        "Warehouse": ["Inbound Quantity", "Outbound Quantity", "Space Used", "Space Capacity", "Picks", "Accurate Picks"],
        "Production": ["Production Quantity", "Planned Production", "Capacity", "Maximum Capacity", "Downtime"],
        "Cost": ["Cost", "Cost Category", "Fulfilled Orders", "Total Orders"],
        "Status / Planning": ["Order ID", "Order Quantity", "Shipped Quantity", "Open Quantity", "PO Status", "Order Status", "Shipment Status", "Due Date", "Open Supply", "Backorder Quantity"],
        "Extended Cost / Logistics": ["Standard Price", "Contract Price", "Actual Price", "Unit Price", "Weight", "Volume", "Distance", "Origin", "Destination", "Incoterm", "Currency"],
        "Site / Lot / Labor": ["Plant", "Site", "Lot", "Batch", "Planner", "Buyer", "Customer Segment", "UOM", "Worker", "Team", "Activity"],
        "Advanced Operations": ["Scrap Quantity", "Good Quantity", "Planned Time", "Run Time", "Schedule Quantity", "Cycle Count Quantity", "System Quantity", "Service Level", "Holding Cost Rate", "Order Cost"],
    }

    for group, fields in field_groups.items():
        with st.expander(group, expanded=(group == "Core")):
            subcols = st.columns(2)
            for i, field in enumerate(fields):
                default = auto.get(field)
                default_index = columns.index(default) if default in columns else 0
                with subcols[i % 2]:
                    chosen = st.selectbox(
                        field,
                        options=columns,
                        index=default_index,
                        key=f"map_{key_suffix}_{field}",
                    )
                    mapping[field] = None if chosen == "-- Not mapped --" else chosen

    # Include fields that are not displayed above, preserving all expected keys.
    for field in EXPECTED_FIELDS:
        mapping.setdefault(field, auto.get(field))
    return mapping


def apply_sidebar_filters(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    out = df.copy()
    st.sidebar.markdown("### Filters")

    date_col = mapping.get("Date")
    if date_col and date_col in out.columns:
        dates = pd.to_datetime(out[date_col], errors="coerce")
        if dates.notna().any():
            min_date = dates.min().date()
            max_date = dates.max().date()
            selected = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
            if isinstance(selected, tuple) and len(selected) == 2:
                start, end = selected
                mask = (dates.dt.date >= start) & (dates.dt.date <= end)
                out = out[mask]

    for field in [
        "Product", "SKU", "Supplier", "Region", "Warehouse", "Customer", "Carrier", "Route",
        "Category", "Lot", "Batch", "Origin", "Destination", "Incoterm", "Currency", "UOM",
        "PO Status", "Order Status", "Shipment Status", "Plant", "Site", "Planner", "Buyer",
    ]:
        col = mapping.get(field)
        if col and col in out.columns:
            values = sorted([str(v) for v in out[col].dropna().unique()])
            selected = st.sidebar.multiselect(field, options=values, default=[])
            if selected:
                out = out[out[col].astype(str).isin(selected)]

    calendar = advanced_features.business_calendar_table(out, mapping)
    date_col = mapping.get("Date")
    if not calendar.empty and date_col and date_col in out.columns:
        fiscal_periods = sorted(calendar["Fiscal Period"].unique())
        selected_periods = st.sidebar.multiselect("Fiscal Period", fiscal_periods, default=[])
        if selected_periods:
            row_periods = pd.to_datetime(out[date_col], errors="coerce").dt.to_period("M").astype(str)
            out = out[row_periods.isin(selected_periods)]

    risk = advanced_features.inventory_risk_table(out, mapping)
    if not risk.empty and st.sidebar.checkbox("Stockout risk only", value=False):
        item_col = mapping.get("SKU") or mapping.get("Product")
        risk_items = risk.loc[risk["stockout_risk"], "Item"].astype(str).tolist()
        if item_col and item_col in out.columns:
            out = out[out[item_col].astype(str).isin(risk_items)]

    segments = advanced_features.abc_xyz(out, mapping)
    if not segments.empty:
        selected_segments = st.sidebar.multiselect("ABC/XYZ Class", sorted(segments["ABC/XYZ"].unique()), default=[])
        if selected_segments:
            item_col = mapping.get("SKU") or mapping.get("Product")
            seg_items = segments.loc[segments["ABC/XYZ"].isin(selected_segments), segments.columns[0]].astype(str).tolist()
            if item_col and item_col in out.columns:
                out = out[out[item_col].astype(str).isin(seg_items)]

    return out


def control_header(source_name: str, sheet_choice: str, filtered_df: pd.DataFrame, quality: dict) -> None:
    st.markdown(
        f"""
        <div class="control-header">
            <h1>SCM Analytics Studio</h1>
            <p>{source_name or "Current dataset"} · {sheet_choice} · {len(filtered_df):,} rows · {quality.get("columns", 0):,} columns</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def workspace_title(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="workspace-title">
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feedback_form(source_name: str, sheet_choice: str, filtered_df: pd.DataFrame) -> None:
    """Collect offline product feedback from users into local SQLite."""
    with st.sidebar.expander("Send Feedback", expanded=False):
        st.caption("Saved locally in SQLite. No internet or external service is used.")
        with st.form("scm_user_feedback_form", clear_on_submit=True):
            name = st.text_input("Name", placeholder="Optional")
            contact = st.text_input("Email or contact", placeholder="Optional")
            category = st.selectbox(
                "Feedback type",
                ["General", "Bug", "Feature request", "Data issue", "Dashboard issue", "Export issue"],
            )
            rating = st.slider("Rating", min_value=1, max_value=5, value=4)
            message = st.text_area("Feedback", placeholder="What should be improved or fixed?")
            submitted = st.form_submit_button("Submit feedback", width="stretch")

        if submitted:
            if not message.strip():
                st.error("Please add a feedback message.")
            else:
                try:
                    context = {
                        "source": source_name,
                        "sheet": sheet_choice,
                        "filtered_rows": int(len(filtered_df)),
                        "filtered_columns": int(filtered_df.shape[1]),
                    }
                    save_feedback(
                        DB_PATH,
                        name=name,
                        contact=contact,
                        category=category,
                        rating=rating,
                        message=message,
                        context=context,
                    )
                    log_audit_event(DB_PATH, "feedback_saved", {"category": category, "rating": rating})
                    st.success("Feedback saved locally.")
                except Exception as e:
                    st.error(f"Could not save feedback: {e}")


def render_data_quality_section(filtered_df: pd.DataFrame, quality: dict) -> None:
    st.subheader("Data Preview")
    st.dataframe(filtered_df.head(200), width="stretch")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{quality['rows']:,}")
    c2.metric("Columns", f"{quality['columns']:,}")
    c3.metric("Duplicates", f"{quality['duplicate_rows']:,}")
    c4.metric("Missing Values", f"{quality['total_missing_values']:,}")

    st.markdown("#### Column Types")
    st.dataframe(infer_column_types(filtered_df), width="stretch")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Numeric Summary")
        st.dataframe(numeric_summary(filtered_df), width="stretch")
    with col_b:
        st.markdown("#### Categorical Summary")
        st.dataframe(categorical_summary(filtered_df), width="stretch")

    st.markdown("#### Missing Values")
    missing_df = pd.DataFrame(
        [{"Column": k, "Missing Values": v} for k, v in quality["missing_by_column"].items()]
    )
    st.dataframe(missing_df, width="stretch")

    if quality["date_ranges"]:
        st.markdown("#### Date Ranges")
        st.dataframe(
            pd.DataFrame(
                [
                    {"Column": col, "Start": bounds.get("min"), "End": bounds.get("max")}
                    for col, bounds in quality["date_ranges"].items()
                ]
            ),
            width="stretch",
        )


def render_smart_chart_section(filtered_df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Smart Chart Generator")
    with st.expander("Suggested charts", expanded=False):
        for suggestion in suggest_charts(filtered_df, mapping):
            st.write(f"- {suggestion}")

    numeric_cols = list(filtered_df.select_dtypes(include="number").columns)
    all_cols = list(filtered_df.columns)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        chart_type = st.selectbox(
            "Chart Type",
            ["line", "bar", "pie", "scatter", "histogram", "box", "heatmap", "area", "treemap", "pareto"],
        )
    with col2:
        x_col = st.selectbox("X-axis", all_cols, index=0)
    with col3:
        y_options = ["-- None --"] + numeric_cols
        y_col = st.selectbox("Y-axis", y_options, index=1 if numeric_cols else 0)
        y_col = None if y_col == "-- None --" else y_col
    with col4:
        color_options = ["-- None --"] + all_cols
        color_col = st.selectbox("Category / Color", color_options)
        color_col = None if color_col == "-- None --" else color_col

    agg = st.selectbox("Aggregation", ["sum", "average", "count", "min", "max"], index=0)
    fig = make_chart(filtered_df, chart_type, x_col, y_col, color_col, agg, title="Smart Chart")
    st.plotly_chart(fig, width="stretch")

    chart_html = fig.to_html(include_plotlyjs=True)
    c1, c2 = st.columns(2)
    c1.download_button("Download chart as HTML", data=chart_html, file_name="smart_chart.html", mime="text/html", width="stretch")
    try:
        png_bytes = chart_png_bytes(filtered_df, chart_type, x_col, y_col, color_col, agg, "Smart Chart")
        c2.download_button("Download chart as PNG", data=png_bytes, file_name="smart_chart.png", mime="image/png", width="stretch")
    except Exception:
        c2.caption("PNG export is unavailable for this chart.")


def render_export_section(filtered_df: pd.DataFrame, mapping: dict, kpi_groups: dict, quality: dict) -> None:
    st.subheader("Export Center")
    kpi_df = kpis_to_frame(kpi_groups)

    c1, c2, c3 = st.columns(3)
    c1.download_button("Cleaned CSV", data=filtered_df.to_csv(index=False).encode("utf-8"), file_name="cleaned_scm_data.csv", mime="text/csv", width="stretch")
    c2.download_button("Cleaned Excel", data=to_excel_bytes(filtered_df, "Cleaned_Data"), file_name="cleaned_scm_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    c3.download_button("Dashboard PDF", data=create_pdf_report(quality, kpi_groups), file_name="scm_dashboard_summary.pdf", mime="application/pdf", width="stretch")

    st.markdown("#### KPI Table")
    st.dataframe(kpi_df.astype(str), width="stretch")
    e1, e2 = st.columns(2)
    e1.download_button("KPI CSV", data=kpi_df.to_csv(index=False).encode("utf-8"), file_name="scm_kpi_table.csv", mime="text/csv", width="stretch")
    e2.download_button("KPI Excel", data=to_excel_bytes(kpi_df, "KPI_Table"), file_name="scm_kpi_table.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")

    st.markdown("#### Optional SQLite Storage")
    sqlite_name = st.text_input("SQLite dataset name", value="cleaned_scm_data")
    if st.button("Save cleaned data to local SQLite", width="stretch"):
        try:
            save_dataframe(filtered_df, DB_PATH, sqlite_name)
            log_audit_event(DB_PATH, "dataset_saved", {"name": sqlite_name, "rows": len(filtered_df)})
            st.success(f"Saved cleaned data locally as: {sqlite_name}")
        except Exception as e:
            st.error(f"Could not save cleaned data to SQLite: {e}")

    advanced_features.render_extra_exports(filtered_df, mapping, kpi_groups, quality)


def render_grouped_workspaces(filtered_df: pd.DataFrame, mapping: dict, quality: dict, kpi_groups: dict, source_name: str, sheet_choice: str) -> None:
    control_header(source_name, sheet_choice, filtered_df, quality)

    workspace = st.sidebar.radio(
        "Workspace",
        ["📊 Data", "📅 Planning", "⚙️ Operations", "💰 Finance", "📤 Exports"],
        index=1,
    )
    workspace = workspace.split(" ", 1)[1]  # strip emoji prefix for routing
    view_mode = st.sidebar.radio("View mode", ["Executive", "Analyst"], horizontal=True)

    if workspace == "Data":
        workspace_title("Data Workspace", "Quality, mapping confidence, local settings, and chart exploration.")
        data_tabs = st.tabs(["Quality", "Settings", "Smart Chart", "Assistant"])
        with data_tabs[0]:
            render_data_quality_section(filtered_df, quality)
        with data_tabs[1]:
            advanced_features.render_settings_help(filtered_df, mapping, DB_PATH)
        with data_tabs[2]:
            render_smart_chart_section(filtered_df, mapping)
        with data_tabs[3]:
            render_workflow_assistant(filtered_df, mapping)

    elif workspace == "Planning":
        workspace_title("Planning Workspace", "Executive control, demand forecasting, inventory policy, and scenarios.")
        if view_mode == "Executive":
            plan_tabs = st.tabs(["Control Tower", "Forecast", "Inventory Risk", "Scenario"])
        else:
            plan_tabs = st.tabs(["Control Tower", "Demand & Sales", "Forecast Accuracy", "Forecast Generation", "Inventory", "Inventory Risk", "Inventory Aging", "Scenario"])
        with plan_tabs[0]:
            advanced_features.render_executive_control_tower(filtered_df, mapping)
        if view_mode == "Executive":
            with plan_tabs[1]:
                advanced_features.render_forecast_generation(filtered_df, mapping)
            with plan_tabs[2]:
                advanced_features.render_inventory_risk(filtered_df, mapping)
            with plan_tabs[3]:
                advanced_features.render_planning_lab(filtered_df, mapping)
        else:
            with plan_tabs[1]:
                demand_analysis.render(filtered_df, mapping)
            with plan_tabs[2]:
                advanced_features.render_forecast_accuracy(filtered_df, mapping)
            with plan_tabs[3]:
                advanced_features.render_forecast_generation(filtered_df, mapping)
            with plan_tabs[4]:
                inventory_analysis.render(filtered_df, mapping)
            with plan_tabs[5]:
                advanced_features.render_inventory_risk(filtered_df, mapping)
            with plan_tabs[6]:
                advanced_features.render_inventory_aging(filtered_df, mapping)
            with plan_tabs[7]:
                advanced_features.render_planning_lab(filtered_df, mapping)

    elif workspace == "Operations":
        workspace_title("Operations Workspace", "Procurement, supplier, logistics, warehouse, production, and MRP execution.")
        if view_mode == "Executive":
            ops_tabs = st.tabs(["Suppliers", "Logistics", "Warehouse", "Production"])
            with ops_tabs[0]:
                advanced_features.render_supplier_scorecard(filtered_df, mapping)
            with ops_tabs[1]:
                advanced_features.render_carrier_lane(filtered_df, mapping)
            with ops_tabs[2]:
                advanced_features.render_warehouse_process(filtered_df, mapping)
            with ops_tabs[3]:
                advanced_features.render_production_performance(filtered_df, mapping)
        else:
            ops_tabs = st.tabs(["Procurement", "PO Aging", "Supplier Scorecard", "Contracts", "Logistics", "Carrier / Lane", "Warehouse", "Warehouse Productivity", "Warehouse Process", "Production", "Production Performance", "MRP Lite"])
            with ops_tabs[0]:
                procurement_analysis.render(filtered_df, mapping)
            with ops_tabs[1]:
                advanced_features.render_po_aging(filtered_df, mapping)
            with ops_tabs[2]:
                advanced_features.render_supplier_scorecard(filtered_df, mapping)
            with ops_tabs[3]:
                advanced_features.render_procurement_contracts(filtered_df, mapping)
            with ops_tabs[4]:
                logistics_analysis.render(filtered_df, mapping)
            with ops_tabs[5]:
                advanced_features.render_carrier_lane(filtered_df, mapping)
            with ops_tabs[6]:
                warehouse_analysis.render(filtered_df, mapping)
            with ops_tabs[7]:
                advanced_features.render_warehouse_productivity(filtered_df, mapping)
            with ops_tabs[8]:
                advanced_features.render_warehouse_process(filtered_df, mapping)
            with ops_tabs[9]:
                production_analysis.render(filtered_df, mapping)
            with ops_tabs[10]:
                advanced_features.render_production_performance(filtered_df, mapping)
            with ops_tabs[11]:
                advanced_features.render_mrp_lite(filtered_df, mapping)

    elif workspace == "Finance":
        workspace_title("Finance Workspace", "SCM cost, margin, landed-cost, and profitability bridge.")
        finance_tabs = st.tabs(["Cost & Profitability", "Finance Bridge", "Landed Cost"])
        with finance_tabs[0]:
            cost_analysis.render(filtered_df, mapping)
        with finance_tabs[1]:
            advanced_features.render_finance_bridge(filtered_df, mapping)
        with finance_tabs[2]:
            advanced_features.render_landed_cost(filtered_df, mapping)

    else:
        workspace_title("Exports Workspace", "Data extracts, report packs, SQLite storage, and custom charts.")
        export_tabs = st.tabs(["Export Center", "Smart Chart", "Assistant"])
        with export_tabs[0]:
            render_export_section(filtered_df, mapping, kpi_groups, quality)
        with export_tabs[1]:
            render_smart_chart_section(filtered_df, mapping)
        with export_tabs[2]:
            render_workflow_assistant(filtered_df, mapping)


@st.cache_data(show_spinner=False)
def _cached_clean(raw_df: pd.DataFrame, normalize: bool, convert: bool, drop_dupes: bool, strategy: str) -> pd.DataFrame:
    return clean_data(raw_df, normalize_columns=normalize, convert_types=convert, drop_duplicates=drop_dupes, missing_strategy=strategy)


@st.cache_data(show_spinner=False)
def _cached_quality(df: pd.DataFrame) -> dict:
    return data_quality_summary(df)


@st.cache_data(show_spinner=False)
def _cached_kpis(df: pd.DataFrame, mapping_json: str) -> dict:
    return get_all_kpis(df, json.loads(mapping_json))


def main():
    css()
    init_storage(DB_PATH)
    log_audit_event(DB_PATH, "app_opened", {"mode": "streamlit"})

    st.sidebar.markdown("## 📂 Load Data")
    uploaded = st.sidebar.file_uploader("Upload CSV / XLSX / XLS", type=["csv", "xlsx", "xls"])
    saved_datasets = list_dataframes(DB_PATH)
    saved_dataset_labels = {
        f"{item['display_name']} ({item['rows_count']:,} rows)": item["table_name"]
        for item in saved_datasets
    }
    selected_saved_dataset = "-- None --"
    if saved_dataset_labels:
        selected_saved_dataset = st.sidebar.selectbox(
            "Saved SQLite dataset",
            ["-- None --"] + list(saved_dataset_labels.keys()),
        )
    use_sample = st.sidebar.checkbox(
        "Use bundled sample data",
        value=uploaded is None and selected_saved_dataset == "-- None --",
    )

    # Every supported source is normalized into a sheet dictionary so CSV, Excel,
    # sample files, and optional SQLite snapshots follow the same dashboard path.
    sheets = {}
    source_name = ""
    if uploaded is not None:
        try:
            sheets = read_file(uploaded)
            source_name = uploaded.name
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
            st.stop()
    elif selected_saved_dataset != "-- None --":
        table_name = saved_dataset_labels[selected_saved_dataset]
        loaded_df = load_dataframe(DB_PATH, table_name)
        if loaded_df.empty:
            st.error("The selected SQLite dataset is empty or no longer available.")
            st.stop()
        sheets = {selected_saved_dataset: loaded_df}
        source_name = selected_saved_dataset
    elif use_sample:
        try:
            sheets = load_sample_workbook(SAMPLE_WORKBOOK)
            source_name = SAMPLE_WORKBOOK.name
        except Exception as e:
            st.error(f"Could not load bundled sample workbook: {e}")
            st.stop()

    if not sheets:
        st.markdown(
            """
            <div style="text-align:center;padding:60px 20px;color:#4b5563;">
                <div style="font-size:3rem;margin-bottom:16px;">📦</div>
                <div style="font-size:1.2rem;font-weight:600;color:#0f1923;margin-bottom:8px;">SCM Analytics Studio</div>
                <div style="font-size:0.95rem;">Upload a CSV or Excel file, or enable the bundled sample data in the sidebar to get started.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    sheet_options = list(sheets.keys())
    if len(sheet_options) > 1:
        selectable_sheets = ["Combine all sheets"] + sheet_options
        default_sheet = "Integrated_SCM_Data" if "Integrated_SCM_Data" in selectable_sheets else selectable_sheets[0]
        sheet_choice = st.sidebar.selectbox("Sheet", selectable_sheets, index=selectable_sheets.index(default_sheet))
    else:
        sheet_choice = sheet_options[0]

    raw_df = combine_sheets(sheets) if sheet_choice == "Combine all sheets" else sheets[sheet_choice]

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🧹 Clean Data")
    normalize_columns = st.sidebar.checkbox("Normalize column names", value=True)
    convert_types = st.sidebar.checkbox("Auto-convert dates and numbers", value=True)
    drop_duplicates = st.sidebar.checkbox("Drop duplicate rows", value=False)
    missing_strategy = st.sidebar.selectbox(
        "Missing value strategy",
        ["keep", "drop_rows", "fill_zero", "fill_forward", "fill_median_mode"],
        index=0,
    )

    with st.spinner("Cleaning data…"):
        df = _cached_clean(raw_df, normalize_columns, convert_types, drop_duplicates, missing_strategy)

    if df.empty:
        st.warning("The selected data is empty after cleaning. Adjust your cleaning options.")
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🗺️ Map Columns")
    saved_mappings = list_mappings(DB_PATH)
    saved_mapping_names = [item["name"] for item in saved_mappings]
    selected_mapping = st.sidebar.selectbox(
        "Saved column mapping",
        ["Auto-detect"] + saved_mapping_names,
    )
    initial_mapping = {} if selected_mapping == "Auto-detect" else load_mapping(DB_PATH, selected_mapping)
    template_upload = st.sidebar.file_uploader("Import mapping template JSON", type=["json"])
    if template_upload is not None:
        try:
            initial_mapping.update(json.loads(template_upload.getvalue().decode("utf-8")))
        except Exception as e:
            st.sidebar.error(f"Could not import mapping template: {e}")
    key_suffix = selected_mapping.replace(" ", "_").lower() if selected_mapping != "Auto-detect" else "auto"

    with st.expander("Column Mapping", expanded=True):
        if selected_mapping != "Auto-detect":
            st.caption(f"Loaded saved mapping profile: {selected_mapping}")
        mapping = mapping_editor(df, initial_mapping=initial_mapping, key_suffix=key_suffix)

        map_c1, map_c2 = st.columns([2, 1])
        with map_c1:
            default_profile = selected_mapping if selected_mapping != "Auto-detect" else Path(source_name or "scm_mapping").stem
            profile_name = st.text_input("Mapping profile name", value=default_profile)
        with map_c2:
            st.write("")
            st.write("")
            if st.button("Save mapping", width="stretch"):
                try:
                    save_mapping(DB_PATH, profile_name, mapping, list(df.columns), source_name=source_name)
                    log_audit_event(DB_PATH, "mapping_saved", {"profile": profile_name, "source": source_name})
                    st.success(f"Saved mapping profile: {profile_name}")
                except Exception as e:
                    st.error(f"Could not save mapping: {e}")

    # Filters are applied after cleaning and mapping so every module reads the same view.
    filtered_df = apply_sidebar_filters(df, mapping)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"**Dataset** · {len(filtered_df):,} rows · {filtered_df.shape[1]:,} cols",
    )
    render_feedback_form(source_name, sheet_choice, filtered_df)

    with st.spinner("Computing quality & KPIs…"):
        quality = _cached_quality(filtered_df)
        kpi_groups = _cached_kpis(filtered_df, json.dumps(mapping, default=str))

    render_grouped_workspaces(filtered_df, mapping, quality, kpi_groups, source_name, sheet_choice)


if __name__ == "__main__":
    main()
