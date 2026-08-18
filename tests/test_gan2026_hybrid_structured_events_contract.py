"""Invariant-focused tests for gan2026 hybrid structured events contract."""

import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    GAN_LLM_WITH_RULES,
    LLM_WITH_RULES_AUTHORED_KEYS,
    PROMPT_VERSION,
    PROMPT_VERSION_FINAL,
    PROMPT_VERSION_V0_5,
    StructuredExtractionRecord,
    StructuredRepairConfig,
    build_prompt_input,
    load_reusable_raw_outputs,
    parse_structured_json,
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


def _raw_structured(final_label: str | None = "2 per month") -> str:
    return json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency",
                    "raw_value": "two seizures per month",
                    "applies_to": "seizures",
                    "time_window": "present",
                    "temporality": "ongoing",
                    "assertion_status": "asserted",
                    "evidence": "two seizures per month",
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "current frequency",
                "final_label": final_label,
                "evidence": "two seizures per month",
                "confidence": 0.91,
                "rationale": "The note states the present seizure frequency.",
            },
        }
    )


def test_build_prompt_input_excludes_gold_and_deterministic_candidates() -> None:
    prompt = json.loads(build_prompt_input(_record()))
    blob = json.dumps(prompt)

    assert PROMPT_VERSION == GAN_LLM_WITH_RULES == "gan_llm_with_rules"
    assert set(prompt) == set(LLM_WITH_RULES_AUTHORED_KEYS)
    assert "prompt_version" not in prompt
    assert "source_row_index" not in prompt
    assert "Gan 2026" not in blob
    assert "LLM-only" not in blob
    assert prompt["note_text"] == _record().note_text
    assert "gold_label" not in blob
    assert "candidate_events" not in prompt
    assert "deterministic_final_selection" not in prompt


def test_build_prompt_input_final_alias_matches_paper_name() -> None:
    record = _record()
    default = json.loads(build_prompt_input(record))
    alias = json.loads(
        build_prompt_input(record, prompt_version=PROMPT_VERSION_FINAL)
    )

    assert PROMPT_VERSION_FINAL == "gan2026_hybrid_structured_events_final"
    assert default == alias
    assert default["task"] == (
        "Read the clinical note. Extract seizure-frequency facts as slim "
        "events, then select the current burden."
    )


def test_build_prompt_input_v05_keeps_historical_envelope() -> None:
    record = _record()
    prompt = json.loads(
        build_prompt_input(record, prompt_version=PROMPT_VERSION_V0_5)
    )

    assert prompt["prompt_version"] == PROMPT_VERSION_V0_5
    assert prompt["source_row_index"] == record.source_row_index
    assert prompt["instructions"] == json.loads(build_prompt_input(record))[
        "instructions"
    ]


@pytest.mark.parametrize(
    "version",
    (
        "gan2026_hybrid_structured_events_v0.6",
        "gan2026_hybrid_structured_events_v0.7",
        "gan2026_hybrid_structured_events_v0.8_luna_rate",
        "gan2026_hybrid_structured_events_v0.8_luna_current",
        "gan2026_hybrid_structured_events_v0.8_deepseek_unknown",
    ),
)
def test_build_prompt_input_rejects_deleted_study_versions(version: str) -> None:
    with pytest.raises(ValueError, match="unsupported prompt version"):
        build_prompt_input(_record(), prompt_version=version)


def test_parse_structured_json_quarantines_schema_invalid_unselected_event() -> None:
    payload = json.loads(_raw_structured())
    payload["events"].append(
        {
            "event_id": "bad",
            "kind": "invented_kind",
            "temporality": "historical",
            "assertion_status": "asserted",
            "evidence": "years ago",
        }
    )

    extraction, _, errors = parse_structured_json(json.dumps(payload))

    assert extraction is not None
    assert all(event.event_id != "bad" for event in extraction.events)
    assert "unselected_event_quarantined: bad" in errors


def test_parse_structured_json_rejects_schema_invalid_selected_event() -> None:
    payload = json.loads(_raw_structured())
    payload["events"][0]["kind"] = "invented_kind"

    extraction, _, errors = parse_structured_json(json.dumps(payload))

    assert extraction is None
    assert errors[-1].startswith("schema_validation_error:")


def test_parse_structured_json_can_compute_final_label_from_selected_event() -> None:
    extraction, normalized_events, errors = parse_structured_json(_raw_structured(None))

    assert extraction is not None
    assert extraction.selection.final_label == "2 per month"
    assert normalized_events[0].normalized_label == "2 per month"
    assert errors == []


def test_elapsed_anchor_converts_seizure_free_since_date_to_month_duration() -> None:
    evidence = (
        "Seizure-free since 27 March 2024 as per patient and collateral reports."
    )
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "seizure_free",
                    "raw_value": "seizure free since 27 March 2024",
                    "applies_to": "seizures",
                    "time_window": "since 27 March 2024",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": evidence,
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "seizure_free",
                "final_label": "seizure free since 27 March 2024",
                "evidence": evidence,
                "confidence": "high",
                "rationale": "The note states seizure freedom since 27 March 2024.",
            },
        }
    )
    note = (
        "Clinic Date: 29 September 2024\n"
        "Seizure-free since 27 March 2024 as per patient and collateral reports."
    )

    extraction, _, errors = parse_structured_json(raw, note_text=note)

    assert extraction is not None
    assert extraction.selection.final_label == "seizure free for 6 month"
    assert any(
        "seizure free for 6 month" in str(error) and "final_label_repaired" in str(error)
        for error in errors
    )


def test_run_split_reuses_raw_outputs_without_new_call(tmp_path: Path) -> None:
    reuse_path = tmp_path / "prior.jsonl"
    reuse_path.write_text(
        json.dumps({"source_row_index": 10, "raw_output": _raw_structured()}) + "\n",
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
    )

    assert metadata["summary"]["structured_records"] == 1
    assert metadata["summary"]["reused_raw_outputs"] == 1
    assert rows[0]["reused_raw_output"] is True
    assert rows[0]["structured_record"]["selection"]["final_label"] == "2 per month"
    assert rows[0]["parse_errors"] == []


def test_parse_structured_json_can_use_clean_scorer_facing_gold_policy() -> None:
    raw = _raw_structured("most weekdays")

    extraction, _, errors = parse_structured_json(
        raw,
        repair_config=StructuredRepairConfig(
            selected_evidence_repair=False,
            basic_label_repair_format_only=True,
            clean_scorer_facing_gold_policy=True,
        ),
    )

    assert extraction is not None
    assert extraction.selection.final_label == "multiple per week"
    assert errors == ["final_label_repaired: 'most weekdays' -> 'multiple per week'"]


def test_parse_structured_json_repairs_schema_aliases_and_normalizes_selected_label() -> None:
    extraction, normalized_events, errors = parse_structured_json(_raw_structured())

    assert isinstance(extraction, StructuredExtractionRecord)
    assert extraction.events[0].kind == "frequency_rate"
    assert extraction.events[0].temporality == "current"
    assert extraction.selection.final_kind == "frequency"
    assert extraction.selection.confidence == "high"
    assert extraction.selection.final_label == "2 per month"
    assert normalized_events[0].normalized_label == "2 per month"
    assert errors == []
