"""Freeze H5 repair policy v1 as a bounded downstream diagnostic contract."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

DEFAULT_POLICY_JSON_PATH = Path(
    "experiments/gan2026_h5_repair_policy_v1_reparse_validation250_2026-06-05.json"
)
DEFAULT_TRANSITIONS_CSV_PATH = Path(
    "experiments/"
    "gan2026_h5_semantic_kind_transformations_policy_v1_validation250_2026-06-05.csv"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_h5_repair_policy_v1_manifest_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_h5_repair_policy_v1_manifest_2026-06-05.md"
)

REPAIR_POLICY_ID = "h5_repair_policy_v1"


def build_h5_repair_policy_manifest(
    policy_reparse: Mapping[str, Any],
    semantic_kind_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build the current bounded H5 repair-policy manifest."""

    conditions = {
        str(condition.get("condition")): condition
        for condition in policy_reparse.get("conditions", [])
        if isinstance(condition, Mapping)
    }
    benchmark = _condition_summary(conditions.get("benchmark_aligned_adapter"))
    format_only = _condition_summary(conditions.get("format_only_repair"))
    selected_evidence = _condition_summary(
        conditions.get("selected_evidence_arithmetic_only")
    )
    transitions = Counter(
        str(row.get("semantic_kind_transition") or "") for row in semantic_kind_rows
    )
    by_condition = Counter(str(row.get("condition") or "") for row in semantic_kind_rows)
    invalid_evidence_rows = sum(
        1
        for row in semantic_kind_rows
        if str(row.get("selected_evidence_valid") or "").lower() == "false"
    )

    return {
        "artifact_kind": "gan2026_h5_repair_policy_v1_manifest",
        "date": "2026-06-05",
        "repair_policy_id": REPAIR_POLICY_ID,
        "split": str(policy_reparse.get("split") or "validation"),
        "split_manifest": str(policy_reparse.get("split_manifest") or "gan2026_split_v1"),
        "claim_boundary": (
            "Validation-development H5 repair-policy contract for the next "
            "diagnostic only. It does not authorize holdout use or "
            "benchmark-comparable claims."
        ),
        "inspection_policy": {
            "validation": "policy_summary_and_validation250_transform_rows",
            "locked_test": "not_used",
        },
        "locked_test_row_level_artifacts_used": 0,
        "source_artifacts": {
            "policy_reparse": str(DEFAULT_POLICY_JSON_PATH),
            "semantic_kind_transformations": str(DEFAULT_TRANSITIONS_CSV_PATH),
        },
        "policy_bounds": [
            {
                "bound_id": "frequency_bearing_prediction_may_not_become_no_reference",
                "status": "disabled",
                "rationale": (
                    "Broad frequency-to-no-reference demotion was the unsafe "
                    "semantic repair. Policy v1 leaves zero frequency->no_reference "
                    "semantic-kind transitions."
                ),
            },
            {
                "bound_id": "per_hour_rates_render_as_multiple_per_day",
                "status": "allowed_benchmark_rendering",
                "rationale": (
                    "Hourly electrographic rates preserve frequency-bearing "
                    "content and render to the Gan unresolved-multiple daily bucket."
                ),
            },
            {
                "bound_id": "vague_frequency_words_render_as_unresolved_multiple",
                "status": "allowed_benchmark_rendering",
                "rationale": (
                    "Vague recurring terms such as rare, occasional, frequent, "
                    "or several stay frequency-bearing and render as multiple-* "
                    "labels rather than sentinel no-reference labels."
                ),
            },
            {
                "bound_id": "cluster_context_preserves_frequency_content",
                "status": "allowed_with_explicit_ablation",
                "rationale": (
                    "Cluster language may affect benchmark rendering, but it "
                    "must not erase current frequency evidence."
                ),
            },
            {
                "bound_id": "benchmark_rendering_separate_from_clinical_selection",
                "status": "required",
                "rationale": (
                    "Renderer gains are scorer-facing deterministic behavior and "
                    "must remain separately attributed in downstream diagnostics."
                ),
            },
        ],
        "condition_summaries": {
            "format_only_repair": format_only,
            "selected_evidence_arithmetic_only": selected_evidence,
            "benchmark_aligned_adapter": benchmark,
        },
        "semantic_kind_transformations": {
            "rows": len(semantic_kind_rows),
            "by_transition": dict(sorted(transitions.items())),
            "by_condition": dict(sorted(by_condition.items())),
            "invalid_selected_evidence_rows": invalid_evidence_rows,
            "frequency_to_no_reference_rows": transitions.get(
                "frequency->no_reference", 0
            ),
        },
        "next_diagnostic_contract": {
            "use_as_current_repair_policy": True,
            "do_not_restore_broad_frequency_to_sentinel_repair": True,
            "no_boundary_renderer_change_in_same_repair_experiment": True,
            "report_renderer_separately_from_clinical_selection": True,
            "carry_h6_no_regression_controls": True,
            "holdout_use_authorized": False,
        },
        "decision": "current_bounded_policy_for_next_validation_diagnostic",
    }


def write_h5_repair_policy_manifest_outputs(
    artifact: Mapping[str, Any],
    *,
    json_path: Path,
    markdown_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    write_h5_repair_policy_manifest_report(artifact, markdown_path)


def write_h5_repair_policy_manifest_report(
    artifact: Mapping[str, Any],
    path: Path,
) -> None:
    transitions = artifact.get("semantic_kind_transformations", {})
    benchmark = artifact.get("condition_summaries", {}).get(
        "benchmark_aligned_adapter", {}
    )
    lines = [
        "# Gan 2026 H5 Repair Policy v1 Manifest",
        "",
        "Validation-development policy contract for the next diagnostic. No "
        "locked-test row-level artifacts are used.",
        "",
        f"- Repair policy: `{artifact.get('repair_policy_id')}`",
        f"- Split manifest: `{artifact.get('split_manifest')}`",
        f"- Decision: `{artifact.get('decision')}`",
        "- Locked-test row-level artifacts used: "
        f"`{artifact.get('locked_test_row_level_artifacts_used')}`",
        "- Holdout use authorized: "
        f"`{artifact.get('next_diagnostic_contract', {}).get('holdout_use_authorized')}`",
        "",
        "## Validation250 Replay",
        "",
        "| Condition | Purist | Changed | W->C | C->W | Semantic-kind transitions |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, item in artifact.get("condition_summaries", {}).items():
        if not isinstance(item, Mapping):
            continue
        lines.append(
            "| `{condition}` | {purist} | {changed} | {wtc} | {ctw} | {semantic} |".format(
                condition=condition,
                purist=_metric(item.get("purist_accuracy")),
                changed=_md(item.get("changed_from_raw")),
                wtc=_md(item.get("raw_wrong_to_correct")),
                ctw=_md(item.get("raw_correct_to_wrong")),
                semantic=_md(item.get("semantic_kind_transitions")),
            )
        )
    lines.extend(
        [
            "",
            "## Bounds",
            "",
            "| Bound | Status |",
            "| --- | --- |",
        ]
    )
    for bound in artifact.get("policy_bounds", []):
        if not isinstance(bound, Mapping):
            continue
        lines.append(
            "| `{bound_id}` | `{status}` |".format(
                bound_id=bound.get("bound_id"),
                status=bound.get("status"),
            )
        )
    lines.extend(
        [
            "",
            "## Transformation Guard",
            "",
            f"- Semantic-kind rows: `{transitions.get('rows')}`",
            "- Frequency-to-no-reference rows: "
            f"`{transitions.get('frequency_to_no_reference_rows')}`",
            "- Invalid selected-evidence rows: "
            f"`{transitions.get('invalid_selected_evidence_rows')}`",
            "- Benchmark adapter Purist replay: "
            f"`{_metric(benchmark.get('purist_accuracy'))}`",
            "",
            "## Interpretation",
            "",
            "Use this policy as the bounded H5 repair contract for the next "
            "validation diagnostic. It permits format repair and bounded "
            "benchmark rendering, blocks broad frequency-to-no-reference "
            "demotion, and keeps renderer effects separate from clinical "
            "selection claims.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def load_semantic_kind_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build H5 repair policy manifest.")
    parser.add_argument("--policy-json", type=Path, default=DEFAULT_POLICY_JSON_PATH)
    parser.add_argument("--transitions-csv", type=Path, default=DEFAULT_TRANSITIONS_CSV_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    artifact = build_h5_repair_policy_manifest(
        json.loads(args.policy_json.read_text(encoding="utf-8")),
        load_semantic_kind_rows(args.transitions_csv),
    )
    write_h5_repair_policy_manifest_outputs(
        artifact,
        json_path=args.json,
        markdown_path=args.markdown,
    )
    print(json.dumps({"json": str(args.json), "markdown": str(args.markdown)}, sort_keys=True))


def _condition_summary(condition: Mapping[str, Any] | None) -> dict[str, Any]:
    condition = condition or {}
    score = condition.get("score") if isinstance(condition.get("score"), Mapping) else {}
    repair = (
        condition.get("repair_attribution")
        if isinstance(condition.get("repair_attribution"), Mapping)
        else {}
    )
    return {
        "purist_accuracy": _number(score.get("purist_accuracy")),
        "purist_correct": _int(score.get("purist_correct")),
        "rows": _int(score.get("rows")),
        "changed_from_raw": _int(repair.get("changed_from_raw")),
        "raw_wrong_to_correct": _int(repair.get("raw_wrong_to_condition_correct")),
        "raw_correct_to_wrong": _int(repair.get("raw_correct_to_condition_wrong")),
        "semantic_kind_transitions": _int(repair.get("semantic_kind_transitions")),
    }


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return round(float(value), 4)
    return None


def _metric(value: Any) -> str:
    number = _number(value)
    return "" if number is None else f"{number:.4f}"


def _md(value: Any) -> str:
    return "" if value is None else str(value)


if __name__ == "__main__":
    main()
