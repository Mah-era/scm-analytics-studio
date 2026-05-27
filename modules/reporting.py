"""Offline export and report helpers shared by the UI and CLI."""
from __future__ import annotations

from io import BytesIO
from typing import Dict

import pandas as pd

from . import (
    cost_analysis,
    demand_analysis,
    inventory_analysis,
    logistics_analysis,
    procurement_analysis,
    production_analysis,
    warehouse_analysis,
)


def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Cleaned_Data") -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return output.getvalue()


def kpis_to_frame(kpi_groups: Dict[str, Dict[str, object]]) -> pd.DataFrame:
    rows = []
    for module, kpis in kpi_groups.items():
        for metric, value in kpis.items():
            rows.append({"Module": module, "Metric": metric, "Value": value})
    return pd.DataFrame(rows)


def get_all_kpis(df: pd.DataFrame, mapping: dict) -> Dict[str, Dict[str, object]]:
    return {
        "Demand & Sales": demand_analysis.build_kpis(df, mapping),
        "Inventory": inventory_analysis.build_kpis(df, mapping),
        "Procurement": procurement_analysis.build_kpis(df, mapping),
        "Logistics": logistics_analysis.build_kpis(df, mapping),
        "Warehouse": warehouse_analysis.build_kpis(df, mapping),
        "Production": production_analysis.build_kpis(df, mapping),
        "Cost & Profitability": cost_analysis.build_kpis(df, mapping),
    }


def create_pdf_report(quality: dict, kpis: Dict[str, Dict[str, object]]) -> bytes:
    """Create a compact PDF summary report fully offline."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="SCM Analytics Studio Summary")
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("SCM Analytics Studio - Dashboard Summary", styles["Title"]))
    story.append(Spacer(1, 12))

    quality_rows = [
        ["Rows", quality.get("rows", 0)],
        ["Columns", quality.get("columns", 0)],
        ["Duplicate Rows", quality.get("duplicate_rows", 0)],
        ["Total Missing Values", quality.get("total_missing_values", 0)],
        ["Date Columns", ", ".join(quality.get("date_columns", [])) or "None"],
    ]
    q_table = Table([["Data Quality Metric", "Value"]] + quality_rows, hAlign="LEFT")
    q_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(Paragraph("Data Quality", styles["Heading2"]))
    story.append(q_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("KPI Summary", styles["Heading2"]))
    kpi_rows = [["Module", "Metric", "Value"]]
    for module, metrics in kpis.items():
        for metric, value in metrics.items():
            if isinstance(value, float):
                value = f"{value:,.2f}"
            kpi_rows.append([module, metric, str(value)])
    kpi_table = Table(kpi_rows, hAlign="LEFT", repeatRows=1)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(kpi_table)

    doc.build(story)
    return buffer.getvalue()
