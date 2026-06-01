from __future__ import annotations

import re
from collections.abc import Callable

from clinical_extraction.tasks.seizure_frequency.gan2026 import label_parser as _labels
from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

NUM_WORDS = {
    "zero": "0",
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
}
UNIT_SYNONYMS = {
    "d": "day",
    "day": "day",
    "days": "day",
    "w": "week",
    "wk": "week",
    "wks": "week",
    "week": "week",
    "weeks": "week",
    "mo": "month",
    "mon": "month",
    "mons": "month",
    "mos": "month",
    "month": "month",
    "months": "month",
    "y": "year",
    "yr": "year",
    "yr.": "year",
    "yrs": "year",
    "year": "year",
    "years": "year",
}


def _words_to_numbers(text: str) -> str:
    return re.sub(
        r"\b(" + "|".join(NUM_WORDS) + r")\b",
        lambda match: NUM_WORDS[match.group(0)],
        text,
    )


def _normalize_ranges(text: str) -> str:
    return re.sub(r"(\d+)\s*[-–—]\s*(\d+)", r"\1 to \2", text)


def _format_prediction_rate(count_text: str, unit_text: str) -> str:
    count = re.sub(r"\s*(?:-|–|—)\s*", " to ", count_text.strip())
    count = re.sub(r"\s+or\s+", " to ", count)
    count = re.sub(r"\s+", " ", count)
    unit = unit_text.rstrip("s").strip()
    if " per " in count:
        return f"{count} {unit}"
    return f"{count} per {unit}"


def _gold_policy_cluster_name_stripping(text: str) -> str:
    text = _labels.normalize_frequency_label(text)
    match = re.fullmatch(
        r"clusters?\s+(?P<label>\d+(?:\s*to\s*\d+)?\s+per\s+"
        r"(?:\d+(?:\s*to\s*\d+)?\s+)?(?:day|week|month|year))",
        text,
    )
    if match:
        return match.group("label")

    match = re.fullmatch(
        r"(?:(?P<count>\d+(?:\s*to\s*\d+)?)\s+)?clusters?\s+"
        r"(?:every|per)\s+(?P<den>\d+(?:\s*to\s*\d+)?(?:\s+|-)?"
        r"(?:day|week|month|year)s?)",
        text,
    )
    if match:
        count = match.group("count") or "1"
        denominator = _labels._normalize_period(
            _normalize_ranges(match.group("den").replace("-", " "))
        )
        return f"{count} per {denominator}"

    match = re.fullmatch(
        r"(?P<count>\d+(?:\s*to\s*\d+)?)\s+clusters?\s+per\s+"
        r"(?P<den>(?:\d+(?:\s*to\s*\d+)?\s+)?(?:day|week|month|year))",
        text,
    )
    if match and "per cluster" not in text:
        return f"{match.group('count')} per {match.group('den')}"
    return text


def _gold_policy_vague_weekday_cadence(text: str) -> str:
    if re.search(r"\b(?:most|several|multiple)\s+weekdays\b", text):
        return "multiple per week"
    return text


def _gold_policy_bimonthly(text: str) -> str:
    if text == "bi-1 per month":
        return "1 per 2 month"
    if re.search(r"\bbi-?monthly\b", text) and not re.search(
        r"\b(?:twice|2)\s+(?:per\s+)?month\b",
        text,
    ):
        return "1 per 2 month"
    return text


def _gold_policy_vague_quantity_explicit_denominator(text: str) -> str:
    text = _labels.normalize_frequency_label(text)
    vague = r"(?:several|multiple|many|few|a few)"
    unit = r"(day|week|month|year)"
    match = re.fullmatch(
        rf"{vague}\s+(?:times?\s+)?(?:per|each|every)\s+{unit}s?",
        text,
    )
    if match:
        return f"multiple per {match.group(1)}"

    match = re.fullmatch(rf"{vague}\s+times?\s+1\s+per\s+{unit}s?", text)
    if match:
        return f"multiple per {match.group(1)}"

    match = re.fullmatch(
        rf"{vague}\s+(?:in\s+)?(?:the\s+)?(?:past|last|this)\s+{unit}s?",
        text,
    )
    if match:
        return f"multiple per {match.group(1)}"
    return text


def _gold_policy_period_dialect_and_shorthand(text: str) -> str:
    text = _labels.normalize_frequency_label(text)
    interval = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
    interval_range = rf"{interval}(?:\s*(?:to|-|–|—)\s*{interval})?"

    q_match = re.fullmatch(
        rf"q\s*(?P<interval>{interval_range})\s*(?P<unit>d|day|wk|week|mo|month|yr|year)",
        text,
    )
    if q_match:
        unit = UNIT_SYNONYMS.get(q_match.group("unit"), q_match.group("unit"))
        return _format_prediction_rate(
            f"1 per {_words_to_numbers(q_match.group('interval'))}",
            unit,
        )

    x_match = re.fullmatch(
        rf"x\s*(?P<count>{interval})\s*(?:/|per\s+)(?P<unit>d|day|wk|week|mo|month|yr|year)",
        text,
    )
    if x_match:
        unit = UNIT_SYNONYMS.get(x_match.group("unit"), x_match.group("unit"))
        return _format_prediction_rate(_words_to_numbers(x_match.group("count")), unit)
    return text


def _gold_policy_cluster_syntax_grammar(text: str) -> str:
    text = _labels.normalize_frequency_label(text)
    num = r"(?:multiple|\d+(?:\s*to\s*\d+)?)"
    unit = r"(?:day|week|month|year)"

    text = re.sub(r"\bcluster\s+days?\b", "cluster", text)
    text = re.sub(r"\bper\s+cluster\s+days?\b", "per cluster", text)

    match = re.fullmatch(
        rf"(?P<count>{num})\s+cluster\s+per\s+"
        rf"(?P<den>(?:\d+(?:\s*to\s*\d+)?\s+)?)"
        rf"(?P<unit>{unit}),\s+(?P<per>{num})\s+per\s+cluster",
        text,
    )
    if match:
        denominator = (match.group("den") or "").strip()
        den_text = f"{denominator} " if denominator and denominator != "1" else ""
        return (
            f"{match.group('count')} cluster per {den_text}{match.group('unit')}, "
            f"{match.group('per')} per cluster"
        )
    return text


def _gold_policy_single_total_window(text: str) -> str:
    text = _labels.normalize_frequency_label(text)
    match = re.fullmatch(
        r"(?P<count>\d+(?:\s*to\s*\d+)?)\s+"
        r"(?:in|over|during|for)\s+"
        r"(?:(?:the\s+)?(?:past|last|this)\s+)?"
        r"(?P<den>\d+(?:\s*to\s*\d+)?)\s+(?P<unit>day|week|month|year)s?",
        text,
    )
    if match:
        return _format_prediction_rate(
            f"{match.group('count')} per {match.group('den')}",
            match.group("unit"),
        )
    return text


def _gold_normalization_policy_rule(
    *,
    rule_id: str,
    description: str,
    apply: Callable[[str], str],
    example: str,
    expected: str,
) -> RuleSpec:
    def build(match: re.Match[str], _context: ExtractionContext) -> str:
        return apply(match.group("label"))

    return RuleSpec(
        rule_id=rule_id,
        group=RuleGroup.GOLD_NORMALIZATION_POLICY,
        portability=Portability.GAN2026_SPECIFIC,
        description=description,
        pattern=re.compile(r"\A(?P<label>.*)\Z", re.DOTALL),
        build=build,
        examples=(RuleExample(text=example, expected_label=expected),),
        provenance="Gan 2026 validation-only gold-normalization policy review.",
    )


CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES = (
    _gold_normalization_policy_rule(
        rule_id="gold_normalization_policy.cluster_name_stripping",
        description=(
            "Drop cluster wording for scorer-facing cadence labels when no within-cluster "
            "event count is available."
        ),
        apply=_gold_policy_cluster_name_stripping,
        example="clusters every 4 weeks",
        expected="1 per 4 week",
    ),
    _gold_normalization_policy_rule(
        rule_id="gold_normalization_policy.vague_weekday_cadence",
        description="Map vague multi-weekday cadence to Gan's coarse multiple-per-week label.",
        apply=_gold_policy_vague_weekday_cadence,
        example="most weekdays",
        expected="multiple per week",
    ),
    _gold_normalization_policy_rule(
        rule_id="gold_normalization_policy.bimonthly",
        description="Map bare bimonthly/bi-monthly to Gan's every-two-month convention.",
        apply=_gold_policy_bimonthly,
        example="bimonthly",
        expected="1 per 2 month",
    ),
    _gold_normalization_policy_rule(
        rule_id="gold_normalization_policy.vague_quantity_explicit_denominator",
        description=(
            "Map vague count words to Gan coarse labels only when the denominator is explicit."
        ),
        apply=_gold_policy_vague_quantity_explicit_denominator,
        example="several per week",
        expected="multiple per week",
    ),
    _gold_normalization_policy_rule(
        rule_id="gold_normalization_policy.period_dialect_and_shorthand",
        description=(
            "Expand period dialects and terse seizure-frequency shorthand when count and "
            "period are preserved."
        ),
        apply=_gold_policy_period_dialect_and_shorthand,
        example="q1-2d",
        expected="1 per 1 to 2 day",
    ),
    _gold_normalization_policy_rule(
        rule_id="gold_normalization_policy.cluster_syntax_grammar",
        description=(
            "Normalize source-near cluster primitives into Gan cluster syntax when cadence "
            "and per-cluster load are already present."
        ),
        apply=_gold_policy_cluster_syntax_grammar,
        example="2 cluster days per month, 6 seizures per cluster day",
        expected="2 cluster per month, 6 per cluster",
    ),
    _gold_normalization_policy_rule(
        rule_id="gold_normalization_policy.single_total_window",
        description="Rephrase one selected total count and explicit window into Gan syntax.",
        apply=_gold_policy_single_total_window,
        example="7 in past 3 months",
        expected="7 per 3 month",
    ),
)
