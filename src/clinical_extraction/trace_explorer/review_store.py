"""Separate local persistence for frontend review decisions."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ReviewStore:
    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS review_decisions (
                    review_kind TEXT NOT NULL,
                    decision_key TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (review_kind, decision_key)
                )
                """
            )

    def save(self, review_kind: str, decision_key: str, payload: dict[str, Any]) -> dict[str, Any]:
        saved = dict(payload)
        saved["timestamp"] = str(saved.get("timestamp") or datetime.now(UTC).isoformat())
        encoded = json.dumps(saved, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO review_decisions(review_kind, decision_key, payload_json, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(review_kind, decision_key) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (review_kind, decision_key, encoded, saved["timestamp"]),
            )
        return saved

    def list(self, review_kind: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM review_decisions
                WHERE review_kind = ?
                ORDER BY updated_at, decision_key
                """,
                (review_kind,),
            ).fetchall()
        return [json.loads(str(row[0])) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=5.0)
