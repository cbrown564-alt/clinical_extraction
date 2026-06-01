from __future__ import annotations

import re

from .candidates import (
    CandidateKind,
    RawCandidate,
)
from .deterministic_candidate_pruning import (
    dedupe_candidates as _dedupe_candidates,
)
from .deterministic_candidate_pruning import (
    prune_contained_frequency_fragments as _prune_contained_frequency_fragments,
)
from .deterministic_rate_extraction import (
    extract_rate_candidates,
)
from .deterministic_text import (
    clean_evidence as _clean_evidence,
)
from .deterministic_text import (
    normalize_note_text as _normalize_note_text,
)
from .rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)
from .rules.cluster import (
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
from .rules.seizure_free import (
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
from .temporal import (
    clinic_date as _clinic_date,
)
from .temporal import (
    full_date as _full_date,
)
from .temporal import (
    month_span as _month_span,
)
from .temporal import (
    month_span_floor as _month_span_floor,
)
from .temporal import (
    relative_note_date as _relative_note_date,
)

_RawCandidate = RawCandidate


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


def _extract_candidates(
    note_text: str, ablation_config: AblationConfig | None = None
) -> list[_RawCandidate]:
    ablation_config = ablation_config or AblationConfig()
    normalized = _normalize_note_text(note_text)
    candidates: list[_RawCandidate] = []
    candidates.extend(_extract_cluster_candidates(normalized, ablation_config))
    candidates.extend(_extract_seizure_free_candidates(normalized, ablation_config))
    candidates.extend(extract_rate_candidates(normalized, ablation_config))
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
    candidates.extend(apply_cluster_rules((NEARLY_INTERVAL_CLUSTER_RULE,), text, ablation_config))
    candidates.extend(
        apply_cluster_rules((SEIZURE_FREE_INTERVAL_DAY_CLUSTER_RULE,), text, ablation_config)
    )
    candidates.extend(apply_cluster_rules((BATCH_WITHIN_24H_RULE,), text, ablation_config))

    candidates.extend(apply_cluster_rules((ADJECTIVE_CLUSTER_RATE_RULE,), text, ablation_config))
    candidates.extend(apply_cluster_rules((SHORTHAND_CLUSTER_RATE_RULE,), text, ablation_config))
    candidates.extend(
        apply_cluster_rules((CLUSTER_COUNT_THIS_PERIOD_VAGUE_SIZE_RULE,), text, ablation_config)
    )
    candidates.extend(apply_cluster_rules((CLUSTER_COUNT_THIS_PERIOD_RULE,), text, ablation_config))
    candidates.extend(apply_cluster_rules((LAST_MONTH_CLUSTER_COUNT_RULE,), text, ablation_config))

    candidates.extend(apply_cluster_rules((CLUSTER_RATE_WITH_SIZE_RULE,), text, ablation_config))
    candidates.extend(
        apply_cluster_rules((MONTHLY_CLUSTER_RATE_WITH_SIZE_RULE,), text, ablation_config)
    )
    candidates.extend(apply_cluster_rules((UNKNOWN_CLUSTER_SIZE_RULE,), text, ablation_config))
    candidates.extend(
        apply_cluster_rules((CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE,), text, ablation_config)
    )
    candidates.extend(apply_cluster_rules((CLUSTERS_EACH_COMPRISING_RULE,), text, ablation_config))
    candidates.extend(apply_cluster_rules((CLUSTER_OVER_PERIOD_RULE,), text, ablation_config))

    candidates.extend(apply_cluster_rules((RUN_WITH_SEPARATE_DAYS_RULE,), text, ablation_config))
    candidates.extend(apply_cluster_rules((VAGUE_CLUSTER_DAYS_RULE,), text, ablation_config))
    candidates.extend(
        apply_cluster_rules(
            (BROAD_CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE,), text, ablation_config
        )
    )

    candidates.extend(
        apply_cluster_rules((CLUSTER_PERIOD_WITH_PER_CLUSTER_RULE,), text, ablation_config)
    )
    candidates.extend(apply_cluster_rules((DESCRIPTOR_CLUSTER_SIZE_RULE,), text, ablation_config))
    candidates.extend(apply_cluster_rules((CLUSTER_TIMING_RULE,), text, ablation_config))

    candidates.extend(apply_cluster_rules((CLUSTER_DAYS_SIMPLE_RULE,), text, ablation_config))
    candidates.extend(
        apply_cluster_rules((CLUSTER_SEIZURE_DAYS_PER_PERIOD_RULE,), text, ablation_config)
    )
    candidates.extend(apply_cluster_rules((SHORT_BURST_CLUSTER_RULE,), text, ablation_config))
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


def _extract_unknown_candidates(text: str, ablation_config: AblationConfig) -> list[_RawCandidate]:
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
        for candidate in QUALITATIVE_IMPROVEMENT_UNKNOWN_RULE.apply(context, ablation_config)
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
