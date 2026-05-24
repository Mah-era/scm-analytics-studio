from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from modules.advanced_features import (
    business_calendar_table,
    chart_bundle_zip_bytes,
    contract_analytics_table,
    failed_row_quarantine,
    full_dashboard_workbook_bytes,
    generated_forecast_table,
    inventory_aging_table,
    landed_cost_table,
    mrp_lite_table,
    powerpoint_summary_bytes,
    validation_report,
    warehouse_process_table,
)
from modules.column_mapper import auto_map_columns
from modules.data_cleaner import clean_data, data_quality_summary
from modules.data_loader import read_file
from modules.reporting import get_all_kpis
from modules.fixture_accuracy import fixture_pack_report
from modules.skill_registry import list_skills, run_skill
from modules.tool_registry import list_tools, run_tool
from cli import main as cli_main
from mcp_server import handle


FIXTURE = ROOT / "tests" / "fixtures" / "legacy" / "sample_data" / "clean_integrated_scm.csv"
NEW_FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "scm_analytics_studio_fixtures"


def fixture_frame():
    df = clean_data(next(iter(read_file(FIXTURE).values())))
    return df, auto_map_columns(df)


def test_advanced_tables_and_exports_smoke():
    df, mapping = fixture_frame()
    df["actual_price"] = df[mapping["Cost"]]
    df["contract_price"] = df["actual_price"] * 0.95
    mapping["Actual Price"] = "actual_price"
    mapping["Contract Price"] = "contract_price"
    quality = data_quality_summary(df)
    kpis = get_all_kpis(df, mapping)

    assert not generated_forecast_table(df, mapping).empty
    assert not inventory_aging_table(df, mapping).empty
    assert not contract_analytics_table(df, mapping).empty
    assert not landed_cost_table(df, mapping).empty
    assert not warehouse_process_table(df, mapping).empty
    assert not mrp_lite_table(df, mapping).empty
    assert not business_calendar_table(df, mapping).empty
    assert not validation_report(df, mapping).empty
    assert len(full_dashboard_workbook_bytes(df, mapping, kpis, quality)) > 1000
    assert len(chart_bundle_zip_bytes(df, mapping)) > 1000
    assert len(powerpoint_summary_bytes(kpis, quality)) > 1000


def test_failed_row_quarantine_flags_bad_values():
    df, mapping = fixture_frame()
    broken = df.head(3).copy()
    broken[mapping["Demand"]] = broken[mapping["Demand"]].astype(object)
    broken[mapping["Delivery Date"]] = broken[mapping["Delivery Date"]].astype(object)
    broken.loc[broken.index[0], mapping["Demand"]] = "bad-number"
    broken.loc[broken.index[1], mapping["Delivery Date"]] = "not-a-date"
    quarantine = failed_row_quarantine(broken, mapping)
    assert len(quarantine) >= 2


def test_cli_fixture_runner_and_export_parity(tmp_path):
    out = tmp_path / "exports"
    assert cli_main([
        "analyze",
        "--input", str(FIXTURE),
        "--output-dir", str(out),
        "--chart-formats", "html",
        "--export-workbook",
        "--export-chart-zip",
        "--export-calendar",
        "--export-scenario",
        "--export-formula-audit",
        "--export-mapping-template",
        "--export-failed-rows",
        "--export-pptx",
    ]) == 0
    for name in [
        "scm_dashboard_workbook.xlsx",
        "chart_bundle.zip",
        "business_calendar.csv",
        "metric_glossary.csv",
        "mapping_template.json",
        "failed_row_quarantine.csv",
        "scm_summary.pptx",
    ]:
        assert (out / name).exists()

    fixture_out = tmp_path / "fixture_regression"
    assert cli_main(["test-fixtures", "--manifest", str(NEW_FIXTURE_ROOT / "00_manifest" / "manifest.csv"), "--output-dir", str(fixture_out)]) == 0
    assert (fixture_out / "fixture_regression_report.csv").exists()


def test_workflow_tools_skills_and_cli(tmp_path):
    df, mapping = fixture_frame()
    assert any(tool["name"] == "forecast" for tool in list_tools())
    assert any(skill.name == "inventory_planner" for skill in list_skills())

    tool_result = run_tool("forecast", df, mapping, {"periods": 3})
    assert tool_result["row_count"] > 0

    skill_results = run_skill("inventory_planner", df, mapping)
    assert len(skill_results) >= 3
    assert all("title" in result for result in skill_results)

    tool_out = tmp_path / "tool"
    assert cli_main(["list-tools"]) == 0
    assert cli_main(["list-skills"]) == 0
    assert cli_main(["run-tool", "--input", str(FIXTURE), "--tool", "forecast", "--params", "{\"periods\": 2}", "--output-dir", str(tool_out)]) == 0
    assert (tool_out / "forecast.csv").exists()

    skill_out = tmp_path / "skill"
    assert cli_main(["run-skill", "--input", str(FIXTURE), "--skill", "inventory_planner", "--output-dir", str(skill_out)]) == 0
    assert (skill_out / "workflow_manifest.json").exists()


def test_new_fixture_pack_accuracy_and_mcp():
    report = fixture_pack_report(NEW_FIXTURE_ROOT)
    assert report["tabular_failed"] == 0
    assert report["golden_kpis"]["passed"] is True

    response = handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    assert response["result"]["tools"]

    call = handle({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "scm_run_tool",
            "arguments": {
                "input_path": str(NEW_FIXTURE_ROOT / "01_happy_path" / "full_integrated_dataset.csv"),
                "tool": "forecast",
                "params": {"periods": 2},
            },
        },
    })
    assert "Generated forecast" in call["result"]["content"][0]["text"]
