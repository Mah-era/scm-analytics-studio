"""Data loading utilities for SCM Analytics Studio.

All functions work offline and avoid external APIs.
"""
from __future__ import annotations

import contextlib
from io import StringIO
from pathlib import Path
from typing import Dict, Iterable, Tuple

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def read_file(uploaded_file) -> Dict[str, pd.DataFrame]:
    """Read an uploaded CSV/XLSX/XLS file into a dict of sheet_name -> dataframe.

    Streamlit UploadedFile objects and local file paths are both supported.
    """
    name = getattr(uploaded_file, "name", str(uploaded_file))
    suffix = Path(name).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}. Use CSV, XLSX, or XLS.")

    if suffix == ".csv":
        df = pd.read_csv(uploaded_file)
        return {"CSV_Data": df}

    # Excel: load all sheets. Legacy BIFF .xls files need xlrd explicitly.
    engine = "xlrd" if suffix == ".xls" else "openpyxl"
    if suffix == ".xls":
        with contextlib.redirect_stdout(StringIO()):
            sheets = pd.read_excel(uploaded_file, sheet_name=None, engine=engine)
    else:
        sheets = pd.read_excel(uploaded_file, sheet_name=None, engine=engine)
    return {str(k): v for k, v in sheets.items()}


def load_sample_workbook(sample_path: str | Path) -> Dict[str, pd.DataFrame]:
    """Load the packaged sample workbook."""
    sample_path = Path(sample_path)
    if not sample_path.exists():
        return {}
    return read_file(sample_path)


def infer_column_types(df: pd.DataFrame) -> pd.DataFrame:
    """Return a small dataframe showing detected column types and examples."""
    rows = []
    for col in df.columns:
        s = df[col]
        non_null = s.dropna()
        example = non_null.iloc[0] if len(non_null) else ""
        rows.append(
            {
                "column": col,
                "pandas_dtype": str(s.dtype),
                "missing_count": int(s.isna().sum()),
                "missing_pct": round(float(s.isna().mean() * 100), 2),
                "unique_count": int(s.nunique(dropna=True)),
                "example": str(example)[:80],
            }
        )
    return pd.DataFrame(rows)


def combine_sheets(sheets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Combine multiple sheets into one dataframe, adding a source_sheet column."""
    frames = []
    for name, df in sheets.items():
        tmp = df.copy()
        tmp["source_sheet"] = name
        frames.append(tmp)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)
