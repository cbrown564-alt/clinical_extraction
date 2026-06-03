from pathlib import Path
from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_typed_operations_reasoner as reasoner,
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=42,
        note_text=(
            "Current diary: three focal seizures over six weeks. "
            "Clusters include two events per cluster in bad weeks. "
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
    operands = {
        "event_count_low": 3,
        "event_count_high": 3,
        "time_window_low": 6,
        "time_window_high": 6,
        "time_window_unit": "week",
        "denominator_count": 1,
        "denominator_unit": "window",
        "cluster_size_low": 2,
        "cluster_size_high": 2,
        "seizure_free_duration_low": None,
        "seizure_free_duration_high": None,
        "seizure_free_duration_unit": None,
        "temporal_anchor": "current diary",
        "semiology_grouping": "focal seizures",
        "uncertainty_type": "none",
        "selected_evidence_id": "ev-1",
    }
    return SimpleNamespace(
        operations=[
            {
                "operation_id": "op-1",
                "operation_kind": "frequency_rate",
                "evidence_id": "ev-1",
                "evidence": "three focal seizures over six weeks",
                "raw_phrase": "three focal seizures over six weeks",
                "temporality": "current",
                "assertion_status": "asserted",
                "certainty": "high",
                "operands": operands,
                "model_normalized_clinical_label": "3 per 6 week",
                "clinical_note": "Current focal-seizure burden.",
            }
        ],
        selection={
            "selected_operation_ids": ["op-1"],
            "rejected_operation_ids": [],
            "target_policy": "target_scoring_policy",
            "final_clinical_state": "frequency",
            "selection_strategy": "current_highest_burden",
            "selected_evidence_id": "ev-1",
            "selected_evidence": "three focal seizures over six weeks",
            "rationale": "The current diary count is the selected fact.",
            "uncertainty_flags": [],
        },
        final_answer={
            "raw_llm_final_label": final_label,
            "raw_llm_final_kind": "frequency",
            "raw_llm_monthly_frequency": 2.17,
            "selected_evidence": "three focal seizures over six weeks",
            "selected_event_ids": ["op-1"],
            "supporting_event_ids": [],
            "rendering_operands": operands,
            "arithmetic_trace": "three over six weeks",
            "raw_clinical_summary": "",
            "combined_rationale": "",
            "final_rationale": "",
        },
    )


def test_build_typed_operations_inputs_exposes_required_operands_without_gold() -> None:
    inputs = reasoner.build_typed_operations_inputs(_record())

    assert inputs["note_text"] == _record().note_text
    assert inputs["output_contract"]["pipeline_family"] == reasoner.PIPELINE_FAMILY
    assert inputs["output_contract"]["typed_output_schema_version"] == (
        reasoner.TYPED_OUTPUT_SCHEMA_VERSION
    )
    assert inputs["output_contract"]["top_level_outputs"] == [
        "operations",
        "selection",
        "final_answer",
    ]
    operand_fields = inputs["output_contract"]["operation_operand_fields"]
    assert "event_count_low" in operand_fields
    assert "time_window_unit" in operand_fields
    assert "denominator_unit" in operand_fields
    assert "cluster_size_low" in operand_fields
    assert "seizure_free_duration_unit" in operand_fields
    assert "temporal_anchor" in operand_fields
    assert "semiology_grouping" in operand_fields
    assert "uncertainty_type" in operand_fields
    assert "selected_evidence_id" in operand_fields
    assert "Do not add any keys other than operations, selection, and final_answer" in str(inputs)
    assert "DOB" in inputs["output_contract"]["forbidden_extra_keys"]
    assert "selected_evidence_id" in inputs["output_contract"]["rendering_operands_rule"]
    assert "\\u" in inputs["output_contract"]["evidence_copy_rule"]["forbidden"]
    assert "control characters" in inputs["output_contract"]["evidence_copy_rule"]["forbidden"]
    assert "gold_label" not in str(inputs)
    assert "deterministic candidates" not in str(inputs)


def test_prediction_to_extraction_validates_operation_trace_and_graph_overlay() -> None:
    extraction, adapter_errors = reasoner.prediction_to_extraction(_prediction())

    assert extraction is not None
    assert adapter_errors == []
    assert reasoner.validate_typed_operations_extraction(
        extraction, note_text=_record().note_text
    ) == []
    graph_bundle = reasoner.typed_operation_graph_overlay(extraction, source_row_index=42)

    assert graph_bundle["projection"]["final_label"] == "3 per 6 week"
    assert graph_bundle["projection"]["selected_node_ids"] == ["op:op-1"]
    assert graph_bundle["nodes"][0]["selected_evidence_id"] == "ev-1"


def test_validate_typed_operations_flags_evidence_id_mismatch() -> None:
    prediction = _prediction()
    prediction.selection["selected_evidence_id"] = "ev-missing"
    extraction, adapter_errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert adapter_errors == []
    errors = reasoner.validate_typed_operations_extraction(
        extraction, note_text=_record().note_text
    )

    assert "selection: selected_evidence_id is not selected operation evidence_id" in errors


def test_run_split_records_typed_operations_and_graph_projection(monkeypatch) -> None:
    class StubProgram:
        def __call__(self, **kwargs):
            return _prediction("3 per 6 weeks")

    monkeypatch.setattr(reasoner, "DspyTypedOperationsReasoner", StubProgram)
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

    assert metadata["architecture"] == reasoner.PIPELINE_FAMILY
    assert metadata["typed_output_schema_version"] == reasoner.TYPED_OUTPUT_SCHEMA_VERSION
    assert metadata["summary"]["structured_records"] == 1
    assert metadata["summary"]["typed_operation_graph_projection_scorable"] == 1
    assert rows[0]["pipeline_family"] == reasoner.PIPELINE_FAMILY
    assert rows[0]["typed_operation_graph"]["projection"]["final_label"] == "3 per 6 week"
    assert rows[0]["score_layers"]["raw_llm"]["final_label"] == "3 per 6 weeks"
    assert rows[0]["score_layers"]["typed_operation_graph_projection"]["final_label"] == (
        "3 per 6 week"
    )


def test_write_report_records_typed_operations_scope(tmp_path: Path) -> None:
    rows, metadata = reasoner.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1800,
        mode="prompt-only",
    )
    report = tmp_path / "typed_operations.md"
    reasoner.write_report(rows, metadata, report, jsonl_path=tmp_path / "rows.jsonl")

    text = report.read_text(encoding="utf-8")
    assert "Typed Operations Reasoner" in text
    assert "event count, time window, denominator" in text
    assert "graph projection is over model-extracted operation nodes" in text
