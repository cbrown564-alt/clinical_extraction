#!/usr/bin/env python3
"""Phase A gates and stage stops for the Gan rules-only three-stage program.

Protocol: docs/research/gan2026/gan_rules_only_three_stage_protocol_2026-08-29.md
Development split only; test450 is never loaded; zero model calls.

Gate A1: three-stage select label AND evidence identical to run_record on
every dev750 record, and the select count reproduces the cited rung
(669/750). Gate A2: the surviving competition pool is identical to the
comparator's post-prune candidate list on every record. Stops are read
only after both gates hold.
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
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    rules as gan_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.three_stage import (
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
    rows: list[dict[str, Any]] = []
    stop_correct = {stop: 0 for stop in STOPS}
    stop_pragmatic = {stop: 0 for stop in STOPS}
    stop_scorable = {stop: 0 for stop in STOPS}
    oracle_pool_correct = 0
    oracle_wide_correct = 0
    drop_counts: Counter[str] = Counter()
    exclusion_counts: Counter[str] = Counter()
    residual = Counter()

    for record in records:
        comparator = gan_rules.run_record(record, comparator_config)
        candidate = run_record_three_stage(record)

        if candidate.stops.select_label != comparator.output.final_value:
            raise RuntimeError(
                "gate A1 failed: select label diverges on "
                f"source_row_index={record.source_row_index}"
            )
        if candidate.final_selection.evidence != comparator.output.evidence:
            raise RuntimeError(
                "gate A1 failed: select evidence diverges on "
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
                "gate A2 failed: competition pool diverges on "
                f"source_row_index={record.source_row_index}"
            )

        stop_labels = {
            "find": candidate.stops.find_label,
            "encode": candidate.stops.encode_label,
            "select": candidate.stops.select_label,
        }
        row: dict[str, Any] = {
            "source_row_index": record.source_row_index,
            "gold_label": record.gold_label,
            "stops": {},
            "find_pick_ledger_index": candidate.stops.find_pick_ledger_index,
            "ledger_size": len(candidate.ledger),
            "drop_reasons": [
                str(entry.drop_reason.value)
                for entry in candidate.ledger
                if entry.drop_reason is not None
            ],
            "exclusion_rule_ids": [
                exclusion.rule_id for exclusion in candidate.exclusions
            ],
        }
        for stop in STOPS:
            scored = score_label(record, stop_labels[stop])
            stop_correct[stop] += int(scored["purist_correct"])
            stop_pragmatic[stop] += int(scored["pragmatic_correct"])
            stop_scorable[stop] += int(scored["scorable"])
            row["stops"][stop] = {
                "label": stop_labels[stop],
                "purist_correct": scored["purist_correct"],
                "pragmatic_correct": scored["pragmatic_correct"],
                "scorable": scored["scorable"],
            }

        pool_oracle = any(
            score_label(record, entry.normalized_label)["purist_correct"]
            for entry in candidate.ledger
            if entry.drop_reason is None
        )
        wide_oracle = pool_oracle or any(
            score_label(record, entry.normalized_label)["purist_correct"]
            for entry in candidate.ledger
            if entry.drop_reason is not None
        )
        oracle_pool_correct += int(pool_oracle)
        oracle_wide_correct += int(wide_oracle)
        row["oracle_pool_correct"] = pool_oracle
        row["oracle_wide_correct"] = wide_oracle

        select_correct = bool(row["stops"]["select"]["purist_correct"])
        if not select_correct:
            residual["select_headroom" if pool_oracle else "recall_gap"] += 1
        for entry in candidate.ledger:
            if entry.drop_reason is not None:
                drop_counts[str(entry.drop_reason.value)] += 1
        for exclusion in candidate.exclusions:
            exclusion_counts[exclusion.rule_id] += 1
        rows.append(row)

    if stop_correct["select"] != EXPECTED_SELECT_CORRECT:
        raise RuntimeError(
            f"select stop {stop_correct['select']}/750 does not reproduce the "
            f"cited rung {EXPECTED_SELECT_CORRECT}/750"
        )

    n = len(records)
    summary = {
        "schema_version": "gan.rules_only.three_stage.dev750.v1",
        "date": datetime.now(UTC).date().isoformat(),
        "protocol": (
            "docs/research/gan2026/gan_rules_only_three_stage_protocol_2026-08-29.md"
        ),
        "split": "dev750",
        "holdout_loaded": False,
        "model_calls": 0,
        "scorer": "purist (pragmatic secondary)",
        "program": "run_record_three_stage(GanThreeStageConfig())",
        "stop_policy": (
            "find/encode = document-order-first pick over the wide "
            "pre-drop ledger (raw label / normalized label); select = "
            "submitted final label"
        ),
        "gates": {
            "a1_select_identical_to_run_record": True,
            "a2_pool_identical_to_comparator": True,
            "select_stop_reproduces_cited_rung": EXPECTED_SELECT_CORRECT,
        },
        "stage_stops": {
            stop: {
                "purist_correct": stop_correct[stop],
                "purist_accuracy": round(stop_correct[stop] / n, 4),
                "pragmatic_correct": stop_pragmatic[stop],
                "pragmatic_accuracy": round(stop_pragmatic[stop] / n, 4),
                "scorable": stop_scorable[stop],
            }
            for stop in STOPS
        },
        "oracle": {
            "pool_correct": oracle_pool_correct,
            "pool_ceiling": round(oracle_pool_correct / n, 4),
            "wide_correct": oracle_wide_correct,
            "wide_ceiling": round(oracle_wide_correct / n, 4),
        },
        "residual_partition": dict(residual),
        "drop_counts": dict(drop_counts),
        "exclusion_counts": dict(exclusion_counts),
        "row_policy": "development_review_permitted",
        "claim_boundary": (
            "Score-neutral stage instrumentation of the living rules program. "
            "Development evidence only; cited five-cell rows are unchanged."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUT_DIR / "dev750_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    rows_path = OUT_DIR / "dev750_rows.jsonl"
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
    print(
        f"oracle pool {oracle_pool_correct}/750 "
        f"({summary['oracle']['pool_ceiling']:.4f}); "
        f"wide {oracle_wide_correct}/750 "
        f"({summary['oracle']['wide_ceiling']:.4f})"
    )
    print(f"residual partition: {dict(residual)}")
    print(f"drops: {dict(drop_counts)}")


if __name__ == "__main__":
    main()
