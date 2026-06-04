from pathlib import Path
from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_simplified_selected_state_reasoner as reasoner,
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=42,
        note_text=(
            "Current diary: three focal seizures over six weeks. "
            "Past history included daily seizures in 2020."
        ),
        gold_label="3 per 6 week",
        gold_reference="three focal seizures over six weeks",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="3 per 6 week",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(26.0, 26.0),
        gold_monthly_frequency=2.1666666666666665,
    )


def _prediction(final_label: str = "3 per 6 weeks") -> SimpleNamespace:
    return SimpleNamespace(
        selected_state={
            "final_kind": "frequency",
            "raw_llm_final_label": final_label,
            "selected_evidence": "three focal seizures over six weeks",
            "raw_source_phrase": "three focal seizures over six weeks",
            "selection_reason": "The current diary is the relevant seizure-frequency state.",
            "uncertainty_flags": [],
        }
    )


def test_build_selected_state_inputs_exposes_minimal_schema_without_gold() -> None:
    inputs = reasoner.build_selected_state_inputs(_record())

    assert inputs["note_text"] == _record().note_text
    assert "pipeline_family" not in inputs["output_contract"]
    assert "typed_output_schema_version" not in inputs["output_contract"]
    assert inputs["output_contract"]["top_level_outputs"] == ["selected_state"]
    assert inputs["output_contract"]["selected_state_fields"] == [
        "final_kind",
        "raw_llm_final_label",
        "selected_evidence",
        "raw_source_phrase",
        "selection_reason",
        "uncertainty_flags",
    ]
    assert inputs["output_contract"]["field_descriptions"]["raw_llm_final_label"]
    assert "selected clinical state" in str(inputs).lower()
    assert "gold_label" not in str(inputs)
    assert "deterministic candidates" not in str(inputs)


def test_prediction_to_extraction_validates_one_selected_state_and_exact_evidence() -> None:
    extraction, adapter_errors = reasoner.prediction_to_extraction(
        _prediction(),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert adapter_errors == []
    assert reasoner.validate_selected_state_extraction(
        extraction,
        note_text=_record().note_text,
    ) == []
    assert extraction.selected_state.final_kind == "frequency"
    assert extraction.selected_state.selected_evidence == "three focal seizures over six weeks"


def test_validate_selected_state_flags_non_exact_evidence() -> None:
    prediction = _prediction()
    prediction.selected_state["selected_evidence"] = "three focal seizures in six weeks"
    extraction, adapter_errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert adapter_errors == []

    assert reasoner.validate_selected_state_extraction(
        extraction,
        note_text=_record().note_text,
    ) == ["evidence: invalid selected evidence"]


def test_prediction_to_extraction_repairs_source_checked_raw_phrase_artifacts() -> None:
    prediction = _prediction("4 per day")
    prediction.selected_state["selected_evidence"] = (
        "On logs, the observed frequency is noted as ≤ four per day."
    )
    prediction.selected_state["raw_source_phrase"] = "\x0264 four per day"
    note_text = "On logs, the observed frequency is noted as ≤ four per day."

    extraction, adapter_errors = reasoner.prediction_to_extraction(
        prediction,
        note_text=note_text,
    )

    assert extraction is not None
    assert adapter_errors == []
    assert extraction.selected_state.raw_source_phrase == "≤ four per day"
    assert reasoner.validate_selected_state_extraction(extraction, note_text=note_text) == []


def test_score_layers_use_selected_evidence_adapter_without_graph_projection(monkeypatch) -> None:
    class StubProgram:
        def __call__(self, **kwargs):
            return _prediction("3 per 6 weeks")

    monkeypatch.setattr(reasoner, "DspySimplifiedSelectedStateReasoner", StubProgram)
    rows, metadata = reasoner.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1200,
        mode="live",
        dspy_cache=False,
    )

    assert metadata["architecture"] == reasoner.PIPELINE_FAMILY
    assert metadata["typed_output_schema_version"] == reasoner.SIMPLIFIED_OUTPUT_SCHEMA_VERSION
    assert metadata["summary"]["structured_records"] == 1
    assert metadata["summary"]["selected_evidence_arithmetic_scorable"] == 1
    assert "typed_operation_graph_projection" not in rows[0]["score_layers"]
    assert "typed_operation_graph" not in rows[0]
    assert rows[0]["pipeline_family"] == reasoner.PIPELINE_FAMILY
    assert rows[0]["score_layers"]["raw_llm"]["final_label"] == "3 per 6 weeks"
    assert rows[0]["score_layers"]["selected_evidence_arithmetic"]["final_label"] == (
        "3 per 6 week"
    )


def test_write_report_records_selection_only_scope(tmp_path: Path) -> None:
    rows, metadata = reasoner.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1200,
        mode="prompt-only",
    )
    report = tmp_path / "simplified_selected_state.md"
    reasoner.write_report(rows, metadata, report, jsonl_path=tmp_path / "rows.jsonl")

    text = report.read_text(encoding="utf-8")
    assert "Simplified Selected State Reasoner" in text
    assert "one selected clinical state" in text
    assert "No graph projection" in text
