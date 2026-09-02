#!/usr/bin/env python3
"""Development run of the living policy-example select prompt.

Protocol:
docs/research/gan2026/gan_llm_select_policy_examples_dev750_protocol_2026-08-31.md
Writes an isolated work cell. Does not overwrite cited cell 5.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from clinical_extraction.paper.gan_later_stage import run_later_stage
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/gan2026/"
    "gan_llm_select_policy_examples_dev750_protocol_2026-08-31.md"
)
OUT_JSON = (
    ROOT
    / "docs/research/gan2026/"
    / "gan_llm_select_policy_examples_dev750_2026-08-31.json"
)
WORK_LEAF = "gan_llm_select_policy_examples"
PROMPT_VERSION = "gan_llm_select_policy_examples"
CITED_CELL5 = 590
CITED_CELL3 = 656
CITED_RULES = 691
CITED_CELL5_ROWS = (
    ROOT
    / "experiments/paper/gan_llm_select_from_extract/gemini37flash"
    / "gan_llm_extract/dev750/rows.jsonl"
)
CANDIDATE_ROWS = (
    ROOT
    / "experiments/paper/gan_llm_select_policy_examples/gemini37flash"
    / "gan_llm_extract/dev750/rows.jsonl"
)


def _flag_map(path: Path) -> dict[int, bool]:
    scored: dict[int, bool] = {}
    for row in load_jsonl_rows(path):
        scored[int(row["source_row_index"])] = bool(
            (row.get("comparison") or {}).get("purist_correct")
        )
    return scored


def _changed_row_totals() -> dict[str, int]:
    if not CITED_CELL5_ROWS.is_file() or not CANDIDATE_ROWS.is_file():
        return {}
    cited = _flag_map(CITED_CELL5_ROWS)
    candidate = _flag_map(CANDIDATE_ROWS)
    shared = sorted(set(cited) & set(candidate))
    rescues = sum(1 for key in shared if candidate[key] and not cited[key])
    harms = sum(1 for key in shared if cited[key] and not candidate[key])
    return {
        "paired_n": len(shared),
        "rescues_vs_cited_cell5": rescues,
        "harms_vs_cited_cell5": harms,
        "net_vs_cited_cell5": rescues - harms,
    }


def main() -> None:
    result = run_later_stage(
        "gan_llm_select_from_extract",
        "gemini37flash",
        split="dev750",
        work_leaf=WORK_LEAF,
        recorded_prompt_version=PROMPT_VERSION,
        live_sync=False,
    )
    summary = result["summary"]
    purist = int(summary["purist_correct"])
    pragmatic = int(summary["pragmatic_correct"])
    n = 750
    payload = {
        "schema_version": "gan_llm_select_policy_examples_dev750.v1",
        "generated_on": datetime.now(UTC).date().isoformat(),
        "protocol": PROTOCOL,
        "dataset": "gan2026",
        "split": "dev750",
        "split_manifest": "gan2026_split_v1",
        "row_policy": "development_review_permitted",
        "model": "gemini/gemini-3.7-flash",
        "model_slug": "gemini37flash",
        "extract_ledger": "gan_llm_extract",
        "select_method": "gan_llm_select_from_extract",
        "prompt_version": PROMPT_VERSION,
        "work_leaf": WORK_LEAF,
        "work_cell": result["artifact"],
        "model_calls": result["model_calls"],
        "call_transport": "openrouter_batch",
        "scorer": "purist",
        "n": n,
        "select": {
            "purist_correct": purist,
            "pragmatic_correct": pragmatic,
            "scorable": n,
            "purist": round(purist / n, 4),
            "pragmatic": round(pragmatic / n, 4),
        },
        "comparators": {
            "cited_cell5_purist": CITED_CELL5,
            "cited_cell3_purist": CITED_CELL3,
            "cited_rules_purist": CITED_RULES,
        },
        "delta_vs_cited_cell5": purist - CITED_CELL5,
        "changed_rows_vs_cited_cell5": _changed_row_totals(),
        "claim_boundary": (
            "Development measurement of the living select prompt. "
            "Not holdout. Not Table 1. Not a promotion. Cited "
            f"dev750 cell 5 stays {CITED_CELL5}/750."
        ),
    }
    OUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
