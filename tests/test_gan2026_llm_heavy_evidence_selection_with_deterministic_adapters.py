from pathlib import Path
from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_heavy_evidence_selection_with_deterministic_adapters as reasoner,
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=42,
        note_text=(
            "Interval history: She reports three focal seizures over six weeks. "
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
        gold_yearly_bounds=(26.0714285714, 26.0714285714),
        gold_monthly_frequency=2.142857142857143,
    )


def _prediction(raw_label: str = "multiple per week") -> SimpleNamespace:
    return SimpleNamespace(
        selected_fact={
            "fact_id": "sf-1",
            "clinical_kind": "frequency",
            "applies_to": "focal seizures",
            "evidence": "three focal seizures over six weeks",
            "raw_value": "three focal seizures over six weeks",
            "temporality": "recent",
            "assertion_status": "asserted",
            "competing_fact_summary": "Historical daily seizures are not current.",
            "rationale": "The recent current-window focal seizure count determines the answer.",
            "benchmark_caveat_flags": ["total_window_statement"],
        },
        operands={
            "frequency": {
                "occurrences_low": 3,
                "occurrences_high": 3,
                "denominator_low": 6,
                "denominator_high": 6,
                "denominator_unit": "week",
                "vague_count": None,
            },
            "cluster": None,
            "seizure_free": None,
        },
        raw_model_answer={
            "raw_model_parser_label": raw_label,
            "raw_model_final_kind": "frequency",
            "selected_evidence": "three focal seizures over six weeks",
            "confidence": "high",
            "clinical_rationale": "The selected evidence is recent and quantified.",
        },
    )


def test_build_typed_inputs_exposes_decision_0007_contract() -> None:
    inputs = reasoner.build_typed_inputs(_record())

    assert inputs["note_text"] == _record().note_text
    assert inputs["output_contract"]["pipeline_family"] == reasoner.PIPELINE_FAMILY
    assert inputs["output_contract"]["typed_output_schema_version"] == (
        reasoner.TYPED_OUTPUT_SCHEMA_VERSION
    )
    assert inputs["output_contract"]["top_level_outputs"] == [
        "selected_fact",
        "operands",
        "raw_model_answer",
    ]
    assert "model selects the clinical fact" in " ".join(inputs["task_instructions"])
    assert "gold_label" not in str(inputs)
    assert "candidate_events" not in str(inputs)


def test_mechanical_adapter_renders_from_selected_frequency_operands() -> None:
    extraction, errors = reasoner.prediction_to_extraction(_prediction())

    assert extraction is not None
    assert errors == []
    assert reasoner.validate_typed_extraction(extraction, note_text=_record().note_text) == []

    adapted = reasoner.mechanical_adapter_label(extraction)

    assert adapted.final_label == "3 per 6 week"
    assert adapted.adapter_families == ("arithmetic_from_selected_operands",)
    assert adapted.operand_complete is True


def test_run_split_reports_primary_mechanical_adapter_layer(monkeypatch) -> None:
    class StubProgram:
        def __call__(self, **kwargs):
            return _prediction("multiple per week")

    monkeypatch.setattr(reasoner, "DspyLlmHeavyEvidenceSelectionReasoner", StubProgram)
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
    assert metadata["claim_type"] == "llm_heavy_clinical_selection_with_deterministic_adapters"
    assert metadata["primary_score_layer"] == "mechanical_adapter_label"
    assert metadata["dspy_adapter"] == "JSONAdapter"
    assert metadata["typed_output_schema_version"] == reasoner.TYPED_OUTPUT_SCHEMA_VERSION
    assert metadata["summary"]["structured_records"] == 1
    assert metadata["summary"]["operand_complete_rows"] == 1
    assert metadata["summary"]["selected_fact_trace_mismatches"] == 0
    assert rows[0]["pipeline_family"] == reasoner.PIPELINE_FAMILY
    assert rows[0]["score_layers"]["raw_model_parser_label"]["final_label"] == "multiple per week"
    assert rows[0]["score_layers"]["mechanical_adapter_label"]["final_label"] == "3 per 6 week"
    assert rows[0]["mechanical_adapter"]["adapter_families"] == [
        "arithmetic_from_selected_operands"
    ]


def test_write_report_records_decision_0007_validation25_gate(tmp_path: Path) -> None:
    rows, metadata = reasoner.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1800,
        mode="prompt-only",
    )
    report = tmp_path / "llm_heavy_decision_0007.md"
    reasoner.write_report(rows, metadata, report, jsonl_path=tmp_path / "rows.jsonl")

    text = report.read_text(encoding="utf-8")
    assert "LLM-heavy clinical selection with deterministic mechanical adapters" in text
    assert "Surface: `validation25` under `gan2026_split_v1`" in text
    assert "Primary adapted layer: `mechanical_adapter_label`" in text
