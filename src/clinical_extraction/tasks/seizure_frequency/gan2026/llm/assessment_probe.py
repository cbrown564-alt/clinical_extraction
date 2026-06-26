"""Thin public facade for the Gan 2026 clinical-assessment probe."""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.assessment_draft import (
    AssessmentDraft,
    AssessmentDraftBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.clinical_assessment_assembly import (
    DISABLED_SWITCH_ISSUE_PREFIX,
    NORMALIZATION_POLICY_ID,
    assemble_clinical_assessment as _assemble_clinical_assessment,
    normalize_assessment_burden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.assessment_probe_signature import (
    DEFAULT_CANDIDATE_SET_JSONL_PATH,
    DEFAULT_JSONL_PATH,
    DEFAULT_REPORT_PATH,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    DspyCandidateSetClinicalAssessment,
    Gan2026CandidateSetClinicalAssessmentSignature,
    build_assessment_inputs,
    prediction_to_assessment_draft,
    run_split,
    summarize_records,
    write_jsonl,
    write_report,
)

# Re-export private assembly helpers exercised by tests and internal callers.
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    clinical_assessment_assembly as _assembly,
)

COMPONENT_OWNER = "llm_candidate_set_clinical_assessment"

_frequency_burden_from_multi_month_bucket_phrase = (
    _assembly._frequency_burden_from_multi_month_bucket_phrase
)
_normalize_phrase_for_parse = _assembly._normalize_phrase_for_parse
_repair_multi_primary_nonadditive_policy = _assembly._repair_multi_primary_nonadditive_policy


def assemble_clinical_assessment(
    draft: AssessmentDraft | None,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> tuple[ClinicalAssessment | None, list[str]]:
    return _assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
        component_owner=COMPONENT_OWNER,
        disabled_ablation_switches=disabled_ablation_switches,
    )


__all__ = [
    "AssessmentDraft",
    "AssessmentDraftBurden",
    "ClinicalAssessment",
    "COMPONENT_OWNER",
    "DEFAULT_CANDIDATE_SET_JSONL_PATH",
    "DEFAULT_JSONL_PATH",
    "DEFAULT_REPORT_PATH",
    "DISABLED_SWITCH_ISSUE_PREFIX",
    "DspyCandidateSetClinicalAssessment",
    "Gan2026CandidateSetClinicalAssessmentSignature",
    "NORMALIZATION_POLICY_ID",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
    "assemble_clinical_assessment",
    "build_assessment_inputs",
    "normalize_assessment_burden",
    "prediction_to_assessment_draft",
    "run_split",
    "summarize_records",
    "write_jsonl",
    "write_report",
]
