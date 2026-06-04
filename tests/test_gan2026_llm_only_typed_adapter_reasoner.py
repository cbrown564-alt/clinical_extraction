from pathlib import Path
from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_typed_adapter_reasoner as reasoner,
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text=(
            "Interval history: Present seizure frequency is two focal seizures per month. "
            "Past history included daily seizures in 2020."
        ),
        gold_label="2 per month",
        gold_reference="two focal seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def _prediction(final_label: str = "2 per month") -> SimpleNamespace:
    quantity = {
        "occurrences_low": 2,
        "occurrences_high": 2,
        "period_low": 1,
        "period_high": 1,
        "period_unit": "month",
    }
    return SimpleNamespace(
        events=[
            {
                "event_id": "sf-1",
                "kind": "frequency_rate",
                "applies_to": "focal seizures",
                "raw_phrase": "two focal seizures per month",
                "evidence": "two focal seizures per month",
                "assertion_status": "asserted",
                "temporality": "current",
                "certainty": "high",
                "clinical_quantity": quantity,
                "model_normalized_clinical_label": "2 per month",
                "notes": "Current quantified focal-seizure rate.",
            }
        ],
        selection={
            "selected_event_ids": ["sf-1"],
            "rejected_event_ids": [],
            "final_clinical_state": "frequency",
            "aggregation_strategy": "highest_current_frequency",
            "final_clinical_label": "2 per month",
            "rationale": "The current event determines the answer.",
            "uncertainty_flags": [],
        },
        final_answer={
            "raw_llm_final_label": final_label,
            "raw_llm_final_kind": "frequency",
            "raw_llm_monthly_frequency": 2.0,
            "selected_evidence": "two focal seizures per month",
            "selected_event_ids": ["sf-1"],
            "rendering_operands": quantity,
            "arithmetic_trace": "two focal seizures per month -> 2 per month",
        },
    )


def test_build_typed_adapter_inputs_excludes_gold_and_opaque_json_string() -> None:
    inputs = reasoner.build_typed_adapter_inputs(_record())

    assert inputs["note_text"] == _record().note_text
    assert "prompt_version" not in inputs["output_contract"]
    assert "pipeline_family" not in inputs["output_contract"]
    assert "typed_output_schema_version" not in inputs["output_contract"]
    assert inputs["output_contract"]["top_level_outputs"] == [
        "events",
        "selection",
        "final_answer",
    ]
    assert inputs["output_contract"]["field_descriptions"]["raw_llm_final_label"]
    assert "opaque JSON string" in " ".join(inputs["task_instructions"])
    assert "gold_label" not in str(inputs)
    assert "candidate_events" not in str(inputs)


def test_prediction_to_extraction_validates_typed_outputs_and_trace() -> None:
    extraction, adapter_errors = reasoner.prediction_to_extraction(_prediction())

    assert extraction is not None
    assert adapter_errors == []
    assert extraction.events[0].event_id == "sf-1"
    assert extraction.final_answer.raw_llm_final_label == "2 per month"
    assert reasoner.validate_typed_extraction(extraction, note_text=_record().note_text) == []


def test_validate_typed_extraction_flags_trace_mismatch() -> None:
    prediction = _prediction()
    prediction.final_answer["selected_event_ids"] = ["sf-2"]
    extraction, adapter_errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert adapter_errors == []
    errors = reasoner.validate_typed_extraction(extraction, note_text=_record().note_text)
    assert "final_answer: unknown selected_event_ids ['sf-2']" in errors
    assert "selected_event_trace: final_answer ids differ from selection ids" in errors


def test_run_split_records_typed_adapter_metadata(monkeypatch) -> None:
    class StubProgram:
        def __call__(self, **kwargs):
            return _prediction("2 per months")

    monkeypatch.setattr(reasoner, "DspyTypedAdapterReasoner", StubProgram)
    rows, metadata = reasoner.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1800,
        mode="live",
        dspy_cache=False,
    )

    assert metadata["architecture"] == "llm_only_typed_adapter_reasoner"
    assert metadata["claim_type"] == "llm_only_typed_adapter_reasoner"
    assert metadata["dspy_adapter"] == "JSONAdapter"
    assert metadata["response_format_mode"] == "scoped_dspy_context_json_adapter"
    assert metadata["typed_output_schema_version"] == "typed_adapter_v0"
    assert metadata["summary"]["structured_records"] == 1
    assert metadata["summary"]["raw_llm_scorable"] == 1
    assert rows[0]["pipeline_family"] == "llm_only_typed_adapter_reasoner"
    assert rows[0]["score_layers"]["raw_llm"]["final_label"] == "2 per months"
    assert rows[0]["score_layers"]["format_only"]["final_label"] == "2 per month"
    assert rows[0]["raw_output"].startswith("{")


def test_write_report_records_predeclared_validation25_scope(tmp_path: Path) -> None:
    rows, metadata = reasoner.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1800,
        mode="prompt-only",
    )
    report = tmp_path / "typed_adapter.md"
    reasoner.write_report(rows, metadata, report, jsonl_path=tmp_path / "rows.jsonl")

    text = report.read_text(encoding="utf-8")
    assert "typed-adapter LLM-only architecture" in text
    assert "Surface: `validation25` under `gan2026_split_v1`" in text
    assert "Stop rule: do not escalate beyond this smoke" in text
