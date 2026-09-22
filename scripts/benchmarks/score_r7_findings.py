"""Score saved R7 rich inventories against the reviewed v0.7 dev750 reference.

No model call, repair, or test450 access. A schema-invalid or absent inventory is
unusable: no true positives, every reference finding is a false negative, and the
predicted count is unknown. Findings are not salvaged from an invalid record.
The frozen matcher is not modified. Reference findings that R7 cannot represent
stay in the primary score and are counted as a separate stratum.

    .venv/bin/python scripts/benchmarks/score_r7_findings.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as fm,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r7 as r7
from scripts.benchmarks.run_r8 import load_reference

VIEW = Path("runs/one_shot_frequency_v2_measurements_r7/dev750/timeout600/timeout_completed")
REFERENCE = Path(
    "runs/seizure_finding_annotation_v0_2/agy_gemini38_high/reviews/claude_v07/"
    "continuation_2026-09-21/source_15672_2026-09-22/reviewed_750.jsonl"
)
OUT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7/"
    "dev750_timeout600/finding_score.json"
)


def ratio(num: int, den: int) -> float | str:
    return num / den if den else "not estimable"


def representation_gap(finding: dict[str, Any]) -> str | None:
    """Why this reviewed finding cannot be a valid R7 finding, if it cannot."""
    try:
        r7.Finding.model_validate(finding)
    except ValidationError as exc:
        error = exc.errors()[0]
        loc = ".".join(str(part) for part in error["loc"] if not isinstance(part, int))
        return f"{loc}: {error['type']}"
    return None


def predictions_for(row: dict[str, Any]) -> list[dict[str, Any]] | None:
    raw = row.get("structured_json")
    if not raw:
        return None
    try:
        payload = json.loads(raw, object_pairs_hook=study.r4.v1._unique_object)
        rich = r7.Rich.model_validate(payload)
    except (ValueError, TypeError, ValidationError):
        return None
    return [finding.model_dump(exclude_none=True) for finding in rich.findings]


def main() -> None:
    if not REFERENCE.is_file():
        raise ValueError("Reviewed dev750 reference is not available")
    selected = study.records()
    if len(selected) != 750:
        raise ValueError("This measurement is dev750 only")
    refs = load_reference(REFERENCE, selected)
    diagnostics = json.loads((VIEW / "diagnostics.json").read_text())
    by_index = {row["source_row_index"]: row for row in diagnostics}
    if set(by_index) != {record.source_row_index for record in selected}:
        raise ValueError("R7 mixed-view coverage is not the dev750 manifest")

    letters = []
    compact = []
    gap_kinds: Counter[str] = Counter()
    ref_type: dict[str, Counter[str]] = {}
    ref_timing: dict[str, Counter[str]] = {}
    pred_type: dict[str, Counter[str]] = {}
    fn_partition: Counter[str] = Counter()
    usable_fn_gap = 0
    ref_diag: Counter[str] = Counter()
    ref_diag_single: Counter[str] = Counter()
    ref_diag_multi = 0
    states: Counter[str] = Counter()

    for record in selected:
        ref = refs[record.source_row_index]
        states[ref["annotation_state"]] += 1
        if ref["annotation_state"] != "complete":
            raise ValueError(f"Row {record.source_row_index} is not a complete reference")
        saved = by_index[record.source_row_index]
        predicted = predictions_for(saved)
        schema_ok = predicted is not None
        failure = saved.get("failure")
        if failure in {"invalid_schema", "no_response"}:
            if schema_ok:
                raise ValueError(f"Invalid row {record.source_row_index} validated")
        elif failure in {None, "invalid_target_label"}:
            if not schema_ok:
                raise ValueError(f"Usable row {record.source_row_index} failed revalidation")
        else:
            raise ValueError(f"Unexpected failure {failure} on {record.source_row_index}")
        scored = fm.score_letter(record.note_text, ref["findings"], predicted)
        letters.append(scored)
        gaps = []
        matched_ref = {pair[1] for pair in scored["pairs"]}
        for finding in ref["findings"]:
            kind = representation_gap(finding)
            timing = finding.get("timing", "current")
            measurement = finding["measurement"]["type"]
            matched = finding["id"] in matched_ref
            ref_type.setdefault(measurement, Counter())[
                "matched" if matched else "missed"
            ] += 1
            ref_timing.setdefault(timing, Counter())["matched" if matched else "missed"] += 1
            if kind:
                gap_kinds[kind] += 1
                gaps.append(finding["id"])
            if not matched:
                if predicted is None:
                    fn_partition["unusable_inventory"] += 1
                elif kind:
                    fn_partition["outside_r7_schema"] += 1
                    usable_fn_gap += 1
                else:
                    fn_partition["representable_unmatched"] += 1
                    best = min(
                        (
                            fm.attribute_diffs(item, finding, record.note_text)
                            for item in predicted or []
                        ),
                        key=len,
                        default=["no_prediction"],
                    )
                    for name in best:
                        ref_diag[name] += 1
                    if len(best) == 1:
                        ref_diag_single[best[0]] += 1
                    else:
                        ref_diag_multi += 1
        if predicted is not None:
            matched_pred = {pair[0] for pair in scored["pairs"]}
            for finding in predicted:
                measurement = finding["measurement"]["type"]
                pred_type.setdefault(measurement, Counter())[
                    "matched" if finding["id"] in matched_pred else "unmatched"
                ] += 1
        compact.append(
            {
                "source_row_index": record.source_row_index,
                "usable": scored["usable"],
                "failure": saved.get("failure"),
                "reference": scored["reference"],
                "predicted": scored["predicted"],
                "tp": scored["tp"],
                "fp": scored["fp"],
                "fn": scored["fn"],
                "outside_r7_schema": gaps,
                "pairs": scored["pairs"],
                "unmatched_diagnostics": scored["unmatched_diagnostics"],
            }
        )

    summary = fm.aggregate(letters)
    usable = [row for row in letters if row["usable"]]
    usable_fn = sum(row["fn"] for row in usable)
    summary.update(
        {
            "precision_scope": (
                "Conditional on usable inventories. Unusable inventories contribute "
                "false negatives to recall and exact-inventory failure, not false positives."
            ),
            "recall_on_usable_inventories": ratio(
                sum(row["tp"] for row in usable),
                sum(row["tp"] for row in usable) + usable_fn,
            ),
            "false_negative_partition": dict(fn_partition),
            "representable_miss_diagnostics": {
                "note": (
                    "Closest unused prediction for each representable unmatched "
                    "reference finding on a usable inventory. A finding may differ "
                    "in several attributes; those totals are not false-negative totals."
                ),
                "findings": fn_partition["representable_unmatched"],
                "single_attribute": dict(ref_diag_single),
                "multiple_attributes": ref_diag_multi,
                "attribute_mentions": dict(ref_diag),
            },
            "reference_findings_by_measurement": {k: dict(v) for k, v in sorted(ref_type.items())},
            "reference_findings_by_timing": {k: dict(v) for k, v in sorted(ref_timing.items())},
            "usable_predictions_by_measurement": {
                k: dict(v) for k, v in sorted(pred_type.items())
            },
            "reference_outside_r7_schema": {
                "findings": sum(gap_kinds.values()),
                "kinds": dict(gap_kinds),
                "unmatched_on_usable_inventories": usable_fn_gap,
                "note": (
                    "Qualitative durations and quarter units are legal in the v0.7 "
                    "reference and illegal in the frozen R7 schema. They are not removed "
                    "from the primary score and are not converted."
                ),
            },
        }
    )
    if sum(fn_partition.values()) != summary["fn"]:
        raise ValueError("False-negative partition does not cover the primary score")
    if sum(ref_diag_single.values()) + ref_diag_multi != fn_partition["representable_unmatched"]:
        raise ValueError("Representable-miss diagnostics do not cover those findings")
    if states != Counter({"complete": 750}):
        raise ValueError(f"Unexpected reference states: {states}")

    plan = json.loads((VIEW / "plan.json").read_text())
    report = {
        "version": "r7_dev750_finding_score_v1",
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": "all 750 development rows; complete v0.7 references; failures retained",
        "n_letters": 750,
        "n_reference_findings": sum(row["reference"] for row in letters),
        "prompt_version": r7.VERSION,
        "revision": r7.REVISION,
        "model": plan["model"],
        "provider_documented_version": plan["provider_documented_version"],
        "view": plan["view"],
        "repair_policy": "none",
        "replay_mode": "saved mixed-attempt responses; revalidated with frozen R7 schema",
        "matching_version": fm.MATCHING_VERSION,
        "reference_path": str(REFERENCE),
        "reference_sha256": study.old.digest(REFERENCE.read_bytes()),
        "matcher_sha256": study.old.digest(Path(fm.__file__).read_bytes()),
        "schema_sha256": study.old.digest(Path(r7.__file__).read_bytes()),
        "scope": (
            "Synthetic development finding score. Not clinical validation, not a "
            "holdout result, and not an R8 evaluation."
        ),
        "matcher_limits": (
            "finding_matching_v07 compares event label, seizure status, timing, "
            "measurement components, period or date, and exact evidence overlap. "
            "It does not compare condition, approximation, or inclusivity. "
            "Document dates are not findings."
        ),
        "summary": summary,
        "letters": compact,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "letters": summary["letters"],
                "usable": summary["usable_letters"],
                "unusable": summary["unusable_letters"],
                "tp": summary["tp"],
                "fp": summary["fp"],
                "fn": summary["fn"],
                "precision": summary["precision"],
                "recall": summary["recall"],
                "f1": summary["f1"],
                "exact_inventory": summary["exact_inventory"],
                "empty_reference_letters": summary["empty_reference_letters"],
                "empty_state_correct": summary["empty_state_correct"],
                "fn_partition": summary["false_negative_partition"],
                "representable_miss": summary["representable_miss_diagnostics"],
                "outside_r7": summary["reference_outside_r7_schema"],
                "recall_on_usable": summary["recall_on_usable_inventories"],
                "reference_by_measurement": summary["reference_findings_by_measurement"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
