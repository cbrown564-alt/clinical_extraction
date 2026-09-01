"""Projection and parse contract for Gan later-stage encode and select."""

from __future__ import annotations

import json

import pytest

from clinical_extraction.paper.gan import verify_gan
from clinical_extraction.paper.gan_later_stage import (
    EXTRACT_METHOD,
    LLM_ENCODE_IS_EXTRACT,
    LLM_SELECT_METHOD,
    MAX_TOKENS,
    encode_work_rows_path,
    extract_rows_path,
    later_stage_work_root,
    parse_encode_labels,
    score_later_stage_row,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.select_from_extract import (
    extract_events_as_select_ledger,
    parse_extract_ledger,
    parse_select_answer,
    project_encode_label,
    project_select_label,
)


def test_encode_projects_the_extract_pick_label() -> None:
    assert (
        project_encode_label({"e1": "4 per day", "e2": "unknown"}, ["e1"]) == "4 per day"
    )


def test_select_uses_a_written_label_only_when_present() -> None:
    labels = {"e1": "4 per day", "e2": "1 per month"}
    assert project_select_label(labels, ["e2"], None) == "1 per month"
    assert project_select_label(labels, ["e1", "e2"], "2 per 6 month") == "2 per 6 month"


def test_parse_encode_and_select_payloads() -> None:
    assert parse_encode_labels(
        '{"labels": [{"event_id": "e1", "label": "4 per day"}]}'
    ) == [{"event_id": "e1", "label": "4 per day"}]
    assert parse_select_answer('{"selected_event_ids": ["e1"]}') == {
        "selected_event_ids": ["e1"]
    }
    assert parse_select_answer(
        '{"events": [], "selection": {"selected_event_ids": ["e2"], "label": "1 per month"}}'
    ) == {"selected_event_ids": ["e2"], "label": "1 per month"}


def test_later_stage_verify_is_gemini_only() -> None:
    assert verify_gan("gan_llm_encode", "dev750", "gemini37flash")["ok"] is True
    assert verify_gan("gan_llm_select", "dev750", "gemini37flash")["ok"] is True
    assert verify_gan("gan_llm_encode", "test450", "gemini37flash")["ok"] is True
    assert verify_gan("gan_llm_select", "test450", "gemini37flash")["row_policy"] == (
        "aggregate_only"
    )
    with pytest.raises(RuntimeError, match="Gemini only"):
        verify_gan("gan_llm_encode", "dev750", "grok46")


def test_later_stage_holdout_cells_use_scratch() -> None:
    assert MAX_TOKENS == 8000
    encode_dev = encode_work_rows_path("dev750")
    encode_holdout = encode_work_rows_path("test450")
    assert "experiments/paper" in encode_dev.as_posix()
    assert EXTRACT_METHOD in encode_dev.as_posix()
    assert "scratch/holdout/paper" in encode_holdout.as_posix()
    assert "scratch/holdout/paper" in later_stage_work_root(
        "gan_llm_select", "gemini37flash", "test450"
    ).as_posix()


def test_unparsed_extract_is_scored_without_a_call() -> None:
    record = GanFrequencyRecord(
        source_row_index=5837,
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
    row = score_later_stage_row(
        "gan_llm_encode",
        record,
        "",
        extract_row={"raw_output": "{"},
        encode_row=None,
        split="dev750",
        machine="validation",
    )
    assert row["call_error"] is None
    assert row["structured_record"] is None
    assert row["parse_errors"][0].startswith("extract_raw_unparsed:")
    assert row["comparison"]["purist_correct"] is False


def _codebook_extract_raw() -> str:
    return json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "up to 4 per day",
                    "applies_to": None,
                    "time_window": None,
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "up to 4 per day",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "1 per month",
                    "applies_to": None,
                    "time_window": None,
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "used to have 1 per month",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "4 per day",
                "evidence": "up to 4 per day",
                "confidence": "high",
                "rationale": "Current burden is up to four a day.",
            },
        }
    )


def test_select_from_extract_uses_final_label_on_the_pick() -> None:
    extract = parse_extract_ledger(_codebook_extract_raw(), note_text=None)
    events = extract_events_as_select_ledger(extract)
    assert events[0]["label"] == "4 per day"
    assert events[1]["label"] == "1 per month"


def test_select_from_extract_scores_without_an_encode_row() -> None:
    record = GanFrequencyRecord(
        source_row_index=10,
        note_text="Present seizure frequency: up to 4 per day.",
        gold_label="4 per day",
        gold_reference="up to 4 per day",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="4 per day",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(1460.0, 1460.0),
        gold_monthly_frequency=120.0,
    )
    row = score_later_stage_row(
        "gan_llm_select_from_extract",
        record,
        '{"selected_event_ids": ["e1"]}',
        extract_row={"raw_output": _codebook_extract_raw()},
        encode_row=None,
        split="dev750",
        machine="validation",
    )
    prompt = json.loads(row["prompt_input_json"])
    assert prompt["first_choice"]["label"] == "4 per day"
    assert prompt["events"][0]["label"] == "4 per day"
    assert prompt["events"][1]["label"] == "1 per month"
    assert row["structured_record"]["selection"]["final_label"] == "4 per day"
    assert row["comparison"]["purist_correct"] is True


def test_select_from_extract_has_its_own_work_cell() -> None:
    path = later_stage_work_root("gan_llm_select_from_extract")
    assert "gan_llm_select_from_extract" in path.as_posix()
    assert "gan_llm_select/" not in path.as_posix()


def test_later_stage_work_leaf_does_not_reuse_cited_select_cell() -> None:
    path = later_stage_work_root(
        "gan_llm_select_from_extract",
        split="test450",
        work_leaf="gan_llm_select_policy_examples",
    )
    posix = path.as_posix()
    assert "gan_llm_select_policy_examples" in posix
    assert "gan_llm_select_from_extract" not in posix


def test_select_from_extract_verify_is_gemini_only() -> None:
    payload = verify_gan("gan_llm_select_from_extract", "dev750", "gemini37flash")
    assert payload["ok"] is True
    holdout = verify_gan("gan_llm_select_from_extract", "test450", "gemini37flash")
    assert holdout["row_policy"] == "aggregate_only"
    assert holdout["holdout_scratch"].endswith("gan_llm_select_from_extract")
    with pytest.raises(RuntimeError, match="Gemini only"):
        verify_gan("gan_llm_select_from_extract", "dev750", "grok46")


def test_llm_row_has_no_separate_encode_stage() -> None:
    assert LLM_ENCODE_IS_EXTRACT is True
    assert LLM_SELECT_METHOD == "gan_llm_select_from_extract"
    assert EXTRACT_METHOD == "gan_llm_extract"

@pytest.mark.local_corpus
def test_later_stage_reads_codebook_extract_work_cell() -> None:
    assert EXTRACT_METHOD == "gan_llm_extract"
    path = extract_rows_path("dev750")
    assert path.is_file()
    assert "gan_llm_extract" in path.as_posix()
    assert "gan_llm_extract_raw" not in path.as_posix()
