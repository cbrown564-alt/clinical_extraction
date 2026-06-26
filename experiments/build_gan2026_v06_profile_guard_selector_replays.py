"""Build v0.6 profile-guard selector replay artifacts.

The script replays the v0.6 selector over two existing no-call surfaces:

* the saved v0.5 validation750 selector rows;
* the v0.5 synthetic boundary-rescue stress panel.

No Gan holdout rows are read, and no model calls are made.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    consensus_fresh_agreement_selector as selector,
)
from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

SOURCE_VALIDATION_JSONL = (
    EXPERIMENTS
    / "gan2026_consensus_fresh_agreement_selector_v0_5_"
    "validation750_no_call_replay_2026-06-15.jsonl"
)
SOURCE_SYNTHETIC_JSON = (
    EXPERIMENTS
    / "gan2026_consensus_fresh_agreement_selector_v0_5_"
    "boundary_rescue_synthetic_stress_2026-06-15.json"
)

VALIDATION_RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_6_"
    "validation750_no_call_replay_2026-06-15"
)
SYNTHETIC_RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_6_"
    "boundary_rescue_synthetic_stress_2026-06-15"
)


def main() -> None:
    validation_rows = _load_jsonl(SOURCE_VALIDATION_JSONL)
    v06_validation_rows = _replay_v06(validation_rows)
    validation_jsonl = EXPERIMENTS / f"{VALIDATION_RUN_ID}.jsonl"
    validation_md = EXPERIMENTS / f"{VALIDATION_RUN_ID}.md"
    _write_jsonl(v06_validation_rows, validation_jsonl)
    selector.write_report(
        v06_validation_rows,
        validation_md,
        jsonl_path=validation_jsonl,
        source_artifacts={
            "v0.5_selector_rows": str(SOURCE_VALIDATION_JSONL),
            "replay_source": "reconstructed component rows from v0.5 selector rows",
        },
    )

    source_synthetic = json.loads(SOURCE_SYNTHETIC_JSON.read_text(encoding="utf-8"))
    v06_synthetic_rows = _replay_v06(source_synthetic["rows"])
    for new_row, old_row in zip(
        v06_synthetic_rows,
        source_synthetic["rows"],
        strict=True,
    ):
        new_row["synthetic_case"] = old_row["synthetic_case"]
        new_row["desired_future_action_match"] = (
            new_row["selector_action"]
            == old_row["synthetic_case"]["desired_future_action"]
        )
    synthetic_summary = _synthetic_summary(v06_synthetic_rows)
    synthetic_json = EXPERIMENTS / f"{SYNTHETIC_RUN_ID}.json"
    synthetic_md = EXPERIMENTS / f"{SYNTHETIC_RUN_ID}.md"
    synthetic_payload = {
        "run_id": SYNTHETIC_RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Synthetic replay of v0.6 profile-guard boundary rescue over the "
            "predeclared v0.5 boundary-rescue stress cases."
        ),
        "source_artifact": str(SOURCE_SYNTHETIC_JSON),
        "selector_summary": selector.summarize_rows(v06_synthetic_rows),
        "stress_summary": synthetic_summary,
        "rows": v06_synthetic_rows,
    }
    synthetic_json.write_text(
        json.dumps(synthetic_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    synthetic_md.write_text(_synthetic_markdown(synthetic_payload), encoding="utf-8")

    _register_validation(selector.summarize_rows(v06_validation_rows))
    _register_synthetic(synthetic_summary, selector.summarize_rows(v06_synthetic_rows))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _replay_v06(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deterministic_rows, consensus_rows, fresh_rows = _component_rows(source_rows)
    return selector.build_selector_rows(
        deterministic_rows=deterministic_rows,
        consensus_rows=consensus_rows,
        fresh_evidence_rows=fresh_rows,
        policy="profile_guard_boundary_rescue_v0_6",
    )


def _component_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    deterministic_rows = []
    consensus_rows = []
    fresh_rows = []
    for row in rows:
        source_row_index = row["source_row_index"]
        deterministic_rows.append(
            {
                "source_row_index": source_row_index,
                "final_label": row["deterministic_label"],
                "comparison": row["score_layers"]["deterministic"]["comparison"],
                "reference": row["reference"],
            }
        )
        features = row.get("decision_features", {})
        consensus_rows.append(
            {
                "source_row_index": source_row_index,
                "consensus_final_label": row["consensus_label"],
                "consensus_comparison": row["score_layers"]["consensus"][
                    "comparison"
                ],
                "consensus_decision": {
                    "reason": features.get("consensus_reason"),
                },
            }
        )
        fresh_rows.append(
            {
                "source_row_index": source_row_index,
                "fresh_evidence_decision_record": {
                    "action": features.get("fresh_action"),
                    "boundary_profile": features.get("fresh_boundary_profile")
                    or [],
                    "uncertainty": features.get("fresh_uncertainty"),
                },
                "decision_record": {
                    "final_label": row["fresh_evidence_label"],
                },
                "score_layers": {
                    "final": {
                        "comparison": row["score_layers"]["fresh_evidence"][
                            "comparison"
                        ]
                    }
                },
            }
        )
    return deterministic_rows, consensus_rows, fresh_rows


def _synthetic_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_risk_type: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    desired_misses = []
    current_rule_false_positives = []
    conservative_false_negatives = []
    safety_successes = []
    for row in rows:
        risk_type = row["synthetic_case"]["risk_type"]
        _accumulate_bucket(by_risk_type[risk_type], row)
        det_correct = _is_layer_correct(row, "deterministic")
        fresh_correct = _is_layer_correct(row, "fresh_evidence")
        selected_correct = _is_layer_correct(row, "selected")
        if row["desired_future_action_match"] is not True:
            desired_misses.append(row["synthetic_case"]["case_id"])
        if det_correct and not fresh_correct and not selected_correct:
            current_rule_false_positives.append(row["synthetic_case"]["case_id"])
        if not det_correct and fresh_correct and not selected_correct:
            conservative_false_negatives.append(row["synthetic_case"]["case_id"])
        if det_correct and not fresh_correct and selected_correct:
            safety_successes.append(row["synthetic_case"]["case_id"])
    return {
        "rows": len(rows),
        "selector_version": rows[0]["selector_version"],
        "actions": dict(Counter(str(row["selector_action"]) for row in rows)),
        "gates": dict(Counter(str(row["selector_gate"]) for row in rows)),
        "deterministic_purist_correct": sum(
            _is_layer_correct(row, "deterministic") for row in rows
        ),
        "consensus_purist_correct": sum(
            _is_layer_correct(row, "consensus") for row in rows
        ),
        "fresh_purist_correct": sum(
            _is_layer_correct(row, "fresh_evidence") for row in rows
        ),
        "selected_purist_correct": sum(
            _is_layer_correct(row, "selected") for row in rows
        ),
        "desired_future_action_matches": sum(
            row["desired_future_action_match"] is True for row in rows
        ),
        "desired_future_action_miss_case_ids": desired_misses,
        "current_rule_false_positive_case_ids": current_rule_false_positives,
        "conservative_false_negative_case_ids": conservative_false_negatives,
        "safety_success_case_ids": safety_successes,
        "by_risk_type": {
            key: dict(value) for key, value in sorted(by_risk_type.items())
        },
    }


def _accumulate_bucket(bucket: dict[str, int], row: dict[str, Any]) -> None:
    bucket["rows"] += 1
    bucket["deterministic_purist_correct"] += int(
        _is_layer_correct(row, "deterministic")
    )
    bucket["consensus_purist_correct"] += int(_is_layer_correct(row, "consensus"))
    bucket["fresh_purist_correct"] += int(_is_layer_correct(row, "fresh_evidence"))
    bucket["selected_purist_correct"] += int(_is_layer_correct(row, "selected"))
    bucket["desired_future_action_matches"] += int(
        row["desired_future_action_match"] is True
    )


def _is_layer_correct(row: dict[str, Any], layer: str) -> bool:
    return row["score_layers"][layer]["comparison"].get("purist_correct") is True


def _synthetic_markdown(payload: dict[str, Any]) -> str:
    stress = payload["stress_summary"]
    selector_summary = payload["selector_summary"]
    lines = [
        "# Gan 2026 Selector v0.6 Boundary-Profile Guard Synthetic Replay",
        "",
        "Date: 2026-06-15",
        "",
        "This is a no-call replay of v0.6 over the predeclared v0.5 "
        "boundary-rescue synthetic stress panel. It is not validation, "
        "holdout, benchmark, or model-performance evidence.",
        "",
        "## Summary",
        "",
        f"- Rows: {stress['rows']}",
        f"- Deterministic Purist: {stress['deterministic_purist_correct']}/{stress['rows']}",
        f"- Consensus Purist: {stress['consensus_purist_correct']}/{stress['rows']}",
        f"- Fresh Purist: {stress['fresh_purist_correct']}/{stress['rows']}",
        f"- Selected Purist: {stress['selected_purist_correct']}/{stress['rows']}",
        (
            "- Desired future action matches: "
            f"{stress['desired_future_action_matches']}/{stress['rows']}"
        ),
        (
            "- Current-rule false positives: "
            f"{len(stress['current_rule_false_positive_case_ids'])}"
        ),
        (
            "- Conservative false negatives: "
            f"{len(stress['conservative_false_negative_case_ids'])}"
        ),
        f"- Safety successes: {len(stress['safety_success_case_ids'])}",
        f"- Selector changed labels: {selector_summary['changed_labels']}",
        (
            "- Selector W->C / C->W: "
            f"{selector_summary['wrong_to_correct']} / "
            f"{selector_summary['correct_to_wrong']}"
        ),
        f"- Changed-label precision: {selector_summary['changed_label_precision']}",
        f"- Actions: `{stress['actions']}`",
        "",
        "## Risk-Type Summary",
        "",
        (
            "| Risk Type | Rows | Deterministic | Consensus | Fresh | Selected | "
            "Desired Matches |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for risk_type, info in stress["by_risk_type"].items():
        lines.append(
            f"| `{risk_type}` | {info['rows']} | "
            f"{info['deterministic_purist_correct']} | "
            f"{info['consensus_purist_correct']} | "
            f"{info['fresh_purist_correct']} | "
            f"{info['selected_purist_correct']} | "
            f"{info['desired_future_action_matches']} |"
        )
    lines.extend(
        [
            "",
            "## Case Readout",
            "",
            (
                "| Case | Risk | Action | Gate | Selected Correct | Desired Match |"
            ),
            "| --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for row in payload["rows"]:
        case = row["synthetic_case"]
        selected_correct = row["score_layers"]["selected"]["comparison"][
            "purist_correct"
        ]
        lines.append(
            f"| `{case['case_id']}` | `{case['risk_type']}` | "
            f"`{row['selector_action']}` | `{row['selector_gate']}` | "
            f"{selected_correct} | {row['desired_future_action_match']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The v0.6 profile guard blocks all three v0.5 hard-negative "
            "false positives while preserving the intended fresh boundary "
            "rescues and the v0.4 positive/negative controls. The remaining "
            "miss is the known conservative `unknown` origin count-plus-window "
            "case, which needs a separate evidence feature before relaxing.",
            "",
            "Decision: revise, not freeze. v0.6 is safer than v0.5 on the "
            "synthetic boundary panel while preserving the validation replay "
            "score, but it is still a saved-output development artifact.",
            "",
        ]
    )
    return "\n".join(lines)


def _register_validation(summary: dict[str, Any]) -> None:
    _upsert_entries(
        RunRegistryEntry(
            run_id=VALIDATION_RUN_ID,
            artifact_paths=(
                f"experiments/{VALIDATION_RUN_ID}.jsonl",
                f"experiments/{VALIDATION_RUN_ID}.md",
            ),
            date="2026-06-15",
            pipeline_family="consensus_fresh_agreement_selector",
            split="validation",
            row_count=summary["rows"],
            model="none",
            model_role=(
                "No-call replay of selector v0.6 over saved v0.5 validation "
                "selector rows reconstructed into component rows."
            ),
            mode="no-call replay",
            replay_status="saved_output_replay",
            repair_mode="selector_v0_6_profile_guard_boundary_rescue",
            cache_reuse_source=str(SOURCE_VALIDATION_JSONL),
            primary_metrics={
                "deterministic_purist_correct": summary[
                    "deterministic_purist_correct"
                ],
                "consensus_purist_correct": summary["consensus_purist_correct"],
                "fresh_evidence_purist_correct": summary[
                    "fresh_evidence_purist_correct"
                ],
                "selected_purist_correct": summary["selected_purist_correct"],
                "changed_labels": summary["changed_labels"],
                "wrong_to_correct": summary["wrong_to_correct"],
                "correct_to_wrong": summary["correct_to_wrong"],
                "changed_label_precision": summary["changed_label_precision"],
            },
            evidence_validity=(
                "Saved-output validation replay; gold labels are used only for "
                "post-hoc scoring. No holdout rows are read."
            ),
            decision="revise",
            supersedes=(VALIDATION_RUN_ID.replace("_v0_6_", "_v0_5_"),),
            claim_language_notes=(
                "v0.6 preserves the v0.5 validation score while adding a "
                "profile guard motivated by a synthetic hard-negative panel. "
                "Still validation-only and not holdout authorization."
            ),
        )
    )


def _register_synthetic(
    stress: dict[str, Any],
    selector_summary: dict[str, Any],
) -> None:
    _upsert_entries(
        RunRegistryEntry(
            run_id=SYNTHETIC_RUN_ID,
            artifact_paths=(
                f"experiments/{SYNTHETIC_RUN_ID}.json",
                f"experiments/{SYNTHETIC_RUN_ID}.md",
            ),
            date="2026-06-15",
            pipeline_family="consensus_fresh_agreement_selector_synthetic_boundary_stress",
            split="synthetic_boundary_rescue_probe",
            row_count=stress["rows"],
            model="none",
            model_role=(
                "Analysis-only synthetic replay over hand-specified v0.5 "
                "boundary-rescue stress cases; no model calls and no Gan rows "
                "are read."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="selector_v0_6_profile_guard_boundary_rescue",
            cache_reuse_source=str(SOURCE_SYNTHETIC_JSON),
            primary_metrics={
                "selected_purist_correct": stress["selected_purist_correct"],
                "desired_future_action_matches": stress[
                    "desired_future_action_matches"
                ],
                "current_rule_false_positive_count": len(
                    stress["current_rule_false_positive_case_ids"]
                ),
                "conservative_false_negative_count": len(
                    stress["conservative_false_negative_case_ids"]
                ),
                "wrong_to_correct": selector_summary["wrong_to_correct"],
                "correct_to_wrong": selector_summary["correct_to_wrong"],
                "changed_label_precision": selector_summary[
                    "changed_label_precision"
                ],
            },
            evidence_validity=(
                "Synthetic mechanism evidence only; no validation or holdout "
                "records are read."
            ),
            decision="revise",
            supersedes=(SYNTHETIC_RUN_ID.replace("_v0_6_", "_v0_5_"),),
            claim_language_notes=(
                "v0.6 blocks v0.5's synthetic hard-negative false positives "
                "and keeps intended positives. This supports revision but does "
                "not authorize a frozen holdout audit."
            ),
        )
    )


def _upsert_entries(new_entry: RunRegistryEntry) -> None:
    entries = [
        entry
        for entry in load_run_registry(REGISTRY_PATH)
        if entry.run_id != new_entry.run_id
    ]
    entries.append(new_entry)
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
