"""Instrument last-event date evidence without changing routing behavior."""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

MONTH_PATTERN = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?"
)
MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}
FULL_DATE_RE = re.compile(
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?[ /-](?:{MONTH_PATTERN})[ /-]\d{{2,4}}\b",
    flags=re.IGNORECASE,
)
FULL_MONTH_DATE_RE = re.compile(
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{MONTH_PATTERN})\s+\d{{2,4}}\b",
    flags=re.IGNORECASE,
)
FULL_SLASH_DATE_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
PARTIAL_DATE_RE = re.compile(
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?(?:[ /-](?:{MONTH_PATTERN})|\s+(?:{MONTH_PATTERN}))\b",
    flags=re.IGNORECASE,
)


def build_last_event_date_rows(
    pressure_rows: Sequence[Mapping[str, Any]],
    residual_rows: Sequence[Mapping[str, Any]],
    *,
    source_records: Sequence[Any] = (),
) -> list[dict[str, Any]]:
    """Build date instrumentation rows for last-event review lanes."""

    residual_by_source = {
        int(row["source_row_index"]): row
        for row in residual_rows
        if row.get("source_row_index") is not None
    }
    source_by_index = {
        int(_record_value(record, "source_row_index")): record
        for record in source_records
        if _record_value(record, "source_row_index") is not None
    }
    rows = []
    for pressure in pressure_rows:
        if pressure.get("review_lane") != "date_policy_needed":
            continue
        source_row_index = int(pressure["source_row_index"])
        residual = residual_by_source.get(source_row_index, {})
        rows.append(
            _date_instrumentation_row(
                source_row_index,
                pressure,
                residual,
                source_by_index.get(source_row_index),
            )
        )
    return rows


def summarize_last_event_date_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize last-event date instrumentation rows."""

    signal_counts = Counter(str(row.get("date_signal_class")) for row in rows)
    release_ready_rows = sum(
        row.get("automatic_release_ready") is True for row in rows
    )
    duration_auditable_rows = sum(row.get("duration_auditable") is True for row in rows)
    reference_date_available_rows = sum(
        row.get("note_or_reference_date_available") is True for row in rows
    )
    blocker_counts = Counter(str(row.get("release_blocker")) for row in rows)
    return {
        "component_name": "last_event_date_instrumentation",
        "policy_name": "last_event_duration_policy_v0",
        "row_count": len(rows),
        "date_signal_class_counts": dict(sorted(signal_counts.items())),
        "release_blocker_counts": dict(sorted(blocker_counts.items())),
        "full_date_rows": signal_counts["full_date_detected"],
        "partial_date_rows": signal_counts["partial_date_missing_year"],
        "no_explicit_date_rows": signal_counts[
            "no_explicit_date_in_selected_evidence"
        ],
        "reference_date_available_rows": reference_date_available_rows,
        "duration_auditable_rows": duration_auditable_rows,
        "automatic_release_ready_rows": release_ready_rows,
        "recommended_next_step": (
            "Use duration-auditable rows only after the candidate-level promotion "
            "gate confirms no deterministic-correct regression and no evidence "
            "or source-id defect."
        ),
        "claim_language": (
            "Validation-development last-event duration policy for review rows. "
            "It derives auditable durations and conflict flags, but does not "
            "itself change prediction-bearing behavior, prompts, scorer policy, "
            "gold labels, locked-test behavior, verifier use, or "
            "benchmark-comparable claims."
        ),
    }


def write_summary_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Last-Event Date Instrumentation",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        (
            f"The review covers {summary['row_count']} last-event rows. "
            f"{summary['full_date_rows']} "
            f"{_row_word(summary['full_date_rows'])} "
            f"{_contain_word(summary['full_date_rows'])} a full date, "
            f"{summary['partial_date_rows']} contain a partial date, and "
            f"{summary['no_explicit_date_rows']} contain no explicit date in "
            "the selected evidence."
        ),
        (
            f"Reference-date anchors are available for "
            f"{summary['reference_date_available_rows']} rows."
        ),
        f"Duration-auditable rows: {summary['duration_auditable_rows']}.",
        "",
        "## Release Readiness",
        "",
        (
            f"Automatic release-ready rows: "
            f"{summary['automatic_release_ready_rows']}."
        ),
        "",
        "## Date Signal Classes",
        "",
        "| Class | Rows |",
        "| --- | ---: |",
    ]
    for signal_class, count in summary["date_signal_class_counts"].items():
        lines.append(f"| `{signal_class}` | {count} |")
    lines.extend(
        [
            "",
            "## Release Blockers",
            "",
            "| Blocker | Rows |",
            "| --- | ---: |",
        ]
    )
    for blocker, count in summary.get("release_blocker_counts", {}).items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Date instrumentation JSONL: `{jsonl_path}`",
            f"- Date instrumentation summary JSON: `{json_path}`",
            "",
            "## Rows",
            "",
            "| Row | Label | Date signal | Derived duration | Blocker | "
            "Event dates | Reference dates |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | `{row['blocked_candidate_label']}` | "
            f"`{row['date_signal_class']}` | "
            f"`{row.get('derived_duration_label') or ''}` | "
            f"`{row.get('release_blocker') or ''}` | "
            f"`{_joined_date_spans(row)}` | "
            f"`{', '.join(row['reference_date_spans'])}` |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _date_instrumentation_row(
    source_row_index: int,
    pressure: Mapping[str, Any],
    residual: Mapping[str, Any],
    source_record: Any | None,
) -> dict[str, Any]:
    evidence = str(residual.get("blocked_candidate_evidence") or "")
    full_dates = _full_date_spans(evidence)
    partial_dates = _partial_date_spans(evidence, full_dates)
    signal_class = _date_signal_class(full_dates, partial_dates)
    reference_dates, reference_source = _reference_date_spans(source_record)
    reference_date_available = bool(reference_dates)
    parsed_event_dates = [_parse_full_date(span) for span in full_dates]
    parsed_reference_dates = [_parse_full_date(span) for span in reference_dates]
    conflict_flags = _conflict_flags(evidence, parsed_event_dates, parsed_reference_dates)
    derived = _derive_duration(parsed_event_dates, parsed_reference_dates)
    duration_auditable = (
        derived is not None
        and not partial_dates
        and not conflict_flags
        and _has_event_target(evidence)
    )
    pressure_class = str(pressure.get("pressure_class") or "")
    label = str(residual.get("blocked_candidate_label") or "")
    release_blocker = _release_blocker(
        signal_class=signal_class,
        reference_date_available=reference_date_available,
        duration_auditable=duration_auditable,
        pressure_class=pressure_class,
        label=label,
        conflict_flags=conflict_flags,
    )
    return {
        "artifact_kind": "gan2026_last_event_date_instrumentation_row",
        "policy_name": "last_event_duration_policy_v0",
        "source_row_index": source_row_index,
        "review_lane": pressure.get("review_lane"),
        "pressure_class": pressure.get("pressure_class"),
        "final_action": pressure.get("final_action"),
        "decision_reason": pressure.get("decision_reason"),
        "blocked_candidate_label": label,
        "blocked_candidate_evidence": residual.get("blocked_candidate_evidence"),
        "blocked_candidate_source_ids": residual.get(
            "blocked_candidate_source_ids", []
        ),
        "explicit_date_spans": full_dates,
        "partial_date_spans": partial_dates,
        "date_signal_class": signal_class,
        "reference_date_spans": reference_dates,
        "reference_date_source": reference_source,
        "note_or_reference_date_available": reference_date_available,
        "parsed_event_dates": [_format_date(value) for value in parsed_event_dates],
        "parsed_reference_dates": [
            _format_date(value) for value in parsed_reference_dates
        ],
        "duration_days": derived["days"] if derived else None,
        "derived_duration_label": derived["label"] if derived else None,
        "derived_duration_months_floor": derived["months_floor"] if derived else None,
        "event_target_present": _has_event_target(evidence),
        "conflict_flags": conflict_flags,
        "duration_auditable": duration_auditable,
        "promotion_gate_ready": release_blocker == "manual_promotion_required",
        "automatic_release_ready": False,
        "release_blocker": release_blocker,
        "claim_boundary": "validation_development_duration_policy_only",
    }


def _full_date_spans(text: str) -> list[str]:
    spans = [match.group(0) for match in FULL_DATE_RE.finditer(text)]
    spans.extend(match.group(0) for match in FULL_MONTH_DATE_RE.finditer(text))
    spans.extend(match.group(0) for match in FULL_SLASH_DATE_RE.finditer(text))
    return _dedupe_preserving_order(spans)


def _partial_date_spans(text: str, full_dates: Sequence[str]) -> list[str]:
    spans = []
    for match in PARTIAL_DATE_RE.finditer(text):
        span = match.group(0)
        if any(span in full_date for full_date in full_dates):
            continue
        spans.append(span)
    return _dedupe_preserving_order(spans)


def _date_signal_class(
    full_dates: Sequence[str],
    partial_dates: Sequence[str],
) -> str:
    if full_dates:
        return "full_date_detected"
    if partial_dates:
        return "partial_date_missing_year"
    return "no_explicit_date_in_selected_evidence"


def _dedupe_preserving_order(values: Sequence[str]) -> list[str]:
    seen = set()
    deduped = []
    for value in values:
        normalized = value.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(value)
    return deduped


def _reference_date_spans(source_record: Any | None) -> tuple[list[str], str | None]:
    if source_record is None:
        return [], None
    note_text = str(_record_value(source_record, "note_text") or "")
    for label, source in (
        ("Clinic Date:", "clinic_date_header"),
        ("Sent:", "sent_header"),
        ("Review Date:", "review_date_header"),
        ("Date:", "date_header"),
    ):
        spans = _dates_after_label(note_text, label)
        if spans:
            return spans, source
    return [], None


def _dates_after_label(text: str, label: str) -> list[str]:
    label_index = text.find(label)
    if label_index < 0:
        return []
    snippet = text[label_index + len(label) : label_index + len(label) + 80]
    return _full_date_spans(snippet)


def _parse_full_date(span: str) -> date | None:
    cleaned = re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", span, flags=re.IGNORECASE)
    cleaned = cleaned.replace("-", " ").replace("/", " ")
    parts = cleaned.split()
    if len(parts) != 3:
        return None
    try:
        day = int(parts[0])
        month_token = parts[1].lower().rstrip(".")
        if month_token.isdigit():
            month = int(month_token)
        else:
            month = MONTHS[month_token]
        year = int(parts[2])
        if year < 100:
            year += 2000 if year < 50 else 1900
        return date(year, month, day)
    except (KeyError, ValueError):
        return None


def _derive_duration(
    event_dates: Sequence[date | None],
    reference_dates: Sequence[date | None],
) -> dict[str, Any] | None:
    event_date = _single_parsed_date(event_dates)
    reference_date = _single_parsed_date(reference_dates)
    if event_date is None or reference_date is None:
        return None
    days = (reference_date - event_date).days
    if days < 0:
        return None
    months_floor = days // 30
    years_floor = days // 365
    if years_floor >= 2:
        label = "seizure free for multiple year"
    elif years_floor == 1:
        label = "seizure free for 1 year"
    elif months_floor >= 1:
        label = f"seizure free for {months_floor} month"
    else:
        label = f"seizure free for {max(days, 0)} day"
    return {"days": days, "months_floor": months_floor, "label": label}


def _single_parsed_date(values: Sequence[date | None]) -> date | None:
    parsed = [value for value in values if value is not None]
    if len(parsed) != 1:
        return None
    return parsed[0]


def _conflict_flags(
    evidence: str,
    event_dates: Sequence[date | None],
    reference_dates: Sequence[date | None],
) -> list[str]:
    flags = []
    if len([value for value in event_dates if value is not None]) > 1:
        flags.append("multiple_full_event_dates")
    if len([value for value in reference_dates if value is not None]) > 1:
        flags.append("multiple_reference_dates")
    if _single_parsed_date(event_dates) and _single_parsed_date(reference_dates):
        if _single_parsed_date(event_dates) > _single_parsed_date(reference_dates):
            flags.append("event_date_after_reference_date")
    lowered = evidence.lower()
    if "another seizure" in lowered or "subsequent seizure" in lowered:
        flags.append("subsequent_event_language")
    return flags


def _has_event_target(evidence: str) -> bool:
    lowered = evidence.lower()
    return any(
        term in lowered
        for term in ("seizure", "seizures", "episode", "episodes", "event", "events")
    )


def _release_blocker(
    *,
    signal_class: str,
    reference_date_available: bool,
    duration_auditable: bool,
    pressure_class: str,
    label: str,
    conflict_flags: Sequence[str],
) -> str:
    if not reference_date_available:
        return "note_or_reference_date_missing"
    if signal_class == "partial_date_missing_year":
        return "partial_date_missing_year"
    if signal_class == "no_explicit_date_in_selected_evidence":
        return "no_explicit_date_in_selected_evidence"
    if conflict_flags:
        return "conflict_flags_present"
    if not duration_auditable:
        return "duration_not_auditable"
    if not label.startswith("seizure free for "):
        return "non_seizure_free_label"
    if pressure_class == "protective_block":
        return "protective_block_validation_accounting"
    return "manual_promotion_required"


def _format_date(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _record_value(record: Any, key: str) -> Any:
    if isinstance(record, Mapping):
        return record.get(key)
    return getattr(record, key, None)


def _joined_date_spans(row: Mapping[str, Any]) -> str:
    spans = list(row.get("explicit_date_spans") or [])
    spans.extend(row.get("partial_date_spans") or [])
    return ", ".join(spans)


def _row_word(count: Any) -> str:
    return "row" if count == 1 else "rows"


def _contain_word(count: Any) -> str:
    return "contains" if count == 1 else "contain"
