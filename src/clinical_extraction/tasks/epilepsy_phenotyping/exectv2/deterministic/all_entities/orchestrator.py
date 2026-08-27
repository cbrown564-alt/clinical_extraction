"""Orchestrator for deterministic all-entity extraction."""

from __future__ import annotations

from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    BIRTH_HISTORY,
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    INVESTIGATIONS,
    ONSET,
    PATIENT_HISTORY,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
    WHEN_DIAGNOSED,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from ..mention_identity import dedupe_mentions
from ..pipeline import extract_seizure_frequency
from .birth_history import _extract_birth_history
from .common import _rule_family_summary
from .diagnosis import _extract_diagnoses
from .epilepsy_cause import _extract_epilepsy_causes
from .investigations import _extract_investigations
from .onset import _extract_onsets
from .patient_history import _extract_patient_history
from .prescription import _extract_prescriptions
from .when_diagnosed import _extract_when_diagnosed

ACTIVE_DETERMINISTIC_ENTITIES: tuple[str, ...] = (
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
    DIAGNOSIS.name,
    ONSET.name,
    WHEN_DIAGNOSED.name,
    BIRTH_HISTORY.name,
    EPILEPSY_CAUSE.name,
    PATIENT_HISTORY.name,
    SEIZURE_FREQUENCY.name,
)


def extract_deterministic_all9(
    letter: ExectLetter,
    *,
    include_diagnosis_resolution_candidate: bool = False,
    include_diagnosis_benchmark_residuals: bool = False,
    keep_unassociated_sf_anchors: bool = False,
    diagnosis_service_context_exclusion: bool = False,
    diagnosis_secondary_to_retention: bool = False,
    diagnosis_focal_onset_alias: bool = False,
) -> PredictedLetter:
    """Extract the active deterministic baseline entities from one letter."""

    sf_prediction = extract_seizure_frequency(
        letter,
        keep_unassociated_anchors=keep_unassociated_sf_anchors,
    )
    mentions = (
        *_extract_diagnoses(
            letter.note_text,
            include_resolution_candidate=include_diagnosis_resolution_candidate,
            include_benchmark_residuals=include_diagnosis_benchmark_residuals,
            service_context_exclusion=diagnosis_service_context_exclusion,
            secondary_to_retention=diagnosis_secondary_to_retention,
            focal_onset_alias=diagnosis_focal_onset_alias,
        ),
        *_extract_investigations(letter.note_text),
        *_extract_onsets(letter.note_text),
        *_extract_when_diagnosed(letter.note_text),
        *_extract_birth_history(letter.note_text),
        *_extract_epilepsy_causes(letter.note_text),
        *_extract_patient_history(letter.note_text),
        *_extract_prescriptions(letter.note_text),
        *sf_prediction.mentions,
    )
    mentions = dedupe_mentions(mentions)
    counts = {
        entity: sum(1 for mention in mentions if mention.entity == entity)
        for entity in ACTIVE_DETERMINISTIC_ENTITIES
    }
    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=mentions,
        diagnostics={
            "architecture_track": "rules_only",
            "rule_set": "deterministic_all9_v0_active_structured_plus_sf",
            "active_entities": ACTIVE_DETERMINISTIC_ENTITIES,
            "entity_counts": counts,
            "diagnosis_resolution_candidate": include_diagnosis_resolution_candidate,
            "diagnosis_benchmark_residuals": include_diagnosis_benchmark_residuals,
            "sf_diagnostics": sf_prediction.diagnostics,
            "rule_families": _rule_family_summary(),
        },
    )


def run_all9_on_letters(
    letters: Sequence[ExectLetter],
    *,
    include_diagnosis_resolution_candidate: bool = False,
    include_diagnosis_benchmark_residuals: bool = False,
) -> list[PredictedLetter]:
    """Compatibility batch adapter for the retained all-nine output."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
        run_all9_on_letters as canonical_run_all9_on_letters,
    )

    return canonical_run_all9_on_letters(
        letters,
        include_diagnosis_resolution_candidate=include_diagnosis_resolution_candidate,
        include_diagnosis_benchmark_residuals=include_diagnosis_benchmark_residuals,
    )
