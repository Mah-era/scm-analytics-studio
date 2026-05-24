"""Workflow Assistant orchestration for local skills, tools, and optional LLM summaries."""
from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

from .llm_client import LLMConfig, summarize_with_llm
from .skill_registry import create_sample_skill, get_skill, list_skills, run_skill, skill_catalog
from .tool_registry import list_tools, run_tool


INTENT_KEYWORDS = {
    "forecast": "demand_forecaster",
    "demand": "demand_forecaster",
    "inventory": "inventory_planner",
    "stockout": "inventory_planner",
    "obsolete": "inventory_planner",
    "aging": "inventory_planner",
    "supplier": "procurement_manager",
    "contract": "procurement_manager",
    "ppv": "procurement_manager",
    "warehouse": "operations_control_tower",
    "mrp": "operations_control_tower",
    "landed": "operations_control_tower",
    "quality": "data_quality_command_center",
    "validate": "data_quality_command_center",
    "invalid": "data_quality_command_center",
}


def suggest_skill(user_request: str) -> str:
    text = user_request.lower()
    for keyword, skill_name in INTENT_KEYWORDS.items():
        if keyword in text:
            return skill_name
    return "operations_control_tower"


def summarize_results(results: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for result in results:
        summary = result.get("summary", {})
        rows.append({
            "Result": result.get("title", ""),
            "Rows": result.get("row_count", 0),
            "Summary": json.dumps(summary, default=str),
        })
    return pd.DataFrame(rows)


def local_narrative(results: list[dict[str, Any]]) -> str:
    lines = []
    for result in results:
        title = result.get("title", "Result")
        count = result.get("row_count", 0)
        summary = result.get("summary", {})
        if summary:
            details = ", ".join(f"{key}: {value}" for key, value in summary.items())
            lines.append(f"{title}: {count} rows. {details}.")
        else:
            lines.append(f"{title}: {count} rows.")
    return "\n".join(lines) if lines else "No workflow results were generated."


def render_workflow_assistant(df: pd.DataFrame, mapping: dict) -> None:
    st.subheader("Workflow Assistant")
    st.caption("Run local skills and tools against the current filtered data. Optional LLM summaries only run when explicitly enabled.")

    create_sample_skill()
    skills = list_skills()
    catalog = skill_catalog()
    tools = pd.DataFrame(list_tools())

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### Skills")
        st.dataframe(catalog, width="stretch", hide_index=True)
    with c2:
        st.markdown("#### Tools")
        st.dataframe(tools, width="stretch", hide_index=True)

    st.markdown("#### Run A Guided Workflow")
    user_request = st.text_input("Plain-English request", value="Find inventory risks and explain what to review first")
    suggested = suggest_skill(user_request)
    names = [skill.name for skill in skills]
    selected_skill = st.selectbox("Skill", names, index=names.index(suggested) if suggested in names else 0)
    skill = get_skill(selected_skill)
    st.info(skill.description)

    use_llm = st.checkbox("Use optional LLM summary", value=False)
    llm_model = st.text_input("LLM model", value="gpt-4o-mini", disabled=not use_llm)
    llm_key = st.text_input("OpenAI API key", value="", type="password", disabled=not use_llm)

    if st.button("Run workflow", width="stretch"):
        try:
            results = run_skill(selected_skill, df, mapping)
            st.session_state["workflow_results"] = results
            st.success(f"Workflow completed: {skill.title}")
        except Exception as exc:
            st.error(f"Workflow failed: {exc}")

    results = st.session_state.get("workflow_results", [])
    if results:
        st.markdown("#### Workflow Summary")
        summary_table = summarize_results(results)
        st.dataframe(summary_table, width="stretch", hide_index=True)
        narrative = local_narrative(results)
        if use_llm and llm_key:
            prompt = f"User request: {user_request}\n\nWorkflow results:\n{summary_table.to_csv(index=False)}"
            narrative = summarize_with_llm(prompt, LLMConfig(enabled=True, model=llm_model, api_key=llm_key))
        st.text_area("Narrative", value=narrative, height=180)

        for result in results:
            table = result.get("table")
            if isinstance(table, pd.DataFrame) and not table.empty:
                with st.expander(result.get("title", "Result"), expanded=False):
                    st.dataframe(table.head(500), width="stretch")
                    st.download_button(
                        f"Download {result.get('title', 'result')} CSV",
                        table.to_csv(index=False).encode("utf-8"),
                        file_name=f"{result.get('title', 'workflow_result').lower().replace(' ', '_')}.csv",
                        mime="text/csv",
                    )

    st.markdown("#### Run A Single Tool")
    tool_names = [tool["name"] for tool in list_tools()]
    selected_tool = st.selectbox("Tool", tool_names)
    params_text = st.text_area("Tool parameters JSON", value="{}", height=100)
    if st.button("Run tool", width="stretch"):
        try:
            result = run_tool(selected_tool, df, mapping, json.loads(params_text or "{}"))
            st.session_state["single_tool_result"] = result
        except Exception as exc:
            st.error(f"Tool failed: {exc}")

    single = st.session_state.get("single_tool_result")
    if single:
        st.markdown(f"#### {single.get('title', 'Tool Result')}")
        st.write(single.get("summary", {}))
        table = single.get("table")
        if isinstance(table, pd.DataFrame):
            st.dataframe(table, width="stretch")
