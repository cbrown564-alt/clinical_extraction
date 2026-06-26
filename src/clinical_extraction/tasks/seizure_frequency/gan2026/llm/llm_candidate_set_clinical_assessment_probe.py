"""Backward-compatible facade for the Gan 2026 clinical-assessment probe."""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    clinical_assessment_assembly as _assembly,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import assessment_probe as _probe

AssessmentDraft = _probe.AssessmentDraft
AssessmentDraftBurden = _probe.AssessmentDraftBurden
ClinicalAssessment = _probe.ClinicalAssessment
DEFAULT_CANDIDATE_SET_JSONL_PATH = _probe.DEFAULT_CANDIDATE_SET_JSONL_PATH
DEFAULT_JSONL_PATH = _probe.DEFAULT_JSONL_PATH
DEFAULT_REPORT_PATH = _probe.DEFAULT_REPORT_PATH
DISABLED_SWITCH_ISSUE_PREFIX = _probe.DISABLED_SWITCH_ISSUE_PREFIX
DspyCandidateSetClinicalAssessment = _probe.DspyCandidateSetClinicalAssessment
Gan2026CandidateSetClinicalAssessmentSignature = (
    _probe.Gan2026CandidateSetClinicalAssessmentSignature
)
NORMALIZATION_POLICY_ID = _probe.NORMALIZATION_POLICY_ID
PIPELINE_FAMILY = _probe.PIPELINE_FAMILY
PROMPT_VERSION = _probe.PROMPT_VERSION
assemble_clinical_assessment = _probe.assemble_clinical_assessment
build_assessment_inputs = _probe.build_assessment_inputs
normalize_assessment_burden = _probe.normalize_assessment_burden
prediction_to_assessment_draft = _probe.prediction_to_assessment_draft
run_split = _probe.run_split
summarize_records = _probe.summarize_records
write_jsonl = _probe.write_jsonl
write_report = _probe.write_report

# Private helpers preserved for existing tests and internal callers.
_frequency_burden_from_multi_month_bucket_phrase = (
    _assembly._frequency_burden_from_multi_month_bucket_phrase
)
_normalize_phrase_for_parse = _assembly._normalize_phrase_for_parse
_repair_multi_primary_nonadditive_policy = _assembly._repair_multi_primary_nonadditive_policy
