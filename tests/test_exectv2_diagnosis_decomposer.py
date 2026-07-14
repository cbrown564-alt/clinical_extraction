"""Tests for the ExECTv2 Diagnosis heading/narrative decomposer."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    diagnosis_decomposer as decomposer,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    MentionRecord,
)

_NOTE = (
    "Diagnosis: epilepsy - probable focal. "
    "Seizure type and frequency: generalised tonic clonic seizures every month. "
    "Family history of epilepsy but no history of febrile seizures."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_diagnosis_spans_decompose_heading_and_narrative() -> None:
    spans = decomposer.diagnosis_spans_for_letter(_LETTER)
    payloads = [span.as_payload() for span in spans]

    heading = next(item for item in payloads if item["span_role"] == "diagnosis-heading")
    assert heading["evidence"] == "Diagnosis: epilepsy - probable focal."
    assert "epilepsy" in heading["concept_hints"]
    assert "focal epilepsy" in heading["concept_hints"]

    narrative = next(item for item in payloads if item["span_role"] == "narrative-seizure-type")
    assert "generalised tonic clonic seizures" in narrative["evidence"]
    assert "tonic clonic seizures" in narrative["concept_hints"]

    assert all("Family history" not in item["evidence"] for item in payloads)


def test_build_prompt_input_includes_decomposition_contract() -> None:
    payload = json.loads(
        decomposer.build_prompt_input(
            _LETTER,
            [
                {
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: epilepsy - probable focal.",
                }
            ],
        )
    )

    assert payload["prompt_version"] == decomposer.PROMPT_VERSION
    assert payload["prompt_version"].endswith("_v0.1")
    assert payload["diagnosis_candidate_spans"]
    assert {"diagnosis-heading", "narrative-seizure-type", "reconcile"} <= set(
        payload["decomposition_contract"]
    )
    rules = " ".join(payload["clinical_rules"])
    assert "candidate spans as a clinical checklist" in rules
    assert "explicitly ask: does this contain the word epilepsy" in rules
    assert "Do not emit CUI or CUIPhrase" in rules


def test_resolution_candidate_prompt_is_explicit_and_opt_in() -> None:
    payload = json.loads(
        decomposer.build_prompt_input(
            _LETTER,
            [],
            prompt_variant="resolution_v02",
        )
    )

    assert payload["prompt_version"].endswith("_v0.2")
    rules = " ".join(payload["clinical_rules"])
    assert "epileptic disorders and named epileptic seizure types only" in rules
    assert "service header" in rules
    assert "status epilepticus" in rules


def test_to_predicted_letter_strips_projection_attrs_and_projects_cui() -> None:
    pred, warnings = decomposer.to_predicted_letter(
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
    assert pred.mentions[0].component_owner == decomposer.COMPONENT_OWNER
    assert any("dropped_model_supplied_projection_attribute" in warning for warning in warnings)


def test_summarize_rows_reports_diagnosis_spans() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 1,
            "n_diagnosis_spans": 2,
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

    summary = decomposer.summarize_rows(rows)

    assert summary["clinical_recovery"]["diagnosis"]["f1"] == 1.0
    assert summary["clinical_recovery"]["concept_only"]["f1"] == 1.0
    assert summary["clinical_recovery"]["concept_negation"]["f1"] == 1.0
    assert summary["clinical_recovery"]["concept_assertion"]["f1"] == 1.0
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
    assert summary["n_diagnosis_spans"] == 2


def test_write_report_includes_diagnosis_span_summary(tmp_path) -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 0,
            "n_diagnosis_spans": 2,
            "n_mentions_raw": 0,
            "n_mentions_scored": 0,
            "n_evidence_invalid": 0,
            "gold_mentions": [],
            "predicted_mentions": [],
        }
    ]
    path = tmp_path / "report.md"

    decomposer.write_report(
        rows,
        {
            "prompt_version": decomposer.PROMPT_VERSION,
            "pipeline_family": decomposer.PIPELINE_FAMILY,
            "split": "dev",
            "model": "test-model",
            "mode": "prompt-only",
        },
        path,
        jsonl_path=tmp_path / "rows.jsonl",
    )

    text = path.read_text(encoding="utf-8")
    assert "Heading/Narrative Decomposer" in text
    assert "Diagnosis spans" in text
