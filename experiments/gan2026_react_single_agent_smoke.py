"""Smoke test for the genuine ReAct single-agent condition (near-zero cost).

Phase 1, Task 11 of docs/plans/proud-bubbling-ocean.md /
docs/experiments/gan2026/agentic/gan2026_agentic_redo_predeclaration_2026-07-01.md.
Runs `single_agent_tools_react` on 5 validation rows and reports: call
failures, parse failures, whether each dspy.ReAct trajectory reaches
`finish` (or a clean max_iters stop), and how many tool calls the model
actually chose to make per row. Does not score against gold or write to
the registry — that is the hard50/battery stage (Task 13), gated on this
smoke test passing cleanly.
"""
from __future__ import annotations

import json

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import react_single_agent
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
    _build_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_direct_labeler import (
    parse_decision_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

MODEL = "openai/gpt-4.1-mini"
N_ROWS = 5


def main() -> None:
    dspy.configure(
        lm=build_dspy_lm(
            MODEL,
            temperature=0.2,
            max_tokens=react_single_agent.BUDGET.max_completion_tokens_per_call,
            cache=True,
        )
    )

    records = load_records_for_split("validation")[:N_ROWS]
    call_failures = 0
    parse_failures = 0

    for record in records:
        prompt_input_json = _build_prompt_input(
            record,
            condition="single_agent_tools_react",
            call_plan={"call_role": "react_agent"},
            parser_result={},
            guide_results=[],
        )
        print("=" * 70)
        print(f"source_row_index={record.source_row_index}")

        try:
            prediction = react_single_agent.run_single_row(
                prompt_input_json, note_text=record.note_text
            )
        except Exception as exc:  # pragma: no cover - live transport only
            call_failures += 1
            print(f"CALL FAILURE: {type(exc).__name__}: {exc}")
            continue

        trajectory = prediction.trajectory
        n_turns = sum(1 for key in trajectory if key.startswith("tool_name_"))
        tool_names_used = [
            trajectory[f"tool_name_{i}"] for i in range(n_turns) if f"tool_name_{i}" in trajectory
        ]
        reached_finish = "finish" in tool_names_used
        print(f"turns={n_turns} tools_used={tool_names_used} reached_finish={reached_finish}")
        for i in range(n_turns):
            thought = trajectory.get(f"thought_{i}", "")
            tool_name = trajectory.get(f"tool_name_{i}", "")
            tool_args = trajectory.get(f"tool_args_{i}", "")
            observation = trajectory.get(f"observation_{i}", "")
            print(f"  [{i}] thought={thought!r}")
            print(f"      tool={tool_name} args={tool_args}")
            print(f"      observation={str(observation)[:200]}")

        decision_json = str(prediction.decision_json)
        decision, parse_errors = parse_decision_json(decision_json)
        if decision is None:
            parse_failures += 1
            print(f"PARSE FAILURE: {parse_errors} | raw={decision_json[:300]}")
        else:
            print(f"decision: final_label={decision.final_label!r} answer_kind={decision.answer_kind!r}")

    print("=" * 70)
    print(
        json.dumps(
            {
                "rows": len(records),
                "call_failures": call_failures,
                "parse_failures": parse_failures,
            },
            indent=2,
        )
    )
    if call_failures or parse_failures:
        raise SystemExit("Smoke test found call or parse failures — do not proceed to battery/hard50.")
    print("Smoke test passed cleanly.")


if __name__ == "__main__":
    main()
