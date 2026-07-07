"""Build the authorized Gate 4 constrained aggregate audit.

The user authorized one frozen aggregate-only locked test450 audit after Gate 3
passed in constrained source-symmetry mode. This script runs a no-call replay of
the frozen v0.9 selector over the Gate 3 component set and writes only aggregate
JSON/Markdown outputs. It intentionally does not write selector rows, row-level
transitions, rationales, evidence, selected events, or failures.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    consensus_fresh_agreement_selector as selector,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

DATE = "2026-06-26"
RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_"
    f"constrained_aggregate_audit_{DATE}"
)
JSON_OUT = EXPERIMENTS / f"{RUN_ID}.json"
MD_OUT = EXPERIMENTS / f"{RUN_ID}.md"

DET_PATH = (
    EXPERIMENTS / "gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_"
    "gpt41mini_2026-06-09.jsonl"
)
CONSENSUS_PATH = (
    EXPERIMENTS / "gan2026_agentic_structured_event_consensus_available_two_agent_exact_"
    "test450_2026-06-13.jsonl"
)
FRESH_PATH = (
    EXPERIMENTS / "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_"
    "2026-06-15.jsonl"
)
GATE3_JSON = (
    EXPERIMENTS / "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_"
    "source_symmetry_preflight_2026-06-26.json"
)


def main() -> None:
    gate3 = json.loads(GATE3_JSON.read_text(encoding="utf-8"))
    if gate3.get("gate_passed") is not True:
        raise SystemExit("Gate 4 blocked: Gate 3 did not pass.")
    if gate3.get("gate_scope") != "constrained_source_symmetry":
        raise SystemExit("Gate 4 expected constrained Gate 3 scope.")

    deterministic_rows = _load_data_rows(DET_PATH)
    consensus_rows = _load_data_rows(CONSENSUS_PATH)
    fresh_rows = _load_data_rows(FRESH_PATH)

    selector_rows = selector.build_selector_rows(
        deterministic_rows=deterministic_rows,
        consensus_rows=consensus_rows,
        fresh_evidence_rows=fresh_rows,
        policy="semantic_equiv_unknown_uncertainty_v0_9",
    )
    payload = _aggregate_payload(
        selector_rows=selector_rows,
        deterministic_rows=deterministic_rows,
        consensus_rows=consensus_rows,
        fresh_rows=fresh_rows,
        gate3=gate3,
    )
    JSON_OUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MD_OUT.write_text(_render_markdown(payload), encoding="utf-8")
    _register(payload)
    print(
        json.dumps(
            {
                "ok": True,
                "gate_passed": payload["promotion_gate"]["gate_passed"],
                "selected_purist_correct": payload["aggregate"]["selected_purist_correct"],
                "deterministic_purist_correct": payload["aggregate"][
                    "deterministic_purist_correct"
                ],
                "scope": payload["claim_scope"],
            },
            sort_keys=True,
        )
    )


def _load_data_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict) and "_metadata" in row:
            continue
        rows.append(row)
    return rows


def _aggregate_payload(
    *,
    selector_rows: list[dict[str, Any]],
    deterministic_rows: list[dict[str, Any]],
    consensus_rows: list[dict[str, Any]],
    fresh_rows: list[dict[str, Any]],
    gate3: dict[str, Any],
) -> dict[str, Any]:
    summary = selector.summarize_rows(selector_rows)
    aggregate = {
        "rows": len(selector_rows),
        "deterministic_purist_correct": summary["deterministic_purist_correct"],
        "deterministic_purist_rate": _rate(summary["deterministic_purist_correct"]),
        "deterministic_pragmatic_correct": _count_layer(
            selector_rows, "deterministic", "pragmatic_correct"
        ),
        "deterministic_pragmatic_rate": _rate(
            _count_layer(selector_rows, "deterministic", "pragmatic_correct")
        ),
        "consensus_purist_correct": summary["consensus_purist_correct"],
        "consensus_purist_rate": _rate(summary["consensus_purist_correct"]),
        "fresh_evidence_purist_correct": summary["fresh_evidence_purist_correct"],
        "fresh_evidence_purist_rate": _rate(summary["fresh_evidence_purist_correct"]),
        "selected_purist_correct": summary["selected_purist_correct"],
        "selected_purist_rate": _rate(summary["selected_purist_correct"]),
        "selected_pragmatic_correct": _count_layer(selector_rows, "selected", "pragmatic_correct"),
        "selected_pragmatic_rate": _rate(
            _count_layer(selector_rows, "selected", "pragmatic_correct")
        ),
        "net_purist_gain_vs_deterministic": summary["net_purist_gain_vs_deterministic"],
        "changed_labels": summary["changed_labels"],
        "wrong_to_correct": summary["wrong_to_correct"],
        "correct_to_wrong": summary["correct_to_wrong"],
        "wrong_to_wrong": summary["wrong_to_wrong"],
        "correct_to_correct": summary["correct_to_correct"],
        "changed_label_precision": summary["changed_label_precision"],
        "selector_action_counts": summary["actions"],
    }
    promotion_gate = {
        "gate_passed": _promotion_gate_passed(aggregate),
        "selected_gain_at_least_10": aggregate["net_purist_gain_vs_deterministic"] >= 10,
        "correct_to_wrong_at_most_5": aggregate["correct_to_wrong"] <= 5,
        "changed_label_precision_at_least_0_60": (
            aggregate["changed_label_precision"] is not None
            and aggregate["changed_label_precision"] >= 0.60
        ),
        "source_integrity_ok": gate3.get("coverage_ok") is True,
        "source_symmetry_exact": False,
        "claim_scope_limited_to_constrained_holdout_evidence": True,
    }
    return {
        "run_id": RUN_ID,
        "date": DATE,
        "authorization": "user_authorized_2026-06-26",
        "selector_policy": "semantic_equiv_unknown_uncertainty_v0_9",
        "claim_scope": "constrained_holdout_evidence",
        "inspection_boundary": {
            "aggregate_only": True,
            "row_level_output_written": False,
            "test_row_failures_opened_for_development": False,
            "forbidden_content_reported": False,
        },
        "source_artifacts": _source_artifacts(),
        "component_integrity": {
            "deterministic": _component_counts(deterministic_rows, DET_PATH),
            "consensus": _component_counts(consensus_rows, CONSENSUS_PATH),
            "fresh_evidence": _component_counts(fresh_rows, FRESH_PATH),
        },
        "gate3_reference": {
            "path": _rel(GATE3_JSON),
            "sha256": _sha256(GATE3_JSON),
            "scope": gate3.get("gate_scope"),
            "exact_consensus_available": gate3.get("exact_consensus_available"),
        },
        "aggregate": aggregate,
        "promotion_gate": promotion_gate,
        "interpretation": _interpretation(promotion_gate),
    }


def _promotion_gate_passed(aggregate: dict[str, Any]) -> bool:
    precision = aggregate["changed_label_precision"]
    return (
        aggregate["net_purist_gain_vs_deterministic"] >= 10
        and aggregate["correct_to_wrong"] <= 5
        and precision is not None
        and precision >= 0.60
    )


def _component_counts(rows: list[dict[str, Any]], path: Path) -> dict[str, Any]:
    source_ids = [int(row["source_row_index"]) for row in rows]
    counts = Counter(source_ids)
    return {
        "path": _rel(path),
        "sha256": _sha256(path),
        "rows": len(rows),
        "unique_source_rows": len(set(source_ids)),
        "duplicate_source_rows": sum(1 for count in counts.values() if count > 1),
        "call_failure_rows": sum(1 for row in rows if row.get("call_error")),
        "parse_or_repair_note_rows": sum(1 for row in rows if row.get("parse_errors")),
    }


def _source_artifacts() -> dict[str, str]:
    return {
        "deterministic": _rel(DET_PATH),
        "consensus": _rel(CONSENSUS_PATH),
        "fresh_evidence": _rel(FRESH_PATH),
    }


def _count_layer(rows: list[dict[str, Any]], layer: str, field: str) -> int:
    return sum(row["score_layers"][layer]["comparison"].get(field) is True for row in rows)


def _rate(count: int) -> float:
    return round(count / 450, 4)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _interpretation(promotion_gate: dict[str, Any]) -> str:
    if promotion_gate["gate_passed"]:
        return (
            "Numeric Gate 4 bars pass, but Gate 3 source symmetry was constrained. "
            "Record as constrained holdout evidence only; do not call it an exact "
            "v0.9 selector holdout claim or a clean architecture comparator."
        )
    return (
        "Gate 4 numeric bars fail. Record as final-evaluation evidence and return "
        "any follow-up to validation-only component-generation work."
    )


def _render_markdown(payload: dict[str, Any]) -> str:
    agg = payload["aggregate"]
    gate = payload["promotion_gate"]
    lines = [
        "# Gan 2026 Consensus/Fresh v0.9 Gate 4 Constrained Aggregate Audit",
        "",
        f"- Date: `{payload['date']}`",
        "- Authorization: `user_authorized_2026-06-26`",
        "- Surface: locked `test450`, aggregate-only readout",
        "- Source symmetry: `constrained`, not exact",
        "- Row-level output written: `false`",
        "",
        "## Aggregate Readout",
        "",
        f"- Deterministic Purist: `{agg['deterministic_purist_correct']}/450` "
        f"(`{agg['deterministic_purist_rate']}`)",
        f"- Deterministic Pragmatic: `{agg['deterministic_pragmatic_correct']}/450` "
        f"(`{agg['deterministic_pragmatic_rate']}`)",
        f"- Consensus Purist: `{agg['consensus_purist_correct']}/450` "
        f"(`{agg['consensus_purist_rate']}`)",
        f"- Fresh-evidence Purist: `{agg['fresh_evidence_purist_correct']}/450` "
        f"(`{agg['fresh_evidence_purist_rate']}`)",
        f"- Selected Purist: `{agg['selected_purist_correct']}/450` "
        f"(`{agg['selected_purist_rate']}`)",
        f"- Selected Pragmatic: `{agg['selected_pragmatic_correct']}/450` "
        f"(`{agg['selected_pragmatic_rate']}`)",
        f"- Net Purist gain vs deterministic: `{agg['net_purist_gain_vs_deterministic']}`",
        f"- Changed labels: `{agg['changed_labels']}`",
        f"- Wrong->correct: `{agg['wrong_to_correct']}`",
        f"- Correct->wrong: `{agg['correct_to_wrong']}`",
        f"- Changed-label precision: `{agg['changed_label_precision']}`",
        f"- Selector actions: `{agg['selector_action_counts']}`",
        "",
        "## Gate Checks",
        "",
    ]
    for key, value in gate.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Component Integrity",
            "",
            "| Component | Rows | Unique Rows | Duplicate Rows | Call Failures | "
            "Parse/Repair Rows | SHA-256 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for name, info in payload["component_integrity"].items():
        lines.append(
            f"| `{name}` | {info['rows']} | {info['unique_source_rows']} | "
            f"{info['duplicate_source_rows']} | {info['call_failure_rows']} | "
            f"{info['parse_or_repair_note_rows']} | `{info['sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            payload["interpretation"],
            "",
            "No test row-level failures, rationales, evidence, selected events, or "
            "row-level transitions were written to this artifact.",
            "",
        ]
    )
    return "\n".join(lines)


def _register(payload: dict[str, Any]) -> None:
    aggregate = payload["aggregate"]
    gate = payload["promotion_gate"]
    entry = RunRegistryEntry(
        run_id=RUN_ID,
        artifact_paths=(
            f"experiments/{RUN_ID}.json",
            f"experiments/{RUN_ID}.md",
            "experiments/build_gan2026_v09_frozen_gate4_constrained_aggregate_audit.py",
        ),
        date=DATE,
        pipeline_family="consensus_fresh_agreement_selector_frozen_gate4",
        split="test",
        row_count=450,
        model="none",
        model_role=(
            "No-call aggregate-only replay of frozen v0.9 selector over Gate 3 "
            "constrained deterministic, two-agent consensus, and fresh-evidence "
            "test components."
        ),
        mode="no-call replay",
        replay_status="saved_output_replay",
        decision="promote" if gate["gate_passed"] else "reject",
        primary_metrics={
            "gate_passed": "yes" if gate["gate_passed"] else "no",
            "claim_scope": payload["claim_scope"],
            "deterministic_purist_correct": aggregate["deterministic_purist_correct"],
            "selected_purist_correct": aggregate["selected_purist_correct"],
            "selected_pragmatic_correct": aggregate["selected_pragmatic_correct"],
            "net_purist_gain_vs_deterministic": aggregate["net_purist_gain_vs_deterministic"],
            "changed_labels": aggregate["changed_labels"],
            "wrong_to_correct": aggregate["wrong_to_correct"],
            "correct_to_wrong": aggregate["correct_to_wrong"],
            "changed_label_precision": aggregate["changed_label_precision"],
            "exact_source_symmetry": "no",
            "row_level_output_written": "no",
        },
        repair_mode="selector_v0_9_constrained_no_call_replay",
        cache_reuse_source=(
            "Gate 3 constrained source set: deterministic DCP test450, available "
            "two-agent consensus test450, and V12 fresh-evidence v0.6/safety-v0.9 "
            "test450 artifact."
        ),
        evidence_validity=(
            "User-authorized frozen aggregate-only locked test450 audit. No row-level "
            "failures, rationales, evidence, selected events, or transitions are "
            "reported; source symmetry is constrained, not exact."
        ),
        supersedes=(
            "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_"
            "source_symmetry_preflight_2026-06-26",
        ),
        claim_language_notes=payload["interpretation"],
        registry_roles=("holdout_anchor", "component_ladder"),
    )
    entries = [item for item in load_run_registry(REGISTRY_PATH) if item.run_id != RUN_ID]
    entries.append(entry)
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts([entry], repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
