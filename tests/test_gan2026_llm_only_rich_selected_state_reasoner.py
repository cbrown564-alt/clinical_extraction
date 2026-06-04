from __future__ import annotations

from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_rich_selected_state_reasoner as reasoner,
)


def _record(note_text: str = "Current diary: multiple seizures in past day.") -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=42,
        note_text=note_text,
        gold_label="multiple per day",
        gold_reference="multiple seizures in past day",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="multiple per day",
        gold_label_kind=FrequencyLabelKind.UNRESOLVED_MULTIPLE,
        gold_yearly_bounds=(-1.0, -1.0),
        gold_monthly_frequency=1000.0,
    )


def _prediction(**updates) -> SimpleNamespace:
    selected_state = {
        "state_kind": "unresolved_multiple",
        "selected_evidence": "multiple seizures in past day",
        "raw_source_phrase": "multiple seizures in past day",
        "currentness": "recent",
        "assertion_status": "asserted",
        "applies_to": "seizures",
        "rate": {
            "count_low": None,
            "count_high": None,
            "count_is_upper_bound": False,
            "count_is_multiple": True,
            "time_count_low": 1,
            "time_count_high": None,
            "time_unit": "day",
            "rate_time_basis_known": True,
            "rate_text": "multiple seizures in past day",
        },
        "cluster": {
            "has_cluster_pattern": False,
            "cluster_cadence_known": False,
            "cluster_cadence_text": "",
            "seizures_per_cluster_low": None,
            "seizures_per_cluster_high": None,
            "cluster_uncertainty": "",
        },
        "seizure_free_boundary": {
            "has_no_event_claim": False,
            "duration_count": None,
            "duration_unit": None,
            "applies_to_all_seizure_types": False,
            "has_recent_events_or_conditions": False,
            "boundary_note": "",
        },
        "conditionality_note": "",
        "ambiguity_flags": [],
        "competing_state_summary": "",
        "selection_reason": "The note states multiple recent seizures.",
        "raw_model_label_hint": "",
    }
    selected_state.update(updates)
    return SimpleNamespace(selected_state=selected_state)


def test_build_rich_selected_state_inputs_keeps_gold_and_metadata_out() -> None:
    inputs = reasoner.build_rich_selected_state_inputs(_record())

    assert inputs["note_text"] == _record().note_text
    assert "gold" not in str(inputs).lower()
    assert "pipeline_family" not in str(inputs)
    assert inputs["output_contract"]["top_level_outputs"] == ["selected_state"]
    assert "conditionality_note" in inputs["output_contract"]["selected_state_fields"]
    assert inputs["output_contract"]["field_descriptions"]["cluster"]


def test_multiple_per_day_renders_from_typed_multiple_state() -> None:
    extraction, errors = reasoner.prediction_to_extraction(
        _prediction(),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert errors == []
    assert reasoner.validate_rich_selected_state(extraction, note_text=_record().note_text) == []
    assert reasoner.deterministic_project_selected_state(extraction) == "multiple per day"


def test_conditional_events_render_unknown_not_seizure_free() -> None:
    note = (
        "Generalised tonic-clonic seizures occur only after nights of curtailed sleep. "
        "No events are reported when sleep has been adequate."
    )
    prediction = _prediction(
        state_kind="unknown",
        selected_evidence="Generalised tonic-clonic seizures occur only after nights of curtailed sleep",
        raw_source_phrase="seizures occur only after nights of curtailed sleep",
        currentness="conditional",
        rate={
            **_prediction().selected_state["rate"],
            "count_is_multiple": False,
            "time_count_low": None,
            "time_unit": None,
            "rate_time_basis_known": False,
        },
        conditionality_note="Events occur only after curtailed sleep.",
        ambiguity_flags=["conditional events block a seizure-free answer"],
    )
    extraction, _errors = reasoner.prediction_to_extraction(prediction, note_text=note)

    assert extraction is not None
    assert reasoner.validate_rich_selected_state(extraction, note_text=note) == []
    assert reasoner.deterministic_project_selected_state(extraction) == "unknown"


def test_cluster_burden_without_cadence_renders_unknown_per_cluster() -> None:
    note = (
        "Episodes come in small runs: typically around four to six short spells "
        "grouped together on days when they occur."
    )
    prediction = _prediction(
        state_kind="unknown",
        selected_evidence="typically around four to six short spells grouped together",
        raw_source_phrase="four to six short spells grouped together",
        currentness="current",
        rate={
            **_prediction().selected_state["rate"],
            "count_is_multiple": False,
            "time_count_low": None,
            "time_unit": None,
            "rate_time_basis_known": False,
        },
        cluster={
            "has_cluster_pattern": True,
            "cluster_cadence_known": False,
            "cluster_cadence_text": "",
            "seizures_per_cluster_low": 4,
            "seizures_per_cluster_high": 6,
            "cluster_uncertainty": "The note does not say how often clusters occur.",
        },
    )
    extraction, _errors = reasoner.prediction_to_extraction(prediction, note_text=note)

    assert extraction is not None
    assert reasoner.validate_rich_selected_state(extraction, note_text=note) == []
    assert reasoner.deterministic_project_selected_state(extraction) == (
        "unknown, 4 to 6 per cluster"
    )


def test_seizure_free_with_recent_events_is_validation_error_and_renders_unknown() -> None:
    note = "No events when sleep is adequate, but seizures occur after curtailed sleep."
    prediction = _prediction(
        state_kind="seizure_free",
        selected_evidence="No events when sleep is adequate",
        raw_source_phrase="No events when sleep is adequate",
        currentness="conditional",
        seizure_free_boundary={
            "has_no_event_claim": True,
            "duration_count": None,
            "duration_unit": None,
            "applies_to_all_seizure_types": False,
            "has_recent_events_or_conditions": True,
            "boundary_note": "No-event claim is conditional.",
        },
        conditionality_note="No events only when sleep is adequate.",
    )
    extraction, _errors = reasoner.prediction_to_extraction(prediction, note_text=note)

    assert extraction is not None
    assert reasoner.validate_rich_selected_state(extraction, note_text=note) == [
        "boundary: seizure_free state has recent events or conditions"
    ]
    assert reasoner.deterministic_project_selected_state(extraction) == "unknown"


def test_current_monthly_summary_renders_one_per_month() -> None:
    note = "At present, his typical pattern is a focal seizure monthly."
    prediction = _prediction(
        state_kind="frequency",
        selected_evidence="At present, his typical pattern is a focal seizure monthly",
        raw_source_phrase="a focal seizure monthly",
        currentness="current",
        rate={
            **_prediction().selected_state["rate"],
            "count_low": 1,
            "count_is_multiple": False,
            "time_count_low": 1,
            "time_unit": "month",
            "rate_time_basis_known": True,
            "rate_text": "a focal seizure monthly",
        },
        raw_model_label_hint="",
    )
    extraction, _errors = reasoner.prediction_to_extraction(prediction, note_text=note)

    assert extraction is not None
    assert reasoner.validate_rich_selected_state(extraction, note_text=note) == []
    assert reasoner.deterministic_project_selected_state(extraction) == "1 per month"
