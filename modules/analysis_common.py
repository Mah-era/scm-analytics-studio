"""Shared Streamlit display helpers for analysis modules."""
from __future__ import annotations

from typing import Dict

import pandas as pd
import streamlit as st


def show_kpis(kpis: Dict[str, object], columns: int = 4):
    if not kpis:
        st.info("No KPI available for the current mapping.")
        return
    cols = st.columns(min(columns, max(1, len(kpis))))
    for i, (label, value) in enumerate(kpis.items()):
        with cols[i % len(cols)]:
            if isinstance(value, float):
                st.metric(label, f"{value:,.2f}")
            else:
                st.metric(label, value)


def field(mapping: dict, name: str):
    value = mapping.get(name)
    return value if value else None


def has_cols(df: pd.DataFrame, *cols) -> bool:
    return all(c and c in df.columns for c in cols)


def show_fig(fig, key: str):
    st.plotly_chart(fig, width="stretch", key=key)
