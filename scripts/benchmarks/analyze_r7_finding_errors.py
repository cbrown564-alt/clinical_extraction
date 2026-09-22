"""Decompose the saved R7 finding-score misses. Development only; no model calls.

The primary score stays finding_matching_v07. The classes here explain that score.
They are not a replacement matcher and not a corrected result.

    .venv/bin/python scripts/benchmarks/analyze_r7_finding_errors.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as fm,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from scripts.benchmarks.run_r8 import load_reference
from scripts.benchmarks.score_r7_findings import REFERENCE, predictions_for, representation_gap

OUT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7/"
    "dev750_timeout600/finding_error_classes.json"
)
CLOSED = {
    "rare",
    "occasional",
    "frequent",
    "increased",
    "decreased",
    "unchanged",
    "variable",
    "unknown",
}
GUIDE_MAP = {
    "infrequent": "occasional",
    "intermittent": "occasional",
    "sporadic": "occasional",
    "most days": "frequent",
    "near-daily": "frequent",
    "near daily": "frequent",
    "more frequent": "increased",
    "worsening frequency": "increased",
    "less frequent": "decreased",
    "reduced": "decreased",
    "not documented": "unknown",
    "unable to quantify": "unknown",
}


def clip(text: str | None, n: int = 140) -> str:
    return " ".join((text or "").split())[:n]


def measurement_brief(measurement: dict[str, Any]) -> str:
    kind = measurement.get("type")
    if kind == "qualitative":
        return f"qualitative:{measurement.get('frequency')}"
    if kind == "rate":
        count = json.dumps(measurement.get("count"), default=str)
        per = json.dumps(measurement.get("per"), default=str)
        return f"rate {count} per {per}"
    if kind == "count":
        return f"count {json.dumps(measurement.get('count'), default=str)}"
    if kind == "cluster":
        return (
            "cluster "
            f"rate={json.dumps(measurement.get('rate'), default=str)} "
            f"count={json.dumps(measurement.get('count'), default=str)} "
            f"size={json.dumps(measurement.get('seizures_per_cluster'), default=str)}"
        )
    if kind == "seizure_free":
        duration = json.dumps(measurement.get("duration"), default=str)
        since = json.dumps(measurement.get("since"), default=str)
        return f"seizure_free {duration} since {since}"
    if kind == "last_seizure":
        return f"last_seizure {json.dumps(measurement.get('occurred_at'), default=str)}"
    return kind or "?"


def brief(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": finding.get("id"),
        "event": clip(finding.get("event", {}).get("type"), 80),
        "status": finding.get("event", {}).get("seizure_status"),
        "timing": finding.get("timing"),
        "measurement": clip(measurement_brief(finding.get("measurement") or {}), 180),
        "period": clip((finding.get("period") or {}).get("time"), 80),
        "evidence": clip(finding.get("evidence")),
    }


def period_kind(pred: dict[str, Any], ref: dict[str, Any]) -> str:
    left, right = pred.get("period"), ref.get("period")
    if left is None and right is None:
        return "both_absent"
    if left is None:
        return "prediction_omitted"
    if right is None:
        return "reference_omitted"
    return "both_present_disagree" if not fm.period_equivalent(left, right) else "equivalent"


def guide_frequency(value: str | None) -> str | None:
    text = fm.norm_text(value)
    if text in CLOSED:
        return text
    return GUIDE_MAP.get(text)


def example(bucket: list[dict[str, Any]], item: dict[str, Any], limit: int = 3) -> None:
    if len(bucket) < limit:
        bucket.append(item)


def main() -> None:
    selected = study.records()
    refs = load_reference(REFERENCE, selected)
    diagnostics = {
        row["source_row_index"]: row
        for row in json.loads(
            Path(
                "runs/one_shot_frequency_v2_measurements_r7/dev750/timeout600/"
                "timeout_completed/diagnostics.json"
            ).read_text()
        )
    }
    fn_class: Counter[str] = Counter()
    fp_class: Counter[str] = Counter()
    type_pairs: Counter[str] = Counter()
    status_pairs: Counter[str] = Counter()
    timing_pairs: Counter[str] = Counter()
    period_pairs: Counter[str] = Counter()
    qual_pairs: Counter[str] = Counter()
    pred_status: Counter[str] = Counter()
    ref_status: Counter[str] = Counter()
    pred_timing: Counter[str] = Counter()
    ref_timing: Counter[str] = Counter()
    pred_freq: Counter[str] = Counter()
    ref_freq: Counter[str] = Counter()
    examples: dict[str, list[dict[str, Any]]] = {}
    normalized_quote_only = 0
    same_evidence_pairs = 0
    status_only_would_match = 0

    for record in selected:
        ref_findings = refs[record.source_row_index]["findings"]
        predicted = predictions_for(diagnostics[record.source_row_index])
        for finding in ref_findings:
            ref_status[finding.get("event", {}).get("seizure_status") or "missing"] += 1
            ref_timing[finding.get("timing") or "missing"] += 1
            if finding["measurement"]["type"] == "qualitative":
                ref_freq[str(finding["measurement"].get("frequency"))] += 1
        if predicted is None:
            fn_class["unusable_inventory"] += len(ref_findings)
            continue
        for finding in predicted:
            pred_status[finding.get("event", {}).get("seizure_status") or "missing"] += 1
            pred_timing[finding.get("timing") or "missing"] += 1
            if finding["measurement"]["type"] == "qualitative":
                pred_freq[str(finding["measurement"].get("frequency"))] += 1
        scored = fm.score_letter(record.note_text, ref_findings, predicted)
        matched_ref = {pair[1] for pair in scored["pairs"]}
        matched_pred = {pair[0] for pair in scored["pairs"]}
        for finding in ref_findings:
            if finding["id"] in matched_ref:
                fn_class["matched"] += 1
                continue
            if representation_gap(finding):
                fn_class["outside_r7_schema"] += 1
                continue
            overlaps = [
                item
                for item in predicted
                if fm.evidence_overlap(
                    record.note_text, item.get("evidence", ""), finding.get("evidence", "")
                )
            ]
            if not overlaps:
                fn_class["no_shared_evidence"] += 1
                norm_hit = any(
                    fm.norm_text(item.get("evidence"))
                    and (
                        fm.norm_text(item.get("evidence")) in fm.norm_text(finding.get("evidence"))
                        or fm.norm_text(finding.get("evidence"))
                        in fm.norm_text(item.get("evidence"))
                    )
                    for item in predicted
                )
                if norm_hit:
                    normalized_quote_only += 1
                example(
                    examples.setdefault("omission", []),
                    {"row": record.source_row_index, "reference": brief(finding)},
                )
                continue
            same_evidence_pairs += 1
            partner = min(
                overlaps,
                key=lambda item: len(fm.attribute_diffs(item, finding, record.note_text)),
            )
            diffs = fm.attribute_diffs(partner, finding, record.note_text)
            # Evidence overlapped, so drop a stale evidence flag if the spans still differ
            # under the matcher's exact-find rule. attribute_diffs uses the same test.
            key = "+".join(sorted(diffs)) or "overlap_but_unmatched_other_assignment"
            fn_class[f"same_evidence:{key}"] += 1
            type_pairs[
                f"{partner['measurement']['type']} vs {finding['measurement']['type']}"
            ] += 1
            status_pairs[
                f"{partner.get('event', {}).get('seizure_status')} vs "
                f"{finding.get('event', {}).get('seizure_status')}"
            ] += 1
            timing_pairs[f"{partner.get('timing')} vs {finding.get('timing')}"] += 1
            if "period" in diffs:
                period_pairs[period_kind(partner, finding)] += 1
            if (
                partner["measurement"]["type"] == "qualitative"
                and finding["measurement"]["type"] == "qualitative"
            ):
                qual_pairs[
                    f"{partner['measurement'].get('frequency')} -> "
                    f"{finding['measurement'].get('frequency')}"
                ] += 1
            if diffs == ["seizure_status"]:
                status_only_would_match += 1
            label = "same_evidence:" + key
            example(
                examples.setdefault(label, []),
                {
                    "row": record.source_row_index,
                    "diffs": diffs,
                    "prediction": brief(partner),
                    "reference": brief(finding),
                },
            )
        for finding in predicted:
            if finding["id"] in matched_pred:
                fp_class["matched"] += 1
                continue
            overlaps_any = any(
                fm.evidence_overlap(
                    record.note_text, finding.get("evidence", ""), ref.get("evidence", "")
                )
                for ref in ref_findings
            )
            fp_class["same_evidence_extra" if overlaps_any else "no_shared_evidence"] += 1

    report = {
        "scope": "Synthetic dev750 explanation of the frozen R7 finding score. Not a new score.",
        "reference_status": dict(ref_status),
        "prediction_status": dict(pred_status),
        "reference_timing": dict(ref_timing),
        "prediction_timing": dict(pred_timing),
        "reference_qualitative_frequency": dict(ref_freq.most_common()),
        "prediction_qualitative_frequency_top": pred_freq.most_common(30),
        "prediction_qualitative_outside_closed_list": sum(
            n for value, n in pred_freq.items() if fm.norm_text(value) not in CLOSED
        ),
        "prediction_qualitative_total": sum(pred_freq.values()),
        "false_negative_classes": dict(fn_class.most_common()),
        "false_positive_classes": dict(fp_class),
        "same_evidence_type_pairs": dict(type_pairs.most_common(20)),
        "same_evidence_status_pairs": dict(status_pairs.most_common(12)),
        "same_evidence_timing_pairs": dict(timing_pairs.most_common(12)),
        "same_evidence_period_when_period_differs": dict(period_pairs),
        "same_evidence_qualitative_pairs": dict(qual_pairs.most_common(20)),
        "same_evidence_disagreement_findings": same_evidence_pairs,
        "status_only_disagreements": status_only_would_match,
        "omission_whose_quote_matches_after_normalisation": normalized_quote_only,
        "guide_frequency_mapped_prediction_count": sum(
            n for value, n in pred_freq.items() if guide_frequency(value) in CLOSED
        ),
        "examples": examples,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    printable = {k: v for k, v in report.items() if k != "examples"}
    print(json.dumps(printable, indent=2)[:20000])
    print("example classes", {k: len(v) for k, v in examples.items()})


if __name__ == "__main__":
    main()
