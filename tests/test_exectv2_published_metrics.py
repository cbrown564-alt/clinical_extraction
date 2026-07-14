from __future__ import annotations

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    published_metric_reproduction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.published import (
    score_published_metrics,
)


def _annotation(
    entity: str,
    text: str,
    *,
    raw_text: str | None = None,
    **attributes: str,
) -> ExectAnnotation:
    return ExectAnnotation(
        entity=entity,
        text=text,
        raw_text=raw_text,
        attributes=attributes,
    )


def _letter(letter_id: str, *annotations: ExectAnnotation) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text="", annotations=annotations)


def test_published_views_separate_phrase_cui_and_feature_agreement() -> None:
    gold = [
        _letter(
            "L1",
            _annotation(
                "Diagnosis",
                "focal-epilepsy",
                raw_text="probable focal epilepsy",
                CUI="C0014547",
                CUIPhrase="focal-epilepsy",
                Certainty="4",
                Negation="Affirmed",
            ),
        )
    ]
    pred = [
        _letter(
            "L1",
            _annotation(
                "Diagnosis",
                "Probable   focal-epilepsy",
                CUI="C0014547",
                CUIPhrase="a different ontology label",
                Certainty="5",
                Negation="Affirmed",
            ),
        )
    ]

    scores = score_published_metrics(gold, pred, ("Diagnosis",))

    assert scores.normalized_phrase.per_entity["Diagnosis"].per_item.f1 == 1.0
    assert scores.cui.per_entity["Diagnosis"].per_item.f1 == 1.0
    assert scores.all_features.per_entity["Diagnosis"].per_item.f1 == 0.0


def test_cui_matching_does_not_require_the_same_surface_phrase() -> None:
    gold = [
        _letter(
            "L1",
            _annotation(
                "Prescription",
                "lamotrigine-100-mg-twice-daily",
                CUI="C0064636",
                DrugName="lamotrigine",
                DrugDose="100",
                DoseUnit="mg",
                Frequency="2",
            ),
        )
    ]
    pred = [
        _letter(
            "L1",
            _annotation(
                "Prescription",
                "Lamictal",
                CUI="C0064636",
                DrugName="lamotrigine",
                DrugDose="100",
                DoseUnit="mg",
                Frequency="2",
            ),
        )
    ]

    scores = score_published_metrics(gold, pred, ("Prescription",))

    assert scores.normalized_phrase.per_entity["Prescription"].per_item.f1 == 0.0
    assert scores.cui.per_entity["Prescription"].per_item.f1 == 1.0
    assert scores.all_features.per_entity["Prescription"].per_item.f1 == 1.0


def test_missing_cuis_never_match_each_other() -> None:
    gold = [_letter("L1", _annotation("Onset", "childhood", Age="8"))]
    pred = [_letter("L1", _annotation("Onset", "childhood", Age="8"))]

    scores = score_published_metrics(gold, pred, ("Onset",))

    assert scores.normalized_phrase.per_entity["Onset"].per_item.f1 == 1.0
    assert scores.cui.per_entity["Onset"].per_item.model_dump() == {
        "tp": 0,
        "fp": 1,
        "fn": 1,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
    }
    assert scores.all_features.per_entity["Onset"].per_item.f1 == 0.0
    assert scores.missing_cui.gold == 1
    assert scores.missing_cui.predicted == 1


def test_unpublished_certainty_and_negation_fields_are_ignored_outside_dx_and_history() -> None:
    gold = [
        _letter(
            "L1",
            _annotation(
                "SeizureFrequency",
                "seizures",
                CUI="C0036572",
                NumberOfSeizures="2",
                TimePeriod="Month",
                Certainty="5",
                Negation="Affirmed",
            ),
        )
    ]
    pred = [
        _letter(
            "L1",
            _annotation(
                "SeizureFrequency",
                "seizures",
                CUI="C0036572",
                NumberOfSeizures="2",
                TimePeriod="Month",
                Certainty="1",
                Negation="Negated",
            ),
        )
    ]

    scores = score_published_metrics(gold, pred, ("SeizureFrequency",))

    assert scores.all_features.per_entity["SeizureFrequency"].per_item.f1 == 1.0


def test_published_negation_is_evaluated_for_history_but_not_diagnosis() -> None:
    gold = [
        _letter(
            "L1",
            _annotation(
                "Diagnosis",
                "epilepsy",
                CUI="C0014544",
                Certainty="5",
                Negation="Affirmed",
            ),
            _annotation(
                "PatientHistory",
                "febrile seizures",
                CUI="C0009952",
                Certainty="5",
                Negation="Affirmed",
            ),
        )
    ]
    pred = [
        _letter(
            "L1",
            _annotation(
                "Diagnosis",
                "epilepsy",
                CUI="C0014544",
                Certainty="5",
                Negation="Negated",
            ),
            _annotation(
                "PatientHistory",
                "febrile seizures",
                CUI="C0009952",
                Certainty="5",
                Negation="Negated",
            ),
        )
    ]

    scores = score_published_metrics(gold, pred, ("Diagnosis", "PatientHistory"))

    assert scores.all_features.per_entity["Diagnosis"].per_item.f1 == 1.0
    assert scores.all_features.per_entity["PatientHistory"].per_item.f1 == 0.0


def test_per_letter_requires_one_correct_feature_bundle_not_every_item() -> None:
    gold = [
        _letter(
            "L1",
            _annotation("Prescription", "drug-a", CUI="C1", DrugDose="100"),
            _annotation("Prescription", "drug-b", CUI="C2", DrugDose="200"),
        )
    ]
    pred = [
        _letter(
            "L1",
            _annotation("Prescription", "drug-a", CUI="C1", DrugDose="100"),
            _annotation("Prescription", "drug-b", CUI="C2", DrugDose="999"),
        )
    ]

    score = score_published_metrics(gold, pred, ("Prescription",)).all_features.per_entity[
        "Prescription"
    ]

    assert score.per_item.tp == 1
    assert score.per_item.fp == 1
    assert score.per_item.fn == 1
    assert score.per_letter.tp == 1
    assert score.per_letter.fp == 0
    assert score.per_letter.fn == 0


def test_paper_overall_is_macro_mean_of_entity_scores() -> None:
    gold = [
        _letter(
            "L1",
            _annotation("Diagnosis", "epilepsy", CUI="C1", Certainty="5"),
            _annotation("Prescription", "lamotrigine", CUI="C2", DrugDose="100"),
        )
    ]
    pred = [
        _letter(
            "L1",
            _annotation("Diagnosis", "epilepsy", CUI="C1", Certainty="5"),
            _annotation("Prescription", "lamotrigine", CUI="C2", DrugDose="200"),
        )
    ]

    score = score_published_metrics(
        gold,
        pred,
        ("Diagnosis", "Prescription"),
    ).all_features

    assert score.macro_per_item.f1 == pytest.approx(0.5)
    assert score.macro_per_letter.f1 == pytest.approx(0.5)


def test_duplicate_mentions_are_scored_as_a_multiset_within_each_letter() -> None:
    annotation = _annotation("Diagnosis", "epilepsy", CUI="C1", Certainty="5")
    gold = [_letter("L1", annotation, annotation)]
    pred = [_letter("L1", annotation)]

    score = score_published_metrics(gold, pred, ("Diagnosis",)).all_features.per_entity[
        "Diagnosis"
    ].per_item

    assert score.tp == 1
    assert score.fp == 0
    assert score.fn == 1
    assert score.f1 == pytest.approx(2 / 3)


def test_published_metric_report_keeps_paper_and_development_results_separate() -> None:
    gold = [
        _letter(
            "L1",
            _annotation("Diagnosis", "epilepsy", CUI="C1", Certainty="5"),
            _annotation("Prescription", "lamotrigine", CUI="C2", DrugDose="100"),
        )
    ]
    pred = [
        _letter(
            "L1",
            _annotation("Diagnosis", "epilepsy", CUI="C1", Certainty="5"),
            _annotation("Prescription", "lamotrigine", CUI="C2", DrugDose="200"),
        )
    ]

    report = published_metric_reproduction.build_published_metric_report(
        gold,
        pred,
        entities=("Diagnosis", "Prescription"),
        candidate_name="fixture",
        split="dev_fixture",
        generated_on="2026-07-14",
        source_revision="abc123",
        dirty_tree=True,
        python_version="3.test",
        dependency_versions={"pydantic": "2.test"},
        split_manifest="fixture.json",
        split_manifest_sha256="deadbeef",
    )

    assert report["paper_reference"]["overall_per_item_f1"] == 0.87
    assert report["paper_reference"]["overall_per_letter_f1"] == 0.9
    assert report["development_result"]["entity_coverage"] == "2/9"
    assert report["development_result"]["paper_comparable_nine_entity_overall"] is False
    assert report["development_result"]["scores"]["all_features"]["macro_per_item"]["f1"] == 0.5
    assert report["existing_score_regression"]["benchmark_micro"]["per_item"]["f1"] == 0.5
    assert report["call_mode"] == "no_call_deterministic_replay"
    categories = {
        example["category"]
        for example in report["development_result"]["mechanism_examples"]
    }
    assert "cui_match_feature_miss" in categories

    markdown = published_metric_reproduction.render_published_metric_report(
        report,
        json_path="fixture.json",
    )
    assert "# ExECTv2 published-metric reproduction" in markdown
    assert "not a reproduction of the original ExECTv2 system" in markdown
    assert "| Diagnosis |" in markdown
