"""Deterministic letter-wide section segmentation and timeline extraction.

Pure Python, zero LLM cost. Produces a compact structural + chronological
context block that a family extractor's prompt builder may optionally
include (see `docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md`,
Phase C). This is deliberately conservative and letter-wide, unlike
`frequency_section.py`'s SeizureFrequency-anchored parsing: it never emits a
`PredictedMention` or a clinical fact, only prompt context.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .normalizer import MONTH_NAME_PATTERN, normalize_month

_SECTION_HEADERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Diagnosis", re.compile(r"(?i)^\s*diagnosis\s*:")),
    ("SeizureFrequency", re.compile(r"(?i)^\s*seizure\s+type\s+and\s+frequency\s*:")),
    ("Medication", re.compile(r"(?i)^\s*(?:current\s+)?(?:anti[- ]?epileptic\s+)?medications?\s*:")),
    ("Investigations", re.compile(r"(?i)^\s*investigations?\s*:")),
    ("Plan", re.compile(r"(?i)^\s*(?:plan|comments?)\s*:?\s*$")),
)

_YEAR = r"(?:19|20)\d{2}"
_INVESTIGATION_LABEL = r"EEG|MRI|CT(?:\s+head)?|CT\s+scan|ECG"

_DATE_DMY = re.compile(rf"\b(?P<day>\d{{1,2}})[/.](?P<month>\d{{1,2}})[/.](?P<year>{_YEAR})\b")
_DATE_MONTH_YEAR = re.compile(rf"\b(?P<month>{MONTH_NAME_PATTERN})\s+(?P<year>{_YEAR})\b", re.IGNORECASE)
_DATE_LABELLED_YEAR = re.compile(rf"\b(?:{_INVESTIGATION_LABEL})\b[^.\n]{{0,40}}?\b(?P<year>{_YEAR})\b", re.IGNORECASE)

_RELATIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("since last clinic", re.compile(r"\bsince\s+(?:the\s+)?(?:last|previous)\s+(?:clinic|appointment|review|visit)\b", re.IGNORECASE)),
    ("N units ago", re.compile(r"\b(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?P<unit>year|month|week|day)s?\s+ago\b", re.IGNORECASE)),
    ("at age N", re.compile(r"\b(?:at\s+the\s+age\s+of|aged)\s+(?P<age>\d{1,3})\b", re.IGNORECASE)),
    ("at time of diagnosis", re.compile(r"\bat\s+the\s+time\s+of\s+diagnosis\b", re.IGNORECASE)),
    ("last year", re.compile(r"\blast\s+year\b", re.IGNORECASE)),
)

_MAX_TIMELINE_EVENTS = 8
_DEFAULT_MAX_CHARS = 600
_CONTEXT_RADIUS = 60


@dataclass(frozen=True)
class LetterSection:
    label: str
    text: str


@dataclass(frozen=True)
class TimelineEvent:
    context: str
    year: int | None
    month: int | None
    anchor: str | None


def segment_letter(note_text: str) -> list[LetterSection]:
    """Split a letter into a small ordered list of clinically-labeled sections.

    Unheaded content (including whole letters with no recognized heading,
    e.g. free-narrative clinic letters) collects under "Narrative".
    """
    lines = note_text.splitlines()
    sections: list[LetterSection] = []
    current_label = "Narrative"
    current_lines: list[str] = []

    def flush() -> None:
        text = "\n".join(current_lines).strip()
        if text:
            sections.append(LetterSection(label=current_label, text=text))

    for line in lines:
        matched_pattern: re.Pattern[str] | None = None
        matched_label = ""
        for label, pattern in _SECTION_HEADERS:
            if pattern.match(line):
                matched_label = label
                matched_pattern = pattern
                break
        if matched_pattern is not None:
            flush()
            current_label = matched_label
            remainder = matched_pattern.sub("", line, count=1).strip()
            current_lines = [remainder] if remainder else []
            continue
        current_lines.append(line)
    flush()
    return sections


def _context_window(text: str, start: int, end: int) -> str:
    lo = max(0, start - _CONTEXT_RADIUS)
    hi = min(len(text), end + _CONTEXT_RADIUS)
    # Snap to word boundaries so the LLM never sees a truncated leading/trailing
    # word fragment (e.g. "oing risk" instead of "ongoing risk").
    if lo > 0:
        next_space = text.find(" ", lo)
        if 0 <= next_space < start:
            lo = next_space + 1
    if hi < len(text):
        prev_space = text.rfind(" ", end, hi)
        if prev_space > end:
            hi = prev_space
    snippet = text[lo:hi].strip()
    snippet = re.sub(r"\s+", " ", snippet)
    return snippet


def build_timeline(note_text: str) -> list[TimelineEvent]:
    """Scan the whole letter for dated or relatively-anchored event mentions.

    Absolute-date events (resolved year, optionally month) are sorted
    chronologically; relative-anchor-only events (no resolvable absolute
    date) are appended afterward in document order.
    """
    dated: list[tuple[int, int, TimelineEvent]] = []
    relative: list[TimelineEvent] = []
    seen_spans: list[tuple[int, int]] = []

    def overlaps(span: tuple[int, int]) -> bool:
        return any(span[0] < e and span[1] > s for s, e in seen_spans)

    for match in _DATE_DMY.finditer(note_text):
        span = match.span()
        if overlaps(span):
            continue
        seen_spans.append(span)
        year = int(match.group("year"))
        month = int(match.group("month"))
        dated.append((year, month, TimelineEvent(
            context=_context_window(note_text, *span), year=year, month=month, anchor=None,
        )))

    for match in _DATE_MONTH_YEAR.finditer(note_text):
        span = match.span()
        if overlaps(span):
            continue
        seen_spans.append(span)
        year = int(match.group("year"))
        month = int(normalize_month(match.group("month")))
        dated.append((year, month, TimelineEvent(
            context=_context_window(note_text, *span), year=year, month=month, anchor=None,
        )))

    for match in _DATE_LABELLED_YEAR.finditer(note_text):
        span = match.span()
        if overlaps(span):
            continue
        seen_spans.append(span)
        year = int(match.group("year"))
        dated.append((year, 0, TimelineEvent(
            context=_context_window(note_text, *span), year=year, month=None, anchor=None,
        )))

    for anchor_label, pattern in _RELATIVE_PATTERNS:
        for match in pattern.finditer(note_text):
            span = match.span()
            if overlaps(span):
                continue
            seen_spans.append(span)
            relative.append(TimelineEvent(
                context=_context_window(note_text, *span), year=None, month=None, anchor=anchor_label,
            ))

    dated.sort(key=lambda row: (row[0], row[1]))
    return [event for _, _, event in dated] + relative


def render_context_block(
    sections: list[LetterSection],
    timeline: list[TimelineEvent],
    max_chars: int = _DEFAULT_MAX_CHARS,
) -> str:
    """Render a compact, length-bounded prompt-context block.

    Caps at `_MAX_TIMELINE_EVENTS` timeline entries and `max_chars` total
    characters so this cannot silently balloon prompt size/cost.
    """
    lines: list[str] = []
    if sections:
        labels = [s.label for s in sections if s.label != "Narrative"]
        if labels:
            lines.append("LETTER STRUCTURE: " + ", ".join(labels))

    shown = timeline[:_MAX_TIMELINE_EVENTS]
    if shown:
        lines.append("TIMELINE (references found in this letter, chronological where dated):")
        for event in shown:
            if event.year is not None:
                when = f"{event.year}" if event.month is None else f"{event.month}/{event.year}"
            else:
                when = f"relative: {event.anchor}"
            lines.append(f"- {when}: {event.context}")
        if len(timeline) > len(shown):
            lines.append(f"(+{len(timeline) - len(shown)} more references omitted)")

    block = "\n".join(lines)
    if len(block) > max_chars:
        block = block[:max_chars].rstrip() + " (truncated)"
    return block
