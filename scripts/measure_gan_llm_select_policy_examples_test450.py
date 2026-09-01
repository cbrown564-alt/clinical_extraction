#!/usr/bin/env python3
"""Aggregate-only test450 run of the living policy-example select prompt.

Protocol:
docs/research/gan2026/gan_llm_select_policy_examples_test450_protocol_2026-08-31.md
Writes an isolated work cell. Does not overwrite cited cell 5.
Do not inspect or quote holdout rows. Public output is counts only.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.paper.gan_later_stage import run_later_stage

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/gan2026/"
    "gan_llm_select_policy_examples_test450_protocol_2026-08-31.md"
)
OUT_JSON = (
    ROOT
    / "docs/research/gan2026/"
    / "gan_llm_select_policy_examples_test450_2026-08-31.json"
)
WORK_LEAF = "gan_llm_select_policy_examples"
PROMPT_VERSION = "gan_llm_select_policy_examples"
CITED_CELL5 = 357
PUBLIC_FORBIDDEN_KEYS = {
    "by_class",
    "classification_report",
    "diagnostics",
    "final_label",
    "gold_label",
    "letter_id",
    "letters",
    "note_text",
    "per_class_deltas",
    "predictions",
    "reference",
    "rows",
    "source_row_index",
    "source_row_indices",
    "traces",
    "incorrect_source_row_indices",
}


def assert_public_payload_aggregate_only(payload: dict[str, Any]) -> None:
    leaked = sorted(PUBLIC_FORBIDDEN_KEYS.intersection(payload))
    if leaked:
        raise ValueError(f"public payload contains forbidden keys: {leaked}")


def main() -> None:
    result = run_later_stage(
        "gan_llm_select_from_extract",
        "gemini37flash",
        split="test450",
        work_leaf=WORK_LEAF,
        recorded_prompt_version=PROMPT_VERSION,
        live_sync=True,
    )
    summary = result["summary"]
    purist = int(summary["purist_correct"])
    pragmatic = int(summary["pragmatic_correct"])
    scorable = int(summary.get("scorable") or summary.get("n") or 450)
    n = 450
    payload = {
        "schema_version": "gan_llm_select_policy_examples_test450.v1",
        "generated_on": datetime.now(UTC).date().isoformat(),
        "protocol": PROTOCOL,
        "dataset": "gan2026",
        "split": "test450",
        "split_manifest": "gan2026_split_v1",
        "row_policy": "aggregate_only",
        "model": "gemini/gemini-3.7-flash",
        "model_slug": "gemini37flash",
        "extract_ledger": "gan_llm_extract",
        "select_method": "gan_llm_select_from_extract",
        "prompt_version": PROMPT_VERSION,
        "work_leaf": WORK_LEAF,
        "work_cell": result["artifact"],
        "model_calls": result["model_calls"],
        "call_transport": "sync",
        "scorer": "purist",
        "n": n,
        "select": {
            "purist_correct": purist,
            "pragmatic_correct": pragmatic,
            "scorable": scorable,
            "purist": round(purist / n, 4),
            "pragmatic": round(pragmatic / n, 4),
        },
        "comparators": {
            "cited_cell5_purist": CITED_CELL5,
            "cited_cell4_purist": 382,
            "cited_cell3_purist": 387,
        },
        "delta_vs_cited_cell5": purist - CITED_CELL5,
        "claim_boundary": (
            "Holdout aggregate-only measurement of a living select-prompt "
            "candidate. Not Table 1. Not a promotion. Cited cell 5 stays "
            f"{CITED_CELL5}/450."
        ),
    }
    assert_public_payload_aggregate_only(payload)
    OUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
