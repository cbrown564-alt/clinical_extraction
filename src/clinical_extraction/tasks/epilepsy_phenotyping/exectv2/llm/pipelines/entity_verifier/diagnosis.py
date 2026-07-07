"""Backward-compatible shim — diagnosis verifier moved to diagnosis_verification/."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.diagnosis_verification.verifier import (
    COMPONENT_OWNER,
    CONFIG,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    DspyDiagnosisVerifier,
)

__all__ = [
    "COMPONENT_OWNER",
    "CONFIG",
    "DspyDiagnosisVerifier",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
]
