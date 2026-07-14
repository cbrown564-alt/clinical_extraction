"""Architecture report assembly for the LLM-first essential evaluation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.audits.cui import (
    cui_projection_audit,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.constants import (
    ESSENTIAL_CLINICAL_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.ledger import (
    row_level_error_ledger,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.projection import (
    as_predicted,
    strip_and_project,
    strip_gold_cui,
    strip_prediction_cui,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.recovery import (
    clinical_fidelity_companions,
    error_taxonomy_summary,
    evidence_validation_summary,
    primary_recovery,
)

from ..clinical_recovery_scorecard import (
    ARTIFACT_LAYER_ENTITIES,
    build_scorecard,
)
from .audits.certainty import (
    certainty_projection_audit,
)


def architecture_report(
    *,
    name: str,
    ownership: str,
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
    entities: Sequence[str] = ARTIFACT_LAYER_ENTITIES,
    include_row_error_ledger: bool = False,
) -> dict[str, Any]:
    """Build the full layer ladder for one architecture over one artifact."""

    predicted = as_predicted(pred_letters)
    cui_free_gold = strip_gold_cui(gold_letters)
    cui_free_predicted = strip_prediction_cui(predicted)
    cui_free_scorecard = build_scorecard(cui_free_gold, cui_free_predicted)
    primary_overall, primary_scores = primary_recovery(cui_free_scorecard)

    fidelity_companions = clinical_fidelity_companions(cui_free_scorecard)

    projected = strip_and_project(predicted)
    projected_scorecard = build_scorecard(gold_letters, projected)
    projected_overall, projected_scores = primary_recovery(projected_scorecard)
    nonessential = {
        entity: cui_free_scorecard["headline_scores"][entity]["headline"]
        for entity in cui_free_scorecard["headline_entities"]
        if entity not in ESSENTIAL_CLINICAL_ENTITIES
    }
    evidence_summary = evidence_validation_summary(
        gold_letters,
        predicted,
        ESSENTIAL_CLINICAL_ENTITIES,
    )
    report = {
        "name": name,
        "ownership": ownership,
        "row_count": len(gold_letters),
        "clinical_recovery_note": (
            "Primary clinical-recovery headline is CUI-free and aggregates only "
            "the five essential families. A CUI-projected companion score is "
            "reported separately because the legacy SeizureFrequency state key "
            "uses CUI as seizure-type identity when present."
        ),
        "clinical_recovery": {
            "primary_entities": list(ESSENTIAL_CLINICAL_ENTITIES),
            "overall": primary_overall,
            "headline_scores": primary_scores,
            "cui_projected_overall": projected_overall,
            "cui_projected_headline_scores": projected_scores,
            "fidelity_companions": fidelity_companions,
            "diagnostic_nonessential_scores": nonessential,
            "artifact_projection_scores": projected_scorecard["artifact_projection_scores"],
        },
        "evidence_validation": evidence_summary,
        "error_taxonomy": error_taxonomy_summary(primary_scores, evidence_summary),
        "certainty_audit": certainty_projection_audit(gold_letters, predicted, entities),
        "cui_audit": cui_projection_audit(gold_letters, predicted, entities),
    }
    if include_row_error_ledger:
        report["row_error_ledger"] = row_level_error_ledger(
            architecture=name,
            ownership=ownership,
            gold_letters=gold_letters,
            pred_letters=predicted,
        )
    return report
