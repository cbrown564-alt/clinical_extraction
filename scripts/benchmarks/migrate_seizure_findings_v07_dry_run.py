# ruff: noqa: E501  (long regular-expression vocabularies are kept on one line each)
"""Dry-run migration of v0.6 seizure-finding annotations to the simplified v0.7 conventions.

Reads a local v0.6 annotation JSONL (default: the merged dev750 working candidate), applies
the v0.7 scope, default and representation rules mechanically, and writes a report, the
migrated candidate and a manual-mapping list to a new local output directory. Nothing is
overwritten; the v0.6 inputs remain the reference for all saved artifacts.

Paths containing ``test450`` receive aggregate counts only: no per-record output, no phrase
lists and no source quotations are written, in line with the holdout policy.
"""

from __future__ import annotations

import argparse
import collections
import copy
import json
import re
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r8 as r8

GUIDE_VERSION = "seizure_finding_annotation_v0.7"
DEFAULT_INPUT = Path(
    "runs/seizure_finding_annotation_v0_2/agy_gemini38_high/reviews/codex/pro_final/"
    "working750_candidate.jsonl"
)
DEFAULT_QUESTIONS = DEFAULT_INPUT.with_name("CB_QUESTIONS.jsonl")
DEFAULT_SOURCES = Path("runs/seizure_finding_annotation_v0_2/agy_gemini38_high/sources.jsonl")
SENTENCE_END = re.compile(r"(?<=[.!?;])\s+|\n+")
DEFAULT_OUT = Path(
    "runs/seizure_finding_annotation_v0_2/agy_gemini38_high/reviews/codex/v07_dry_run"
)

DISSOLVED_GROUPS = {
    "Aura and symptom versus event boundary",
    "Event identity and overlapping descriptions",
    "Counting unit and event membership",
    "Device signals versus clinical events",
    "Latest cluster representation",
    "Average versus approximation",
}

NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "once": 1,
    "single": 1,
    "two": 2,
    "twice": 2,
    "couple": 2,
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
}
UNIT_WORDS = {
    "d": "day",
    "day": "day",
    "days": "day",
    "daily": "day",
    "night": "day",
    "nights": "day",
    "nightly": "day",
    "wk": "week",
    "wks": "week",
    "w": "week",
    "week": "week",
    "weeks": "week",
    "weekly": "week",
    "fortnight": "fortnight",
    "fortnightly": "fortnight",
    "mo": "month",
    "m": "month",
    "month": "month",
    "months": "month",
    "monthly": "month",
    "yr": "year",
    "y": "year",
    "year": "year",
    "years": "year",
    "yearly": "year",
    "annually": "year",
    "quarter": "quarter",
    "quarterly": "quarter",
}
NUM = r"(?:\d+(?:\.\d+)?|a|an|one|once|single|two|twice|couple|three|thrice|four|five|six|seven|eight|nine|ten|eleven|twelve)"
RANGE = rf"(?P<lo>{NUM})(?:\s*(?:-|–|to|or)\s*(?P<hi>{NUM}))?"
UNIT = r"(?P<unit>d|days?|nights?|wks?|w|weeks?|mo|m|months?|yrs?|y|years?|quarters?|fortnights?)"
APPROX = r"(?:about|around|roughly|approximately|approx\.?|~|on average|an average of|estimated(?: at)?)?\s*"
VAGUE = r"(?P<vague>several|a few|few|multiple|many|numerous|dozens|couple of|handful of)"

CADENCE_START = (
    r"(?=(?:about|around|roughly|approximately|every|each|q\d|\d|once|twice|"
    r"one|two|three|four|five|six|seven|eight|nine|ten|daily|weekly|monthly|nightly|yearly|several|few|multiple|many)\b)"
)
# Up to four plain words naming the event (e.g. "an absence seizure", "generalised convulsions occur"),
# provided none of them introduces a qualifier that changes the claim.
SUBJECT_PREFIX = re.compile(rf"^(?P<prefix>(?:[a-z][a-z-]*\s+){{1,5}}?){CADENCE_START}")
PREFIX_BLOCKERS = re.compile(
    r"\b(with|of|periods?|pattern|only|when|no|not|without|up to|at least|more than|less than|fewer than|"
    r"at most|maximum|minimum|longest|shortest|free|between|from|since|until|after|before)\b"
)
TRAILING_QUALIFIER = re.compile(
    r"\s+(?:on average|or so|or thereabouts|at present|currently|approximately)$"
)
ON_A_BASIS = re.compile(r"^on an?\s+(daily|weekly|monthly|nightly|yearly|fortnightly)\s+basis$")
BOUND_PREFIX = re.compile(
    r"^(?P<bound>up to|no more than|at most|≤|<=|at least|≥|>=|more than|over)\s*"
)
BOUND_RELATION = {
    "up to": "at_most",
    "no more than": "at_most",
    "at most": "at_most",
    "≤": "at_most",
    "<=": "at_most",
    "at least": "at_least",
    "≥": "at_least",
    ">=": "at_least",
    "more than": "more_than",
    "over": "more_than",
}
SEIZURE_DAYS = [
    re.compile(rf"^{APPROX}(?:seizure[- ]days?:?\s*)?(?P<lo>{NUM})\s*/\s*\d+\s+(?P<tail>.+)$"),
    re.compile(
        rf"^{APPROX}(?P<lo>{NUM})\s+(?:seizure[- ])?(?:days?|nights?|mornings?)\s+(?:per|a|each|every)\s+{UNIT}$"
    ),
    re.compile(
        rf"^{APPROX}(?:occurring\s+)?(?:on\s+)?{RANGE}\s+(?:days?|nights?|mornings?)\s+(?:of\s+the|per|a|each|every)\s+{UNIT}$"
    ),
]
INTERVAL = re.compile(
    rf"(?:median\s+)?(?:inter-?seizure\s+)?intervals?\s+(?:≈|of|ranging|around|about|approximately|~)?\s*{RANGE}\s+{UNIT}\b"
)
CLUSTER_WITH_SIZE = [
    re.compile(
        rf"^{APPROX}(?P<simple>daily|weekly|monthly|quarterly|yearly|nightly|fortnightly)\s+clusters?,?\s*"
        rf"(?:typically|usually|often|of|with|each)?\s*(?:of\s+)?{RANGE}\s*(?:seizures?|events?|episodes?|absences?|convulsions?)?(?P<tail>.*)$"
    ),
    re.compile(
        rf"^{APPROX}(?P<simple>daily|weekly|monthly|quarterly|yearly|nightly|fortnightly),?\s*{RANGE}\s+per\s+cluster$"
    ),
]
CLUSTER_SPACING = re.compile(
    rf"(?:in\s+)?clusters?,?\s*(?:generally|typically|usually)?\s*spaced\s+{RANGE}\s+{UNIT}\s+apart"
)
INTERVAL_ONLY = re.compile(
    r"^(?:may|can|could|might)\s+(?:occasionally\s+|sometimes\s+)?(?:go|manage|have)\b.*\bwithout\b"
)
AMBIGUOUS_CADENCE = re.compile(r"\b(bimonthly|biweekly|biannual\w*)\b")
LEADING_VERB = re.compile(
    r"^(?:(?:now|currently|still|typically|usually|often|generally|reported|described as)\s+)?"
    r"(?:occurring|occurs?|happening|happens?|recurring|recurs?)\s+(?:on\s+)?"
)
CONDITION_ONLY = re.compile(
    r"^(?:occurring|occur|happen\w*|seizures happen|only|exclusively|predominantly|mainly|mostly|when|"
    r"cluster around|clear peri-?menstrual|associated with|highly cyclical|nocturnal clustering pattern|"
    r"mostly|usually|typically|often)\b"
)
FREQUENCY_CONTENT = re.compile(
    r"(\d|\b(per|every|each|daily|weekly|monthly|nightly|yearly|annual\w*|times|once|twice|occasion\w*|rare\w*|"
    r"frequen\w*|infrequent\w*|intermittent\w*|sporadic\w*|most|some|several|few|many|numerous|multiple|dozens|"
    r"couple|unknown|documented|quantif\w*|unclear|uncertain|increas\w*|reduc\w*|decreas\w*|more|less|fewer|"
    r"improv\w*|worse\w*|deteriorat\w*|escalat\w*|fell|rose|stable|unchanged|persist\w*|continu\w*|ongoing|"
    r"variable|fluctuat\w*|trend|days?|weeks?|months?|years?|nights?|mornings?|free|q\d|q(?:one|two|three)|/wk|/mo|/yr|"
    r"one|two|three|four|five|six|seven|eight|nine|ten|single|higher|lower|spike|surge|diminish\w*|lessen\w*|"
    r"tail\w* off|interval\w*|uncommon|sparse|scattered|closer together|exacerbat\w*)\b)"
)

CADENCE_PATTERNS = [
    re.compile(
        rf"^{APPROX}(?P<simple>daily|weekly|monthly|yearly|annually|nightly|fortnightly|quarterly)$"
    ),
    re.compile(rf"^{APPROX}every\s+(?:other|second)\s+{UNIT}$"),
    re.compile(rf"^{APPROX}(?:once\s+)?(?:every|each)\s+{RANGE}\s+(?:of\s+)?{UNIT}$"),
    re.compile(rf"^{APPROX}(?:every|each)\s+{UNIT}(?:\s+or\s+(?P<alt>two|so))?$"),
    re.compile(
        rf"^{APPROX}{RANGE}\s*(?:times?|seizures?|events?|episodes?|x)?\s*(?:per|a|an|each|every|/)\s*{UNIT}$"
    ),
    re.compile(
        rf"^{APPROX}{RANGE}\s*(?:seizures?|events?|episodes?)?\s+(?:per|a|an|each|every)\s+{UNIT}\s+or\s+(?P<alt>two|so)$"
    ),
    re.compile(rf"^{APPROX}{RANGE}\s*/\s*{UNIT}$"),
    re.compile(rf"^{APPROX}q\s?{RANGE}\s?{UNIT}$"),
    re.compile(
        rf"^{APPROX}{VAGUE}\s*(?:times?|seizures?|events?|episodes?)?\s*(?:per|a|an|each|every)\s+{UNIT}$"
    ),
    re.compile(
        rf"^{APPROX}(?:once|twice)\s+(?:or|to)\s+(?:twice|three times|thrice)\s+(?:per|a|an|each|every)\s+{UNIT}$"
    ),
]

CLOSED_VOCAB: list[tuple[str, re.Pattern[str]]] = [
    ("variable", re.compile(r"\b(variable|variability|fluctuat\w*|varies|irregular)\b")),
    (
        "unknown",
        re.compile(
            r"\b(unknown|not documented|undocumented|not tracked|not reliably|no reliable|unable to (?:quantify|provide)|could not|cannot|difficult to quantify|hard to quantify|unquantified|not (?:been )?(?:quantified|recorded|specified)|uncertain|unclear|not clear|not available)\b"
        ),
    ),
    (
        "increased",
        re.compile(
            r"\b(increas\w*|more frequent\w*|more often|more episodes|more events|more seizures|escalat\w*|worsen\w*|deteriorat\w*|rose|risen|rise|higher frequency|higher|clear increase|upward trend|exacerbat\w*|spike|surge|closer together|shorter inter-event intervals)\b|^more$"
        ),
    ),
    (
        "decreased",
        re.compile(
            r"\b(reduc\w*|decreas\w*|less frequent\w*|less often|less commonly|fewer|fell|fallen|improv\w*|settled|thin(?:ned)? out|longer seizure-free intervals|lower frequency|declin\w*|rarer|more rarely|markedly infrequent|downward trend|diminish\w*|lessen\w*|tail(?:ed)? off|intervals? (?:between events )?lengthened)\b|^less$"
        ),
    ),
    (
        "unchanged",
        re.compile(
            r"\b(unchanged|not altered|no change|no significant change|stable|remains? (?:the )?same|persisted without|little alteration|no clear progression|without major change|similar(?: pattern| frequency)?|remain(?:s|ed)? at|not chang\w*|has not coincided with any change)\b"
        ),
    ),
    (
        "rare",
        re.compile(
            r"^(?:very\s+|only\s+|appears?\s+|remains?\s+|still\s+|now\s+|currently\s+)*(rare(?:ly)?|very infrequent(?:ly)?|seldom|exceptional(?:ly)?|relatively low frequency|low[- ]frequency)\b"
        ),
    ),
    (
        "frequent",
        re.compile(
            r"^(?:very\s+|now\s+)?(frequent(?:ly)?|(?:on\s+)?most (?:days|nights|weeks|weekdays|shifts|mornings)|near-daily|nearly daily|almost daily|near daily|multiple|numerous|many|frequent short episodes)\b"
        ),
    ),
    (
        "occasional",
        re.compile(
            r"^(?:only\s+|appears?\s+|remains?\s+|still\s+|now\s+|approximately\s+|roughly\s+)*(occasional(?:ly)?|infrequent(?:ly)?|intermittent(?:ly)?|sporadic(?:ally)?|sometimes|at times|on occasion|on some (?:occasions|days|nights|mornings|evenings)|from time to time|episodic|periodic(?:ally)?|now and then|the odd occurrence|(?:once\s+)?every (?:few|several) (?:days|weeks|months|years)|spaced several|uncommon|sparse|scattered|infrequency|some)\b"
        ),
    ),
]
OCCURRENCE_ONLY = re.compile(
    r"^(?:(?:have|has|had)\s+)?(recurrent|ongoing.*|continu\w*|persist\w*|relapse\w*|history of.*|.*history|"
    r"previously (?:experiencing|suffered from|had).*|"
    r"enduring seizure profile|together with .*|developed .*|experience[sd]?|can occur|captured|breakthrough .*|"
    r"remains? (?:seizure|event)[- ]?free.*|seizures?|has (?:had|suffered).*|suffers? from.*|"
    r"has (?:been )?(?:diagnosed|known).*|active|present|noted|typical pattern|"
    r"(?:no|not|without|denies|denied|no clear|there have been no)\b.*(?:cluster\w*|pattern|predominance|periodicity))$"
)
ALTERNATIVE_COUNT = re.compile(
    rf"^{APPROX}{RANGE}\s+(?:[\w\s-]*?\b)?(?:seizures?|events?|episodes?|spasms?|attacks?|jerks?|absences?|"
    rf"convulsions?|clonic|mal|gtcs?|tc|automatisms?|myoclonus|spells?)\b(?P<tail>.*)$"
)
ATTRIBUTION_ONLY = re.compile(
    r"^(reported|witnessed|documented|recorded|noted|observed|captured|described|self-reported|patient-reported|"
    r"carer-reported|partner-reported|by report|diary entries|app-recorded entries|recorded (?:seizures|events) only|"
    r"(?:reported|witnessed|documented|recorded|noted|observed|confirmed|corroborated) (?:by|at|in|on|during|from) .*|"
    r"(?:per|from|according to) (?:the )?(?:patient|carer|partner|diary|log|app|family|school|staff).*|"
    r"(?:patient|carer|partner|family|diary|log|app|staff|colleague)[- ]?(?:reported|witnessed|recorded|documented|noted).*)$"
)
HEDGE_PREFIX = re.compile(
    r"^(typically|usually|often|mostly|mainly|predominantly|sometimes|occasionally|generally|"
    r"frequently|tend(?:s|ing)? to|particularly|especially)\b[,:]?\s*(?P<rest>.*)$"
)


def to_number(token: str) -> float:
    token = token.lower()
    if token in NUMBER_WORDS:
        return NUMBER_WORDS[token]
    return float(token)


def duration(lo: float, hi: float | None, unit: str) -> dict[str, Any]:
    if unit == "fortnight":
        lo, hi, unit = lo * 2, (hi * 2 if hi is not None else None), "week"
    if hi is None or hi == lo:
        return {"type": "number", "value": lo, "unit": unit}
    return {"type": "range", "lower": lo, "upper": hi, "unit": unit}


def quantity(lo: float, hi: float | None) -> dict[str, Any]:
    if hi is None or hi == lo:
        return {"type": "number", "value": lo}
    return {"type": "range", "lower": lo, "upper": hi}


def bounded(relation: str, value: dict[str, Any]) -> dict[str, Any]:
    inner: Any = value["value"] if value["type"] == "number" else value
    return {"type": "bound", "relation": relation, "value": inner}


def parse_cadence(phrase: str) -> dict[str, Any] | None:
    """Return an R7 rate measurement for a plain-reading cadence phrase, else None."""
    text = phrase.strip().lower().rstrip(".").strip("“”\"'")
    text = TRAILING_QUALIFIER.sub("", text)
    relation: str | None = None
    bound = BOUND_PREFIX.match(text)
    if bound:
        relation = BOUND_RELATION[bound.group("bound")]
        text = text[bound.end() :]
    basis = ON_A_BASIS.match(text)
    if basis:
        text = basis.group(1)
    rate = _match_cadence(text)
    if rate is None:
        prefixed = SUBJECT_PREFIX.match(text)
        if prefixed and not PREFIX_BLOCKERS.search(prefixed.group("prefix")):
            rate = _match_cadence(text[prefixed.end("prefix") :])
    if rate is None:
        interval = INTERVAL.search(text)
        if interval:
            lo = to_number(interval.group("lo"))
            hi = to_number(interval.group("hi")) if interval.group("hi") else None
            rate = {
                "type": "rate",
                "count": quantity(1, None),
                "per": duration(lo, hi, UNIT_WORDS[interval.group("unit")]),
            }
    if rate is not None and relation is not None:
        rate["count"] = bounded(relation, rate["count"])
    return rate


def _match_cadence(text: str) -> dict[str, Any] | None:
    for index, pattern in enumerate(CADENCE_PATTERNS):
        match = pattern.match(text)
        if not match:
            continue
        groups = match.groupdict()
        if groups.get("simple"):
            unit = UNIT_WORDS[groups["simple"]]
            return {"type": "rate", "count": quantity(1, None), "per": duration(1, None, unit)}
        unit = UNIT_WORDS[groups["unit"]]
        if index == 1:
            return {"type": "rate", "count": quantity(1, None), "per": duration(2, None, unit)}
        if index == 3:
            hi = 2.0 if groups.get("alt") == "two" else None
            return {"type": "rate", "count": quantity(1, None), "per": duration(1, hi, unit)}
        if index == 8:
            return {
                "type": "rate",
                "count": {"type": "qualitative", "quantity": groups["vague"]},
                "per": duration(1, None, unit),
            }
        if index == 9:
            lo = (
                1.0
                if text.startswith(("about", "around", "roughly", "approximately"))
                or "once" in text.split(" or ")[0]
                else 2.0
            )
            hi = 3.0 if "three" in text or "thrice" in text else 2.0
            return {"type": "rate", "count": quantity(lo, hi), "per": duration(1, None, unit)}
        lo = to_number(groups["lo"])
        hi = to_number(groups["hi"]) if groups.get("hi") else None
        if index == 2:
            return {"type": "rate", "count": quantity(1, None), "per": duration(lo, hi, unit)}
        if index == 5:
            return {"type": "rate", "count": quantity(lo, hi), "per": duration(1, 2, unit)}
        if index == 7:
            return {"type": "rate", "count": quantity(1, None), "per": duration(lo, hi, unit)}
        return {"type": "rate", "count": quantity(lo, hi), "per": duration(1, None, unit)}
    return None


def map_qualitative(phrase: str) -> tuple[str, dict[str, Any] | None]:
    """Classify a v0.6 qualitative phrase: rate, closed-vocabulary value, excluded or manual."""
    original = phrase.strip().lower().rstrip(".").strip("“”\"'")
    text = LEADING_VERB.sub("", original)
    measurement: dict[str, Any]
    if AMBIGUOUS_CADENCE.search(text):
        return "manual_mapping", None
    for index, pattern in enumerate(SEIZURE_DAYS):
        days = pattern.match(text)
        if not days:
            continue
        lo = to_number(days.group("lo"))
        hi = to_number(days.group("hi")) if index == 2 and days.group("hi") else None
        if index == 0:
            measurement = {
                "type": "count",
                "count": quantity(lo, None),
                "_period_hint": days.group("tail").strip(),
            }
        else:
            unit = UNIT_WORDS[days.group("unit")]
            measurement = {
                "type": "rate",
                "count": quantity(lo, hi),
                "per": duration(1, None, unit),
            }
        measurement["_event_label"] = "seizure days"
        return "converted_to_seizure_days", measurement
    spacing = CLUSTER_SPACING.search(text)
    if spacing:
        lo = to_number(spacing.group("lo"))
        hi = to_number(spacing.group("hi")) if spacing.group("hi") else None
        return "converted_to_cluster", {
            "type": "cluster",
            "rate": {
                "count": quantity(1, None),
                "per": duration(lo, hi, UNIT_WORDS[spacing.group("unit")]),
            },
        }
    for pattern in CLUSTER_WITH_SIZE:
        cluster = pattern.match(text)
        if not cluster:
            continue
        unit = UNIT_WORDS[cluster.group("simple")]
        lo = to_number(cluster.group("lo"))
        hi = to_number(cluster.group("hi")) if cluster.group("hi") else None
        size: dict[str, Any] = quantity(lo, hi)
        tail = cluster.groupdict().get("tail") or ""
        if re.match(r"^\s*or more\b", tail):
            size = bounded("at_least", size)
        return "converted_to_cluster", {
            "type": "cluster",
            "rate": {"count": quantity(1, None), "per": duration(1, None, unit)},
            "seizures_per_cluster": size,
        }
    if INTERVAL_ONLY.match(text):
        return "excluded_interval_only", None
    rate = parse_cadence(text)
    if rate is not None:
        return "converted_to_rate", rate
    alternative = ALTERNATIVE_COUNT.match(text)
    if (
        alternative
        and alternative.group("hi")
        and not re.search(r"\b(per|every|each|a week|a month|a day|a year)\b", text)
    ):
        lo, hi = to_number(alternative.group("lo")), to_number(alternative.group("hi"))
        measurement = {"type": "count", "count": quantity(min(lo, hi), max(lo, hi))}
        tail = alternative.group("tail").strip(" ,")
        if tail:
            measurement["_period_hint"] = tail
        return "converted_to_count_range", measurement
    for value, pattern in CLOSED_VOCAB:
        if pattern.search(text):
            return "closed_vocabulary", {"type": "qualitative", "frequency": value}
    if OCCURRENCE_ONLY.match(original):
        return "excluded_occurrence_only", None
    if CONDITION_ONLY.match(original):
        return "excluded_condition_only", None
    if not FREQUENCY_CONTENT.search(original):
        return "excluded_no_frequency_content", None
    return "manual_mapping", None


def migrate_condition(condition: str | None) -> tuple[str, str | None]:
    if not condition:
        return "none", None
    text = condition.strip()
    if ATTRIBUTION_ONLY.match(text.lower()):
        return "dropped_attribution", None
    hedge = HEDGE_PREFIX.match(text)
    if hedge:
        rest = hedge.group("rest").strip(" ,;")
        if not rest:
            return "dropped_hedge", None
        if ATTRIBUTION_ONLY.match(rest.lower()):
            return "dropped_attribution", None
        return "hedge_stripped", rest
    if re.search(r"\b(report|witness|document|record|noted|observ|diary|corroborat)", text, re.I):
        return "manual_attribution_mixed", text
    return "kept", text


def strip_flags(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            key: strip_flags(value)
            for key, value in obj.items()
            if key not in {"approximate", "lower_inclusive", "upper_inclusive"}
        }
    if isinstance(obj, list):
        return [strip_flags(item) for item in obj]
    return obj


def trim_evidence(span: str, finding: dict[str, Any], hint: str) -> str:
    """Shortest sentence run inside the span that carries the measurement (guide v0.7)."""
    pieces = [part for part in SENTENCE_END.split(span) if part and part.strip()]
    sentences: list[str] = []
    cursor = 0
    for piece in pieces:
        start = span.find(piece, cursor)
        if start < 0:
            return span
        sentences.append(span[start : start + len(piece)])
        cursor = start + len(piece)
    if len(sentences) <= 1:
        return span
    measurement = finding["measurement"]
    tokens: list[str] = [hint.lower()] if hint else []

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"time", "quantity", "frequency"} and isinstance(item, str):
                    tokens.append(item.lower())
                elif key in {"value", "lower", "upper"} and isinstance(item, int | float):
                    number = int(item) if float(item).is_integer() else item
                    tokens.append(str(number))
                    tokens.extend(w for w, n in NUMBER_WORDS.items() if n == number and len(w) > 2)
                else:
                    collect(item)

    collect(measurement)
    collect(finding.get("period") or {})
    scores = []
    for index, sentence in enumerate(sentences):
        low = sentence.lower()
        score = sum(1 for token in tokens if token and token in low)
        scores.append((score, index))
    best_score, best = max(scores, key=lambda pair: (pair[0], -pair[1]))
    if best_score == 0:
        return span
    label = finding["event"]["type"].lower()
    start = best
    if label not in sentences[best].lower() and best > 0:
        start = best - 1
    begin = span.find(sentences[start])
    end = span.find(sentences[best], begin) + len(sentences[best])
    return span[begin:end]


def finding_key(finding: dict[str, Any]) -> str:
    keyed = {
        "event": {k: str(v).lower() for k, v in finding["event"].items()},
        "measurement": finding["measurement"],
        "timing": finding["timing"],
        "condition": (finding.get("condition") or "").lower(),
        "period": (finding.get("period") or {}).get("time", "").lower(),
    }
    return json.dumps(keyed, sort_keys=True)


def migrate_record(
    record: dict[str, Any],
    question_groups: dict[tuple[str, str], str],
    tally: collections.Counter[str],
    manual: list[dict[str, Any]],
    conversions: list[dict[str, Any]],
    excluded: list[dict[str, Any]],
    source_text: str | None = None,
) -> dict[str, Any]:
    source_id = str(record["source_id"])
    findings: list[dict[str, Any]] = []
    dropped_ids: set[str] = set()
    notes: list[str] = []
    manual_ids: list[str] = []
    for original in record["findings"]:
        finding = copy.deepcopy(original)
        measurement = finding["measurement"]
        kind = measurement["type"]
        hint = measurement.get("frequency", "") if kind == "qualitative" else ""
        tally[f"before.measurement.{kind}"] += 1
        tally[f"before.timing.{finding['timing']}"] += 1
        if finding.get("condition"):
            tally["before.with_condition"] += 1
        if measurement.get("approximate"):
            tally["before.approximate_flag"] += 1
        if (
            kind == "seizure_free"
            and not measurement.get("duration")
            and not measurement.get("since")
        ):
            tally["dropped.bare_seizure_free"] += 1
            dropped_ids.add(finding["id"])
            continue
        if finding["timing"] == "future":
            tally["dropped.future_timing"] += 1
            dropped_ids.add(finding["id"])
            continue
        if kind == "cluster" and not any(
            measurement.get(k) for k in ("rate", "count", "seizures_per_cluster")
        ):
            tally["dropped.unquantified_cluster"] += 1
            dropped_ids.add(finding["id"])
            continue
        if kind == "qualitative":
            outcome, replacement = map_qualitative(measurement["frequency"])
            tally[f"qualitative.{outcome}"] += 1
            if outcome.startswith("excluded_"):
                dropped_ids.add(finding["id"])
                excluded.append(
                    {
                        "source_id": source_id,
                        "finding_id": finding["id"],
                        "outcome": outcome,
                        "phrase": measurement["frequency"],
                    }
                )
                continue
            if outcome == "manual_mapping":
                manual.append(
                    {
                        "source_id": source_id,
                        "finding_id": finding["id"],
                        "phrase": measurement["frequency"],
                    }
                )
                notes.append(
                    f"MANUAL {finding['id']}: qualitative phrase {measurement['frequency']!r}"
                )
                manual_ids.append(finding["id"])
                finding["measurement"] = {"type": "qualitative", "frequency": "unknown"}
            elif replacement is not None:
                hint = replacement.pop("_period_hint", None)
                if hint and not finding.get("period"):
                    finding["period"] = {"time": hint}
                label = replacement.pop("_event_label", None)
                if label:
                    finding["event"]["type"] = label
                if outcome.startswith("converted_to"):
                    conversions.append(
                        {
                            "source_id": source_id,
                            "finding_id": finding["id"],
                            "phrase": measurement["frequency"],
                            "measurement": replacement,
                        }
                    )
                finding["measurement"] = replacement
        if finding["timing"] == "unclear":
            tally["timing.unclear_to_current"] += 1
            finding["timing"] = "current"
        condition_outcome, condition = migrate_condition(finding.get("condition"))
        tally[f"condition.{condition_outcome}"] += 1
        if condition is None:
            finding.pop("condition", None)
        else:
            finding["condition"] = condition
            if condition_outcome == "manual_attribution_mixed":
                notes.append(f"CONDITION {finding['id']}: check attribution in {condition!r}")
        if finding["event"].get("seizure_status") in (None, "unspecified"):
            tally["status.unspecified_to_stated"] += 1
            finding["event"]["seizure_status"] = "stated"
        derived = r8.derive_scope(finding["event"]["type"])
        if finding["event"].get("scope") != derived:
            tally["scope.rederived"] += 1
        finding["event"]["scope"] = derived
        finding = strip_flags(finding)
        if source_text is not None:
            trimmed = trim_evidence(finding["evidence"], finding, hint)
            if trimmed != finding["evidence"] and trimmed in source_text:
                tally["evidence.trimmed"] += 1
                finding["evidence"] = trimmed
        findings.append(finding)

    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for finding in findings:
        key = finding_key(finding)
        if key in seen:
            tally["merged.duplicate_after_migration"] += 1
            dropped_ids.add(finding["id"])
            continue
        seen.add(key)
        merged.append(finding)

    retained_reasons: list[str] = []
    for issue in record.get("issues", []):
        group = question_groups.get((source_id, issue["id"]), "ungrouped")
        linked = set(issue.get("finding_ids", []))
        if group in DISSOLVED_GROUPS:
            tally[f"issues.dissolved_by_rule.{group}"] += 1
        elif linked and linked <= dropped_ids:
            tally[f"issues.dissolved_findings_dropped.{group}"] += 1
        else:
            tally[f"issues.retained_for_review.{group}"] += 1
            retained_reasons.append(f"{issue['id']}: {issue['question']}")

    if manual_ids:
        retained_reasons.append(
            "manual mapping needed for " + ", ".join(manual_ids) + " (see notes)"
        )
    out: dict[str, Any] = {
        "guide_version": GUIDE_VERSION,
        "source_id": str(record["source_id"]),
        "source_row_index": record["source_row_index"],
        "source_sha256": record["source_sha256"],
        "annotation_state": "needs_review" if retained_reasons else "complete",
        "document_dates": strip_flags(record.get("document_dates", [])),
        "findings": merged,
    }
    if retained_reasons:
        out["review_reason"] = " | ".join(retained_reasons)
    if notes:
        out["notes"] = " | ".join(notes)
    for finding in merged:
        tally[f"after.measurement.{finding['measurement']['type']}"] += 1
        tally[f"after.timing.{finding['timing']}"] += 1
        if finding.get("condition"):
            tally["after.with_condition"] += 1
    tally["after.state." + out["annotation_state"]] += 1
    tally["before.state." + record["annotation_state"]] += 1
    tally["before.findings"] += len(record["findings"])
    tally["after.findings"] += len(merged)
    tally["before.relations"] += sum(
        len(c.get("relations", [])) for c in record.get("finding_context", [])
    )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument(
        "--write-records",
        action="store_true",
        help="Write migrated records for a test450 input (annotation continuation only).",
    )
    args = parser.parse_args()
    aggregate_only = "test450" in str(args.annotations) and not args.write_records
    texts: dict[str, str] = {}
    if args.sources.exists():
        for line in args.sources.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                texts[str(row["source_id"])] = row["note_text"]

    records = [
        json.loads(line) for line in args.annotations.read_text().splitlines() if line.strip()
    ]
    question_groups: dict[tuple[str, str], str] = {}
    if args.questions.exists() and not aggregate_only:
        for line in args.questions.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                question_groups[(str(row["source_id"]), row["issue_id"])] = row["group"]

    tally: collections.Counter[str] = collections.Counter()
    manual: list[dict[str, Any]] = []
    conversions: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    migrated = [
        migrate_record(
            r, question_groups, tally, manual, conversions, excluded, texts.get(str(r["source_id"]))
        )
        for r in records
    ]

    args.out.mkdir(parents=True, exist_ok=True)
    report = {
        "guide_version": GUIDE_VERSION,
        "mode": "aggregate_only" if aggregate_only else "dry_run_with_records",
        "input": str(args.annotations),
        "records": len(records),
        "counts": dict(sorted(tally.items())),
    }
    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    if not aggregate_only:
        with (args.out / "migrated_candidate.jsonl").open("w") as handle:
            for row in migrated:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        phrase_counts = collections.Counter(item["phrase"].lower() for item in manual)
        with (args.out / "manual_mapping.jsonl").open("w") as handle:
            for phrase, count in phrase_counts.most_common():
                ids = sorted(
                    {item["source_id"] for item in manual if item["phrase"].lower() == phrase}
                )
                handle.write(
                    json.dumps(
                        {"phrase": phrase, "count": count, "source_ids": ids}, ensure_ascii=False
                    )
                    + "\n"
                )
        with (args.out / "conversions.jsonl").open("w") as handle:
            for item in conversions:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        with (args.out / "excluded_qualitative.jsonl").open("w") as handle:
            for item in excluded:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
