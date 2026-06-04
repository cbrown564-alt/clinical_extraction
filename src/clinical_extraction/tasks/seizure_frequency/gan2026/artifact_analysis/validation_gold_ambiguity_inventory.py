"""Build a validation750 gold-label ambiguity review CSV."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    GanFrequencyRecord,
    load_records_for_split,
)

DEFAULT_CSV_PATH = Path(
    "experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.json"
)

FIELDNAMES = (
    "manual_ambiguity_label",
    "manual_notes",
    "manual_corrected_gold_label",
    "validation_order",
    "source_row_index",
    "split",
    "gold_label",
    "gold_label_kind",
    "gold_reference",
    "codex_initial_ambiguity_label",
    "codex_ambiguity_reasons",
    "codex_ambiguity_rationale",
    "gold_monthly_frequency",
    "gold_yearly_bounds",
    "row_ok",
    "labels_match_all_categories",
    "quotes_ok_all_categories",
    "reference_found_in_note",
    "reference_context",
    "note_text_single_line",
)

NUMBER_WORDS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
)


def build_inventory_rows(
    *,
    split: str = "validation",
    data_path: Path = DEFAULT_DATA_PATH,
    manifest_path: Path = DEFAULT_SPLIT_MANIFEST_PATH,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records = load_records_for_split(split, data_path=data_path, manifest_path=manifest_path)
    rows = [_inventory_row(order, record, split=split) for order, record in enumerate(records, 1)]
    return rows, summarize_inventory(
        rows,
        split=split,
        data_path=data_path,
        manifest_path=manifest_path,
    )


def summarize_inventory(
    rows: Sequence[Mapping[str, Any]],
    *,
    split: str,
    data_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    ambiguity_counts = Counter(str(row["codex_initial_ambiguity_label"]) for row in rows)
    kind_counts = Counter(str(row["gold_label_kind"]) for row in rows)
    reasons = Counter(
        reason
        for row in rows
        for reason in str(row["codex_ambiguity_reasons"]).split(";")
        if reason
    )
    ambiguous_rows = [
        int(row["source_row_index"])
        for row in rows
        if row["codex_initial_ambiguity_label"] == "ambiguous"
    ]
    return {
        "artifact_kind": "gan2026_validation750_gold_reference_ambiguity_review",
        "date": "2026-06-04",
        "split_manifest": manifest_path.name,
        "split": split,
        "data_path": str(data_path),
        "row_count": len(rows),
        "claim_language": (
            "Reviewer worklist only. The initial clear/ambiguous labels are heuristic "
            "screening labels over validation gold/reference text and note context; they "
            "do not change gold labels, scorer policy, prompts, rules, or holdout claims."
        ),
        "ambiguity_counts": dict(sorted(ambiguity_counts.items())),
        "gold_label_kind_counts": dict(sorted(kind_counts.items())),
        "ambiguity_reason_counts": dict(
            sorted(reasons.items(), key=lambda item: (-item[1], item[0]))
        ),
        "ambiguous_source_row_indices": ambiguous_rows,
    }


def write_inventory_csv(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in FIELDNAMES})


def write_inventory_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _inventory_row(order: int, record: GanFrequencyRecord, *, split: str) -> dict[str, Any]:
    classification = _classify_gold_reference(record)
    reference_found, reference_context = _reference_context(record.note_text, record.gold_reference)
    return {
        "manual_ambiguity_label": "",
        "manual_notes": "",
        "manual_corrected_gold_label": "",
        "validation_order": order,
        "source_row_index": record.source_row_index,
        "split": split,
        "gold_label": record.gold_label,
        "gold_label_kind": str(record.gold_label_kind),
        "gold_reference": record.gold_reference,
        "codex_initial_ambiguity_label": classification["label"],
        "codex_ambiguity_reasons": ";".join(classification["reasons"]),
        "codex_ambiguity_rationale": classification["rationale"],
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "gold_yearly_bounds": _format_yearly_bounds(record.gold_yearly_bounds),
        "row_ok": record.row_ok,
        "labels_match_all_categories": record.labels_match_all_categories,
        "quotes_ok_all_categories": record.quotes_ok_all_categories,
        "reference_found_in_note": reference_found,
        "reference_context": reference_context,
        "note_text_single_line": _one_line(record.note_text),
    }


def _classify_gold_reference(record: GanFrequencyRecord) -> dict[str, Any]:
    reasons: list[str] = []
    label = record.gold_normalized_label.lower()
    reference = record.gold_reference.lower()
    kind = record.gold_label_kind

    if kind == FrequencyLabelKind.UNKNOWN:
        if _explicit_unknown_reference(reference):
            reasons.append("explicit_unknown_frequency")
        else:
            reasons.append("unknown_gold_boundary")
    if kind == FrequencyLabelKind.NO_REFERENCE and not _clear_no_reference(reference):
        reasons.append("no_reference_boundary")
    if kind == FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        reasons.append("unresolved_multiple_or_vague_count")
    if _has_vague_count_or_period(label, reference):
        reasons.append("vague_count_or_period")
    if _has_uncertainty_language(reference):
        reasons.append("uncertainty_language")
    if _has_conditional_or_trigger_language(reference):
        reasons.append("conditional_or_trigger_bound")
    if _has_last_event_boundary(reference, label=label, kind=kind):
        reasons.append("last_event_or_seizure_free_boundary")
    if _has_non_epileptic_boundary(reference, label=label, kind=kind):
        reasons.append("non_epileptic_or_seizure_like_boundary")
    if _has_relative_change_without_base_rate(reference):
        reasons.append("relative_change_without_base_rate")
    if _has_cluster_convention(label, reference):
        reasons.append("cluster_or_per_cluster_convention")
    if _has_upper_bound_or_range(reference):
        reasons.append("range_or_upper_bound")
    if _has_calendar_or_diary_arithmetic(reference):
        reasons.append("calendar_or_diary_arithmetic")
    if _gold_needs_frequency_but_reference_is_weak(record):
        reasons.append("reference_does_not_explicitly_support_frequency")
    if (
        not record.row_ok
        or not record.labels_match_all_categories
        or not record.quotes_ok_all_categories
    ):
        reasons.append("author_quality_flag_not_all_ok")

    reasons = list(dict.fromkeys(reasons))
    label_out = "ambiguous" if _is_ambiguous(reasons) else "clear"
    return {
        "label": label_out,
        "reasons": reasons if label_out == "ambiguous" else [],
        "rationale": _rationale(label_out, reasons),
    }


def _is_ambiguous(reasons: Sequence[str]) -> bool:
    strong_reasons = {
        "unknown_gold_boundary",
        "no_reference_boundary",
        "unresolved_multiple_or_vague_count",
        "uncertainty_language",
        "conditional_or_trigger_bound",
        "last_event_or_seizure_free_boundary",
        "non_epileptic_or_seizure_like_boundary",
        "relative_change_without_base_rate",
        "cluster_or_per_cluster_convention",
        "range_or_upper_bound",
        "calendar_or_diary_arithmetic",
        "reference_does_not_explicitly_support_frequency",
        "author_quality_flag_not_all_ok",
    }
    weak_only = set(reasons) <= {"explicit_unknown_frequency", "vague_count_or_period"}
    return bool(set(reasons) & strong_reasons) and not weak_only


def _rationale(label: str, reasons: Sequence[str]) -> str:
    if label == "clear":
        return (
            "Initial screen: gold label and reference look directly reviewable without an "
            "obvious ambiguity flag."
        )
    return "Initial screen: " + "; ".join(reason.replace("_", " ") for reason in reasons) + "."


def _explicit_unknown_reference(reference: str) -> bool:
    return _has_any(
        reference,
        "frequency unknown",
        "unknown frequency",
        "uncertain frequency",
        "unable to quantify",
        "cannot quantify",
        "not quantified",
        "unclear frequency",
    )


def _clear_no_reference(reference: str) -> bool:
    normalized = _one_line(reference).lower()
    return normalized in {
        "",
        "no seizure frequency reference",
        "no frequency reference",
        "no current seizure frequency reference",
    }


def _has_vague_count_or_period(label: str, reference: str) -> bool:
    text = " ".join([label, reference])
    return _has_any(
        text,
        "multiple",
        "several",
        "few",
        "many",
        "occasional",
        "sporadic",
        "rare",
        "frequent",
        "bimonthly",
        "biweekly",
        "every few",
        "from time to time",
        "most weekdays",
    )


def _has_uncertainty_language(reference: str) -> bool:
    return _has_any(
        reference,
        "uncertain",
        "unclear",
        "unsure",
        "possible",
        "suspected",
        "may represent",
        "may be",
        "could represent",
        "depending on",
        "ambiguous",
        "approx",
        "approximately",
        "about",
        "roughly",
    )


def _has_conditional_or_trigger_language(reference: str) -> bool:
    return _has_any(
        reference,
        "only with",
        "only after",
        "after alcohol",
        "sleep deprivation",
        "missed asm",
        "missed doses",
        "trigger",
        "triggers",
        "exposure",
        "luteal",
        "catamenial",
        "photosensitive",
        "with flicker",
        "skipping meals",
        "caffeine-associated",
        "stress-related",
    )


def _has_last_event_boundary(
    reference: str,
    *,
    label: str,
    kind: FrequencyLabelKind,
) -> bool:
    if not _has_any(reference, "last seizure", "latest one", "last reported event"):
        return False
    return kind != FrequencyLabelKind.SEIZURE_FREE or "seizure free" not in label


def _has_non_epileptic_boundary(
    reference: str,
    *,
    label: str,
    kind: FrequencyLabelKind,
) -> bool:
    if not _has_any(reference, "non-epileptic", "seizure-like", "not epileptic"):
        return False
    return kind in {FrequencyLabelKind.SEIZURE_FREE, FrequencyLabelKind.NO_REFERENCE} or (
        "seizure free" in label
    )


def _has_relative_change_without_base_rate(reference: str) -> bool:
    if not _has_any(reference, "increased", "reduced", "worsening", "improved", "%"):
        return False
    return not _has_frequency_signal(reference)


def _has_cluster_convention(label: str, reference: str) -> bool:
    text = " ".join([label, reference])
    return "cluster" in text or "per cluster" in text


def _has_upper_bound_or_range(reference: str) -> bool:
    if _has_any(reference, "up to", "at most", "less than", "no more than", "<=", "≤"):
        return True
    return bool(re.search(r"\b\d+\s*(?:-|–|—|to)\s*\d+\b", reference))


def _has_calendar_or_diary_arithmetic(reference: str) -> bool:
    if _has_any(reference, "diary", "calendar"):
        return True
    return bool(
        re.search(
            r"\b(?:jan|january|feb|february|mar|march|apr|april|jun|june|jul|july|"
            r"aug|august|sep|sept|september|oct|october|nov|november|dec|december)\b",
            reference,
        )
    )


def _gold_needs_frequency_but_reference_is_weak(record: GanFrequencyRecord) -> bool:
    if record.gold_label_kind not in {
        FrequencyLabelKind.FREQUENCY,
        FrequencyLabelKind.SEIZURE_FREE,
    }:
        return False
    reference = record.gold_reference.lower()
    if "seizure free" in record.gold_normalized_label and _has_any(
        reference,
        "no seizures",
        "no events",
        "seizure free",
        "seizure-free",
        "since",
    ):
        return False
    return not _has_frequency_signal(reference)


def _has_frequency_signal(text: str) -> bool:
    if re.search(r"\d", text):
        return True
    if re.search(r"\b(" + "|".join(NUMBER_WORDS) + r")\b", text):
        return True
    return _has_any(
        text,
        "daily",
        "nightly",
        "weekly",
        "monthly",
        "yearly",
        "per day",
        "per week",
        "per month",
        "per year",
        "once",
        "twice",
        "multiple",
        "several",
        "few",
        "many",
        "seizure free",
        "seizure-free",
        "no seizures",
        "no events",
    )


def _reference_context(note_text: str, reference: str, *, window: int = 180) -> tuple[bool, str]:
    note_single = _one_line(note_text)
    reference_single = _one_line(reference)
    if not reference_single:
        return False, ""
    match = re.search(re.escape(reference_single), note_single, re.IGNORECASE)
    if not match:
        return False, ""
    start = max(match.start() - window, 0)
    end = min(match.end() + window, len(note_single))
    prefix = "..." if start else ""
    suffix = "..." if end < len(note_single) else ""
    return True, f"{prefix}{note_single[start:end]}{suffix}"


def _format_yearly_bounds(bounds: tuple[float, float] | None) -> str:
    if bounds is None:
        return ""
    return f"{bounds[0]} to {bounds[1]}"


def _one_line(text: str) -> str:
    return " ".join(str(text).split())


def _has_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_SPLIT_MANIFEST_PATH)
    parser.add_argument("--csv-path", type=Path, default=DEFAULT_CSV_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    args = parser.parse_args()

    rows, metadata = build_inventory_rows(
        split=args.split,
        data_path=args.data_path,
        manifest_path=args.manifest_path,
    )
    write_inventory_csv(rows, args.csv_path)
    write_inventory_json(metadata, args.json_path)
    print(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
