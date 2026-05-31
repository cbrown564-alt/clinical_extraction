from __future__ import annotations


def evidence_is_substring(note_text: str, evidence: str) -> bool:
    """Return whether evidence appears exactly in the source note."""
    return bool(evidence) and evidence in note_text


def locate_evidence(note_text: str, evidence: str) -> tuple[int, int] | None:
    """Return character offsets for exact evidence, if present."""
    if not evidence:
        return None
    start = note_text.find(evidence)
    if start < 0:
        return None
    return start, start + len(evidence)

