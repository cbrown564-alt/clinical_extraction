#!/usr/bin/env python3
"""Phase C select-keep arms for the Gan rules-only three-stage program.

Protocol: docs/research/gan2026/gan_rules_only_three_stage_protocol_2026-08-29.md
Development split only; test450 is never loaded; zero model calls.

Arms are named keep configurations. The baseline arm gates every
provisional class (Phase B behavior, select 669/750). Each keep arm
lets the named classes compete through the existing priority ladder.
Per arm the script records net Purist delta, rescued rows
(baseline-wrong, arm-correct) and regressed rows (baseline-correct,
arm-wrong). Protocol acceptance requires isolated-positive,
leave-one-out-negative, and zero regressions.

Usage: measure_gan_rules_only_select_keeps_dev750.py [arm ...]
Default: baseline plus each class kept alone.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.paper.gan_cell_replay import score_label
from clinical_extraction.paper.methods import gan_machine_split
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.recall_first import (  # noqa: E501
    ALL_PROVISIONAL_CLASSES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.three_stage import (  # noqa: E501
    EXCLUSIVE_TRIGGER_OVERRIDE,
    SINGLE_DATED_EVENT_OVERRIDE,
    GanThreeStageConfig,
    run_record_three_stage,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "experiments/gan2026_rules_only_three_stage_20260829/keep_arms"
BASELINE_SELECT_CORRECT = 669

SHORT = {name: name.removeprefix("provisional.") for name in ALL_PROVISIONAL_CLASSES}

Arm = tuple[frozenset[str], frozenset[str]]  # (kept_classes, select_overrides)

# Phase C candidate components. Bare keeps compete through the existing
# ladder; the two override components pair a keep with its named
# pre-ladder select rule.
COMPONENTS: dict[str, Arm] = {
    "keep_electrographic_hourly_rate": (
        frozenset({"provisional.electrographic_hourly_rate"}),
        frozenset(),
    ),
    "keep_nightly_narrative_rate": (
        frozenset({"provisional.nightly_narrative_rate"}),
        frozenset(),
    ),
    "keep_non_epileptic_current_free": (
        frozenset({"provisional.non_epileptic_current_free"}),
        frozenset(),
    ),
    "keep_vague_multiple_rate": (
        frozenset({"provisional.vague_multiple_rate"}),
        frozenset(),
    ),
    "keep_monthly_cluster_unclear_count": (
        frozenset({"provisional.monthly_cluster_unclear_count"}),
        frozenset(),
    ),
    "keep_exclusive_trigger_override": (
        frozenset({"provisional.trigger_conditioned_unknown"}),
        frozenset({EXCLUSIVE_TRIGGER_OVERRIDE}),
    ),
    "keep_single_dated_event_override": (
        frozenset({"provisional.single_dated_event_unknown"}),
        frozenset({SINGLE_DATED_EVENT_OVERRIDE}),
    ),
}


def _union(arms: list[Arm]) -> Arm:
    kept: frozenset[str] = frozenset()
    overrides: frozenset[str] = frozenset()
    for arm_kept, arm_overrides in arms:
        kept |= arm_kept
        overrides |= arm_overrides
    return kept, overrides


def build_arms() -> dict[str, Arm]:
    arms: dict[str, Arm] = {"baseline": (frozenset(), frozenset())}
    for name in sorted(ALL_PROVISIONAL_CLASSES):
        arms[f"keep_{SHORT[name]}"] = (frozenset({name}), frozenset())
    arms["keep_exclusive_trigger_override"] = COMPONENTS[
        "keep_exclusive_trigger_override"
    ]
    arms["keep_single_dated_event_override"] = COMPONENTS[
        "keep_single_dated_event_override"
    ]
    arms["phase_c_candidate"] = _union(list(COMPONENTS.values()))
    for component_name in COMPONENTS:
        rest = [
            arm for name, arm in COMPONENTS.items() if name != component_name
        ]
        arms[f"loo_{component_name}"] = _union(rest)
    return arms


def run_arm(records: list[Any], arm: Arm) -> dict[int, dict[str, Any]]:
    kept, overrides = arm
    config = GanThreeStageConfig(
        provisional_classes=ALL_PROVISIONAL_CLASSES,
        kept_classes=kept,
        select_overrides=overrides,
    )
    rows: dict[int, dict[str, Any]] = {}
    for record in records:
        result = run_record_three_stage(record, config)
        label = result.stops.select_label
        rows[record.source_row_index] = {
            "label": label,
            "purist_correct": bool(score_label(record, label)["purist_correct"]),
            "evidence": result.final_selection.evidence,
        }
    return rows


def main() -> None:
    records = sorted(
        load_records_for_split(gan_machine_split("dev750")),
        key=lambda record: record.source_row_index,
    )
    if len(records) != 750:
        raise RuntimeError(f"expected 750 development records, found {len(records)}")

    all_arms = build_arms()
    requested = sys.argv[1:] or list(all_arms)
    unknown = [name for name in requested if name not in all_arms]
    if unknown:
        raise SystemExit(f"unknown arms: {unknown}; known: {list(all_arms)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    baseline_rows = run_arm(records, all_arms["baseline"])
    baseline_correct = sum(
        row["purist_correct"] for row in baseline_rows.values()
    )
    if baseline_correct != BASELINE_SELECT_CORRECT:
        raise RuntimeError(
            f"baseline select {baseline_correct}/750 does not reproduce "
            f"{BASELINE_SELECT_CORRECT}/750"
        )

    for arm_name in requested:
        if arm_name == "baseline":
            arm_rows = baseline_rows
        else:
            arm_rows = run_arm(records, all_arms[arm_name])
        correct = sum(row["purist_correct"] for row in arm_rows.values())
        rescued = sorted(
            index
            for index, row in arm_rows.items()
            if row["purist_correct"] and not baseline_rows[index]["purist_correct"]
        )
        regressed = sorted(
            index
            for index, row in arm_rows.items()
            if not row["purist_correct"] and baseline_rows[index]["purist_correct"]
        )
        changed = sorted(
            index
            for index, row in arm_rows.items()
            if row["label"] != baseline_rows[index]["label"]
        )
        summary = {
            "schema_version": "gan.rules_only.select_keeps.dev750.v1",
            "date": datetime.now(UTC).date().isoformat(),
            "protocol": (
                "docs/research/gan2026/"
                "gan_rules_only_three_stage_protocol_2026-08-29.md"
            ),
            "split": "dev750",
            "holdout_loaded": False,
            "model_calls": 0,
            "scorer": "purist",
            "arm": arm_name,
            "kept_classes": sorted(all_arms[arm_name][0]),
            "select_overrides": sorted(all_arms[arm_name][1]),
            "select_purist_correct": correct,
            "select_purist_accuracy": round(correct / 750, 4),
            "net_vs_baseline": correct - baseline_correct,
            "rescued_rows": rescued,
            "regressed_rows": regressed,
            "changed_rows": changed,
            "zero_regressions": not regressed,
            "row_policy": "development_review_permitted",
        }
        path = OUT_DIR / f"{arm_name}.json"
        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(
            f"{arm_name}: {correct}/750 (net {correct - baseline_correct:+d}), "
            f"rescued {len(rescued)}, regressed {len(regressed)}, "
            f"changed {len(changed)}"
        )
        if regressed:
            print(f"    regressed rows: {regressed}")


if __name__ == "__main__":
    main()
