from __future__ import annotations


def normalize_frequency_label(label: str) -> str:
    """Normalize label text before Gan-compatible parsing.

    This is a placeholder for the first milestone: port the author-provided repair and
    parsing behavior under tests, preserving benchmark compatibility.
    """
    return " ".join(label.strip().lower().split())

