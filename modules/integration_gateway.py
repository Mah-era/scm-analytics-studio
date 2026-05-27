"""Shared helpers for MCP and local HTTP API integrations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .column_mapper import auto_map_columns
from .data_cleaner import clean_data, data_quality_summary
from .data_loader import combine_sheets, read_file
from .skill_registry import run_skill, skill_catalog
from .tool_registry import list_tools, run_tool


APP_DIR = Path(__file__).resolve().parents[1]


def resolve_path(value: str | None) -> Path:
    if not value:
        raise ValueError("input_path is required.")
    path = Path(value)
    if not path.is_absolute():
        path = APP_DIR / path
    return path


def load_dataset(input_path: str, sheet: str | None = None, mapping_template: str | None = None) -> tuple[pd.DataFrame, dict]:
    source = resolve_path(input_path)
    sheets = read_file(source)
    if not sheets:
        raise ValueError(f"No readable tabular data found in {source}.")
    if sheet == "Combine all sheets" or (sheet is None and len(sheets) > 1):
        raw = combine_sheets(sheets)
    elif sheet:
        if sheet not in sheets:
            raise ValueError(f"Sheet '{sheet}' not found. Available sheets: {', '.join(sheets)}")
        raw = sheets[sheet]
    else:
        raw = next(iter(sheets.values()))
    df = clean_data(raw)
    mapping = auto_map_columns(df)
    if mapping_template:
        template_path = resolve_path(mapping_template)
        template = json.loads(template_path.read_text(encoding="utf-8"))
        mapping.update({field: col for field, col in template.items() if col in df.columns})
    return df, mapping


def dataframe_preview(df: pd.DataFrame, limit: int = 50) -> list[dict[str, Any]]:
    return df.head(limit).where(pd.notna(df.head(limit)), None).to_dict(orient="records")


def serialize_result(result: dict[str, Any], preview_rows: int = 50) -> dict[str, Any]:
    table = result.get("table")
    payload = {key: value for key, value in result.items() if key != "table"}
    if isinstance(table, pd.DataFrame):
        payload["columns"] = list(table.columns)
        payload["preview"] = dataframe_preview(table, preview_rows)
    return payload


def run_tool_on_file(input_path: str, tool_name: str, params: dict | None = None, sheet: str | None = None, mapping_template: str | None = None) -> dict[str, Any]:
    df, mapping = load_dataset(input_path, sheet, mapping_template)
    result = run_tool(tool_name, df, mapping, params or {})
    payload = serialize_result(result)
    payload["source_rows"] = int(len(df))
    payload["source_columns"] = int(df.shape[1])
    return payload


def run_skill_on_file(input_path: str, skill_name: str, params: dict | None = None, sheet: str | None = None, mapping_template: str | None = None) -> dict[str, Any]:
    df, mapping = load_dataset(input_path, sheet, mapping_template)
    results = run_skill(skill_name, df, mapping, params or {})
    return {
        "skill": skill_name,
        "source_rows": int(len(df)),
        "source_columns": int(df.shape[1]),
        "results": [serialize_result(result) for result in results],
    }


def inspect_dataset(input_path: str, sheet: str | None = None, mapping_template: str | None = None) -> dict[str, Any]:
    df, mapping = load_dataset(input_path, sheet, mapping_template)
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "quality": data_quality_summary(df),
        "mapping": mapping,
        "preview": dataframe_preview(df, 20),
    }


def integration_catalog() -> dict[str, Any]:
    skills = skill_catalog()
    return {
        "tools": list_tools(),
        "skills": skills.where(pd.notna(skills), None).to_dict(orient="records"),
    }
