"""Inventory H5 semantic repair families before further candidate work."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_REPLACEMENT_JSON_PATH = Path(
    "experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_"
    "2026-06-02.json"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_h5_repair_inventory_v0_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_h5_repair_inventory_v0_2026-06-05.md"
)
DEFAULT_ABLATION_JSON_PATH = Path(
    "experiments/gan2026_h5_repair_family_ablation_v0_2026-06-05.json"
)
DEFAULT_ABLATION_REPORT_PATH = Path(
    "experiments/gan2026_h5_repair_family_ablation_v0_2026-06-05.md"
)


@dataclass(frozen=True)
class RepairFamily:
    family_id: str
    layer: str
    portability_category: str
    semantic_effect: str
    prediction_owner: str
    source_grounding: str
    default_policy: str
    rationale: str


REPAIR_FAMILIES = (
    RepairFamily(
        family_id="format_only_prediction_surface",
        layer="format_only_repair",
        portability_category="general",
        semantic_effect="format_only",
        prediction_owner="llm_selected_label",
        source_grounding="already_selected_label",
        default_policy="allowed",
        rationale=(
            "Parser-compatible spelling, units, whitespace, number words, and "
            "JSON/schema-compatible label surface repairs should preserve the "
            "selected fact."
        ),
    ),
    RepairFamily(
        family_id="selected_evidence_arithmetic",
        layer="selected_evidence_arithmetic_only",
        portability_category="seizure_frequency",
        semantic_effect="denominator_or_window_policy",
        prediction_owner="llm_selected_evidence_then_deterministic_arithmetic",
        source_grounding="selected_exact_evidence",
        default_policy="allowed_with_ablation",
        rationale=(
            "Arithmetic over already selected evidence can be portable, but it "
            "changes denominator/window semantics and must remain separately "
            "ablated from raw model selection."
        ),
    ),
    RepairFamily(
        family_id="benchmark_convention_renderer",
        layer="benchmark_aligned_adapter",
        portability_category="benchmark_format",
        semantic_effect="benchmark_convention_or_sentinel_policy",
        prediction_owner="deterministic_benchmark_renderer",
        source_grounding="typed_or_selected_clinical_state",
        default_policy="review_required",
        rationale=(
            "Gan scorer-facing rendering can be useful, but it must not silently "
            "change clinical state or be counted as LLM-owned clinical selection."
        ),
    ),
    RepairFamily(
        family_id="seizure_free_boundary_duration",
        layer="semantic_repair_helper",
        portability_category="clinical_epilepsy",
        semantic_effect="boundary_state_or_selected_event",
        prediction_owner="deterministic_semantic_repair",
        source_grounding="source_event_dates_and_boundary_evidence",
        default_policy="quarantine_until_panel_ablation",
        rationale=(
            "Seizure-free and last-event duration rules change boundary state and "
            "must be tested on hard/control panels before promotion."
        ),
    ),
    RepairFamily(
        family_id="non_epileptic_current_event_projection",
        layer="semantic_repair_helper",
        portability_category="clinical_epilepsy",
        semantic_effect="semantic_kind_or_sentinel_state",
        prediction_owner="deterministic_semantic_repair",
        source_grounding="non_epileptic_event_evidence",
        default_policy="quarantine_until_panel_ablation",
        rationale=(
            "Mapping current non-epileptic events into a Gan seizure-frequency "
            "label is a clinical boundary and benchmark-convention decision."
        ),
    ),
    RepairFamily(
        family_id="cluster_and_vague_multiple_completion",
        layer="semantic_repair_helper",
        portability_category="benchmark_format",
        semantic_effect="cluster_interpretation_or_benchmark_convention",
        prediction_owner="deterministic_semantic_repair",
        source_grounding="cluster_or_vague_frequency_evidence",
        default_policy="review_required",
        rationale=(
            "Cluster and vague-multiple completion changes benchmark-rendered "
            "labels and should be reported apart from clinical extraction wins."
        ),
    ),
)

CONDITION_TO_FAMILY_ID = {
    "format_only_repair": "format_only_prediction_surface",
    "selected_evidence_arithmetic_only": "selected_evidence_arithmetic",
    "benchmark_aligned_adapter": "benchmark_convention_renderer",
    "full_stack": "benchmark_convention_renderer",
}


def build_h5_semantic_repair_inventory(
    replacement_ablation: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the validation-only H5 repair-family inventory artifact."""

    families = [asdict(family) for family in REPAIR_FAMILIES]
    condition_ladder = _condition_ladder(replacement_ablation)
    category_counts = Counter(family["portability_category"] for family in families)
    policy_counts = Counter(family["default_policy"] for family in families)
    semantic_families = [
        family for family in families if family["semantic_effect"] != "format_only"
    ]
    review_families = [
        family
        for family in families
        if family["default_policy"] in {"review_required", "quarantine_until_panel_ablation"}
    ]

    return {
        "artifact_kind": "gan2026_h5_semantic_repair_inventory_v0",
        "date": "2026-06-05",
        "hypothesis_id": "H5",
        "split_manifest": str(
            replacement_ablation.get("split_manifest") or "gan2026_split_v1"
        ),
        "claim_boundary": (
            "Validation-development repair-family inventory only. This artifact "
            "uses saved validation repair-ladder summaries and static repair "
            "taxonomy; it writes no locked-test row-level artifacts."
        ),
        "inspection_policy": {
            "validation": "summary_and_static_taxonomy",
            "locked_test": "not_used",
        },
        "locked_test_row_level_artifacts_used": 0,
        "source_artifacts": {
            "same_output_ladder": str(DEFAULT_REPLACEMENT_JSON_PATH),
        },
        "summary": {
            "repair_families": len(families),
            "semantic_families": len(semantic_families),
            "quarantined_or_review_required_families": len(review_families),
            "by_portability_category": dict(sorted(category_counts.items())),
            "by_default_policy": dict(sorted(policy_counts.items())),
        },
        "repair_families": families,
        "condition_ladder": condition_ladder,
        "decision": "ready_for_one_family_at_a_time_ablation",
    }


def write_h5_inventory_outputs(
    artifact: Mapping[str, Any],
    *,
    json_path: Path,
    markdown_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    write_h5_inventory_report(artifact, markdown_path)


def build_h5_repair_family_ablation(
    inventory: Mapping[str, Any],
) -> dict[str, Any]:
    """Interpret saved same-output ladder transitions by repair family."""

    family_lookup = {
        str(family.get("family_id")): family
        for family in inventory.get("repair_families", [])
        if isinstance(family, Mapping)
    }
    by_family: dict[str, dict[str, Any]] = {}
    for condition, ladder_item in inventory.get("condition_ladder", {}).items():
        if not isinstance(ladder_item, Mapping):
            continue
        family_id = str(ladder_item.get("family_id") or "")
        family = family_lookup.get(family_id, {})
        entry = by_family.setdefault(
            family_id,
            {
                "family_id": family_id,
                "conditions": [],
                "portability_category": family.get("portability_category"),
                "semantic_effect": family.get("semantic_effect"),
                "default_policy": family.get("default_policy"),
                "changed_from_raw": 0,
                "semantic_kind_transitions": 0,
                "raw_wrong_to_correct": 0,
                "raw_correct_to_wrong": 0,
                "purist_category_transitions": 0,
                "pragmatic_category_transitions": 0,
            },
        )
        entry["conditions"].append(condition)
        _max_int(entry, "changed_from_raw", ladder_item.get("changed_from_raw"))
        _max_int(
            entry,
            "semantic_kind_transitions",
            ladder_item.get("semantic_kind_transitions"),
        )
        _max_int(
            entry,
            "raw_wrong_to_correct",
            ladder_item.get("raw_wrong_to_condition_correct"),
        )
        _max_int(
            entry,
            "raw_correct_to_wrong",
            ladder_item.get("raw_correct_to_condition_wrong"),
        )
        _max_int(
            entry,
            "purist_category_transitions",
            ladder_item.get("purist_category_transitions"),
        )
        _max_int(
            entry,
            "pragmatic_category_transitions",
            ladder_item.get("pragmatic_category_transitions"),
        )

    family_rows = []
    for row in by_family.values():
        row["decision"] = _family_ablation_decision(row)
        family_rows.append(row)
    family_rows.sort(key=lambda item: str(item.get("family_id")))

    return {
        "artifact_kind": "gan2026_h5_repair_family_ablation_v0",
        "date": "2026-06-05",
        "hypothesis_id": "H5",
        "split_manifest": inventory.get("split_manifest") or "gan2026_split_v1",
        "claim_boundary": (
            "Validation-development same-output family ablation over saved H5 "
            "ladder summaries. It does not change prediction policy and does not "
            "use locked-test row-level artifacts."
        ),
        "inspection_policy": {
            "validation": "saved_same_output_ladder",
            "locked_test": "not_used",
        },
        "locked_test_row_level_artifacts_used": 0,
        "source_artifacts": inventory.get("source_artifacts", {}),
        "family_ablation": family_rows,
        "decision": "repair_policy_review_required_before_new_candidate",
    }


def write_h5_repair_family_ablation_outputs(
    artifact: Mapping[str, Any],
    *,
    json_path: Path,
    markdown_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    write_h5_repair_family_ablation_report(artifact, markdown_path)


def write_h5_inventory_report(artifact: Mapping[str, Any], path: Path) -> None:
    summary = artifact.get("summary", {})
    lines = [
        "# Gan 2026 H5 Semantic Repair Inventory",
        "",
        "Validation-development repair taxonomy only. No locked-test row-level "
        "artifacts are used.",
        "",
        f"- Hypothesis: `{artifact.get('hypothesis_id')}`",
        f"- Split manifest: `{artifact.get('split_manifest')}`",
        f"- Decision: `{artifact.get('decision')}`",
        "- Locked-test row-level artifacts used: "
        f"`{artifact.get('locked_test_row_level_artifacts_used')}`",
        "",
        "## Summary",
        "",
        f"- Repair families: `{summary.get('repair_families')}`",
        f"- Semantic families: `{summary.get('semantic_families')}`",
        "- Quarantined or review-required families: "
        f"`{summary.get('quarantined_or_review_required_families')}`",
        "",
        "## Family Taxonomy",
        "",
        "| Family | Layer | Portability | Effect | Default policy |",
        "| --- | --- | --- | --- | --- |",
    ]
    for family in artifact.get("repair_families", []):
        if not isinstance(family, Mapping):
            continue
        lines.append(
            "| `{family}` | `{layer}` | `{portability}` | `{effect}` | `{policy}` |".format(
                family=family.get("family_id"),
                layer=family.get("layer"),
                portability=family.get("portability_category"),
                effect=family.get("semantic_effect"),
                policy=family.get("default_policy"),
            )
        )
    lines.extend(
        [
            "",
            "## Saved Ladder Mapping",
            "",
            "| Condition | Family | Changed | Semantic-kind transitions | W->C | C->W |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for condition, item in sorted(artifact.get("condition_ladder", {}).items()):
        if not isinstance(item, Mapping):
            continue
        lines.append(
            "| `{condition}` | `{family}` | {changed} | {semantic} | {wtc} | {ctw} |".format(
                condition=condition,
                family=item.get("family_id"),
                changed=_md(item.get("changed_from_raw")),
                semantic=_md(item.get("semantic_kind_transitions")),
                wtc=_md(item.get("raw_wrong_to_condition_correct")),
                ctw=_md(item.get("raw_correct_to_condition_wrong")),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This inventory separates format-only label cleanup from semantic repair "
            "families that can change the prediction-bearing clinical state or "
            "Gan-rendered label. The next experiment should disable or isolate one "
            "semantic family at a time; no boundary/renderer or action-policy "
            "changes should be mixed into that ablation.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def write_h5_repair_family_ablation_report(
    artifact: Mapping[str, Any],
    path: Path,
) -> None:
    lines = [
        "# Gan 2026 H5 Repair Family Ablation",
        "",
        "Validation-development same-output ladder interpretation only. No "
        "prediction policy changes or locked-test row-level artifacts are used.",
        "",
        f"- Hypothesis: `{artifact.get('hypothesis_id')}`",
        f"- Split manifest: `{artifact.get('split_manifest')}`",
        f"- Decision: `{artifact.get('decision')}`",
        "- Locked-test row-level artifacts used: "
        f"`{artifact.get('locked_test_row_level_artifacts_used')}`",
        "",
        "## Family Decisions",
        "",
        "| Family | Changed | Semantic-kind transitions | W->C | C->W | Decision |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in artifact.get("family_ablation", []):
        if not isinstance(row, Mapping):
            continue
        lines.append(
            "| `{family}` | {changed} | {semantic} | {wtc} | {ctw} | `{decision}` |".format(
                family=row.get("family_id"),
                changed=_md(row.get("changed_from_raw")),
                semantic=_md(row.get("semantic_kind_transitions")),
                wtc=_md(row.get("raw_wrong_to_correct")),
                ctw=_md(row.get("raw_correct_to_wrong")),
                decision=row.get("decision"),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Format-only repair remains allowed. Any family with semantic-kind, "
            "Purist/Pragmatic category, or raw-correct-to-wrong transitions needs "
            "a bounded policy decision before it can contribute to a promoted "
            "candidate. Benchmark rendering remains review-required because its "
            "wins are scorer-facing unless clinical state preservation is shown "
            "separately.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build H5 repair-family inventory.")
    parser.add_argument("--replacement-json", type=Path, default=DEFAULT_REPLACEMENT_JSON_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--ablation-json", type=Path, default=DEFAULT_ABLATION_JSON_PATH)
    parser.add_argument(
        "--ablation-markdown",
        type=Path,
        default=DEFAULT_ABLATION_REPORT_PATH,
    )
    args = parser.parse_args(argv)

    artifact = build_h5_semantic_repair_inventory(
        json.loads(args.replacement_json.read_text(encoding="utf-8"))
    )
    write_h5_inventory_outputs(artifact, json_path=args.json, markdown_path=args.markdown)
    ablation = build_h5_repair_family_ablation(artifact)
    write_h5_repair_family_ablation_outputs(
        ablation,
        json_path=args.ablation_json,
        markdown_path=args.ablation_markdown,
    )
    print(
        json.dumps(
            {
                "ablation_json": str(args.ablation_json),
                "ablation_markdown": str(args.ablation_markdown),
                "json": str(args.json),
                "markdown": str(args.markdown),
            },
            sort_keys=True,
        )
    )


def _family_ablation_decision(row: Mapping[str, Any]) -> str:
    if row.get("semantic_effect") == "format_only":
        return "keep_allowed"
    if _int(row.get("raw_correct_to_wrong")):
        return "revise_or_bound"
    if row.get("default_policy") in {"review_required", "quarantine_until_panel_ablation"}:
        return str(row.get("default_policy"))
    if _int(row.get("semantic_kind_transitions")) or _int(
        row.get("purist_category_transitions")
    ):
        return "allowed_with_explicit_ablation"
    return "diagnostic_only"


def _condition_ladder(replacement_ablation: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    ladder: dict[str, dict[str, Any]] = {}
    for condition in replacement_ablation.get("conditions", []):
        if not isinstance(condition, Mapping):
            continue
        condition_name = str(condition.get("condition") or "")
        if condition_name not in CONDITION_TO_FAMILY_ID:
            continue
        repair = (
            condition.get("repair_attribution")
            if isinstance(condition.get("repair_attribution"), Mapping)
            else {}
        )
        ladder[condition_name] = {
            "family_id": CONDITION_TO_FAMILY_ID[condition_name],
            "changed_from_raw": _int(repair.get("changed_from_raw")),
            "exact_normalized_label_transitions": _int(
                repair.get("exact_normalized_label_transitions")
            ),
            "pragmatic_category_transitions": _int(
                repair.get("pragmatic_category_transitions")
            ),
            "purist_category_transitions": _int(repair.get("purist_category_transitions")),
            "semantic_kind_transitions": _int(repair.get("semantic_kind_transitions")),
            "raw_wrong_to_condition_correct": _int(
                repair.get("raw_wrong_to_condition_correct")
            ),
            "raw_correct_to_condition_wrong": _int(
                repair.get("raw_correct_to_condition_wrong")
            ),
        }
    return ladder


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _max_int(target: dict[str, Any], key: str, value: Any) -> None:
    parsed = _int(value)
    if parsed is not None:
        target[key] = max(target[key], parsed)


def _md(value: Any) -> str:
    return "" if value is None else str(value)


if __name__ == "__main__":
    main()
