from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd

from modules.chart_generator import chart_png_bytes, make_chart
from modules.column_mapper import EXPECTED_FIELDS, auto_map_columns
from modules.data_cleaner import clean_data, data_quality_summary
from modules.data_loader import combine_sheets, load_sample_workbook, read_file
from modules.local_storage import (
    init_storage,
    list_audit_events,
    list_dataframes,
    list_mappings,
    log_audit_event,
    load_dataframe,
    load_mapping,
    save_dataframe,
    save_mapping,
)
from modules.advanced_features import (
    METRIC_GLOSSARY,
    business_calendar_table,
    chart_bundle_zip_bytes,
    failed_row_quarantine,
    full_dashboard_workbook_bytes,
    generated_forecast_table,
    landed_cost_table,
    powerpoint_summary_bytes,
    validation_report,
)
from modules.reporting import create_pdf_report, get_all_kpis, kpis_to_frame, to_excel_bytes
from modules.fixture_accuracy import fixture_pack_report
from modules.skill_registry import create_sample_skill, list_skills, run_skill, skill_catalog
from modules.tool_registry import list_tools, run_tool


APP_DIR = Path(__file__).resolve().parent
SAMPLE_WORKBOOK = APP_DIR / "sample_data" / "sample_scm_data.xlsx"
DB_PATH = APP_DIR / "data" / "scm_analytics_studio.sqlite"


def parse_field_assignments(values: Optional[Iterable[str]]) -> Dict[str, str]:
    assignments: Dict[str, str] = {}
    for item in values or []:
        if "=" not in item:
            raise ValueError(f"Invalid mapping '{item}'. Use Field=Column.")
        field, column = item.split("=", 1)
        field = field.strip()
        column = column.strip()
        if field not in EXPECTED_FIELDS:
            raise ValueError(f"Unknown SCM field '{field}'.")
        assignments[field] = column
    return assignments


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def load_source(args: argparse.Namespace) -> tuple[Dict[str, pd.DataFrame], str]:
    if args.sqlite_table:
        df = load_dataframe(DB_PATH, args.sqlite_table)
        if df.empty:
            raise ValueError(f"SQLite dataset '{args.sqlite_table}' is empty or unavailable.")
        return {args.sqlite_table: df}, args.sqlite_table

    source = Path(args.input) if args.input else SAMPLE_WORKBOOK
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")

    sheets = load_sample_workbook(source) if source == SAMPLE_WORKBOOK else read_file(source)
    if not sheets:
        raise ValueError(f"No readable data found in: {source}")
    return sheets, source.name


def select_sheet(sheets: Dict[str, pd.DataFrame], sheet_name: Optional[str]) -> pd.DataFrame:
    if sheet_name == "Combine all sheets":
        return combine_sheets(sheets)
    if sheet_name:
        if sheet_name not in sheets:
            raise ValueError(f"Sheet '{sheet_name}' not found. Available: {', '.join(sheets)}")
        return sheets[sheet_name]
    if "Integrated_SCM_Data" in sheets:
        return sheets["Integrated_SCM_Data"]
    return next(iter(sheets.values()))


def build_mapping(args: argparse.Namespace, df: pd.DataFrame, source_name: str) -> Dict[str, Optional[str]]:
    mapping = auto_map_columns(df)
    if getattr(args, "mapping_template", None):
        template = json.loads(Path(args.mapping_template).read_text(encoding="utf-8"))
        mapping.update({field: col for field, col in template.items() if col in df.columns})
    if args.mapping_profile:
        saved = load_mapping(DB_PATH, args.mapping_profile)
        if not saved:
            raise ValueError(f"Mapping profile '{args.mapping_profile}' was not found.")
        mapping.update({field: col for field, col in saved.items() if col in df.columns})

    for field, column in parse_field_assignments(args.map).items():
        if column not in df.columns:
            raise ValueError(f"Column '{column}' for field '{field}' was not found.")
        mapping[field] = column

    if args.save_mapping:
        save_mapping(DB_PATH, args.save_mapping, mapping, list(df.columns), source_name)
    return mapping


def filter_dataframe(df: pd.DataFrame, mapping: dict, args: argparse.Namespace) -> pd.DataFrame:
    out = df.copy()
    date_col = mapping.get("Date")
    if date_col and date_col in out.columns and (args.date_start or args.date_end):
        dates = pd.to_datetime(out[date_col], errors="coerce")
        if args.date_start:
            out = out[dates >= pd.to_datetime(args.date_start)]
            dates = pd.to_datetime(out[date_col], errors="coerce")
        if args.date_end:
            out = out[dates <= pd.to_datetime(args.date_end)]

    for field, values in {
        "Product": args.product,
        "SKU": getattr(args, "sku", None),
        "Supplier": args.supplier,
        "Region": args.region,
        "Warehouse": args.warehouse,
        "Customer": args.customer,
        "Carrier": getattr(args, "carrier", None),
        "Route": getattr(args, "route", None),
        "Lot": getattr(args, "lot", None),
        "Batch": getattr(args, "batch", None),
        "Origin": getattr(args, "origin", None),
        "Destination": getattr(args, "destination", None),
        "Incoterm": getattr(args, "incoterm", None),
        "Currency": getattr(args, "currency", None),
        "UOM": getattr(args, "uom", None),
        "Planner": getattr(args, "planner", None),
        "Buyer": getattr(args, "buyer", None),
        "PO Status": getattr(args, "po_status", None),
        "Order Status": getattr(args, "order_status", None),
        "Shipment Status": getattr(args, "shipment_status", None),
    }.items():
        column = mapping.get(field)
        if column and column in out.columns and values:
            out = out[out[column].astype(str).isin(values)]
    return out


def chart_specs(mapping: dict) -> list[tuple[str, str, Optional[str], Optional[str], Optional[str], str]]:
    return [
        ("monthly_demand_trend", "line", mapping.get("Date"), mapping.get("Demand"), None, "sum"),
        ("product_wise_demand", "bar", mapping.get("Product"), mapping.get("Demand"), None, "sum"),
        ("inventory_levels", "area", mapping.get("Date"), mapping.get("Inventory"), None, "sum"),
        ("abc_inventory_pareto", "pareto", mapping.get("SKU") or mapping.get("Product"), mapping.get("Inventory"), None, "sum"),
        ("supplier_purchase_cost", "bar", mapping.get("Supplier"), mapping.get("Procurement Cost") or mapping.get("Cost"), None, "sum"),
        ("supplier_defect_rate", "pie", mapping.get("Supplier"), mapping.get("Defective Units"), None, "sum"),
        ("route_transport_cost", "bar", mapping.get("Route"), mapping.get("Shipment Cost") or mapping.get("Logistics Cost"), None, "sum"),
        ("shipment_location_heatmap", "heatmap", mapping.get("Region"), mapping.get("Shipment Cost") or mapping.get("Logistics Cost"), mapping.get("Warehouse"), "sum"),
        ("warehouse_stock", "bar", mapping.get("Warehouse"), mapping.get("Inventory"), None, "sum"),
        ("production_volume", "line", mapping.get("Date"), mapping.get("Production Quantity"), None, "sum"),
        ("product_production", "bar", mapping.get("Product"), mapping.get("Production Quantity"), None, "sum"),
        ("cost_over_time", "line", mapping.get("Date"), mapping.get("Cost"), None, "sum"),
        ("cost_breakdown", "pie", mapping.get("Cost Category") or mapping.get("Category"), mapping.get("Cost"), None, "sum"),
    ]


def export_charts(df: pd.DataFrame, mapping: dict, charts_dir: Path, formats: set[str]) -> list[str]:
    charts_dir.mkdir(parents=True, exist_ok=True)
    exported: list[str] = []
    for name, chart_type, x_col, y_col, color_col, agg in chart_specs(mapping):
        if not x_col or x_col not in df.columns:
            continue
        if y_col and y_col not in df.columns:
            continue
        if color_col and color_col not in df.columns:
            color_col = None
        if color_col == x_col:
            color_col = None

        fig = make_chart(df, chart_type, x_col, y_col, color_col, agg, name.replace("_", " ").title())
        if "html" in formats:
            html_path = charts_dir / f"{name}.html"
            html_path.write_text(fig.to_html(include_plotlyjs=True), encoding="utf-8")
            exported.append(str(html_path))
        if "png" in formats:
            try:
                png = chart_png_bytes(df, chart_type, x_col, y_col, color_col, agg, name.replace("_", " ").title())
                png_path = charts_dir / f"{name}.png"
                png_path.write_bytes(png)
                exported.append(str(png_path))
            except Exception:
                continue
    return exported


def analyze(args: argparse.Namespace) -> int:
    init_storage(DB_PATH)
    sheets, source_name = load_source(args)
    raw_df = select_sheet(sheets, args.sheet)
    df = clean_data(
        raw_df,
        normalize_columns=not args.no_normalize_columns,
        convert_types=not args.no_convert_types,
        drop_duplicates=args.drop_duplicates,
        missing_strategy=args.missing_strategy,
    )
    if df.empty:
        raise ValueError("No rows remain after cleaning.")

    mapping = build_mapping(args, df, source_name)
    filtered = filter_dataframe(df, mapping, args)
    if filtered.empty:
        raise ValueError("No rows remain after filters.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    quality = data_quality_summary(filtered)
    kpis = get_all_kpis(filtered, mapping)
    kpi_df = kpis_to_frame(kpis)
    validation = validation_report(filtered, mapping)

    if args.validation_only:
        print(validation.to_json(orient="records", indent=2))
        log_audit_event(DB_PATH, "cli_validation", {"source": source_name, "rows": len(filtered)})
        return 0

    if args.export_cleaned:
        (output_dir / "cleaned_scm_data.csv").write_bytes(filtered.to_csv(index=False).encode("utf-8"))
        (output_dir / "cleaned_scm_data.xlsx").write_bytes(to_excel_bytes(filtered, "Cleaned_Data"))
    if args.export_kpis:
        (output_dir / "scm_kpi_table.csv").write_bytes(kpi_df.to_csv(index=False).encode("utf-8"))
        (output_dir / "scm_kpi_table.xlsx").write_bytes(to_excel_bytes(kpi_df, "KPI_Table"))
    if args.export_pdf:
        (output_dir / "scm_dashboard_summary.pdf").write_bytes(create_pdf_report(quality, kpis))
    if args.export_pptx:
        (output_dir / "scm_summary.pptx").write_bytes(powerpoint_summary_bytes(kpis, quality))
    if args.export_workbook:
        (output_dir / "scm_dashboard_workbook.xlsx").write_bytes(full_dashboard_workbook_bytes(filtered, mapping, kpis, quality))
    if args.export_glossary or args.export_formula_audit:
        glossary = pd.DataFrame([{"Metric": k, "Definition": v} for k, v in METRIC_GLOSSARY.items()])
        glossary.to_csv(output_dir / "metric_glossary.csv", index=False)
    if args.export_audit:
        pd.DataFrame(list_audit_events(DB_PATH)).to_csv(output_dir / "audit_log.csv", index=False)
    if args.export_chart_zip:
        (output_dir / "chart_bundle.zip").write_bytes(chart_bundle_zip_bytes(filtered, mapping))
    if args.export_calendar:
        business_calendar_table(filtered, mapping).to_csv(output_dir / "business_calendar.csv", index=False)
    if args.export_scenario:
        generated_forecast_table(filtered, mapping).to_csv(output_dir / "scenario_forecast.csv", index=False)
        landed_cost_table(filtered, mapping).to_csv(output_dir / "scenario_landed_cost.csv", index=False)
    if args.export_mapping_template:
        write_json(output_dir / "mapping_template.json", mapping)
    if args.export_failed_rows:
        failed_row_quarantine(filtered, mapping).to_csv(output_dir / "failed_row_quarantine.csv", index=False)

    write_json(output_dir / "data_quality_summary.json", quality)
    write_json(output_dir / "column_mapping.json", mapping)
    validation.to_csv(output_dir / "data_quality_issue_report.csv", index=False)

    formats = {fmt.strip().lower() for fmt in args.chart_formats.split(",") if fmt.strip()}
    exported_charts = export_charts(filtered, mapping, output_dir / "charts", formats)

    if args.save_sqlite:
        save_dataframe(filtered, DB_PATH, args.save_sqlite)

    log_audit_event(DB_PATH, "cli_analyze", {"source": source_name, "rows": len(filtered), "output_dir": str(output_dir)})
    summary = {
        "source": source_name,
        "rows": int(filtered.shape[0]),
        "columns": int(filtered.shape[1]),
        "output_dir": str(output_dir),
        "charts_exported": len(exported_charts),
    }
    print(json.dumps(summary, indent=2))
    return 0


def test_fixtures(args: argparse.Namespace) -> int:
    manifest = Path(args.manifest)
    if not manifest.exists():
        manifest = APP_DIR / "tests" / "fixtures" / "scm_analytics_studio_fixtures" / "00_manifest" / "manifest.csv"
    if not manifest.exists():
        raise FileNotFoundError(manifest)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_df = pd.read_csv(manifest)
    base = manifest.parent
    if base.name in {"00_manifest", "13_cli_export"}:
        base = base.parent
    rows = []
    tabular_formats = {"csv", "xlsx", "xls", "excel"}
    for _, item in manifest_df.iterrows():
        rel = item.get("file_name") or item.get("relative_path") or item.get("path") or item.get("file")
        if not isinstance(rel, str) or not rel:
            continue
        source = base / rel
        suffix = source.suffix.lower().lstrip(".")
        declared_format = str(item.get("format", suffix)).lower()
        if suffix not in tabular_formats and declared_format not in tabular_formats:
            rows.append({"fixture": str(source), "status": "SKIP", "detail": "Non-tabular fixture"})
            continue
        status = "PASS"
        detail = ""
        try:
            sheets = read_file(source)
            if not sheets:
                raise ValueError("No readable sheets")
            df = clean_data(combine_sheets(sheets) if len(sheets) > 1 else next(iter(sheets.values())))
            mapping = auto_map_columns(df)
            validation = validation_report(df, mapping)
            if df.empty:
                raise ValueError("Empty after cleaning")
            (output_dir / f"{source.stem}_validation.csv").write_text(validation.to_csv(index=False), encoding="utf-8")
        except Exception as exc:
            status = "FAIL"
            detail = str(exc)
        rows.append({"fixture": str(source), "status": status, "detail": detail})
    report = pd.DataFrame(rows)
    report.to_csv(output_dir / "fixture_regression_report.csv", index=False)
    print(json.dumps({
        "fixtures": len(report),
        "passed": int((report["status"] == "PASS").sum()),
        "failed": int((report["status"] == "FAIL").sum()),
        "skipped": int((report["status"] == "SKIP").sum()),
        "report": str(output_dir / "fixture_regression_report.csv"),
    }, indent=2))
    return 1 if args.strict and (report["status"] == "FAIL").any() else 0


def check_fixture_accuracy(args: argparse.Namespace) -> int:
    root = Path(args.fixture_root)
    if not root.is_absolute():
        root = APP_DIR / root
    report = fixture_pack_report(root)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, report)
    print(json.dumps({
        "fixture_root": report["fixture_root"],
        "tabular_passed": report["tabular_passed"],
        "tabular_failed": report["tabular_failed"],
        "skipped": report["skipped"],
        "average_mapped_fields": report["average_mapped_fields"],
        "golden_kpis_passed": report.get("golden_kpis", {}).get("passed"),
        "report": str(output),
    }, indent=2))
    return 1 if args.strict and (report["tabular_failed"] or not report.get("golden_kpis", {}).get("passed", True)) else 0


def serve(args: argparse.Namespace) -> int:
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(Path(__file__).resolve().parent / "app.py"),
        "--server.address",
        args.host,
        "--server.port",
        str(args.port),
        "--browser.gatherUsageStats",
        "false",
    ]
    return subprocess.call(cmd)


def serve_api(args: argparse.Namespace) -> int:
    cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent / "api_server.py"),
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]
    return subprocess.call(cmd)


def serve_mcp(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(Path(__file__).resolve().parent / "mcp_server.py")]
    return subprocess.call(cmd)


def list_saved(args: argparse.Namespace) -> int:
    init_storage(DB_PATH)
    print(json.dumps({"mappings": list_mappings(DB_PATH), "datasets": list_dataframes(DB_PATH), "audit": list_audit_events(DB_PATH, 20)}, indent=2))
    return 0


def backup_sqlite(args: argparse.Namespace) -> int:
    init_storage(DB_PATH)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(DB_PATH.read_bytes())
    print(json.dumps({"backup": str(target)}, indent=2))
    return 0


def restore_sqlite(args: argparse.Namespace) -> int:
    source = Path(args.input)
    if not source.exists():
        raise FileNotFoundError(source)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_bytes(source.read_bytes())
    print(json.dumps({"restored": str(DB_PATH)}, indent=2))
    return 0


def generate_sample(args: argparse.Namespace) -> int:
    sheets = load_sample_workbook(SAMPLE_WORKBOOK)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() == ".csv":
        sheets["Integrated_SCM_Data"].to_csv(out, index=False)
    else:
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            for name, df in sheets.items():
                df.to_excel(writer, sheet_name=name[:31], index=False)
    print(json.dumps({"sample": str(out)}, indent=2))
    return 0


def load_cli_dataset_for_workflow(args: argparse.Namespace) -> tuple[pd.DataFrame, dict, str]:
    init_storage(DB_PATH)
    sheets, source_name = load_source(args)
    raw_df = select_sheet(sheets, args.sheet)
    df = clean_data(raw_df)
    mapping = build_mapping(args, df, source_name)
    return filter_dataframe(df, mapping, args), mapping, source_name


def list_workflow_tools(args: argparse.Namespace) -> int:
    print(pd.DataFrame(list_tools()).to_json(orient="records", indent=2))
    return 0


def list_workflow_skills(args: argparse.Namespace) -> int:
    create_sample_skill()
    print(skill_catalog().to_json(orient="records", indent=2))
    return 0


def run_workflow_tool(args: argparse.Namespace) -> int:
    df, mapping, source_name = load_cli_dataset_for_workflow(args)
    params = json.loads(args.params or "{}")
    result = run_tool(args.tool, df, mapping, params)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    table = result.get("table")
    if isinstance(table, pd.DataFrame):
        table.to_csv(output_dir / f"{args.tool}.csv", index=False)
    print(json.dumps({"source": source_name, "tool": args.tool, "summary": result.get("summary", {}), "rows": result.get("row_count", 0)}, indent=2, default=str))
    return 0


def run_workflow_skill(args: argparse.Namespace) -> int:
    create_sample_skill()
    df, mapping, source_name = load_cli_dataset_for_workflow(args)
    params = json.loads(args.params or "{}")
    results = run_skill(args.skill, df, mapping, params)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for result in results:
        title = result.get("title", "result")
        file_name = f"{title.lower().replace(' ', '_').replace('/', '_')}.csv"
        table = result.get("table")
        if isinstance(table, pd.DataFrame):
            table.to_csv(output_dir / file_name, index=False)
        manifest.append({"title": title, "rows": result.get("row_count", 0), "summary": result.get("summary", {}), "file": file_name})
    write_json(output_dir / "workflow_manifest.json", manifest)
    print(json.dumps({"source": source_name, "skill": args.skill, "results": manifest}, indent=2, default=str))
    return 0


def add_workflow_dataset_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", help="CSV/XLSX/XLS input file. Defaults to bundled sample workbook.")
    parser.add_argument("--sheet", help="Excel sheet name, or 'Combine all sheets'.")
    parser.add_argument("--sqlite-table", help="Load a previously saved SQLite dataset instead of a file.")
    parser.add_argument("--mapping-profile", help="Saved mapping profile to apply.")
    parser.add_argument("--mapping-template", help="Import a JSON mapping template.")
    parser.add_argument("--map", action="append", help="Manual mapping override, for example --map Demand=Qty.")
    parser.add_argument("--date-start")
    parser.add_argument("--date-end")
    parser.add_argument("--product", action="append")
    parser.add_argument("--supplier", action="append")
    parser.add_argument("--region", action="append")
    parser.add_argument("--warehouse", action="append")
    parser.add_argument("--customer", action="append")
    parser.add_argument("--sku", action="append")
    parser.add_argument("--carrier", action="append")
    parser.add_argument("--route", action="append")
    parser.add_argument("--lot", action="append")
    parser.add_argument("--batch", action="append")
    parser.add_argument("--origin", action="append")
    parser.add_argument("--destination", action="append")
    parser.add_argument("--incoterm", action="append")
    parser.add_argument("--currency", action="append")
    parser.add_argument("--uom", action="append")
    parser.add_argument("--planner", action="append")
    parser.add_argument("--buyer", action="append")
    parser.add_argument("--po-status", action="append")
    parser.add_argument("--order-status", action="append")
    parser.add_argument("--shipment-status", action="append")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline CLI for SCM Analytics Studio.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Run the full offline SCM analysis and export files.")
    analyze_parser.add_argument("--input", help="CSV/XLSX/XLS input file. Defaults to bundled sample workbook.")
    analyze_parser.add_argument("--sheet", help="Excel sheet name, or 'Combine all sheets'. Defaults to Integrated_SCM_Data when available.")
    analyze_parser.add_argument("--sqlite-table", help="Load a previously saved SQLite dataset instead of a file.")
    analyze_parser.add_argument("--output-dir", default="exports/cli_run", help="Folder for exported CLI outputs.")
    analyze_parser.add_argument("--missing-strategy", default="keep", choices=["keep", "drop_rows", "fill_zero", "fill_forward", "fill_median_mode"])
    analyze_parser.add_argument("--drop-duplicates", action="store_true")
    analyze_parser.add_argument("--no-normalize-columns", action="store_true")
    analyze_parser.add_argument("--no-convert-types", action="store_true")
    analyze_parser.add_argument("--mapping-profile", help="Saved mapping profile to apply.")
    analyze_parser.add_argument("--mapping-template", help="Import a JSON mapping template.")
    analyze_parser.add_argument("--save-mapping", help="Save the resulting mapping under this profile name.")
    analyze_parser.add_argument("--map", action="append", help="Manual mapping override, for example --map Demand=Qty --map Date=Order_Date.")
    analyze_parser.add_argument("--date-start")
    analyze_parser.add_argument("--date-end")
    analyze_parser.add_argument("--product", action="append")
    analyze_parser.add_argument("--supplier", action="append")
    analyze_parser.add_argument("--region", action="append")
    analyze_parser.add_argument("--warehouse", action="append")
    analyze_parser.add_argument("--customer", action="append")
    analyze_parser.add_argument("--sku", action="append")
    analyze_parser.add_argument("--carrier", action="append")
    analyze_parser.add_argument("--route", action="append")
    analyze_parser.add_argument("--lot", action="append")
    analyze_parser.add_argument("--batch", action="append")
    analyze_parser.add_argument("--origin", action="append")
    analyze_parser.add_argument("--destination", action="append")
    analyze_parser.add_argument("--incoterm", action="append")
    analyze_parser.add_argument("--currency", action="append")
    analyze_parser.add_argument("--uom", action="append")
    analyze_parser.add_argument("--planner", action="append")
    analyze_parser.add_argument("--buyer", action="append")
    analyze_parser.add_argument("--po-status", action="append")
    analyze_parser.add_argument("--order-status", action="append")
    analyze_parser.add_argument("--shipment-status", action="append")
    analyze_parser.add_argument("--chart-formats", default="html,png", help="Comma-separated chart formats: html,png.")
    analyze_parser.add_argument("--export-cleaned", action=argparse.BooleanOptionalAction, default=True)
    analyze_parser.add_argument("--export-kpis", action=argparse.BooleanOptionalAction, default=True)
    analyze_parser.add_argument("--export-pdf", action=argparse.BooleanOptionalAction, default=True)
    analyze_parser.add_argument("--export-workbook", action="store_true")
    analyze_parser.add_argument("--export-pptx", action="store_true")
    analyze_parser.add_argument("--export-glossary", action="store_true")
    analyze_parser.add_argument("--export-audit", action="store_true")
    analyze_parser.add_argument("--export-chart-zip", action="store_true")
    analyze_parser.add_argument("--export-calendar", action="store_true")
    analyze_parser.add_argument("--export-scenario", action="store_true")
    analyze_parser.add_argument("--export-formula-audit", action="store_true")
    analyze_parser.add_argument("--export-mapping-template", action="store_true")
    analyze_parser.add_argument("--export-failed-rows", action="store_true")
    analyze_parser.add_argument("--save-sqlite", help="Optional local SQLite table name for cleaned filtered data.")
    analyze_parser.add_argument("--validation-only", action="store_true", help="Only run validation and print issues as JSON.")
    analyze_parser.set_defaults(func=analyze)

    serve_parser = subparsers.add_parser("serve", help="Run the Streamlit app.")
    serve_parser.add_argument("--host", default="localhost")
    serve_parser.add_argument("--port", type=int, default=3000)
    serve_parser.set_defaults(func=serve)

    api_parser = subparsers.add_parser("api-server", help="Run the local HTTP integration API.")
    api_parser.add_argument("--host", default="localhost")
    api_parser.add_argument("--port", type=int, default=8765)
    api_parser.set_defaults(func=serve_api)

    mcp_parser = subparsers.add_parser("mcp-server", help="Run the stdio MCP-style integration server.")
    mcp_parser.set_defaults(func=serve_mcp)

    list_parser = subparsers.add_parser("list-saved", help="List saved mapping profiles and SQLite datasets.")
    list_parser.set_defaults(func=list_saved)

    backup_parser = subparsers.add_parser("backup-sqlite", help="Export the local SQLite database.")
    backup_parser.add_argument("--output", default="exports/scm_analytics_studio.sqlite")
    backup_parser.set_defaults(func=backup_sqlite)

    restore_parser = subparsers.add_parser("restore-sqlite", help="Restore the local SQLite database from a backup.")
    restore_parser.add_argument("--input", required=True)
    restore_parser.set_defaults(func=restore_sqlite)

    sample_parser = subparsers.add_parser("generate-sample", help="Generate a sample CSV/XLSX file from bundled training data.")
    sample_parser.add_argument("--output", default="exports/generated_sample.xlsx")
    sample_parser.set_defaults(func=generate_sample)

    fixture_parser = subparsers.add_parser("test-fixtures", help="Run bundled spreadsheet fixtures and produce a pass/fail report.")
    fixture_parser.add_argument("--manifest", default="tests/fixtures/scm_analytics_studio_fixtures/00_manifest/manifest.csv")
    fixture_parser.add_argument("--output-dir", default="exports/fixture_regression")
    fixture_parser.add_argument("--strict", action="store_true", help="Exit with failure if any fixture fails.")
    fixture_parser.set_defaults(func=test_fixtures)

    fixture_accuracy_parser = subparsers.add_parser("check-fixture-accuracy", help="Process the full fixture pack and compare golden KPI expectations.")
    fixture_accuracy_parser.add_argument("--fixture-root", default="tests/fixtures/scm_analytics_studio_fixtures")
    fixture_accuracy_parser.add_argument("--output", default="exports/fixture_accuracy_report.json")
    fixture_accuracy_parser.add_argument("--strict", action="store_true")
    fixture_accuracy_parser.set_defaults(func=check_fixture_accuracy)

    subparsers.add_parser("list-tools", help="List local workflow tools.").set_defaults(func=list_workflow_tools)
    subparsers.add_parser("list-skills", help="List guided workflow skills.").set_defaults(func=list_workflow_skills)

    tool_parser = subparsers.add_parser("run-tool", help="Run one local tool against an SCM dataset.")
    add_workflow_dataset_args(tool_parser)
    tool_parser.add_argument("--tool", required=True)
    tool_parser.add_argument("--params", default="{}")
    tool_parser.add_argument("--output-dir", default="exports/tool_run")
    tool_parser.add_argument("--save-mapping")
    tool_parser.set_defaults(func=run_workflow_tool)

    skill_parser = subparsers.add_parser("run-skill", help="Run a guided workflow skill against an SCM dataset.")
    add_workflow_dataset_args(skill_parser)
    skill_parser.add_argument("--skill", required=True)
    skill_parser.add_argument("--params", default="{}")
    skill_parser.add_argument("--output-dir", default="exports/skill_run")
    skill_parser.add_argument("--save-mapping")
    skill_parser.set_defaults(func=run_workflow_skill)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
