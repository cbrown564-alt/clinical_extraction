from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.find_encode import (
    FindFact,
    encode_find_fact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

from ..deterministic_frequency_tokens import (
    ADJECTIVE_PERIOD_TOKEN,
    NUMBER_TOKEN,
    UNIT_TOKEN,
)
from ..deterministic_rate_distractors import (
    is_medication_or_dose_rate_distractor as _is_medication_or_dose_rate_distractor_impl,
)
from ..deterministic_rate_terms import (
    QUALIFIED_SEIZURE_TERMS,
    SEIZURE_DESCRIPTOR_PHRASE,
    SEIZURE_RATE_PHRASE,
    SEIZURE_TERMS,
    WORD_TOKEN,
)


def apply_rate_rules(
    specs: Sequence[RuleSpec],
    text: str,
    ablation_config: AblationConfig,
) -> list[RawCandidate]:
    context = ExtractionContext(text=text)
    candidates: list[RawCandidate] = []
    for spec in specs:
        candidates.extend(
            candidate
            for candidate in spec.apply(context, ablation_config)
            if isinstance(candidate, RawCandidate)
        )
    return candidates


def _build_rate_candidate(
    match: re.Match[str],
    *,
    rule_id: str,
    count: str,
    unit: str,
    denominator: str | None = None,
    evidence_group: str | int = "evidence",
) -> RawCandidate:
    fact = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count=count,
        unit=unit,
        denominator=denominator,
    )
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label=encode_find_fact(fact),
        evidence=_clean_evidence(match.group(evidence_group)),
        rule_id=rule_id,
        rule_group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
        find_fact=fact,
    )


def _build_daily_basis_current(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.daily_basis_current",
        count="1",
        unit="day",
    )


def _build_days_of_week_rate(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.days_of_week",
        count=match.group("count"),
        unit="week",
    )


def _build_nights_per_period(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.nights_per_period",
        count=match.group("count"),
        unit=match.group("unit"),
    )


def _build_descriptor_rate(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.descriptor_count_per_period",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.groupdict().get("denominator"),
        evidence_group=0,
    )


def _build_qualified_direct_rate(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.qualified_direct_count_per_period",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.groupdict().get("denominator"),
        evidence_group=0,
    )


def _build_quarter_direct_rate(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.quarter_direct_count_per_period",
        count=match.group("count"),
        unit=match.group("unit"),
        evidence_group=0,
    )


def _build_implicit_interval(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.implicit_every_n_interval",
        count="1",
        unit=match.group("unit"),
        denominator=match.groupdict().get("denominator"),
        evidence_group=0,
    )


def _build_implicit_nightly_interval(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.implicit_every_night_interval",
        count="1",
        unit="day",
    )


def _build_every_other_interval(
    match: re.Match[str], _context: ExtractionContext, *, rule_id: str
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id=rule_id,
        count="1",
        unit=match.group("unit"),
        denominator="2",
        evidence_group=0,
    )


def _build_implicit_every_other_interval(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate:
    return _build_every_other_interval(match, context, rule_id="rate.implicit_every_other_interval")


def _build_occurring_interval(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.occurring_every_n_interval",
        count="1",
        unit=match.group("unit"),
        denominator=match.groupdict().get("denominator"),
        evidence_group=0,
    )


def _build_occurring_every_other_interval(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate:
    return _build_every_other_interval(
        match, context, rule_id="rate.occurring_every_other_interval"
    )


def _build_direct_rate(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.direct_count_per_period",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.groupdict().get("denominator"),
        evidence_group=0,
    )


def _build_adjective_rate(
    match: re.Match[str], _context: ExtractionContext, *, rule_id: str
) -> RawCandidate:
    period = match.groupdict().get("period") or match.groupdict().get("period_after")
    if period is None:
        raise ValueError(f"Rule {rule_id} matched without a period group")
    return _build_rate_candidate(
        match,
        rule_id=rule_id,
        count="1",
        unit=_adverbial_period_unit(period),
        denominator=_adverbial_period_denominator(period),
        evidence_group="evidence",
    )


def _build_seizure_adjective_rate(match: re.Match[str], context: ExtractionContext) -> RawCandidate:
    return _build_adjective_rate(match, context, rule_id="rate.seizure_adjective")


def _build_standalone_adjective_rate(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate:
    return _build_adjective_rate(match, context, rule_id="rate.standalone_adjective")


def _build_occurring_adjective_rate(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate:
    return _build_adjective_rate(match, context, rule_id="rate.occurring_adjective")


def _build_no_more_than_adverbial_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.no_more_than_adverbial",
        count=match.group("count"),
        unit=_adverbial_period_unit(match.group("period")),
        evidence_group=0,
    )


def _build_occurring_once_per_night(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.occurring_once_per_night",
        count="1",
        unit="day",
    )


def _build_persistent_adverbial_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.persistent_adverbial",
        count="1",
        unit=_adverbial_period_unit(match.group("period")),
    )


def _build_counted_adverbial_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.counted_adverbial",
        count=match.group("count"),
        unit=_adverbial_period_unit(match.group("period")),
    )


def _build_simple_partial_adverbial_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.simple_partial_adverbial",
        count="1",
        unit=_adverbial_period_unit(match.group("period")),
    )


def _build_recent_count(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.recent_count",
        count=match.group("count"),
        unit=match.group("unit"),
        evidence_group=0,
    )


def _build_count_during_recent_window(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.count_during_recent_window",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.group("denominator"),
        evidence_group=0,
    )


def _build_there_have_been_count(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.there_have_been_count",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.groupdict().get("denominator"),
        evidence_group="evidence",
    )


def _build_recorded_year_count(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.recorded_year_count",
        count=match.group("count"),
        unit="year",
        evidence_group=0,
    )


def _build_yesterday_count(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.yesterday_or_today_count",
        count=match.group("count"),
        unit="day",
        evidence_group=0,
    )


def _build_period_first_recent_count(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.period_first_recent_count",
        count=match.group("count"),
        unit=match.group("unit"),
        evidence_group=0,
    )


def _build_period_first_experienced_count(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.period_first_experienced_count",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.group("denominator"),
        evidence_group=0,
    )


def _build_period_first_featuring_count(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.period_first_featuring_count",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.group("denominator"),
        evidence_group=0,
    )


def _build_period_first_timeframe_count(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.period_first_timeframe_count",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.group("denominator"),
        evidence_group=0,
    )


def _build_period_first_occurred_count(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.period_first_occurred_count",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.group("denominator"),
        evidence_group=0,
    )


def _skip_period_first_experienced_count(match: re.Match[str], context: ExtractionContext) -> bool:
    trailing_context = context.text[match.end() : match.end() + 30].lower()
    return (
        "in that timeframe" in trailing_context
        or "have occurred" in trailing_context
        or "featuring" in trailing_context
    )


def _has_historical_lead_in(match: re.Match[str], context: ExtractionContext) -> bool:
    preceding = context.text[max(0, match.start() - 140) : match.start()].lower()
    historical_markers = (
        "by way of comparison",
        "baseline",
        "before ",
        "earlier",
        "historically",
        "history of",
        "previously",
        "prior to",
        "used to",
    )
    return any(marker in preceding for marker in historical_markers)


def _is_medication_or_dose_rate_distractor(
    match: re.Match[str], context: ExtractionContext
) -> bool:
    return _is_medication_or_dose_rate_distractor_impl(match, context.text)


def _is_nonprogressive_myoclonic_rate_distractor(
    match: re.Match[str], context: ExtractionContext
) -> bool:
    surrounding = context.text[max(0, match.start() - 90) : match.end() + 90].lower()
    return (
        "myoclonic jerk" in surrounding
        and re.search(r"\bwithout\s+progression\s+to\s+convulsions?\b", surrounding) is not None
    )


def _is_adjective_rate_distractor(match: re.Match[str], context: ExtractionContext) -> bool:
    evidence = match.group(0).lower()
    preceding = context.text[max(0, match.start() - 80) : match.start()].lower()
    following = context.text[match.end() : match.end() + 80].lower()
    surrounding = f"{preceding} {evidence} {following}"
    if evidence.startswith("daily") or evidence.endswith("daily"):
        if re.search(r"\bbrief\s+periods?\s+of\s+$", preceding):
            return True
    if evidence == "daily seizure":
        return (
            "recording" in following
            or "chart" in following
            or "diary" in following
            or "seizures:" in following
        )
    return bool(re.search(r"\b(?:smoker|tobacco|caffeine|coffee|alcohol|units)\b", surrounding))


DAILY_BASIS_CURRENT_RULE = RuleSpec(
    rule_id="rate.daily_basis_current",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Current seizure events described as occurring on a daily basis.",
    pattern=re.compile(
        rf"\b(?P<evidence>continues\s+to\s+experience\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+on\s+a\s+daily\s+basis)\b",
        re.IGNORECASE,
    ),
    build=_build_daily_basis_current,
    examples=(
        RuleExample(
            text="She continues to experience epileptic spasm on a daily basis.",
            expected_label="1 per day",
            expected_evidence="continues to experience epileptic spasm on a daily basis",
        ),
    ),
    provenance="Portable V1 current-rate expression.",
)

DAYS_OF_WEEK_RATE_RULE = RuleSpec(
    rule_id="rate.days_of_week",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Current seizure events counted by days of the week.",
    pattern=re.compile(
        rf"\b(?P<evidence>(?:{SEIZURE_RATE_PHRASE})\s+are\s+now\s+occurring\s+on\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+days?\s+of\s+the\s+week)\b",
        re.IGNORECASE,
    ),
    build=_build_days_of_week_rate,
    examples=(
        RuleExample(
            text="Absence seizures are now occurring on two to three days of the week.",
            expected_label="2 to 3 per week",
            expected_evidence=(
                "Absence seizures are now occurring on two to three days of the week"
            ),
        ),
    ),
    provenance="Portable V1 current-rate expression.",
)

NIGHTS_PER_PERIOD_RULE = RuleSpec(
    rule_id="rate.nights_per_period",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Current seizure events counted by nights per week, month, or year.",
    pattern=re.compile(
        rf"\b(?P<evidence>still\s+has\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+nights?\s+per\s+(?P<unit>week|month|year))\b",
        re.IGNORECASE,
    ),
    build=_build_nights_per_period,
    examples=(
        RuleExample(
            text="He still has generalised tonic-clonic seizures three nights per week.",
            expected_label="3 per week",
            expected_evidence=("still has generalised tonic-clonic seizures three nights per week"),
        ),
    ),
    provenance="Portable V1 current-rate expression.",
)

DESCRIPTOR_RATE_RULE = RuleSpec(
    rule_id="rate.descriptor_count_per_period",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Descriptor-led seizure rate such as reports five focal seizures per week.",
    pattern=re.compile(
        rf"\b(?:rate\s+of|records|reports)\s+(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:focal|sensory|automatisms?|non-motor|motor|aware|impaired-awareness|"
        rf"impaired\s+awareness|tonic-clonic|myoclonic|absence|brief)(?:\s+"
        rf"(?:focal|sensory|automatisms?|non-motor|motor|aware|impaired-awareness|"
        rf"impaired\s+awareness|tonic-clonic|myoclonic|absence|brief)){{0,4}}\s+"
        rf"per\s+(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    ),
    build=_build_descriptor_rate,
    examples=(
        RuleExample(
            text="The diary records five focal automatisms per week.",
            expected_label="5 per week",
            expected_evidence="records five focal automatisms per week",
        ),
    ),
    provenance="Portable V1 direct count-per-period expression.",
)

QUALIFIED_DIRECT_RATE_RULE = RuleSpec(
    rule_id="rate.qualified_direct_count_per_period",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure-type-qualified direct count per period.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:(?!day|days|week|weeks|month|months|quarter|quarters|year|years)"
        rf"{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS})\s+"
        rf"(?:per|each|every)\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    ),
    build=_build_qualified_direct_rate,
    examples=(
        RuleExample(
            text="She describes 6 to 7 myoclonic per week.",
            expected_label="6 to 7 per week",
            expected_evidence="6 to 7 myoclonic per week",
        ),
    ),
    provenance="Portable V1 direct count-per-period expression.",
)

IMPLICIT_INTERVAL_RULE = RuleSpec(
    rule_id="rate.implicit_every_n_interval",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure noun followed by every-N interval.",
    pattern=re.compile(
        rf"\b(?:{SEIZURE_TERMS})\s+every\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    ),
    build=_build_implicit_interval,
    exclude=(_has_historical_lead_in,),
    examples=(
        RuleExample(
            text="Present Seizure Frequency: focal seizures every 6 days.",
            expected_label="1 per 6 day",
            expected_evidence="seizures every 6 days",
        ),
    ),
    provenance="Portable V1 interval expression.",
)

IMPLICIT_NIGHTLY_INTERVAL_RULE = RuleSpec(
    rule_id="rate.implicit_every_night_interval",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure noun or descriptor followed by every night.",
    pattern=re.compile(
        rf"\b(?P<evidence>(?:{SEIZURE_RATE_PHRASE}|{SEIZURE_DESCRIPTOR_PHRASE})"
        rf"\s+every\s+night)\b",
        re.IGNORECASE,
    ),
    build=_build_implicit_nightly_interval,
    examples=(
        RuleExample(
            text="She now describes seizures every night.",
            expected_label="1 per day",
            expected_evidence="seizures every night",
        ),
    ),
    provenance="Portable V1 interval expression.",
)

IMPLICIT_EVERY_OTHER_INTERVAL_RULE = RuleSpec(
    rule_id="rate.implicit_every_other_interval",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure noun followed by every-other interval.",
    pattern=re.compile(
        rf"\b(?:{SEIZURE_TERMS})\s+every\s+other\s+(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    ),
    build=_build_implicit_every_other_interval,
    examples=(
        RuleExample(
            text="The current pattern is seizures every other week.",
            expected_label="1 per 2 week",
            expected_evidence="seizures every other week",
        ),
    ),
    provenance="Portable V1 interval expression.",
)

OCCURRING_INTERVAL_RULE = RuleSpec(
    rule_id="rate.occurring_every_n_interval",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Occurring/cluster verbs followed by every-N interval.",
    pattern=re.compile(
        rf"\b(?P<verb>occurring|occur|occurs|cluster|clusters)\s+"
        rf"(?:only\s+|roughly\s+|approximately\s+)?every\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    ),
    build=_build_occurring_interval,
    exclude=(_has_historical_lead_in,),
    examples=(
        RuleExample(
            text="The carer reports that seizures are occurring every 2 days.",
            expected_label="1 per 2 day",
            expected_evidence="occurring every 2 days",
        ),
    ),
    provenance="Portable V1 interval expression.",
)

OCCURRING_EVERY_OTHER_INTERVAL_RULE = RuleSpec(
    rule_id="rate.occurring_every_other_interval",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Occurring verbs followed by every-other interval.",
    pattern=re.compile(
        r"\b(?P<verb>occurring|occur|occurs)\s+"
        r"(?:only\s+|roughly\s+|approximately\s+)?every\s+other\s+"
        r"(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    ),
    build=_build_occurring_every_other_interval,
    examples=(
        RuleExample(
            text="Events are now occurring only every other month.",
            expected_label="1 per 2 month",
            expected_evidence="occurring only every other month",
        ),
    ),
    provenance="Portable V1 interval expression.",
)

QUARTER_DIRECT_RATE_RULE = RuleSpec(
    rule_id="rate.quarter_direct_count_per_period",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Direct count per quarter.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+per\s+(?P<unit>quarter)\b",
        re.IGNORECASE,
    ),
    build=_build_quarter_direct_rate,
    examples=(
        RuleExample(
            text="In clinic they report 12 to 30 per quarter.",
            expected_label="12 to 30 per 3 month",
            expected_evidence="12 to 30 per quarter",
        ),
    ),
    provenance="Portable V1 direct count-per-period expression.",
)

DIRECT_RATE_RULE = RuleSpec(
    rule_id="rate.direct_count_per_period",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Generic direct count per period with medication-dose exclusions.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:times?|{SEIZURE_TERMS})?\s*(?:per|each|every)\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    ),
    build=_build_direct_rate,
    exclude=(
        _is_medication_or_dose_rate_distractor,
        _is_nonprogressive_myoclonic_rate_distractor,
    ),
    examples=(
        RuleExample(
            text="He still has focal seizures four times per day.",
            expected_label="4 per day",
            expected_evidence="four times per day",
        ),
        RuleExample(
            text="Current medication is lamotrigine 100 mg twice per day.",
            anti_example=True,
            note="Medication dose frequency is not a seizure-frequency candidate.",
        ),
    ),
    provenance="Portable V1 direct count-per-period expression.",
)

SEIZURE_ADJECTIVE_RATE_RULE = RuleSpec(
    rule_id="rate.seizure_adjective",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure noun or descriptor modified by daily/weekly/monthly/yearly.",
    pattern=re.compile(
        rf"\b(?P<evidence>(?P<period>{ADJECTIVE_PERIOD_TOKEN})\s+"
        rf"(?:{SEIZURE_RATE_PHRASE})|"
        rf"(?:(?:{SEIZURE_RATE_PHRASE})|{SEIZURE_DESCRIPTOR_PHRASE})\s+"
        rf"(?P<period_after>{ADJECTIVE_PERIOD_TOKEN}))\b",
        re.IGNORECASE,
    ),
    build=_build_seizure_adjective_rate,
    exclude=(_is_adjective_rate_distractor,),
    examples=(
        RuleExample(
            text="Present Seizure Frequency: monthly seizures.",
            expected_label="1 per month",
            expected_evidence="monthly seizures",
        ),
        RuleExample(
            text="They report a myoclonic jerk daily.",
            expected_label="1 per day",
            expected_evidence="myoclonic jerk daily",
        ),
    ),
    provenance="Portable V1 adjective-rate expression.",
)

STANDALONE_ADJECTIVE_RATE_RULE = RuleSpec(
    rule_id="rate.standalone_adjective",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Frequency, pattern, or rate stated as daily/weekly/monthly/yearly.",
    pattern=re.compile(
        r"\b(?:frequency|pattern|rate)\s+(?:is\s+|was\s+|reported as\s+)?"
        rf"(?P<evidence>(?P<period>{ADJECTIVE_PERIOD_TOKEN}))\b",
        re.IGNORECASE,
    ),
    build=_build_standalone_adjective_rate,
    examples=(
        RuleExample(
            text="Current seizure frequency is daily.",
            expected_label="1 per day",
            expected_evidence="daily",
        ),
    ),
    provenance="Portable V1 adjective-rate expression.",
)

OCCURRING_ADJECTIVE_RATE_RULE = RuleSpec(
    rule_id="rate.occurring_adjective",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Occurring verbs modified by daily/weekly/monthly/yearly.",
    pattern=re.compile(
        r"\b(?P<evidence>(?:occurring|occur|occurs)\s+"
        r"(?:roughly\s+|approximately\s+)?"
        rf"(?P<period>{ADJECTIVE_PERIOD_TOKEN}))\b",
        re.IGNORECASE,
    ),
    build=_build_occurring_adjective_rate,
    exclude=(_is_adjective_rate_distractor,),
    examples=(
        RuleExample(
            text="She describes her seizures as occurring roughly yearly.",
            expected_label="1 per year",
            expected_evidence="occurring roughly yearly",
        ),
    ),
    provenance="Portable V1 adjective-rate expression.",
)

NO_MORE_THAN_ADVERBIAL_RATE_RULE = RuleSpec(
    rule_id="rate.no_more_than_adverbial",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Upper-bound adverbial rates such as no more than twice weekly.",
    pattern=re.compile(
        r"\bno\s+more\s+than\s+(?P<count>once|twice|thrice)\s+"
        r"(?P<period>daily|weekly|monthly|yearly)\b",
        re.IGNORECASE,
    ),
    build=_build_no_more_than_adverbial_rate,
    examples=(
        RuleExample(
            text="Focal events occur no more than twice weekly.",
            expected_label="2 per week",
            expected_evidence="no more than twice weekly",
        ),
    ),
    provenance="Portable V1 adverbial-rate expression.",
)

OCCURRING_ONCE_PER_NIGHT_RULE = RuleSpec(
    rule_id="rate.occurring_once_per_night",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure phrase followed by occurring once per night.",
    pattern=re.compile(
        rf"\b(?:{SEIZURE_RATE_PHRASE})\s+"
        rf"(?P<evidence>occurring\s+once\s+per\s+night)\b",
        re.IGNORECASE,
    ),
    build=_build_occurring_once_per_night,
    examples=(
        RuleExample(
            text="Focal seizures occurring once per night.",
            expected_label="1 per day",
            expected_evidence="occurring once per night",
        ),
    ),
    provenance="Portable V1 adverbial-rate expression.",
)

PERSISTENT_ADVERBIAL_RATE_RULE = RuleSpec(
    rule_id="rate.persistent_adverbial",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Persistent semiology described as daily/weekly/monthly/yearly.",
    pattern=re.compile(
        rf"\b(?P<evidence>(?:{QUALIFIED_SEIZURE_TERMS})\s+persist\s+"
        rf"(?P<period>daily|weekly|monthly|yearly))\b",
        re.IGNORECASE,
    ),
    build=_build_persistent_adverbial_rate,
    examples=(
        RuleExample(
            text="Brief myoclonic jerks persist monthly on awakening.",
            expected_label="1 per month",
            expected_evidence="Brief myoclonic jerks persist monthly",
        ),
    ),
    provenance="Portable V1 adverbial-rate expression.",
)

COUNTED_ADVERBIAL_RATE_RULE = RuleSpec(
    rule_id="rate.counted_adverbial",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Counted event phrase followed by daily/weekly/monthly/yearly.",
    pattern=re.compile(
        rf"\b(?P<evidence>(?:typically|usually)\s+(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+(?P<period>daily|weekly|monthly|yearly))\b",
        re.IGNORECASE,
    ),
    build=_build_counted_adverbial_rate,
    examples=(
        RuleExample(
            text="Events are typically four episodes monthly.",
            expected_label="4 per month",
            expected_evidence="typically four episodes monthly",
        ),
    ),
    provenance="Portable V1 adverbial-rate expression.",
)

SIMPLE_PARTIAL_ADVERBIAL_RATE_RULE = RuleSpec(
    rule_id="rate.simple_partial_adverbial",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Simple partial seizure followed by daily/weekly/monthly/yearly.",
    pattern=re.compile(
        r"\b(?P<evidence>simple\s+partial\s+seizure\s+"
        r"(?P<period>daily|weekly|monthly|yearly))\b",
        re.IGNORECASE,
    ),
    build=_build_simple_partial_adverbial_rate,
    examples=(
        RuleExample(
            text="She now describes a simple partial seizure monthly.",
            expected_label="1 per month",
            expected_evidence="simple partial seizure monthly",
        ),
    ),
    provenance="Portable V1 adverbial-rate expression.",
)

RECENT_COUNT_RULE = RuleSpec(
    rule_id="rate.recent_count",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Counted seizure phrase in a single recent day/week/month/quarter/year.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"(?:last|this|past)\s+(?P<unit>day|week|month|quarter|year)\b",
        re.IGNORECASE,
    ),
    build=_build_recent_count,
    exclude=(_has_historical_lead_in,),
    examples=(
        RuleExample(
            text="He describes three or four seizures last week.",
            expected_label="3 to 4 per week",
            expected_evidence="three or four seizures last week",
        ),
    ),
    provenance="Portable V1 recent-window count expression.",
)

COUNT_DURING_RECENT_WINDOW_RULE = RuleSpec(
    rule_id="rate.count_during_recent_window",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Counted seizure phrase during or in a recent multi-unit window.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"(?:during|in)\s+(?:the\s+)?(?:last|past)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    ),
    build=_build_count_during_recent_window,
    exclude=(_has_historical_lead_in,),
    examples=(
        RuleExample(
            text="The diary shows 7 to 9 focal onset seizures in three weeks.",
            expected_label="7 to 9 per 3 week",
            expected_evidence="7 to 9 focal onset seizures in three weeks",
        ),
    ),
    provenance="Portable V1 recent-window count expression.",
)

THERE_HAVE_BEEN_COUNT_RULE = RuleSpec(
    rule_id="rate.there_have_been_count",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Counted events over, in, during, or recorded in a period.",
    pattern=re.compile(
        rf"\b(?:there\s+(?:have|has|were|are)\s+been\s+)?"
        rf"(?P<evidence>(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"(?:over|in|during|recorded\s+in)\s+(?:the\s+)?(?:past|last)?\s*"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN}|fortnight))\b",
        re.IGNORECASE,
    ),
    build=_build_there_have_been_count,
    examples=(
        RuleExample(
            text="There have been four brief episodes over the past three weeks.",
            expected_label="4 per 3 week",
            expected_evidence="four brief episodes over the past three weeks",
        ),
    ),
    provenance="Portable V1 recent-window count expression.",
)

RECORDED_YEAR_COUNT_RULE = RuleSpec(
    rule_id="rate.recorded_year_count",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Counted seizure phrase recorded in a year so far.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        r"recorded\s+in\s+\d{4}\s+so\s+far\b",
        re.IGNORECASE,
    ),
    build=_build_recorded_year_count,
    examples=(
        RuleExample(
            text="Seven brief seizures recorded in 2024 so far.",
            expected_label="7 per year",
            expected_evidence="Seven brief seizures recorded in 2024 so far",
        ),
    ),
    provenance="Portable V1 recent-window count expression.",
)

YESTERDAY_OR_TODAY_COUNT_RULE = RuleSpec(
    rule_id="rate.yesterday_or_today_count",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Counted seizure phrase yesterday or today.",
    pattern=re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        r"(?:yesterday|today)\b",
        re.IGNORECASE,
    ),
    build=_build_yesterday_count,
    examples=(
        RuleExample(
            text="The patient reported 1 tonic-clonic seizures yesterday.",
            expected_label="1 per day",
            expected_evidence="1 tonic-clonic seizures yesterday",
        ),
    ),
    provenance="Portable V1 recent-window count expression.",
)

PERIOD_FIRST_RECENT_COUNT_RULE = RuleSpec(
    rule_id="rate.period_first_recent_count",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Single-unit period-first count such as This week ... three seizures.",
    pattern=re.compile(
        rf"\b(?P<period>This|Over the past|Over the last|During the past|During the last)\s+"
        rf"(?P<unit>day|week|month|year),?\s+"
        rf".{{0,60}}?\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\b",
        re.IGNORECASE,
    ),
    build=_build_period_first_recent_count,
    examples=(
        RuleExample(
            text="This week he has had 3 or 4 focal impaired awareness seizures.",
            expected_label="3 to 4 per week",
            expected_evidence="This week he has had 3 or 4 focal impaired awareness seizures",
        ),
    ),
    provenance="Portable V1 period-first count expression.",
)

PERIOD_FIRST_EXPERIENCED_COUNT_RULE = RuleSpec(
    rule_id="rate.period_first_experienced_count",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Multi-unit period-first count with count later in the span.",
    pattern=re.compile(
        rf"\b(?P<period>Over the past|Over the last|During the past|During the last|"
        rf"over the past|over the last|during the past|during the last|in the past|"
        rf"in the last)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN})[,\s()]+"
        rf".{{0,80}}?\b(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\b",
        re.IGNORECASE,
    ),
    build=_build_period_first_experienced_count,
    exclude=(_skip_period_first_experienced_count,),
    examples=(
        RuleExample(
            text="Over the past month, they estimate 3 to 4 seizures.",
            expected_label="3 to 4 per month",
            expected_evidence="Over the past month, they estimate 3 to 4 seizures",
        ),
    ),
    provenance="Portable V1 period-first count expression.",
)

PERIOD_FIRST_FEATURING_COUNT_RULE = RuleSpec(
    rule_id="rate.period_first_featuring_count",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Period-first count with featuring-awareness wording.",
    pattern=re.compile(
        rf"\b(?P<period>Over the past|Over the last|During the past|During the last|"
        rf"over the past|over the last|during the past|during the last)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN}),?\s+"
        rf".{{0,80}}?\b(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+featuring\s+"
        rf"(?:{WORD_TOKEN}\s+){{0,3}}awareness\b",
        re.IGNORECASE,
    ),
    build=_build_period_first_featuring_count,
    examples=(
        RuleExample(
            text=(
                "Over the last three weeks, there have been four brief episodes "
                "featuring impaired awareness."
            ),
            expected_label="4 per 3 week",
            expected_evidence=(
                "Over the last three weeks, there have been four brief episodes "
                "featuring impaired awareness"
            ),
        ),
    ),
    provenance="Portable V1 period-first count expression.",
)

PERIOD_FIRST_TIMEFRAME_COUNT_RULE = RuleSpec(
    rule_id="rate.period_first_timeframe_count",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Period-first count ending with in that timeframe.",
    pattern=re.compile(
        rf"\b(?P<period>Over the past|Over the last|During the past|During the last)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN}),?\s+"
        rf".{{0,260}}?\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        r"in\s+that\s+timeframe\b",
        re.IGNORECASE,
    ),
    build=_build_period_first_timeframe_count,
    examples=(
        RuleExample(
            text="Over the past four months, she reports three events in that timeframe.",
            expected_label="3 per 4 month",
            expected_evidence=(
                "Over the past four months, she reports three events in that timeframe"
            ),
        ),
    ),
    provenance="Portable V1 period-first count expression.",
)

PERIOD_FIRST_OCCURRED_COUNT_RULE = RuleSpec(
    rule_id="rate.period_first_occurred_count",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Period-first count with have occurred wording.",
    pattern=re.compile(
        rf"\b(?P<period>Over the past|Over the last|During the past|During the last)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN}),?\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        r"have\s+occurred\b",
        re.IGNORECASE,
    ),
    build=_build_period_first_occurred_count,
    examples=(
        RuleExample(
            text="Over the past six weeks, four episodes have occurred.",
            expected_label="4 per 6 week",
            expected_evidence="Over the past six weeks, four episodes have occurred",
        ),
    ),
    provenance="Portable V1 period-first count expression.",
)

PORTABLE_RATE_RULES = (
    DAILY_BASIS_CURRENT_RULE,
    DAYS_OF_WEEK_RATE_RULE,
    NIGHTS_PER_PERIOD_RULE,
    DESCRIPTOR_RATE_RULE,
    QUALIFIED_DIRECT_RATE_RULE,
    IMPLICIT_INTERVAL_RULE,
    IMPLICIT_NIGHTLY_INTERVAL_RULE,
    IMPLICIT_EVERY_OTHER_INTERVAL_RULE,
    OCCURRING_INTERVAL_RULE,
    OCCURRING_EVERY_OTHER_INTERVAL_RULE,
    QUARTER_DIRECT_RATE_RULE,
    DIRECT_RATE_RULE,
    SEIZURE_ADJECTIVE_RATE_RULE,
    STANDALONE_ADJECTIVE_RATE_RULE,
    OCCURRING_ADJECTIVE_RATE_RULE,
    NO_MORE_THAN_ADVERBIAL_RATE_RULE,
    OCCURRING_ONCE_PER_NIGHT_RULE,
    PERSISTENT_ADVERBIAL_RATE_RULE,
    COUNTED_ADVERBIAL_RATE_RULE,
    SIMPLE_PARTIAL_ADVERBIAL_RATE_RULE,
    RECENT_COUNT_RULE,
    COUNT_DURING_RECENT_WINDOW_RULE,
    THERE_HAVE_BEEN_COUNT_RULE,
    RECORDED_YEAR_COUNT_RULE,
    YESTERDAY_OR_TODAY_COUNT_RULE,
    PERIOD_FIRST_RECENT_COUNT_RULE,
    PERIOD_FIRST_EXPERIENCED_COUNT_RULE,
    PERIOD_FIRST_FEATURING_COUNT_RULE,
    PERIOD_FIRST_TIMEFRAME_COUNT_RULE,
    PERIOD_FIRST_OCCURRED_COUNT_RULE,
)


def _adverbial_period_unit(value: str) -> str:
    return {
        "daily": "day",
        "weekly": "week",
        "monthly": "month",
        "yearly": "year",
        "bimonthly": "month",
    }[value.lower()]


def _adverbial_period_denominator(value: str) -> str | None:
    if value.lower() == "bimonthly":
        return "2"
    return None


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")
