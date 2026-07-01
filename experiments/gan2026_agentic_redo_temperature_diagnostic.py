"""Cheap diagnostic (50 calls): is temperature=0.2 vs temperature=0.0 the
cause of single_greedy's implausible 34/50 -> 17/50 drop in the battery+
hard50 run? Reruns single_greedy on hard50 ONLY, at temperature=0.0, and
reports accuracy for direct comparison against the temperature=0.2 result
already on disk in gan2026_agentic_redo_battery_hard50_results.jsonl.
"""
from __future__ import annotations

import json

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.contracts import AgentBudget
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
    _compare_to_gold,
    _condition_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_direct_labeler import (
    LlmOnlyDirectLabelerDecisionRecord,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

MODEL = "openai/gpt-4.1-mini"
HARD50_PATH = "experiments/gan2026_agentic_validation_hard50_source_rows_2026-06-12.txt"

BUDGET = AgentBudget(
    model_calls_per_row=4,
    prompt_token_budget=2_500,
    max_completion_tokens_per_call=600,
    max_tool_calls_per_row=3,
    max_tool_output_tokens_per_row=700,
    aggregation_budget_model_calls=1,
)


def load_hard50():
    with open(HARD50_PATH, encoding="utf-8") as fh:
        idx = {int(line) for line in fh.read().splitlines() if line.strip()}
    records = [r for r in load_records_for_split("validation") if r.source_row_index in idx]
    assert len(records) == 50
    return records


def main() -> None:
    dspy.configure(lm=build_dspy_lm(MODEL, temperature=0.0, max_tokens=600, cache=True))
    records = load_hard50()

    correct = 0
    wrong_rows = []
    for record in records:
        trace = _condition_trace(
            "single_greedy",
            record=record,
            model=MODEL,
            temperature=0.0,
            max_tokens=600,
            mode="live",
            budget=BUDGET,
            parser_result={},
            guide_results=[],
        )
        final_label = trace.get("final_label")
        if not final_label:
            wrong_rows.append((record.source_row_index, "NO_LABEL"))
            continue
        decision = LlmOnlyDirectLabelerDecisionRecord(
            final_label=final_label,
            evidence="",
            answer_kind="frequency",
            selected_seizure_type=None,
            time_window=None,
            confidence="medium",
            rationale="",
        )
        try:
            comparison = _compare_to_gold(record, decision)
        except ValueError:
            wrong_rows.append((record.source_row_index, f"UNPARSEABLE:{final_label!r}"))
            continue
        if comparison["purist_correct"]:
            correct += 1
        else:
            wrong_rows.append((record.source_row_index, final_label))

    print(json.dumps({"temperature": 0.0, "purist_correct": correct, "n": len(records)}, indent=2))
    print("wrong/unparseable rows:", wrong_rows)


if __name__ == "__main__":
    main()
