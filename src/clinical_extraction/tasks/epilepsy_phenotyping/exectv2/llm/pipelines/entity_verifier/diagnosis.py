"""Diagnosis verifier pipeline config (reference; full migration deferred)."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_verifier as _legacy,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)

CONFIG = VerifierConfig(
    entity_name=DIAGNOSIS.name,
    prompt_version=_legacy.PROMPT_VERSION,
    pipeline_family=_legacy.PIPELINE_FAMILY,
    component_owner=_legacy.COMPONENT_OWNER,
    dspy_signature=_legacy.ExECTv2DiagnosisVerifierSignature,
    draft_field_name="draft_diagnosis_mentions",
    report_title="ExECTv2 Diagnosis Verifier",
    draft_mentions_label="Draft Diagnosis mentions",
    clinical_recovery_section_title="Diagnosis Clinical-Recovery Headline",
    clinical_recovery_key="diagnosis",
    task_text=(
        "Review the clinical letter and the draft Diagnosis mentions from the "
        "single structured key-entity extractor. Return the final Diagnosis "
        "mentions only. You may keep, delete, edit, or add mentions, but every "
        "final mention must be supported by exact source evidence."
    ),
    output_schema={},
    clinical_rules=_legacy._clinical_rules,
    worked_examples=_legacy._worked_examples,
    summarize_rows=_legacy.summarize_rows,
    include_source_near_in_report=True,
)

__all__ = ["CONFIG"]
