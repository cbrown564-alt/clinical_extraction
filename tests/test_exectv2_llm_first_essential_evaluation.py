"""Tests for the LLM-first essential clinical evaluation (plan satellite 11)."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first_essential_evaluation import (  # noqa: E501
    align_predictions_to_gold,
    architecture_report,
    certainty_projection_audit,
    cui_concept_buckets,
)


def _gold(letter_id: str, mentions: list[ExectAnnotation]) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text="", annotations=tuple(mentions))


def _pred(letter_id: str, mentions: list[PredictedMention]) -> PredictedLetter:
    return PredictedLetter(letter_id=letter_id, mentions=tuple(mentions))


def test_certainty_distribution_and_default_ceiling() -> None:
    affirmed5 = {"Certainty": "5", "Negation": "Affirmed"}
    gold = [
        _gold("EA1", [ExectAnnotation("Diagnosis", "epilepsy", dict(affirmed5))]),
        _gold("EA2", [ExectAnnotation("Diagnosis", "focal epilepsy", dict(affirmed5))]),
        _gold("EA3", [
            ExectAnnotation("Diagnosis", "jme", {"Certainty": "4", "Negation": "Affirmed"}),
        ]),
    ]
    pred = [_pred(g.letter_id, []) for g in gold]
    audit = certainty_projection_audit(gold, pred, ["Diagnosis"])
    diag = audit["per_entity"]["Diagnosis"]
    assert diag["certainty"]["present"] == 3
    assert diag["certainty"]["distinct_values"] == 2
    # Dominant value "5" covers 2/3 of mentions.
    assert diag["certainty"]["default_projection_ceiling"] == round(2 / 3, 4)
    # Negation is constant -> a default rule is always right.
    assert diag["negation"]["default_projection_ceiling"] == 1.0


def test_cui_buckets_split_consistent_inconsistent_and_result_conditioned() -> None:
    gold = [
        _gold("EA1", [
            # one_to_one: single CUI for the concept
            ExectAnnotation("Diagnosis", "epilepsy", {"CUIPhrase": "epilepsy", "CUI": "C0014544"}),
            # result_conditioned: Investigations concept with >1 CUI
            ExectAnnotation("Investigations", "eeg", {"CUIPhrase": "EEG", "CUI": "C0151611"}),
        ]),
        _gold("EA2", [
            ExectAnnotation("Diagnosis", "epilepsy", {"CUIPhrase": "epilepsy", "CUI": "C0014544"}),
            ExectAnnotation("Investigations", "eeg", {"CUIPhrase": "EEG", "CUI": "C0744602"}),
            # gold_inconsistent: same non-investigation concept, two CUIs
            ExectAnnotation("EpilepsyCause", "stroke", {"CUIPhrase": "stroke", "CUI": "C0038454"}),
        ]),
        _gold("EA3", [
            ExectAnnotation("EpilepsyCause", "stroke", {"CUIPhrase": "stroke", "CUI": "C0999999"}),
        ]),
    ]
    buckets = cui_concept_buckets(gold, ["Diagnosis", "Investigations", "EpilepsyCause"])
    assert buckets["bucket_concepts"]["one_to_one"] == 1
    assert buckets["bucket_concepts"]["result_conditioned"] == 1
    assert buckets["bucket_concepts"]["gold_inconsistent"] == 1


def test_align_predictions_emits_empty_for_missing() -> None:
    gold = [_gold("EA1", []), _gold("EA2", [])]
    mention = PredictedMention(entity="Diagnosis", text="epilepsy", attributes={}, evidence="")
    by_id = {"EA1": _pred("EA1", [mention])}
    aligned = align_predictions_to_gold(gold, by_id)
    assert [p.letter_id for p in aligned] == ["EA1", "EA2"]
    assert len(aligned[0].mentions) == 1
    assert len(aligned[1].mentions) == 0  # missing -> empty letter


def test_architecture_report_carries_ownership_and_layers() -> None:
    gold_attrs = {"DiagCategory": "Epilepsy", "CUIPhrase": "epilepsy", "CUI": "C0014544"}
    gold = [_gold("EA1", [ExectAnnotation("Diagnosis", "epilepsy", gold_attrs)])]
    pred = [_pred("EA1", [
        PredictedMention(
            entity="Diagnosis", text="epilepsy",
            attributes={"DiagCategory": "Epilepsy"}, evidence="",
        )
    ])]
    report = architecture_report(
        name="t", ownership="llm_first", gold_letters=gold, pred_letters=pred
    )
    assert report["ownership"] == "llm_first"
    assert "overall" in report["clinical_recovery"]
    assert "concept_buckets" in report["cui_audit"]
    assert "per_entity" in report["certainty_audit"]
