"""Build H1 hidden-family validation/test aggregate slice readouts."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    hidden_family_atlas,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

POLICY_NAME = "gan2026_h1_hidden_family_slice_aggregates_v0"
VARIANT = "selective_safety_floor_gate_v0"
DEFAULT_VALIDATION_JSONL_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_"
    "2026-06-03.jsonl"
)
DEFAULT_TEST_JSONL_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_v0_test450_frozen_audit_"
    "first_readout_2026-06-03.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_h1_hidden_family_slice_aggregates_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_h1_hidden_family_slice_aggregates_v0_2026-06-05.md"
)


def build_h1_slice_aggregates(
    validation_rows: Sequence[Mapping[str, Any]],
    test_rows: Sequence[Mapping[str, Any]],
    *,
    validation_records: Mapping[int, GanFrequencyRecord],
    test_records: Mapping[int, GanFrequencyRecord],
    variant: str = VARIANT,
) -> dict[str, Any]:
    """Return aggregate-only H1 hidden-family readouts."""

    validation_family = _family_summaries(
        validation_rows,
        records=validation_records,
        variant=variant,
    )
    test_family = _family_summaries(test_rows, records=test_records, variant=variant)
    family_gaps = _family_gaps(validation_family, test_family)
    decision = _decision(family_gaps)
    return {
        "artifact_kind": "gan2026_h1_hidden_family_slice_aggregates_v0",
        "policy_name": POLICY_NAME,
        "hypothesis_id": "H1",
        "hypothesis": "Hidden-family mix explains the aggregate validation-test gap.",
        "split_manifest": "gan2026_split_v1",
        "candidate_variant": variant,
        "inspection_policy": {
            "validation": "row_level_allowed",
            "locked_test": "aggregate_predeclared_slice_only_no_row_level_failures",
        },
        "source_artifacts": {
            "validation": str(DEFAULT_VALIDATION_JSONL_PATH),
            "locked_test": str(DEFAULT_TEST_JSONL_PATH),
        },
        "validation": _surface_summary(validation_family),
        "locked_test": _surface_summary(test_family),
        "family_gaps": family_gaps,
        "decision": decision,
        "interpretation": _interpretation(decision),
        "locked_test_row_level_artifacts_written": 0,
        "claim_boundary": (
            "H1 aggregate-only predeclared hidden-family slice readout. The "
            "script may read frozen test rows to compute aggregate family "
            "membership and correctness, but it writes no test row ids, clinical "
            "text, raw outputs, or row-level failure records."
        ),
        "recommended_next_step": _recommended_next_step(decision),
    }


def write_report(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 H1 Hidden-Family Slice Aggregates v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Interpretation",
        "",
        str(summary["interpretation"]),
        "",
        "## Surface Summary",
        "",
        "| Split | Rows | Correct | Proxy | Families |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for split_key, label in [("validation", "validation750"), ("locked_test", "test450")]:
        surface = summary[split_key]
        lines.append(
            f"| {label} | {surface['rows']} | {surface['correct_rows']} | "
            f"{_format_rate(surface['purist_proxy'])} | {surface['family_count']} |"
        )
    lines.extend(
        [
            "",
            "## Family Gaps",
            "",
            "| Family | Validation rows | Validation proxy | Test rows | Test proxy | "
            "Gap | Contribution | Action shift |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in summary["family_gaps"]:
        lines.append(
            "| {family} | {validation_rows} | {validation_proxy} | {test_rows} | "
            "{test_proxy} | {gap} | {contribution} | {action_shift} |".format(
                family=f"`{row['family']}`",
                validation_rows=row["validation_rows"],
                validation_proxy=_format_rate(row["validation_purist_proxy"]),
                test_rows=row["test_rows"],
                test_proxy=_format_rate(row["test_purist_proxy"]),
                gap=_format_rate(row["validation_minus_test_gap"]),
                contribution=_format_rate(row["test_weighted_gap_contribution"]),
                action_shift=_format_rate(row["test_minus_validation_changed_rate"]),
            )
        )
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Inspection Boundary",
            "",
            "This artifact writes aggregate family rows only. It does not write test row "
            "ids, clinical text, raw model outputs, or row-level failures.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def materialize_h1_slice_aggregates(
    *,
    validation_jsonl_path: Path = DEFAULT_VALIDATION_JSONL_PATH,
    test_jsonl_path: Path = DEFAULT_TEST_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    validation_records = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    test_records = {record.source_row_index: record for record in load_records_for_split("test")}
    summary = build_h1_slice_aggregates(
        load_jsonl_rows(validation_jsonl_path),
        load_jsonl_rows(test_jsonl_path),
        validation_records=validation_records,
        test_records=test_records,
    )
    summary = {
        **summary,
        "source_artifacts": {
            "validation": str(validation_jsonl_path),
            "locked_test": str(test_jsonl_path),
        },
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
    }
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(summary, output_report_path)
    return summary


def _family_summaries(
    rows: Sequence[Mapping[str, Any]],
    *,
    records: Mapping[int, GanFrequencyRecord],
    variant: str,
) -> list[dict[str, Any]]:
    family_rows: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        for family in _families_for_row(row, records=records, variant=variant):
            family_rows[family].append(row)
    return [
        _summarize_family(family, members, variant=variant)
        for family, members in sorted(family_rows.items())
    ]


def _summarize_family(
    family: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    variant: str,
) -> dict[str, Any]:
    transitions = Counter(_transition(row, variant=variant) for row in rows)
    correct_rows = sum(_variant_correct(row, variant=variant) is True for row in rows)
    changed_rows = sum(_variant_changed(row, variant=variant) is True for row in rows)
    return {
        "family": family,
        "rows": len(rows),
        "correct_rows": correct_rows,
        "purist_proxy": _rate(correct_rows, len(rows)),
        "changed_rows": changed_rows,
        "changed_rate": _rate(changed_rows, len(rows)),
        "wrong_to_correct": transitions["W_to_C"],
        "correct_to_wrong": transitions["C_to_W"],
    }


def _surface_summary(family_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    total_rows = max((int(row["rows"]) for row in family_rows), default=0)
    if not any(row["family"] == "all_rows" for row in family_rows):
        total_rows = sum(int(row["rows"]) for row in family_rows)
    all_rows = next((row for row in family_rows if row["family"] == "all_rows"), None)
    return {
        "rows": int(all_rows["rows"]) if all_rows else total_rows,
        "correct_rows": int(all_rows["correct_rows"]) if all_rows else 0,
        "purist_proxy": all_rows["purist_proxy"] if all_rows else None,
        "family_count": len([row for row in family_rows if row["family"] != "all_rows"]),
        "families": list(family_rows),
    }


def _family_gaps(
    validation_family: Sequence[Mapping[str, Any]],
    test_family: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validation_by_family = {str(row["family"]): row for row in validation_family}
    test_by_family = {str(row["family"]): row for row in test_family}
    test_total = int(test_by_family.get("all_rows", {}).get("rows") or 0)
    rows = []
    for family in sorted(set(validation_by_family) & set(test_by_family)):
        if family == "all_rows":
            continue
        validation = validation_by_family[family]
        test = test_by_family[family]
        gap = float(validation["purist_proxy"]) - float(test["purist_proxy"])
        test_weight = _rate(int(test["rows"]), test_total) or 0.0
        rows.append(
            {
                "family": family,
                "validation_rows": validation["rows"],
                "validation_purist_proxy": validation["purist_proxy"],
                "validation_changed_rate": validation["changed_rate"],
                "test_rows": test["rows"],
                "test_purist_proxy": test["purist_proxy"],
                "test_changed_rate": test["changed_rate"],
                "validation_minus_test_gap": gap,
                "test_weighted_gap_contribution": gap * test_weight,
                "test_minus_validation_changed_rate": (
                    float(test["changed_rate"]) - float(validation["changed_rate"])
                ),
                "validation_w_to_c": validation["wrong_to_correct"],
                "validation_c_to_w": validation["correct_to_wrong"],
                "test_w_to_c": test["wrong_to_correct"],
                "test_c_to_w": test["correct_to_wrong"],
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -max(float(row["test_weighted_gap_contribution"]), 0.0),
            str(row["family"]),
        ),
    )


def _families_for_row(
    row: Mapping[str, Any],
    *,
    records: Mapping[int, GanFrequencyRecord],
    variant: str,
) -> tuple[str, ...]:
    source_row_index = int(row["source_row_index"])
    record = records[source_row_index]
    variant_row = _variant_row(row, variant=variant)
    predicted_label = str(variant_row.get("final_label") or row.get("baseline_label") or "")
    families = hidden_family_atlas.classify_hidden_families(
        note_text=record.note_text,
        gold_label=record.gold_normalized_label,
        predicted_label=predicted_label,
    )
    return ("all_rows", *families)


def _variant_row(row: Mapping[str, Any], *, variant: str) -> Mapping[str, Any]:
    return (row.get("gate_variants") or {}).get(variant) or {}


def _variant_correct(row: Mapping[str, Any], *, variant: str) -> bool:
    return bool(_variant_row(row, variant=variant).get("purist_correct"))


def _variant_changed(row: Mapping[str, Any], *, variant: str) -> bool:
    return bool(_variant_row(row, variant=variant).get("changed"))


def _transition(row: Mapping[str, Any], *, variant: str) -> str:
    before = bool(row.get("deterministic_correct"))
    after = _variant_correct(row, variant=variant)
    if before and after:
        return "C_to_C"
    if before and not after:
        return "C_to_W"
    if not before and after:
        return "W_to_C"
    return "W_to_W"


def _decision(family_gaps: Sequence[Mapping[str, Any]]) -> str:
    positive = [
        float(row["test_weighted_gap_contribution"])
        for row in family_gaps
        if float(row["test_weighted_gap_contribution"]) > 0
    ]
    if not positive:
        return "h1_not_supported_no_positive_family_gap_concentration"
    top_three = sum(sorted(positive, reverse=True)[:3])
    total = sum(positive)
    if total and top_three / total >= 0.6:
        return "h1_plausible_gap_concentrates_in_top_family_slices"
    return "h1_inconclusive_gap_not_strongly_concentrated"


def _interpretation(decision: str) -> str:
    if decision == "h1_plausible_gap_concentrates_in_top_family_slices":
        return (
            "Hidden-family mix is plausible as an explanatory factor. Treat the "
            "top contributing families as priority strata for H3/H7 follow-up, "
            "while remembering family memberships can overlap."
        )
    if decision == "h1_not_supported_no_positive_family_gap_concentration":
        return (
            "This aggregate readout does not show positive family-level gap "
            "concentration for the selected surface."
        )
    return (
        "H1 remains inconclusive: family slices show gaps, but concentration is "
        "not strong enough to explain the aggregate gap alone."
    )


def _recommended_next_step(decision: str) -> str:
    if decision == "h1_plausible_gap_concentrates_in_top_family_slices":
        return (
            "Use the top H1 families to define candidate-exposure and "
            "adversarial/minimal-pair panels before any new architecture."
        )
    return (
        "Do not accept hidden-family mix as the primary explanation yet; move to "
        "H3 candidate-exposure instrumentation and H7 template-brittleness panels."
    )


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _format_rate(value: Any) -> str:
    if value is None:
        return ""
    return f"{float(value):.4f}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validation-jsonl-path",
        type=Path,
        default=DEFAULT_VALIDATION_JSONL_PATH,
    )
    parser.add_argument("--test-jsonl-path", type=Path, default=DEFAULT_TEST_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    materialize_h1_slice_aggregates(
        validation_jsonl_path=args.validation_jsonl_path,
        test_jsonl_path=args.test_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
