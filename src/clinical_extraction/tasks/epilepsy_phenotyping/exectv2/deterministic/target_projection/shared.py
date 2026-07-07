"""Shared helpers for target-indicator projection."""

from __future__ import annotations


def local_evidence_context(
    note_text: str,
    evidence: str,
    *,
    before: int,
    after: int,
) -> str:
    if not note_text or not evidence:
        return evidence
    lowered_note = note_text.lower()
    lowered_evidence = evidence.lower()
    index = lowered_note.find(lowered_evidence)
    if index < 0:
        return evidence
    start = max(0, index - before)
    end = min(len(note_text), index + len(evidence) + after)
    return note_text[start:end]


def period_to_canonical(period: str) -> str:
    normalized = period.strip().lower()
    if normalized.startswith("day"):
        return "Day"
    if normalized.startswith("week"):
        return "Week"
    if normalized.startswith("month"):
        return "Month"
    if normalized.startswith("year"):
        return "Year"
    return period


def clean_number(value: str) -> str:
    return value[:-2] if value.endswith(".0") else value
