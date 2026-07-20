from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.core.evidence import locate_evidence
from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import temporal
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
)

from .deterministic.deterministic_extraction import (
    _extract_candidates as _extract_candidates,
)
from .deterministic.deterministic_selection import (
    select_final_event as _select_final_event,
)
from .deterministic.deterministic_text import (
    exact_evidence as _exact_evidence,
)
from .deterministic.deterministic_text import (
    fallback_evidence as _fallback_evidence,
)

_RawCandidate = RawCandidate
_clinic_date = temporal.clinic_date
_month_span_floor = temporal.month_span_floor
_relative_note_date = temporal.relative_note_date

__all__ = [
    "CandidateKind",
    "Gan2026PipelineV1",
    "_RawCandidate",
    "_candidate_event",
    "_clinic_date",
    "_extract_candidates",
    "_fallback_evidence",
    "_month_span_floor",
    "_normalize_candidate",
    "_relative_note_date",
    "_select_final_event",
]


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
        from .runner import Gan2026PipelineRunner, PipelineConfiguration

        config = PipelineConfiguration(
            architecture="deterministic_canonical_pipeline",
            ablation_config=self.ablation_config,
        )
        self._runner = Gan2026PipelineRunner(config)

    def run(self, item: GanRecord) -> PipelineResult[FinalExtraction]:
        return self._runner.run(item)


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
