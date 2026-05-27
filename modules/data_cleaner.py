"""Data cleaning and quality checks."""
from __future__ import annotations

import re
import warnings
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd


DATE_KEYWORDS = ["date", "day", "month", "year", "received", "ordered", "promised"]
NUMERIC_KEYWORDS = [
    "qty", "quantity", "demand", "sales", "revenue", "cost", "price", "inventory",
    "stock", "lead", "time", "defect", "unit", "capacity", "downtime", "orders",
    "shipment", "space", "picks", "cogs", "margin", "forecast", "fulfilled",
]


def clean_numeric_text(series: pd.Series) -> pd.Series:
    """Normalize common offline spreadsheet numeric strings before parsing."""
    text = series.astype(str).str.strip()
    negative = text.str.match(r"^\(.*\)$")
    text = text.str.replace(r"^\((.*)\)$", r"\1", regex=True)
    text = text.str.replace(r"[$,৳%]", "", regex=True)
    text = text.str.replace(r"(?i)\b(bdt|usd|eur|gbp|inr|tk)\b", "", regex=True)
    text = text.str.replace(r"\s+", "", regex=True)
    text = text.replace({"": np.nan, "nan": np.nan, "None": np.nan, "NONE": np.nan})
    parsed = pd.to_numeric(text, errors="coerce")
    return parsed.where(~negative, -parsed)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Trim and standardize column names while preserving readability."""
    out = df.copy()
    out.columns = [
        re.sub(r"\s+", "_", str(c).strip()).strip("_")
        for c in out.columns
    ]
    return out


def _looks_like_date(col: str, s: pd.Series) -> bool:
    name = col.lower()
    if pd.api.types.is_datetime64_any_dtype(s):
        return True
    if pd.api.types.is_numeric_dtype(s):
        return False
    if any(k in name for k in DATE_KEYWORDS) or "delivery_date" in name:
        return True
    if s.dtype == "object":
        sample = s.dropna().astype(str).head(20)
        if len(sample) == 0:
            return False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            parsed = pd.to_datetime(sample, errors="coerce", dayfirst=False)
        return parsed.notna().mean() >= 0.7
    return False


def _looks_like_numeric(col: str, s: pd.Series) -> bool:
    if pd.api.types.is_numeric_dtype(s):
        return True
    name = col.lower()
    name_tokens = set(re.sub(r"[^a-z0-9]+", "_", name).strip("_").split("_"))
    if name_tokens.intersection({"id", "sku", "code"}):
        return False
    if any(k in name for k in NUMERIC_KEYWORDS):
        return True
    if s.dtype == "object":
        sample = s.dropna().astype(str).head(30)
        if len(sample) == 0:
            return False
        parsed = clean_numeric_text(sample)
        return parsed.notna().mean() >= 0.75
    return False


def auto_convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Try to convert date-like and numeric-like columns."""
    out = df.copy()

    for col in out.columns:
        if _looks_like_date(col, out[col]):
            converted = pd.to_datetime(out[col], errors="coerce")
            # Keep conversion only if it actually worked for many values or the column name is date-like.
            if converted.notna().sum() >= max(1, int(out[col].notna().sum() * 0.5)):
                out[col] = converted

    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            continue
        if _looks_like_numeric(col, out[col]):
            if out[col].dtype == "object":
                out[col] = clean_numeric_text(out[col])
            else:
                out[col] = pd.to_numeric(out[col], errors="coerce")

    return out


def clean_data(
    df: pd.DataFrame,
    normalize_columns: bool = True,
    convert_types: bool = True,
    drop_duplicates: bool = False,
    missing_strategy: str = "keep",
) -> pd.DataFrame:
    """Clean a dataframe using user-selected strategies.

    missing_strategy: keep | drop_rows | fill_zero | fill_forward | fill_median_mode
    """
    out = df.copy()

    if normalize_columns:
        out = normalize_column_names(out)

    if convert_types:
        out = auto_convert_types(out)

    if drop_duplicates:
        out = out.drop_duplicates()

    if missing_strategy == "drop_rows":
        out = out.dropna()
    elif missing_strategy == "fill_zero":
        out = out.fillna(0)
    elif missing_strategy == "fill_forward":
        out = out.ffill().bfill()
    elif missing_strategy == "fill_median_mode":
        for col in out.columns:
            if pd.api.types.is_numeric_dtype(out[col]):
                out[col] = out[col].fillna(out[col].median())
            elif pd.api.types.is_datetime64_any_dtype(out[col]):
                out[col] = out[col].fillna(out[col].mode().iloc[0] if not out[col].mode().empty else pd.NaT)
            else:
                mode = out[col].mode(dropna=True)
                out[col] = out[col].fillna(mode.iloc[0] if not mode.empty else "Unknown")

    return out


def data_quality_summary(df: pd.DataFrame) -> Dict[str, object]:
    """Return data quality stats for display."""
    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in df.columns if c not in numeric_cols and c not in date_cols]

    date_ranges = {}
    for c in date_cols:
        date_ranges[c] = {
            "min": str(df[c].min()) if df[c].notna().any() else None,
            "max": str(df[c].max()) if df[c].notna().any() else None,
        }

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "duplicate_rows": int(df.duplicated().sum()),
        "total_missing_values": int(df.isna().sum().sum()),
        "missing_by_column": df.isna().sum().sort_values(ascending=False).astype(int).to_dict(),
        "date_columns": date_cols,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "date_ranges": date_ranges,
    }


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    nums = df.select_dtypes(include="number")
    if nums.empty:
        return pd.DataFrame()
    return nums.describe().T.reset_index().rename(columns={"index": "column"})


def categorical_summary(df: pd.DataFrame, max_columns: int = 20) -> pd.DataFrame:
    cats = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_datetime64_any_dtype(df[c])]
    rows = []
    for col in cats[:max_columns]:
        rows.append(
            {
                "column": col,
                "unique_count": int(df[col].nunique(dropna=True)),
                "top_value": "" if df[col].dropna().empty else str(df[col].mode(dropna=True).iloc[0]),
            }
        )
    return pd.DataFrame(rows)
