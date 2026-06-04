from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from models import Item


SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_name TEXT,
  source_type TEXT,
  title TEXT,
  url TEXT UNIQUE,
  published_at TEXT,
  raw_text TEXT,
  summary TEXT,
  product_name TEXT,
  category TEXT,
  score INTEGER,
  reason TEXT,
  is_consumer_ai INTEGER,
  is_ai_for_fun INTEGER,
  experience_innovation TEXT,
  why_it_matters TEXT,
  created_at TEXT
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    ensure_columns(conn)
    return conn


def ensure_columns(conn: sqlite3.Connection) -> None:
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(items)").fetchall()}
    additions = {
        "experience_innovation": "TEXT",
        "why_it_matters": "TEXT",
    }
    for name, column_type in additions.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE items ADD COLUMN {name} {column_type}")
    conn.commit()


def insert_items(conn: sqlite3.Connection, items: Iterable[Item]) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    count = 0
    for item in items:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO items (
              source_name, source_type, title, url, published_at, raw_text,
              summary, product_name, category, score, reason,
              is_consumer_ai, is_ai_for_fun, experience_innovation,
              why_it_matters, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.source_name,
                item.source_type,
                item.title,
                item.url,
                item.published_at,
                item.raw_text,
                item.summary,
                item.product_name,
                item.category,
                item.score,
                item.reason,
                int(bool(item.is_consumer_ai)),
                int(bool(item.is_ai_for_fun)),
                item.experience_innovation,
                item.why_it_matters,
                created_at,
            ),
        )
        count += cursor.rowcount
    conn.commit()
    return count


def fetch_weekly_items(conn: sqlite3.Connection, start_iso: str, min_score: int = 6) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT *
        FROM items
        WHERE created_at >= ?
          AND score >= ?
          AND is_consumer_ai = 1
          AND is_ai_for_fun = 1
        ORDER BY score DESC, created_at DESC
        """,
        (start_iso, min_score),
    ).fetchall()
