"""Tests for the ExECTv2 SeizureFrequency candidate-span state adjudicator."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_state_adjudicator as adjudicator,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
)

_NOTE = (
    "Unfortunately after the period of seizure freedom the seizures have returned. "
    "She has not had any further seizures since her last clinic appointment and "
    "since starting the lamotrigine. He has had on average one seizure a year "
    "since the age of 17 but a total of 3 in 2020. Family history mentions "
    "epilepsy but no history of seizures."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_candidate_spans_cover_residual_state_patterns() -> None:
    candidates = adjudicator.candidate_spans_for_letter(_LETTER)
    payloads = [candidate.as_payload() for candidate in candidates]

    returned = next(item for item in payloads if item["evidence"] == "the seizures have returned")
    assert returned["state_hint"] == "unknown"
    assert returned["text_hint"] == "seizures"
    assert returned["candidate_type"] == "generic_qualitative_change"
    assert returned["decision_lane"] == "qualitative_change"

    seizure_free = next(
        item for item in payloads if item["evidence"].startswith("not had any further seizures")
    )
    assert seizure_free["state_hint"] == "seizure-free"
    assert seizure_free["candidate_type"] == "generic_seizure_free_anchor"

    active = next(item for item in payloads if item["evidence"] == "a total of 3 in 2020")
    assert active["state_hint"] == "active-rate"
    assert active["text_hint"] == "seizures"
    assert active["candidate_type"] == "generic_active_rate"

    assert all("Family history" not in item["evidence"] for item in payloads)


def test_candidate_spans_type_named_rates_and_prior_event_references() -> None:
    note = (
        "He gets around 1 generalised tonic clonic seizure in his sleep per month. "
        "He last had a seizure before this around a year ago."
    )
    letter = ExectLetter(letter_id="TEST002", note_text=note)

    payloads = [
        candidate.as_payload() for candidate in adjudicator.candidate_spans_for_letter(letter)
    ]

    named_rate = next(
        item for item in payloads if "generalised tonic clonic seizure" in item["evidence"]
    )
    assert named_rate["candidate_type"] == "named_active_rate"
    assert named_rate["decision_lane"] == "active_rate"

    previous = next(item for item in payloads if "seizure before this" in item["evidence"])
    assert previous["candidate_type"] == "prior_event_reference"
    assert previous["decision_lane"] == "reject_or_seizure_free"


def test_build_prompt_input_includes_candidate_span_guide_and_rules() -> None:
    payload = json.loads(
        adjudicator.build_prompt_input(
            _LETTER,
            [
                {
                    "text": "seizures",
                    "attributes": {"FrequencyChange": "Increased"},
                    "evidence": "the seizures have returned",
                }
            ],
        )
    )

    assert payload["prompt_version"] == adjudicator.PROMPT_VERSION
    assert payload["prompt_version"].endswith("_v0.5")
    assert payload["candidate_evidence_spans"]
    assert payload["typed_candidate_guide"]
    assert payload["candidate_evidence_spans"][0]["candidate_type"]
    assert payload["generic_seizure_policy"]
    assert payload["seizure_free_anchor_guide"]
    assert payload["unknown_change_recovery_lane"]
    assert {"active-rate", "seizure-free", "unknown", "reject"} <= set(
        payload["state_decision_guide"]
    )
    rules = " ".join(payload["clinical_rules"])
    assert "Candidate spans are not predictions" in rules
    assert "state_hint='reject'" in rules
    assert "Do not emit a generic seizures active-rate" in rules
    assert "unlabelled attacks, episodes, events" in rules
    assert "driving-advice requirements" in rules
    assert "epilepsy stability" in rules
    assert "Unknown/change-state recovery is a separate lane" in rules
    assert "candidate_type" in rules
    assert "prior_event_reference" in rules
    assert "seizure_free_anchor_guide" in rules
    assert "last seizure was on 15 April" in rules
    assert "split them" in rules
    assert "Do not emit CUI or CUIPhrase" in rules
    seizure_free_rendering = " ".join(payload["seizure_free_anchor_guide"]["rendering"])
    assert "NumberOfSeizures='0'" in seizure_free_rendering
    assert "text='seizures'" in seizure_free_rendering
    seizure_free_rejects = " ".join(payload["seizure_free_anchor_guide"]["reject"])
    assert "last seizure before this" in seizure_free_rejects
    assert "no further episodes/collapses" in seizure_free_rejects
    examples = payload["worked_examples"]
    assert any("improved her seizures" in e["note_fragment"] for e in examples)
    assert any("seizures have been worse" in e["note_fragment"] for e in examples)
    assert any("seizures remain well controlled" in e["note_fragment"] for e in examples)
    assert any(
        "generalised tonic clonic seizure in his sleep" in e["note_fragment"] for e in examples
    )
    assert any("history of staring episodes" in e["note_fragment"] for e in examples)
    assert any("last seizure was on the 15th April" in e["note_fragment"] for e in examples)
    assert any("no further seizures" in e["note_fragment"] for e in examples)
    reject_free = " ".join(payload["generic_seizure_policy"]["reject_generic_seizure_free"])
    assert "Driving advice" in reject_free
    recovery = " ".join(
        payload["unknown_change_recovery_lane"]["generic_seizures_frequency_change"]
    )
    assert "seizures have been worse" in recovery
    assert "seizures remain well controlled" in recovery


def test_to_predicted_letter_strips_projection_attrs_and_projects_cui() -> None:
    pred, warnings = adjudicator.to_predicted_letter(
        "TEST001",
        [
            MentionRecord(
                text="generalised tonic clonic seizures",
                attributes={
                    "CUI": "WRONG",
                    "CUIPhrase": "wrong",
                    "LowerNumberOfSeizures": "3",
                    "UpperNumberOfSeizures": "4",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
                evidence="3-4 generalised tonic chronic seizures per week",
                confidence="high",
                rationale="Source typo is normalized.",
            )
        ],
        note_text="She had 3-4 generalised tonic chronic seizures per week.",
    )

    assert pred.mentions[0].text == "generalised tonic clonic seizures"
    assert pred.mentions[0].attributes["CUI"] == "C0494475"
    assert pred.mentions[0].component_owner == adjudicator.COMPONENT_OWNER
    assert any("dropped_model_supplied_projection_attribute" in warning for warning in warnings)


def test_summarize_rows_reports_candidate_spans_and_sf_recovery() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 1,
            "n_candidate_spans": 3,
            "n_mentions_raw": 1,
            "n_mentions_scored": 1,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "text": "seizures",
                    "attributes": {
                        "CUI": "C0036572",
                        "CUIPhrase": "seizures",
                        "FrequencyChange": "Increased",
                    },
                }
            ],
            "predicted_mentions": [
                {
                    "text": "seizures",
                    "attributes": {
                        "CUI": "C0036572",
                        "CUIPhrase": "seizures",
                        "FrequencyChange": "Increased",
                    },
                    "evidence": "the seizures have returned",
                }
            ],
        }
    ]

    summary = adjudicator.summarize_rows(rows)

    assert summary["clinical_recovery"]["seizure_frequency"]["f1"] == 1.0
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
    assert summary["n_candidate_spans"] == 3


def test_write_report_includes_candidate_span_summary(tmp_path) -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 0,
            "n_candidate_spans": 2,
            "n_mentions_raw": 0,
            "n_mentions_scored": 0,
            "n_evidence_invalid": 0,
            "gold_mentions": [],
            "predicted_mentions": [],
        }
    ]
    path = tmp_path / "report.md"

    adjudicator.write_report(
        rows,
        {
            "prompt_version": adjudicator.PROMPT_VERSION,
            "pipeline_family": adjudicator.PIPELINE_FAMILY,
            "split": "dev",
            "model": "test-model",
            "mode": "prompt-only",
        },
        path,
        jsonl_path=tmp_path / "rows.jsonl",
    )

    text = path.read_text(encoding="utf-8")
    assert "Candidate-Span State Adjudicator" in text
    assert "Candidate spans" in text
