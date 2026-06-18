"""Tests for the ExECTv2 benchmark CUI-projection ablation (satellite 09, Phase D)."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.cui_projection_diagnostic import (
    cui_projection_diagnostic,
    render_markdown,
)


def _letter(letter_id: str, mentions: list[ExectAnnotation]) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text="", annotations=tuple(mentions))


def test_coverage_and_agreement() -> None:
    gold = [
        _letter(
            "EA0001",
            [
                ExectAnnotation("Diagnosis", "focal epilepsy",
                                {"DiagCategory": "Epilepsy", "CUI": "C0014547"}),
                ExectAnnotation("Diagnosis", "jme",
                                {"DiagCategory": "Epilepsy", "CUI": "C0270853"}),
            ],
        )
    ]
    pred = [
        _letter(
            "EA0001",
            [
                # overlap, correct CUI
                ExectAnnotation("Diagnosis", "focal epilepsy",
                                {"DiagCategory": "Epilepsy", "CUI": "C0014547"}),
                # overlap, no CUI -> coverage miss
                ExectAnnotation("Diagnosis", "jme", {"DiagCategory": "Epilepsy"}),
            ],
        )
    ]
    diag = cui_projection_diagnostic(gold, pred, ["Diagnosis"])
    d = diag.per_entity["Diagnosis"]
    assert d.predicted_mentions == 2
    assert d.predicted_with_cui == 1
    assert d.coverage == 0.5
    assert d.gold_cui_density == 1.0
    assert d.overlap_pairs == 2
    assert d.cui_both_present == 1
    assert d.cui_agree == 1
    assert d.cui_agreement_rate == 1.0


def test_disagreement_counted() -> None:
    gold = [_letter("EA1", [ExectAnnotation("Onset", "epilepsy", {"CUI": "C0014544"})])]
    pred = [_letter("EA1", [ExectAnnotation("Onset", "epilepsy", {"CUI": "C9999999"})])]
    diag = cui_projection_diagnostic(gold, pred, ["Onset"])
    d = diag.per_entity["Onset"]
    assert d.cui_both_present == 1
    assert d.cui_agree == 0
    assert d.cui_agreement_rate == 0.0


def test_overall_micro_average() -> None:
    gold = [
        _letter("EA1", [ExectAnnotation("Diagnosis", "epilepsy", {"CUI": "C0014544"})]),
        _letter("EA2", [ExectAnnotation("Prescription", "lamotrigine", {"CUI": "C0064636"})]),
    ]
    pred = [
        _letter("EA1", [ExectAnnotation("Diagnosis", "epilepsy", {"CUI": "C0014544"})]),
        _letter("EA2", [ExectAnnotation("Prescription", "lamotrigine", {})]),
    ]
    diag = cui_projection_diagnostic(gold, pred, ["Diagnosis", "Prescription"])
    assert diag.overall.predicted_mentions == 2
    assert diag.overall.predicted_with_cui == 1
    assert diag.overall.coverage == 0.5


def test_render_markdown_has_overall_row() -> None:
    gold = [_letter("EA1", [ExectAnnotation("Diagnosis", "epilepsy", {"CUI": "C0014544"})])]
    pred = [_letter("EA1", [ExectAnnotation("Diagnosis", "epilepsy", {"CUI": "C0014544"})])]
    diag = cui_projection_diagnostic(gold, pred, ["Diagnosis"])
    md = render_markdown(diag, entities=["Diagnosis"])
    assert "| overall |" in md
    assert "CUI projection is a deterministic post-step" in md
