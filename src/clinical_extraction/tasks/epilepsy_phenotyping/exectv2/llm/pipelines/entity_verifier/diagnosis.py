"""Diagnosis entity verifier pipeline config."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.diagnosis_content import (
    COMPONENT_OWNER,
    OUTPUT_SCHEMA,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    TASK_TEXT,
    ExECTv2DiagnosisVerifierSignature,
    _clinical_rules,
    _worked_examples,
    summarize_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
    make_dspy_module,
)

CONFIG = VerifierConfig(
    entity_name=DIAGNOSIS.name,
    prompt_version=PROMPT_VERSION,
    pipeline_family=PIPELINE_FAMILY,
    component_owner=COMPONENT_OWNER,
    dspy_signature=ExECTv2DiagnosisVerifierSignature,
    draft_field_name="draft_diagnosis_mentions",
    report_title="ExECTv2 Diagnosis Verifier",
    draft_mentions_label="Draft Diagnosis mentions",
    clinical_recovery_section_title="Diagnosis Clinical-Recovery Headline",
    clinical_recovery_key="diagnosis",
    task_text=TASK_TEXT,
    output_schema=OUTPUT_SCHEMA,
    clinical_rules=_clinical_rules,
    worked_examples=_worked_examples,
    summarize_rows=summarize_rows,
    include_source_near_in_report=True,
)

DspyDiagnosisVerifier = make_dspy_module(CONFIG)

__all__ = [
    "COMPONENT_OWNER",
    "CONFIG",
    "DspyDiagnosisVerifier",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
]
