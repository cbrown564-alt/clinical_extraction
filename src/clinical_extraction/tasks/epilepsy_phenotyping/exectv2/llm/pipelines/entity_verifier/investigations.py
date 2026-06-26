"""Investigations entity verifier pipeline config."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    INVESTIGATIONS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.investigations_content import (
    COMPONENT_OWNER,
    OUTPUT_SCHEMA,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    TASK_TEXT,
    ExECTv2InvestigationsVerifierSignature,
    _clinical_rules,
    _worked_examples,
    summarize_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
    make_dspy_module,
)

CONFIG = VerifierConfig(
    entity_name=INVESTIGATIONS.name,
    prompt_version=PROMPT_VERSION,
    pipeline_family=PIPELINE_FAMILY,
    component_owner=COMPONENT_OWNER,
    dspy_signature=ExECTv2InvestigationsVerifierSignature,
    draft_field_name="draft_investigations_mentions",
    report_title="ExECTv2 Investigations Verifier",
    draft_mentions_label="Draft Investigations mentions",
    clinical_recovery_section_title="Investigations Clinical-Recovery Headline",
    clinical_recovery_key="investigations",
    task_text=TASK_TEXT,
    output_schema=OUTPUT_SCHEMA,
    clinical_rules=_clinical_rules,
    worked_examples=_worked_examples,
    summarize_rows=summarize_rows,
    include_source_near_in_report=False,
)

DspyInvestigationsVerifier = make_dspy_module(CONFIG)

__all__ = [
    "COMPONENT_OWNER",
    "CONFIG",
    "DspyInvestigationsVerifier",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
]
