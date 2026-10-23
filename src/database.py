"""SQLite connection & query helpers for Telecom Nexus."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "telecom_nexus.db"


def get_db_path() -> Path:
    custom = os.environ.get("TELECOM_NEXUS_DB")
    if custom:
        return Path(custom)
    return DEFAULT_DB_PATH


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    target = db_path or get_db_path()
    if not target.exists():
        from data.seed_telecom_data import seed_all

        seed_all(target)
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    return conn


def fetch_all(query: str, params: tuple[Any, ...] = (), db_path: Path | None = None) -> list[dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def fetch_one(query: str, params: tuple[Any, ...] = (), db_path: Path | None = None) -> dict[str, Any] | None:
    with get_connection(db_path) as conn:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None


def execute_write(query: str, params: tuple[Any, ...] = (), db_path: Path | None = None) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(query, params)
        conn.commit()
        return cur.rowcount
