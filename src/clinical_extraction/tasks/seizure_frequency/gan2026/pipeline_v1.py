from __future__ import annotations

import re
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.core.evidence import evidence_is_substring, locate_evidence
from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    FrequencyLabelKind,
    label_to_frequency_record,
    repair_prediction_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rules.cluster import (
    ADJECTIVE_CLUSTER_RATE_RULE,
    BATCH_WITHIN_24H_RULE,
    BROAD_CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE,
    CLUSTER_COUNT_THIS_PERIOD_RULE,
    CLUSTER_COUNT_THIS_PERIOD_VAGUE_SIZE_RULE,
    CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE,
    CLUSTER_COUNT_WITH_IMPLIED_SIZE_RULE,
    CLUSTER_DAYS_SIMPLE_RULE,
    CLUSTER_OVER_PERIOD_RULE,
    CLUSTER_PERIOD_WITH_PER_CLUSTER_RULE,
    CLUSTER_RATE_WITH_SIZE_RULE,
    CLUSTER_SEIZURE_DAYS_PER_PERIOD_RULE,
    CLUSTER_SIZE_WITHOUT_COUNT_RULE,
    CLUSTER_TIMING_RULE,
    CLUSTERS_EACH_COMPRISING_RULE,
    DESCRIPTOR_CLUSTER_SIZE_RULE,
    LAST_CONVULSIVE_CLUSTER_PERSISTENCE_RULE,
    LAST_MONTH_CLUSTER_COUNT_RULE,
    MONTHLY_CLUSTER_RATE_WITH_SIZE_RULE,
    NEARLY_INTERVAL_CLUSTER_RULE,
    RUN_WITH_SEPARATE_DAYS_RULE,
    SEIZURE_FREE_CYCLE_CLUSTER_RULE,
    SEIZURE_FREE_INTERVAL_DAY_CLUSTER_RULE,
    SHORT_BURST_CLUSTER_RULE,
    SHORTHAND_CLUSTER_RATE_RULE,
    UNKNOWN_CLUSTER_SIZE_RULE,
    VAGUE_CLUSTER_DAYS_RULE,
    apply_cluster_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rules.diary import (
    DIARY_DATE_LIST_RULE,
    INCREASING_MONTHLY_COUNT_RULE,
    MONTHLY_COUNT_LOG_RULE,
    MONTHLY_DIARY_SUMMARY_RULES,
    RECORDED_MONTH_LOG_RULE,
    SEIZURE_DAY_LOG_RULE,
    SEIZURE_DAYS_FRACTION_RULE,
    SEIZURE_DAYS_PER_PERIOD_RULE,
    SLEEP_AWAKE_MONTH_SUMMARY_RULES,
    SPARSE_FULL_MONTH_LOG_RULE,
    apply_diary_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rules.gan_shorthand import (
    ABS_ADJECTIVE_RATE_RULE,
    ABS_COUNT_RATE_RULE,
    Q_INTERVAL_RULE,
    TC_SZ_COUNT_RATE_RULE,
    apply_gan_shorthand_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rules.rate import (
    COUNT_DURING_RECENT_WINDOW_RULE,
    COUNTED_ADVERBIAL_RATE_RULE,
    DAILY_BASIS_CURRENT_RULE,
    DAYS_OF_WEEK_RATE_RULE,
    DESCRIPTOR_RATE_RULE,
    DIRECT_RATE_RULE,
    IMPLICIT_EVERY_OTHER_INTERVAL_RULE,
    IMPLICIT_INTERVAL_RULE,
    IMPLICIT_NIGHTLY_INTERVAL_RULE,
    NIGHTS_PER_PERIOD_RULE,
    NO_MORE_THAN_ADVERBIAL_RATE_RULE,
    OCCURRING_ADJECTIVE_RATE_RULE,
    OCCURRING_EVERY_OTHER_INTERVAL_RULE,
    OCCURRING_INTERVAL_RULE,
    OCCURRING_ONCE_PER_NIGHT_RULE,
    PERIOD_FIRST_EXPERIENCED_COUNT_RULE,
    PERIOD_FIRST_FEATURING_COUNT_RULE,
    PERIOD_FIRST_OCCURRED_COUNT_RULE,
    PERIOD_FIRST_RECENT_COUNT_RULE,
    PERIOD_FIRST_TIMEFRAME_COUNT_RULE,
    PERSISTENT_ADVERBIAL_RATE_RULE,
    QUALIFIED_DIRECT_RATE_RULE,
    QUARTER_DIRECT_RATE_RULE,
    RECENT_COUNT_RULE,
    RECORDED_YEAR_COUNT_RULE,
    SEIZURE_ADJECTIVE_RATE_RULE,
    SIMPLE_PARTIAL_ADVERBIAL_RATE_RULE,
    STANDALONE_ADJECTIVE_RATE_RULE,
    THERE_HAVE_BEEN_COUNT_RULE,
    YESTERDAY_OR_TODAY_COUNT_RULE,
    apply_rate_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rules.seizure_free import (
    ABSENCE_FOR_DURATION_RULE,
    CURRENT_CONTROL_PHRASE_RULE,
    GENERIC_SEIZURE_FREE_RULE,
    LAST_EPILEPTIC_EVENT_RULE,
    NO_DEFINITE_EVENTS_RULE,
    NO_EVENTS_FOR_DURATION_RULE,
    SEIZURE_FREE_DURATION_STATUS_RULE,
    SEIZURE_FREE_ONE_AND_HALF_YEARS_RULE,
    SEIZURE_FREE_SINCE_DATE_RULE,
    apply_seizure_free_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rules.temporal_selection import (
    temporal_selection_rule_is_enabled,
)

_RawCandidate = RawCandidate


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


@dataclass(frozen=True)
class _ParsedMonthDate:
    year: int
    month: int
    day: int | None = None


def _build_qualitative_improvement_unknown(
    match: re.Match[str], _context: ExtractionContext
) -> _RawCandidate:
    return _RawCandidate(
        kind=CandidateKind.UNKNOWN_FREQUENCY,
        label="unknown",
        evidence=_clean_evidence(match.group(0)),
        rule_id="unknown.qualitative_improvement",
        rule_group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


QUALITATIVE_IMPROVEMENT_UNKNOWN_RULE = RuleSpec(
    rule_id="unknown.qualitative_improvement",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Treat qualitative current improvement spans as unknown frequency.",
    pattern=re.compile(
        r"\bBetter\s+over\s+the\s+past\s+(?P<duration>\d+|[a-z]+)\s+months?\b",
        re.IGNORECASE,
    ),
    build=_build_qualitative_improvement_unknown,
    examples=(
        RuleExample(
            text="She describes seizure control as Better over the past seven months.",
            expected_label="unknown",
            expected_evidence="Better over the past seven months",
        ),
    ),
    provenance="Validation-derived V1 qualitative improvement unknown-frequency guard.",
)


NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "single": "1",
    "once": "1",
    "twice": "2",
    "thrice": "3",
    "several": "multiple",
    "few": "multiple",
}

NUMBER_WORD_PATTERN = "|".join(NUMBER_WORDS)
MONTH_ABBREVIATIONS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}
FULL_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}
MONTH_NAME_PATTERN = "|".join([*FULL_MONTHS, *MONTH_ABBREVIATIONS])
MONTH_YEAR_DATE_PATTERN = rf"(?:(?:{MONTH_NAME_PATTERN})|\d{{1,2}})\s*(?:[-/]\s*|\s+)\d{{4}}"
NUMBER_VALUE_TOKEN = rf"(?:multiple|\d+|{NUMBER_WORD_PATTERN})"
NUMBER_TOKEN = (
    rf"(?:{NUMBER_VALUE_TOKEN}(?:\s+(?:to|or)\s+{NUMBER_VALUE_TOKEN}|"
    rf"\s*[-–—]\s*{NUMBER_VALUE_TOKEN})?)"
)
UNIT_TOKEN = r"day|week|month|quarter|year|days|weeks|months|quarters|years"
WORD_TOKEN = r"[a-z][a-z\-‑–—]*"
SEIZURE_TERMS = (
    r"seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|"
    r"myoclonics?|jerks?|auras?|status epilepticus"
)
QUALIFIED_SEIZURE_TERMS = rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS})"
SEIZURE_RATE_PHRASE = (
    rf"(?:(?:tonic-clonic|myoclonic|convulsive|focal|absence|drop|epileptic|"
    rf"impaired awareness|focal onset|petit mal|brief)\s+){{0,4}}(?:{SEIZURE_TERMS})"
)
SEIZURE_RATE_DESCRIPTOR = (
    r"(?:tonic-clonic|myoclonic|convulsive|focal|absence|drop|epileptic|"
    r"impaired awareness|focal onset|petit mal|simple partial)"
)
SEIZURE_DESCRIPTOR_PHRASE = (
    r"(?:tonic-clonic|myoclonic|convulsive|focal(?:\s+[a-z][a-z-]*){0,3}|"
    r"absence|drop|epileptic|impaired awareness|focal onset|petit mal|simple partial)"
)
SEIZURE_TYPE_DESCRIPTOR = (
    r"(?:focal\s+(?:non-motor|sensory|tonic|clonic|motor|aware|impaired-awareness|"
    r"impaired\s+awareness)|tonic|atonic|myoclonic|absence|petit\s+mal)"
)


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


def _extract_candidates(
    note_text: str, ablation_config: AblationConfig | None = None
) -> list[_RawCandidate]:
    ablation_config = ablation_config or AblationConfig()
    normalized = _normalize_note_text(note_text)
    candidates: list[_RawCandidate] = []
    candidates.extend(_extract_cluster_candidates(normalized, ablation_config))
    candidates.extend(_extract_seizure_free_candidates(normalized, ablation_config))
    candidates.extend(_extract_rate_candidates(normalized, ablation_config))
    candidates.extend(_extract_unknown_candidates(normalized, ablation_config))
    return _prune_contained_frequency_fragments(_dedupe_candidates(candidates), normalized)


def _extract_cluster_candidates(
    text: str, ablation_config: AblationConfig | None = None
) -> list[_RawCandidate]:
    ablation_config = ablation_config or AblationConfig()
    candidates: list[_RawCandidate] = []
    candidates.extend(
        apply_cluster_rules((SEIZURE_FREE_CYCLE_CLUSTER_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules(
            (LAST_CONVULSIVE_CLUSTER_PERSISTENCE_RULE,),
            text,
            ablation_config,
            helpers={
                "clinic_date": _clinic_date,
                "relative_note_date": _relative_note_date,
                "month_span": _month_span,
            },
        )
    )
    candidates.extend(
        apply_cluster_rules((NEARLY_INTERVAL_CLUSTER_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules(
            (SEIZURE_FREE_INTERVAL_DAY_CLUSTER_RULE,), text, ablation_config
        )
    )
    candidates.extend(
        apply_cluster_rules((BATCH_WITHIN_24H_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_cluster_rules((ADJECTIVE_CLUSTER_RATE_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((SHORTHAND_CLUSTER_RATE_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules(
            (CLUSTER_COUNT_THIS_PERIOD_VAGUE_SIZE_RULE,), text, ablation_config
        )
    )
    candidates.extend(
        apply_cluster_rules((CLUSTER_COUNT_THIS_PERIOD_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((LAST_MONTH_CLUSTER_COUNT_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_cluster_rules((CLUSTER_RATE_WITH_SIZE_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules(
            (MONTHLY_CLUSTER_RATE_WITH_SIZE_RULE,), text, ablation_config
        )
    )
    candidates.extend(
        apply_cluster_rules((UNKNOWN_CLUSTER_SIZE_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules(
            (CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE,), text, ablation_config
        )
    )
    candidates.extend(
        apply_cluster_rules((CLUSTERS_EACH_COMPRISING_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((CLUSTER_OVER_PERIOD_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_cluster_rules((RUN_WITH_SEPARATE_DAYS_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((VAGUE_CLUSTER_DAYS_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules(
            (BROAD_CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE,), text, ablation_config
        )
    )

    candidates.extend(
        apply_cluster_rules((CLUSTER_PERIOD_WITH_PER_CLUSTER_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((DESCRIPTOR_CLUSTER_SIZE_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((CLUSTER_TIMING_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_cluster_rules((CLUSTER_DAYS_SIMPLE_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((CLUSTER_SEIZURE_DAYS_PER_PERIOD_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((SHORT_BURST_CLUSTER_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((CLUSTER_COUNT_WITH_IMPLIED_SIZE_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_cluster_rules((CLUSTER_SIZE_WITHOUT_COUNT_RULE,), text, ablation_config)
    )
    return candidates


def _extract_seizure_free_candidates(
    text: str, ablation_config: AblationConfig | None = None
) -> list[_RawCandidate]:
    ablation_config = ablation_config or AblationConfig()
    candidates: list[_RawCandidate] = []
    candidates.extend(
        apply_seizure_free_rules(
            (
                SEIZURE_FREE_SINCE_DATE_RULE,
                ABSENCE_FOR_DURATION_RULE,
                NO_EVENTS_FOR_DURATION_RULE,
                SEIZURE_FREE_DURATION_STATUS_RULE,
                SEIZURE_FREE_ONE_AND_HALF_YEARS_RULE,
                LAST_EPILEPTIC_EVENT_RULE,
                GENERIC_SEIZURE_FREE_RULE,
                NO_DEFINITE_EVENTS_RULE,
                CURRENT_CONTROL_PHRASE_RULE,
            ),
            text,
            ablation_config,
            helpers={
                "clinic_date": _clinic_date,
                "full_date": _full_date,
                "month_span_floor": _month_span_floor,
            },
        )
    )

    return candidates


def _extract_distributed_count_candidates(text: str) -> list[_RawCandidate]:
    candidates: list[_RawCandidate] = []
    event_description = r"[a-z][a-z-]*(?:\s+[a-z][a-z-]*){0,4}"
    distributed_count = re.compile(
        rf"\b(?P<count_a>{NUMBER_VALUE_TOKEN})\s+{event_description}\s+and\s+"
        rf"(?P<count_b>{NUMBER_VALUE_TOKEN})\s+{event_description}\s+"
        rf"(?:(?:in|during)\s+)?(?:the\s+)?(?:last|past|this)\s+"
        rf"(?:(?P<denominator>{NUMBER_VALUE_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in distributed_count.finditer(text):
        count_a = _integer_number_token(match.group("count_a"))
        count_b = _integer_number_token(match.group("count_b"))
        if count_a is None or count_b is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    str(count_a + count_b),
                    match.group("unit"),
                    match.groupdict().get("denominator"),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )
    return candidates


def _extract_rate_candidates(
    text: str, ablation_config: AblationConfig | None = None
) -> list[_RawCandidate]:
    ablation_config = ablation_config or AblationConfig()
    candidates: list[_RawCandidate] = []
    remission_then_breakthrough = re.compile(
        rf"\bseizure[- ]free\s+for\s+(?P<denominator>{NUMBER_TOKEN})\s+"
        rf"(?P<unit>months?|years?)"
        rf".{{0,180}}?\b(?:before\s+experiencing|until)\b"
        rf".{{0,140}}?\b(?:{SEIZURE_TERMS})\b"
        rf"(?:\s+occurred)?(?:\s+(?:{NUMBER_TOKEN})\s+\w+days?\s+ago)?"
        rf"(?:.{{0,80}}?\bpreceded\s+by\s+a\s+cluster\s+of\s+absences\b)?",
        re.IGNORECASE,
    )
    for match in remission_then_breakthrough.finditer(text):
        evidence = _clean_evidence(match.group(0))
        count = "2" if "preceded by a cluster of absences" in evidence.lower() else "1"
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(count, match.group("unit"), match.group("denominator")),
                evidence=evidence,
            )
        )

    no_seizures_then_count = re.compile(
        rf"\bno\s+(?:{SEIZURE_TERMS})\s+for\s+nearly\s+a\s+(?P<unit>year|month)"
        rf".{{0,180}}?\bleading\s+to\s+(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\b"
        rf"(?:\s+(?:{NUMBER_TOKEN})\s+\w+days?\s+ago)?",
        re.IGNORECASE,
    )
    for match in no_seizures_then_count.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    no_seizures_then_single_breakthrough = re.compile(
        rf"\b(?P<evidence>no\s+(?:{SEIZURE_TERMS})\s+for\s+nearly\s+a\s+"
        rf"(?P<unit>year|month).{{0,160}}?\bleading\s+to\s+a\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})(?:\s+{NUMBER_TOKEN}\s+\w+\s+ago)?)\b",
        re.IGNORECASE,
    )
    for match in no_seizures_then_single_breakthrough.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit")),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    no_seizures_then_precursor_count = re.compile(
        rf"\b(?P<evidence>did\s+not\s+have\s+(?:{SEIZURE_TERMS})\s+for\s+"
        rf"over\s+(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>months?|years?),?\s+"
        rf"but\s+then\s+reported\s+(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})(?:\s+{NUMBER_TOKEN}\s+\w+\s+ago)?,\s+"
        rf"each\s+preceded\s+by\s+myoclonic\s+jerks)\b",
        re.IGNORECASE,
    )
    for match in no_seizures_then_precursor_count.finditer(text):
        count = _integer_number_token(match.group("count"))
        if count is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(str(count * 2), match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    medication_withdrawal_burst = re.compile(
        rf"\b(?:discontinued|came off|stopped|withdrew from)\s+"
        rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:on\s+)?(?P<start_date>"
        rf"\d{{1,2}}(?:[-/ ](?:{MONTH_NAME_PATTERN}))|"
        rf"\d{{1,2}}\s+(?:{MONTH_NAME_PATTERN}))\b"
        rf".{{0,120}}?\b(?P<evidence>"
        rf"(?:Shortly afterwards|Soon afterwards|In the following week|"
        rf"Around that period|At that time),?\s+"
        rf"(?:she|he|they)\s+(?:experienced|had|reported)\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS}))\b",
        re.IGNORECASE,
    )
    clinic_date = _clinic_date(text)
    for match in medication_withdrawal_burst.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span(start_date, clinic_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    initial_second_event = re.compile(
        rf"\b(?P<evidence>(?:His|Her|The)\s+(?:initial|first)\s+"
        rf"(?:event|seizure)\s+(?:was|was reported)\s+in\s+"
        rf"(?P<first_month>{MONTH_NAME_PATTERN})\s+(?P<first_year>\d{{4}})"
        rf".{{0,180}}?\b(?:A\s+second|The\s+second)\s+event\s+"
        rf"(?:occurred|took place)\s+.*?\b(?:the\s+following\s+)?"
        rf"(?P<second_month>{MONTH_NAME_PATTERN})\s+(?P<second_year>\d{{4}}))\b",
        re.IGNORECASE,
    )
    for match in initial_second_event.finditer(text):
        start_date = _year_month_date(match.group("first_year"), match.group("first_month"))
        end_date = _year_month_date(match.group("second_year"), match.group("second_month"))
        denominator = _month_span(start_date, end_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("2", "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    first_second_third_event = re.compile(
        rf"\b(?P<evidence>The\s+first\s+seizure\s+was\s+reported\s+in\s+"
        rf"(?P<first_month>{MONTH_NAME_PATTERN})\s+(?P<first_year>\d{{4}})"
        rf".{{0,180}}?\bThe\s+second\s+and\s+third\s+event\s+took\s+place\s+in\s+"
        rf"(?P<second_month>{MONTH_NAME_PATTERN})\s+(?P<second_year>\d{{4}}))\b",
        re.IGNORECASE,
    )
    for match in first_second_third_event.finditer(text):
        start_date = _year_month_date(match.group("first_year"), match.group("first_month"))
        end_date = _year_month_date(match.group("second_year"), match.group("second_month"))
        denominator = _month_span(start_date, end_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("3", "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    first_next_event_narrative = re.compile(
        rf"\b(?P<evidence>(?:His|Her|He|She)\s+first\s+"
        rf"(?:(?:experienced|had)\s+a\s+)?seizure\s+"
        rf"(?:occurred\s+)?(?:was\s+)?in\s+"
        rf"(?P<first_month>{MONTH_NAME_PATTERN})\s+(?P<first_year>\d{{4}})"
        rf".{{0,180}}?\b(?:His|Her|The)\s+"
        rf"(?:(?P<next_count_before>{NUMBER_TOKEN})\s+)?"
        rf"(?P<next_phrase>next|second(?:\s+and\s+third)?)\s+"
        rf"(?:(?P<next_count_after>{NUMBER_TOKEN})\s+)?"
        rf"(?:seizures?|events?)\s+(?:came|was|occurred|took\s+place)\s+in\s+"
        rf"(?P<second_month>{MONTH_NAME_PATTERN})\s+(?P<second_year>\d{{4}}))\b",
        re.IGNORECASE,
    )
    for match in first_next_event_narrative.finditer(text):
        start_date = _year_month_date(match.group("first_year"), match.group("first_month"))
        end_date = _year_month_date(match.group("second_year"), match.group("second_month"))
        denominator = _month_span(start_date, end_date)
        if denominator is None:
            continue
        next_count = match.groupdict().get("next_count_before") or match.groupdict().get(
            "next_count_after"
        )
        if next_count is not None:
            additional_events = _integer_number_token(next_count)
        elif "third" in match.group("next_phrase").lower():
            additional_events = 2
        else:
            additional_events = 1
        if additional_events is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(str(1 + additional_events), "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    residual_jerks_since_date = re.compile(
        rf"\b(?P<evidence>No\s+further\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"have\s+occurred\s+since\s+(?P<start_date>"
        rf"{MONTH_YEAR_DATE_PATTERN}),?\s+although\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+(?:single\s+)?jerks?\s+remain)\b",
        re.IGNORECASE,
    )
    for match in residual_jerks_since_date.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span(start_date, clinic_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    last_tonic_clonic_with_jerks = re.compile(
        rf"\b(?P<evidence>Last\s+tonic[-‑–—]clonic\s+seizure\s+was\s+in\s+"
        rf"(?P<start_date>{MONTH_YEAR_DATE_PATTERN}),?\s+with\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+morning\s+jerks\s+since\s+then)\b",
        re.IGNORECASE,
    )
    for match in last_tonic_clonic_with_jerks.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span(start_date, clinic_date)
        total_count = _increment_number_token(match.group("count"))
        if denominator is None or total_count is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(total_count, "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    clearly_witnessed_tonic_clonic_with_jerks = re.compile(
        rf"\b(?:Her|His|The)\s+(?P<evidence>last\s+clearly\s+witnessed\s+"
        rf"tonic[-‑–—]clonic\s+seizure\s+was\s+in\s+"
        rf"(?P<start_date>{MONTH_YEAR_DATE_PATTERN}),?\s+with\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+morning\s+jerks\s+since\s+then)\b",
        re.IGNORECASE,
    )
    for match in clearly_witnessed_tonic_clonic_with_jerks.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span(start_date, clinic_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    candidates.extend(
        apply_rate_rules(
            (DAILY_BASIS_CURRENT_RULE, DAYS_OF_WEEK_RATE_RULE),
            text,
            ablation_config,
        )
    )

    cluster_spacing_interval = re.compile(
        rf"\b(?P<evidence>(?:{SEIZURE_RATE_PHRASE})\s+typically\s+occur\s+in\s+"
        rf"clusters?,\s+generally\s+spaced\s+(?P<denominator>{NUMBER_TOKEN})\s+"
        rf"(?P<unit>days?|weeks?|months?)\s+apart)\b",
        re.IGNORECASE,
    )
    for match in cluster_spacing_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    candidates.extend(
        apply_rate_rules((NIGHTS_PER_PERIOD_RULE,), text, ablation_config)
    )

    year_to_date_count = re.compile(
        rf"\b(?P<evidence>(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"(?:(?:reported|documented)\s+)?(?:so\s+far\s+this\s+year|"
        rf"this\s+year\s+to\s+date|in\s+\d{{4}}\s+so\s+far))\b",
        re.IGNORECASE,
    )
    for match in year_to_date_count.finditer(text):
        if clinic_date is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month", str(clinic_date.month)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    remission_then_drop_and_jerks = re.compile(
        rf"\b(?P<evidence>(?P<denominator>{NUMBER_TOKEN})\s+months?\s+remission,?\s+"
        rf"then\s+sustained\s+a\s+drop\s+attack(?:\s+\d+\s+\w+\s+ago)?,?\s+"
        rf"preceded\s+by\s+myoclonic\s+jerks)\b",
        re.IGNORECASE,
    )
    for match in remission_then_drop_and_jerks.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("2", "month", match.group("denominator")),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    last_episode_since_date = re.compile(
        rf"\b(?P<evidence>(?:His|Her|The)?\s*"
        rf"(?:last\s+(?:such\s+)?(?:event|episode)|most\s+recent\s+episode)\s+"
        rf"(?:was\s+)?(?:recorded\s+)?(?:occurred\s+)?on\s+"
        rf"(?P<start_date>\d{{1,2}}[-/ ](?:{MONTH_NAME_PATTERN})))\b",
        re.IGNORECASE,
    )
    for match in last_episode_since_date.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span_with_terminal_partial(start_date, clinic_date)
        if denominator is None:
            continue
        evidence = _clean_evidence(match.group("evidence"))
        if evidence.lower().startswith("the last such episode"):
            evidence = evidence.removeprefix("The ")
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", "month", str(denominator)),
                evidence=evidence,
            )
        )

    candidates.extend(
        apply_diary_rules(
            SLEEP_AWAKE_MONTH_SUMMARY_RULES,
            text,
            ablation_config,
            helpers={
                "clinic_date": _clinic_date,
                "relative_note_date": _relative_note_date,
                "month_span": _month_span,
            },
        )
    )

    candidates.extend(
        apply_diary_rules(
            MONTHLY_DIARY_SUMMARY_RULES,
            text,
            ablation_config,
            helpers={
                "clinic_date": _clinic_date,
                "relative_note_date": _relative_note_date,
                "month_span_inclusive": _month_span_inclusive,
            },
        )
    )
    candidates.extend(_extract_distributed_count_candidates(text))

    candidates.extend(apply_rate_rules((DESCRIPTOR_RATE_RULE,), text, ablation_config))
    candidates.extend(
        apply_rate_rules((QUALIFIED_DIRECT_RATE_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_rate_rules((QUARTER_DIRECT_RATE_RULE,), text, ablation_config)
    )

    candidates.extend(apply_rate_rules((DIRECT_RATE_RULE,), text, ablation_config))

    candidates.extend(
        apply_rate_rules((COUNT_DURING_RECENT_WINDOW_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((THERE_HAVE_BEEN_COUNT_RULE,), text, ablation_config)
    )

    over_period = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS}|{SEIZURE_DESCRIPTOR_PHRASE})\s+"
        rf"(?:over|in|during|across)\s+(?:the\s+)?(?:last|past)?\s*"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in over_period.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    match.group("count"),
                    match.group("unit"),
                    match.group("denominator"),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    candidates.extend(apply_rate_rules((IMPLICIT_INTERVAL_RULE,), text, ablation_config))

    candidates.extend(
        apply_rate_rules((IMPLICIT_NIGHTLY_INTERVAL_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((IMPLICIT_EVERY_OTHER_INTERVAL_RULE,), text, ablation_config)
    )

    candidates.extend(apply_rate_rules((OCCURRING_INTERVAL_RULE,), text, ablation_config))

    candidates.extend(
        apply_rate_rules((OCCURRING_EVERY_OTHER_INTERVAL_RULE,), text, ablation_config)
    )

    fortnight_interval = re.compile(
        r"\bonce\s+in\s+a\s+fortnight\b",
        re.IGNORECASE,
    )
    for match in fortnight_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", "week", "2"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    second_period_interval = re.compile(
        r"\bhappening\s+(?:about\s+|roughly\s+|approximately\s+)?every\s+second\s+"
        r"(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    )
    for match in second_period_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), "2"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    median_interval = re.compile(
        rf"\bmedian\s+inter-seizure\s+interval\s*(?:≈|~|=|is)?\s*"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in median_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    ranging_interval = re.compile(
        rf"\b(?:(?:{SEIZURE_TERMS})\s+occurring\s+with\s+|occurring\s+with\s+)?"
        rf"intervals\s+ranging\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in ranging_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    standalone_every_interval = re.compile(
        rf"\bEvery\s+(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN})"
        r"(?:\s+on\s+average)?\b",
        re.IGNORECASE,
    )
    for match in standalone_every_interval.finditer(text):
        if _has_historical_lead_in(text, match.start()):
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    typical_month_single = re.compile(
        rf"\b(?P<count>one|single|1)\s+(?:brief\s+)?(?:{SEIZURE_RATE_PHRASE})\s+"
        r"in\s+a\s+typical\s+month\b",
        re.IGNORECASE,
    )
    for match in typical_month_single.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    implicit_a_period = re.compile(
        rf"\b(?:{SEIZURE_TERMS})\s+(?P<count>once|twice|thrice)\s+"
        rf"(?:a|an|per)\s+(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    )
    for match in implicit_a_period.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    frequency_a_period = re.compile(
        r"\b(?P<count>once|twice|thrice)\s+(?:a|an)\s+"
        r"(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    )
    for match in frequency_a_period.finditer(text):
        if _is_medication_or_dose_rate_distractor(match, text):
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    candidates.extend(
        apply_rate_rules((NO_MORE_THAN_ADVERBIAL_RATE_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((OCCURRING_ONCE_PER_NIGHT_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((PERSISTENT_ADVERBIAL_RATE_RULE,), text, ablation_config)
    )

    qualitative_recent_multiple = re.compile(
        rf"\b(?P<evidence>(?:occurring\s+)?(?:multiple|several)\s+"
        rf"(?:times|(?:{QUALIFIED_SEIZURE_TERMS}))\s+"
        rf"(?:in\s+)?(?:the\s+)?past\s+week|"
        rf"Several\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+per\s+week|"
        rf"(?:{QUALIFIED_SEIZURE_TERMS}|{SEIZURE_TYPE_DESCRIPTOR})\s+"
        rf"occur\s+several\s+times\s+"
        rf"(?:each|per)\s+week|"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+several\s+times\s+per\s+week|"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+on\s+most\s+days)\b",
        re.IGNORECASE,
    )
    for match in qualitative_recent_multiple.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="multiple per week",
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    most_nights_rate = re.compile(
        r"\b(?P<evidence>happening\s+on\s+most\s+nights\s+of\s+the\s+week)\b",
        re.IGNORECASE,
    )
    for match in most_nights_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="multiple per week",
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    near_daily_dozens_rate = re.compile(
        rf"\b(?P<evidence>(?:{QUALIFIED_SEIZURE_TERMS}|{SEIZURE_DESCRIPTOR_PHRASE})\s+"
        rf"occur\s+on\s+a\s+"
        rf"near-daily\s+basis,\s+sometimes\s+dozens\s+in\s+a\s+day)\b",
        re.IGNORECASE,
    )
    for match in near_daily_dozens_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="multiple per day",
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    candidates.extend(
        apply_rate_rules((COUNTED_ADVERBIAL_RATE_RULE,), text, ablation_config)
    )

    most_weekdays_rate = re.compile(
        rf"\b(?:(?:she|he|they|patient|carer|caregiver)\s+reports?\s+)?"
        rf"(?P<evidence>(?:{QUALIFIED_SEIZURE_TERMS})\s+occurring\s+on\s+"
        rf"most\s+weekdays)\b",
        re.IGNORECASE,
    )
    for match in most_weekdays_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="multiple per week",
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    candidates.extend(
        apply_rate_rules((SIMPLE_PARTIAL_ADVERBIAL_RATE_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((SEIZURE_ADJECTIVE_RATE_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((STANDALONE_ADJECTIVE_RATE_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((OCCURRING_ADJECTIVE_RATE_RULE,), text, ablation_config)
    )

    candidates.extend(apply_rate_rules((RECENT_COUNT_RULE,), text, ablation_config))

    candidates.extend(
        apply_rate_rules((PERIOD_FIRST_RECENT_COUNT_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((PERIOD_FIRST_EXPERIENCED_COUNT_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((PERIOD_FIRST_FEATURING_COUNT_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((PERIOD_FIRST_TIMEFRAME_COUNT_RULE,), text, ablation_config)
    )

    period_first_distributed_count = re.compile(
        rf"\b(?P<period>Over the past|Over the last|During the past|During the last|"
        rf"over the past|over the last|during the past|during the last)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN}),?\s+"
        rf".{{0,80}}?\b(?P<count_a>{NUMBER_VALUE_TOKEN})\s+"
        rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS}).{{0,120}}?\band\s+"
        rf"(?:approximately\s+|about\s+|around\s+)?(?P<count_b>{NUMBER_VALUE_TOKEN})\s+"
        rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS})\b",
        re.IGNORECASE,
    )
    for match in period_first_distributed_count.finditer(text):
        count_a = _integer_number_token(match.group("count_a"))
        count_b = _integer_number_token(match.group("count_b"))
        if count_a is None or count_b is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    str(count_a + count_b),
                    match.group("unit"),
                    match.group("denominator"),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    candidates.extend(
        apply_rate_rules((PERIOD_FIRST_OCCURRED_COUNT_RULE,), text, ablation_config)
    )

    adjective_count_rates = (
        (r"daily", "day"),
        (r"weekly", "week"),
        (r"monthly", "month"),
        (r"yearly", "year"),
    )
    for adjective, unit in adjective_count_rates:
        pattern = re.compile(
            rf"\b(?:occurring|occur|occurs)\s+(?:roughly\s+|approximately\s+|about\s+)?"
            rf"(?P<count>{NUMBER_TOKEN})\s+{adjective}\b",
            re.IGNORECASE,
        )
        for match in pattern.finditer(text):
            candidates.append(
                _RawCandidate(
                    kind=CandidateKind.FREQUENCY_RATE,
                    label=_rate_label(match.group("count"), unit),
                    evidence=_clean_evidence(match.group(0)),
                )
            )

    candidates.extend(
        apply_rate_rules((RECORDED_YEAR_COUNT_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_rate_rules((YESTERDAY_OR_TODAY_COUNT_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_diary_rules((SEIZURE_DAYS_PER_PERIOD_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_diary_rules((SEIZURE_DAYS_FRACTION_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_gan_shorthand_rules(
            (
                TC_SZ_COUNT_RATE_RULE,
                ABS_ADJECTIVE_RATE_RULE,
                ABS_COUNT_RATE_RULE,
                Q_INTERVAL_RULE,
            ),
            text,
            ablation_config,
        )
    )

    candidates.extend(
        apply_diary_rules((DIARY_DATE_LIST_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_diary_rules((SEIZURE_DAY_LOG_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_diary_rules((MONTHLY_COUNT_LOG_RULE,), text, ablation_config)
    )
    candidates.extend(
        apply_diary_rules((SPARSE_FULL_MONTH_LOG_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_diary_rules((INCREASING_MONTHLY_COUNT_RULE,), text, ablation_config)
    )

    candidates.extend(
        apply_diary_rules((RECORDED_MONTH_LOG_RULE,), text, ablation_config)
    )

    last_prior_event_interval = re.compile(
        r"\bLast event:\s*[^.;]*?\b\d+\s+weeks?\s+ago[^.;]*?;\s+prior\s+to\s+that,\s+"
        r"one\s+event\s+in\s+late\s+[A-Z][a-z]+\s+\d{4}\b",
        re.IGNORECASE,
    )
    for match in last_prior_event_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="1 per 1 to 2 month",
                evidence=_clean_evidence(match.group(0)),
            )
        )

    bad_week_ceiling = re.compile(
        rf"\bup\s+to\s+(?P<count>{NUMBER_TOKEN})\s+in\s+bad\s+weeks\b",
        re.IGNORECASE,
    )
    for match in bad_week_ceiling.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "week"),
                evidence=_clean_evidence(match.group(0)),
            )
        )
    return candidates


def _extract_unknown_candidates(
    text: str, ablation_config: AblationConfig
) -> list[_RawCandidate]:
    trigger_conditioned = [
        re.compile(
            r"\bonly\s+when\s+significantly\s+short\s+on\s+sleep\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bSeizures\s+happen\s+when\s+perimenstrual\s+only\s+\(days\s+-3\s+to\s+\+3\)",
            re.IGNORECASE,
        ),
    ]
    candidates = [
        _RawCandidate(
            kind=CandidateKind.UNKNOWN_FREQUENCY,
            label="unknown",
            evidence=_clean_evidence(match.group(0)),
        )
        for pattern in trigger_conditioned
        for match in pattern.finditer(text)
    ]
    context = ExtractionContext(text=text)
    candidates.extend(
        candidate
        for candidate in QUALITATIVE_IMPROVEMENT_UNKNOWN_RULE.apply(
            context, ablation_config
        )
        if isinstance(candidate, _RawCandidate)
    )
    unknown = re.compile(
        r"\b(?:frequency unclear|unclear frequency|cannot specify how often|last seizure\b.*?)",
        re.IGNORECASE,
    )
    candidates.extend(
        _RawCandidate(
            kind=CandidateKind.UNKNOWN_FREQUENCY,
            label="unknown",
            evidence=_clean_evidence(match.group(0)),
        )
        for match in unknown.finditer(text)
    )
    return candidates


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


def _select_final_event(
    candidate_events: list[CandidateEvent],
    normalized_events: list[NormalizedEvent],
    ablation_config: AblationConfig | None = None,
) -> FinalSelection:
    ablation_config = ablation_config or AblationConfig()
    pairs = list(zip(candidate_events, normalized_events, strict=True))
    scored_pairs = [
        (event, normalized, _selection_score((event, normalized), ablation_config))
        for event, normalized in pairs
    ]
    selected_event, selected_normalized, selected_score = max(
        scored_pairs,
        key=lambda scored_pair: scored_pair[2].priority(),
    )
    selected_rationale = _selection_rationale(selected_normalized)
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


def _selection_score(
    pair: tuple[CandidateEvent, NormalizedEvent],
    ablation_config: AblationConfig | None = None,
) -> SelectionScore:
    ablation_config = ablation_config or AblationConfig()
    event, normalized = pair
    evidence = event.evidence.lower()
    if normalized.semantic_kind is FrequencyLabelKind.FREQUENCY:
        evidence_priority = _frequency_summary_priority(evidence)
        return _ablatable_selection_score(
            ablation_config,
            semantic_priority=4,
            evidence_priority=evidence_priority,
            monthly_frequency_priority=normalized.monthly_frequency,
            reason=(
                "frequency_current_summary"
                if evidence_priority > 0
                else "frequency_monthly_rate"
            ),
        )
    if normalized.semantic_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        if _is_specific_current_multiple_evidence(event.evidence):
            return _ablatable_selection_score(
                ablation_config,
                semantic_priority=4,
                evidence_priority=1,
                monthly_frequency_priority=normalized.monthly_frequency,
                reason="specific_current_multiple",
            )
        return _ablatable_selection_score(
            ablation_config,
            semantic_priority=3,
            evidence_priority=0,
            monthly_frequency_priority=0.0,
            reason="generic_unresolved_multiple",
        )
    if normalized.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        if _is_current_seizure_free_evidence(evidence):
            return _ablatable_selection_score(
                ablation_config,
                semantic_priority=5,
                evidence_priority=0,
                monthly_frequency_priority=0.0,
                reason="current_seizure_free",
            )
        return _ablatable_selection_score(
            ablation_config,
            semantic_priority=2,
            evidence_priority=0,
            monthly_frequency_priority=0.0,
            reason="generic_seizure_free",
        )
    if normalized.semantic_kind is FrequencyLabelKind.UNKNOWN:
        if _is_trigger_conditioned_unknown_evidence(evidence):
            return _ablatable_selection_score(
                ablation_config,
                semantic_priority=6,
                evidence_priority=0,
                monthly_frequency_priority=0.0,
                reason="trigger_conditioned_unknown",
            )
        return _ablatable_selection_score(
            ablation_config,
            semantic_priority=1,
            evidence_priority=0,
            monthly_frequency_priority=0.0,
            reason="generic_unknown",
        )
    return _ablatable_selection_score(
        ablation_config,
        semantic_priority=0,
        evidence_priority=0,
        monthly_frequency_priority=0.0,
        reason="no_reference",
    )


def _ablatable_selection_score(
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


def _selection_rationale(normalized: NormalizedEvent) -> str:
    if normalized.semantic_kind is FrequencyLabelKind.FREQUENCY:
        return "Selected the highest normalized current frequency candidate."
    if normalized.semantic_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        return "Selected an unresolved multiple-frequency candidate."
    if normalized.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        return "Selected the explicit seizure-free statement."
    if normalized.semantic_kind is FrequencyLabelKind.UNKNOWN:
        return "Selected seizure-frequency evidence that could not be converted to a rate."
    return "No seizure-frequency evidence was found."


def _is_specific_current_multiple_evidence(evidence: str) -> bool:
    normalized = evidence.lower()
    return (
        "most weekdays" in normalized
        or "most nights of the week" in normalized
        or "several episodes per week" in normalized
        or "multiple times in past week" in normalized
        or "near-daily basis, sometimes dozens in a day" in normalized
        or re.search(r"\boccur\s+several\s+times\s+(?:each|per)\s+week\b", normalized)
        is not None
        or re.search(r"\bon\s+most\s+days\b", normalized) is not None
        or (
            "several" in normalized and re.search(r"\blast\s+week\b", normalized) is not None
        )
    )


def _frequency_summary_priority(evidence: str) -> int:
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


def _is_trigger_conditioned_unknown_evidence(evidence: str) -> bool:
    return (
        "only when significantly short on sleep" in evidence
        or "perimenstrual only" in evidence
        or evidence.startswith("better over the past")
    )


def _is_current_seizure_free_evidence(evidence: str) -> bool:
    return (
        re.search(r"\bseizure-free since \d{1,2}(?:[-/ ]|$)", evidence) is not None
        or re.search(r"\bseizure-free interval since \d{1,2}(?:[-/ ]|$)", evidence)
        is not None
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


def _clinic_date(text: str) -> _ParsedMonthDate | None:
    match = re.search(
        rf"\b(?:Clinic Date:|Sent:|Date:)\s*(?P<day>\d{{1,2}})\s+"
        rf"(?P<month>{MONTH_NAME_PATTERN})\s+(?P<year>\d{{4}})\b",
        text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    return _ParsedMonthDate(
        year=int(match.group("year")),
        month=_month_number(match.group("month")),
        day=int(match.group("day")),
    )


def _relative_note_date(value: str, anchor: _ParsedMonthDate | None) -> _ParsedMonthDate | None:
    normalized = value.strip()
    day_month = re.match(
        rf"(?P<day>\d{{1,2}})[-/ ](?P<month>{MONTH_NAME_PATTERN})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_month is not None and anchor is not None:
        month = _month_number(day_month.group("month"))
        year = anchor.year - 1 if month > anchor.month else anchor.year
        return _ParsedMonthDate(year=year, month=month, day=int(day_month.group("day")))

    month_year = re.match(
        rf"(?P<month>{MONTH_NAME_PATTERN})[-/ ](?P<year>\d{{4}})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if month_year is not None:
        return _year_month_date(month_year.group("year"), month_year.group("month"))

    numeric_or_named_month_year = re.match(
        rf"(?P<month>(?:{MONTH_NAME_PATTERN})|\d{{1,2}})\s*[-/]\s*(?P<year>\d{{4}})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if numeric_or_named_month_year is not None:
        return _year_month_date(
            numeric_or_named_month_year.group("year"),
            numeric_or_named_month_year.group("month"),
        )

    month_only = re.match(
        rf"(?P<month>{MONTH_NAME_PATTERN})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if month_only is not None and anchor is not None:
        month = _month_number(month_only.group("month"))
        year = anchor.year - 1 if month > anchor.month else anchor.year
        return _ParsedMonthDate(year=year, month=month)

    return None


def _full_date(value: str) -> _ParsedMonthDate | None:
    normalized = value.strip()
    numeric = re.match(
        r"(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})$",
        normalized,
    )
    if numeric is not None:
        return _ParsedMonthDate(
            year=int(numeric.group("year")),
            month=int(numeric.group("month")),
            day=int(numeric.group("day")),
        )

    day_named = re.match(
        rf"(?P<day>\d{{1,2}})[-\s](?P<month>{MONTH_NAME_PATTERN})[-\s](?P<year>\d{{4}})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_named is not None:
        return _ParsedMonthDate(
            year=int(day_named.group("year")),
            month=_month_number(day_named.group("month")),
            day=int(day_named.group("day")),
        )
    return None


def _year_month_date(year: str, month: str) -> _ParsedMonthDate:
    return _ParsedMonthDate(year=int(year), month=_month_number(month))


def _month_number(value: str) -> int:
    stripped = value.strip()
    if stripped.isdigit():
        return int(stripped)
    normalized = stripped.lower()[:3]
    return MONTH_ABBREVIATIONS[normalized]


def _month_span(start: _ParsedMonthDate | None, end: _ParsedMonthDate | None) -> int | None:
    if start is None or end is None:
        return None
    months = (end.year - start.year) * 12 + end.month - start.month
    if months <= 0:
        return None
    return months


def _month_span_floor(start: _ParsedMonthDate | None, end: _ParsedMonthDate | None) -> int | None:
    months = _month_span(start, end)
    if months is None:
        return None
    if start.day is not None and end.day is not None and end.day < start.day:
        months -= 1
    return months if months > 0 else None


def _month_span_with_terminal_partial(
    start: _ParsedMonthDate | None, end: _ParsedMonthDate | None
) -> int | None:
    months = _month_span(start, end)
    if months is None:
        return None
    if start.day is not None and end.day is not None and end.day > start.day:
        return months + 1
    return months


def _month_span_inclusive(
    start: _ParsedMonthDate | None, end: _ParsedMonthDate | None
) -> int | None:
    if start is None or end is None:
        return None
    months = (end.year - start.year) * 12 + end.month - start.month
    if months < 0:
        return None
    return months + 1


def _rate_label(count: str, unit: str, denominator: str | None = None) -> str:
    count_value = _number_token(count)
    unit_value = _singular_unit(unit)
    denominator_value = _number_token(denominator) if denominator else None
    if unit_value == "fortnight":
        unit_value = "week"
        denominator_value = "2"
    if unit_value == "quarter":
        unit_value = "month"
        denominator_value = _quarter_month_denominator(denominator_value)
    if denominator_value in {None, "1"}:
        return f"{count_value} per {unit_value}"
    return f"{count_value} per {denominator_value} {unit_value}"


def _number_token(value: str | None) -> str:
    if value is None:
        return "1"
    normalized = re.sub(r"\s*[-–—]\s*", " to ", value.lower())
    normalized = " ".join(normalized.split())
    if " to " in normalized:
        return " to ".join(_number_token(part) for part in normalized.split(" to "))
    if " or " in normalized:
        return " to ".join(_number_token(part) for part in normalized.split(" or "))
    return NUMBER_WORDS.get(normalized, normalized)


def _cluster_size_token(value: str | None) -> str:
    if value is None:
        return "multiple"
    normalized = re.sub(r"\bor more\b", "", value, flags=re.IGNORECASE)
    normalized = re.sub(r"[≈~]", "", normalized)
    normalized = re.sub(r"\s*-\s*", " to ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if normalized == "":
        return "multiple"
    return _number_token(normalized)


def _infer_cluster_size(text: str) -> str:
    patterns = [
        re.compile(
            rf"\beach\s+(?:approximately|about|around|roughly|\~|≈)?\s*(?P<count>{NUMBER_TOKEN})(?:\s*to\s*{NUMBER_TOKEN})?\s+(?:{SEIZURE_TERMS}|events?|episodes?|spells?)",
            re.IGNORECASE,
        ),
        re.compile(
            rf"\b(?:usually|typically)\s+(?:approximately|about|around|roughly|\~|≈)?\s*(?P<count>{NUMBER_TOKEN})(?:\s*or\s+more)?\s+(?:{SEIZURE_TERMS}|events?|episodes?|spells?)",
            re.IGNORECASE,
        ),
        re.compile(
            rf"\beach\s+cluster\s+(?:involves|comprising|comprised of)\s+"
            rf"(?:approximately|about|around|roughly|\~|≈)?\s*(?P<count>{NUMBER_TOKEN})(?:\s*to\s*{NUMBER_TOKEN})?\s+"
            rf"(?:{WORD_TOKEN}\s+){{0,2}}(?:{SEIZURE_TERMS}|events?|episodes?|spells?)",
            re.IGNORECASE,
        ),
        re.compile(
            rf"\b(?:approximately|about|around|roughly|\~|≈)?\s*(?P<count>{NUMBER_TOKEN})(?:\s*or\s+more)?\s+per\s*(?:cluster|episode)\b",
            re.IGNORECASE,
        ),
        re.compile(
            rf"(?P<count>{NUMBER_TOKEN})\s+(?:{SEIZURE_TERMS}|events?|episodes?|spells?)\s+per\s+(?:cluster|episode)\b",
            re.IGNORECASE,
        ),
        re.compile(rf"(?P<count>{NUMBER_TOKEN})\s+times\b", re.IGNORECASE),
    ]
    for pattern in patterns:
        match = pattern.search(text)
        if match is not None:
            return _cluster_size_token(match.group("count"))
    return "multiple"


def _integer_number_token(value: str) -> int | None:
    normalized = _number_token(value)
    if normalized.isdigit():
        return int(normalized)
    return None


def _increment_number_token(value: str) -> str | None:
    normalized = _number_token(value)
    if " to " in normalized:
        parts = normalized.split(" to ")
        increments = []
        for part in parts:
            if not part.isdigit():
                return None
            increments.append(str(int(part) + 1))
        return " to ".join(increments)
    if normalized.isdigit():
        return str(int(normalized) + 1)
    return None


def _quarter_month_denominator(denominator: str | None) -> str:
    if denominator in {None, "1"}:
        return "3"
    if denominator and denominator.isdigit():
        return str(int(denominator) * 3)
    return f"3 {denominator}"


def _singular_unit(value: str) -> str:
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


def _period_unit_label(value: str) -> str:
    normalized = value.lower().strip()
    if normalized == "fortnight":
        return "2 week"
    return _singular_unit(normalized)


def _period_label(unit: str, denominator: str | None = None) -> str:
    denominator_value = _number_token(denominator) if denominator else None
    unit_value = _singular_unit(unit)
    if denominator_value in {None, "1"}:
        return unit_value
    return f"{denominator_value} {unit_value}"


def _cluster_period_label(unit: str) -> str:
    unit_value = _singular_unit(unit)
    if unit_value in {"daily", "weekly", "monthly", "yearly", "fortnightly"}:
        return unit_value[:-2] if unit_value.endswith("ly") else unit_value
    if unit_value == "fortnight":
        return "2 week"
    if unit_value == "quarter":
        return "3 month"
    return unit_value


def _expanded_compact_unit(value: str) -> str:
    return {
        "d": "day",
        "day": "day",
        "wk": "week",
        "week": "week",
        "mo": "month",
        "month": "month",
        "yr": "year",
        "year": "year",
    }[value.lower()]


def _adverbial_period_unit(value: str) -> str:
    return {
        "daily": "day",
        "weekly": "week",
        "monthly": "month",
        "yearly": "year",
    }[value.lower()]


def _has_historical_lead_in(text: str, start: int) -> bool:
    preceding = text[max(0, start - 140) : start].lower()
    historical_markers = (
        "by way of comparison",
        "compared with earlier",
        "compared with the earlier",
        "earlier pattern",
        "prior to this",
        "prior to these",
        "prior to recent",
        "prior pattern",
        "historical description",
        "before improvement",
        "previously",
        "historically",
    )
    current_markers = (
        "over the past",
        "over the last",
        "current",
        "now",
        "however",
        "at present",
        "has reduced",
        "have reduced",
        "stabilised at",
        "stabilized at",
    )
    latest_historical = max((preceding.rfind(marker) for marker in historical_markers), default=-1)
    if latest_historical == -1:
        return False
    latest_current = max((preceding.rfind(marker) for marker in current_markers), default=-1)
    return latest_current < latest_historical


def _is_medication_or_dose_rate_distractor(match: re.Match[str], text: str) -> bool:
    preceding = text[max(0, match.start() - 80) : match.start()].lower()
    following = text[match.end() : match.end() + 80].lower()
    surrounding = f"{preceding} {match.group(0).lower()} {following}"
    dose_pattern = re.compile(
        r"\b(?:dose|dosing|current treatment|current medication|medication|"
        r"levetiracetam|lamotrigine|carbamazepine|brivaracetam|lacosamide|"
        r"valproate|epilim|topiramate|zonisamide|sumatriptan)\b"
        r".{0,80}(?:\b\d+\s*(?:mg|g|micrograms?|mcg|µg)\b|"
        r"\b(?:mg|g|micrograms?|mcg|µg)\b)",
        re.IGNORECASE,
    )
    if dose_pattern.search(surrounding):
        return True
    if re.search(r"\b(?:migraine|headache|prn)\b", surrounding) and re.search(
        r"\bper\s+(?:day|week|month|year)\b", match.group(0), re.IGNORECASE
    ):
        return True
    return False


def _normalize_note_text(note_text: str) -> str:
    return re.sub(r"\s+", " ", note_text)


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")


def _fallback_evidence(note_text: str) -> str:
    first_sentence = re.split(r"(?<=[.!?])\s+", note_text.strip(), maxsplit=1)[0]
    return first_sentence[:240] if first_sentence else ""


def _exact_evidence(note_text: str, evidence: str) -> str:
    if evidence in note_text:
        return evidence
    pattern = r"\s+".join(re.escape(part) for part in evidence.split())
    match = re.search(pattern, note_text)
    if match:
        return note_text[match.start() : match.end()].strip(" .;:\n\t")
    return evidence


def _dedupe_candidates(candidates: list[_RawCandidate]) -> list[_RawCandidate]:
    seen: set[tuple[CandidateKind, str | None, str]] = set()
    deduped: list[_RawCandidate] = []
    for candidate in candidates:
        key = (candidate.kind, candidate.label, candidate.evidence)
        if key not in seen:
            seen.add(key)
            deduped.append(candidate)
    return deduped


def _prune_contained_frequency_fragments(
    candidates: list[_RawCandidate], text: str
) -> list[_RawCandidate]:
    has_current_frequency_candidate = any(
        candidate.kind in {CandidateKind.FREQUENCY_RATE, CandidateKind.CLUSTER_FREQUENCY}
        and not _is_historical_candidate(candidate, text)
        for candidate in candidates
    )
    pruned: list[_RawCandidate] = []
    for candidate in candidates:
        if candidate.kind is CandidateKind.FREQUENCY_RATE and any(
            _is_contained_monthly_list_fragment(candidate, other) for other in candidates
        ):
            continue
        if (
            has_current_frequency_candidate
            and candidate.kind in {CandidateKind.FREQUENCY_RATE, CandidateKind.CLUSTER_FREQUENCY}
            and _is_historical_candidate(candidate, text)
        ):
            continue
        pruned.append(candidate)
    return pruned


def _is_contained_monthly_list_fragment(candidate: _RawCandidate, other: _RawCandidate) -> bool:
    if other is candidate or other.kind is not CandidateKind.FREQUENCY_RATE:
        return False
    candidate_evidence = candidate.evidence.lower()
    other_evidence = other.evidence.lower()
    if candidate_evidence == other_evidence or candidate_evidence not in other_evidence:
        return False
    if len(other_evidence) < len(candidate_evidence) + 20:
        return False
    month_mentions = re.findall(rf"\b(?:{MONTH_NAME_PATTERN})\b", other.evidence, re.IGNORECASE)
    if len(month_mentions) < 2:
        return False
    return any(
        marker in other_evidence
        for marker in (
            "this month",
            "as of this month",
            "has recorded",
            "cluster of",
            "run of",
        )
    )


def _is_historical_candidate(candidate: _RawCandidate, text: str) -> bool:
    match = re.search(r"\s+".join(re.escape(part) for part in candidate.evidence.split()), text)
    if match is None:
        return False
    return _has_historical_lead_in(text, match.start())
