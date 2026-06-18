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
    ESSENTIAL_CLINICAL_ENTITIES,
    align_predictions_to_gold,
    architecture_report,
    certainty_projection_audit,
    cui_concept_buckets,
    project_guideline_certainty_negation,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_first_essential_evaluation import (  # noqa: E501
    render_markdown,
)


def _gold(
    letter_id: str,
    mentions: list[ExectAnnotation],
    note_text: str = "",
) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note_text, annotations=tuple(mentions))


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


def test_guideline_certainty_projection_rules_cover_triggers_and_febrile_negation() -> None:
    assert project_guideline_certainty_negation(
        "Diagnosis",
        "complex partial seizures",
        "She is having possible complex partial seizures.",
    ) == {"Certainty": "3", "Negation": "Affirmed"}
    assert project_guideline_certainty_negation(
        "EpilepsyCause",
        "perinatal insult",
        "The MRI changes are probably representative of a perinatal insult.",
    ) == {"Certainty": "4", "Negation": "Affirmed"}
    assert project_guideline_certainty_negation(
        "PatientHistory",
        "febrile seizures",
        "There is no history of febrile seizures, head injury or meningitis.",
    ) == {"Certainty": "1", "Negation": "Negated"}
    assert project_guideline_certainty_negation(
        "Investigations",
        "EEG",
        "The EEG was normal.",
    ) == {}


def test_cui_buckets_split_consistent_inconsistent_and_result_conditioned() -> None:
    gold = [
        _gold("EA1", [
            # one_to_one: single CUI for the concept
            ExectAnnotation("Diagnosis", "epilepsy", {"CUIPhrase": "epilepsy", "CUI": "C0014544"}),
            # result_conditioned: Investigations concept with >1 CUI
            ExectAnnotation(
                "Investigations",
                "eeg",
                {"CUIPhrase": "EEG", "CUI": "C0151611", "EEG_Results": "Abnormal"},
            ),
        ]),
        _gold("EA2", [
            ExectAnnotation("Diagnosis", "epilepsy", {"CUIPhrase": "epilepsy", "CUI": "C0014544"}),
            ExectAnnotation(
                "Investigations",
                "eeg",
                {"CUIPhrase": "EEG", "CUI": "C0744602", "EEG_Results": "Normal"},
            ),
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


def test_architecture_report_primary_headline_is_essential_only() -> None:
    gold = [
        _gold("EA1", [
            ExectAnnotation("Diagnosis", "epilepsy", {"Certainty": "5", "Negation": "Affirmed"}),
            ExectAnnotation("Onset", "childhood", {"Certainty": "5", "Negation": "Affirmed"}),
        ])
    ]
    pred = [
        _pred("EA1", [
            PredictedMention(
                entity="Diagnosis",
                text="epilepsy",
                attributes={"Certainty": "5", "Negation": "Affirmed"},
                evidence="epilepsy",
            )
        ])
    ]
    report = architecture_report(
        name="t", ownership="llm_first", gold_letters=gold, pred_letters=pred
    )
    assert tuple(report["clinical_recovery"]["primary_entities"]) == ESSENTIAL_CLINICAL_ENTITIES
    assert set(report["clinical_recovery"]["headline_scores"]) == set(ESSENTIAL_CLINICAL_ENTITIES)
    assert report["clinical_recovery"]["overall"]["f1"] == 1.0
    assert "Onset" in report["clinical_recovery"]["diagnostic_nonessential_scores"]


def test_architecture_report_separates_cui_free_and_projected_sf_recovery() -> None:
    gold = [
        _gold("EA1", [
            ExectAnnotation(
                "SeizureFrequency",
                "seizures",
                {"CUI": "C0036572", "NumberOfSeizures": "2"},
            )
        ])
    ]
    pred = [
        _pred("EA1", [
            PredictedMention(
                entity="SeizureFrequency",
                text="seizures",
                attributes={"NumberOfSeizures": "2"},
                evidence="seizures twice a month",
            )
        ])
    ]
    report = architecture_report(
        name="t", ownership="llm_first", gold_letters=gold, pred_letters=pred
    )
    assert report["clinical_recovery"]["overall"]["f1"] == 1.0
    assert report["clinical_recovery"]["cui_projected_overall"]["f1"] == 1.0
    assert "CUI-free" in report["clinical_recovery_note"]


def test_architecture_report_includes_evidence_and_error_summary() -> None:
    gold = [
        _gold("EA1", [
            ExectAnnotation("Diagnosis", "epilepsy", {"Certainty": "5", "Negation": "Affirmed"}),
            ExectAnnotation("EpilepsyCause", "stroke", {"Certainty": "5", "Negation": "Affirmed"}),
        ], note_text="The patient has epilepsy after a stroke.")
    ]
    pred = [
        _pred("EA1", [
            PredictedMention(
                entity="Diagnosis",
                text="epilepsy",
                attributes={"Certainty": "5", "Negation": "Affirmed"},
                evidence="epilepsy",
            ),
            PredictedMention(
                entity="Diagnosis",
                text="migraine",
                attributes={"Certainty": "5", "Negation": "Affirmed"},
                evidence="not in note text",
            ),
        ])
    ]
    report = architecture_report(
        name="t", ownership="llm_first", gold_letters=gold, pred_letters=pred
    )
    evidence = report["evidence_validation"]
    assert evidence["overall"]["predicted_mentions"] == 2
    assert evidence["overall"]["exact_evidence_rate"] == 0.5
    errors = report["error_taxonomy"]["overall"]
    assert errors["candidate_miss"] == 1
    assert errors["wrong_detail_selection"] == 1
    assert errors["evidence_failure"] == 1


def test_render_markdown_surfaces_diagnostic_limitations() -> None:
    arch = architecture_report(
        name="t",
        ownership="llm_first",
        gold_letters=[_gold("EA1", [ExectAnnotation("Diagnosis", "epilepsy", {})])],
        pred_letters=[_pred("EA1", [])],
    )
    report = {
        "plan": "plan.md",
        "split": "dev",
        "row_count": 1,
        "generated_on": "2026-06-18",
        "sources": {"llm_first": "artifact.jsonl"},
        "architectures": [arch],
    }
    md = render_markdown(report)
    assert "Evidence validation and error taxonomy" in md
    assert "Guideline projection accuracy over gold rows" in md
    assert "missing_mapping" in md
