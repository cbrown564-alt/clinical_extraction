#!/usr/bin/env python3
"""Phase B recall-first ceiling measurement for the Gan rules-only program.

Protocol: docs/research/gan2026/gan_rules_only_three_stage_protocol_2026-08-29.md
Development split only; test450 is never loaded; zero model calls.

Gate B: with every provisional producer class enabled, the select stop is
label- and evidence-identical to ``run_record`` on all 750 development
records and the competition pool is unchanged (the Select gate drops all
provisional candidates). The ceiling read is the wide-ledger oracle with
provisional candidates versus the Phase A wide oracle, plus per-class
attribution of newly reachable rows.
"""

from __future__ import annotations

import json
from collections import Counter
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
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    rules as gan_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.three_stage import (  # noqa: E501
    GanThreeStageConfig,
    run_record_three_stage,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "experiments/gan2026_rules_only_three_stage_20260829"
EXPECTED_SELECT_CORRECT = 669
STOPS = ("find", "encode", "select")


def main() -> None:
    records = sorted(
        load_records_for_split(gan_machine_split("dev750")),
        key=lambda record: record.source_row_index,
    )
    if len(records) != 750:
        raise RuntimeError(f"expected 750 development records, found {len(records)}")

    comparator_config = PipelineConfiguration(architecture="rules")
    config = GanThreeStageConfig(provisional_classes=ALL_PROVISIONAL_CLASSES)

    rows: list[dict[str, Any]] = []
    stop_correct = {stop: 0 for stop in STOPS}
    select_correct_count = 0
    oracle_wide_baseline = 0
    oracle_wide_with_provisional = 0
    produced_counts: Counter[str] = Counter()
    rescue_rows: dict[str, list[int]] = {name: [] for name in ALL_PROVISIONAL_CLASSES}
    unique_rescue_rows: dict[str, list[int]] = {
        name: [] for name in ALL_PROVISIONAL_CLASSES
    }
    rescued_recall_gap_rows: list[int] = []

    for record in records:
        comparator = gan_rules.run_record(record, comparator_config)
        candidate = run_record_three_stage(record, config)

        if candidate.stops.select_label != comparator.output.final_value:
            raise RuntimeError(
                "gate B failed: select label diverges on "
                f"source_row_index={record.source_row_index}"
            )
        if candidate.final_selection.evidence != comparator.output.evidence:
            raise RuntimeError(
                "gate B failed: select evidence diverges on "
                f"source_row_index={record.source_row_index}"
            )
        comparator_pool = [
            (event["kind"], event["raw_value"], event["evidence"])
            for event in comparator.diagnostics["candidate_events"]
        ]
        candidate_pool = [
            (str(entry.kind.value), entry.raw_label, entry.evidence)
            for entry in candidate.ledger
            if entry.drop_reason is None
        ]
        if candidate_pool != comparator_pool:
            raise RuntimeError(
                "gate B failed: competition pool diverges on "
                f"source_row_index={record.source_row_index}"
            )

        stop_labels = {
            "find": candidate.stops.find_label,
            "encode": candidate.stops.encode_label,
            "select": candidate.stops.select_label,
        }
        stop_scores = {
            stop: score_label(record, stop_labels[stop]) for stop in STOPS
        }
        for stop in STOPS:
            stop_correct[stop] += int(stop_scores[stop]["purist_correct"])
        select_correct = bool(stop_scores["select"]["purist_correct"])
        select_correct_count += int(select_correct)

        baseline_reachable = any(
            score_label(record, entry.normalized_label)["purist_correct"]
            for entry in candidate.ledger
            if entry.provisional_class is None
        )
        correct_classes = sorted(
            {
                entry.provisional_class
                for entry in candidate.ledger
                if entry.provisional_class is not None
                and score_label(record, entry.normalized_label)["purist_correct"]
            }
        )
        oracle_wide_baseline += int(baseline_reachable)
        oracle_wide_with_provisional += int(
            baseline_reachable or bool(correct_classes)
        )

        for entry in candidate.ledger:
            if entry.provisional_class is not None:
                produced_counts[entry.provisional_class] += 1
        if not baseline_reachable and correct_classes:
            for name in correct_classes:
                rescue_rows[name].append(record.source_row_index)
            if len(correct_classes) == 1:
                unique_rescue_rows[correct_classes[0]].append(
                    record.source_row_index
                )
            if not select_correct:
                rescued_recall_gap_rows.append(record.source_row_index)

        rows.append(
            {
                "source_row_index": record.source_row_index,
                "gold_label": record.gold_label,
                "stops": {
                    stop: {
                        "label": stop_labels[stop],
                        "purist_correct": stop_scores[stop]["purist_correct"],
                    }
                    for stop in STOPS
                },
                "baseline_reachable": baseline_reachable,
                "provisional_correct_classes": correct_classes,
                "provisional_entries": [
                    {
                        "class": entry.provisional_class,
                        "normalized_label": entry.normalized_label,
                        "evidence": entry.evidence,
                    }
                    for entry in candidate.ledger
                    if entry.provisional_class is not None
                ],
            }
        )

    if select_correct_count != EXPECTED_SELECT_CORRECT:
        raise RuntimeError(
            f"select stop {select_correct_count}/750 does not reproduce the "
            f"cited rung {EXPECTED_SELECT_CORRECT}/750"
        )

    n = len(records)
    summary = {
        "schema_version": "gan.rules_only.recall_first.dev750.v1",
        "date": datetime.now(UTC).date().isoformat(),
        "protocol": (
            "docs/research/gan2026/gan_rules_only_three_stage_protocol_2026-08-29.md"
        ),
        "split": "dev750",
        "holdout_loaded": False,
        "model_calls": 0,
        "scorer": "purist",
        "program": (
            "run_record_three_stage(GanThreeStageConfig("
            "provisional_classes=ALL_PROVISIONAL_CLASSES))"
        ),
        "gates": {
            "select_identical_to_run_record": True,
            "pool_identical_to_comparator": True,
            "select_stop_reproduces_cited_rung": EXPECTED_SELECT_CORRECT,
        },
        "stage_stops": {
            stop: {
                "purist_correct": stop_correct[stop],
                "purist_accuracy": round(stop_correct[stop] / n, 4),
            }
            for stop in STOPS
        },
        "oracle": {
            "wide_baseline_correct": oracle_wide_baseline,
            "wide_baseline_ceiling": round(oracle_wide_baseline / n, 4),
            "wide_with_provisional_correct": oracle_wide_with_provisional,
            "wide_with_provisional_ceiling": round(
                oracle_wide_with_provisional / n, 4
            ),
            "ceiling_gain_rows": oracle_wide_with_provisional
            - oracle_wide_baseline,
        },
        "per_class": {
            name: {
                "candidates_produced": produced_counts.get(name, 0),
                "rescue_rows": rescue_rows[name],
                "unique_rescue_rows": unique_rescue_rows[name],
            }
            for name in sorted(ALL_PROVISIONAL_CLASSES)
        },
        "rescued_recall_gap_rows": rescued_recall_gap_rows,
        "row_policy": "development_review_permitted",
        "claim_boundary": (
            "Development ceiling evidence only. Provisional candidates are "
            "gated out of competition; the select stop and the cited "
            "five-cell rows are unchanged. Keeps are a Phase C decision."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUT_DIR / "dev750_recall_first_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    rows_path = OUT_DIR / "dev750_recall_first_rows.jsonl"
    rows_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    print(summary_path)
    for stop in STOPS:
        stats = summary["stage_stops"][stop]
        print(
            f"{stop}: purist {stats['purist_correct']}/750 "
            f"({stats['purist_accuracy']:.4f})"
        )
    oracle = summary["oracle"]
    print(
        f"wide oracle: baseline {oracle['wide_baseline_correct']}/750 -> "
        f"with provisional {oracle['wide_with_provisional_correct']}/750 "
        f"(+{oracle['ceiling_gain_rows']})"
    )
    for name in sorted(ALL_PROVISIONAL_CLASSES):
        stats = summary["per_class"][name]
        print(
            f"{name}: produced {stats['candidates_produced']}, "
            f"rescues {len(stats['rescue_rows'])} "
            f"(unique {len(stats['unique_rescue_rows'])})"
        )


if __name__ == "__main__":
    main()
