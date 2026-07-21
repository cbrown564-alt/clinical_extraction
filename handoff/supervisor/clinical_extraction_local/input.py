"""Strict JSONL input for private notes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import InputValidationError


@dataclass(frozen=True)
class InputNote:
    note_id: str
    text: str


def read_notes(path: Path) -> list[InputNote]:
    notes: list[InputNote] = []
    seen: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise InputValidationError(f"cannot read {path.name}") from exc
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row: Any = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InputValidationError(f"line {line_number}: invalid JSON") from exc
        if not isinstance(row, dict):
            raise InputValidationError(f"line {line_number}: expected an object")
        unknown = sorted(set(row) - {"id", "text"})
        if unknown:
            raise InputValidationError(
                f"line {line_number}: unknown fields are not allowed: {', '.join(unknown)}"
            )
        note_id = row.get("id")
        text = row.get("text")
        if not isinstance(note_id, str) or not note_id.strip():
            raise InputValidationError(f"line {line_number}: id must be a non-empty string")
        if not isinstance(text, str) or not text.strip():
            raise InputValidationError(f"line {line_number}: text must be a non-empty string")
        if note_id in seen:
            raise InputValidationError(f"line {line_number}: duplicate id")
        seen.add(note_id)
        notes.append(InputNote(note_id=note_id, text=text))
    if not notes:
        raise InputValidationError("the input contains no notes")
    return notes

