import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm import (
    PROMPT_VERSION,
    CanonicalLlmDecisionRecord,
    build_prompt_input,
    load_reusable_raw_outputs,
    parse_decision_json,
    run_split,
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text="Present seizure frequency: two seizures per month.",
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def test_build_prompt_input_excludes_gold_and_embeds_rule_taxonomy() -> None:
    prompt = json.loads(build_prompt_input(_record()))

    assert prompt["prompt_version"] == PROMPT_VERSION
    assert prompt["note_text"] == _record().note_text
    assert "gold_label" not in json.dumps(prompt)

    notes = prompt["guidance_for_tricky_cases"]["notes"]
    assert any("cluster_axis_ambiguity" in note for note in notes)
    assert any("seizure_free_conflict" in note for note in notes)
    assert any("same_window_additive_frequency" in note for note in notes)


def test_parse_decision_json_accepts_fenced_json_and_repairs_label() -> None:
    raw = """```json
    {
      "final_label": " 2 PER MONTH ",
      "evidence": "two seizures per month",
      "answer_kind": "frequency",
      "selected_seizure_type": "seizures",
      "time_window": "current",
      "applied_rule_families": ["concrete_frequency_precedence"],
      "confidence": "high",
      "rationale": "The note explicitly gives the current frequency."
    }
    ```"""

    decision, errors = parse_decision_json(raw)

    assert isinstance(decision, CanonicalLlmDecisionRecord)
    assert decision.final_label == "2 per month"
    assert decision.applied_rule_families == ["concrete_frequency_precedence"]
    assert errors == ["final_label_repaired: ' 2 PER MONTH ' -> '2 per month'"]


def test_run_split_reuses_raw_outputs_without_new_call(tmp_path: Path) -> None:
    raw_output = json.dumps(
        {
            "final_label": "2 per month",
            "evidence": "two seizures per month",
            "answer_kind": "frequency",
            "selected_seizure_type": "seizures",
            "time_window": "current",
            "applied_rule_families": [],
            "confidence": "high",
            "rationale": "The note gives the current frequency.",
        }
    )
    reuse_path = tmp_path / "prior.jsonl"
    reuse_path.write_text(
        json.dumps({"source_row_index": 10, "raw_output": raw_output}) + "\n",
        encoding="utf-8",
    )

    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs=load_reusable_raw_outputs(reuse_path),
        reuse_source=str(reuse_path),
        escalation_reason="testing reuse",
    )

    assert metadata["summary"]["decision_records"] == 1
    assert metadata["summary"]["reused_raw_outputs"] == 1
    assert rows[0]["reused_raw_output"] is True
    assert rows[0]["decision_record"]["final_label"] == "2 per month"
    assert rows[0]["parse_errors"] == []


def test_run_split_retains_explorer_compatible_llm_only_boundary(tmp_path: Path) -> None:
    raw_output = json.dumps(
        {
            "final_label": " 2 PER MONTH ",
            "evidence": "two seizures per month",
            "answer_kind": "frequency",
            "selected_seizure_type": "seizures",
            "time_window": "current",
            "applied_rule_families": [],
            "confidence": "high",
            "rationale": "The note gives the current frequency.",
        }
    )

    rows, _ = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        reuse_raw_outputs={10: raw_output},
        reuse_source="test fixture",
    )

    trace = rows[0]["row_trace"]
    assert trace["schema_version"] == "gan2026.row_trace.v1"
    assert trace["method"] == "llm_only"
    assert trace["model_prediction"]["record"]["final_label"] == " 2 PER MONTH "
    assert trace["deterministic_adapter"]["after_label"] == "2 per month"
    assert trace["evidence_validation"] == {
        "evidence": "two seizures per month",
        "exact_substring": True,
    }
