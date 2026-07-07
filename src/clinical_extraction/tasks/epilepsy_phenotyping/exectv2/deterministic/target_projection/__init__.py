"""Deterministic projection and evidence-repair policy for target indicators (Stack C).

SF projection implementations live in ``sf_surface_registry/builders/projection_*``.
Non-SF investigation projection remains here until a sibling registry exists.

Prefer ``sf_surface_registry.adapters.projection`` for the target-indicators post-process path.

Builder symbols are re-exported **lazily** (PEP 562 ``__getattr__``) to avoid an
import cycle: ``sf_surface_registry.builders.projection_cross_entity`` imports
``target_projection.constants``, which runs this package ``__init__``. Eagerly
importing the builders here would re-enter the still-initializing
``projection_cross_entity`` module and raise ``ImportError`` on a partially
initialized name (e.g. ``controlled_focal_seizures_evidence``). The local
submodule re-exports below do not import back into the builders, so they stay eager.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from .constants import (
    ASYMMETRIC_DOSING,
    CONTROLLED_ON_DOSE,
    EVERY_N_PERIODS,
    EVERY_N_TO_M_PERIODS,
)
from .investigations import (
    project_eeg_context_to_mri_normal,
    project_mri_context_to_eeg_result,
)
from .policy import (
    ProjectionFamilySwitches,
    audit_only_projection_replay_switches,
    effective_target_projection_family_switches,
    is_projection_family_enabled,
    quarantined_projection_family_warning,
)
from .shared import clean_number, local_evidence_context, period_to_canonical

_BUILDER_PKG = (
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic"
    ".sf_surface_registry.builders"
)

# name -> builder submodule, resolved lazily by ``__getattr__`` (see docstring).
_LAZY_EXPORTS: dict[str, str] = {
    # projection_cross_entity
    "controlled_focal_seizures_evidence": "projection_cross_entity",
    "frequent_myoclonic_jerks_evidence": "projection_cross_entity",
    "project_context_parent_epilepsy": "projection_cross_entity",
    "project_controlled_context_to_infrequent_state": "projection_cross_entity",
    "project_diagnosis_context_to_sf_states": "projection_cross_entity",
    "project_diagnosis_frequency_header_to_sf": "projection_cross_entity",
    "project_diagnosis_header_parent_epilepsy": "projection_cross_entity",
    "project_dated_diagnosis_context_to_sf": "projection_cross_entity",
    "project_dropped_sf_to_diagnosis": "projection_cross_entity",
    "project_empty_sf_candidate_to_diagnosis": "projection_cross_entity",
    "project_focal_diagnosis_context_to_sf": "projection_cross_entity",
    "project_infrequent_context_state": "projection_cross_entity",
    "project_returned_context_to_increased_state": "projection_cross_entity",
    "project_sf_context_to_focal_diagnosis": "projection_cross_entity",
    "remote_last_seizures_evidence": "projection_cross_entity",
    # projection_evidence_repair
    "extend_asymmetric_prescription_evidence": "projection_evidence_repair",
    "extend_probable_temporal_diagnosis_evidence": "projection_evidence_repair",
    "frequency_from_prescription_source": "projection_evidence_repair",
    "is_daily_total_dose": "projection_evidence_repair",
    "repair_absence_like_frequency_evidence": "projection_evidence_repair",
    "repair_case_only_evidence": "projection_evidence_repair",
    "repair_ellipsis_evidence": "projection_evidence_repair",
    "repair_no_further_since_evidence": "projection_evidence_repair",
    "repair_prescription_attrs_from_text": "projection_evidence_repair",
    "repair_prescription_frequency_synonym_evidence": "projection_evidence_repair",
    "repair_since_last_clinic_count_evidence": "projection_evidence_repair",
    "repair_whitespace_equivalent_evidence": "projection_evidence_repair",
    # projection_sf_state
    "project_diagnosis_text_from_evidence": "projection_sf_state",
    "project_sf_state_from_evidence": "projection_sf_state",
}


def __getattr__(name: str) -> object:
    submodule = _LAZY_EXPORTS.get(name)
    if submodule is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(f"{_BUILDER_PKG}.{submodule}"), name)
    globals()[name] = value  # cache so subsequent access skips __getattr__
    return value


def __dir__() -> list[str]:
    return sorted(__all__)


if TYPE_CHECKING:  # eager re-exports for type checkers / IDEs only (no runtime cycle)
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        controlled_focal_seizures_evidence as controlled_focal_seizures_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        frequent_myoclonic_jerks_evidence as frequent_myoclonic_jerks_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_context_parent_epilepsy as project_context_parent_epilepsy,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_controlled_context_to_infrequent_state as project_controlled_context_to_infrequent_state,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_dated_diagnosis_context_to_sf as project_dated_diagnosis_context_to_sf,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_diagnosis_context_to_sf_states as project_diagnosis_context_to_sf_states,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_diagnosis_frequency_header_to_sf as project_diagnosis_frequency_header_to_sf,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_diagnosis_header_parent_epilepsy as project_diagnosis_header_parent_epilepsy,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_dropped_sf_to_diagnosis as project_dropped_sf_to_diagnosis,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_empty_sf_candidate_to_diagnosis as project_empty_sf_candidate_to_diagnosis,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_focal_diagnosis_context_to_sf as project_focal_diagnosis_context_to_sf,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_infrequent_context_state as project_infrequent_context_state,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_returned_context_to_increased_state as project_returned_context_to_increased_state,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        project_sf_context_to_focal_diagnosis as project_sf_context_to_focal_diagnosis,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_cross_entity import (
        remote_last_seizures_evidence as remote_last_seizures_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        extend_asymmetric_prescription_evidence as extend_asymmetric_prescription_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        extend_probable_temporal_diagnosis_evidence as extend_probable_temporal_diagnosis_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        frequency_from_prescription_source as frequency_from_prescription_source,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        is_daily_total_dose as is_daily_total_dose,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        repair_absence_like_frequency_evidence as repair_absence_like_frequency_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        repair_case_only_evidence as repair_case_only_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        repair_ellipsis_evidence as repair_ellipsis_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        repair_no_further_since_evidence as repair_no_further_since_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        repair_prescription_attrs_from_text as repair_prescription_attrs_from_text,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        repair_prescription_frequency_synonym_evidence as repair_prescription_frequency_synonym_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        repair_since_last_clinic_count_evidence as repair_since_last_clinic_count_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_evidence_repair import (
        repair_whitespace_equivalent_evidence as repair_whitespace_equivalent_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_sf_state import (
        project_diagnosis_text_from_evidence as project_diagnosis_text_from_evidence,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.projection_sf_state import (
        project_sf_state_from_evidence as project_sf_state_from_evidence,
    )

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
