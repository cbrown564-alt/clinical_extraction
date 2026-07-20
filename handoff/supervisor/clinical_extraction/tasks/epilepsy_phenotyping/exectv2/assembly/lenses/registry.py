"""Lens manifest registry for ExECTv2 assembly."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    LensManifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)

from .base import (
    DiagnosisLens,
    EntityLens,
    InvestigationsLens,
    PrescriptionLens,
    SeizureFrequencyLens,
    ThinArtifactLens,
)
from .diagnosis import DiagnosisDictionaryLens, DiagnosisHeadingRecoveryLens
from .investigations import InvestigationsDictionaryLens
from .prescription import PrescriptionDictionaryLens
from .seizure_frequency import SeizureFrequencyDictionaryLens


def lens_from_manifest(config: LensManifest) -> EntityLens:
    dictionary_lens_by_manifest: dict[tuple[str, str], type[ThinArtifactLens]] = {
        (DIAGNOSIS.name, "diagnosis_convention_dictionary_v09"): DiagnosisDictionaryLens,
        (SEIZURE_FREQUENCY.name, "sf_convention_dictionary_v09"): SeizureFrequencyDictionaryLens,
        (PRESCRIPTION.name, "prescription_dictionary_v09"): PrescriptionDictionaryLens,
        (
            INVESTIGATIONS.name,
            "investigations_convention_dictionary_v09",
        ): InvestigationsDictionaryLens,
    }
    legacy_diagnosis_dictionary_lens_ids = frozenset(
        {
            "diagnosis_heading_recovery_residual_benchmark_v05",
            "diagnosis_heading_recovery_convention_alias_v04",
            "diagnosis_heading_recovery_convention_cleanup_v03",
        }
    )
    key = (config.entity, config.lens)
    if key in dictionary_lens_by_manifest:
        return dictionary_lens_by_manifest[key](lens_id=config.lens, entity=config.entity)
    if config.entity == DIAGNOSIS.name and config.lens in legacy_diagnosis_dictionary_lens_ids:
        return DiagnosisDictionaryLens(lens_id=config.lens, entity=config.entity)
    if config.entity == DIAGNOSIS.name and config.lens == "diagnosis_heading_recovery_v02":
        return DiagnosisHeadingRecoveryLens(lens_id=config.lens, entity=config.entity)
    lens_type = {
        DIAGNOSIS.name: DiagnosisLens,
        SEIZURE_FREQUENCY.name: SeizureFrequencyLens,
        PRESCRIPTION.name: PrescriptionLens,
        INVESTIGATIONS.name: InvestigationsLens,
    }.get(config.entity, ThinArtifactLens)
    return lens_type(lens_id=config.lens, entity=config.entity)
