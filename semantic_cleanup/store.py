"""SQLite storage for validated semantic entries; used only during builds."""

from __future__ import annotations

from contextlib import AbstractContextManager
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable

from .schema import validate_semantic_entry


class SemanticStore(AbstractContextManager):
    def __init__(self, path: Path | str, *, writable: bool = False):
        self.path = Path(path)
        if not writable and not self.path.exists():
            raise FileNotFoundError(self.path)
        if writable:
            self.connection = sqlite3.connect(self.path)
        else:
            self.connection = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        if writable:
            self.connection.execute(
                "CREATE TABLE IF NOT EXISTS semantic_entries (word TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )

    def get(self, word: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT payload FROM semantic_entries WHERE word = ?", (word,)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def upsert_many(self, entries: Iterable[dict[str, Any]], *, limits: dict[str, int] | None = None) -> int:
        values = []
        for entry in entries:
            normalized = validate_semantic_entry(entry, limits=limits)
            values.append((normalized["word"], json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))))
        with self.connection:
            self.connection.executemany(
                "INSERT INTO semantic_entries(word, payload) VALUES (?, ?) "
                "ON CONFLICT(word) DO UPDATE SET payload=excluded.payload",
                values,
            )
        return len(values)

    def close(self) -> None:
        self.connection.close()

    def __exit__(self, *args: object) -> None:
        self.close()
