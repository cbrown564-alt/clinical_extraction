from __future__ import annotations

import re

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
    ("\\n", "\n"),
    ("\\t", "\t"),
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
    whitespace_repaired = repair_whitespace_evidence_copy(repaired, note_text)
    if whitespace_repaired != repaired:
        return whitespace_repaired
    ellipsis_repaired = repair_ellipsis_span_evidence_copy(repaired, note_text)
    if ellipsis_repaired != repaired:
        return ellipsis_repaired
    section_repaired = repair_section_header_list_item_evidence_copy(repaired, note_text)
    if section_repaired != repaired:
        return section_repaired
    return evidence


def repair_case_only_evidence_copy(evidence: str, note_text: str) -> str:
    """Repair case-only copy drift when the case-correct source substring exists."""

    start = note_text.lower().find(evidence.lower())
    if start < 0:
        return evidence
    return note_text[start : start + len(evidence)]


def repair_whitespace_evidence_copy(evidence: str, note_text: str) -> str:
    """Repair case plus whitespace copy drift to the exact source span."""

    span = _find_flexible_whitespace_span(note_text, evidence)
    if span is None:
        return evidence
    start, end = span
    repaired = note_text[start:end]
    return repaired if repaired != evidence else evidence


def repair_ellipsis_span_evidence_copy(
    evidence: str,
    note_text: str,
    *,
    max_gap_chars: int = 600,
) -> str:
    """Repair model ``...`` omissions to one bounded exact source span."""

    parts = [part.strip() for part in re.split(r"\s*(?:\.{3}|…)\s*", evidence) if part.strip()]
    if len(parts) < 2:
        return evidence

    start: int | None = None
    end: int | None = None
    search_from = 0
    for part in parts:
        span = _find_flexible_whitespace_span(note_text, part, start=search_from)
        if span is None:
            return evidence
        part_start, part_end = span
        if start is None:
            start = part_start
        if end is not None and part_start - end > max_gap_chars:
            return evidence
        end = part_end
        search_from = part_end

    if start is None or end is None:
        return evidence
    repaired = note_text[start:end]
    return repaired if repaired != evidence else evidence


def repair_section_header_list_item_evidence_copy(
    evidence: str,
    note_text: str,
    *,
    max_section_chars: int = 1000,
) -> str:
    """Repair ``header + selected list item`` evidence to the source section span."""

    parts = _split_section_header_and_item(evidence)
    if parts is None:
        return evidence
    header, item = parts
    header_span = _find_flexible_whitespace_span(note_text, header)
    if header_span is None:
        return evidence

    section_start = header_span[0]
    section_limit = min(len(note_text), section_start + max_section_chars)
    blank_line = re.search(r"\n\s*\n", note_text[header_span[1] : section_limit])
    if blank_line:
        section_limit = header_span[1] + blank_line.start()

    item_span = _find_flexible_whitespace_span(
        note_text[:section_limit],
        item,
        start=header_span[1],
    )
    if item_span is None:
        return evidence

    repaired = note_text[section_start : item_span[1]]
    return repaired if repaired != evidence else evidence


def _split_section_header_and_item(evidence: str) -> tuple[str, str] | None:
    stripped = evidence.strip()
    colon_index = stripped.find(":")
    if 0 <= colon_index <= 80:
        header = stripped[: colon_index + 1]
        item = stripped[colon_index + 1 :].strip()
        return (header, item) if item else None

    tab_index = stripped.find("\t")
    if 0 <= tab_index <= 80:
        header = stripped[:tab_index].strip()
        item = stripped[tab_index + 1 :].strip()
        return (header, item) if header and item else None

    numbered = re.match(r"^([A-Za-z][A-Za-z /-]{2,60})\s+(\d+[.)]\s+.+)$", stripped)
    if numbered:
        return numbered.group(1).strip(), numbered.group(2).strip()
    return None


def _find_flexible_whitespace_span(
    note_text: str,
    evidence: str,
    *,
    start: int = 0,
) -> tuple[int, int] | None:
    if not evidence:
        return None
    suffix = note_text[start:]
    pattern = "".join(r"\s+" if char.isspace() else re.escape(char) for char in evidence)
    match = re.search(pattern, suffix, flags=re.IGNORECASE)
    if not match:
        return None
    return start + match.start(), start + match.end()
