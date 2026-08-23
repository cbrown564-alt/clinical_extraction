"""Invariant-focused tests for gan2026 hybrid structured events contract."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    DEFAULT_SEMANTIC_FAMILY_ORDER,
    GAN_LLM_WITH_RULES,
    LLM_WITH_RULES_AUTHORED_KEYS,
    PROMPT_VERSION,
    StructuredExtractionRecord,
    StructuredRepairConfig,
    adjacent_semantic_family_orders,
    build_prompt_input,
    load_reusable_raw_outputs,
    parse_structured_json,
    parse_structured_json_with_trace,
    run_split,
    summarize_records,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    dated_sequence_label_from_events,
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

    assert PROMPT_VERSION == GAN_LLM_WITH_RULES == "gan_llm_extract_raw"
    assert set(prompt) == set(LLM_WITH_RULES_AUTHORED_KEYS)
    assert "prompt_version" not in prompt
    assert "source_row_index" not in prompt
    assert "Gan 2026" not in blob
    assert "LLM-only" not in blob
    assert prompt["note_text"] == _record().note_text
    assert "gold_label" not in blob
    assert "candidate_events" not in prompt
    assert "deterministic_final_selection" not in prompt


@pytest.mark.parametrize(
    "version",
    (
        "gan2026_hybrid_structured_events_v0.5",
        "gan2026_hybrid_structured_events_final",
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


def test_parse_keeps_written_label_when_selected_event_ids_are_omitted() -> None:
    payload = json.loads(_raw_structured("unknown"))
    del payload["selection"]["selected_event_ids"]
    extraction, _, errors = parse_structured_json(
        json.dumps(payload),
        note_text=_record().note_text,
        repair_config=StructuredRepairConfig.for_mode("raw_model"),
    )

    assert extraction is not None
    assert extraction.selection.selected_event_ids == []
    assert extraction.selection.final_label == "unknown"
    assert not any(str(error).startswith("schema_validation_error:") for error in errors)


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


def test_extract_keeps_model_label_and_encode_owns_resolve() -> None:
    raw = _raw_structured(None)
    extract, extract_norm, _, extract_trace = parse_structured_json_with_trace(
        raw,
        note_text=_record().note_text,
        repair_config=StructuredRepairConfig.for_mode("raw_model"),
    )
    encoded, encoded_norm, _, encode_trace = parse_structured_json_with_trace(
        raw,
        note_text=_record().note_text,
        repair_config=StructuredRepairConfig.for_mode("llm_encode"),
    )

    assert extract is not None
    assert extract.selection.final_label is None
    assert extract_norm == []
    assert encoded is not None
    assert encoded.selection.final_label == "2 per month"
    assert encoded_norm[0].normalized_label == "2 per month"
    resolve_hops = [
        hop
        for hop in encode_trace["answer_states"]
        if hop["stage_id"] == "gan.encode.resolve_label"
    ]
    assert resolve_hops
    assert resolve_hops[0]["cell_id"] == "llm_encode"
    assert resolve_hops[0]["effect_class"] == "encode"
    assert not any(
        hop["stage_id"] == "gan.encode.resolve_label"
        for hop in extract_trace["answer_states"]
    )


def test_llm_select_after_codebook_keeps_select_and_named_encode() -> None:
    after = StructuredRepairConfig.for_mode("llm_select_after_codebook")
    living = StructuredRepairConfig.for_mode("llm_select")
    codebook = StructuredRepairConfig.for_mode("gan_rules_encode")
    assert after.encode_enabled() is True
    assert after.select_enabled() is True
    assert after.codebook_label_repair is True
    assert after.selected_evidence_repair is False
    assert after.basic_label_repair is False
    assert after.resolved_repair_mode == "llm_select_after_codebook"
    assert after.residual_jerk_repair is living.residual_jerk_repair
    assert after.elapsed_anchor_repair is living.elapsed_anchor_repair
    assert after.monthly_diary_repair is living.monthly_diary_repair
    assert codebook.select_enabled() is False


def test_llm_select_only_keeps_select_families_and_drops_encode() -> None:
    only = StructuredRepairConfig.for_mode("llm_select_only")
    living = StructuredRepairConfig.for_mode("llm_select")
    assert only.encode_enabled() is False
    assert only.select_enabled() is True
    assert only.basic_label_repair is False
    assert only.selected_evidence_repair is False
    assert only.resolved_repair_mode == "llm_select_only"
    assert only.residual_jerk_repair is living.residual_jerk_repair
    assert only.elapsed_anchor_repair is living.elapsed_anchor_repair
    assert only.dated_sequence_repair is living.dated_sequence_repair
    assert only.usual_interval_repair is living.usual_interval_repair


def test_living_hybrid_select_drops_jerk_and_elapsed() -> None:
    living = StructuredRepairConfig.for_mode("llm_select")
    assert living.residual_jerk_repair is False
    assert living.elapsed_anchor_repair is False
    assert living.dated_sequence_repair is True
    assert living.post_change_burst_repair is True


def test_dated_sequence_does_not_mine_dates_from_the_letter() -> None:
    extraction = SimpleNamespace(
        events=[
            SimpleNamespace(
                evidence="frequency is unclear",
                raw_value="",
                time_window="",
            )
        ]
    )
    note = (
        "Clinic Date: 1 June 2024\n"
        "She had a seizure in March 2024 and another seizure in May 2024."
    )
    assert (
        dated_sequence_label_from_events(extraction, "unknown", note_text=note) is None
    )


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

    living, _, _ = parse_structured_json(raw, note_text=note)
    extraction, _, errors = parse_structured_json(
        raw,
        note_text=note,
        repair_config=StructuredRepairConfig(
            residual_jerk_repair=False,
            elapsed_anchor_repair=True,
        ),
    )

    assert living is not None
    assert living.selection.final_label != "seizure free for 6 month"
    assert extraction is not None
    assert extraction.selection.final_label == "seizure free for 6 month"
    assert any(
        "seizure free for 6 month" in str(error) and "final_label_repaired" in str(error)
        for error in errors
    )


def test_elapsed_seizure_free_is_not_replaced_by_a_short_diary() -> None:
    """Sustained dated freedom stays after a later countable diary.

    Family: monthly_diary after elapsed_anchor. Portability: seizure_frequency.
    """
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
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "2",
                    "applies_to": "seizures",
                    "time_window": "January 2024",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "2 in January",
                    "notes": None,
                },
                {
                    "event_id": "e3",
                    "kind": "frequency_rate",
                    "raw_value": "1",
                    "applies_to": "seizures",
                    "time_window": "February 2024",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "1 in February",
                    "notes": None,
                },
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
        "Seizure-free since 27 March 2024 as per patient and collateral reports. "
        "2 in January. 1 in February."
    )

    living, _, _ = parse_structured_json(raw, note_text=note)
    extraction, _, _errors = parse_structured_json(
        raw,
        note_text=note,
        repair_config=StructuredRepairConfig(
            residual_jerk_repair=False,
            elapsed_anchor_repair=True,
        ),
    )

    assert living is not None
    assert living.selection.final_label == "3 per 2 month"
    assert extraction is not None
    assert extraction.selection.final_label == "seizure free for 6 month"


def test_default_semantic_order_puts_diary_after_elapsed_anchor() -> None:
    """Diary after elapsed-anchor is the measured default.

    Family: semantic family order. Portability: seizure_frequency.
    """
    assert DEFAULT_SEMANTIC_FAMILY_ORDER[-2:] == (
        "elapsed_anchor",
        "monthly_diary",
    )
    swaps = adjacent_semantic_family_orders()
    assert ("elapsed_anchor", "monthly_diary") in {
        pair for pair, _order in swaps
    }
    diary_first = next(
        order for pair, order in swaps if pair == ("elapsed_anchor", "monthly_diary")
    )
    assert diary_first[-2:] == ("monthly_diary", "elapsed_anchor")


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


def test_parse_structured_json_fills_omitted_kind_on_selected_sibling_event() -> None:
    payload = json.loads(_raw_structured())
    typed = dict(payload["events"][0])
    typed["event_id"] = "e1"
    typed["kind"] = "frequency_rate"
    omitted = dict(payload["events"][0])
    omitted["event_id"] = "e2"
    omitted.pop("kind")
    payload["events"] = [typed, omitted]
    payload["selection"]["selected_event_ids"] = ["e1", "e2"]

    extraction, _, errors = parse_structured_json(json.dumps(payload))

    assert extraction is not None
    assert [event.kind for event in extraction.events] == [
        "frequency_rate",
        "frequency_rate",
    ]
    assert extraction.selection.final_label == "2 per month"
    assert errors == []


def test_vague_seizure_free_does_not_veto_countable_monthly_diary() -> None:
    """Allow a countable diary to replace inflated 'seizure free for multiple'.

    Family: monthly_diary. Portability: seizure_frequency.
    """
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "seizure_free",
                    "raw_value": "no seizures",
                    "applies_to": "seizures",
                    "time_window": "this month so far",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "This month so far she has no seizures",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "4",
                    "applies_to": "seizures",
                    "time_window": "February",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "earlier 4 in February",
                    "notes": None,
                },
                {
                    "event_id": "e3",
                    "kind": "frequency_rate",
                    "raw_value": "7",
                    "applies_to": "seizures",
                    "time_window": "December",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "7 in December",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "seizure_free",
                "final_label": "seizure free this month so far",
                "evidence": "This month so far she has no seizures",
                "confidence": "high",
                "rationale": "The current month is seizure-free so far.",
            },
        }
    )
    note = (
        "Clinic Date: 15 March 2025\n"
        "This month so far she has no seizures. Earlier 4 in February and 7 in December."
    )

    extraction, _, _errors = parse_structured_json(raw, note_text=note)

    assert extraction is not None
    assert extraction.selection.final_label == "11 per 3 month"


def test_week_scale_rate_still_blocks_monthly_diary() -> None:
    """Keep a parsable week-scale selection against a multi-month diary sum.

    Family: monthly_diary. Portability: seizure_frequency.
    """
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "2 per week",
                    "applies_to": "seizures",
                    "time_window": "over the past month",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "overall frequency has been twice per week",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "5",
                    "applies_to": "seizures",
                    "time_window": "June",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "In June: five events during sleep",
                    "notes": None,
                },
                {
                    "event_id": "e3",
                    "kind": "frequency_rate",
                    "raw_value": "1",
                    "applies_to": "seizures",
                    "time_window": "August",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "In August: one while awake",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "2 per week",
                "evidence": "overall frequency has been twice per week",
                "confidence": "high",
                "rationale": "The current rate is twice per week.",
            },
        }
    )

    extraction, _, _errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "2 per week"


def test_month_x_count_log_keeps_the_multi_month_span() -> None:
    """A Month-x-N trend is a span sum unless rules see an increasing-lead-in.

    Family: monthly_diary. Portability: seizure_frequency.
    """
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "3",
                    "applies_to": "seizures",
                    "time_window": "July 2025",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "July x 3 focal aware motor",
                    "notes": "Three focal aware motor seizures in July.",
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "4",
                    "applies_to": "seizures",
                    "time_window": "August 2025",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "August x 4 focal aware motor",
                    "notes": "Four focal aware motor seizures in August.",
                },
                {
                    "event_id": "e3",
                    "kind": "frequency_rate",
                    "raw_value": "5",
                    "applies_to": "seizures",
                    "time_window": "September 2025",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "September x 5 focal aware motor",
                    "notes": "Five focal aware motor seizures in September.",
                },
            ],
            "selection": {
                "selected_event_ids": ["e3"],
                "final_kind": "frequency",
                "final_label": "5 per month",
                "evidence": "September x 5 focal aware motor",
                "confidence": "high",
                "rationale": "The latest complete month is September x 5.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "12 per 3 month"
    assert any("12 per 3 month" in str(error) for error in errors)


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


def test_summarize_records_counts_predicted_candidates() -> None:
    rows = [
        {
            "structured_record": {
                "events": [{"event_id": "e1"}, {"event_id": "e2"}],
                "selection": {"final_label": "2 per month"},
            },
            "comparison": {"purist_correct": True, "pragmatic_correct": True},
        },
        {
            "encoded_events": [{"event_id": "e1"}, {"event_id": "e2"}, {"event_id": "e3"}],
            "structured_record": {
                "events": [{"event_id": "e1"}],
                "selection": {"final_label": "unknown"},
            },
            "comparison": {"purist_correct": False, "pragmatic_correct": False},
        },
    ]

    summary = summarize_records(rows)

    assert summary["predicted_candidate_count"] == 5
