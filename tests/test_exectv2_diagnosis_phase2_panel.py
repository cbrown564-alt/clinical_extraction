"""Tests for the ExECTv2 Diagnosis Phase 2 residual panel runner."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_phase2_panel as phase2,
)


def test_select_panel_round_robins_residual_families() -> None:
    records = [
        _record("EA0001", "gold", "epilepsy", "epilepsy"),
        _record("EA0002", "predicted", "tonic clonic seizures", "tonic clonic seizures"),
        _record("EA0003", "gold", "focal epilepsy", "focal epilepsy"),
        _record("EA0004", "gold", "secondary generalised seizures", "secondary"),
        _record("EA0005", "gold", "juvenile myoclonic epilepsy", "JME"),
        _record("EA0006", "gold", "absence seizures", "absence seizures"),
    ]

    panel = phase2.select_panel(records, panel_size=5)

    assert [item.letter_id for item in panel] == [
        "EA0001",
        "EA0002",
        "EA0003",
        "EA0004",
        "EA0005",
    ]
    assert panel[0].residual_families == ("generic_epilepsy",)
    assert panel[1].residual_families == ("tonic_clonic",)


def test_build_prompt_input_keeps_row_specific_gold_residuals_out_of_prompt() -> None:
    payload = json.loads(
        phase2.build_prompt_input(
            ExectLetter(
                letter_id="EA0001",
                note_text="Diagnosis: probable focal epilepsy.",
            ),
            variant="candidate_selector",
            current_mentions=[
                {
                    "text": "epilepsy",
                    "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: probable focal epilepsy.",
                }
            ],
            verifier_mentions=[],
            decomposer_mentions=[],
            diagnosis_spans=[
                {
                    "span_id": "D0",
                    "evidence": "Diagnosis: probable focal epilepsy.",
                    "concept_hints": ["focal epilepsy"],
                }
            ],
        )
    )

    assert payload["prompt_version"] == phase2.PROMPT_VERSION
    assert payload["variant"] == "candidate_selector"
    assert "residual" not in json.dumps(payload["candidate_sources"]).lower()
    assert "Do not include CUI" in " ".join(payload["strict_constraints"])
    assert payload["candidate_sources"]["current_v02_mentions"][0]["text"] == "epilepsy"
    assert payload["candidate_concept_groups"][0]["group_id"] == "generic_epilepsy"


def test_summarize_rows_compares_variant_to_v02_panel_control() -> None:
    current_rows = [
        {
            "letter_id": "EA0001",
            "gold_mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                }
            ],
            "predicted_mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "epilepsy",
                    "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                }
            ],
        }
    ]
    rows = [
        {
            "row_id": "candidate_selector:EA0001",
            "letter_id": "EA0001",
            "variant": "candidate_selector",
            "parse_errors": [],
            "n_mentions_raw": 1,
            "n_mentions_scored": 1,
            "n_evidence_invalid": 0,
            "gold_mentions": current_rows[0]["gold_mentions"],
            "predicted_mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                }
            ],
        }
    ]

    summary = phase2.summarize_rows(rows, current_rows=current_rows, panel_ids=["EA0001"])

    assert summary["baseline_v02"]["f1"] == 0.0
    assert summary["variant_scores"]["candidate_selector"]["f1"] == 1.0
    assert summary["variant_scores"]["candidate_selector"]["delta_f1_vs_v02"] == 1.0
    assert summary["variant_scores"]["candidate_selector"]["changed_rows_vs_v02"] == 1


def _record(letter_id: str, side: str, text: str, evidence: str) -> dict[str, str]:
    return {
        "letter_id": letter_id,
        "entity": "Diagnosis",
        "side": side,
        "key": text,
        "example_text": text,
        "evidence": evidence,
    }
