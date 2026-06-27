"""Backward-compatible shim — diagnosis content moved to diagnosis_verification/."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.diagnosis_verification.verifier_content import (
    COMPONENT_OWNER,
    OUTPUT_SCHEMA,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    TASK_TEXT,
    ExECTv2DiagnosisVerifierSignature,
    _attribute_vocabulary,
    _clinical_rules,
    _worked_examples,
    summarize_rows,
)

__all__ = [
    "COMPONENT_OWNER",
    "ExECTv2DiagnosisVerifierSignature",
    "OUTPUT_SCHEMA",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
    "TASK_TEXT",
    "_attribute_vocabulary",
    "_clinical_rules",
    "_worked_examples",
    "summarize_rows",
]
