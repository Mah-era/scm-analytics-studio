"""SQLite local storage for offline mappings and optional data snapshots."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


def _connect(db_path: str | Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _safe_identifier(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", str(name).strip()).strip("_")
    if not cleaned:
        cleaned = "scm_data"
    if cleaned[0].isdigit():
        cleaned = f"scm_{cleaned}"
    return cleaned[:60]


def init_storage(db_path: str | Path) -> None:
    """Create the offline SQLite schema if it does not exist."""
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mapping_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                source_name TEXT,
                columns_json TEXT NOT NULL,
                mapping_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dataset_snapshots (
                table_name TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                rows_count INTEGER NOT NULL,
                columns_count INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                detail_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dashboard_templates (
                name TEXT PRIMARY KEY,
                config_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                contact TEXT,
                category TEXT NOT NULL,
                rating INTEGER,
                message TEXT NOT NULL,
                context_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_mapping(
    db_path: str | Path,
    name: str,
    mapping: Dict[str, Optional[str]],
    columns: List[str],
    source_name: str = "",
) -> None:
    """Save or update a reusable column mapping profile."""
    init_storage(db_path)
    profile_name = str(name).strip()
    if not profile_name:
        raise ValueError("Mapping profile name is required.")

    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO mapping_profiles (name, source_name, columns_json, mapping_json)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                source_name = excluded.source_name,
                columns_json = excluded.columns_json,
                mapping_json = excluded.mapping_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                profile_name,
                source_name,
                json.dumps(list(columns)),
                json.dumps(mapping),
            ),
        )


def list_mappings(db_path: str | Path) -> List[Dict[str, Any]]:
    """Return saved mapping profile metadata."""
    init_storage(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT name, source_name, created_at, updated_at
            FROM mapping_profiles
            ORDER BY updated_at DESC, name ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def load_mapping(db_path: str | Path, name: str) -> Dict[str, Optional[str]]:
    """Load one saved mapping profile by name."""
    init_storage(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT mapping_json FROM mapping_profiles WHERE name = ?",
            (name,),
        ).fetchone()
    if row is None:
        return {}
    return json.loads(row["mapping_json"])


def delete_mapping(db_path: str | Path, name: str) -> None:
    init_storage(db_path)
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM mapping_profiles WHERE name = ?", (name,))


def save_dataframe(df: pd.DataFrame, db_path: str | Path, table_name: str = "scm_data") -> None:
    """Save a cleaned dataset to a local SQLite table."""
    init_storage(db_path)
    safe_table = _safe_identifier(table_name)
    with _connect(db_path) as conn:
        df.to_sql(safe_table, conn, if_exists="replace", index=False)
        conn.execute(
            """
            INSERT INTO dataset_snapshots (table_name, display_name, rows_count, columns_count)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(table_name) DO UPDATE SET
                display_name = excluded.display_name,
                rows_count = excluded.rows_count,
                columns_count = excluded.columns_count,
                updated_at = CURRENT_TIMESTAMP
            """,
            (safe_table, str(table_name), int(df.shape[0]), int(df.shape[1])),
        )


def load_dataframe(db_path: str | Path, table_name: str = "scm_data") -> pd.DataFrame:
    """Load a previously saved local SQLite dataset."""
    db_path = Path(db_path)
    if not db_path.exists():
        return pd.DataFrame()
    safe_table = _safe_identifier(table_name)
    with _connect(db_path) as conn:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (safe_table,),
        ).fetchone()
        if exists is None:
            return pd.DataFrame()
        return pd.read_sql_query(f'SELECT * FROM "{safe_table}"', conn)


def list_dataframes(db_path: str | Path) -> List[Dict[str, Any]]:
    """Return saved dataset snapshot metadata."""
    init_storage(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT table_name, display_name, rows_count, columns_count, created_at, updated_at
            FROM dataset_snapshots
            ORDER BY updated_at DESC, display_name ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def log_audit_event(db_path: str | Path, action: str, detail: Dict[str, Any] | None = None) -> None:
    init_storage(db_path)
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO audit_log (action, detail_json) VALUES (?, ?)",
            (action, json.dumps(detail or {}, default=str)),
        )


def list_audit_events(db_path: str | Path, limit: int = 200) -> List[Dict[str, Any]]:
    init_storage(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT action, detail_json, created_at FROM audit_log ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["detail"] = json.loads(item.pop("detail_json") or "{}")
        out.append(item)
    return out


def save_dashboard_template(db_path: str | Path, name: str, config: Dict[str, Any]) -> None:
    init_storage(db_path)
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO dashboard_templates (name, config_json)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET
                config_json = excluded.config_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (name, json.dumps(config, default=str)),
        )


def list_dashboard_templates(db_path: str | Path) -> List[Dict[str, Any]]:
    init_storage(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name, config_json, updated_at FROM dashboard_templates ORDER BY updated_at DESC"
        ).fetchall()
    return [{"name": r["name"], "config": json.loads(r["config_json"]), "updated_at": r["updated_at"]} for r in rows]


def save_feedback(
    db_path: str | Path,
    *,
    name: str,
    contact: str,
    category: str,
    rating: int,
    message: str,
    context: Dict[str, Any] | None = None,
) -> None:
    """Save one user feedback entry to the local offline SQLite database."""
    init_storage(db_path)
    if not str(message).strip():
        raise ValueError("Feedback message is required.")
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO user_feedback (name, contact, category, rating, message, context_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(name).strip(),
                str(contact).strip(),
                str(category).strip() or "General",
                int(rating),
                str(message).strip(),
                json.dumps(context or {}, default=str),
            ),
        )


def list_feedback(db_path: str | Path, limit: int = 500) -> List[Dict[str, Any]]:
    """Return recent user feedback entries."""
    init_storage(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, name, contact, category, rating, message, context_json, created_at
            FROM user_feedback
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["context"] = json.loads(item.pop("context_json") or "{}")
        out.append(item)
    return out
