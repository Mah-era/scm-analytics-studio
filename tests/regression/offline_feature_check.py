"""Offline regression check for SCM Analytics Studio.

Run from the project root with:
    python tests/regression/offline_feature_check.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from modules import (
    cost_analysis,
    demand_analysis,
    inventory_analysis,
    logistics_analysis,
    procurement_analysis,
    production_analysis,
    warehouse_analysis,
)
from modules.chart_generator import chart_png_bytes, grouped_bar, make_chart, pareto_chart, time_series
from modules.column_mapper import auto_map_columns
from modules.data_cleaner import clean_data, data_quality_summary
from modules.data_loader import load_sample_workbook
from modules.local_storage import (
    init_storage,
    list_dataframes,
    list_mappings,
    load_dataframe,
    load_mapping,
    save_dataframe,
    save_mapping,
)
from modules.reporting import create_pdf_report, get_all_kpis, kpis_to_frame, to_excel_bytes
from cli import main as cli_main

SAMPLE_WORKBOOK = ROOT / "sample_data" / "sample_scm_data.xlsx"


def main() -> None:
    sheets = load_sample_workbook(SAMPLE_WORKBOOK)
    df = clean_data(sheets["Integrated_SCM_Data"])
    mapping = auto_map_columns(df)
    quality = data_quality_summary(df)

    module_builders = [
        demand_analysis.build_kpis,
        inventory_analysis.build_kpis,
        procurement_analysis.build_kpis,
        logistics_analysis.build_kpis,
        warehouse_analysis.build_kpis,
        production_analysis.build_kpis,
        cost_analysis.build_kpis,
    ]
    for build_kpis in module_builders:
        result = build_kpis(df, mapping)
        assert result, build_kpis.__module__

    chart_specs = {
        "line": (mapping["Date"], mapping["Demand"], None),
        "bar": (mapping["Product"], mapping["Demand"], None),
        "pie": (mapping["Region"], mapping["Demand"], None),
        "scatter": (mapping["Inventory"], mapping["Demand"], None),
        "histogram": (mapping["Demand"], None, None),
        "box": (mapping["Region"], mapping["Demand"], None),
        "heatmap": (mapping["Region"], mapping["Demand"], mapping["Warehouse"]),
        "area": (mapping["Date"], mapping["Demand"], None),
        "treemap": (mapping["Product"], mapping["Demand"], None),
        "pareto": (mapping["Product"], mapping["Demand"], None),
    }
    for chart_type, (x_col, y_col, color_col) in chart_specs.items():
        fig = make_chart(df, chart_type, x_col, y_col, color_col, "sum", chart_type)
        assert len(fig.to_html()) > 1000, chart_type
        assert len(chart_png_bytes(df, chart_type, x_col, y_col, color_col, "sum", chart_type)) > 1000, chart_type

    all_kpis = get_all_kpis(df, mapping)
    assert len(to_excel_bytes(df)) > 1000
    assert len(to_excel_bytes(kpis_to_frame(all_kpis), "KPI_Table")) > 1000
    assert len(create_pdf_report(quality, all_kpis)) > 1000

    db_path = ROOT / "data" / "offline_feature_check.sqlite"
    init_storage(db_path)
    save_mapping(db_path, "sample", mapping, list(df.columns), "sample_scm_data.xlsx")
    assert load_mapping(db_path, "sample")["Demand"] == "Demand"
    assert list_mappings(db_path)
    save_dataframe(df.head(5), db_path, "sample_snapshot")
    assert load_dataframe(db_path, "sample_snapshot").shape == (5, df.shape[1])
    assert list_dataframes(db_path)
    db_path.unlink(missing_ok=True)

    sparse_df = df[["Date", "Product"]].head(5)
    sparse_mapping = auto_map_columns(sparse_df)
    assert get_all_kpis(sparse_df, sparse_mapping)
    assert len(make_chart(sparse_df, "bar", "Product", None, None, "count", "Sparse").to_html()) > 1000

    wrong_type_df = df[["Date", "Product"]].head(5).assign(Demand="not numeric")
    assert len(grouped_bar(wrong_type_df, "Product", "Demand", "Bad Bar").to_html()) > 1000
    assert len(time_series(wrong_type_df, "Date", "Demand", title="Bad Trend").to_html()) > 1000
    assert len(pareto_chart(wrong_type_df, "Product", "Demand", "Bad Pareto").to_html()) > 1000

    cli_dir = ROOT / "exports" / "offline_feature_check"
    assert cli_main(["analyze", "--output-dir", str(cli_dir), "--chart-formats", "html,png"]) == 0
    assert cli_main(["analyze", "--output-dir", str(cli_dir), "--validation-only"]) == 0
    assert cli_main(["generate-sample", "--output", str(cli_dir / "generated_sample.csv")]) == 0
    assert cli_main(["backup-sqlite", "--output", str(cli_dir / "backup.sqlite")]) == 0
    assert (cli_dir / "cleaned_scm_data.csv").exists()
    assert (cli_dir / "scm_kpi_table.xlsx").exists()
    assert (cli_dir / "scm_dashboard_summary.pdf").exists()
    assert any((cli_dir / "charts").glob("*.html"))
    assert any((cli_dir / "charts").glob("*.png"))
    assert (cli_dir / "generated_sample.csv").exists()
    assert (cli_dir / "backup.sqlite").exists()

    print("Offline feature check passed.")


if __name__ == "__main__":
    main()
