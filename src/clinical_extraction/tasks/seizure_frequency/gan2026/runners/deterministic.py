"""Deterministic rules-only single-item runner."""

from __future__ import annotations

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.assessment_draft import (
    AssessmentDraft,
    AssessmentDraftBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    deterministic_candidate_set_from_raw,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_clinical_assessment_probe as assessment_probe,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    _candidate_event,
    _extract_candidates,
    _fallback_evidence,
    _normalize_candidate,
    _select_final_event,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def run_item(item: GanRecord, config: PipelineConfiguration) -> PipelineResult[FinalExtraction]:
    """Run one record through the deterministic rules-only architecture."""
    raw_candidates = _extract_candidates(item.note_text, config.ablation_config)
    if not raw_candidates:
        raw_candidates = [
            RawCandidate(
                kind=CandidateKind.NO_REFERENCE,
                label="no seizure frequency reference",
                evidence=_fallback_evidence(item.note_text),
            )
        ]

    candidate_set = deterministic_candidate_set_from_raw(
        raw_candidates,
        note_text=item.note_text,
        source_row_index=item.source_row_index or 1,
    )

    candidate_events = [
        _candidate_event(index=index, candidate=candidate, note_text=item.note_text)
        for index, candidate in enumerate(raw_candidates, start=1)
    ]
    normalized_events = [
        _normalize_candidate(event, raw_candidate, config.ablation_config)
        for event, raw_candidate in zip(candidate_events, raw_candidates, strict=True)
    ]
    final_selection = _select_final_event(
        candidate_events,
        normalized_events,
        config.ablation_config,
    )

    selected_index = int(final_selection.selected_event_ids[0].split("_")[1]) - 1
    selected_candidate = candidate_set.candidates[selected_index]

    output = FinalExtraction(
        final_value=final_selection.final_label,
        rationale=final_selection.rationale,
        evidence=final_selection.evidence,
    )

    disabled_switches = {
        group.value for group in RuleGroup if group not in config.ablation_config.enabled_groups
    } | set(config.ablation_config.disabled_rule_ids)

    draft = AssessmentDraft(
        assessment_kind=selected_candidate.candidate_kind,
        primary_candidate_ids=[selected_candidate.candidate_id],
        supporting_candidate_ids=[
            c.candidate_id
            for idx, c in enumerate(candidate_set.candidates)
            if idx != selected_index
        ],
        normalized_burden=AssessmentDraftBurden(source_normalized_phrase=final_selection.evidence),
        assessment_summary=final_selection.rationale,
    )
    try:
        clinical_assessment, _ = assessment_probe.assemble_clinical_assessment(
            draft,
            candidate_set=candidate_set,
            disabled_ablation_switches=disabled_switches,
        )
    except Exception:
        clinical_assessment = None

    diagnostics = {
        "candidate_events": [event.model_dump(mode="json") for event in candidate_events],
        "normalized_events": [event.model_dump(mode="json") for event in normalized_events],
        "final_selection": final_selection.model_dump(mode="json"),
        "evidence_valid": evidence_is_substring(item.note_text, final_selection.evidence),
        "clinical_assessment": (clinical_assessment.model_dump() if clinical_assessment else None),
    }
    return PipelineResult(output=output, diagnostics=diagnostics)
