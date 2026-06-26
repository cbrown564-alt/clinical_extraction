"""Tests for the ExECTv2 candidate-backed family-conditioned adjudicator."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_family_conditioned_candidate_adjudicator as adjudicator,
)
from tests.helpers.prompt_hygiene import FORBIDDEN_PHRASES

_NOTE = (
    "Diagnosis: focal epilepsy. "
    "Current treatment is lamotrigine 100 mg twice daily. "
    "She has focal seizures every month."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def _source_row() -> dict[str, object]:
    return {
        "letter_id": "TEST001",
        "prompt_version": "source_v1",
        "pipeline_family": "source_family",
        "mode": "live",
        "predicted_mentions": [
            {
                "entity": PRESCRIPTION.name,
                "text": "lamotrigine 100 mg twice daily",
                "evidence": "Current treatment is lamotrigine 100 mg twice daily.",
                "attributes": {
                    "DrugName": "lamotrigine",
                    "DrugDose": "100",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
                "confidence": "high",
                "rationale": "Active regimen.",
            },
            {
                "entity": DIAGNOSIS.name,
                "text": "focal epilepsy",
                "evidence": "Diagnosis: focal epilepsy.",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "confidence": "high",
                "rationale": "Diagnosis line.",
            },
        ],
        "candidate_spans": [{"candidate_id": "C0", "evidence": "focal seizures every month"}],
    }


def test_build_candidate_bundle_filters_target_family_and_preserves_source() -> None:
    bundle = adjudicator.build_candidate_bundle(
        _LETTER,
        PRESCRIPTION.name,
        {"trusted": [_source_row()]},
    )

    assert len(bundle["candidate_mentions"]) == 1
    candidate = bundle["candidate_mentions"][0]
    assert candidate["entity"] == PRESCRIPTION.name
    assert candidate["source"] == "trusted"
    assert candidate["source_prompt_version"] == "source_v1"
    assert bundle["auxiliary_candidates"]
    assert all(row["family"] == "medication" for row in bundle["candidate_evidence_ledger"])


def test_prompt_uses_one_schema_and_candidate_bundle_without_forbidden_phrases() -> None:
    prompt = adjudicator.build_prompt_input(
        _LETTER,
        PRESCRIPTION.name,
        {"trusted": [_source_row()]},
    )
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in prompt]
    assert leaked == []

    payload = json.loads(prompt)
    assert payload["prompt_version"] == adjudicator.PROMPT_VERSION
    assert payload["target_family"] == PRESCRIPTION.name
    assert payload["candidate_bundle"]["candidate_mentions"]
    assert "clinical_events" in payload["output_schema"]
    assert payload["output_schema"]["clinical_events"][0]["mentions"][0]["entity"] == (
        PRESCRIPTION.name
    )
    assert payload["family_profile"]["entity"] == PRESCRIPTION.name


def test_candidate_passthrough_produces_target_mentions_only() -> None:
    bundle = adjudicator.build_candidate_bundle(
        _LETTER,
        PRESCRIPTION.name,
        {"trusted": [_source_row()]},
    )
    mentions = adjudicator.candidate_mentions_as_flat_mentions(
        bundle,
        target_family=PRESCRIPTION.name,
    )
    prediction, warnings = adjudicator.to_predicted_letter(
        "TEST001",
        mentions,
        note_text=_NOTE,
        target_family=PRESCRIPTION.name,
    )

    assert warnings == []
    assert [m.entity for m in prediction.mentions] == [PRESCRIPTION.name]
    assert prediction.mentions[0].component_owner == adjudicator.COMPONENT_OWNER
    assert prediction.diagnostics["pipeline_family"] == adjudicator.PIPELINE_FAMILY


def test_summarize_rows_uses_family_comparator() -> None:
    row = {
        "letter_id": "TEST001",
        "target_family": PRESCRIPTION.name,
        "parse_errors": [],
        "gold_mentions": [
            {
                "entity": PRESCRIPTION.name,
                "text": "lamotrigine 100 mg twice daily",
                "attributes": {
                    "DrugName": "lamotrigine",
                    "DrugDose": "100",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
            }
        ],
        "predicted_mentions": [
            {
                "entity": PRESCRIPTION.name,
                "text": "lamotrigine 100 mg twice daily",
                "attributes": {
                    "DrugName": "lamotrigine",
                    "DrugDose": "100",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
            }
        ],
    }

    summary = adjudicator.summarize_rows([row], target_family=PRESCRIPTION.name)

    assert summary["clinical_recovery"]["headline"]["f1"] == 1.0
    assert summary["clinical_recovery"]["current_comparator_f1"] == 0.817


def test_rows_by_letter_keeps_multiple_source_rows() -> None:
    rows = [_source_row(), {**_source_row(), "letter_id": "TEST002"}]

    grouped = adjudicator.rows_by_letter(rows)

    assert sorted(grouped) == ["TEST001", "TEST002"]


def test_candidate_bundle_can_target_sf_event_family() -> None:
    bundle = adjudicator.build_candidate_bundle(
        _LETTER,
        SEIZURE_FREQUENCY.name,
        {"trusted": [_source_row()]},
    )

    assert all(row["family"] == "seizure_frequency" for row in bundle["candidate_evidence_ledger"])


def test_parse_candidate_events_json_repairs_trailing_brackets() -> None:
    raw = (
        '{"clinical_events": [{"family": "diagnosis", "anchor_text": "epilepsy", '
        '"evidence": "Diagnosis: focal epilepsy.", "event_state": {}, '
        '"mentions": [{"entity": "Diagnosis", "text": "focal epilepsy", '
        '"attributes": {"DiagCategory": "Epilepsy", "Certainty": "5", '
        '"Negation": "Affirmed"}}], "confidence": "high", '
        '"rationale": "Candidate copied."}]}]}'
    )

    record, errors = adjudicator.parse_candidate_events_json(raw)

    assert record is not None
    assert record.clinical_events[0].mentions[0].text == "focal epilepsy"
    assert errors == [] or any(
        "ignored_trailing_json_brackets" in error for error in errors
    )


def test_action_prompt_requests_candidate_id_actions_only() -> None:
    prompt = adjudicator.build_action_prompt_input(
        _LETTER,
        PRESCRIPTION.name,
        {"trusted": [_source_row()]},
    )
    payload = json.loads(prompt)

    assert payload["prompt_version"] == adjudicator.PROMPT_VERSION
    assert "candidate_actions" in payload["output_schema"]
    assert "do not rewrite mention text" in payload["task"].lower()
    assert payload["candidate_bundle"]["candidate_mentions"][0]["candidate_id"]


def test_parse_candidate_actions_json_keeps_valid_actions() -> None:
    raw = json.dumps(
        {
            "candidate_actions": [
                {
                    "candidate_id": "trusted:M0",
                    "action": "keep",
                    "reason_code": "supported",
                    "rationale": "Evidence supports the candidate.",
                },
                {"candidate_id": "trusted:M1", "action": "reject", "reason_code": "wrong_entity"},
                {"candidate_id": "", "action": "drop"},
            ]
        }
    )

    actions, notes = adjudicator.parse_candidate_actions_json(raw)

    assert actions == [
        {
            "candidate_id": "trusted:M0",
            "action": "keep",
            "reason_code": "supported",
            "rationale": "Evidence supports the candidate.",
        },
        {
            "candidate_id": "trusted:M1",
            "action": "reject",
            "reason_code": "wrong_entity",
            "rationale": "",
        },
    ]
    assert notes == ["dropped_invalid_action: 2"]


def test_parse_candidate_actions_json_accepts_bare_action_list() -> None:
    raw = json.dumps(
        [
            {
                "candidate_id": "trusted:M0",
                "action": "keep",
                "reason_code": "supported",
                "rationale": "Evidence supports it.",
            }
        ]
    )

    actions, notes = adjudicator.parse_candidate_actions_json(raw)

    assert actions == [
        {
            "candidate_id": "trusted:M0",
            "action": "keep",
            "reason_code": "supported",
            "rationale": "Evidence supports it.",
        }
    ]
    assert notes == ["coerced_top_level_candidate_actions_list"]


def test_parse_candidate_actions_json_recovers_action_triples_from_bad_rationale() -> None:
    raw = (
        '{"candidate_actions": [{"candidate_id": "trusted:M0", "action": "keep", '
        '"reason_code": "supported", "rationale": "bad "quote" text"}, '
        '{"candidate_id": "trusted:M1", "action": "reject", '
        '"reason_code": "wrong_entity", "rationale": "also bad"}]}'
    )

    actions, notes = adjudicator.parse_candidate_actions_json(raw)

    assert actions == [
        {
            "candidate_id": "trusted:M0",
            "action": "keep",
            "reason_code": "supported",
            "rationale": "",
        },
        {
            "candidate_id": "trusted:M1",
            "action": "reject",
            "reason_code": "wrong_entity",
            "rationale": "",
        },
    ]
    assert notes == ["recovered_malformed_candidate_actions: Expecting ',' delimiter"]


def test_apply_candidate_actions_copies_candidates_and_ignores_unverified_rejects() -> None:
    bundle = adjudicator.build_candidate_bundle(
        _LETTER,
        PRESCRIPTION.name,
        {"trusted": [_source_row()]},
    )

    mentions, warnings = adjudicator.apply_candidate_actions(
        bundle,
        [
            {
                "candidate_id": bundle["candidate_mentions"][0]["candidate_id"],
                "action": "reject",
                "reason_code": "unsupported",
                "rationale": "Model wanted to reject this.",
            }
        ],
        target_family=PRESCRIPTION.name,
        note_text=_NOTE,
    )

    assert len(mentions) == 1
    assert mentions[0].text == "lamotrigine 100 mg twice daily"
    assert "ignored_unverified_reject" in warnings[0]


def test_apply_candidate_actions_can_reject_missing_actions_for_protocol_strict_mode() -> None:
    bundle = adjudicator.build_candidate_bundle(
        _LETTER,
        PRESCRIPTION.name,
        {"trusted": [_source_row()]},
    )

    mentions, warnings = adjudicator.apply_candidate_actions(
        bundle,
        [],
        target_family=PRESCRIPTION.name,
        note_text=_NOTE,
        default_missing_action="reject",
    )

    assert mentions == []
    assert warnings == [
        f"missing_action_rejected: {bundle['candidate_mentions'][0]['candidate_id']}"
    ]


def test_apply_candidate_actions_honors_verifiable_bad_evidence_reject() -> None:
    bad_row = _source_row()
    bad_row["predicted_mentions"][0]["evidence"] = "not in note"  # type: ignore[index]
    bundle = adjudicator.build_candidate_bundle(
        _LETTER,
        PRESCRIPTION.name,
        {"trusted": [bad_row]},
    )
    candidate_id = bundle["candidate_mentions"][0]["candidate_id"]

    mentions, warnings = adjudicator.apply_candidate_actions(
        bundle,
        [
            {
                "candidate_id": candidate_id,
                "action": "reject",
                "reason_code": "evidence_not_substring",
                "rationale": "Evidence is not present.",
            }
        ],
        target_family=PRESCRIPTION.name,
        note_text=_NOTE,
    )

    assert mentions == []
    assert warnings == [f"honored_reject: {candidate_id}: evidence_not_substring"]
