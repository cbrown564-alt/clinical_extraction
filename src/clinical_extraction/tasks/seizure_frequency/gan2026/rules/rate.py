from __future__ import annotations

import re
from collections.abc import Sequence

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
SEIZURE_DESCRIPTOR_PHRASE = (
    r"(?:tonic-clonic|myoclonic|convulsive|focal(?:\s+[a-z][a-z-]*){0,3}|"
    r"absence|drop|epileptic|impaired awareness|focal onset|petit mal|simple partial)"
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
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label=_rate_label(count, unit, denominator),
        evidence=_clean_evidence(match.group(evidence_group)),
        rule_id=rule_id,
        rule_group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _build_daily_basis_current(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.daily_basis_current",
        count="1",
        unit="day",
    )


def _build_days_of_week_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.days_of_week",
        count=match.group("count"),
        unit="week",
    )


def _build_nights_per_period(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.nights_per_period",
        count=match.group("count"),
        unit=match.group("unit"),
    )


def _build_descriptor_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.descriptor_count_per_period",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.groupdict().get("denominator"),
        evidence_group=0,
    )


def _build_qualified_direct_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.qualified_direct_count_per_period",
        count=match.group("count"),
        unit=match.group("unit"),
        denominator=match.groupdict().get("denominator"),
        evidence_group=0,
    )


def _build_quarter_direct_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_rate_candidate(
        match,
        rule_id="rate.quarter_direct_count_per_period",
        count=match.group("count"),
        unit=match.group("unit"),
        evidence_group=0,
    )


def _build_implicit_interval(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
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
    return _build_every_other_interval(
        match, context, rule_id="rate.implicit_every_other_interval"
    )


def _build_occurring_interval(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
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
            expected_evidence=(
                "still has generalised tonic-clonic seizures three nights per week"
            ),
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
)


def _rate_label(count: str, unit: str, denominator: str | None = None) -> str:
    count_value = _number_token(count)
    unit_value = _singular_unit(unit)
    denominator_value = _number_token(denominator) if denominator else None
    if unit_value == "quarter":
        unit_value = "month"
        denominator_value = _quarter_month_denominator(denominator_value)
    if denominator_value in {None, "1"}:
        return f"{count_value} per {unit_value}"
    return f"{count_value} per {denominator_value} {unit_value}"


def _quarter_month_denominator(denominator: str | None) -> str:
    if denominator in {None, "1"}:
        return "3"
    if denominator and denominator.isdigit():
        return str(int(denominator) * 3)
    return f"3 {denominator}"


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


def _singular_unit(value: str) -> str:
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")
