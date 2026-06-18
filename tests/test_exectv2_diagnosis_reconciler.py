"""Tests for the ExECTv2 Diagnosis decomposition reconciler."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_reconciler as reconciler,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
)

_NOTE = (
    "Diagnosis: epilepsy - probable focal. "
    "Seizure type and frequency: generalised tonic clonic seizures every month."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_build_prompt_input_carries_two_candidate_sources_and_rules() -> None:
    payload = json.loads(
        reconciler.build_prompt_input(
            _LETTER,
            verifier_mentions=[
                {
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: epilepsy - probable focal.",
                }
            ],
            decomposer_mentions=[
                {
                    "text": "epilepsy",
                    "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: epilepsy - probable focal.",
                }
            ],
            diagnosis_spans=[
                {
                    "span_id": "D0",
                    "evidence": "Diagnosis: epilepsy - probable focal.",
                    "span_role": "diagnosis-heading",
                    "concept_hints": ["epilepsy", "focal epilepsy"],
                }
            ],
        )
    )

    assert payload["prompt_version"] == reconciler.PROMPT_VERSION
    assert payload["prompt_version"].endswith("_v0.2")
    sources = payload["candidate_sources"]
    assert sources["verifier_mentions"][0]["text"] == "focal epilepsy"
    assert sources["decomposer_mentions"][0]["text"] == "epilepsy"
    assert sources["diagnosis_candidate_spans"][0]["span_role"] == "diagnosis-heading"
    groups = payload["candidate_concept_groups"]
    assert {group["group_id"] for group in groups} >= {
        "generic_epilepsy",
        "focal_epilepsy_family",
    }
    focal_group = next(
        group for group in groups if group["group_id"] == "focal_epilepsy_family"
    )
    assert focal_group["decision_question"] == (
        "Which focal-family Diagnosis concepts are directly asserted?"
    )
    assert focal_group["candidates"][0]["source"] == "verifier"
    rules = " ".join(payload["reconciliation_rules"])
    assert "verifier_mentions as the starting point" in rules
    assert "Classify each candidate_concept_groups bucket" in rules
    assert "patient-level established" in rules
    assert "Be conservative with seizure-type-only" in rules
    assert "Do not infer symptomatic structural focal epilepsy" in rules
    assert "Preserve secondary generalised seizure concepts" in rules


def test_candidate_concept_groups_merge_sources_by_clinical_family() -> None:
    groups = reconciler.candidate_concept_groups(
        verifier_mentions=[
            {
                "text": "focal epilepsy",
                "attributes": {"Certainty": "5"},
                "evidence": "Diagnosis: focal epilepsy",
            },
            {
                "text": "tonic clonic seizures",
                "attributes": {"Certainty": "5"},
                "evidence": "generalised tonic clonic seizures",
            },
        ],
        decomposer_mentions=[
            {
                "text": "epilepsy",
                "attributes": {"Certainty": "5"},
                "evidence": "Diagnosis: focal epilepsy",
            },
            {
                "text": "secondary generalised seizures",
                "attributes": {"Certainty": "5"},
                "evidence": "secondary generalised seizures",
            },
        ],
        diagnosis_spans=[
            {
                "span_id": "D0",
                "evidence": "Diagnosis: symptomatic structural focal epilepsy",
                "span_role": "diagnosis-heading",
                "concept_hints": ["symptomatic structural focal epilepsy"],
            }
        ],
    )

    by_id = {group["group_id"]: group for group in groups}
    assert [candidate["source"] for candidate in by_id["generic_epilepsy"]["candidates"]] == [
        "decomposer"
    ]
    assert {candidate["source"] for candidate in by_id["focal_epilepsy_family"]["candidates"]} == {
        "span",
        "verifier",
    }
    assert by_id["tonic_clonic_family"]["decision_question"].startswith("Which tonic-clonic")
    assert by_id["secondary_generalised_family"]["candidates"][0]["text"] == (
        "secondary generalised seizures"
    )
    assert by_id["structural_symptomatic_family"]["candidates"][0]["source"] == "span"


def test_mentions_by_letter_filters_to_diagnosis() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "predicted_mentions": [
                {"entity": "Diagnosis", "text": "epilepsy", "attributes": {}},
                {"entity": "Prescription", "text": "lamotrigine", "attributes": {}},
            ],
        }
    ]

    assert reconciler.mentions_by_letter(rows) == {
        "TEST001": [
            {
                "text": "epilepsy",
                "attributes": {},
                "evidence": "",
                "confidence": "",
                "rationale": "",
            }
        ]
    }


def test_to_predicted_letter_strips_projection_attrs_and_projects_cui() -> None:
    pred, warnings = reconciler.to_predicted_letter(
        "TEST001",
        [
            MentionRecord(
                text="focal epilepsy",
                attributes={
                    "CUI": "WRONG",
                    "CUIPhrase": "wrong",
                    "DiagCategory": "Epilepsy",
                    "Certainty": "4",
                    "Negation": "Affirmed",
                },
                evidence="Diagnosis: epilepsy - probable focal.",
                confidence="high",
                rationale="Probable focal epilepsy.",
            )
        ],
        note_text=_NOTE,
    )

    assert pred.mentions[0].text == "focal epilepsy"
    assert pred.mentions[0].attributes["CUI"]
    assert pred.mentions[0].component_owner == reconciler.COMPONENT_OWNER
    assert any("dropped_model_supplied_projection_attribute" in warning for warning in warnings)


def test_summarize_rows_reports_reconciler_candidate_counts() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_verifier_mentions": 1,
            "n_decomposer_mentions": 2,
            "n_diagnosis_spans": 1,
            "n_mentions_raw": 1,
            "n_mentions_scored": 1,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                }
            ],
            "predicted_mentions": [
                {
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: epilepsy - probable focal.",
                }
            ],
        }
    ]

    summary = reconciler.summarize_rows(rows)

    assert summary["clinical_recovery"]["diagnosis"]["f1"] == 1.0
    assert summary["n_verifier_mentions"] == 1
    assert summary["n_decomposer_mentions"] == 2
    assert summary["n_diagnosis_spans"] == 1


def test_write_report_includes_reconciler_candidate_summary(tmp_path) -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_verifier_mentions": 1,
            "n_decomposer_mentions": 2,
            "n_diagnosis_spans": 1,
            "n_mentions_raw": 0,
            "n_mentions_scored": 0,
            "n_evidence_invalid": 0,
            "gold_mentions": [],
            "predicted_mentions": [],
        }
    ]
    path = tmp_path / "report.md"

    reconciler.write_report(
        rows,
        {
            "prompt_version": reconciler.PROMPT_VERSION,
            "pipeline_family": reconciler.PIPELINE_FAMILY,
            "split": "dev",
            "model": "test-model",
            "mode": "prompt-only",
        },
        path,
        jsonl_path=tmp_path / "rows.jsonl",
    )

    text = path.read_text(encoding="utf-8")
    assert "Diagnosis Decomposition Reconciler" in text
    assert "Verifier candidate mentions" in text
    assert "Decomposer candidate mentions" in text
