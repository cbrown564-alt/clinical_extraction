from pathlib import Path
from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_sparse_operands_selected_state_reasoner as reasoner,
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


def _prediction(final_label: str = "about three in interval") -> SimpleNamespace:
    return SimpleNamespace(
        selected_state={
            "final_kind": "frequency",
            "raw_llm_final_label": final_label,
            "selected_evidence": "three focal seizures over six weeks",
            "raw_source_phrase": "three focal seizures over six weeks",
            "selected_operation_kind": "frequency_rate",
            "operands": {
                "count_low": 3,
                "count_high": None,
                "period_count_low": 6,
                "period_count_high": None,
                "period_unit": "week",
                "cluster_count": None,
                "seizures_per_cluster_low": None,
                "seizures_per_cluster_high": None,
                "seizure_free_duration_count": None,
                "seizure_free_duration_unit": None,
                "abstain_reason": "",
            },
            "selection_reason": "The current diary is the relevant seizure-frequency state.",
            "uncertainty_flags": [],
        }
    )


def test_build_sparse_operands_inputs_exposes_a2_schema_without_gold() -> None:
    inputs = reasoner.build_sparse_operands_inputs(_record())

    assert inputs["note_text"] == _record().note_text
    assert "pipeline_family" not in inputs["output_contract"]
    assert "typed_output_schema_version" not in inputs["output_contract"]
    assert inputs["output_contract"]["top_level_outputs"] == ["selected_state"]
    assert "operands" in inputs["output_contract"]["selected_state_fields"]
    assert "period_count_high" in inputs["output_contract"]["numeric_detail_fields"]
    assert inputs["output_contract"]["field_descriptions"]["operands"]
    assert inputs["output_contract"]["numeric_detail_field_descriptions"]["period_count_high"]
    assert "numeric detail" in str(inputs).lower()
    assert "gold_label" not in str(inputs)
    assert "deterministic candidates" not in str(inputs)


def test_prediction_to_extraction_validates_sparse_operands_and_exact_evidence() -> None:
    extraction, adapter_errors = reasoner.prediction_to_extraction(
        _prediction(),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert adapter_errors == []
    assert reasoner.validate_sparse_operands_extraction(
        extraction,
        note_text=_record().note_text,
    ) == []
    assert extraction.selected_state.operands.count_low == 3
    assert extraction.selected_state.operands.period_unit == "week"


def test_validate_sparse_operands_flags_numeric_operands_on_sentinel_state() -> None:
    prediction = _prediction("unknown")
    prediction.selected_state["final_kind"] = "unknown"
    prediction.selected_state["selected_operation_kind"] = "unknown_frequency"
    extraction, adapter_errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert adapter_errors == []

    assert reasoner.validate_sparse_operands_extraction(
        extraction,
        note_text=_record().note_text,
    ) == ["sparse_operands_boundary: numeric operands on sentinel state"]


def test_score_layers_add_sparse_operand_adapter_without_graph_projection(monkeypatch) -> None:
    class StubProgram:
        def __call__(self, **kwargs):
            return _prediction("about three in interval")

    monkeypatch.setattr(reasoner, "DspySparseOperandsSelectedStateReasoner", StubProgram)
    rows, metadata = reasoner.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1400,
        mode="live",
        dspy_cache=False,
    )

    assert metadata["architecture"] == reasoner.PIPELINE_FAMILY
    assert metadata["typed_output_schema_version"] == reasoner.SPARSE_OPERANDS_SCHEMA_VERSION
    assert metadata["summary"]["structured_records"] == 1
    assert "sparse_operand_adapter" in rows[0]["score_layers"]
    assert "typed_operation_graph_projection" not in rows[0]["score_layers"]
    assert "typed_operation_graph" not in rows[0]
    assert rows[0]["score_layers"]["sparse_operand_adapter"]["final_label"] == "3 per 6 week"


def test_sparse_operand_adapter_ignores_operands_for_unknown_state(monkeypatch) -> None:
    class StubProgram:
        def __call__(self, **kwargs):
            prediction = _prediction("unknown")
            prediction.selected_state["final_kind"] = "unknown"
            prediction.selected_state["selected_evidence"] = "no seizure frequency reference"
            prediction.selected_state["raw_source_phrase"] = "no seizure frequency reference"
            prediction.selected_state["selected_operation_kind"] = "unknown_frequency"
            prediction.selected_state["operands"] = {
                **prediction.selected_state["operands"],
                "count_low": None,
                "period_count_low": None,
                "period_unit": None,
                "abstain_reason": "Selected state is unclear.",
            }
            return prediction

    monkeypatch.setattr(reasoner, "DspySparseOperandsSelectedStateReasoner", StubProgram)
    rows, _metadata = reasoner.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1400,
        mode="live",
        dspy_cache=False,
    )

    assert rows[0]["score_layers"]["sparse_operand_adapter"]["final_label"] == "unknown"


def test_sparse_operand_adapter_defers_cluster_cadence_without_per_cluster_load() -> None:
    prediction = _prediction("clusters every 4 weeks")
    prediction.selected_state["selected_evidence"] = (
        "At present he reports clusters of brief absence episodes every 4 weeks, "
        "usually over 1-2 days."
    )
    prediction.selected_state["raw_source_phrase"] = (
        "clusters of brief absence episodes every 4 weeks"
    )
    prediction.selected_state["selected_operation_kind"] = "cluster_frequency"
    prediction.selected_state["operands"] = {
        **prediction.selected_state["operands"],
        "count_low": 1,
        "count_high": 2,
        "period_count_low": 4,
        "period_unit": "week",
    }
    extraction, adapter_errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert adapter_errors == []
    assert reasoner._sparse_operand_adapter_label(extraction) is None


def test_sparse_operand_adapter_defers_unresolved_multiple_to_selected_evidence() -> None:
    prediction = _prediction("multiple per day")
    prediction.selected_state["selected_evidence"] = (
        "In the 24 hours prior to clinic he experienced multiple seizures in past day."
    )
    prediction.selected_state["raw_source_phrase"] = "multiple seizures in past day"
    prediction.selected_state["operands"] = {
        **prediction.selected_state["operands"],
        "count_low": 2,
        "period_count_low": 1,
        "period_unit": "day",
    }
    extraction, adapter_errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert adapter_errors == []
    assert reasoner._sparse_operand_adapter_label(extraction) is None


def test_write_report_records_sparse_operands_scope(tmp_path: Path) -> None:
    rows, metadata = reasoner.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1400,
        mode="prompt-only",
    )
    report = tmp_path / "sparse_operands.md"
    reasoner.write_report(rows, metadata, report, jsonl_path=tmp_path / "rows.jsonl")

    text = report.read_text(encoding="utf-8")
    assert "Sparse Operands Selected State Reasoner" in text
    assert "Sparse nullable operands" in text
    assert "No operation graph projection" in text
