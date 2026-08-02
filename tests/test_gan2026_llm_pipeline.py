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
    write_jsonl,
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


def test_build_prompt_input_instructs_short_plain_rationale() -> None:
    # Regression guard: qwen3.6:35b filled the `rationale` field with verbose
    # step-by-step deliberation (e.g. "Is '4 per month' definitely allowed? ...
    # I will proceed with...") when the prompt gave it no style guidance,
    # embedding quotes/control-characters/run-on punctuation that broke JSON
    # parsing (PROMPT_VERSION v0.1 -> v0.2). The prompt must explicitly tell
    # the model to keep rationale to one short, plain sentence with an example.
    instructions = " ".join(json.loads(build_prompt_input(_record()))["instructions"])

    assert "Write rationale as one short, plain-language sentence" in instructions
    assert "Do not show step-by-step reasoning" in instructions


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


def test_parse_decision_json_tolerates_missing_applied_rule_families() -> None:
    raw = json.dumps(
        {
            "final_label": "2 per month",
            "evidence": "two seizures per month",
            "answer_kind": "frequency",
            "selected_seizure_type": "seizures",
            "time_window": "current",
            "confidence": "high",
            "rationale": "The note gives the current frequency.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.applied_rule_families == []
    assert errors == []


def test_parse_decision_json_accepts_null_time_window_and_seizure_type() -> None:
    # Regression guard: qwen3.6:35b legitimately emits JSON null for
    # time_window and/or selected_seizure_type when the note contains no
    # usable seizure-frequency reference at all (answer_kind "no_reference"),
    # where gpt-4.1-mini instead always emits a string (often "" for the same
    # case). Both are valid representations of "nothing specific to report";
    # the schema must accept null rather than raising
    # "Input should be a valid string".
    raw = json.dumps(
        {
            "final_label": "no seizure frequency reference",
            "evidence": "...",
            "answer_kind": "no_reference",
            "selected_seizure_type": None,
            "time_window": None,
            "applied_rule_families": [],
            "confidence": "high",
            "rationale": "...",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.selected_seizure_type is None
    assert decision.time_window is None
    assert errors == []


def test_parse_decision_json_coerces_ration_typo_to_rationale() -> None:
    # Regression guard: a local model (qwen3.6:35b) emitted the field name
    # "ration" instead of "rationale", which otherwise fails schema validation
    # with a spurious "Field required" error despite the content being present.
    raw = json.dumps(
        {
            "final_label": "2 per month",
            "evidence": "two seizures per month",
            "answer_kind": "frequency",
            "selected_seizure_type": "seizures",
            "time_window": "current",
            "confidence": "high",
            "ration": "The note gives the current frequency.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.rationale == "The note gives the current frequency."
    assert errors == []


def test_parse_decision_json_coerces_scalar_applied_rule_families() -> None:
    raw = json.dumps(
        {
            "final_label": "2 per month",
            "evidence": "two seizures per month",
            "answer_kind": "frequency",
            "selected_seizure_type": "seizures",
            "time_window": "current",
            "applied_rule_families": "seizure_free_conflict",
            "confidence": "high",
            "rationale": "The note gives the current frequency.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.applied_rule_families == ["seizure_free_conflict"]
    assert errors == []


def test_prompt_only_run_writes_not_run_records(tmp_path: Path) -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
    )

    assert metadata["summary"]["decision_records"] == 0
    assert metadata["dspy_cache"] is True
    assert rows[0]["parse_errors"] == ["not_run"]
    assert rows[0]["prompt_version"] == PROMPT_VERSION

    path = tmp_path / "records.jsonl"
    write_jsonl(rows, path)
    assert json.loads(path.read_text(encoding="utf-8"))["source_row_index"] == 10


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
    assert metadata["summary"]["evidence_text_contained"] == 1
    assert metadata["summary"]["evidence_text_containment_rate"] == 1.0
    assert rows[0]["reused_raw_output"] is True
    assert rows[0]["decision_record"]["final_label"] == "2 per month"
    assert rows[0]["evidence_text_contained"] is True
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
    assert trace["model_prediction"]["raw_output_field"] == "raw_output"
    assert trace["deterministic_adapter"]["before_label"] == " 2 PER MONTH "
    assert trace["deterministic_adapter"]["after_label"] == "2 per month"
    assert trace["deterministic_adapter"]["events"] == [
        "final_label_repaired: ' 2 PER MONTH ' -> '2 per month'"
    ]
    assert trace["evidence_validation"] == {
        "evidence": "two seizures per month",
        "exact_substring": True,
    }
    assert trace["scoring"] == rows[0]["comparison"]


def test_run_split_checkpoints_progress(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "checkpoint.jsonl"
    report_path = tmp_path / "checkpoint.md"

    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        progress_every=1,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
    )

    assert metadata["summary"]["decision_records"] == 0
    assert len(rows) == 1
    assert jsonl_path.exists()
    assert report_path.exists()
    assert json.loads(jsonl_path.read_text(encoding="utf-8"))["parse_errors"] == ["not_run"]
