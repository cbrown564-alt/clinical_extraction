"""Decisive component-generation audit: does live ambiguity-aware fresh
evidence move the selector oracle ceiling above 739/750?

This reads the live v0.7 + safety-v0.9 fresh-evidence generation over the
predeclared 22-row validation hard slice (the 17 selector-v0.9 selected-wrong
rows plus the five supervisor ambiguity rows not already present) and compares
the *new* fresh component against the prior component availability recorded in
the v0.9 residual component-generation audit.

The single decisive question (Insight 2 of the unknown-frequency pathways doc):
selection is saturated, so the only way to lift the holdout target is to make a
*correct component exist* on rows where none did. Concretely, of the 11 rows
where no deterministic/consensus/fresh-v0.4 component was Purist-correct, how
many does live ambiguity-aware fresh generation now get correct?

Validation-only. No locked test rows are read. The model calls were already made
by the slice run; this script only scores saved outputs against gold.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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

SLICE_JSONL = (
    EXPERIMENTS / "gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_7_safety_v0_9_"
    "2026-06-15.jsonl"
)
RESIDUAL_AUDIT_JSON = (
    EXPERIMENTS / "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "residual_component_generation_audit_2026-06-15.json"
)

RUN_ID = "gan2026_ambiguity_live_component_generation_audit_v0_7_2026-06-15"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"

# Prior selector oracle ceiling and the selected-correct floor it builds on, from
# the v0.9 residual audit (733 selected-correct + 6 recoverable = 739).
PRIOR_SELECTED_CORRECT = 733
PRIOR_ORACLE_CEILING = 739
VALIDATION_ROWS = 750

# Supervisor ambiguity panel: source_row_index -> (expected label, expected class).
SUPERVISOR_PANEL = {
    11272: ("unknown", "last_event_only_unknown"),
    14454: ("2 per 2 month", "explicit_count_window"),
    14029: ("unknown", "unknown_count_or_window"),
    13267: ("2 per 5 month", "explicit_count_window"),
    14137: ("unknown", "unknown_count_or_window"),
    11337: ("unknown", "unknown_count_or_window"),
}


def main() -> None:
    slice_rows = _load_slice_rows(SLICE_JSONL)
    residual = _load_residual_records(RESIDUAL_AUDIT_JSON)
    summary = _audit(slice_rows, residual)
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Decisive validation-only audit: does live v0.7 + safety-v0.9 "
            "ambiguity-aware fresh-evidence generation produce a Purist-correct "
            "component on rows where none existed, lifting the selector oracle "
            "ceiling above 739/750?"
        ),
        "slice_artifact": str(SLICE_JSONL),
        "prior_residual_audit": str(RESIDUAL_AUDIT_JSON),
        "summary": summary,
    }
    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(summary)
    print(json.dumps(summary["headline"], indent=2, sort_keys=True))


def _load_slice_rows(path: Path) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        rows[int(row["source_row_index"])] = row
    return rows


def _load_residual_records(path: Path) -> dict[int, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        int(record["source_row_index"]): record
        for record in payload["summary"]["selected_wrong_records"]
    }


def _new_fresh_correct(slice_row: dict[str, Any]) -> bool:
    return bool(slice_row["score_layers"]["final"]["comparison"].get("purist_correct") is True)


def _new_fresh_view(slice_row: dict[str, Any]) -> dict[str, Any]:
    decision = slice_row.get("fresh_evidence_decision_record") or {}
    final = slice_row["score_layers"]["final"]
    return {
        "new_fresh_label": final.get("final_label"),
        "new_fresh_purist_correct": _new_fresh_correct(slice_row),
        "ambiguity_classification": decision.get("ambiguity_classification"),
        "action": decision.get("action"),
        "gate_fallback": [
            event
            for event in slice_row.get("action_render_events") or []
            if "gate_fallback" in str(event)
        ],
    }


def _audit(
    slice_rows: dict[int, dict[str, Any]],
    residual: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    no_correct_rows: list[dict[str, Any]] = []
    recoverable_rows: list[dict[str, Any]] = []
    residual_with_correct_component_now = 0

    for index, record in residual.items():
        slice_row = slice_rows[index]
        view = _new_fresh_view(slice_row)
        det_correct = "deterministic" in record["correct_components"]
        cons_correct = "consensus" in record["correct_components"]
        prior_fresh_correct = "fresh_evidence" in record["correct_components"]
        any_correct_now = det_correct or cons_correct or view["new_fresh_purist_correct"]
        if any_correct_now:
            residual_with_correct_component_now += 1
        entry = {
            "source_row_index": index,
            "gold_label": record["gold_label"],
            "gold_band": record["gold_band"],
            "deterministic_label": record["deterministic_label"],
            "consensus_label": record["consensus_label"],
            "fresh_v04_label": record["fresh_evidence_label"],
            "prior_fresh_correct": prior_fresh_correct,
            "audit_categories": record["audit_categories"],
            **view,
        }
        if not record["correct_components"]:
            no_correct_rows.append(entry)
        else:
            recoverable_rows.append(entry)

    no_correct_fixed = sum(1 for entry in no_correct_rows if entry["new_fresh_purist_correct"])
    recoverable_preserved = sum(
        1 for entry in recoverable_rows if entry["new_fresh_purist_correct"]
    )
    recoverable_fresh_regressions = [
        entry["source_row_index"]
        for entry in recoverable_rows
        if entry["prior_fresh_correct"] and not entry["new_fresh_purist_correct"]
    ]

    new_oracle_ceiling = PRIOR_SELECTED_CORRECT + residual_with_correct_component_now
    panel = _supervisor_panel(slice_rows)

    return {
        "headline": {
            "no_correct_rows": len(no_correct_rows),
            "no_correct_rows_fixed_by_live_fresh": no_correct_fixed,
            "prior_oracle_ceiling": PRIOR_ORACLE_CEILING,
            "new_oracle_ceiling": new_oracle_ceiling,
            "oracle_ceiling_delta": new_oracle_ceiling - PRIOR_ORACLE_CEILING,
            "supervisor_panel_pass": panel["passed"],
            "supervisor_panel_total": panel["total"],
        },
        "recoverable_rows_count": len(recoverable_rows),
        "recoverable_rows_fresh_preserved": recoverable_preserved,
        "recoverable_fresh_regressions": recoverable_fresh_regressions,
        "residual_rows_with_correct_component_now": residual_with_correct_component_now,
        "no_correct_rows": sorted(no_correct_rows, key=lambda e: e["source_row_index"]),
        "recoverable_rows": sorted(recoverable_rows, key=lambda e: e["source_row_index"]),
        "supervisor_panel": panel,
    }


def _supervisor_panel(slice_rows: dict[int, dict[str, Any]]) -> dict[str, Any]:
    cases = []
    passed = 0
    for index, (expected_label, expected_class) in SUPERVISOR_PANEL.items():
        slice_row = slice_rows[index]
        view = _new_fresh_view(slice_row)
        label_correct = bool(view["new_fresh_purist_correct"])
        if label_correct:
            passed += 1
        cases.append(
            {
                "source_row_index": index,
                "expected_label": expected_label,
                "expected_class": expected_class,
                "new_fresh_label": view["new_fresh_label"],
                "new_ambiguity_classification": view["ambiguity_classification"],
                "label_purist_correct": label_correct,
                "class_matches_expected": (view["ambiguity_classification"] == expected_class),
            }
        )
    return {
        "total": len(SUPERVISOR_PANEL),
        "passed": passed,
        "cases": sorted(cases, key=lambda c: c["source_row_index"]),
    }


def _yn(value: bool) -> str:
    return "yes" if value else "no"


def _markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    head = summary["headline"]
    lines = [
        "# Gan 2026 Ambiguity-Aware Live Component-Generation Audit",
        "",
        "Date: 2026-06-15",
        "",
        "This is the decisive validation-only experiment from the unknown-frequency "
        "agentic pathways doc. It scores live `v0.7` + safety-`v0.9` ambiguity-aware "
        "fresh-evidence generation over the predeclared 22-row validation hard slice "
        "against gold and the prior component availability. It reads no locked test "
        "rows; the model calls were made on the validation split.",
        "",
        "## Decisive Result",
        "",
        (
            "The selector line is saturated: an oracle over the current "
            "deterministic/consensus/fresh-v0.4 components topped out at "
            f"{head['prior_oracle_ceiling']}/{VALIDATION_ROWS}, with "
            f"{head['no_correct_rows']} validation rows having no Purist-correct "
            "component at all. The only way to lift the holdout target is to make a "
            "correct component *exist* on those rows."
        ),
        "",
        (
            f"- No-correct rows fixed by live ambiguity-aware fresh generation: "
            f"**{head['no_correct_rows_fixed_by_live_fresh']}/"
            f"{head['no_correct_rows']}**"
        ),
        (
            f"- Selector oracle ceiling: {head['prior_oracle_ceiling']}/"
            f"{VALIDATION_ROWS} -> **{head['new_oracle_ceiling']}/"
            f"{VALIDATION_ROWS}** (delta {head['oracle_ceiling_delta']:+d})"
        ),
        (
            f"- Recoverable rows fresh component preserved: "
            f"{summary['recoverable_rows_fresh_preserved']}/"
            f"{summary['recoverable_rows_count']} "
            f"(regressions: {summary['recoverable_fresh_regressions'] or 'none'})"
        ),
        (
            f"- Supervisor ambiguity panel (live): "
            f"{head['supervisor_panel_pass']}/{head['supervisor_panel_total']} "
            "labels Purist-correct"
        ),
        "",
        "## No-Correct Rows (the rows that gate the ceiling)",
        "",
        "These 11 rows had no Purist-correct deterministic, consensus, or "
        "fresh-v0.4 component. Deterministic and consensus are unchanged, so the "
        "ceiling moves only where live fresh generation is newly correct.",
        "",
        "| Row | Band | Gold | Det/Consensus | Fresh v0.4 | Fresh v0.7 (live) | Ambiguity class | Now correct |",
        "| ---: | --- | --- | --- | --- | --- | --- | :---: |",
    ]
    for entry in summary["no_correct_rows"]:
        lines.append(
            f"| {entry['source_row_index']} "
            f"| `{entry['gold_band']}` "
            f"| `{entry['gold_label']}` "
            f"| `{entry['deterministic_label']}` "
            f"| `{entry['fresh_v04_label']}` "
            f"| `{entry['new_fresh_label']}` "
            f"| `{entry['ambiguity_classification']}` "
            f"| {_yn(entry['new_fresh_purist_correct'])} |"
        )
    lines.extend(
        [
            "",
            "## Recoverable Rows (regression guard)",
            "",
            "These rows already had a correct component at v0.4 (mostly "
            "fresh-only). Live regeneration must not destroy them.",
            "",
            "| Row | Band | Gold | Fresh v0.4 | Fresh v0.7 (live) | Prior fresh correct | Now correct |",
            "| ---: | --- | --- | --- | --- | :---: | :---: |",
        ]
    )
    for entry in summary["recoverable_rows"]:
        lines.append(
            f"| {entry['source_row_index']} "
            f"| `{entry['gold_band']}` "
            f"| `{entry['gold_label']}` "
            f"| `{entry['fresh_v04_label']}` "
            f"| `{entry['new_fresh_label']}` "
            f"| {_yn(entry['prior_fresh_correct'])} "
            f"| {_yn(entry['new_fresh_purist_correct'])} |"
        )
    lines.extend(
        [
            "",
            "## Supervisor Ambiguity Panel (live)",
            "",
            "The six supervisor-discussed rows, now scored on live generation "
            "rather than the parser/safety-gate contract. This is the precision "
            "check: the explicit count-window cases (`14454`, `13267`) must stay "
            "frequencies while the ambiguous cases collapse to `unknown`.",
            "",
            "| Row | Expected | Live label | Expected class | Live class | Label ok | Class match |",
            "| ---: | --- | --- | --- | --- | :---: | :---: |",
        ]
    )
    for case in summary["supervisor_panel"]["cases"]:
        lines.append(
            f"| {case['source_row_index']} "
            f"| `{case['expected_label']}` "
            f"| `{case['new_fresh_label']}` "
            f"| `{case['expected_class']}` "
            f"| `{case['new_ambiguity_classification']}` "
            f"| {_yn(case['label_purist_correct'])} "
            f"| {_yn(case['class_matches_expected'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            _interpretation(summary),
            "",
        ]
    )
    return "\n".join(lines)


def _interpretation(summary: dict[str, Any]) -> str:
    head = summary["headline"]
    delta = head["oracle_ceiling_delta"]
    fixed = head["no_correct_rows_fixed_by_live_fresh"]
    total = head["no_correct_rows"]
    regressions = summary["recoverable_fresh_regressions"]
    parts = [
        (
            f"Live ambiguity-aware fresh generation made a correct component exist "
            f"on {fixed} of {total} previously no-correct rows, moving the selector "
            f"oracle ceiling {delta:+d} to {head['new_oracle_ceiling']}/"
            f"{VALIDATION_ROWS}."
        )
    ]
    if delta > 0:
        parts.append(
            "This is the first result in the line to lift the ceiling rather than "
            "reshuffle existing components: it attacks the correlated-failure "
            "bottleneck (Insight 2) directly. The component pool, not just the "
            "selector, has improved. The next step is a wider validation replay of "
            "the regenerated fresh component through the frozen selector, then a "
            "held-out-family CV check, before any holdout protocol."
        )
    else:
        parts.append(
            "The ceiling did not move: even with the explicit ambiguity contract, "
            "live fresh generation reproduces the same over-reading on the hard "
            "rows. This confirms the line has converged on the component-generation "
            "wall and that the next bet must change the evidence the model sees, "
            "not the decision contract layered on top."
        )
    if regressions:
        parts.append(
            "Caveat: live regeneration regressed previously-correct fresh rows "
            f"{regressions}; a wider replay must confirm net ceiling movement, not "
            "a local trade."
        )
    return " ".join(parts)


def _register(summary: dict[str, Any]) -> None:
    head = summary["headline"]
    entries = [entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
                f"experiments/{SLICE_JSONL.name}",
            ),
            date="2026-06-15",
            pipeline_family="fresh_evidence_reasoner_ambiguity_component_generation",
            split="validation",
            row_count=22,
            model="openai/gpt-4.1",
            model_role=(
                "Live v0.7 + safety-v0.9 ambiguity-aware fresh-evidence generation "
                "over a predeclared 22-row validation hard slice. Scored against "
                "gold for component availability; no holdout rows are read."
            ),
            mode="live",
            replay_status="live",
            repair_mode="ambiguity_classification_component_generation",
            cache_reuse_source=str(SLICE_JSONL),
            primary_metrics={
                "no_correct_rows": head["no_correct_rows"],
                "no_correct_rows_fixed_by_live_fresh": (
                    head["no_correct_rows_fixed_by_live_fresh"]
                ),
                "prior_oracle_ceiling": head["prior_oracle_ceiling"],
                "new_oracle_ceiling": head["new_oracle_ceiling"],
                "oracle_ceiling_delta": head["oracle_ceiling_delta"],
                "recoverable_rows_fresh_preserved": (summary["recoverable_rows_fresh_preserved"]),
                "supervisor_panel_pass": head["supervisor_panel_pass"],
            },
            evidence_validity=(
                "Validation-only live generation. Gold labels are used post-hoc "
                "for component availability and the supervisor panel; no locked "
                "test rows are read and no scorer policy changes."
            ),
            decision="revise",
            supersedes=("gan2026_ambiguity_live_component_generation_audit_2026-06-15",),
            claim_language_notes=(
                "Measures whether the ambiguity contract lifts the component "
                "oracle ceiling on the predeclared residual slice. Not a "
                "holdout-facing candidate; a wider validation replay and "
                "held-out-family CV are required before any freeze."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
