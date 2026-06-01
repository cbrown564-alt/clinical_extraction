from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.core.evidence import evidence_is_substring, locate_evidence
from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026 import temporal
from clinical_extraction.tasks.seizure_frequency.gan2026.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_extraction import (
    _extract_candidates,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_selection import (
    select_final_event as _select_final_event,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_text import (
    exact_evidence as _exact_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_text import (
    fallback_evidence as _fallback_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
)

_RawCandidate = RawCandidate
_clinic_date = temporal.clinic_date
_month_span_floor = temporal.month_span_floor
_relative_note_date = temporal.relative_note_date


class CandidateEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    kind: CandidateKind
    raw_value: str | None
    evidence: str
    start_char: int | None = None
    end_char: int | None = None
    rule_id: str = "unknown"
    rule_group: RuleGroup | None = None
    portability: Portability | None = None
    match_groups: dict[str, str | None] = Field(default_factory=dict)


class NormalizedEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    normalized_label: str
    semantic_kind: FrequencyLabelKind
    monthly_frequency: float
    validation_errors: tuple[str, ...] = ()


class Gan2026PipelineV1:
    """First deterministic, schema-shaped seizure-frequency baseline."""

    def __init__(self, ablation_config: AblationConfig | None = None) -> None:
        self.ablation_config = ablation_config or AblationConfig()

    def run(self, item: GanRecord) -> PipelineResult[FinalExtraction]:
        candidates = _extract_candidates(item.note_text, self.ablation_config)
        if not candidates:
            candidates = [
                _RawCandidate(
                    kind=CandidateKind.NO_REFERENCE,
                    label="no seizure frequency reference",
                    evidence=_fallback_evidence(item.note_text),
                )
            ]

        candidate_events = [
            _candidate_event(index=index, candidate=candidate, note_text=item.note_text)
            for index, candidate in enumerate(candidates, start=1)
        ]
        normalized_events = [
            _normalize_candidate(event, raw_candidate, self.ablation_config)
            for event, raw_candidate in zip(candidate_events, candidates, strict=True)
        ]
        final_selection = _select_final_event(
            candidate_events,
            normalized_events,
            self.ablation_config,
        )
        output = FinalExtraction(
            final_value=final_selection.final_label,
            rationale=final_selection.rationale,
            evidence=final_selection.evidence,
        )

        diagnostics = {
            "candidate_events": [event.model_dump(mode="json") for event in candidate_events],
            "normalized_events": [event.model_dump(mode="json") for event in normalized_events],
            "final_selection": final_selection.model_dump(mode="json"),
            "evidence_valid": evidence_is_substring(item.note_text, final_selection.evidence),
        }
        return PipelineResult(output=output, diagnostics=diagnostics)


def _candidate_event(index: int, candidate: _RawCandidate, note_text: str) -> CandidateEvent:
    evidence = _exact_evidence(note_text, candidate.evidence)
    span = locate_evidence(note_text, evidence)
    start_char, end_char = span if span else (None, None)
    return CandidateEvent(
        event_id=f"event_{index}",
        kind=candidate.kind,
        raw_value=candidate.label,
        evidence=evidence,
        start_char=start_char,
        end_char=end_char,
        rule_id=candidate.rule_id,
        rule_group=candidate.rule_group,
        portability=candidate.portability,
        match_groups=dict(candidate.match_groups),
    )


def _normalize_candidate(
    event: CandidateEvent,
    candidate: _RawCandidate,
    ablation_config: AblationConfig | None = None,
) -> NormalizedEvent:
    ablation_config = ablation_config or AblationConfig()
    label = repair_prediction_label(candidate.label, ablation_config)
    errors: tuple[str, ...] = ()
    try:
        record = label_to_frequency_record(label)
    except ValueError as exc:
        record = label_to_frequency_record("unknown")
        label = "unknown"
        errors = (str(exc),)
    return NormalizedEvent(
        event_id=event.event_id,
        normalized_label=label,
        semantic_kind=record.kind,
        monthly_frequency=record.monthly_frequency,
        validation_errors=errors,
    )
