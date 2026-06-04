"""Instrument last-event date evidence without changing routing behavior."""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

MONTH_PATTERN = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?"
)
FULL_DATE_RE = re.compile(
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?[ /-](?:{MONTH_PATTERN})[ /-]\d{{2,4}}\b",
    flags=re.IGNORECASE,
)
FULL_MONTH_DATE_RE = re.compile(
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{MONTH_PATTERN})\s+\d{{2,4}}\b",
    flags=re.IGNORECASE,
)
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
    reference_date_available_rows = sum(
        row.get("note_or_reference_date_available") is True for row in rows
    )
    return {
        "component_name": "last_event_date_instrumentation",
        "row_count": len(rows),
        "date_signal_class_counts": dict(sorted(signal_counts.items())),
        "full_date_rows": signal_counts["full_date_detected"],
        "partial_date_rows": signal_counts["partial_date_missing_year"],
        "no_explicit_date_rows": signal_counts[
            "no_explicit_date_in_selected_evidence"
        ],
        "reference_date_available_rows": reference_date_available_rows,
        "automatic_release_ready_rows": release_ready_rows,
        "recommended_next_step": (
            "Add auditable duration derivation and conflict checks before any "
            "last-event automatic release."
        ),
        "claim_language": (
            "Validation-development date instrumentation for last-event review "
            "rows. It does not change prediction-bearing behavior, prompts, "
            "scorer policy, gold labels, locked-test behavior, verifier use, or "
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
            "| Row | Label | Date signal | Event dates | Reference dates |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | `{row['blocked_candidate_label']}` | "
            f"`{row['date_signal_class']}` | "
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
    return {
        "artifact_kind": "gan2026_last_event_date_instrumentation_row",
        "source_row_index": source_row_index,
        "review_lane": pressure.get("review_lane"),
        "final_action": pressure.get("final_action"),
        "decision_reason": pressure.get("decision_reason"),
        "blocked_candidate_label": residual.get("blocked_candidate_label"),
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
        "automatic_release_ready": False,
        "release_blocker": (
            "release_policy_not_implemented"
            if reference_date_available
            else "note_or_reference_date_missing"
        ),
        "claim_boundary": "validation_development_instrumentation_only",
    }


def _full_date_spans(text: str) -> list[str]:
    spans = [match.group(0) for match in FULL_DATE_RE.finditer(text)]
    spans.extend(match.group(0) for match in FULL_MONTH_DATE_RE.finditer(text))
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
