"""Pre-ladder component-ablation artifacts for the v5 claim-table selector."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_claim_table_selector import (
    PROMPT_POLICY_TAXONOMY,
    PROMPT_VERSION,
    REQUIRED_ABLATIONS_BEFORE_LADDER,
)

DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_llm_only_claim_table_selector_v5_pre_ladder_component_ablation_2026-06-01.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_claim_table_selector_v5_pre_ladder_component_ablation_2026-06-01.md"
)

CONDITIONS = (
    {
        "name": "raw_model_claim_table",
        "score_layer": "raw",
        "component_role": "prediction-bearing model claim table and final query",
        "enabled": ("LLM claim extraction", "LLM final query"),
        "disabled": (
            "strict schema repair",
            "constrained selector state audit",
            "clean scorer-facing policy",
        ),
    },
    {
        "name": "strict_schema_repair",
        "score_layer": "strict_format",
        "component_role": "non-semantic shape and parser-format compatibility repair",
        "enabled": ("LLM claim extraction", "LLM final query", "strict schema repair"),
        "disabled": ("clean scorer-facing policy",),
    },
    {
        "name": "constrained_selector_state",
        "score_layer": "strict_format",
        "component_role": "claim-table plus selector_decision, cluster_axis, and boundary_state",
        "enabled": (
            "LLM claim extraction",
            "LLM constrained selector",
            "cluster-axis state",
            "boundary-state field",
            "strict schema repair",
        ),
        "disabled": ("clean scorer-facing policy",),
    },
    {
        "name": "clean_scorer_facing_policy",
        "score_layer": "clean_scorer_facing",
        "component_role": "frozen scorer-facing label cleanup after selector state is preserved",
        "enabled": (
            "LLM claim extraction",
            "LLM constrained selector",
            "cluster-axis state",
            "boundary-state field",
            "strict schema repair",
            "clean scorer-facing policy",
        ),
        "disabled": (),
    },
)


def build_claim_table_component_ablation(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_jsonl: str | None = None,
) -> dict[str, Any]:
    """Build a pre-ladder v5 component-ablation payload from saved JSONL rows."""

    return {
        "artifact_kind": "claim_table_component_ablation",
        "prompt_version": PROMPT_VERSION,
        "claim_language": "pre-ladder development attribution artifact, not a benchmark result",
        "validation_ladder_status": {
            "state": "blocked_until_required_ablations_exist",
            "blocked_ladder_sizes": [25, 50, 250],
            "required_ablations_before_ladder_runs": REQUIRED_ABLATIONS_BEFORE_LADDER,
        },
        "source_jsonl": source_jsonl,
        "row_count": len(rows),
        "prompt_policy_ids": [policy["policy_id"] for policy in PROMPT_POLICY_TAXONOMY],
        "state_fields": {
            "claim_fields": ("cluster_axis", "boundary_state"),
            "final_query_fields": ("selector_decision", "cluster_axis", "boundary_state"),
        },
        "conditions": [_condition_payload(condition, rows) for condition in CONDITIONS],
    }


def write_claim_table_component_ablation_json(result: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_claim_table_component_ablation_report(result: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 Claim-Table V5 Pre-Ladder Component Ablation",
        "",
        "This is a pre-ladder development attribution artifact, not a held-out or benchmark "
        "claim.",
        "",
        f"- Prompt version: `{result['prompt_version']}`",
        f"- Source JSONL: `{result.get('source_jsonl') or 'none; design gate only'}`",
        f"- Rows: {result['row_count']}",
        "- Validation ladder status: blocked until required ablations exist for "
        "`25`, `50`, and `250` validation rows.",
        "- Required ablations: "
        + ", ".join(
            f"`{name}`"
            for name in result["validation_ladder_status"][
                "required_ablations_before_ladder_runs"
            ]
        ),
        "",
        "## Condition Summary",
        "",
        "| Condition | Role | Rows | Purist | Pragmatic | Scorable | Selector state | Issues |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in result["conditions"]:
        summary = condition["summary"]
        lines.append(
            f"| {condition['name']} | {condition['component_role']} | {summary['rows']} | "
            f"{summary['purist_accuracy']:.4f} | {summary['pragmatic_accuracy']:.4f} | "
            f"{summary['scorable_rows']} | {summary['selector_state_complete']} | "
            f"{summary['parse_or_validation_issues']} |"
        )

    lines.extend(["", "## Component Map", ""])
    for condition in result["conditions"]:
        enabled = ", ".join(condition["components_enabled"]) or "none"
        disabled = ", ".join(condition["components_disabled"]) or "none"
        lines.extend(
            [
                f"### {condition['name']}",
                "",
                f"- Score layer: `{condition['score_layer']}`",
                f"- Enabled: {enabled}",
                f"- Disabled: {disabled}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate the v5 claim-table pre-ladder component-ablation artifact."
    )
    parser.add_argument("--jsonl", type=Path, default=None)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rows = load_jsonl_rows(args.jsonl) if args.jsonl else []
    result = build_claim_table_component_ablation(
        rows,
        source_jsonl=str(args.jsonl) if args.jsonl else None,
    )
    write_claim_table_component_ablation_json(result, args.json)
    write_claim_table_component_ablation_report(result, args.markdown)
    print(json.dumps({"json": str(args.json), "markdown": str(args.markdown)}, sort_keys=True))


def _condition_payload(
    condition: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    layer = str(condition["score_layer"])
    condition_rows = [_row_payload(row, layer) for row in rows]
    return {
        "name": condition["name"],
        "score_layer": layer,
        "component_role": condition["component_role"],
        "components_enabled": condition["enabled"],
        "components_disabled": condition["disabled"],
        "summary": _summarize_rows(condition_rows),
        "rows": condition_rows,
    }


def _row_payload(row: Mapping[str, Any], layer: str) -> dict[str, Any]:
    score_layer = (row.get("score_layers") or {}).get(layer) or {}
    structured = row.get("structured_record") or {}
    final_query = structured.get("final_query") if isinstance(structured, Mapping) else {}
    claims = structured.get("claims") if isinstance(structured, Mapping) else []
    return {
        "source_row_index": row.get("source_row_index"),
        "prediction_label": score_layer.get("final_label"),
        "gold_label": (row.get("reference") or {}).get("gold_label"),
        "purist_correct": bool(score_layer.get("purist_correct")),
        "pragmatic_correct": bool(score_layer.get("pragmatic_correct")),
        "scorable": bool(score_layer.get("scorable")),
        "selector_decision": _mapping_get(final_query, "selector_decision"),
        "final_query_cluster_axis": _mapping_get(final_query, "cluster_axis"),
        "final_query_boundary_state": _mapping_get(final_query, "boundary_state"),
        "claim_cluster_axis_present": _all_claims_have(claims, "cluster_axis"),
        "claim_boundary_state_present": _all_claims_have(claims, "boundary_state"),
        "selected_evidence_valid": (row.get("evidence_summary") or {}).get(
            "selected_evidence_valid"
        ),
        "parse_or_validation_issues": tuple(str(error) for error in row.get("parse_errors") or ()),
    }


def _summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    count = len(rows)
    purist = sum(bool(row.get("purist_correct")) for row in rows)
    pragmatic = sum(bool(row.get("pragmatic_correct")) for row in rows)
    return {
        "rows": count,
        "scorable_rows": sum(bool(row.get("scorable")) for row in rows),
        "purist_correct": purist,
        "purist_accuracy": round(purist / count, 4) if count else 0.0,
        "pragmatic_correct": pragmatic,
        "pragmatic_accuracy": round(pragmatic / count, 4) if count else 0.0,
        "selector_state_complete": sum(_selector_state_complete(row) for row in rows),
        "parse_or_validation_issues": sum(
            bool(row.get("parse_or_validation_issues")) for row in rows
        ),
    }


def _selector_state_complete(row: Mapping[str, Any]) -> bool:
    return all(
        (
            row.get("selector_decision"),
            row.get("final_query_cluster_axis"),
            row.get("final_query_boundary_state"),
            row.get("claim_cluster_axis_present"),
            row.get("claim_boundary_state_present"),
        )
    )


def _mapping_get(value: Any, key: str) -> Any:
    return value.get(key) if isinstance(value, Mapping) else None


def _all_claims_have(claims: Any, field: str) -> bool:
    return isinstance(claims, list) and bool(claims) and all(
        isinstance(claim, Mapping) and bool(claim.get(field)) for claim in claims
    )


if __name__ == "__main__":
    main()
