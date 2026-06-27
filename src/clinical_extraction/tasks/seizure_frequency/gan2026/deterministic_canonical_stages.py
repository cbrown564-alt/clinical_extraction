"""Named, stage-owned wrappers for the `deterministic_canonical_pipeline` config.

This module is the staging seam for `Gan2026PipelineRunner`'s
`deterministic_canonical_pipeline` architecture
([[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]],
[[0013-stage-deterministic-canonical-config-before-generalizing-its-rules]]).
Each function below is a thin, named wrapper over the existing `deterministic`
internals — Extract, Normalize, Select & Render, and Evidence Trace Check — so
that a later family-by-family de-overfitting rewrite (the plan's Section 4)
has named, separable seams to rewrite within. This pass changes no rules and
no behavior: every wrapper returns the same typed objects the `deterministic`
architecture already returns
([[0014-evidence-trace-check-not-verify-for-deterministic-canonical-pipeline]]
explains why the fourth stage is named "Evidence Trace Check" rather than
"Verify").
"""

from __future__ import annotations

from collections.abc import Sequence

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    deterministic_candidate_set_from_raw,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_selection import (
    FinalSelection,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.assessment_draft import (
    AssessmentDraft,
    AssessmentDraftBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_clinical_assessment_probe as assessment_probe,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    CandidateEvent,
    NormalizedEvent,
    _candidate_event,
    _extract_candidates,
    _fallback_evidence,
    _normalize_candidate,
    _select_final_event,
)


def extract_stage(
    note_text: str,
    *,
    source_row_index: int,
    ablation_config: AblationConfig | None = None,
    use_state_graph: bool = False,
) -> tuple[tuple[RawCandidate, ...], CandidateSet, tuple[CandidateEvent, ...]]:
    """Extract: raw note text -> evidence-anchored `CandidateSet`/`CandidateEvent`s.

    When ``use_state_graph`` is True, delegates to the clinical frequency state
    graph harvester and materializes candidates with
    ``source_type="state_graph_node"``. Default False preserves the existing
    pipeline_v1 rule-family extraction path unchanged.

    Otherwise wraps `_extract_candidates` (rule-family extraction, with the
    existing `NO_REFERENCE` fallback when nothing is found),
    `deterministic_candidate_set_from_raw` (raw candidates -> `CandidateSet`),
    and `_candidate_event` (locate each candidate's evidence span and assign an
    `event_id`) — unchanged.
    """
    if use_state_graph:
        from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph.extract import (
            extract_stage as state_graph_extract_stage,
        )

        return state_graph_extract_stage(
            note_text,
            source_row_index=source_row_index,
        )

    ablation_config = ablation_config or AblationConfig()
    raw_candidates = _extract_candidates(note_text, ablation_config)
    if not raw_candidates:
        raw_candidates = [
            RawCandidate(
                kind=CandidateKind.NO_REFERENCE,
                label="no seizure frequency reference",
                evidence=_fallback_evidence(note_text),
            )
        ]

    candidate_set = deterministic_candidate_set_from_raw(
        raw_candidates,
        note_text=note_text,
        source_row_index=source_row_index,
    )
    candidate_events = tuple(
        _candidate_event(index=index, candidate=candidate, note_text=note_text)
        for index, candidate in enumerate(raw_candidates, start=1)
    )
    return tuple(raw_candidates), candidate_set, candidate_events


def normalize_stage(
    candidate_events: Sequence[CandidateEvent],
    raw_candidates: Sequence[RawCandidate],
    *,
    ablation_config: AblationConfig | None = None,
) -> tuple[NormalizedEvent, ...]:
    """Normalize: label repair plus frequency-record parsing -> `NormalizedEvent`s.

    Wraps `_normalize_candidate` (label repair via `repair_prediction_label`,
    then `label_to_frequency_record` parsing with the existing `unknown`
    fallback on `ValueError`) — unchanged. This is the most likely Section 4
    rewrite target, which is why it is kept as its own seam rather than folded
    into Extract alongside the event-shaping it is paired with today.
    """
    ablation_config = ablation_config or AblationConfig()
    return tuple(
        _normalize_candidate(event, raw_candidate, ablation_config)
        for event, raw_candidate in zip(candidate_events, raw_candidates, strict=True)
    )


def select_and_render_stage(
    candidate_events: Sequence[CandidateEvent],
    normalized_events: Sequence[NormalizedEvent],
    *,
    ablation_config: AblationConfig | None = None,
) -> FinalSelection:
    """Select & Render: score and pick among normalized candidates, render the final label.

    Wraps `_select_final_event` (`deterministic/deterministic_selection.py`)
    unchanged. Named as one combined stage — not separate Project/Render
    stages — because the underlying selection logic has no internal seam
    between "decide the projected fact" and "render it"; see
    [[0014-evidence-trace-check-not-verify-for-deterministic-canonical-pipeline]]
    and `CONTEXT.md`'s "Select & Render" entry for why splitting it would be a
    behavior-risking refactor rather than a staging pass.
    """
    return _select_final_event(candidate_events, normalized_events, ablation_config)


def evidence_trace_check_stage(
    note_text: str,
    *,
    final_selection: FinalSelection,
    candidate_set: CandidateSet,
    selected_index: int,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> tuple[bool, ClinicalAssessment | None]:
    """Evidence Trace Check: verbatim evidence-substring check plus a diagnostic-only `ClinicalAssessment` probe.

    Wraps the existing `evidence_is_substring` check and the existing
    `AssessmentDraft`/`assemble_clinical_assessment` diagnostic probe —
    unchanged, including the probe's `try/except` (it is visibility-only and
    must never fail the pipeline run). Deliberately not named "Verify": see
    [[0014-evidence-trace-check-not-verify-for-deterministic-canonical-pipeline]]
    for why this stage does not adopt `VerificationDecision`/`Verifier Action`
    affirm/reject/route semantics that the deterministic pipeline does not (and
    should not, as part of this staging pass) implement.
    """
    selected_candidate = candidate_set.candidates[selected_index]
    draft = AssessmentDraft(
        assessment_kind=selected_candidate.candidate_kind,
        primary_candidate_ids=[selected_candidate.candidate_id],
        supporting_candidate_ids=[
            candidate.candidate_id
            for idx, candidate in enumerate(candidate_set.candidates)
            if idx != selected_index
        ],
        normalized_burden=AssessmentDraftBurden(
            source_normalized_phrase=final_selection.evidence
        ),
        assessment_summary=final_selection.rationale,
    )
    try:
        clinical_assessment, _ = assessment_probe.assemble_clinical_assessment(
            draft,
            candidate_set=candidate_set,
            disabled_ablation_switches=disabled_ablation_switches,
        )
    except Exception:
        clinical_assessment = None

    evidence_valid = evidence_is_substring(note_text, final_selection.evidence)
    return evidence_valid, clinical_assessment
