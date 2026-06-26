"""SeizureFrequency entity verifier pipeline config."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
    make_dspy_module,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.sf_content import (
    COMPONENT_OWNER,
    OUTPUT_SCHEMA,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    TASK_TEXT,
    ExECTv2SFVerifierSignature,
    _clinical_rules,
    _worked_examples,
    summarize_rows,
)

CONFIG = VerifierConfig(
    entity_name=SEIZURE_FREQUENCY.name,
    prompt_version=PROMPT_VERSION,
    pipeline_family=PIPELINE_FAMILY,
    component_owner=COMPONENT_OWNER,
    dspy_signature=ExECTv2SFVerifierSignature,
    draft_field_name="draft_seizure_frequency_mentions",
    report_title="ExECTv2 SeizureFrequency Verifier",
    draft_mentions_label="Draft SF mentions",
    clinical_recovery_section_title="SeizureFrequency Clinical-Recovery Headline",
    clinical_recovery_key="seizure_frequency",
    task_text=TASK_TEXT,
    output_schema=OUTPUT_SCHEMA,
    clinical_rules=_clinical_rules,
    worked_examples=_worked_examples,
    summarize_rows=summarize_rows,
    include_source_near_in_report=True,
)

DspySFVerifier = make_dspy_module(CONFIG)

__all__ = [
    "COMPONENT_OWNER",
    "CONFIG",
    "DspySFVerifier",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
]
