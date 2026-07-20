from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)

from .rule_metadata import (
    AblationConfig,
)
from .rules.temporal_selection import (
    temporal_selection_rule_is_enabled,
)


class CandidateEventLike(Protocol):
    event_id: str
    evidence: str


class NormalizedEventLike(Protocol):
    event_id: str
    normalized_label: str
    semantic_kind: FrequencyLabelKind
    monthly_frequency: float
    validation_errors: tuple[str, ...]


class SelectionScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    semantic_priority: int
    evidence_priority: int
    monthly_frequency_priority: float
    reason: str

    def priority(self) -> SelectionPriority:
        return SelectionPriority(
            semantic=self.semantic_priority,
            evidence=self.evidence_priority,
            monthly_frequency=self.monthly_frequency_priority,
        )


class SelectionPriority(BaseModel):
    model_config = ConfigDict(frozen=True)

    semantic: int
    evidence: int
    monthly_frequency: float

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SelectionPriority):
            return NotImplemented
        return (
            self.semantic,
            self.evidence,
            self.monthly_frequency,
        ) < (
            other.semantic,
            other.evidence,
            other.monthly_frequency,
        )


class SelectionCandidateScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    score: SelectionScore
    selected: bool = False


class SelectionDecisionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    final_label: str
    final_kind: FrequencyLabelKind
    monthly_frequency: float
    evidence: str
    rationale: str
    validation_errors: tuple[str, ...] = ()
    score: SelectionScore
    priority: SelectionPriority


class FinalSelection(BaseModel):
    model_config = ConfigDict(frozen=True)

    final_label: str
    final_kind: FrequencyLabelKind
    selected_event_ids: tuple[str, ...]
    rationale: str
    evidence: str
    monthly_frequency: float
    validation_errors: tuple[str, ...] = ()
    selected_score: SelectionScore
    selected_decision: SelectionDecisionRecord
    selection_candidates: tuple[SelectionCandidateScore, ...]


def select_final_event(
    candidate_events: Sequence[CandidateEventLike],
    normalized_events: Sequence[NormalizedEventLike],
    ablation_config: AblationConfig | None = None,
) -> FinalSelection:
    ablation_config = ablation_config or AblationConfig()
    pairs = list(zip(candidate_events, normalized_events, strict=True))
    scored_pairs = [
        (event, normalized, selection_score((event, normalized), ablation_config))
        for event, normalized in pairs
    ]
    selected_event, selected_normalized, selected_score = max(
        scored_pairs,
        key=lambda scored_pair: scored_pair[2].priority(),
    )
    selected_rationale = selection_rationale(selected_normalized)
    selected_decision = SelectionDecisionRecord(
        event_id=selected_event.event_id,
        final_label=selected_normalized.normalized_label,
        final_kind=selected_normalized.semantic_kind,
        monthly_frequency=selected_normalized.monthly_frequency,
        evidence=selected_event.evidence,
        rationale=selected_rationale,
        validation_errors=selected_normalized.validation_errors,
        score=selected_score,
        priority=selected_score.priority(),
    )
    return FinalSelection(
        final_label=selected_normalized.normalized_label,
        final_kind=selected_normalized.semantic_kind,
        selected_event_ids=(selected_event.event_id,),
        rationale=selected_rationale,
        evidence=selected_event.evidence,
        monthly_frequency=selected_normalized.monthly_frequency,
        validation_errors=selected_normalized.validation_errors,
        selected_score=selected_score,
        selected_decision=selected_decision,
        selection_candidates=tuple(
            SelectionCandidateScore(
                event_id=event.event_id,
                score=score,
                selected=event.event_id == selected_event.event_id,
            )
            for event, _normalized, score in scored_pairs
        ),
    )


def selection_score(
    pair: tuple[CandidateEventLike, NormalizedEventLike],
    ablation_config: AblationConfig | None = None,
) -> SelectionScore:
    ablation_config = ablation_config or AblationConfig()
    event, normalized = pair
    evidence = event.evidence.lower()
    if normalized.semantic_kind is FrequencyLabelKind.FREQUENCY:
        evidence_priority = frequency_summary_priority(evidence)
        return ablatable_selection_score(
            ablation_config,
            semantic_priority=4,
            evidence_priority=evidence_priority,
            monthly_frequency_priority=normalized.monthly_frequency,
            reason=(
                "frequency_current_summary" if evidence_priority > 0 else "frequency_monthly_rate"
            ),
        )
    if normalized.semantic_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        if is_specific_current_multiple_evidence(event.evidence):
            return ablatable_selection_score(
                ablation_config,
                semantic_priority=4,
                evidence_priority=1,
                monthly_frequency_priority=normalized.monthly_frequency,
                reason="specific_current_multiple",
            )
        return ablatable_selection_score(
            ablation_config,
            semantic_priority=3,
            evidence_priority=0,
            monthly_frequency_priority=0.0,
            reason="generic_unresolved_multiple",
        )
    if normalized.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        if is_current_seizure_free_evidence(evidence):
            return ablatable_selection_score(
                ablation_config,
                semantic_priority=5,
                evidence_priority=0,
                monthly_frequency_priority=0.0,
                reason="current_seizure_free",
            )
        return ablatable_selection_score(
            ablation_config,
            semantic_priority=2,
            evidence_priority=0,
            monthly_frequency_priority=0.0,
            reason="generic_seizure_free",
        )
    if normalized.semantic_kind is FrequencyLabelKind.UNKNOWN:
        if is_trigger_conditioned_unknown_evidence(evidence):
            return ablatable_selection_score(
                ablation_config,
                semantic_priority=6,
                evidence_priority=0,
                monthly_frequency_priority=0.0,
                reason="trigger_conditioned_unknown",
            )
        return ablatable_selection_score(
            ablation_config,
            semantic_priority=1,
            evidence_priority=0,
            monthly_frequency_priority=0.0,
            reason="generic_unknown",
        )
    return ablatable_selection_score(
        ablation_config,
        semantic_priority=0,
        evidence_priority=0,
        monthly_frequency_priority=0.0,
        reason="no_reference",
    )


def ablatable_selection_score(
    ablation_config: AblationConfig,
    *,
    semantic_priority: int,
    evidence_priority: int,
    monthly_frequency_priority: float,
    reason: str,
) -> SelectionScore:
    if not temporal_selection_rule_is_enabled(reason, ablation_config):
        return SelectionScore(
            semantic_priority=0,
            evidence_priority=0,
            monthly_frequency_priority=0.0,
            reason=f"{reason}_disabled",
        )
    return SelectionScore(
        semantic_priority=semantic_priority,
        evidence_priority=evidence_priority,
        monthly_frequency_priority=monthly_frequency_priority,
        reason=reason,
    )


def selection_rationale(normalized: NormalizedEventLike) -> str:
    if normalized.semantic_kind is FrequencyLabelKind.FREQUENCY:
        return "Selected the highest normalized current frequency candidate."
    if normalized.semantic_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        return "Selected an unresolved multiple-frequency candidate."
    if normalized.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        return "Selected the explicit seizure-free statement."
    if normalized.semantic_kind is FrequencyLabelKind.UNKNOWN:
        return "Selected seizure-frequency evidence that could not be converted to a rate."
    return "No seizure-frequency evidence was found."


def is_specific_current_multiple_evidence(evidence: str) -> bool:
    normalized = evidence.lower()
    return (
        "most weekdays" in normalized
        or "most nights of the week" in normalized
        or "several episodes per week" in normalized
        or "multiple times in past week" in normalized
        or "near-daily basis, sometimes dozens in a day" in normalized
        or re.search(r"\boccur\s+several\s+times\s+(?:each|per)\s+week\b", normalized) is not None
        or re.search(r"\bon\s+most\s+days\b", normalized) is not None
        or ("several" in normalized and re.search(r"\blast\s+week\b", normalized) is not None)
    )


def frequency_summary_priority(evidence: str) -> int:
    if (
        "seizure days:" in evidence
        or evidence.startswith("abs ")
        or "in a typical month" in evidence
        or "median inter-seizure interval" in evidence
        or re.search(r"\bq(?:one|two|three|four|five|six|seven|eight|nine|\d)", evidence)
        is not None
    ):
        return 2
    return 0


def is_trigger_conditioned_unknown_evidence(evidence: str) -> bool:
    return (
        "only when significantly short on sleep" in evidence
        or "perimenstrual only" in evidence
        or evidence.startswith("better over the past")
    )


def is_current_seizure_free_evidence(evidence: str) -> bool:
    return (
        re.search(r"\bseizure-free since \d{1,2}(?:[-/ ]|$)", evidence) is not None
        or re.search(r"\bseizure-free interval since \d{1,2}(?:[-/ ]|$)", evidence) is not None
        or evidence.startswith("last seizure on")
        or re.search(
            r"\bno events for\s+(?:\d+|one|two|three|four|five|six|seven|"
            r"eight|nine|ten|eleven|twelve)\s+months?\b",
            evidence,
        )
        is not None
        or "absence of events for over" in evidence
        or "no occurrence of events suggestive of seizures" in evidence
        or "no definite seizure events" in evidence
        or "no seizures since last visit" in evidence
        or "no events, warnings, or auras for over" in evidence
        or "no spell-like events suggestive of seizures over the past" in evidence
        or "seizure-free interval extends to" in evidence
        or "drug-free remission since" in evidence
        or "no focal clonic since" in evidence
        or "sustained remission since" in evidence
        or "prior cluster pattern resolved since" in evidence
        or "recorded seizure rate at zero over the last" in evidence
        or "seizure free for one and a half years" in evidence
        or "not experiencing any seizures in one and a half years" in evidence
        or "currently in long-term remission, having been seizure free for years" in evidence
        or "has not experienced any seizures" in evidence
        or evidence
        in {"no events suggestive of seizures", "no recent events suggestive of seizures"}
        or evidence == "sustained postoperative seizure freedom"
        or evidence == "no recorded events since"
        or evidence == "interval history negative for seizures"
        or evidence == "durable seizure control"
        or evidence == "seizure cessation following initiation of last asm"
        or evidence == "steady run without clear seizures at present"
    )
