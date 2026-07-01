"""Smoke test for ExECTv2 SF Angle 2 (near-zero cost). Phase 3, Task 22.
Runs multi_agent_d3_static and multi_agent_dynamic_orchestrator on 5 dev
letters, scores via the production score_frequency_state, and reports
call/parse failures and tool-use behavior.
"""
from __future__ import annotations

import json

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.agentic import (
    multi_agent_ceiling,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    build_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from experiments.exectv2_sf_react_single_agent_smoke import score_extraction

MODEL = "openai/gpt-4.1-mini"
N_ROWS = 5


def smoke_d3_static(letters) -> tuple[int, int]:
    print("\n" + "#" * 70)
    print("# multi_agent_d3_static")
    print("#" * 70)
    call_failures = 0
    parse_failures = 0
    for letter in letters:
        prompt_input_json = build_prompt_input(letter)
        try:
            result = multi_agent_ceiling.run_d3_static(prompt_input_json)
        except Exception as exc:  # pragma: no cover - live transport only
            call_failures += 1
            print(f"{letter.letter_id}: CALL FAILURE: {type(exc).__name__}: {exc}")
            continue
        f1, notes = score_extraction(letter, result["extraction_json"])
        if f1 is None:
            parse_failures += 1
        print(f"{letter.letter_id}: f1={f1} notes={notes[:2]}")
    return call_failures, parse_failures


def smoke_dynamic_orchestrator(letters) -> tuple[int, int]:
    print("\n" + "#" * 70)
    print("# multi_agent_dynamic_orchestrator")
    print("#" * 70)
    call_failures = 0
    parse_failures = 0
    for letter in letters:
        prompt_input_json = build_prompt_input(letter)
        try:
            prediction = multi_agent_ceiling.run_dynamic_orchestrator_row(
                prompt_input_json, note_text=letter.note_text
            )
        except Exception as exc:  # pragma: no cover - live transport only
            call_failures += 1
            print(f"{letter.letter_id}: CALL FAILURE: {type(exc).__name__}: {exc}")
            continue
        trajectory = prediction.trajectory
        n_turns = sum(1 for key in trajectory if key.startswith("tool_name_"))
        tools_used = [trajectory[f"tool_name_{i}"] for i in range(n_turns)]
        f1, notes = score_extraction(letter, str(prediction.extraction_json))
        if f1 is None:
            parse_failures += 1
        print(f"{letter.letter_id}: f1={f1} turns={n_turns} tools_used={tools_used} notes={notes[:2]}")
    return call_failures, parse_failures


def main() -> None:
    dspy.configure(lm=build_dspy_lm(MODEL, temperature=0.0, max_tokens=800, cache=True))
    letters = load_letters_for_split("dev")[:N_ROWS]

    d3_failures, d3_parse_failures = smoke_d3_static(letters)
    orch_failures, orch_parse_failures = smoke_dynamic_orchestrator(letters)

    print("\n" + "=" * 70)
    print(
        json.dumps(
            {
                "rows": len(letters),
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
        raise SystemExit("Smoke test found call or parse failures.")
    print("Smoke test passed cleanly for both Angle 2 conditions.")


if __name__ == "__main__":
    main()
