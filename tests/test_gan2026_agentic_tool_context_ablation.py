from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    tool_context_ablation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tool_context_ablation import (
    TOOL_CONTEXT_CONDITIONS,
    run_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_tool_context_ablation_varies_only_prompt_context(monkeypatch) -> None:
    prompts: list[dict] = []

    def fake_model_call(prompt_input_json: str, *, model: str, temperature: float, max_tokens: int):
        del model, temperature, max_tokens
        prompts.append(json.loads(prompt_input_json))
        return (
            '{"final_label":"2 per week","evidence":"2 seizures per week",'
            '"answer_kind":"frequency","selected_seizure_type":"seizure",'
            '"time_window":"current","confidence":"high",'
            '"rationale":"The note states 2 seizures per week."}'
        )

    monkeypatch.setattr(tool_context_ablation, "_run_model_call", fake_model_call)

    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="live",
        dspy_cache=True,
        api_base=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    assert metadata["summary"]["rows"] == 1
    assert metadata["summary"]["conditions"] == list(TOOL_CONTEXT_CONDITIONS)
    assert metadata["condition_summaries"]["direct_no_tool_context"]["purist_correct"] == 1
    assert set(rows[0]["condition_traces"]) == set(TOOL_CONTEXT_CONDITIONS)

    prompts_by_condition = {prompt["condition"]: prompt for prompt in prompts}
    assert "tool_context" not in prompts_by_condition["direct_no_tool_context"]
    assert set(prompts_by_condition["direct_parser_only"]["tool_context"]) == {
        "parser_result",
        "tool_attribution_boundary",
    }
    assert set(prompts_by_condition["direct_boundary_guide_only"]["tool_context"]) == {
        "boundary_guides",
        "tool_attribution_boundary",
    }
    assert set(prompts_by_condition["direct_parser_plus_boundary_guide"]["tool_context"]) == {
        "parser_result",
        "boundary_guides",
        "tool_attribution_boundary",
    }


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=201,
        note_text="Clinic Date: 12 June 2026\nShe reports 2 seizures per week.",
        gold_label="2 per week",
        gold_reference="2 seizures per week",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per week",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(104.0, 104.0),
        gold_monthly_frequency=8.690476190476192,
    )
