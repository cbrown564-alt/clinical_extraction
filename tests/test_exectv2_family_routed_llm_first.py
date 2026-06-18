"""Tests for the predeclared family-routed ExECTv2 comparison."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_family_routed_llm_first import (  # noqa: E501
    PIPELINE_FAMILY,
    ROUTED_PRIMARY_ENTITIES,
    _gate_decision,
    combine_family_routed_predictions,
)


def test_combine_family_routed_predictions_uses_shared_pid_and_routed_sf() -> None:
    gold = [ExectLetter(letter_id="EA0001", note_text="")]
    shared = PredictedLetter(
        letter_id="EA0001",
        mentions=(
            _mention("Prescription", "lamotrigine"),
            _mention("Investigations", "MRI"),
            _mention("Diagnosis", "epilepsy"),
            _mention("SeizureFrequency", "seizures"),
            _mention("EpilepsyCause", "stroke"),
        ),
    )
    sf_route = PredictedLetter(
        letter_id="EA0001",
        mentions=(_mention("SeizureFrequency", "focal seizures"),),
    )

    routed = combine_family_routed_predictions(
        gold,
        {"EA0001": shared},
        {"EA0001": sf_route},
    )

    assert len(routed) == 1
    assert [m.entity for m in routed[0].mentions] == [
        "Prescription",
        "Investigations",
        "Diagnosis",
        "SeizureFrequency",
    ]
    assert routed[0].mentions[-1].text == "focal seizures"
    assert routed[0].mentions[-1].component_owner == "hybrid_sf_route"
    assert routed[0].diagnostics["pipeline_family"] == PIPELINE_FAMILY


def test_routed_primary_recovery_scores_only_predeclared_four_families() -> None:
    assert ROUTED_PRIMARY_ENTITIES == (
        "Prescription",
        "Investigations",
        "Diagnosis",
        "SeizureFrequency",
    )


def test_gate_decision_requires_qualified_routed_candidate_to_beat_single_pass() -> None:
    candidates = [
        _candidate("llm_only_all_entities", 0.40, 0.20, p_f1=0.80, i_f1=0.70),
        _candidate(
            "family_routed_llm_first",
            0.55,
            0.65,
            p_f1=0.79,
            i_f1=0.69,
            evidence=1.0,
        ),
    ]
    route_summary = {"sf_route": {"call_or_parse_failures": 0}}

    decision = _gate_decision(candidates, route_summary)

    assert decision["decision"] == "dev-gate-passed-qualified"
    assert "llm_first_with_hybrid_sf_route" in " ".join(decision["notes"])


def _mention(entity: str, text: str) -> PredictedMention:
    return PredictedMention(entity=entity, text=text, attributes={}, evidence=text)


def _candidate(
    name: str,
    overall_f1: float,
    sf_f1: float,
    *,
    p_f1: float,
    i_f1: float,
    evidence: float = 1.0,
) -> dict:
    return {
        "name": name,
        "routed_primary_recovery": {
            "overall": {"f1": overall_f1},
            "headline_scores": {
                "Prescription": {"f1": p_f1},
                "Investigations": {"f1": i_f1},
                "SeizureFrequency": {"f1": sf_f1},
            },
        },
        "routed_primary_evidence": {"overall": {"exact_evidence_rate": evidence}},
    }
