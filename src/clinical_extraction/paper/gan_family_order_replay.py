"""Replay adjacent semantic-family swaps on saved Gan hybrid raw output."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.gan_rung_replay import score_label
from clinical_extraction.paper.methods import gan_machine_split
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    DEFAULT_SEMANTIC_FAMILY_ORDER,
    StructuredRepairConfig,
    adjacent_semantic_family_orders,
    parse_structured_json_with_trace,
)

ROOT = discover_repo_root(start=Path(__file__))

CELLS: tuple[tuple[str, Path], ...] = (
    (
        "grok46_hybrid",
        ROOT / "paper_experiments/gan/gan_llm_with_rules/grok46/dev750/rows.jsonl",
    ),
    (
        "gpt56luna_hybrid",
        ROOT / "paper_experiments/gan/gan_llm_with_rules/gpt56luna/dev750/rows.jsonl",
    ),
    (
        "gpt56luna_pre_post",
        ROOT / "experiments/paper/gan_llm_pre_post/gpt56luna/dev750/rows.jsonl",
    ),
)


def _label_for_order(
    raw_output: str,
    note_text: str,
    order: tuple[str, ...],
) -> str | None:
    extraction, _, _, _trace = parse_structured_json_with_trace(
        raw_output,
        note_text=note_text,
        repair_config=StructuredRepairConfig(
            repair_mode="llm_select",
            semantic_family_order=order,
        ),
    )
    if extraction is None:
        return None
    return extraction.selection.final_label


def replay_adjacent_swaps(split: str = "dev750") -> dict[str, Any]:
    """Score the default order and each adjacent swap. Development only."""

    if split != "dev750":
        raise ValueError("family-order replay is development-only")
    records = {
        record.source_row_index: record
        for record in load_records_for_split(gan_machine_split(split))
    }
    conditions: list[tuple[str, tuple[str, ...]]] = [
        ("default", DEFAULT_SEMANTIC_FAMILY_ORDER),
        *[
            (f"swap:{pair[0]}|{pair[1]}", order)
            for pair, order in adjacent_semantic_family_orders()
        ],
    ]

    cell_results: dict[str, Any] = {}
    for cell_id, path in CELLS:
        if not path.is_file():
            cell_results[cell_id] = {"missing": str(path)}
            continue
        raw_rows = {
            int(row["source_row_index"]): str(row["raw_output"])
            for row in load_jsonl_rows(path)
        }
        baseline_ok: dict[int, bool] = {}
        baseline_label: dict[int, str | None] = {}
        for index, raw in raw_rows.items():
            record = records[index]
            label = _label_for_order(raw, record.note_text, DEFAULT_SEMANTIC_FAMILY_ORDER)
            scored = score_label(record, label)
            baseline_ok[index] = bool(scored["purist_correct"])
            baseline_label[index] = scored["predicted_label"]
        baseline_correct = sum(baseline_ok.values())
        swaps: list[dict[str, Any]] = []
        for name, order in conditions:
            if name == "default":
                continue
            help_rows: list[dict[str, Any]] = []
            harm_rows: list[dict[str, Any]] = []
            for index, raw in raw_rows.items():
                record = records[index]
                label = _label_for_order(raw, record.note_text, order)
                scored = score_label(record, label)
                ok = bool(scored["purist_correct"])
                if ok and not baseline_ok[index]:
                    help_rows.append(
                        {
                            "source_row_index": index,
                            "gold": record.gold_label,
                            "before": baseline_label[index],
                            "after": scored["predicted_label"],
                        }
                    )
                if baseline_ok[index] and not ok:
                    harm_rows.append(
                        {
                            "source_row_index": index,
                            "gold": record.gold_label,
                            "before": baseline_label[index],
                            "after": scored["predicted_label"],
                        }
                    )
            swaps.append(
                {
                    "condition": name,
                    "order": list(order),
                    "purist_correct": baseline_correct + len(help_rows) - len(harm_rows),
                    "purist_help": len(help_rows),
                    "purist_harm": len(harm_rows),
                    "help_rows": help_rows,
                    "harm_rows": harm_rows,
                }
            )
        cell_results[cell_id] = {
            "n": len(raw_rows),
            "baseline_purist_correct": baseline_correct,
            "swaps": swaps,
        }

    adopt: list[str] = []
    for swap_index, (pair, _order) in enumerate(adjacent_semantic_family_orders()):
        name = f"swap:{pair[0]}|{pair[1]}"
        complete_cells = [
            cell
            for cell in cell_results.values()
            if "swaps" in cell
        ]
        if len(complete_cells) != len(CELLS):
            continue
        if all(
            cell["swaps"][swap_index]["purist_help"] >= 1
            and cell["swaps"][swap_index]["purist_harm"] == 0
            for cell in complete_cells
        ):
            adopt.append(name)

    return {
        "created_at": datetime.now(UTC).isoformat(),
        "split": split,
        "protocol": "docs/research/gan2026/gan_semantic_family_order_protocol_2026-08-20.md",
        "default_order": list(DEFAULT_SEMANTIC_FAMILY_ORDER),
        "adopt_if_harm_free_on_all_cells": adopt,
        "cells": cell_results,
    }


def write_adjacent_swap_artifact(path: Path | None = None) -> Path:
    """Write the adjacent-swap replay artifact."""

    payload = replay_adjacent_swaps()
    out = path or (
        ROOT / "experiments/paper/gan_semantic_family_order/dev750_adjacent_swaps.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main() -> None:
    path = write_adjacent_swap_artifact()
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(path)
    print("adopt", payload["adopt_if_harm_free_on_all_cells"])
    for cell_id, cell in payload["cells"].items():
        if "missing" in cell:
            print(cell_id, "MISSING", cell["missing"])
            continue
        print(cell_id, "baseline", cell["baseline_purist_correct"], "/", cell["n"])
        for swap in cell["swaps"]:
            print(
                " ",
                swap["condition"],
                "help",
                swap["purist_help"],
                "harm",
                swap["purist_harm"],
                "correct",
                swap["purist_correct"],
            )


if __name__ == "__main__":
    main()
