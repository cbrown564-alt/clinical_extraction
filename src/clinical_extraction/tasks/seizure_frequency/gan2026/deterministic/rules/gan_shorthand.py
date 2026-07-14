"""Compact clinical shorthand rules for seizure frequency extraction.

These rules capture seizure frequency expressed in compact notation conventions
found in epilepsy clinical documentation — seizure-type abbreviation prefix with
count and unit denominator (e.g., "TC 5/mo", "sz 2/wk"), absence shorthand
(e.g., "abs daily", "absence 3 monthly"), and standard medical q-interval
notation (e.g., "q2-3wk", "q6h"). They are intentionally kept in the
GAN_SHORTHAND group so that ablation of this family remains a single switch;
their portability reflects their actual clinical scope after de-overfitting
(Phase 2 of the three-way architecture comparison plan, Section 4).

De-overfitting note (2026-06-09): the original versions of these rules used
GAN2026_SPECIFIC portability and accepted formatting that was specific to the
GAN 2026 benchmark dataset — word numbers embedded in compact shorthand ("TC
nine/mo"), and special separator characters before counts (asterisk, X, ×, e.g.
"TC *5/wk", "sz X7/mo"). These embellishments matched validation phrasing but
would not generalise to real clinical notes. The rewritten rules require
digit-only counts and remove special separator prefixes, so they match the
compact notation as it would appear in genuine clinical documentation.
Rows that depended on the benchmark-specific variants are now correctly
null/unknown rather than extracted via rules that only fire on validation data.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

# Digit-only range token: matches "5", "2-3", "1–2", "4—6" but NOT word numbers
# like "nine" or "four". Compact shorthand with word numbers is GAN-dataset-specific
# notation; real clinical notes use digit counts.
DIGIT_RANGE_TOKEN = r"(?:\d+(?:\s*[-–—]\s*\d+)?)"

# Legacy word-number table and derived tokens are kept for backwards-compatible
# helper functions only; they are no longer used in rule patterns after
# de-overfitting.
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


def apply_gan_shorthand_rules(
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


def _build_shorthand_rate_candidate(
    match: re.Match[str],
    *,
    rule_id: str,
    count: str,
    unit: str,
    denominator: str | None = None,
    portability: Portability = Portability.SEIZURE_FREQUENCY,
) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label=_rate_label(count, unit, denominator),
        evidence=_clean_evidence(match.group("evidence")),
        rule_id=rule_id,
        rule_group=RuleGroup.GAN_SHORTHAND,
        portability=portability,
        match_groups=match.groupdict(),
    )


def _build_tc_sz_count_rate(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_shorthand_rate_candidate(
        match,
        rule_id="gan_shorthand.tc_sz_count_rate",
        count=match.group("count"),
        unit=_expanded_compact_unit(match.group("unit")),
        portability=Portability.SEIZURE_FREQUENCY,
    )


def _build_abs_adjective_rate(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    period = match.group("period").lower()
    period_labels = {
        "daily": "1 per day",
        "weekly": "1 per week",
        "monthly": "1 per month",
        "yearly": "1 per year",
        "bimonthly": "1 per 2 month",
    }
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label=period_labels[period],
        evidence=_clean_evidence(match.group("evidence")),
        rule_id="gan_shorthand.abs_adjective_rate",
        rule_group=RuleGroup.GAN_SHORTHAND,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _build_abs_count_rate(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    period_units = {
        "daily": ("day", None),
        "weekly": ("week", None),
        "monthly": ("month", None),
        "yearly": ("year", None),
        "bimonthly": ("month", "2"),
    }
    unit, denominator = period_units[match.group("period").lower()]
    return _build_shorthand_rate_candidate(
        match,
        rule_id="gan_shorthand.abs_count_rate",
        count=match.group("count"),
        unit=unit,
        denominator=denominator,
        portability=Portability.SEIZURE_FREQUENCY,
    )


def _build_q_interval(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_shorthand_rate_candidate(
        match,
        rule_id="gan_shorthand.q_interval",
        count="1",
        unit=_expanded_compact_unit(match.group("unit")),
        denominator=match.group("denominator"),
        portability=Portability.CLINICAL_EPILEPSY,
    )


TC_SZ_COUNT_RATE_RULE = RuleSpec(
    rule_id="gan_shorthand.tc_sz_count_rate",
    group=RuleGroup.GAN_SHORTHAND,
    portability=Portability.SEIZURE_FREQUENCY,
    description=(
        "Compact epilepsy seizure-type abbreviation with digit count per abbreviated "
        "period (e.g., 'TC 5/mo', 'sz 2/wk', 'GTC 3/month'). Digit-only counts; "
        "no special separator prefix."
    ),
    pattern=re.compile(
        rf"\b(?P<evidence>(?:TC|GTCS|GTC|sz)\s*:?\s*"
        rf"(?P<count>{DIGIT_RANGE_TOKEN})\s*/\s*"
        r"(?P<unit>d|day|wk|week|mo|month|yr|year))\b",
        re.IGNORECASE,
    ),
    build=_build_tc_sz_count_rate,
    examples=(
        RuleExample(
            text="Clinic shorthand says TC 5/mo.",
            expected_label="5 per month",
            expected_evidence="TC 5/mo",
        ),
        RuleExample(
            text="Current frequency reported as: sz 2/wk.",
            expected_label="2 per week",
            expected_evidence="sz 2/wk",
        ),
        RuleExample(
            text="GTCS: 3/month seen this quarter.",
            expected_label="3 per month",
            expected_evidence="GTCS: 3/month",
        ),
        RuleExample(
            text="TC nine/mo",
            anti_example=True,
            note=(
                "Word numbers in compact shorthand are GAN-dataset-specific notation "
                "and not matched by the generalized rule."
            ),
        ),
        RuleExample(
            text="sz X7/mo",
            anti_example=True,
            note=(
                "Asterisk/X/× separator variants are GAN-dataset-specific notation "
                "and not matched by the generalized rule."
            ),
        ),
    ),
    provenance=(
        "Generalized from GAN 2026 compact notation (2026-06-09 Phase 2 de-overfitting): "
        "digit-only counts, no special separators, SEIZURE_FREQUENCY portability."
    ),
)

ABS_ADJECTIVE_RATE_RULE = RuleSpec(
    rule_id="gan_shorthand.abs_adjective_rate",
    group=RuleGroup.GAN_SHORTHAND,
    portability=Portability.SEIZURE_FREQUENCY,
    description=(
        "Compact absence seizure shorthand with adjective period (e.g., 'abs daily', "
        "'absence monthly'). No special separator prefix."
    ),
    pattern=re.compile(
        r"\b(?P<evidence>(?:abs|absence)\s+"
        r"(?P<period>daily|weekly|monthly|yearly|bimonthly))\b",
        re.IGNORECASE,
    ),
    build=_build_abs_adjective_rate,
    examples=(
        RuleExample(
            text="Diary shorthand says abs monthly.",
            expected_label="1 per month",
            expected_evidence="abs monthly",
        ),
        RuleExample(
            text="Absence seizures are occurring daily.",
            expected_label="1 per day",
            expected_evidence="absence daily",
        ),
        RuleExample(
            text="abs *monthly",
            anti_example=True,
            note=(
                "Asterisk separator before period is GAN-dataset-specific notation "
                "and not matched by the generalized rule."
            ),
        ),
    ),
    provenance=(
        "Generalized from GAN 2026 compact notation (2026-06-09 Phase 2 de-overfitting): "
        "no asterisk separator, 'absence' added as prefix alternative, "
        "SEIZURE_FREQUENCY portability."
    ),
)

ABS_COUNT_RATE_RULE = RuleSpec(
    rule_id="gan_shorthand.abs_count_rate",
    group=RuleGroup.GAN_SHORTHAND,
    portability=Portability.SEIZURE_FREQUENCY,
    description=(
        "Compact absence seizure shorthand with digit count plus adjective period "
        "(e.g., 'abs 8 monthly', 'absence 3 weekly'). No special separator prefix."
    ),
    pattern=re.compile(
        r"\b(?P<evidence>(?:abs|absence)\s+(?P<count>\d+)\s+"
        r"(?P<period>daily|weekly|monthly|yearly|bimonthly))\b",
        re.IGNORECASE,
    ),
    build=_build_abs_count_rate,
    examples=(
        RuleExample(
            text="On their calendar, abs 8 monthly over the past three months.",
            expected_label="8 per month",
            expected_evidence="abs 8 monthly",
        ),
        RuleExample(
            text="absence 3 weekly documented.",
            expected_label="3 per week",
            expected_evidence="absence 3 weekly",
        ),
    ),
    provenance=(
        "Generalized from GAN 2026 compact notation (2026-06-09 Phase 2 de-overfitting): "
        "no asterisk separator, 'absence' added as prefix alternative, digit-only count, "
        "SEIZURE_FREQUENCY portability."
    ),
)

Q_INTERVAL_RULE = RuleSpec(
    rule_id="gan_shorthand.q_interval",
    group=RuleGroup.GAN_SHORTHAND,
    portability=Portability.CLINICAL_EPILEPSY,
    description=(
        "Standard medical q-interval shorthand with digit denominator and abbreviated "
        "unit (e.g., 'q2-3wk', 'q6h', 'q1-2d'). Digit-only denominators."
    ),
    pattern=re.compile(
        rf"\b(?P<evidence>q(?P<denominator>{DIGIT_RANGE_TOKEN})\s*"
        r"(?P<unit>d|day|wk|week|mo|month|yr|year))\b",
        re.IGNORECASE,
    ),
    build=_build_q_interval,
    examples=(
        RuleExample(
            text="The current clinic shorthand is q2 - 3wk.",
            expected_label="1 per 2 to 3 week",
            expected_evidence="q2 - 3wk",
        ),
        RuleExample(
            text="Currently events are occurring q1-2d on workdays.",
            expected_label="1 per 1 to 2 day",
            expected_evidence="q1-2d",
        ),
        RuleExample(
            text="qtwo - threewk",
            anti_example=True,
            note=(
                "Word numbers in q-interval notation are GAN-dataset-specific "
                "and not matched by the generalized rule."
            ),
        ),
    ),
    provenance=(
        "Generalized from GAN 2026 compact notation (2026-06-09 Phase 2 de-overfitting): "
        "digit-only denominator, CLINICAL_EPILEPSY portability."
    ),
)

GAN_SHORTHAND_RULES = (
    TC_SZ_COUNT_RATE_RULE,
    ABS_ADJECTIVE_RATE_RULE,
    ABS_COUNT_RATE_RULE,
    Q_INTERVAL_RULE,
)


def _rate_label(count: str, unit: str, denominator: str | None = None) -> str:
    count_value = _number_token(count)
    unit_value = _singular_unit(unit)
    denominator_value = _number_token(denominator) if denominator else None
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


def _singular_unit(value: str) -> str:
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


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


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")
