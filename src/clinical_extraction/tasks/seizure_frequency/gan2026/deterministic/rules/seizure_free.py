from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from datetime import date
from typing import cast

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

WORD_TOKEN = r"[a-z][a-z\-‑–—]*"
SEIZURE_TERMS = (
    r"seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|"
    r"myoclonics?|jerks?|auras?|status epilepticus"
)
QUALIFIED_SEIZURE_TERMS = rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS})"
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
NUMBER_VALUE_TOKEN = rf"(?:multiple|\d+|{NUMBER_WORD_PATTERN})"
NUMBER_TOKEN = (
    rf"(?:{NUMBER_VALUE_TOKEN}(?:\s+(?:to|or)\s+{NUMBER_VALUE_TOKEN}|"
    rf"\s*[-–—]\s*{NUMBER_VALUE_TOKEN})?)"
)


def apply_seizure_free_rules(
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


def _build_seizure_free_candidate(
    match: re.Match[str],
    *,
    rule_id: str,
    label: str = "seizure free for multiple year",
    evidence_group: str | int = 0,
) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.SEIZURE_FREE,
        label=label,
        evidence=_clean_evidence(match.group(evidence_group)),
        rule_id=rule_id,
        rule_group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _build_no_definite_events(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_seizure_free_candidate(
        match,
        rule_id="seizure_free.no_definite_events",
        label="seizure free for multiple month",
    )


def _build_current_control_phrase(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_seizure_free_candidate(
        match,
        rule_id="seizure_free.current_control_phrase",
    )


def _build_seizure_free_since_date(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate | None:
    full_date = cast("Callable[[str], date | None]", context.helper("full_date"))
    clinic_date_func = cast("Callable[[str], date | None]", context.helper("clinic_date"))
    month_span_floor = cast(
        "Callable[[date | None, date | None], int | None]",
        context.helper("month_span_floor"),
    )
    months = month_span_floor(full_date(match.group("date")), clinic_date_func(context.text))
    if months is None:
        return None
    return _build_seizure_free_candidate(
        match,
        rule_id="seizure_free.since_date",
        label=f"seizure free for {months} month",
    )


def _build_absence_for_duration(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    count = match.groupdict().get("count") or match.groupdict().get("over_count")
    return _build_seizure_free_candidate(
        match,
        rule_id="seizure_free.absence_for_duration",
        label=f"seizure free for {_number_token(count)} month",
        evidence_group="evidence",
    )


def _build_no_events_for_duration(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_seizure_free_candidate(
        match,
        rule_id="seizure_free.no_events_for_duration",
        label=(
            f"seizure free for {_number_token(match.group('count'))} "
            f"{_singular_unit(match.group('unit'))}"
        ),
        evidence_group="evidence",
    )


def _build_duration_status(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    count = match.groupdict().get("count") or match.groupdict().get("zero_count")
    unit = match.groupdict().get("unit") or match.groupdict().get("zero_unit")
    return _build_seizure_free_candidate(
        match,
        rule_id="seizure_free.duration_status",
        label=f"seizure free for {_number_token(count)} {_singular_unit(unit)}",
        evidence_group="evidence",
    )


def _build_one_and_half_years(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_seizure_free_candidate(
        match,
        rule_id="seizure_free.one_and_half_years",
        label="seizure free for 1.5 year",
    )


def _build_last_epileptic_event(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    return _build_seizure_free_candidate(
        match,
        rule_id="seizure_free.last_epileptic_event",
        label=f"seizure free for {_number_token(match.group('count'))} month",
        evidence_group="evidence",
    )


def _build_generic_seizure_free(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    count = match.groupdict().get("count")
    unit = match.groupdict().get("unit")
    if count and unit:
        label = f"seizure free for {_number_token(count)} {_singular_unit(unit)}"
    else:
        label = "seizure free for multiple year"
    return _build_seizure_free_candidate(
        match,
        rule_id="seizure_free.generic_duration_or_since",
        label=label,
    )


def _is_generic_seizure_free_distractor(match: re.Match[str], context: ExtractionContext) -> bool:
    evidence = match.group(0).lower()
    following = context.text[match.end() : match.end() + 260].lower()
    surrounding = context.text[max(0, match.start() - 80) : match.end() + 260].lower()
    if "up to" in evidence:
        return True
    if "required period" in evidence or "interval" in evidence:
        return True
    followup_months = re.compile(
        rf"\bfollow-?up\s+in\s+(?:\d+|{NUMBER_WORD_PATTERN})\s+months?\b",
        re.IGNORECASE,
    )
    if followup_months.search(evidence):
        return True
    if re.search(r"\b(?:before experiencing|until)\b", following):
        return True
    if re.search(r"\bhowever\b.{0,120}\b(?:reports?|reported|had|has had)\b", following):
        return True
    if "however" in following and "over the past" in following:
        return True
    if re.search(
        r"\bto\s+(?:\d+|[a-z]+)\s+to\s+(?:\d+|[a-z]+)\s+"
        r"(?:seizures|events|episodes)\b",
        following,
    ):
        return True
    if re.search(r"\bthen\s+(?:developed|sustained|experienced|had)\b", following):
        return True
    return bool(re.search(r"\b(?:breakthrough|recent)\s+(?:seizure|event|episode)", surrounding))


SEIZURE_FREE_SINCE_DATE_RULE = RuleSpec(
    rule_id="seizure_free.since_date",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure-free or last-event date converted to a month duration.",
    pattern=re.compile(
        rf"\b(?:seizure(?:[-\u2010-\u2015]|\s)free\s+(?:interval\s+)?since|"
        rf"drug-free\s+remission\s+since|no\s+focal\s+clonic\s+since|"
        rf"sustained\s+remission\s+since|prior\s+cluster\s+pattern\s+resolved\s+since|"
        rf"last\s+seizure\s+on)\s+"
        rf"(?P<date>\d{{1,2}}(?:[-/](?:\d{{1,2}}|{MONTH_NAME_PATTERN})[-/]\d{{4}}|"
        rf"\s+(?:{MONTH_NAME_PATTERN})\s+\d{{4}}))\b",
        re.IGNORECASE,
    ),
    build=_build_seizure_free_since_date,
    examples=(
        RuleExample(
            text="Clinic Date: 23 December 2021. Drug-free remission since 20-Jun-2021.",
            expected_label="seizure free for 6 month",
            expected_evidence="Drug-free remission since 20-Jun-2021",
        ),
    ),
    provenance="Portable V1 date-anchored seizure-free assertion.",
)

ABSENCE_FOR_DURATION_RULE = RuleSpec(
    rule_id="seizure_free.absence_for_duration",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Absence of seizure-like events with an explicit month duration.",
    pattern=re.compile(
        rf"\b(?P<evidence>(?:absence\s+of\s+events|"
        rf"no\s+occurrence\s+of\s+events\s+suggestive\s+of\s+seizures)"
        rf".{{0,80}}?\b(?P<count>{NUMBER_TOKEN})\s+months?\s+ago|"
        rf"absence\s+of\s+events\s+for\s+over\s+(?P<over_count>{NUMBER_TOKEN})\s+months?)\b",
        re.IGNORECASE,
    ),
    build=_build_absence_for_duration,
    examples=(
        RuleExample(
            text="There has been an absence of events for over six months.",
            expected_label="seizure free for 6 month",
            expected_evidence="absence of events for over six months",
        ),
    ),
    provenance="Portable V1 duration-based no-event assertion.",
)

NO_EVENTS_FOR_DURATION_RULE = RuleSpec(
    rule_id="seizure_free.no_events_for_duration",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="No events, warnings, auras, or spell-like events for a duration.",
    pattern=re.compile(
        rf"\b(?P<evidence>no\s+(?:events,\s+warnings,\s+or\s+auras|"
        rf"spell-like\s+events\s+suggestive\s+of\s+seizures)\s+"
        rf"(?:for\s+over|for|over)\s+(?:the\s+past\s+)?(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?P<unit>months?|years?))\b",
        re.IGNORECASE,
    ),
    build=_build_no_events_for_duration,
    examples=(
        RuleExample(
            text="Patient reports no events, warnings, or auras for over 18 months.",
            expected_label="seizure free for 18 month",
            expected_evidence="no events, warnings, or auras for over 18 months",
        ),
    ),
    provenance="Portable V1 duration-based no-event assertion.",
)

SEIZURE_FREE_DURATION_STATUS_RULE = RuleSpec(
    rule_id="seizure_free.duration_status",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure-free interval or zero recorded rate with explicit duration.",
    pattern=re.compile(
        rf"\b(?P<evidence>seizure(?:[-\u2010-\u2015]|\s)free\s+interval\s+"
        rf"extends\s+to\s+(?P<count>{NUMBER_TOKEN})\s+(?P<unit>months?|years?)|"
        rf"recorded\s+seizure\s+rate\s+at\s+zero\s+over\s+the\s+last\s+"
        rf"(?P<zero_count>{NUMBER_TOKEN})\s+(?P<zero_unit>months?|years?))\b",
        re.IGNORECASE,
    ),
    build=_build_duration_status,
    examples=(
        RuleExample(
            text="Seizure-free interval extends to eleven months.",
            expected_label="seizure free for 11 month",
            expected_evidence="Seizure-free interval extends to eleven months",
        ),
    ),
    provenance="Portable V1 duration-based seizure-free assertion.",
)

SEIZURE_FREE_ONE_AND_HALF_YEARS_RULE = RuleSpec(
    rule_id="seizure_free.one_and_half_years",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="One-and-a-half-year seizure-free duration.",
    pattern=re.compile(
        r"\b(?:seizure(?:[-\u2010-\u2015]|\s)free\s+for|"
        r"not\s+experiencing\s+any\s+seizures\s+in)\s+one\s+and\s+a\s+half\s+years\b",
        re.IGNORECASE,
    ),
    build=_build_one_and_half_years,
    examples=(
        RuleExample(
            text="She has now been seizure free for one and a half years.",
            expected_label="seizure free for 1.5 year",
            expected_evidence="seizure free for one and a half years",
        ),
    ),
    provenance="Portable V1 duration-based seizure-free assertion.",
)

LAST_EPILEPTIC_EVENT_RULE = RuleSpec(
    rule_id="seizure_free.last_epileptic_event",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Last clearly epileptic event approximately N months ago.",
    pattern=re.compile(
        rf"\b(?P<evidence>last\s+had\s+a\s+clearly\s+epileptic\s+"
        rf"(?:{WORD_TOKEN}\s+){{0,5}}?event\s+approximately\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+months?\s+ago)\b",
        re.IGNORECASE,
    ),
    build=_build_last_epileptic_event,
    examples=(
        RuleExample(
            text="She last had a clearly epileptic focal event approximately six months ago.",
            expected_label="seizure free for 6 month",
            expected_evidence=(
                "last had a clearly epileptic focal event approximately six months ago"
            ),
        ),
    ),
    provenance="Portable V1 last-event seizure-free assertion.",
)

GENERIC_SEIZURE_FREE_RULE = RuleSpec(
    rule_id="seizure_free.generic_duration_or_since",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Generic seizure-free/free-of/no-seizure duration or since assertion.",
    pattern=re.compile(
        rf"\b(?:seizure(?:[-\u2010-\u2015]|\s)free|free of (?:{SEIZURE_TERMS})|"
        rf"no (?:further )?(?:{SEIZURE_TERMS})).{{0,80}}?"
        rf"(?:(?P<count>{NUMBER_TOKEN})\s+(?P<unit>months|month|years|year)|"
        r"several years|long duration|since\b)",
        re.IGNORECASE,
    ),
    build=_build_generic_seizure_free,
    exclude=(_is_generic_seizure_free_distractor,),
    examples=(
        RuleExample(
            text="She remains free of seizures for two years on the current regimen.",
            expected_label="seizure free for 2 year",
            expected_evidence="free of seizures for two years",
        ),
        RuleExample(
            text="There have been no seizures since the last clinic review.",
            expected_label="seizure free for multiple year",
            expected_evidence="no seizures since",
        ),
        RuleExample(
            text=(
                "The driving plan is to reassess after the seizure-free interval. "
                "Current seizures are weekly."
            ),
            anti_example=True,
            note="Administrative seizure-free interval mention is not current no-event evidence.",
        ),
    ),
    provenance="Portable V1 generic seizure-free assertion with historical/current guards.",
)


NO_DEFINITE_EVENTS_RULE = RuleSpec(
    rule_id="seizure_free.no_definite_events",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Explicit no-definite-event assertion.",
    pattern=re.compile(
        rf"\bno\s+definite\s+(?:{QUALIFIED_SEIZURE_TERMS})\b",
        re.IGNORECASE,
    ),
    build=_build_no_definite_events,
    examples=(
        RuleExample(
            text="Since the last appointment, the patient reports no definite seizure events.",
            expected_label="seizure free for multiple month",
            expected_evidence="no definite seizure events",
        ),
    ),
    provenance="Portable V1 no-event assertion.",
)

CURRENT_CONTROL_PHRASE_RULE = RuleSpec(
    rule_id="seizure_free.current_control_phrase",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Current control or no-event assertion without a precise duration.",
    pattern=re.compile(
        rf"\b(?:"
        rf"seizure\s+freedom\s+continues|"
        rf"complete\s+seizure\s+control|"
        rf"complete\s+control\s+of\s+seizures|"
        rf"no\s+recurrence|"
        rf"seizures\s+remain\s+settled\s+without\s+recent\s+breakthrough\s+events|"
        rf"currently\s+in\s+long-term\s+remission,\s+having\s+been\s+"
        rf"seizure\s+free\s+for\s+years|"
        rf"has\s+not\s+experienced\s+any\s+(?:{SEIZURE_TERMS})|"
        rf"no\s+clinical\s+seizures\s+observed\s+since|"
        rf"no\s+(?:further\s+)?(?:witnessed\s+)?(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"(?:reported|observed|recorded|since|suggestive\s+of\s+seizures)|"
        rf"free\s+of\s+(?:his|her|their)\s+usual\s+attacks\s+over\s+this\s+interval|"
        rf"no\s+auras,\s+warnings,\s+or\s+witnessed\s+events\s+"
        rf"for\s+an\s+extended\s+period|"
        rf"has\s+not\s+described\s+any\s+further\s+events\s+"
        rf"suggestive\s+of\s+seizures|"
        rf"no\s+(?:recent\s+)?events\s+suggestive\s+of\s+seizures|"
        rf"sustained\s+postoperative\s+seizure\s+freedom|"
        rf"no\s+recorded\s+events\s+since|"
        rf"interval\s+history\s+negative\s+for\s+seizures|"
        rf"durable\s+seizure\s+control|"
        rf"seizure\s+cessation\s+following\s+initiation\s+of\s+last\s+asm|"
        rf"no\s+recorded\s+events,\s+either\s+focal\s+or\s+generalised,\s+"
        rf"during\s+the\s+period\s+monitored|"
        rf"typical\s+episodes\s+have\s+not\s+recurred|"
        rf"no\s+further\s+events\s+suggestive\s+of\s+"
        rf"(?:her|his|their)\s+previous\s+spells|"
        rf"no\s+recorded\s+spells\s+suggestive\s+of\s+seizure\s+activity|"
        rf"episode-free\s+on\s+(?:her|his|their)\s+current\s+routine|"
        rf"recorded\s+seizure\s+rate\s+at\s+zero\s+on\s+"
        rf"the\s+monitoring\s+platform\s+during\s+this\s+period|"
        rf"no\s+recorded\s+events\s+requiring\s+rescue\s+measures|"
        rf"no\s+recorded\s+events|"
        rf"seizure-free\s+by\s+patient\s+report|"
        rf"no\s+clear-cut\s+events\s+to\s+suggest\s+recent\s+seizures|"
        rf"no\s+events\s+of\s+concern|"
        rf"no\s+episodes\s+brought\s+to\s+attention\s+by\s+"
        rf"(?:carers|caregivers)\s+or\s+bystanders,\s+nor\s+any\s+"
        rf"events\s+(?:he|she|they)\s+has\s+recognised\s+as\s+seizures|"
        rf"without\s+events\s+for\s+an\s+extended\s+period|"
        rf"steady\s+run\s+without\s+clear\s+seizures\s+at\s+present|"
        rf"focal\s+epileptic\s+spasms\s+freedom\s+achieved"
        rf")\b",
        re.IGNORECASE,
    ),
    build=_build_current_control_phrase,
    examples=(
        RuleExample(
            text="Since his last review, seizure freedom continues.",
            expected_label="seizure free for multiple year",
            expected_evidence="seizure freedom continues",
        ),
        RuleExample(
            text="He described remaining free of his usual attacks over this interval.",
            expected_label="seizure free for multiple year",
            expected_evidence="free of his usual attacks over this interval",
        ),
    ),
    provenance="Portable V1 current-control no-event assertion set.",
)

SEIZURE_FREE_RULES = (
    SEIZURE_FREE_SINCE_DATE_RULE,
    ABSENCE_FOR_DURATION_RULE,
    NO_EVENTS_FOR_DURATION_RULE,
    SEIZURE_FREE_DURATION_STATUS_RULE,
    SEIZURE_FREE_ONE_AND_HALF_YEARS_RULE,
    LAST_EPILEPTIC_EVENT_RULE,
    GENERIC_SEIZURE_FREE_RULE,
    NO_DEFINITE_EVENTS_RULE,
    CURRENT_CONTROL_PHRASE_RULE,
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


def _singular_unit(value: str | None) -> str:
    if value is None:
        return "month"
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")
