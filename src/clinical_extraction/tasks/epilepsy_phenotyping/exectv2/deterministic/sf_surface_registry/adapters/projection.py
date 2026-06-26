"""Projection-phase adapter — Stack C facade over registry builders + policy."""

from __future__ import annotations

from collections.abc import Sequence
from types import SimpleNamespace
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
    project_context_parent_epilepsy,
    project_controlled_context_to_infrequent_state,
    project_diagnosis_context_to_sf_states,
    project_diagnosis_frequency_header_to_sf,
    project_diagnosis_header_parent_epilepsy,
    project_dated_diagnosis_context_to_sf,
    project_dropped_sf_to_diagnosis,
    project_empty_sf_candidate_to_diagnosis,
    project_focal_diagnosis_context_to_sf,
    project_infrequent_context_state,
    project_returned_context_to_increased_state,
    project_sf_context_to_focal_diagnosis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
    frequency_from_prescription_source,
    repair_case_only_evidence,
    repair_prescription_attrs_from_text,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_sf_state import (
    project_diagnosis_text_from_evidence,
    project_sf_state_from_evidence,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.constants import (
    ASYMMETRIC_DOSING,
    CONTROLLED_ON_DOSE,
    EVERY_N_PERIODS,
    EVERY_N_TO_M_PERIODS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.investigations import (
    project_eeg_context_to_mri_normal,
    project_mri_context_to_eeg_result,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.policy import (
    ProjectionFamilySwitches,
    audit_only_projection_replay_switches,
    effective_target_projection_family_switches,
    is_projection_family_enabled,
    quarantined_projection_family_warning,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.shared import (
    clean_number,
    local_evidence_context,
)

projection_patterns = SimpleNamespace(
    ASYMMETRIC_DOSING=ASYMMETRIC_DOSING,
    CONTROLLED_ON_DOSE=CONTROLLED_ON_DOSE,
    EVERY_N_PERIODS=EVERY_N_PERIODS,
    EVERY_N_TO_M_PERIODS=EVERY_N_TO_M_PERIODS,
    clean_number=clean_number,
    local_evidence_context=local_evidence_context,
)


class _ProjectionAdapter:
    """Facade over target_projection for the target-indicators post-process path."""

    def empty_sf_candidate(self, mention: Any) -> Any | None:
        return project_empty_sf_candidate_to_diagnosis(mention)

    def repair_evidence(
        self,
        mentions: Sequence[Any],
        *,
        note_text: str,
        projection_family_switches: ProjectionFamilySwitches | None = None,
    ) -> tuple[list[Any], list[str]]:
        return repair_case_only_evidence(
            mentions,
            note_text=note_text,
            projection_family_switches=projection_family_switches,
        )

    def normalize_prescription_attributes(
        self,
        normalized: dict[str, str],
        *,
        text: str,
        evidence: str,
    ) -> list[str]:
        return repair_prescription_attrs_from_text(
            normalized,
            source=f"{text} {evidence}",
        )

    def prescription_frequency_from_evidence(self, normalized_evidence: str) -> str | None:
        return frequency_from_prescription_source(normalized_evidence)

    def is_quarantined_family_enabled(
        self,
        family: str,
        switches: ProjectionFamilySwitches | None,
    ) -> bool:
        return is_projection_family_enabled(family, switches)

    def quarantine_warning(self, family: str) -> str:
        return quarantined_projection_family_warning(family)

    def project_sf_state(
        self,
        text: str,
        attrs: dict[str, str],
        evidence: str,
        *,
        projection_family_switches: ProjectionFamilySwitches | None = None,
    ) -> tuple[str, dict[str, str], list[str]]:
        return project_sf_state_from_evidence(
            text,
            attrs,
            evidence,
            projection_family_switches=projection_family_switches,
        )

    def project_dropped_sf(
        self,
        text: str,
        evidence: str,
        mention: Any,
        *,
        component_owner: str,
    ) -> PredictedMention | None:
        return project_dropped_sf_to_diagnosis(
            text,
            evidence,
            mention,
            component_owner=component_owner,
        )

    def project_diagnosis_frequency_header(
        self,
        base_mention: PredictedMention,
        note_text: str,
    ) -> PredictedMention | None:
        return project_diagnosis_frequency_header_to_sf(base_mention, note_text)

    def normalize_diagnosis_text(self, text: str, evidence: str) -> str:
        return project_diagnosis_text_from_evidence(text, evidence)

    def expand_mention_projections(
        self,
        *,
        entity: str,
        base_mention: PredictedMention,
        expanded_mentions: list[PredictedMention],
        note_text: str,
        text: str,
        projection_family_switches: ProjectionFamilySwitches | None = None,
    ) -> tuple[list[PredictedMention], list[str]]:
        warnings: list[str] = []
        if entity == "Diagnosis":
            context_parent = project_context_parent_epilepsy(base_mention, note_text)
            if context_parent is not None:
                expanded_mentions.append(context_parent)
                warnings.append("Diagnosis: projected_context_parent_epilepsy")
            diagnosis_sf_states, diagnosis_sf_state_warnings = (
                project_diagnosis_context_to_sf_states(
                    base_mention,
                    note_text,
                    projection_family_switches=projection_family_switches,
                )
            )
            if diagnosis_sf_states:
                expanded_mentions.extend(diagnosis_sf_states)
            warnings.extend(
                f"Diagnosis: {warning}" for warning in diagnosis_sf_state_warnings
            )
            projected_sf = project_focal_diagnosis_context_to_sf(
                base_mention,
                note_text,
            )
            if projected_sf is not None:
                expanded_mentions.append(projected_sf)
                warnings.append(
                    "Diagnosis: projected_focal_diagnosis_context_to_sf_state: "
                    f"{text!r}"
                )
            projected_parent = project_diagnosis_header_parent_epilepsy(
                base_mention,
                note_text,
            )
            if projected_parent is not None:
                expanded_mentions.append(projected_parent)
                warnings.append("Diagnosis: projected_header_parent_epilepsy")
            projected_dated_sf = project_dated_diagnosis_context_to_sf(
                base_mention,
                note_text,
            )
            if projected_dated_sf is not None:
                expanded_mentions.append(projected_dated_sf)
                warnings.append("Diagnosis: projected_dated_diagnosis_context_to_sf")
        if entity == "SeizureFrequency":
            projected_diagnosis = project_sf_context_to_focal_diagnosis(
                base_mention,
                note_text,
            )
            if projected_diagnosis is not None:
                expanded_mentions.append(projected_diagnosis)
                warnings.append(
                    "SeizureFrequency: projected_sf_context_to_focal_diagnosis: "
                    f"{text!r}"
                )
            controlled_state = project_controlled_context_to_infrequent_state(
                base_mention,
                note_text,
            )
            if controlled_state is not None:
                expanded_mentions.append(controlled_state)
                warnings.append(
                    "SeizureFrequency: projected_controlled_context_to_infrequent_state"
                )
            infrequent_state = project_infrequent_context_state(
                base_mention,
                note_text,
            )
            if infrequent_state is not None:
                family = "projected_infrequent_context_state"
                if is_projection_family_enabled(
                    family,
                    projection_family_switches,
                ):
                    expanded_mentions.append(infrequent_state)
                    warnings.append(f"SeizureFrequency: {family}")
                else:
                    warnings.append(
                        "SeizureFrequency: "
                        + quarantined_projection_family_warning(family)
                    )
            increased_state = project_returned_context_to_increased_state(
                base_mention,
                note_text,
            )
            if increased_state is not None:
                expanded_mentions.append(increased_state)
                warnings.append(
                    "SeizureFrequency: projected_returned_context_to_increased_state"
                )
        if entity == "Investigations":
            projected_mri = project_eeg_context_to_mri_normal(
                base_mention,
                note_text,
            )
            if projected_mri is not None:
                expanded_mentions.append(projected_mri)
                warnings.append("Investigations: projected_eeg_context_to_mri_normal")
            projected_eeg = project_mri_context_to_eeg_result(
                base_mention,
                note_text,
            )
            if projected_eeg is not None:
                expanded_mentions.append(projected_eeg)
                warnings.append("Investigations: projected_mri_context_to_eeg_result")
        return expanded_mentions, warnings


apply_all = _ProjectionAdapter()

__all__ = [
    "ProjectionFamilySwitches",
    "apply_all",
    "audit_only_projection_replay_switches",
    "effective_target_projection_family_switches",
    "projection_patterns",
]
