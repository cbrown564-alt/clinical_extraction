from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import cast

from clinical_extraction.tasks.seizure_frequency.gan2026.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
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
NUMBER_VALUE_TOKEN = rf"(?:multiple|\d+|{NUMBER_WORD_PATTERN})"
NUMBER_TOKEN = (
    rf"(?:{NUMBER_VALUE_TOKEN}(?:\s+(?:to|or)\s+{NUMBER_VALUE_TOKEN}|"
    rf"\s*[-–—]\s*{NUMBER_VALUE_TOKEN})?)"
)
WORD_TOKEN = r"[a-z][a-z\-‑–—]*"
UNIT_TOKEN = r"day|week|month|quarter|year|days|weeks|months|quarters|years"
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
SEIZURE_TERMS = (
    r"seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|"
    r"myoclonics?|jerks?|auras?|status epilepticus"
)
QUALIFIED_SEIZURE_TERMS = rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS})"


def apply_cluster_rules(
    specs: Sequence[RuleSpec],
    text: str,
    ablation_config: AblationConfig,
    helpers: dict[str, object] | None = None,
) -> list[RawCandidate]:
    context = ExtractionContext(text=text, helpers=helpers)
    candidates: list[RawCandidate] = []
    for spec in specs:
        candidates.extend(
            candidate
            for candidate in spec.apply(context, ablation_config)
            if isinstance(candidate, RawCandidate)
        )
    return candidates


def _build_cluster_candidate(
    match: re.Match[str],
    *,
    rule_id: str,
    label: str,
    evidence_group: str | int = 0,
) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.CLUSTER_FREQUENCY,
        label=label,
        evidence=_clean_evidence(match.group(evidence_group)),
        rule_id=rule_id,
        rule_group=RuleGroup.CLUSTER_ARITHMETIC,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _build_adjective_cluster_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    period = _adjective_cluster_period(match.group("period"))
    return _build_cluster_candidate(
        match,
        rule_id="cluster.adjective_rate",
        label=f"1 cluster per {period}, multiple per cluster",
    )


def _build_shorthand_cluster_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    evidence = re.sub(r"^ongoing\s+", "", match.group(0), flags=re.IGNORECASE)
    return RawCandidate(
        kind=CandidateKind.CLUSTER_FREQUENCY,
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_expanded_compact_unit(match.group('unit'))}, multiple per cluster"
        ),
        evidence=_clean_evidence(evidence),
        rule_id="cluster.compact_count_per_period",
        rule_group=RuleGroup.CLUSTER_ARITHMETIC,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _build_this_period_cluster_count(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.count_this_period",
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_cluster_period_label(match.group('period'))}, multiple per cluster"
        ),
    )


def _build_this_period_vague_size(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.count_this_period_vague_size",
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_cluster_period_label(match.group('period'))}, multiple per cluster"
        ),
    )


def _build_last_month_cluster_count(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.last_month_count",
        label=(
            f"{_number_token(match.group('count'))} cluster per month, "
            "multiple per cluster"
        ),
    )


def _build_cluster_rate_with_size(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    count = _number_token(match.group("count"))
    period = _singular_unit(match.group("period"))
    per_cluster = _number_token(match.group("per_cluster"))
    return _build_cluster_candidate(
        match,
        rule_id="cluster.rate_with_size",
        label=f"{count} cluster per {period}, {per_cluster} per cluster",
    )


def _build_monthly_cluster_rate_with_size(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.monthly_rate_with_size",
        label=(
            "1 cluster per month, "
            f"{_number_token(match.group('per_cluster'))} per cluster"
        ),
    )


def _build_unknown_cluster_size(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    per_cluster = _number_token(match.group("per_cluster"))
    return RawCandidate(
        kind=CandidateKind.UNKNOWN_FREQUENCY,
        label=f"unknown, {per_cluster} per cluster",
        evidence=_clean_evidence(match.group(0)),
        rule_id="cluster.unknown_frequency_with_size",
        rule_group=RuleGroup.CLUSTER_ARITHMETIC,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _build_this_period_cluster_with_size(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.count_this_period_with_size",
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_singular_unit(match.group('period'))}, "
            f"{_number_token(match.group('per_cluster'))} per cluster"
        ),
    )


def _build_clusters_each_comprising(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    count = match.group("prefix_count") or match.group("count")
    denominator = match.group("prefix_denominator") or match.group("denominator")
    unit = match.group("prefix_unit") or match.group("unit")
    return _build_cluster_candidate(
        match,
        rule_id="cluster.each_comprising",
        label=(
            f"{_number_token(count)} cluster per {_period_label(unit, denominator)}, "
            f"{_number_token(match.group('per_cluster'))} per cluster"
        ),
    )


def _build_cluster_over_period(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.count_over_period",
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_period_label(match.group('unit'), match.group('denominator'))}, "
            "multiple per cluster"
        ),
    )


def _build_seizure_free_cycle_cluster(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.seizure_free_cycle",
        label=(
            f"1 cluster per "
            f"{_period_label(match.group('unit'), match.group('denominator'))}, "
            f"{_cluster_size_token(match.group('raw_per_cluster'))} per cluster"
        ),
    )


def _build_last_convulsive_cluster_persistence(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate | None:
    clinic_date_func = cast(Callable[[str], object], context.helper("clinic_date"))
    relative_note_date = cast(
        Callable[[str, object], object | None], context.helper("relative_note_date")
    )
    month_span = cast(
        Callable[[object | None, object | None], int | None],
        context.helper("month_span"),
    )
    clinic_date = clinic_date_func(context.text)
    start_date = relative_note_date(match.group("start_date"), clinic_date)
    denominator = month_span(start_date, clinic_date)
    if denominator is None:
        return None
    return _build_cluster_candidate(
        match,
        rule_id="cluster.last_convulsive_persistence",
        label=f"multiple cluster per {denominator} month, multiple per cluster",
        evidence_group="evidence",
    )


def _build_nearly_interval_cluster(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.nearly_interval",
        label=(
            f"1 cluster per "
            f"{_period_label(match.group('unit'), match.group('denominator'))}, "
            f"{_number_token(match.group('low'))} to "
            f"{_number_token(match.group('high'))} per cluster"
        ),
        evidence_group="evidence",
    )


def _build_interval_day_cluster(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.seizure_free_interval_day",
        label=(
            f"1 cluster per "
            f"{_period_label(match.group('unit'), match.group('denominator'))}, "
            f"{_cluster_size_token(match.group('count'))} per cluster"
        ),
        evidence_group="evidence",
    )


def _build_batch_within_24h(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.batch_within_24h",
        label=(
            f"1 cluster per "
            f"{_period_label(match.group('unit'), match.group('denominator'))}, "
            f"{_cluster_size_token(match.group('count'))} per cluster"
        ),
        evidence_group="evidence",
    )


def _build_run_with_separate_days(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.run_with_separate_days",
        label=(
            f"1 cluster per {_period_unit_label(match.group('period'))}, "
            f"{_number_token(match.group('per_cluster'))} per cluster"
        ),
    )


def _build_vague_days_over_period(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.vague_days_over_period",
        label=(
            f"{_number_token(match.group('days'))} cluster per "
            f"{_period_unit_label(match.group('period'))}, multiple per cluster"
        ),
    )


def _build_broad_this_period_cluster_with_size(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.broad_count_this_period_with_size",
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_cluster_period_label(match.group('period'))}, "
            f"{_cluster_size_token(match.group('raw_per_cluster'))} per cluster"
        ),
    )


def _build_period_with_per_cluster(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.period_with_per_cluster",
        label=(
            f"1 cluster per {_cluster_period_label(match.group('period'))}, "
            f"{_cluster_size_token(match.group('raw_per_cluster'))} per cluster"
        ),
    )


def _build_descriptor_cluster_size(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.descriptor_size",
        label=(
            f"1 cluster per {_cluster_period_label(match.group('period'))}, "
            f"{_cluster_size_token(match.group('raw_per_cluster'))} per cluster"
        ),
    )


def _build_cluster_timing(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate:
    surrounding = context.text[max(0, match.start() - 260) : match.end() + 260]
    return _build_cluster_candidate(
        match,
        rule_id="cluster.timing_days",
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_cluster_period_label(match.group('period'))}, "
            f"{_infer_cluster_size(surrounding)} per cluster"
        ),
    )


def _build_cluster_days_simple(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.days_this_period",
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_singular_unit(match.group('period'))}, multiple per cluster"
        ),
    )


def _build_cluster_seizure_days_per_period(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.seizure_days_per_period",
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_singular_unit(match.group('period'))}, multiple per cluster"
        ),
        evidence_group="evidence",
    )


def _build_short_burst_cluster(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.short_burst_monthly",
        label="1 cluster per month, multiple per cluster",
    )


def _build_cluster_count_with_implied_size(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate | None:
    per_cluster_context = re.compile(
        rf"(?:\beach\s+)?~?\s*(?P<raw_per_cluster>{NUMBER_TOKEN}(?:\s*[-–—]\s*{NUMBER_TOKEN})?\s*)\s+"
        rf"(?:{SEIZURE_TERMS}|events?|episodes?|spells?)",
        re.IGNORECASE,
    )
    per_cluster_match = per_cluster_context.search(match.group("rest"))
    if per_cluster_match is None:
        return None
    return _build_cluster_candidate(
        match,
        rule_id="cluster.count_with_implied_size",
        label=(
            f"{_number_token(match.group('count'))} cluster per "
            f"{_cluster_period_label(match.group('period'))}, "
            f"{_cluster_size_token(per_cluster_match.group('raw_per_cluster'))} per cluster"
        ),
    )


def _build_size_without_count(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_cluster_candidate(
        match,
        rule_id="cluster.size_without_count",
        label=(
            f"1 cluster per {_cluster_period_label(match.group('period'))}, "
            f"{_cluster_size_token(match.group('raw_per_cluster'))} per cluster"
        ),
    )


ADJECTIVE_CLUSTER_RATE_RULE = RuleSpec(
    rule_id="cluster.adjective_rate",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Adjective cluster rate such as weekly morning clusters reported.",
    pattern=re.compile(
        rf"\b(?P<period>daily|weekly|monthly|yearly)\s+"
        rf"(?:{WORD_TOKEN}\s+){{0,3}}clusters?\s+reported\b",
        re.IGNORECASE,
    ),
    build=_build_adjective_cluster_rate,
    examples=(
        RuleExample(
            text="Weekly morning clusters reported; number per cluster not documented.",
            expected_label="1 cluster per week, multiple per cluster",
            expected_evidence="Weekly morning clusters reported",
        ),
    ),
    provenance="Portable V1 cluster-rate expression.",
)

SHORTHAND_CLUSTER_RATE_RULE = RuleSpec(
    rule_id="cluster.compact_count_per_period",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Compact cluster count per period such as clusters 3x/month.",
    pattern=re.compile(
        r"\b(?:(?:ongoing|nocturnal|morning|evening|monthly|weekly|daily)\s+){0,3}"
        r"clusters?\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s*(?:x|×|/)\s*/?\s*"
        r"(?P<unit>d|day|wk|week|mo|month|yr|year)\b",
        re.IGNORECASE,
    ),
    build=_build_shorthand_cluster_rate,
    examples=(
        RuleExample(
            text="Diagnosis: ongoing nocturnal clusters 3x/month.",
            expected_label="3 cluster per month, multiple per cluster",
            expected_evidence="nocturnal clusters 3x/month",
        ),
    ),
    provenance="Portable V1 cluster-rate expression.",
)

CLUSTER_COUNT_THIS_PERIOD_VAGUE_SIZE_RULE = RuleSpec(
    rule_id="cluster.count_this_period_vague_size",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Cluster count this period with vague cluster size.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+clusters?\s+this\s+"
        rf"(?P<period>week|month|quarter|year),?\s+each\s+lasting\s+"
        rf".{{0,40}}?\bseveral\s+(?:brief\s+)?(?:events?|episodes?|seizures?)\b",
        re.IGNORECASE,
    ),
    build=_build_this_period_vague_size,
    examples=(
        RuleExample(
            text=(
                "He describes three clusters this quarter, each lasting 1-2 days "
                "with several brief episodes."
            ),
            expected_label="3 cluster per 3 month, multiple per cluster",
            expected_evidence=(
                "three clusters this quarter, each lasting 1-2 days with "
                "several brief episodes"
            ),
        ),
    ),
    provenance="Portable V1 cluster-count expression.",
)

CLUSTER_COUNT_THIS_PERIOD_RULE = RuleSpec(
    rule_id="cluster.count_this_period",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Cluster count this week/month/quarter/year with unknown size.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+clusters?\s+this\s+"
        rf"(?P<period>week|month|quarter|year)\b",
        re.IGNORECASE,
    ),
    build=_build_this_period_cluster_count,
    examples=(
        RuleExample(
            text="Patient reports two clusters this quarter.",
            expected_label="2 cluster per 3 month, multiple per cluster",
            expected_evidence="two clusters this quarter",
        ),
    ),
    provenance="Portable V1 cluster-count expression.",
)

LAST_MONTH_CLUSTER_COUNT_RULE = RuleSpec(
    rule_id="cluster.last_month_count",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Last-month cluster count with optional approximation marker.",
    pattern=re.compile(
        rf"\blast\s+month\s*(?:≈|~|about|around|approximately)?\s*"
        rf"(?P<count>{NUMBER_TOKEN})\s+clusters?\b",
        re.IGNORECASE,
    ),
    build=_build_last_month_cluster_count,
    examples=(
        RuleExample(
            text="Cluster frequency unclear this month; last month ≈three clusters.",
            expected_label="3 cluster per month, multiple per cluster",
            expected_evidence="last month ≈three clusters",
        ),
    ),
    provenance="Portable V1 cluster-count expression.",
)

CLUSTER_RATE_WITH_SIZE_RULE = RuleSpec(
    rule_id="cluster.rate_with_size",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Cluster count per period with explicit events per cluster.",
    pattern=re.compile(
        rf"\bcluster(?: days?|s)?\s+(?P<count>{NUMBER_TOKEN})\s+(?:this|per)\s+"
        rf"(?P<period>{UNIT_TOKEN}).{{0,80}}?(?:typically|usually|each|with)?\s*"
        rf"(?P<per_cluster>{NUMBER_TOKEN})\s+(?:{SEIZURE_TERMS})?\s*"
        r"(?:in\s+24\s+h|per cluster)?",
        re.IGNORECASE,
    ),
    build=_build_cluster_rate_with_size,
    examples=(
        RuleExample(
            text="Cluster days 2 this month, typically five events in 24 h.",
            expected_label="2 cluster per month, 5 per cluster",
            expected_evidence="Cluster days 2 this month, typically five events in 24 h",
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

MONTHLY_CLUSTER_RATE_WITH_SIZE_RULE = RuleSpec(
    rule_id="cluster.monthly_rate_with_size",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Monthly clusters with explicit events over 24 hours.",
    pattern=re.compile(
        rf"\bMonthly\s+clusters?,?\s+(?:typically|usually|each|with)?\s*"
        rf"(?P<per_cluster>{NUMBER_TOKEN})\s+(?:{SEIZURE_TERMS})\s+over\s+24\s+h\b",
        re.IGNORECASE,
    ),
    build=_build_monthly_cluster_rate_with_size,
    examples=(
        RuleExample(
            text="Monthly clusters, typically 6 to 7 seizures over 24 h.",
            expected_label="1 cluster per month, 6 to 7 per cluster",
            expected_evidence="Monthly clusters, typically 6 to 7 seizures over 24 h",
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

UNKNOWN_CLUSTER_SIZE_RULE = RuleSpec(
    rule_id="cluster.unknown_frequency_with_size",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Known events per cluster with unclear cluster frequency.",
    pattern=re.compile(
        rf"\bclusters? characterized by (?P<per_cluster>{NUMBER_TOKEN})\s+.*?"
        rf"(?:frequency unclear|cannot specify how often|unclear frequency)",
        re.IGNORECASE,
    ),
    build=_build_unknown_cluster_size,
    examples=(
        RuleExample(
            text="Clusters characterized by five spells, but frequency unclear.",
            expected_label="unknown, 5 per cluster",
            expected_evidence="Clusters characterized by five spells, but frequency unclear",
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE = RuleSpec(
    rule_id="cluster.count_this_period_with_size",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="This-week/month cluster count with explicit events per cluster.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+clusters?\s+this\s+"
        rf"(?P<period>month|week);?\s+each\s+"
        rf"(?:approx|≈|about|around)?\s*(?P<per_cluster>{NUMBER_TOKEN})\s+"
        rf"(?:{SEIZURE_TERMS})\b",
        re.IGNORECASE,
    ),
    build=_build_this_period_cluster_with_size,
    examples=(
        RuleExample(
            text="Two clusters this month; each approx six absences.",
            expected_label="2 cluster per month, 6 per cluster",
            expected_evidence="Two clusters this month; each approx six absences",
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

CLUSTERS_EACH_COMPRISING_RULE = RuleSpec(
    rule_id="cluster.each_comprising",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Cluster count over a recent window with each-comprising size.",
    pattern=re.compile(
        rf"\b(?:(?P<prefix>Over the past|Over the last|During the past|During the last)\s+"
        rf"(?P<prefix_denominator>{NUMBER_TOKEN})\s+(?P<prefix_unit>{UNIT_TOKEN})\s+"
        rf".{{0,80}}?\b(?P<prefix_count>{NUMBER_TOKEN})\s+clusters?|"
        rf"(?P<count>{NUMBER_TOKEN})\s+clusters?\s+"
        rf"(?:over|in|during)\s+(?:the\s+)?(?:past|last)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN}))"
        rf".{{0,120}}?\beach\s+comprising\s+"
        rf"(?P<per_cluster>{NUMBER_TOKEN})\s+(?:brief\s+)?"
        rf"(?:{WORD_TOKEN}\s+){{0,3}}(?:{SEIZURE_TERMS})\b",
        re.IGNORECASE,
    ),
    build=_build_clusters_each_comprising,
    examples=(
        RuleExample(
            text=(
                "Over the past six weeks he has experienced three clusters, "
                "each comprising two to four brief events."
            ),
            expected_label="3 cluster per 6 week, 2 to 4 per cluster",
            expected_evidence=(
                "Over the past six weeks he has experienced three clusters, "
                "each comprising two to four brief events"
            ),
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

CLUSTER_OVER_PERIOD_RULE = RuleSpec(
    rule_id="cluster.count_over_period",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Cluster count over a recent window with unspecified cluster size.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{WORD_TOKEN}\s+){{0,3}}clusters?\s+"
        rf"over\s+(?:the\s+)?(?:past|last)\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    ),
    build=_build_cluster_over_period,
    examples=(
        RuleExample(
            text="Two myoclonic clusters over the past three weeks.",
            expected_label="2 cluster per 3 week, multiple per cluster",
            expected_evidence="Two myoclonic clusters over the past three weeks",
        ),
    ),
    provenance="Portable V1 cluster-count expression.",
)

SEIZURE_FREE_CYCLE_CLUSTER_RULE = RuleSpec(
    rule_id="cluster.seizure_free_cycle",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure-free cycle followed by same-day cluster size.",
    pattern=re.compile(
        rf"\bseizure[- ]free\s+for\s+up\s+to\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>months?|years?)"
        rf".{{0,80}}?\bclusters?\s+of\s+"
        rf"(?P<raw_per_cluster>{NUMBER_TOKEN})\s+"
        rf"(?:{SEIZURE_TERMS}|events?|episodes?|spells?)\s+in\s+a\s+single\s+day\b",
        re.IGNORECASE,
    ),
    build=_build_seizure_free_cycle_cluster,
    examples=(
        RuleExample(
            text=(
                "Seizure-free for up to two months then clusters of four seizures "
                "in a single day."
            ),
            expected_label="1 cluster per 2 month, 4 per cluster",
            expected_evidence=(
                "Seizure-free for up to two months then clusters of four seizures "
                "in a single day"
            ),
        ),
    ),
    provenance="Portable V1 cluster-cycle expression.",
)

LAST_CONVULSIVE_CLUSTER_PERSISTENCE_RULE = RuleSpec(
    rule_id="cluster.last_convulsive_persistence",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Last convulsive seizure date with persisting myoclonic clusters.",
    pattern=re.compile(
        rf"\b(?P<evidence>(?:Her|His|The)\s+last\s+convulsive\s+seizure\s+"
        rf"was\s+recorded\s+in\s+(?P<start_date>{MONTH_YEAR_DATE_PATTERN}),?\s+"
        rf"with\s+occasional\s+clusters?\s+of\s+myoclonic\s+jerks\s+persisting)\b",
        re.IGNORECASE,
    ),
    build=_build_last_convulsive_cluster_persistence,
    examples=(
        RuleExample(
            text=(
                "Clinic Date: 01 June 2023. His last convulsive seizure was recorded "
                "in 03/2022, with occasional clusters of myoclonic jerks persisting."
            ),
            expected_label="multiple cluster per 15 month, multiple per cluster",
            expected_evidence="occasional clusters of myoclonic jerks persisting",
        ),
    ),
    provenance="Portable V1 date-span cluster expression.",
)

NEARLY_INTERVAL_CLUSTER_RULE = RuleSpec(
    rule_id="cluster.nearly_interval",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Nearly interval without seizures followed by one-day recurrence cluster.",
    pattern=re.compile(
        rf"\b(?P<evidence>go\s+(?:nearly\s+)?(?P<denominator>{NUMBER_TOKEN})\s+"
        rf"(?P<unit>days?|weeks?)\s+without\s+(?:{SEIZURE_TERMS}),?\s+"
        rf"but\s+when\s+they\s+recur\s+[^.]*?\bin\s+one\s+day,?\s+"
        rf"often\s+between\s+(?P<low>{NUMBER_VALUE_TOKEN})\s+and\s+"
        rf"(?P<high>{NUMBER_VALUE_TOKEN}))\b",
        re.IGNORECASE,
    ),
    build=_build_nearly_interval_cluster,
    examples=(
        RuleExample(
            text=(
                "They go nearly two weeks without seizures, but when they recur "
                "in one day, often between 4 and 6."
            ),
            expected_label="1 cluster per 2 week, 4 to 6 per cluster",
            expected_evidence=(
                "go nearly two weeks without seizures, but when they recur "
                "in one day, often between 4 and 6"
            ),
        ),
    ),
    provenance="Portable V1 cluster-cycle expression.",
)

SEIZURE_FREE_INTERVAL_DAY_CLUSTER_RULE = RuleSpec(
    rule_id="cluster.seizure_free_interval_day",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure-free interval followed by a day with multiple events.",
    pattern=re.compile(
        rf"\b(?P<evidence>seizure[- ]free\s+for\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+consecutive\s+(?P<unit>days?|weeks?),?\s+"
        rf"followed\s+by\s+a\s+day\s+with\s+multiple\s+events,?\s+"
        rf"typically\s+(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS}))\b",
        re.IGNORECASE,
    ),
    build=_build_interval_day_cluster,
    examples=(
        RuleExample(
            text=(
                "Seizure-free for three consecutive days, followed by a day with "
                "multiple events, typically four brief seizures."
            ),
            expected_label="1 cluster per 3 day, 4 per cluster",
            expected_evidence=(
                "Seizure-free for three consecutive days, followed by a day with "
                "multiple events, typically four brief seizures"
            ),
        ),
    ),
    provenance="Portable V1 cluster-cycle expression.",
)

BATCH_WITHIN_24H_RULE = RuleSpec(
    rule_id="cluster.batch_within_24h",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Interval without seizures followed by batches within 24 hours.",
    pattern=re.compile(
        rf"\b(?P<evidence>go\s+(?P<denominator>{NUMBER_TOKEN})\s+"
        rf"(?P<unit>days?|weeks?)\s+without\s+(?:{SEIZURE_TERMS}),?\s+"
        rf"but\s+when\s+they\s+happen\s+[^.]*?\bin\s+batches,?\s+"
        rf"with\s+(?P<count>{NUMBER_TOKEN})\s+occurring\s+within\s+24\s+hours)\b",
        re.IGNORECASE,
    ),
    build=_build_batch_within_24h,
    examples=(
        RuleExample(
            text=(
                "They go four days without seizures, but when they happen they "
                "come in batches, with two occurring within 24 hours."
            ),
            expected_label="1 cluster per 4 day, 2 per cluster",
            expected_evidence=(
                "go four days without seizures, but when they happen they come "
                "in batches, with two occurring within 24 hours"
            ),
        ),
    ),
    provenance="Portable V1 cluster-cycle expression.",
)

RUN_WITH_SEPARATE_DAYS_RULE = RuleSpec(
    rule_id="cluster.run_with_separate_days",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Run or cluster over a recent window with separate-day event count.",
    pattern=re.compile(
        rf"\bover\s+the\s+past\s+(?P<period>fortnight|month|week),?\s+"
        rf".{{0,80}}?\b(?:cluster|run)\b.{{0,80}}?\bwith\s+"
        rf"(?P<per_cluster>{NUMBER_TOKEN})\s+(?:short\s+)?(?:{SEIZURE_TERMS})\s+"
        r"occurring on separate days\b",
        re.IGNORECASE,
    ),
    build=_build_run_with_separate_days,
    examples=(
        RuleExample(
            text=(
                "Over the past fortnight she describes a run of brief events, "
                "with three short episodes occurring on separate days."
            ),
            expected_label="1 cluster per 2 week, 3 per cluster",
            expected_evidence=(
                "Over the past fortnight she describes a run of brief events, "
                "with three short episodes occurring on separate days"
            ),
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

VAGUE_CLUSTER_DAYS_RULE = RuleSpec(
    rule_id="cluster.vague_days_over_period",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Cluster over a recent window occurring on multiple or several days.",
    pattern=re.compile(
        r"\bover\s+the\s+past\s+(?P<period>month|week|fortnight),?\s+"
        r".{0,80}?\bcluster\b.{0,80}?\bon\s+(?P<days>multiple|several)\s+days\b",
        re.IGNORECASE,
    ),
    build=_build_vague_days_over_period,
    examples=(
        RuleExample(
            text=(
                "Over the past month, the patient reports a cluster of short events "
                "on multiple days."
            ),
            expected_label="multiple cluster per month, multiple per cluster",
            expected_evidence=(
                "Over the past month, the patient reports a cluster of short events "
                "on multiple days"
            ),
        ),
    ),
    provenance="Portable V1 cluster-day expression.",
)

BROAD_CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE = RuleSpec(
    rule_id="cluster.broad_count_this_period_with_size",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="This-period cluster count with intervening descriptors and explicit size.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+clusters?\s+this\s+"
        rf"(?P<period>week|month|quarter|year)[,;]?\s*.*?\beach\b.*?"
        rf"(?:approx|about|around|roughly|~|≈)?\s*"
        rf"(?P<raw_per_cluster>{NUMBER_TOKEN})(?:\s*or\s+more)?\s+"
        rf"(?:{SEIZURE_TERMS})\b",
        re.IGNORECASE,
    ),
    build=_build_broad_this_period_cluster_with_size,
    examples=(
        RuleExample(
            text="There have been three clusters this month; each ~4 - 5 events.",
            expected_label="3 cluster per month, 4 to 5 per cluster",
            expected_evidence="three clusters this month; each ~4 - 5 events",
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

CLUSTER_PERIOD_WITH_PER_CLUSTER_RULE = RuleSpec(
    rule_id="cluster.period_with_per_cluster",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Periodic cluster statement with explicit per-cluster size.",
    pattern=re.compile(
        rf"\b(?P<period>daily|weekly|monthly|yearly|quarter)\b[^.;]{{0,80}}?\b"
        rf"(?P<raw_per_cluster>{NUMBER_TOKEN})(?:\s*or\s+more)?\s+per\s+cluster\b",
        re.IGNORECASE,
    ),
    build=_build_period_with_per_cluster,
    examples=(
        RuleExample(
            text="Cluster burden increased; now weekly, five per cluster.",
            expected_label="1 cluster per week, 5 per cluster",
            expected_evidence="weekly, five per cluster",
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

DESCRIPTOR_CLUSTER_SIZE_RULE = RuleSpec(
    rule_id="cluster.descriptor_size",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Adjective cluster period with usually/typically size descriptor.",
    pattern=re.compile(
        rf"\b(?P<period>daily|weekly|monthly|yearly)\s+clusters?,\s*"
        rf"(?:usually|typically)\s+(?P<raw_per_cluster>{NUMBER_TOKEN})"
        rf"(?:\s*or\s+more)?\s+(?:{SEIZURE_TERMS}|events?|episodes?|spells?)\b",
        re.IGNORECASE,
    ),
    build=_build_descriptor_cluster_size,
    examples=(
        RuleExample(
            text="Previously, the seizure frequency was weekly clusters, usually three events.",
            expected_label="1 cluster per week, 3 per cluster",
            expected_evidence="weekly clusters, usually three events",
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

CLUSTER_TIMING_RULE = RuleSpec(
    rule_id="cluster.timing_days",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Clusters on several/count mornings, evenings, nights, or afternoons per period.",
    pattern=re.compile(
        rf"\b(?:(?:on|occurring)\s+)(?P<count>{NUMBER_TOKEN}|several|multiple)\s+"
        rf"(?P<time>(?:morning|mornings|evening|evenings|night|nights|afternoon|afternoons))\s+"
        rf"(?:each|per)\s+(?P<period>week|month|fortnight)\b",
        re.IGNORECASE,
    ),
    build=_build_cluster_timing,
    examples=(
        RuleExample(
            text=(
                "Clusters on several mornings each week, sometimes repeating two or "
                "three times within the same morning."
            ),
            expected_label="multiple cluster per week, 2 to 3 per cluster",
            expected_evidence="on several mornings each week",
        ),
    ),
    provenance="Portable V1 cluster-timing expression.",
)

CLUSTER_DAYS_SIMPLE_RULE = RuleSpec(
    rule_id="cluster.days_this_period",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Cluster days this month/week with unspecified events per cluster.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+cluster\s+days?\s+this\s+"
        rf"(?P<period>month|week);?\b",
        re.IGNORECASE,
    ),
    build=_build_cluster_days_simple,
    examples=(
        RuleExample(
            text="Two cluster days this month.",
            expected_label="2 cluster per month, multiple per cluster",
            expected_evidence="Two cluster days this month",
        ),
    ),
    provenance="Portable V1 cluster-day expression.",
)

CLUSTER_SEIZURE_DAYS_PER_PERIOD_RULE = RuleSpec(
    rule_id="cluster.seizure_days_per_period",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Clusters of seizures on N days each week/month.",
    pattern=re.compile(
        rf"\b(?P<evidence>clusters?\s+of\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+on\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+days?\s+each\s+(?P<period>week|month))\b",
        re.IGNORECASE,
    ),
    build=_build_cluster_seizure_days_per_period,
    examples=(
        RuleExample(
            text="He suffers clusters of absence seizures on four to five days each week.",
            expected_label="4 to 5 cluster per week, multiple per cluster",
            expected_evidence="clusters of absence seizures on four to five days each week",
        ),
    ),
    provenance="Portable V1 cluster-day expression.",
)

SHORT_BURST_CLUSTER_RULE = RuleSpec(
    rule_id="cluster.short_burst_monthly",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Short bursts around the beginning of most months.",
    pattern=re.compile(
        r"\b(?P<evidence>short\s+bursts?\s+around\s+the\s+beginning\s+of\s+most\s+months)\b",
        re.IGNORECASE,
    ),
    build=_build_short_burst_cluster,
    examples=(
        RuleExample(
            text="Short bursts around the beginning of most months.",
            expected_label="1 cluster per month, multiple per cluster",
            expected_evidence="Short bursts around the beginning of most months",
        ),
    ),
    provenance="Portable V1 cluster-timing expression.",
)

CLUSTER_COUNT_WITH_IMPLIED_SIZE_RULE = RuleSpec(
    rule_id="cluster.count_with_implied_size",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="This-period cluster count whose trailing context implies cluster size.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})(?:\s+[\w-]+){{0,3}}?\s+clusters?\s+this\s+"
        rf"(?P<period>month|week|fortnight)\b(?P<rest>[^.]{{0,200}})",
        re.IGNORECASE,
    ),
    build=_build_cluster_count_with_implied_size,
    examples=(
        RuleExample(
            text="She reports 1 Travel-related clusters this month; ~4 - 6 events per episode.",
            expected_label="1 cluster per month, 4 to 6 per cluster",
            expected_evidence="1 Travel-related clusters this month; ~4 - 6 events per episode",
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

CLUSTER_SIZE_WITHOUT_COUNT_RULE = RuleSpec(
    rule_id="cluster.size_without_count",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Period with per-cluster size but no explicit cluster count.",
    pattern=re.compile(
        rf"\b(?P<period>daily|weekly|monthly|yearly|fortnightly|fortnight)\b"
        rf"[\s,;-]{{0,40}}?\s*\b(?:about|around|approximately|roughly|~)?\s*"
        rf"(?P<raw_per_cluster>{NUMBER_TOKEN})(?:\s*or\s+more)?\s+"
        rf"per\s+(?:{SEIZURE_TERMS}|events?|episodes?|spells?)?\s*cluster\b",
        re.IGNORECASE,
    ),
    build=_build_size_without_count,
    examples=(
        RuleExample(
            text="Current pattern is fortnightly, about five per event cluster.",
            expected_label="1 cluster per 2 week, 5 per cluster",
            expected_evidence="fortnightly, about five per event cluster",
        ),
    ),
    provenance="Portable V1 cluster-size expression.",
)

CLUSTER_RULES = (
    SEIZURE_FREE_CYCLE_CLUSTER_RULE,
    LAST_CONVULSIVE_CLUSTER_PERSISTENCE_RULE,
    NEARLY_INTERVAL_CLUSTER_RULE,
    SEIZURE_FREE_INTERVAL_DAY_CLUSTER_RULE,
    BATCH_WITHIN_24H_RULE,
    ADJECTIVE_CLUSTER_RATE_RULE,
    SHORTHAND_CLUSTER_RATE_RULE,
    CLUSTER_COUNT_THIS_PERIOD_VAGUE_SIZE_RULE,
    CLUSTER_COUNT_THIS_PERIOD_RULE,
    LAST_MONTH_CLUSTER_COUNT_RULE,
    CLUSTER_RATE_WITH_SIZE_RULE,
    MONTHLY_CLUSTER_RATE_WITH_SIZE_RULE,
    UNKNOWN_CLUSTER_SIZE_RULE,
    CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE,
    CLUSTERS_EACH_COMPRISING_RULE,
    CLUSTER_OVER_PERIOD_RULE,
    RUN_WITH_SEPARATE_DAYS_RULE,
    VAGUE_CLUSTER_DAYS_RULE,
    BROAD_CLUSTER_COUNT_THIS_PERIOD_WITH_SIZE_RULE,
    CLUSTER_PERIOD_WITH_PER_CLUSTER_RULE,
    DESCRIPTOR_CLUSTER_SIZE_RULE,
    CLUSTER_TIMING_RULE,
    CLUSTER_DAYS_SIMPLE_RULE,
    CLUSTER_SEIZURE_DAYS_PER_PERIOD_RULE,
    SHORT_BURST_CLUSTER_RULE,
    CLUSTER_COUNT_WITH_IMPLIED_SIZE_RULE,
    CLUSTER_SIZE_WITHOUT_COUNT_RULE,
)


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


def _cluster_period_label(unit: str) -> str:
    unit_value = _singular_unit(unit)
    if unit_value in {"daily", "weekly", "monthly", "yearly", "fortnightly"}:
        return unit_value[:-2] if unit_value.endswith("ly") else unit_value
    if unit_value == "fortnight":
        return "2 week"
    if unit_value == "quarter":
        return "3 month"
    return unit_value


def _adjective_cluster_period(value: str) -> str:
    return {
        "daily": "day",
        "weekly": "week",
        "monthly": "month",
        "yearly": "year",
    }[value.lower()]


def _period_label(unit: str, denominator: str | None = None) -> str:
    denominator_value = _number_token(denominator) if denominator else None
    unit_value = _singular_unit(unit)
    if denominator_value in {None, "1"}:
        return unit_value
    return f"{denominator_value} {unit_value}"


def _period_unit_label(value: str) -> str:
    normalized = value.lower().strip()
    if normalized == "fortnight":
        return "2 week"
    return _singular_unit(normalized)


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
            rf"\beach\s+(?:approximately|about|around|roughly|\~|≈)?\s*"
            rf"(?P<count>{NUMBER_TOKEN})(?:\s*to\s*{NUMBER_TOKEN})?\s+"
            rf"(?:{SEIZURE_TERMS}|events?|episodes?|spells?)",
            re.IGNORECASE,
        ),
        re.compile(
            rf"\b(?:usually|typically)\s+(?:approximately|about|around|roughly|\~|≈)?\s*"
            rf"(?P<count>{NUMBER_TOKEN})(?:\s*or\s+more)?\s+"
            rf"(?:{SEIZURE_TERMS}|events?|episodes?|spells?)",
            re.IGNORECASE,
        ),
        re.compile(
            rf"\beach\s+cluster\s+(?:involves|comprising|comprised of)\s+"
            rf"(?:approximately|about|around|roughly|\~|≈)?\s*"
            rf"(?P<count>{NUMBER_TOKEN})(?:\s*to\s*{NUMBER_TOKEN})?\s+"
            rf"(?:{WORD_TOKEN}\s+){{0,2}}(?:{SEIZURE_TERMS}|events?|episodes?|spells?)",
            re.IGNORECASE,
        ),
        re.compile(
            rf"\b(?:approximately|about|around|roughly|\~|≈)?\s*"
            rf"(?P<count>{NUMBER_TOKEN})(?:\s*or\s+more)?\s+"
            r"per\s*(?:cluster|episode)\b",
            re.IGNORECASE,
        ),
        re.compile(
            rf"(?P<count>{NUMBER_TOKEN})\s+(?:{SEIZURE_TERMS}|events?|episodes?|spells?)\s+"
            r"per\s+(?:cluster|episode)\b",
            re.IGNORECASE,
        ),
        re.compile(rf"(?P<count>{NUMBER_TOKEN})\s+times\b", re.IGNORECASE),
    ]
    for pattern in patterns:
        match = pattern.search(text)
        if match is not None:
            return _cluster_size_token(match.group("count"))
    return "multiple"


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


def _singular_unit(value: str) -> str:
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")
