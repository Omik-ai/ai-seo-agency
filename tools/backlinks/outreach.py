"""Outreach tracker — SQLite-backed CRM for link building.

Tracks prospects, pitches, responses, and acquired links.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Prospect:
    id: int | None = None
    domain: str = ""
    contact_email: str | None = None
    contact_form: str | None = None
    page_url: str = ""
    anchor_text: str = ""
    target_url: str = ""
    status: str = "prospect"  # prospect | pitched | responded | acquired | rejected | noop
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""


DEFAULT_DB_PATH = Path("data/backlinks.db")


SCHEMA = """
CREATE TABLE IF NOT EXISTS prospects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL,
    contact_email TEXT,
    contact_form TEXT,
    page_url TEXT NOT NULL,
    anchor_text TEXT,
    target_url TEXT NOT NULL,
    status TEXT DEFAULT 'prospect',
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_status ON prospects(status);
CREATE INDEX IF NOT EXISTS idx_domain ON prospects(domain);
"""


class OutreachTracker:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def add_prospect(self, p: Prospect) -> int:
        now = datetime.utcnow().isoformat()
        p.created_at = now
        p.updated_at = now
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO prospects
                (domain, contact_email, contact_form, page_url, anchor_text, target_url, status, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (p.domain, p.contact_email, p.contact_form, p.page_url, p.anchor_text, p.target_url, p.status, p.notes, p.created_at, p.updated_at),
            )
            conn.commit()
            return cur.lastrowid or 0

    def update_status(self, prospect_id: int, status: str, notes: str = "") -> None:
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                "UPDATE prospects SET status = ?, notes = ?, updated_at = ? WHERE id = ?",
                (status, notes, now, prospect_id),
            )
            conn.commit()

    def list_prospects(self, status: str | None = None, limit: int = 100) -> list[Prospect]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            if status:
                rows = conn.execute(
                    "SELECT * FROM prospects WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM prospects ORDER BY updated_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [Prospect(**dict(r)) for r in rows]

    def stats(self) -> dict[str, int]:
        with self._connect() as conn:
            rows = conn.execute("SELECT status, COUNT(*) FROM prospects GROUP BY status").fetchall()
        return {status: count for status, count in rows}
