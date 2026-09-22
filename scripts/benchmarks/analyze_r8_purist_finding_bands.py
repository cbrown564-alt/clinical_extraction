"""Project saved R8 findings onto Purist bands. Diagnostic only; not a new score.

    .venv/bin/python scripts/benchmarks/analyze_r8_purist_finding_bands.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as fm,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
from clinical_extraction.tasks.shared.epilepsy.normalization import label_to_frequency_record
from scripts.benchmarks.run_r8 import inspect, load_reference, records

RESPONSES = Path(
    "runs/one_shot_frequency_v2_measurements_r8/dev750_rich_only/responses.jsonl"
)
REQUESTS = Path(
    "runs/one_shot_frequency_v2_measurements_r8/dev750_rich_only/requests.jsonl"
)
REFERENCE = Path(
    "runs/seizure_finding_annotation_v0_2/agy_gemini38_high/reviews/claude_v07/"
    "continuation_2026-09-21/source_15672_2026-09-22/reviewed_750.jsonl"
)
OUT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r8/"
    "dev750_rich_only/purist_band_diagnostic.json"
)


def fmt(value: float) -> str:
    return str(int(value)) if float(value) == int(value) else str(value)


def quantity_text(quantity: dict[str, Any] | None) -> str | None:
    if not quantity:
        return None
    kind = quantity.get("type")
    if kind == "number":
        return fmt(float(quantity["value"]))
    if kind == "range":
        return f"{fmt(float(quantity['lower']))} to {fmt(float(quantity['upper']))}"
    if kind == "qualitative":
        text = str(quantity.get("quantity") or "").strip().lower()
        return "multiple" if text == "multiple" else None
    if kind == "bound":
        inner = quantity.get("value")
        relation = quantity.get("relation")
        number = quantity_text(inner) if isinstance(inner, dict) else fmt(float(inner))
        if number is None:
            return None
        if relation in {"at_least", "more_than"}:
            return f"{number} or more"
        return number
    return None


def duration_text(duration: dict[str, Any] | None) -> str | None:
    if not duration or duration.get("type") == "qualitative" or duration.get("unit") == "quarter":
        return None
    unit = duration.get("unit")
    kind = duration.get("type")
    if kind == "number":
        value = float(duration["value"])
        return unit if value == 1 else f"{fmt(value)} {unit}"
    if kind == "range":
        return f"{fmt(float(duration['lower']))} to {fmt(float(duration['upper']))} {unit}"
    if kind == "bound":
        inner = duration_text({**duration, "type": "number", "value": _bound_number(duration)})
        return inner
    return None


def _bound_number(duration: dict[str, Any]) -> float:
    value = duration.get("value")
    if isinstance(value, dict):
        return float(value.get("lower") or value.get("value"))
    return float(value)


def finding_label(finding: dict[str, Any]) -> tuple[str | None, str]:
    """Return a Gan label and why, or (None, reason). Seizure-free ignores duration."""
    measurement = finding.get("measurement") or {}
    kind = measurement.get("type")
    if kind == "rate":
        count = quantity_text(measurement.get("count"))
        per = duration_text(measurement.get("per"))
        if count and per:
            return f"{count} per {per}", "rate"
        return None, "rate_unprojectable"
    if kind == "count":
        count = quantity_text(measurement.get("count"))
        per = duration_text((finding.get("period") or {}).get("duration"))
        if count and per:
            return f"{count} per {per}", "count_as_rate"
        return None, "count_without_numeric_window"
    if kind == "cluster":
        rate = measurement.get("rate") or {}
        count = quantity_text(rate.get("count")) if rate else None
        per = duration_text(rate.get("per")) if rate else None
        size = quantity_text(measurement.get("seizures_per_cluster"))
        if count and per and size:
            return f"{count} cluster per {per}, {size} per cluster", "cluster"
        if count and per:
            return f"{count} per {per}", "cluster_rate_without_size"
        return None, "cluster_unprojectable"
    if kind == "seizure_free":
        return "seizure free", "seizure_free_collapsed"
    if kind == "qualitative":
        return None, "qualitative"
    if kind == "last_seizure":
        return None, "last_seizure"
    return None, "other"


def band(label: str | None) -> str | None:
    if not label:
        return None
    try:
        monthly = label_to_frequency_record(label).monthly_frequency
    except (ValueError, ZeroDivisionError, OverflowError):
        return None
    return str(map_purist(monthly))


def project(finding: dict[str, Any]) -> dict[str, Any]:
    label, reason = finding_label(finding)
    purist = band(label)
    return {"label": label, "reason": reason if purist else f"unparsed:{reason}", "purist": purist}


def subclass_exact_misses(selected, refs, responses, jobs) -> dict[str, Any]:
    """Closest same-evidence partner for each exact-unmatched reference finding."""
    from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
        one_shot_thinking as study,
    )

    counts: Counter[str] = Counter()
    for record in selected:
        saved = responses[jobs[record.source_row_index]["request_id"]]
        content, finish = study.old.response_content(saved.get("response"))
        checked = inspect(content, finish, record, "r8_rich")
        reference = refs[record.source_row_index]["findings"]
        predicted = checked["findings"] if checked["record_valid"] else None
        exact = fm.score_letter(record.note_text, reference, predicted)
        if predicted is None:
            counts["unusable_inventory"] += len(reference)
            continue
        matched = {pair[1] for pair in exact["pairs"]}
        for ref in reference:
            if ref["id"] in matched:
                counts["exact_match"] += 1
                continue
            overlaps = [
                pred
                for pred in predicted
                if fm.evidence_overlap(
                    record.note_text, pred.get("evidence", ""), ref.get("evidence", "")
                )
            ]
            if not overlaps:
                counts["no_shared_evidence"] += 1
                continue
            pred = min(
                overlaps,
                key=lambda item: len(fm.attribute_diffs(item, ref, record.note_text)),
            )
            diffs = tuple(sorted(fm.attribute_diffs(pred, ref, record.note_text)))
            event_ok = fm.label_key(pred["event"]["type"]) == fm.label_key(ref["event"]["type"])
            timing_ok = pred.get("timing") == ref.get("timing")
            measure_ok = fm.measurement_equal(pred["measurement"], ref["measurement"])
            if event_ok and timing_ok and measure_ok:
                counts["same_measurement_event_timing"] += 1
                if diffs == ("period",):
                    counts["period_only"] += 1
                elif diffs == ("seizure_status",):
                    counts["status_only"] += 1
                continue
            left, right = project(pred), project(ref)
            if event_ok and timing_ok and left["purist"] and right["purist"]:
                key = "same_band" if left["purist"] == right["purist"] else "different_band"
                counts[key] += 1
                if left["reason"] == "seizure_free_collapsed":
                    counts[key + "_seizure_free_collapsed"] += 1
            elif not event_ok:
                counts["event_label"] += 1
            elif not timing_ok:
                counts["timing"] += 1
            else:
                counts["not_a_purist_rate"] += 1
            if len(diffs) == 1:
                counts[f"single_{diffs[0]}"] += 1
    return dict(counts)


def main() -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
        one_shot_thinking as study,
    )

    selected = records("dev750")
    refs = load_reference(REFERENCE, selected)
    responses = {row["request_id"]: row for row in study.old.read_lines(RESPONSES)}
    jobs = {row["source_row_index"]: row for row in study.old.read_lines(REQUESTS)}
    same_band = Counter()
    different_band = Counter()
    unprojectable = Counter()
    reasons = Counter()
    examples: dict[str, list[dict[str, Any]]] = {}
    # Sensitivity: evidence overlap, equivalent event, same timing, same Purist band.
    # Exact measurement matches still count. Unprojectable non-exact pairs do not.
    tp = fp = fn = 0
    exact_tp = 0
    band_only_tp = 0
    seizure_free_collapse_tp = 0

    for record in selected:
        saved = responses[jobs[record.source_row_index]["request_id"]]
        content, finish = study.old.response_content(saved.get("response"))
        checked = inspect(content, finish, record, "r8_rich")
        reference = refs[record.source_row_index]["findings"]
        predicted = checked["findings"] if checked["record_valid"] else None
        exact = fm.score_letter(record.note_text, reference, predicted)
        exact_tp += exact["tp"]
        if predicted is None:
            fn += len(reference)
            continue
        matched_ref = {pair[1] for pair in exact["pairs"]}
        matched_pred = {pair[0] for pair in exact["pairs"]}
        used_ref: set[str] = set(matched_ref)
        used_pred: set[str] = set(matched_pred)
        tp += len(matched_ref)
        candidates = []
        for pred in predicted:
            if pred["id"] in used_pred:
                continue
            for ref in reference:
                if ref["id"] in used_ref:
                    continue
                if not fm.evidence_overlap(
                    record.note_text, pred.get("evidence", ""), ref.get("evidence", "")
                ):
                    continue
                if fm.label_key(pred["event"]["type"]) != fm.label_key(ref["event"]["type"]):
                    continue
                if pred.get("timing") != ref.get("timing"):
                    continue
                left, right = project(pred), project(ref)
                if left["purist"] and left["purist"] == right["purist"]:
                    candidates.append((pred, ref, left, right))
        # Greedy by source order. This is a ceiling sketch, not the frozen one-to-one matcher.
        for pred, ref, left, right in candidates:
            if pred["id"] in used_pred or ref["id"] in used_ref:
                continue
            used_pred.add(pred["id"])
            used_ref.add(ref["id"])
            tp += 1
            band_only_tp += 1
            collapsed = left["reason"] == "seizure_free_collapsed"
            kind = "seizure_free_collapsed" if collapsed else "same_band"
            if kind == "seizure_free_collapsed":
                seizure_free_collapse_tp += 1
            same_band[f"{left['reason']} {left['purist']}"] += 1
            bucket = examples.setdefault(kind, [])
            if len(bucket) < 4:
                bucket.append(
                    {
                        "row": record.source_row_index,
                        "prediction": left["label"],
                        "reference": right["label"],
                        "band": left["purist"],
                        "pred_evidence": " ".join((pred.get("evidence") or "").split())[:140],
                        "ref_evidence": " ".join((ref.get("evidence") or "").split())[:140],
                    }
                )
        for ref in reference:
            if ref["id"] in used_ref:
                continue
            fn += 1
            overlaps = [
                pred
                for pred in predicted
                if fm.evidence_overlap(
                    record.note_text, pred.get("evidence", ""), ref.get("evidence", "")
                )
            ]
            if not overlaps:
                unprojectable["no_shared_evidence"] += 1
                continue
            pred = overlaps[0]
            left, right = project(pred), project(ref)
            if left["purist"] and right["purist"]:
                if left["purist"] == right["purist"]:
                    reasons["same_band_blocked_by_event_or_timing"] += 1
                else:
                    different_band[f"{right['purist']} vs {left['purist']}"] += 1
            else:
                unprojectable[left["reason"] if not left["purist"] else right["reason"]] += 1
        fp += len(predicted) - len(used_pred)

    report = {
        "scope": (
            "Saved R8 rich dev750. Exact score remains finding_matching_v07. "
            "The band sketch is not an adopted scorer."
        ),
        "exact_tp": exact_tp,
        "band_sketch": {
            "rule": (
                "Keep an exact match. Also match an unused pair when evidence overlaps, "
                "event labels are equivalent, timing agrees, and the projected Purist "
                "band agrees. Period text, seizure status, and exact quantity spelling "
                "are not required. Every seizure-free finding projects to currently_no_seizure."
            ),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "added_by_band": band_only_tp,
            "added_only_because_seizure_free_collapses": seizure_free_collapse_tp,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
        },
        "added_pair_kinds": dict(same_band),
        "same_evidence_different_band": dict(different_band.most_common(15)),
        "unmatched_reference_with_overlap_unprojectable_or_blocked": dict(unprojectable),
        "same_band_blocked_by_event_or_timing": reasons["same_band_blocked_by_event_or_timing"],
        "exact_miss_subclasses": subclass_exact_misses(selected, refs, responses, jobs),
        "examples": examples,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    printable = {k: v for k, v in report.items() if k != "examples"}
    print(json.dumps(printable, indent=2))


if __name__ == "__main__":
    main()
