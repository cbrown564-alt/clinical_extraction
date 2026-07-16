"""Standard-dictionary convention modules for ExECTv2 deterministic repair."""

from __future__ import annotations

from ..sf_surface_registry.adapters.convention import (
    is_sf_convention_noise,
    sf_convention_rewrite,
    sf_residual_additions,
)
from .diagnosis import (
    DIAGNOSIS_CONVENTION_ALIAS_REPAIRS,
    DIAGNOSIS_RESIDUAL_CONVENTION_NOISE,
    DIAGNOSIS_SINGLE_SEIZURE_SURFACES,
    DIAGNOSIS_STANDALONE_NOISE,
    DIAGNOSIS_SURFACE_CONVENTION_REPAIRS,
    RESIDUAL_SOURCE_CONCEPT_PATTERNS,
    diagnosis_convention_attribute_repairs,
    diagnosis_convention_target,
    diagnosis_residual_addition_category,
    diagnosis_residual_additions,
    is_diagnosis_convention_noise,
    is_redundant_diagnosis_residual_addition,
    should_add_generic_epilepsy_companion,
)
from .investigations import (
    investigation_convention_attribute_repairs,
    investigation_residual_additions,
    is_investigation_convention_noise,
)
from .prescription import (
    is_bounded_explicit_current_prescription,
    is_explicit_current_prescription,
    is_prescription_convention_noise,
    prescription_convention_attribute_repairs,
    prescription_residual_additions,
    prescription_residual_rule_group,
    split_daily_dose_regimen,
)
from .shared import (
    DRUG_SURFACE_ALIASES,
    dose_from_text,
    frequency_code,
    normalize_dose_unit,
    normalize_dose_value,
    normalize_drug_name,
)

__all__ = [
    "DIAGNOSIS_CONVENTION_ALIAS_REPAIRS",
    "DIAGNOSIS_RESIDUAL_CONVENTION_NOISE",
    "DIAGNOSIS_SINGLE_SEIZURE_SURFACES",
    "DIAGNOSIS_STANDALONE_NOISE",
    "DIAGNOSIS_SURFACE_CONVENTION_REPAIRS",
    "DRUG_SURFACE_ALIASES",
    "RESIDUAL_SOURCE_CONCEPT_PATTERNS",
    "diagnosis_convention_attribute_repairs",
    "diagnosis_convention_target",
    "diagnosis_residual_addition_category",
    "diagnosis_residual_additions",
    "dose_from_text",
    "frequency_code",
    "investigation_convention_attribute_repairs",
    "investigation_residual_additions",
    "is_diagnosis_convention_noise",
    "is_investigation_convention_noise",
    "is_bounded_explicit_current_prescription",
    "is_explicit_current_prescription",
    "is_prescription_convention_noise",
    "is_redundant_diagnosis_residual_addition",
    "is_sf_convention_noise",
    "normalize_dose_unit",
    "normalize_dose_value",
    "normalize_drug_name",
    "prescription_convention_attribute_repairs",
    "prescription_residual_additions",
    "prescription_residual_rule_group",
    "sf_convention_rewrite",
    "sf_residual_additions",
    "should_add_generic_epilepsy_companion",
    "split_daily_dose_regimen",
]
