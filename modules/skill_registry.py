"""Plugin-style skill registry for guided SCM workflows."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .tool_registry import run_tool


APP_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = APP_DIR / "skills"


@dataclass(frozen=True)
class Skill:
    name: str
    title: str
    category: str
    description: str
    tools: list[str]
    prompts: list[str]
    params: dict[str, Any]
    source: str


BUILTIN_SKILLS = [
    Skill(
        name="data_quality_command_center",
        title="Data Quality Command Center",
        category="Data Quality",
        description="Run validation, failed-row quarantine, and business calendar checks.",
        tools=["data_quality", "failed_rows", "business_calendar"],
        prompts=["Check my data quality", "Find invalid rows", "Create fiscal calendar"],
        params={},
        source="builtin",
    ),
    Skill(
        name="inventory_planner",
        title="Inventory Planner",
        category="Inventory",
        description="Find stockout risk, ABC/XYZ classes, inventory aging, and reorder actions.",
        tools=["inventory_risk", "abc_xyz", "inventory_aging"],
        prompts=["Find stockout risks", "Segment my SKUs", "Show aging and obsolete stock"],
        params={},
        source="builtin",
    ),
    Skill(
        name="demand_forecaster",
        title="Demand Forecaster",
        category="Demand",
        description="Generate a forecast and summarize planning KPIs.",
        tools=["forecast", "kpi_snapshot"],
        prompts=["Forecast demand", "Build a forward demand view"],
        params={"forecast": {"method": "Moving average", "periods": 6, "window": 3}},
        source="builtin",
    ),
    Skill(
        name="procurement_manager",
        title="Procurement Manager",
        category="Procurement",
        description="Review supplier contract compliance, PPV, and open supply risk.",
        tools=["supplier_contracts", "kpi_snapshot"],
        prompts=["Analyze supplier contracts", "Find PPV and off-contract spend"],
        params={},
        source="builtin",
    ),
    Skill(
        name="operations_control_tower",
        title="Operations Control Tower",
        category="Operations",
        description="Run a cross-functional control tower pack with KPIs, warehouse flow, landed cost, and MRP-lite.",
        tools=["kpi_snapshot", "warehouse_process", "landed_cost", "mrp_lite"],
        prompts=["Run control tower", "Show operations risks", "Prepare executive action pack"],
        params={},
        source="builtin",
    ),
]


def _load_skill_file(path: Path) -> Skill:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return Skill(
        name=payload["name"],
        title=payload.get("title", payload["name"].replace("_", " ").title()),
        category=payload.get("category", "Custom"),
        description=payload.get("description", ""),
        tools=list(payload.get("tools", [])),
        prompts=list(payload.get("prompts", [])),
        params=dict(payload.get("params", {})),
        source=str(path),
    )


def list_skills(skills_dir: Path = SKILLS_DIR) -> list[Skill]:
    skills = list(BUILTIN_SKILLS)
    if skills_dir.exists():
        for path in sorted(skills_dir.glob("*.json")):
            try:
                skills.append(_load_skill_file(path))
            except Exception:
                continue
    return skills


def skill_catalog(skills_dir: Path = SKILLS_DIR) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "name": skill.name,
            "title": skill.title,
            "category": skill.category,
            "description": skill.description,
            "tools": ", ".join(skill.tools),
            "source": skill.source,
        }
        for skill in list_skills(skills_dir)
    ])


def get_skill(name: str, skills_dir: Path = SKILLS_DIR) -> Skill:
    for skill in list_skills(skills_dir):
        if skill.name == name:
            return skill
    raise ValueError(f"Unknown skill '{name}'.")


def run_skill(name: str, df: pd.DataFrame, mapping: dict, params: dict | None = None, skills_dir: Path = SKILLS_DIR) -> list[dict]:
    skill = get_skill(name, skills_dir)
    overrides = params or {}
    results = []
    for tool_name in skill.tools:
        tool_params = {}
        tool_params.update(skill.params.get(tool_name, {}))
        tool_params.update(overrides.get(tool_name, {}))
        results.append(run_tool(tool_name, df, mapping, tool_params))
    return results


def create_sample_skill(skills_dir: Path = SKILLS_DIR) -> Path:
    skills_dir.mkdir(parents=True, exist_ok=True)
    path = skills_dir / "inventory_exception_review.json"
    if not path.exists():
        path.write_text(
            json.dumps(
                {
                    "name": "inventory_exception_review",
                    "title": "Inventory Exception Review",
                    "category": "Inventory",
                    "description": "Custom example skill that focuses on SKU risk, segmentation, and failed rows.",
                    "tools": ["inventory_risk", "abc_xyz", "failed_rows"],
                    "prompts": ["Review inventory exceptions", "Find risky SKUs"],
                    "params": {},
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return path
