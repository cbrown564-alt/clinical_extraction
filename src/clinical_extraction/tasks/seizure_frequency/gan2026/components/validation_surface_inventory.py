"""Inventory available validation750 artifacts for staged hybrid assembly."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_REASONER_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_"
    "deterministic_safety_floor_v2_replay_2026-06-03.jsonl"
)
DEFAULT_SAFETY_FLOOR_JSONL_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.jsonl"
)
DEFAULT_SAFETY_FLOOR_JSON_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.json"
)
DEFAULT_ROUTER_JSONL_PATH = Path(
    "experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl"
)
DEFAULT_ROUTER_JSON_PATH = Path(
    "experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.json"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_staged_hybrid_validation750_input_inventory_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_staged_hybrid_validation750_input_inventory_2026-06-04.md"
)


def summarize_reasoner_replay(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize the full-validation hybrid reasoner replay surface."""

    component_status_counts: dict[str, dict[str, int]] = {}
    for row in rows:
        for name, status in row.get("component_status", {}).items():
            component_status_counts.setdefault(name, {})
            component_status_counts[name][str(status)] = (
                component_status_counts[name].get(str(status), 0) + 1
            )

    return {
        "component_name": "hybrid_reasoner_replay",
        "row_count": len(rows),
        "source_row_count": _unique_source_row_count(rows),
        "source_row_coverage": _coverage_label(rows),
        "component_status_counts": component_status_counts,
        "ready_for_staged_assembly": True,
        "assembly_role": "historical full-validation source candidate replay",
        "notes": [
            "Provides full-validation source rows and source-id status.",
            "Saved prompt payloads are historical evidence, not prompt text to reuse.",
        ],
    }


def summarize_safety_floor_gate(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize the full-validation selective safety-floor gate surface."""

    variant_summary = (
        (summary or {})
        .get("slice_summary", {})
        .get("validation750", {})
        .get("variant_summary", {})
    )
    combined_summary = variant_summary.get("combined_selective_gate_v0", {})

    return {
        "component_name": "selective_safety_floor_gate_v0",
        "row_count": len(rows),
        "source_row_count": _unique_source_row_count(rows),
        "source_row_coverage": _coverage_label(rows),
        "selected_evidence_exact_rows": _truthy_count(rows, "selected_evidence_exact"),
        "selected_source_ids_exist_rows": _truthy_count(rows, "selected_source_ids_exist"),
        "combined_gate_summary": combined_summary,
        "ready_for_staged_assembly": True,
        "assembly_role": "full-validation safety floor and rescue gate replay",
        "notes": [
            "Provides full-validation evidence/source-id quality checks.",
            "Combined gate summary is development accounting, not benchmark evidence.",
        ],
    }


def summarize_selective_action_router(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize the full-validation selective-action router surface."""

    action_counts = Counter(str(row.get("selective_action")) for row in rows)
    metrics = dict((summary or {}).get("metrics", {}))

    return {
        "component_name": "rq9_selective_action_router_v3",
        "row_count": len(rows),
        "source_row_count": _unique_source_row_count(rows),
        "source_row_coverage": _coverage_label(rows),
        "action_counts": dict(sorted(action_counts.items())),
        "metrics": metrics,
        "ready_for_staged_assembly": True,
        "assembly_role": "full-validation selective predict/abstain/review policy",
        "notes": [
            "Gold and human-review fields are development accounting only.",
            "Router predictions do not authorize locked-test or benchmark-comparable claims.",
        ],
    }


def build_validation_surface_inventory(
    *,
    reasoner_rows: Sequence[Mapping[str, Any]],
    safety_floor_rows: Sequence[Mapping[str, Any]],
    router_rows: Sequence[Mapping[str, Any]],
    safety_floor_summary: Mapping[str, Any] | None = None,
    router_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a claim-bounded inventory of available validation750 inputs."""

    available_components = [
        summarize_reasoner_replay(reasoner_rows),
        summarize_safety_floor_gate(safety_floor_rows, safety_floor_summary),
        summarize_selective_action_router(router_rows, router_summary),
    ]
    component_row_counts = {
        component["component_name"]: component["row_count"]
        for component in available_components
    }
    full_validation_components = [
        component["component_name"]
        for component in available_components
        if component["row_count"] == 750 and component["source_row_count"] == 750
    ]

    return {
        "artifact_kind": "gan2026_staged_hybrid_validation750_input_inventory",
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "claim_language": (
            "Inventory of saved validation750 component surfaces for staged assembly. "
            "This artifact makes no new model calls and does not authorize locked-test "
            "inspection, whole-pipeline promotion, or benchmark-comparable claims."
        ),
        "available_components": available_components,
        "component_row_counts": component_row_counts,
        "full_validation_components": full_validation_components,
        "missing_component_inputs": [
            {
                "component_name": "rich_selected_state_fact_carrier",
                "needed_for": "new selected-state union assembly contract",
                "status": "not materialized at validation750 in the current component shape",
            },
            {
                "component_name": "boundary_v3_selected_state_candidates",
                "needed_for": "validation750 selected-state union replay",
                "status": (
                    "hard-panel artifact exists; validation750 component input "
                    "not identified"
                ),
            },
            {
                "component_name": "promoted_binary_selective_verifier",
                "needed_for": "full-validation verifier effect estimate",
                "status": (
                    "saved slice exists; full-validation use needs predeclared "
                    "calls or gating"
                ),
            },
        ],
        "next_assembly_action": (
            "Adapt the available validation750 source-candidate, safety-floor, and "
            "router surfaces into assembly rows first; keep the verifier slice separate "
            "until a full-validation verifier protocol exists."
        ),
    }


def write_summary_json(inventory: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(inventory: Mapping[str, Any], path: Path, *, json_path: Path) -> None:
    lines = [
        "# Gan 2026 Staged Hybrid Validation750 Input Inventory",
        "",
        str(inventory["claim_language"]),
        "",
        "## Available Components",
        "",
        "| Component | Rows | Unique source rows | Ready | Assembly role |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for component in inventory["available_components"]:
        lines.append(
            f"| `{component['component_name']}` | {component['row_count']} | "
            f"{component['source_row_count']} | "
            f"{'yes' if component['ready_for_staged_assembly'] else 'no'} | "
            f"{component['assembly_role']} |"
        )

    lines.extend(
        [
            "",
            "## Missing Inputs",
            "",
            "| Component | Needed for | Status |",
            "| --- | --- | --- |",
        ]
    )
    for component in inventory["missing_component_inputs"]:
        lines.append(
            f"| `{component['component_name']}` | {component['needed_for']} | "
            f"{component['status']} |"
        )

    lines.extend(
        [
            "",
            "## Next Assembly Action",
            "",
            str(inventory["next_assembly_action"]),
            "",
            "## Artifact",
            "",
            f"- Summary JSON: `{json_path}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _truthy_count(rows: Sequence[Mapping[str, Any]], key: str) -> int:
    return sum(bool(row.get(key)) for row in rows)


def _unique_source_row_count(rows: Sequence[Mapping[str, Any]]) -> int:
    return len({int(row["source_row_index"]) for row in rows if row.get("source_row_index")})


def _coverage_label(rows: Sequence[Mapping[str, Any]]) -> str:
    row_count = len(rows)
    source_count = _unique_source_row_count(rows)
    if row_count == 750 and source_count == 750:
        return "validation750"
    return f"{row_count} rows / {source_count} unique source rows"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reasoner-jsonl-path", type=Path, default=DEFAULT_REASONER_JSONL_PATH)
    parser.add_argument(
        "--safety-floor-jsonl-path", type=Path, default=DEFAULT_SAFETY_FLOOR_JSONL_PATH
    )
    parser.add_argument(
        "--safety-floor-json-path", type=Path, default=DEFAULT_SAFETY_FLOOR_JSON_PATH
    )
    parser.add_argument("--router-jsonl-path", type=Path, default=DEFAULT_ROUTER_JSONL_PATH)
    parser.add_argument("--router-json-path", type=Path, default=DEFAULT_ROUTER_JSON_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    inventory = build_validation_surface_inventory(
        reasoner_rows=load_jsonl_rows(args.reasoner_jsonl_path),
        safety_floor_rows=load_jsonl_rows(args.safety_floor_jsonl_path),
        router_rows=load_jsonl_rows(args.router_jsonl_path),
        safety_floor_summary=_load_json(args.safety_floor_json_path),
        router_summary=_load_json(args.router_json_path),
    )
    inventory = {
        **inventory,
        "source_artifacts": {
            "reasoner_jsonl": str(args.reasoner_jsonl_path),
            "safety_floor_jsonl": str(args.safety_floor_jsonl_path),
            "safety_floor_json": str(args.safety_floor_json_path),
            "router_jsonl": str(args.router_jsonl_path),
            "router_json": str(args.router_json_path),
        },
    }
    write_summary_json(inventory, args.json_path)
    write_report(inventory, args.report_path, json_path=args.json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
