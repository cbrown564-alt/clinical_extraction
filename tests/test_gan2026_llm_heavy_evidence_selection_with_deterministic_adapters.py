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


def _cluster_cadence_prediction() -> SimpleNamespace:
    return SimpleNamespace(
        selected_fact={
            "fact_id": "cluster-1",
            "clinical_kind": "cluster_frequency",
            "applies_to": "absence episodes",
            "evidence": "clusters of brief absence episodes every 4 weeks",
            "raw_value": "clusters of brief absence episodes every 4 weeks",
            "temporality": "current",
            "assertion_status": "asserted",
            "competing_fact_summary": "",
            "rationale": "The selected answer is the cadence of clusters.",
            "benchmark_caveat_flags": ["cluster_axis"],
        },
        operands={
            "frequency": None,
            "cluster": {
                "clusters_low": 1,
                "clusters_high": 1,
                "cluster_period_low": 4,
                "cluster_period_high": 4,
                "cluster_period_unit": "week",
                "events_per_cluster_low": None,
                "events_per_cluster_high": None,
                "cluster_answer_axis": "cluster_cadence",
            },
            "seizure_free": None,
        },
        raw_model_answer={
            "raw_model_parser_label": "1 per 4 week",
            "raw_model_final_kind": "cluster_frequency",
            "selected_evidence": "clusters of brief absence episodes every 4 weeks",
            "confidence": "high",
            "clinical_rationale": "The note states the cadence directly.",
        },
    )


def test_build_typed_inputs_exposes_decision_0007_contract() -> None:
    inputs = reasoner.build_typed_inputs(_record())
    instructions = " ".join(inputs["task_instructions"])
    contract = inputs["output_contract"]

    assert inputs["note_text"] == _record().note_text
    assert contract["pipeline_family"] == reasoner.PIPELINE_FAMILY
    assert contract["prompt_version"].endswith("_v1")
    assert contract["typed_output_schema_version"] == reasoner.TYPED_OUTPUT_SCHEMA_VERSION
    assert contract["typed_output_schema_version"] == "selected_fact_operands_v1"
    assert contract["top_level_outputs"] == [
        "selected_fact",
        "operands",
        "raw_model_answer",
    ]
    assert "model selects the clinical fact" in instructions
    assert "Unicode inequality symbols" in instructions
    assert "HTML entities" in instructions
    assert "occurrences_high" in instructions
    assert "full upper-bound statement exactly" in instructions
    assert "no prefixes, underscores, plural units" in instructions
    assert contract["raw_parser_label_grammar"]["frequency"] == (
        "N per D unit or N to M per D to E unit"
    )
    assert "multiple per unit" in contract["raw_parser_label_grammar"]["vague_frequency"]
    assert contract["evidence_copy_contract"]["preserve_unicode"] is True
    assert contract["upper_bound_contract"]["evidence_required"] is True
    assert "≤" in contract["upper_bound_contract"]["allowed_cues"]
    assert "occurrences_high without occurrences_low" in contract["upper_bound_contract"][
        "operand_rule"
    ]
    assert contract["clinical_kind_operand_consistency"]["frequency"] == (
        "total seizure burden, even when the note mentions clustering"
    )
    assert "gold_label" not in str(inputs)
    assert "candidate_events" not in str(inputs)


def test_default_artifact_paths_are_v1_contract_outputs() -> None:
    assert "gpt41mini_v1" in str(reasoner.DEFAULT_JSONL_PATH)
    assert "gpt41mini_v1" in str(reasoner.DEFAULT_REPORT_PATH)


def test_mechanical_adapter_renders_from_selected_frequency_operands() -> None:
    extraction, errors = reasoner.prediction_to_extraction(_prediction())

    assert extraction is not None
    assert errors == []
    assert reasoner.validate_typed_extraction(extraction, note_text=_record().note_text) == []

    adapted = reasoner.mechanical_adapter_label(extraction)

    assert adapted.final_label == "3 per 6 week"
    assert adapted.adapter_families == ("arithmetic_from_selected_operands",)
    assert adapted.operand_complete is True


def test_mechanical_adapter_renders_upper_bound_high_operand_with_bound_evidence() -> None:
    prediction = _prediction("2 per week")
    prediction.selected_fact["evidence"] = "the overall frequency has been ≤ twice per week"
    prediction.selected_fact["raw_value"] = "≤ twice per week"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    prediction.operands["frequency"] = {
        "occurrences_low": None,
        "occurrences_high": 2,
        "denominator_low": 1,
        "denominator_high": 1,
        "denominator_unit": "week",
        "vague_count": None,
    }
    extraction, errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert errors == []

    adapted = reasoner.mechanical_adapter_label(extraction)

    assert adapted.final_label == "2 per 1 week"
    assert adapted.adapter_families == ("upper_bound_from_selected_operands",)
    assert adapted.operand_complete is True


def test_mechanical_adapter_rejects_high_only_operand_without_bound_evidence() -> None:
    prediction = _prediction("2 per week")
    prediction.selected_fact["evidence"] = "the overall frequency was discussed per week"
    prediction.selected_fact["raw_value"] = "2 per week"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    prediction.operands["frequency"] = {
        "occurrences_low": None,
        "occurrences_high": 2,
        "denominator_low": 1,
        "denominator_high": 1,
        "denominator_unit": "week",
        "vague_count": None,
    }
    extraction, errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert errors == []

    adapted = reasoner.mechanical_adapter_label(extraction)

    assert adapted.final_label is None
    assert adapted.error == "incomplete_frequency_operands"
    assert adapted.operand_complete is False


def test_prediction_to_extraction_repairs_source_checked_unicode_evidence_copy() -> None:
    prediction = _prediction("4 per day")
    prediction.selected_fact["evidence"] = (
        "On the accommodation logs, the observed frequency is noted as \x0264 four "
        "per day, with variable clustering."
    )
    prediction.selected_fact["raw_value"] = "\x0264 four per day"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    note_text = (
        "On the accommodation logs, the observed frequency is noted as ≤ four "
        "per day, with variable clustering."
    )

    extraction, errors = reasoner.prediction_to_extraction(
        prediction,
        note_text=note_text,
    )

    assert errors == []
    assert extraction is not None
    assert extraction.selected_fact.evidence == (
        "On the accommodation logs, the observed frequency is noted as ≤ four "
        "per day, with variable clustering."
    )
    assert reasoner.validate_typed_extraction(extraction, note_text=note_text) == []


def test_prediction_to_extraction_repairs_numeric_entity_inequality_artifact() -> None:
    prediction = _prediction("1 per month")
    prediction.selected_fact["evidence"] = "events have reduced to \x026#8804; once per month"
    prediction.selected_fact["raw_value"] = "\x026#8804; once per month"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    note_text = "events have reduced to ≤ once per month"

    extraction, errors = reasoner.prediction_to_extraction(
        prediction,
        note_text=note_text,
    )

    assert errors == []
    assert extraction is not None
    assert extraction.selected_fact.evidence == "events have reduced to ≤ once per month"
    assert reasoner.validate_typed_extraction(extraction, note_text=note_text) == []


def test_prediction_to_extraction_repairs_case_only_evidence_copy() -> None:
    prediction = _prediction("1 per year")
    prediction.selected_fact["evidence"] = "she reports yearly seizures"
    prediction.raw_model_answer["selected_evidence"] = "she reports yearly seizures"

    extraction, errors = reasoner.prediction_to_extraction(
        prediction,
        note_text="She reports yearly seizures",
    )

    assert errors == []
    assert extraction is not None
    assert extraction.selected_fact.evidence == "She reports yearly seizures"
    assert extraction.raw_model_answer.selected_evidence == "She reports yearly seizures"


def test_prediction_to_extraction_leaves_unmatched_evidence_copy_artifact_invalid() -> None:
    prediction = _prediction("4 per day")
    prediction.selected_fact["evidence"] = "frequency is \x0264 four per day"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]

    extraction, errors = reasoner.prediction_to_extraction(
        prediction,
        note_text="frequency is fewer than four per day",
    )

    assert errors == []
    assert extraction is not None
    assert reasoner.validate_typed_extraction(extraction, note_text="other text") == [
        "evidence: invalid selected_fact evidence",
        "evidence: invalid raw_model_answer selected evidence",
    ]


def test_cluster_cadence_adapter_renders_bare_frequency_axis() -> None:
    extraction, errors = reasoner.prediction_to_extraction(_cluster_cadence_prediction())

    assert extraction is not None
    assert errors == []

    adapted = reasoner.mechanical_adapter_label(extraction)

    assert adapted.final_label == "1 per 4 week"
    assert adapted.adapter_families == ("cluster_cadence_rendering",)
    assert adapted.operand_complete is True


def test_final_projection_falls_back_to_raw_label_when_operands_incomplete() -> None:
    prediction = _prediction("multiple per shift")
    prediction.selected_fact["evidence"] = (
        "Daniel Harris reports that these episodes crop up most shifts, especially "
        "during the busiest part of service."
    )
    prediction.selected_fact["raw_value"] = "most shifts"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    prediction.operands["frequency"] = {
        "occurrences_low": None,
        "occurrences_high": None,
        "denominator_low": None,
        "denominator_high": None,
        "denominator_unit": None,
        "vague_count": "multiple",
    }
    extraction, errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert errors == []

    mechanical = reasoner.mechanical_adapter_label(extraction)
    projected = reasoner.final_projected_label(
        extraction,
        mechanical,
        context_text="Daniel Harris reports that these episodes crop up most shifts.",
    )

    assert mechanical.final_label is None
    assert projected.final_label == "multiple per shift"
    assert projected.projection_families == ("raw_label_fallback",)


def test_final_projection_repairs_bimonthly_from_selected_evidence() -> None:
    prediction = _prediction("2 per 1 month")
    prediction.selected_fact["evidence"] = "This patient reports bimonthly seizures."
    prediction.selected_fact["raw_value"] = "bimonthly seizures"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    prediction.operands["frequency"] = {
        "occurrences_low": 2,
        "occurrences_high": 2,
        "denominator_low": 1,
        "denominator_high": 1,
        "denominator_unit": "month",
        "vague_count": None,
    }
    extraction, errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert errors == []

    projected = reasoner.final_projected_label(
        extraction,
        reasoner.mechanical_adapter_label(extraction),
    )

    assert projected.final_label == "1 per 2 month"
    assert projected.projection_families == ("selected_evidence_projection",)


def test_final_projection_repairs_every_other_day_from_selected_evidence() -> None:
    prediction = _prediction("3 to 4 per 6 week")
    prediction.selected_fact["evidence"] = (
        "These have become frequent, with seizures every other day."
    )
    prediction.selected_fact["raw_value"] = "1 per 2 days"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    prediction.operands["frequency"] = {
        "occurrences_low": 3,
        "occurrences_high": 4,
        "denominator_low": 6,
        "denominator_high": 6,
        "denominator_unit": "week",
        "vague_count": None,
    }
    extraction, errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert errors == []

    projected = reasoner.final_projected_label(
        extraction,
        reasoner.mechanical_adapter_label(extraction),
    )

    assert projected.final_label == "1 per 2 day"
    assert projected.projection_families == ("selected_evidence_projection",)


def test_final_projection_prefers_current_monthly_state_over_year_to_date_count() -> None:
    prediction = _prediction("4 per 1 year")
    prediction.selected_fact["evidence"] = (
        "Currently reporting monthly seizures, typically brief focal-onset episodes "
        "with rapid recovery as described by the family. Since commencing ketogenic "
        "diet therapy, the family notes a marked reduction in seizure frequency with "
        "only four brief seizures recorded in 2017 so far."
    )
    prediction.selected_fact["raw_value"] = "4 per year"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    prediction.operands["frequency"] = {
        "occurrences_low": 4,
        "occurrences_high": 4,
        "denominator_low": 1,
        "denominator_high": 1,
        "denominator_unit": "year",
        "vague_count": None,
    }
    extraction, errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert errors == []

    projected = reasoner.final_projected_label(
        extraction,
        reasoner.mechanical_adapter_label(extraction),
    )

    assert projected.final_label == "1 per month"
    assert projected.projection_families == ("selected_evidence_projection",)


def test_final_projection_applies_vague_weekday_benchmark_policy() -> None:
    prediction = _prediction("3 to 5 per 7 day")
    prediction.selected_fact["evidence"] = (
        "Over the past two months she reports brief absences occurring on most "
        "weekdays, often clustering around late afternoon."
    )
    prediction.selected_fact["raw_value"] = "most weekdays"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    prediction.operands["frequency"] = {
        "occurrences_low": 3,
        "occurrences_high": 5,
        "denominator_low": 7,
        "denominator_high": 7,
        "denominator_unit": "day",
        "vague_count": None,
    }
    extraction, errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert errors == []

    projected = reasoner.final_projected_label(
        extraction,
        reasoner.mechanical_adapter_label(extraction),
    )

    assert projected.final_label == "multiple per week"
    assert projected.projection_families == ("selected_evidence_vague_weekday_policy",)


def test_final_projection_prefers_stabilised_current_rate_over_prior_rate() -> None:
    prediction = _prediction("1 per 3 week")
    prediction.selected_fact["evidence"] = (
        "Prior to these changes, seizures occurred once every two to three days. "
        "Over the past three months, they have stabilised at seizures every 3 weeks "
        "by the patient’s report."
    )
    prediction.selected_fact["raw_value"] = "1 seizure every 3 weeks"
    prediction.raw_model_answer["selected_evidence"] = prediction.selected_fact["evidence"]
    prediction.operands["frequency"] = {
        "occurrences_low": 1,
        "occurrences_high": 1,
        "denominator_low": 3,
        "denominator_high": 3,
        "denominator_unit": "week",
        "vague_count": None,
    }
    extraction, errors = reasoner.prediction_to_extraction(prediction)

    assert extraction is not None
    assert errors == []

    projected = reasoner.final_projected_label(
        extraction,
        reasoner.mechanical_adapter_label(extraction),
    )

    assert projected.final_label == "1 per 3 week"


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
    assert metadata["primary_score_layer"] == "final_projected_label"
    assert metadata["dspy_adapter"] == "JSONAdapter"
    assert metadata["typed_output_schema_version"] == reasoner.TYPED_OUTPUT_SCHEMA_VERSION
    assert metadata["summary"]["structured_records"] == 1
    assert metadata["summary"]["operand_complete_rows"] == 1
    assert metadata["summary"]["selected_fact_trace_mismatches"] == 0
    assert rows[0]["pipeline_family"] == reasoner.PIPELINE_FAMILY
    assert rows[0]["score_layers"]["raw_model_parser_label"]["final_label"] == "multiple per week"
    assert rows[0]["score_layers"]["mechanical_adapter_label"]["final_label"] == "3 per 6 week"
    assert rows[0]["score_layers"]["final_projected_label"]["final_label"] == "3 per 6 week"
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
    assert "Primary score layer: `final_projected_label`" in text
