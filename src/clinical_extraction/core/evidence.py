from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import overload

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
    words = [re.escape(word) for word in evidence.split() if word]
    if not words:
        return None
    pattern = r"\s+".join(words)
    match = re.search(pattern, suffix, flags=re.IGNORECASE)
    if not match:
        return None
    return start + match.start(), start + match.end()


class EvidenceGrade(StrEnum):
    EXACT = "EXACT"
    REPAIRED_ARTIFACT = "REPAIRED_ARTIFACT"
    REPAIRED_CASE = "REPAIRED_CASE"
    REPAIRED_WHITESPACE = "REPAIRED_WHITESPACE"
    REPAIRED_ELLIPSIS = "REPAIRED_ELLIPSIS"
    REPAIRED_SECTION = "REPAIRED_SECTION"
    ABSENT = "ABSENT"
    EMPTY = "EMPTY"


GROUNDED_GRADES: frozenset[EvidenceGrade] = frozenset(
    grade
    for grade in EvidenceGrade
    if grade.name.startswith("EXACT") or grade.name.startswith("REPAIRED_")
)


def grade_evidence(note_text: str, evidence: str) -> EvidenceGrade:
    """Classify one evidence string using the existing repair cascade priority."""

    if not str(evidence or "").strip():
        return EvidenceGrade.EMPTY
    if evidence_is_substring(note_text, evidence):
        return EvidenceGrade.EXACT

    repaired = clean_semantically_neutral_text_artifacts(evidence)
    if repaired and repaired != evidence and evidence_is_substring(note_text, repaired):
        return EvidenceGrade.REPAIRED_ARTIFACT

    case_repaired = repair_case_only_evidence_copy(repaired, note_text)
    if case_repaired != repaired and evidence_is_substring(note_text, case_repaired):
        return EvidenceGrade.REPAIRED_CASE

    whitespace_repaired = repair_whitespace_evidence_copy(repaired, note_text)
    if whitespace_repaired != repaired and evidence_is_substring(note_text, whitespace_repaired):
        return EvidenceGrade.REPAIRED_WHITESPACE

    ellipsis_repaired = repair_ellipsis_span_evidence_copy(repaired, note_text)
    if ellipsis_repaired != repaired and evidence_is_substring(note_text, ellipsis_repaired):
        return EvidenceGrade.REPAIRED_ELLIPSIS

    section_repaired = repair_section_header_list_item_evidence_copy(repaired, note_text)
    if section_repaired != repaired and evidence_is_substring(note_text, section_repaired):
        return EvidenceGrade.REPAIRED_SECTION

    return EvidenceGrade.ABSENT


def is_grounded(grade: EvidenceGrade) -> bool:
    return grade in GROUNDED_GRADES


@dataclass(frozen=True)
class EvidenceGroundedness:
    total: int
    grounded: int
    exact: int
    by_grade: dict[EvidenceGrade, int]
    per_item: tuple[tuple[str, EvidenceGrade], ...]

    @property
    def grounded_rate(self) -> float | None:
        if self.total <= 0:
            return None
        return round(self.grounded / self.total, 4)

    @property
    def exact_rate(self) -> float | None:
        if self.total <= 0:
            return None
        return round(self.exact / self.total, 4)


def _coerce_evidence_items(evidence: str | Sequence[str]) -> tuple[str, ...]:
    if isinstance(evidence, str):
        return (evidence,)
    return tuple(str(item) for item in evidence)


@overload
def score_evidence_set(note_text: str, evidence: str) -> EvidenceGroundedness: ...


@overload
def score_evidence_set(note_text: str, evidence: Sequence[str]) -> EvidenceGroundedness: ...


def score_evidence_set(
    note_text: str,
    evidence: str | Sequence[str],
) -> EvidenceGroundedness:
    """Grade one evidence string or a set of strings against ``note_text``."""

    items = _coerce_evidence_items(evidence)
    per_item: list[tuple[str, EvidenceGrade]] = []
    by_grade: Counter[EvidenceGrade] = Counter()
    for item in items:
        grade = grade_evidence(note_text, item)
        per_item.append((item, grade))
        by_grade[grade] += 1

    total = len(items)
    grounded = sum(count for grade, count in by_grade.items() if is_grounded(grade))
    exact = by_grade.get(EvidenceGrade.EXACT, 0)
    return EvidenceGroundedness(
        total=total,
        grounded=grounded,
        exact=exact,
        by_grade=dict(by_grade),
        per_item=tuple(per_item),
    )
