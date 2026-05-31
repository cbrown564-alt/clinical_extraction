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
) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label=_rate_label(count, unit, denominator),
        evidence=_clean_evidence(match.group("evidence")),
        rule_id=rule_id,
        rule_group=RuleGroup.GAN_SHORTHAND,
        portability=Portability.GAN2026_SPECIFIC,
        match_groups=match.groupdict(),
    )


def _build_tc_sz_count_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_shorthand_rate_candidate(
        match,
        rule_id="gan_shorthand.tc_sz_count_rate",
        count=match.group("count"),
        unit=_expanded_compact_unit(match.group("unit")),
    )


def _build_abs_adjective_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
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
        portability=Portability.GAN2026_SPECIFIC,
        match_groups=match.groupdict(),
    )


def _build_abs_count_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
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
    )


def _build_q_interval(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_shorthand_rate_candidate(
        match,
        rule_id="gan_shorthand.q_interval",
        count="1",
        unit=_expanded_compact_unit(match.group("unit")),
        denominator=match.group("denominator"),
    )


TC_SZ_COUNT_RATE_RULE = RuleSpec(
    rule_id="gan_shorthand.tc_sz_count_rate",
    group=RuleGroup.GAN_SHORTHAND,
    portability=Portability.GAN2026_SPECIFIC,
    description="Compact tonic-clonic or seizure shorthand count per abbreviated period.",
    pattern=re.compile(
        rf"\b(?P<evidence>(?:TC|sz)\s+(?:[*x×]\s*)?"
        rf"(?P<count>{NUMBER_VALUE_TOKEN})\s*/\s*"
        r"(?P<unit>d|day|wk|week|mo|month|yr|year))\b",
        re.IGNORECASE,
    ),
    build=_build_tc_sz_count_rate,
    examples=(
        RuleExample(
            text="Clinic shorthand says TC *nine/mo.",
            expected_label="9 per month",
            expected_evidence="TC *nine/mo",
        ),
        RuleExample(
            text="Current frequency reported as: sz ×nine/mo.",
            expected_label="9 per month",
            expected_evidence="sz ×nine/mo",
        ),
    ),
    provenance="Gan 2026 compact validation shorthand.",
)

ABS_ADJECTIVE_RATE_RULE = RuleSpec(
    rule_id="gan_shorthand.abs_adjective_rate",
    group=RuleGroup.GAN_SHORTHAND,
    portability=Portability.GAN2026_SPECIFIC,
    description="Compact absence shorthand with adjective period.",
    pattern=re.compile(
        r"\b(?P<evidence>abs\s+(?:[*x×]\s*)?"
        r"(?P<period>daily|weekly|monthly|yearly|bimonthly))\b",
        re.IGNORECASE,
    ),
    build=_build_abs_adjective_rate,
    examples=(
        RuleExample(
            text="Diary shorthand says abs *monthly.",
            expected_label="1 per month",
            expected_evidence="abs *monthly",
        ),
    ),
    provenance="Gan 2026 compact validation shorthand.",
)

ABS_COUNT_RATE_RULE = RuleSpec(
    rule_id="gan_shorthand.abs_count_rate",
    group=RuleGroup.GAN_SHORTHAND,
    portability=Portability.GAN2026_SPECIFIC,
    description="Compact absence shorthand count plus adjective period.",
    pattern=re.compile(
        rf"\b(?P<evidence>abs\s+(?P<count>{NUMBER_TOKEN})\s+"
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
    ),
    provenance="Gan 2026 compact validation shorthand.",
)

Q_INTERVAL_RULE = RuleSpec(
    rule_id="gan_shorthand.q_interval",
    group=RuleGroup.GAN_SHORTHAND,
    portability=Portability.GAN2026_SPECIFIC,
    description="Compact q-interval shorthand such as q2-3wk or qone to twod.",
    pattern=re.compile(
        rf"\b(?P<evidence>q(?P<denominator>{NUMBER_TOKEN})\s*"
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
            text="Currently events are occurring qone to twod on workdays.",
            expected_label="1 per 1 to 2 day",
            expected_evidence="qone to twod",
        ),
    ),
    provenance="Gan 2026 compact validation shorthand.",
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
