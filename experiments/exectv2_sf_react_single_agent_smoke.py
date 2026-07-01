"""Smoke test for the ExECTv2 SF ReAct single-agent condition (near-zero
cost). Phase 3, Task 20 of docs/plans/proud-bubbling-ocean.md. Runs
single_greedy and single_agent_tools_react on 5 dev letters, scores each
via the production score_frequency_state, and reports call/parse failures
and tool-use behavior.
"""
from __future__ import annotations

import json

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.agentic import (
    react_single_agent,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    DspySinglePassSFExtractor,
    build_prompt_input,
    to_predicted_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    parse_extraction_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    score_frequency_state,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

MODEL = "openai/gpt-4.1-mini"
N_ROWS = 5
SPEC = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]


def score_extraction(letter, raw_output: str) -> tuple[float | None, list[str]]:
    extraction, parse_errors = parse_extraction_json(raw_output) if raw_output else (None, ["not_run"])
    if extraction is None:
        return None, parse_errors
    predicted_letter, warnings = to_predicted_letter(
        letter.letter_id, extraction.mentions, spec=SPEC, note_text=letter.note_text
    )
    pred_exect_letter = to_exect_letter(predicted_letter, note_text=letter.note_text)
    scores = score_frequency_state([letter], [pred_exect_letter])
    return scores.clinical_headline.f1, parse_errors + warnings


def main() -> None:
    dspy.configure(lm=build_dspy_lm(MODEL, temperature=0.0, max_tokens=800, cache=True))
    letters = load_letters_for_split("dev")[:N_ROWS]

    print("#" * 70)
    print("# single_greedy")
    print("#" * 70)
    greedy = DspySinglePassSFExtractor()
    for letter in letters:
        prompt_input_json = build_prompt_input(letter)
        prediction = greedy(prompt_input_json=prompt_input_json)
        f1, notes = score_extraction(letter, str(prediction.extraction_json))
        print(f"{letter.letter_id}: f1={f1} notes={notes[:2]}")

    print("\n" + "#" * 70)
    print("# single_agent_tools_react")
    print("#" * 70)
    call_failures = 0
    parse_failures = 0
    for letter in letters:
        prompt_input_json = build_prompt_input(letter)
        try:
            prediction = react_single_agent.run_single_row(
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
        print(
            f"{letter.letter_id}: f1={f1} turns={n_turns} tools_used={tools_used} "
            f"notes={notes[:2]}"
        )

    print("\n" + "=" * 70)
    print(json.dumps({"rows": len(letters), "call_failures": call_failures, "parse_failures": parse_failures}, indent=2))
    if call_failures or parse_failures:
        raise SystemExit("Smoke test found call or parse failures.")
    print("Smoke test passed cleanly.")


if __name__ == "__main__":
    main()
