"""Build scorer-independent Diagnosis sensitivity views from reviewed disagreements."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    sha256_file,
)

SENSITIVITY_SCHEMA = "exectv2_diagnosis_sensitivity_v1"

_CONSERVATIVE_MECHANISMS = frozenset(
    {
        "same_cui_representation",
        "reviewed_equivalence",
        "clinical_granularity",
    }
)


def build_sensitivity_report(
    *,
    ledger_jsonl: Path,
    audit_summary_json: Path,
    out_json: Path | None = None,
) -> dict[str, Any]:
    """Apply reviewed representation decisions as explicit diagnostic adjustments.

    The fixed primary scorer and gold labels remain unchanged. A forgiven missed row
    increments recall credit; a forgiven spurious row increments precision credit.
    """

    ledger = [
        json.loads(line)
        for line in ledger_jsonl.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    audit = json.loads(audit_summary_json.read_text(encoding="utf-8"))
    methods: Mapping[str, Any] = audit.get("methods", {})
    _validate_fixed_reproduction(ledger, methods)

    definitions: tuple[tuple[str, str, Callable[[Mapping[str, Any]], bool]], ...] = (
        (
            "multiplicity_and_clinical_granularity",
            "Forgives reviewed same-CUI, accepted-equivalence, and clinical-granularity "
            "differences; excludes likely gold omissions and manually classified rows.",
            lambda decision: decision.get("mechanism") in _CONSERVATIVE_MECHANISMS,
        ),
        (
            "reviewed_interpretation",
            "Forgives every disagreement classified as a representation issue in the "
            "completed review, including likely gold omissions and manual decisions.",
            lambda decision: decision.get("triage") == "representation",
        ),
    )
    views: dict[str, Any] = {}
    for name, description, include in definitions:
        selected = [row for row in ledger if include(row.get("review_decision", {}))]
        mechanism_counts = Counter(
            str(row.get("review_decision", {}).get("mechanism")) for row in selected
        )
        method_results: dict[str, Any] = {}
        for method, method_audit in sorted(methods.items()):
            fixed = method_audit["scores"]["concept_only"]
            reproduced_fixed = _adjusted_scores(
                fixed, forgiven_missed=0, forgiven_spurious=0
            )
            fixed_f1 = float(fixed.get("f1", reproduced_fixed["f1"]))
            if abs(fixed_f1 - reproduced_fixed["f1"]) > 1e-12:
                raise ValueError(f"fixed score reproduction mismatch for {method}")
            forgiven_missed = sum(
                row.get("direction") == "missed" and method in row.get("methods", [])
                for row in selected
            )
            forgiven_spurious = sum(
                row.get("direction") == "spurious" and method in row.get("methods", [])
                for row in selected
            )
            adjusted = _adjusted_scores(
                fixed,
                forgiven_missed=forgiven_missed,
                forgiven_spurious=forgiven_spurious,
            )
            method_results[method] = {
                "adjustments": {
                    "forgiven_missed": forgiven_missed,
                    "forgiven_spurious": forgiven_spurious,
                },
                "fixed_primary_f1": fixed_f1,
                "scores": adjusted,
                "delta_f1_vs_fixed_primary": adjusted["f1"] - fixed_f1,
            }
        views[name] = {
            "description": description,
            "review_rows_in_view": len(selected),
            "mechanism_counts": dict(sorted(mechanism_counts.items())),
            "methods": method_results,
        }

    report = {
        "schema_version": SENSITIVITY_SCHEMA,
        "dataset": audit.get("dataset"),
        "split": audit.get("split", "dev140"),
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "call_mode": "no_calls_review_overlay_arithmetic",
        "fixed_primary_scorer": audit.get("scorer"),
        "primary_result_changed": False,
        "ledger_jsonl": str(ledger_jsonl),
        "ledger_sha256": sha256_file(ledger_jsonl),
        "audit_summary_json": str(audit_summary_json),
        "audit_summary_sha256": sha256_file(audit_summary_json),
        "fixed_reproduction": "passed",
        "views": views,
        "claim_boundary": (
            "Development diagnostic sensitivity only. These views do not modify gold, "
            "the fixed primary scorer, test60, or any holdout claim."
        ),
    }
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _validate_fixed_reproduction(
    ledger: list[Mapping[str, Any]], methods: Mapping[str, Any]
) -> None:
    for method, method_audit in methods.items():
        expected = method_audit["disagreements"]
        observed = Counter(
            str(row.get("direction"))
            for row in ledger
            if method in row.get("methods", [])
        )
        for direction in ("missed", "spurious"):
            if observed[direction] != expected[direction]:
                raise ValueError(
                    f"disagreement count mismatch for {method} {direction}: "
                    f"ledger={observed[direction]}, audit={expected[direction]}"
                )
        if sum(observed.values()) != expected["total"]:
            raise ValueError(
                f"disagreement count mismatch for {method} total: "
                f"ledger={sum(observed.values())}, audit={expected['total']}"
            )


def _adjusted_scores(
    fixed: Mapping[str, Any], *, forgiven_missed: int, forgiven_spurious: int
) -> dict[str, Any]:
    gold_count = int(fixed["gold_count"])
    pred_count = int(fixed["pred_count"])
    recall_tp = int(fixed["recall_tp"]) + forgiven_missed
    precision_tp = int(fixed["precision_tp"]) + forgiven_spurious
    if recall_tp > gold_count or precision_tp > pred_count:
        raise ValueError("sensitivity adjustment exceeds the fixed score denominator")
    recall = recall_tp / gold_count if gold_count else 0.0
    precision = precision_tp / pred_count if pred_count else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "gold_count": gold_count,
        "pred_count": pred_count,
        "recall_tp": recall_tp,
        "precision_tp": precision_tp,
        "remaining_fn": int(fixed["fn"]) - forgiven_missed,
        "remaining_fp": int(fixed["fp"]) - forgiven_spurious,
        "recall": recall,
        "precision": precision,
        "f1": f1,
    }

