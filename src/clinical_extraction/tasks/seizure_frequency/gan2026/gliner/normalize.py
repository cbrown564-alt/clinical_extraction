"""Format-only normalisation of GLiNER value spans into the expanded schema's shapes.

This step is deliberately not semantic: it reads the number words, ranges, bounds and
time units written in one span. It never converts units, sums counts, infers a
window, or chooses between findings. A span it cannot read becomes ``verbatim``,
which the lenient finding score treats as not comparable rather than wrong.
"""

from __future__ import annotations

import re
from typing import Any

NORMALIZER = "gliner_span_format_v1"

WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "once": 1,
    "single": 1,
    "two": 2,
    "twice": 2,
    "three": 3,
    "thrice": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
}
UNITS = {
    "second": "second",
    "minute": "minute",
    "hour": "hour",
    "day": "day",
    "daily": "day",
    "night": "day",
    "nightly": "day",
    "week": "week",
    "weekly": "week",
    "month": "month",
    "monthly": "month",
    "quarter": "quarter",
    "quarterly": "quarter",
    "year": "year",
    "yearly": "year",
    "annual": "year",
    "annually": "year",
}
FILLER = {"per", "every", "each", "a", "an", "the", "in", "over", "last", "past", "this", "one"}
# Lexical cadence words with a fixed stated length; no unit conversion is applied.
CADENCE = {"fortnight": (2, "week"), "fortnightly": (2, "week")}
RELATION = {
    "at least": "at_least",
    "minimum of": "at_least",
    "≥": "at_least",
    ">=": "at_least",
    "more than": "more_than",
    ">": "more_than",
    "at most": "at_most",
    "up to": "at_most",
    "no more than": "at_most",
    "≤": "at_most",
    "<=": "at_most",
    "less than": "less_than",
    "fewer than": "less_than",
    "<": "less_than",
}
_NUMBER = r"\d+(?:\.\d+)?|" + "|".join(sorted(WORDS, key=len, reverse=True))
_TOKEN = re.compile(rf"(?<![\w.])({_NUMBER})(?![\w])", re.I)
_RANGE = re.compile(rf"(?<![\w.])({_NUMBER})\s*(?:-|–|—|to|or)\s*({_NUMBER})(?![\w])", re.I)


def _value(token: str) -> float:
    token = token.lower()
    return float(WORDS[token]) if token in WORDS else float(token)


def _integral(value: float) -> int | float:
    return int(value) if value == int(value) else value


def _relation(text: str) -> str | None:
    lowered = text.lower()
    for phrase in sorted(RELATION, key=len, reverse=True):
        pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)" if phrase[0].isalpha() else re.escape(phrase)
        if re.search(pattern, lowered):
            return RELATION[phrase]
    return None


def quantity(span: str | None, *, integer: bool = True) -> dict[str, Any] | None:
    """Number, range or bound written in ``span``; ``verbatim`` when unreadable."""
    if span is None or not span.strip():
        return None
    text = span.strip()
    cast = (lambda v: int(round(v))) if integer else _integral
    ranged = _RANGE.search(text)
    relation = _relation(text)
    if ranged:
        low, high = sorted((_value(ranged[1]), _value(ranged[2])))
        if low > 0 and low != high:
            value: dict[str, Any] = {"kind": "range", "lower": cast(low), "upper": cast(high)}
            if relation:
                return {"kind": "bound", "relation": relation, "value": value}
            return value
    numbers = [_value(m[1]) for m in _TOKEN.finditer(text)]
    # "a"/"an" only count when nothing more specific is written.
    specific = [m[1] for m in _TOKEN.finditer(text) if m[1].lower() not in ("a", "an")]
    if specific:
        numbers = [_value(specific[0])]
    if len(numbers) >= 1 and numbers[0] > 0:
        number = cast(numbers[0])
        if relation:
            return {"kind": "bound", "relation": relation, "value": number}
        return {"kind": "number", "value": number}
    return {"kind": "verbatim", "text": text}


def duration(span: str | None) -> dict[str, Any] | None:
    """Number or range of one written time unit; ``verbatim`` when unreadable."""
    if span is None or not span.strip():
        return None
    text = span.strip()
    lowered = text.lower()
    for word, (value, unit) in CADENCE.items():
        if re.search(rf"(?<!\w){word}(?!\w)", lowered):
            return {"kind": "number", "value": value, "unit": unit}
    # A span such as "4 per 2 weeks" keeps only the part after its last "per"/"every".
    marker = list(re.finditer(r"(?<!\w)(?:per|every|each|a|/)(?!\w)", lowered))
    if marker and _TOKEN.search(re.sub(r"(?<!\w)an?(?!\w)", " ", lowered[: marker[-1].start()])):
        text = text[marker[-1].end() :].strip() or text
        lowered = text.lower()
    units = []
    for word in re.findall(r"[a-z]+", lowered):
        base = word if word in UNITS else word[:-1] if word[:-1] in UNITS else None
        if base:
            units.append(UNITS[base])
    if len(set(units)) != 1:
        return {"kind": "verbatim", "text": text}
    unit = units[0]
    amount = quantity(text, integer=False)
    if amount is None or amount["kind"] == "verbatim":
        # A bare unit ("per month", "weekly") is one unit; vague wording stays verbatim.
        rest = re.sub(
            r"[a-z]+",
            lambda m: "" if m[0] in FILLER or m[0] in UNITS or m[0][:-1] in UNITS else m[0],
            lowered,
        )
        if rest.strip(" ,./-"):
            return {"kind": "verbatim", "text": text}
        return {"kind": "number", "value": 1, "unit": unit}
    if amount["kind"] == "bound" and isinstance(amount["value"], dict):
        return {"kind": "verbatim", "text": text}
    return {**amount, "unit": unit}
