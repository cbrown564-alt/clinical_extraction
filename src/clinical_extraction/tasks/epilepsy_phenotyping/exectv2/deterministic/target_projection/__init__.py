"""Deterministic projection and evidence-repair policy for target indicators (Stack C).

.. deprecated::
    Prefer ``sf_surface_registry.adapters.projection`` for new SF-related imports.
    Shared regex patterns live in ``sf_surface_registry.patterns`` (Phase 1).
    This package remains the authoritative projection implementation until Phase 3
    registers rules in ``catalog/projection_sf.yaml`` and derives quarantine policy
    from the registry; it will become thin re-export shims for one release cycle
    after ``adapters.projection`` owns the facade.

Non-SF projection (EEG/MRI investigations, prescription repair) may later move to
a sibling ``target_projection_registry``; see design doc non-goals.

See ``sf_surface_registry/README.md`` for migration status.
"""

from __future__ import annotations

from .constants import (
    ASYMMETRIC_DOSING,
    CONTROLLED_ON_DOSE,
    EVERY_N_PERIODS,
    EVERY_N_TO_M_PERIODS,
)
from .cross_entity import (
    controlled_focal_seizures_evidence,
    frequent_myoclonic_jerks_evidence,
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
    remote_last_seizures_evidence,
)
from .investigations import (
    project_eeg_context_to_mri_normal,
    project_mri_context_to_eeg_result,
)
from .evidence_repair import (
    extend_asymmetric_prescription_evidence,
    extend_probable_temporal_diagnosis_evidence,
    frequency_from_prescription_source,
    is_daily_total_dose,
    repair_absence_like_frequency_evidence,
    repair_case_only_evidence,
    repair_ellipsis_evidence,
    repair_no_further_since_evidence,
    repair_prescription_attrs_from_text,
    repair_prescription_frequency_synonym_evidence,
    repair_since_last_clinic_count_evidence,
    repair_whitespace_equivalent_evidence,
)
from .policy import (
    ProjectionFamilySwitches,
    audit_only_projection_replay_switches,
    effective_target_projection_family_switches,
    is_projection_family_enabled,
    quarantined_projection_family_warning,
)
from .sf_state import (
    project_diagnosis_text_from_evidence,
    project_sf_state_from_evidence,
)
from .shared import clean_number, local_evidence_context, period_to_canonical

__all__ = [
    "ASYMMETRIC_DOSING",
    "CONTROLLED_ON_DOSE",
    "EVERY_N_PERIODS",
    "EVERY_N_TO_M_PERIODS",
    "ProjectionFamilySwitches",
    "audit_only_projection_replay_switches",
    "clean_number",
    "controlled_focal_seizures_evidence",
    "effective_target_projection_family_switches",
    "extend_asymmetric_prescription_evidence",
    "extend_probable_temporal_diagnosis_evidence",
    "frequency_from_prescription_source",
    "frequent_myoclonic_jerks_evidence",
    "is_daily_total_dose",
    "is_projection_family_enabled",
    "local_evidence_context",
    "period_to_canonical",
    "project_context_parent_epilepsy",
    "project_controlled_context_to_infrequent_state",
    "project_diagnosis_context_to_sf_states",
    "project_diagnosis_frequency_header_to_sf",
    "project_diagnosis_header_parent_epilepsy",
    "project_diagnosis_text_from_evidence",
    "project_dated_diagnosis_context_to_sf",
    "project_dropped_sf_to_diagnosis",
    "project_eeg_context_to_mri_normal",
    "project_empty_sf_candidate_to_diagnosis",
    "project_focal_diagnosis_context_to_sf",
    "project_infrequent_context_state",
    "project_mri_context_to_eeg_result",
    "project_returned_context_to_increased_state",
    "project_sf_context_to_focal_diagnosis",
    "project_sf_state_from_evidence",
    "quarantined_projection_family_warning",
    "remote_last_seizures_evidence",
    "repair_absence_like_frequency_evidence",
    "repair_case_only_evidence",
    "repair_ellipsis_evidence",
    "repair_no_further_since_evidence",
    "repair_prescription_attrs_from_text",
    "repair_prescription_frequency_synonym_evidence",
    "repair_since_last_clinic_count_evidence",
    "repair_whitespace_equivalent_evidence",
]
