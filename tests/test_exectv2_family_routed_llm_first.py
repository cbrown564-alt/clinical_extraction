"""Tests for the predeclared family-routed ExECTv2 comparison."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_family_routed_llm_first as routed_module,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_family_routed_llm_first import (  # noqa: E501
    FOCUSED_DIAGNOSIS_AGGREGATE_OWNERSHIP,
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


def test_combine_family_routed_predictions_cannot_promote_pi_specialist_mentions() -> None:
    gold = [ExectLetter(letter_id="EA0001", note_text="")]
    shared = PredictedLetter(
        letter_id="EA0001",
        mentions=(
            _mention("Prescription", "shared lamotrigine"),
            _mention("Investigations", "shared MRI"),
        ),
    )
    specialist_or_route = PredictedLetter(
        letter_id="EA0001",
        mentions=(
            _mention("Prescription", "specialist lamotrigine"),
            _mention("Investigations", "specialist MRI"),
            _mention("SeizureFrequency", "routed focal seizures"),
        ),
    )

    routed = combine_family_routed_predictions(
        gold,
        {"EA0001": shared},
        {"EA0001": specialist_or_route},
    )

    mentions = routed[0].mentions
    assert [(m.entity, m.text, m.component_owner) for m in mentions] == [
        ("Prescription", "shared lamotrigine", "llm_first"),
        ("Investigations", "shared MRI", "llm_first"),
        ("SeizureFrequency", "routed focal seizures", "hybrid_sf_route"),
    ]
    assert routed[0].diagnostics["prescription_investigations_route_policy"] == (
        "shared_broad_pass_only"
    )


def test_routed_primary_recovery_scores_only_predeclared_four_families() -> None:
    assert ROUTED_PRIMARY_ENTITIES == (
        "Prescription",
        "Investigations",
        "Diagnosis",
        "SeizureFrequency",
    )


def test_optional_focused_diagnosis_route_replaces_shared_diagnosis_only() -> None:
    gold = [ExectLetter(letter_id="EA0001", note_text="")]
    shared = PredictedLetter(
        letter_id="EA0001",
        mentions=(
            _mention("Prescription", "lamotrigine"),
            _mention("Investigations", "MRI"),
            _mention("Diagnosis", "shared epilepsy"),
        ),
    )
    diagnosis_route = PredictedLetter(
        letter_id="EA0001",
        mentions=(_mention("Diagnosis", "focused focal epilepsy"),),
    )
    sf_route = PredictedLetter(
        letter_id="EA0001",
        mentions=(_mention("SeizureFrequency", "monthly seizures"),),
    )

    routed = combine_family_routed_predictions(
        gold,
        {"EA0001": shared},
        {"EA0001": sf_route},
        {"EA0001": diagnosis_route},
    )

    assert [m.text for m in routed[0].mentions] == [
        "lamotrigine",
        "MRI",
        "focused focal epilepsy",
        "monthly seizures",
    ]
    assert "shared epilepsy" not in [m.text for m in routed[0].mentions]
    assert routed[0].mentions[2].component_owner == "hybrid_diagnosis_reconciler"
    assert routed[0].diagnostics["shared_pass_entities"] == [
        "Investigations",
        "Prescription",
    ]
    assert routed[0].diagnostics["diagnosis_route_entities"] == ["Diagnosis"]
    assert routed[0].diagnostics["aggregate_ownership"] == (
        FOCUSED_DIAGNOSIS_AGGREGATE_OWNERSHIP
    )


def test_build_comparison_with_focused_diagnosis_adds_no_call_replay_candidate(
    monkeypatch,
) -> None:
    gold = [ExectLetter(letter_id="EA0001", note_text="monthly seizures")]
    shared = PredictedLetter(
        letter_id="EA0001",
        mentions=(
            _mention("Prescription", "shared lamotrigine"),
            _mention("Investigations", "shared MRI"),
            _mention("Diagnosis", "shared epilepsy"),
        ),
    )
    diagnosis_route = PredictedLetter(
        letter_id="EA0001",
        mentions=(_mention("Diagnosis", "focused focal epilepsy"),),
    )
    sf_route = PredictedLetter(
        letter_id="EA0001",
        mentions=(_mention("SeizureFrequency", "monthly seizures"),),
    )
    hybrid = PredictedLetter(letter_id="EA0001", mentions=())
    captured: dict[str, list[tuple[str, str, str]]] = {}

    def fake_predictions(path: Path) -> dict[str, PredictedLetter]:
        if path == Path("shared.jsonl"):
            return {"EA0001": shared}
        if path == Path("diagnosis.jsonl"):
            return {"EA0001": diagnosis_route}
        if path == Path("sf.jsonl"):
            return {"EA0001": sf_route}
        if path == Path("hybrid.jsonl"):
            return {"EA0001": hybrid}
        raise AssertionError(f"unexpected artifact path: {path}")

    def fake_candidate_report(
        *,
        name: str,
        ownership: str,
        gold_letters,
        pred_letters,
    ) -> dict:
        captured[name] = [
            (mention.entity, mention.text, mention.component_owner)
            for letter in pred_letters
            for mention in letter.mentions
        ]
        return {"name": name, "ownership": ownership}

    monkeypatch.setattr(
        routed_module,
        "build_family_routed_preflight",
        lambda _root: SimpleNamespace(
            can_run_dev_ladder=True,
            blockers=[],
            planned_dev_ladder=("pilot25", "dev140"),
        ),
    )
    monkeypatch.setattr(routed_module, "load_letters_for_split", lambda _split: gold)
    monkeypatch.setattr(routed_module, "predicted_by_id_from_artifact", fake_predictions)
    monkeypatch.setattr(routed_module, "_rows_by_id", lambda _path: {})
    monkeypatch.setattr(
        routed_module,
        "run_all9_on_letters",
        lambda letters: [
            PredictedLetter(letter_id=letter.letter_id, mentions=())
            for letter in letters
        ],
    )
    monkeypatch.setattr(routed_module, "_candidate_report", fake_candidate_report)
    monkeypatch.setattr(
        routed_module,
        "_route_summary",
        lambda **_kwargs: {"sf_route": {"call_or_parse_failures": 0}},
    )
    monkeypatch.setattr(
        routed_module,
        "_gate_decision",
        lambda candidates, route_summary: {
            "decision": "dev-only-no-call-replay",
            "notes": [],
        },
    )

    report = routed_module.build_family_routed_comparison(
        shared_pass_artifact=Path("shared.jsonl"),
        diagnosis_route_artifact=Path("diagnosis.jsonl"),
        sf_route_artifact=Path("sf.jsonl"),
        hybrid_comparator_artifact=Path("hybrid.jsonl"),
    )

    assert report["input_artifacts"]["diagnosis_route"] == "diagnosis.jsonl"
    assert captured["family_routed_with_focused_diagnosis_route"] == [
        ("Prescription", "shared lamotrigine", "llm_first"),
        ("Investigations", "shared MRI", "llm_first"),
        ("Diagnosis", "focused focal epilepsy", "hybrid_diagnosis_reconciler"),
        ("SeizureFrequency", "monthly seizures", "hybrid_sf_route"),
    ]
    assert ("Diagnosis", "shared epilepsy", "llm_first") not in captured[
        "family_routed_with_focused_diagnosis_route"
    ]


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
