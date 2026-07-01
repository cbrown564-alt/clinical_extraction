"""Smoke test for Angle 2's two ceiling candidates (near-zero cost).

Phase 2 pre-check of docs/plans/proud-bubbling-ocean.md / the predeclaration
doc. Runs `multi_agent_d3_static` and `multi_agent_dynamic_orchestrator` on
5 validation rows and reports: call failures, parse failures, whether the
resolver actually cites specialist evidence, and (for the orchestrator)
which tools it chose to invoke. Does not score against gold or write to
the registry.
"""
from __future__ import annotations

import json

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import multi_agent_ceiling
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


def smoke_d3_static(records) -> tuple[int, int]:
    print("\n" + "#" * 70)
    print("# multi_agent_d3_static")
    print("#" * 70)
    call_failures = 0
    parse_failures = 0
    for record in records:
        prompt_input_json = _build_prompt_input(
            record,
            condition=multi_agent_ceiling.CONDITION_D3_STATIC,
            call_plan={"call_role": "d3_static"},
            parser_result={},
            guide_results=[],
        )
        print("=" * 70)
        print(f"source_row_index={record.source_row_index}")
        try:
            result = multi_agent_ceiling.run_d3_static(prompt_input_json)
        except Exception as exc:  # pragma: no cover - live transport only
            call_failures += 1
            print(f"CALL FAILURE: {type(exc).__name__}: {exc}")
            continue

        decision, parse_errors = parse_decision_json(result["decision_json"])
        if decision is None:
            parse_failures += 1
            print(f"PARSE FAILURE: {parse_errors} | raw={result['decision_json'][:300]}")
            continue
        print(f"final_label={decision.final_label!r} answer_kind={decision.answer_kind!r}")
        try:
            decision_payload = json.loads(result["decision_json"])
            cited = decision_payload.get("cited_specialists")
            rejected = decision_payload.get("rejected_alternatives")
            print(f"cited_specialists={cited}")
            print(f"rejected_alternatives={rejected}")
        except json.JSONDecodeError:
            pass
    return call_failures, parse_failures


def smoke_dynamic_orchestrator(records) -> tuple[int, int]:
    print("\n" + "#" * 70)
    print("# multi_agent_dynamic_orchestrator")
    print("#" * 70)
    call_failures = 0
    parse_failures = 0
    for record in records:
        prompt_input_json = _build_prompt_input(
            record,
            condition=multi_agent_ceiling.CONDITION_DYNAMIC_ORCHESTRATOR,
            call_plan={"call_role": "orchestrator"},
            parser_result={},
            guide_results=[],
        )
        print("=" * 70)
        print(f"source_row_index={record.source_row_index}")
        try:
            prediction = multi_agent_ceiling.run_dynamic_orchestrator_row(
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

        decision_json = str(prediction.decision_json)
        decision, parse_errors = parse_decision_json(decision_json)
        if decision is None:
            parse_failures += 1
            print(f"PARSE FAILURE: {parse_errors} | raw={decision_json[:300]}")
        else:
            print(f"final_label={decision.final_label!r} answer_kind={decision.answer_kind!r}")
    return call_failures, parse_failures


def main() -> None:
    dspy.configure(
        lm=build_dspy_lm(MODEL, temperature=0.2, max_tokens=600, cache=True)
    )
    records = load_records_for_split("validation")[:N_ROWS]

    d3_failures, d3_parse_failures = smoke_d3_static(records)
    orch_failures, orch_parse_failures = smoke_dynamic_orchestrator(records)

    print("\n" + "=" * 70)
    print(
        json.dumps(
            {
                "rows": len(records),
                "d3_static": {"call_failures": d3_failures, "parse_failures": d3_parse_failures},
                "dynamic_orchestrator": {
                    "call_failures": orch_failures,
                    "parse_failures": orch_parse_failures,
                },
            },
            indent=2,
        )
    )
    if d3_failures or d3_parse_failures or orch_failures or orch_parse_failures:
        raise SystemExit("Smoke test found call or parse failures — do not proceed to battery/hard50.")
    print("Smoke test passed cleanly for both Angle 2 conditions.")


if __name__ == "__main__":
    main()
