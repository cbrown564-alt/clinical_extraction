from __future__ import annotations

SEMANTICALLY_NEUTRAL_TEXT_ARTIFACTS: tuple[tuple[str, str], ...] = (
    ("\x026#8804;", "≤"),
    ("\x026 ", "≤ "),
    ("\x0264", "≤"),
    ("\x0260;", "≤"),
    ("\x0260", "≤"),
    ("\x00b", "≤"),
    ("\x0b", "≤"),
    ("\x1c", "≤"),
    ("\\u2264", "≤"),
    ("&le;", "≤"),
    ("&#8804;", "≤"),
    ("&#x2264;", "≤"),
    ("â€\x9d", '"'),
)


def evidence_is_substring(note_text: str, evidence: str) -> bool:
    """Return whether evidence appears exactly in the source note."""
    return bool(evidence) and evidence in note_text


def locate_evidence(note_text: str, evidence: str) -> tuple[int, int] | None:
    """Return character offsets for exact evidence, if present."""
    if not evidence:
        return None

    start = note_text.find(evidence)
    if start >= 0:
        return start, start + len(evidence)

    repaired = repair_evidence_text_if_source_exact(evidence, note_text)
    if not repaired or repaired == evidence:
        return None

    start = note_text.find(repaired)
    if start >= 0:
        return start, start + len(repaired)

    return None


def clean_semantically_neutral_text_artifacts(text: str) -> str:
    """Normalize mojibake/control artifacts that do not alter clinical semantics."""
    for before, after in SEMANTICALLY_NEUTRAL_TEXT_ARTIFACTS:
        text = text.replace(before, after)
    return text.replace("\x00", "")


def repair_evidence_text_if_source_exact(evidence: str, note_text: str) -> str:
    """Repair copy artifacts only when the result is exact source evidence."""

    if evidence_is_substring(note_text, evidence):
        return evidence
    repaired = clean_semantically_neutral_text_artifacts(evidence)
    if repaired and repaired != evidence and evidence_is_substring(note_text, repaired):
        return repaired
    case_repaired = repair_case_only_evidence_copy(repaired, note_text)
    if case_repaired != repaired:
        return case_repaired
    return evidence


def repair_case_only_evidence_copy(evidence: str, note_text: str) -> str:
    """Repair case-only copy drift when the case-correct source substring exists."""

    start = note_text.lower().find(evidence.lower())
    if start < 0:
        return evidence
    return note_text[start : start + len(evidence)]
