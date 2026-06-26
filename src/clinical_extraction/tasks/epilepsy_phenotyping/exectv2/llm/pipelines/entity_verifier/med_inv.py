"""Prescription/Investigations verifier pipeline config (reference; migration deferred)."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    INVESTIGATIONS,
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_med_inv_verifier as _legacy,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)

CONFIG = VerifierConfig(
    entity_name=INVESTIGATIONS.name,
    prompt_version=_legacy.PROMPT_VERSION,
    pipeline_family=_legacy.PIPELINE_FAMILY,
    component_owner=_legacy.COMPONENT_OWNER,
    dspy_signature=_legacy.ExECTv2MedInvVerifierSignature,
    draft_field_name="draft_mentions",
    report_title="ExECTv2 Prescription/Investigations Verifier",
    draft_mentions_label="Draft Prescription/Investigations mentions",
    clinical_recovery_section_title="Clinical-Recovery Headline",
    clinical_recovery_key="investigations",
    task_text=(
        "Review the clinical letter and draft Prescription/Investigations "
        "mentions from the single structured key-entity extractor. Return final "
        "Prescription and Investigations mentions only. You may keep, delete, "
        "edit, or add mentions, but every final mention must be supported by "
        "exact source evidence."
    ),
    output_schema={},
    clinical_rules=_legacy._clinical_rules,
    worked_examples=_legacy._worked_examples,
    summarize_rows=_legacy.summarize_rows,
    include_source_near_in_report=False,
    draft_entity_names=(PRESCRIPTION.name, INVESTIGATIONS.name),
    include_entity_in_draft=True,
)

__all__ = ["CONFIG"]
