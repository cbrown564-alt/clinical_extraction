"""Seizure-free detection rules for ExECTv2.

In the ExECTv2 annotation scheme, seizure-free observations are encoded as
SeizureFrequency mentions with ``NumberOfSeizures="0"``.

Rules are adapted from the Gan 2026 seizure-free rule set, simplified for the
synthetic ExECTv2 letter format.  The Gan 2026 rules carry portability tags
SEIZURE_FREQUENCY; these carry CLINICAL_EPILEPSY since the patterns are not
dataset-specific.
"""
from __future__ import annotations

import re

from clinical_extraction.tasks.shared.epilepsy.terms import (
    NUMBER_TOKEN,
    QUALIFIED_SEIZURE_TERMS,
    SEIZURE_TERMS,
)

from ..candidates import AttributeExtraction, AttributeKind
from ..normalizer import clean_span, normalize_count, normalize_unit
from ..rule_metadata import (
    ExtractionContext,
    Portability,
    RuleGroup,
)

_UNIT = r"day|week|month|year|days|weeks|months|years"
_COUNT = NUMBER_TOKEN
# Approximation qualifiers that precede a duration count ("seizure free for more
# than five years", "for almost 2 years") — gold keeps the count, dropping the
# qualifier, so they must not block the duration match.
_DUR_QUALIFIER = r"(?:over|more\s+than|at\s+least|nearly|almost|around|about|approximately|the\s+past)"

# A "no <seizure>" / control phrase is NOT a current seizure-frequency statement
# when it sits in a history / family-history / risk / investigation-marker frame:
# "no history of febrile seizures", "no significant seizure markers", "no witness
# descriptions", "no previous history of seizures". These are existence/absence
# statements about the past or about findings, which the guideline (L255) does
# not treat as a frequency statement. QUALIFIED_SEIZURE_TERMS allows up to four
# filler words before the noun, so these slip past the bare "no <seizure>" intent.
_NONCLINICAL_CONTEXT = re.compile(
    r"\b(?:history|family|risk|marker|markers|witness|descriptions?|warning|"
    r"driv\w*|licen\w*|dvla|allowed\s+to)\b",
    re.IGNORECASE,
)
_SEIZURE_FREE_DISTRACTOR_CONTEXT = re.compile(
    r"\b(?:driv\w*|dvla|licen\w*|refrain|before\s+the\s+seizure|"
    r"up\s+to\s+\w+\s+\w+\s+seizure\s+free|mother\s+used\s+to|family\s+history)\b",
    re.IGNORECASE,
)


def _is_nonclinical_zero_context(match: re.Match[str], context: ExtractionContext) -> bool:
    lo = max(0, match.start() - 30)
    hi = min(len(context.text), match.end() + 15)
    return bool(_NONCLINICAL_CONTEXT.search(context.text[lo:hi]))


def _is_seizure_free_distractor_context(
    match: re.Match[str], context: ExtractionContext
) -> bool:
    lo = max(0, match.start() - 80)
    hi = min(len(context.text), match.end() + 90)
    window = context.text[lo:hi]
    if _SEIZURE_FREE_DISTRACTOR_CONTEXT.search(window):
        return True
    following = context.text[match.end(): match.end() + 90]
    return bool(re.search(r"\b(?:however|but)\b.{0,50}\b(?:had|another)\s+(?:a\s+)?seizure\b", following, re.IGNORECASE))


def _sf_attrs(
    period_count: str | None = None,
    unit: str | None = None,
) -> dict[str, str]:
    d: dict[str, str] = {"NumberOfSeizures": "0"}
    if period_count is not None:
        d["NumberOfTimePeriods"] = normalize_count(period_count)
    if unit is not None:
        d["TimePeriod"] = normalize_unit(unit)
    return d


def _sf_candidate(
    match: re.Match[str],
    rule_id: str,
    portability: Portability,
    period_count: str | None = None,
    unit: str | None = None,
) -> AttributeExtraction:
    evidence = clean_span(match.group(0))
    return AttributeExtraction(
        evidence=evidence,
        span=(match.start(), match.end()),
        attributes=_sf_attrs(period_count=period_count, unit=unit),
        kind=AttributeKind.SEIZURE_FREE,
        rule_id=rule_id,
        rule_group=RuleGroup.SEIZURE_FREE,
        portability=portability,
    )


# ---------------------------------------------------------------------------
# Rule 1: "seizure free" / "seizure-free" with optional duration
#          "seizure free for 3 months", "seizure-free for 2 years"
# ---------------------------------------------------------------------------

def _build_sf_with_duration(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    count = match.group("count")
    unit = match.group("unit")
    return _sf_candidate(
        match,
        rule_id="sf.duration",
        portability=Portability.CLINICAL_EPILEPSY,
        period_count=count,
        unit=unit,
    )




# ---------------------------------------------------------------------------
# Rule 2: bare "seizure free" / "seizure-free" (no duration)
# ---------------------------------------------------------------------------

def _build_sf_bare(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _sf_candidate(
        match,
        rule_id="sf.bare",
        portability=Portability.CLINICAL_EPILEPSY,
    )


def _is_sf_bare_distractor(match: re.Match[str], context: ExtractionContext) -> bool:
    following = context.text[match.end(): match.end() + 120].lower()
    # "seizure-free interval" used administratively (e.g. driving law references)
    if re.search(r"\binterval\b", following[:40]):
        # Still valid if the interval is described as extending/achieved
        if re.search(r"\b(?:achieved|extends|established|maintained)\b", following[:80]):
            return False
        return True
    # "required seizure-free period" — administrative
    if re.search(r"\brequired\b", context.text[max(0, match.start() - 30): match.start()].lower()):
        return True
    return False




# ---------------------------------------------------------------------------
# Rule 3: "no seizures" with optional duration
#          "no seizures for 6 months", "no further seizures"
# ---------------------------------------------------------------------------

def _build_no_seizures_duration(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    count = match.groupdict().get("count")
    unit = match.groupdict().get("unit")
    return _sf_candidate(
        match,
        rule_id="sf.no_seizures_duration",
        portability=Portability.CLINICAL_EPILEPSY,
        period_count=count,
        unit=unit,
    )




# ---------------------------------------------------------------------------
# Rule 3a: "has not had <specific seizure type> for N years"
# ---------------------------------------------------------------------------

def _build_no_had_duration(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _sf_candidate(
        match,
        rule_id="sf.no_had_duration",
        portability=Portability.CLINICAL_EPILEPSY,
        period_count=match.group("count"),
        unit=match.group("unit"),
    )




# ---------------------------------------------------------------------------
# Rule 4: generic control phrases  ("complete seizure control",
#          "seizure freedom", "no events of concern", etc.)
# ---------------------------------------------------------------------------

_CONTROL_PHRASES = re.compile(
    rf"\b(?:"
    rf"complete\s+seizure\s+control|"
    rf"seizure\s+freedom(?:\s+(?:continues|maintained|achieved))?|"
    rf"free\s+of\s+(?:his|her|their|all)?\s*(?:{SEIZURE_TERMS})|"
    rf"no\s+clinical\s+seizures|"
    rf"no\s+recorded\s+(?:{SEIZURE_TERMS})|"
    rf"no\s+events\s+of\s+concern|"
    rf"no\s+breakthrough\s+(?:{SEIZURE_TERMS})|"
    rf"interval\s+history\s+negative\s+for\s+seizures|"
    rf"has\s+not\s+(?:experienced|reported|had)\s+any\s+(?:further\s+)?(?:{SEIZURE_TERMS})|"
    rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+(?:are|is|seem|seems|remain|remains)\s+"
    rf"(?:completely\s+)?(?:well\s+)?under\s+control"
    rf")\b",
    re.IGNORECASE,
)


def _build_control_phrase(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _sf_candidate(
        match,
        rule_id="sf.control_phrase",
        portability=Portability.CLINICAL_EPILEPSY,
    )




# ---------------------------------------------------------------------------
# Rule 5: "0 seizures" / "zero seizures" — explicit zero count
# ---------------------------------------------------------------------------

def _build_zero_count(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _sf_candidate(
        match,
        rule_id="sf.zero_count",
        portability=Portability.CLINICAL_EPILEPSY,
    )
# RuleSpec metadata: sf_surface_registry/catalog/extract.yaml
# Assembled via sf_surface_registry/adapters/extraction.py

from .extract_impl_types import ExtractRuleImpl

SEIZURE_FREE_EXTRACT_IMPLS: dict[str, ExtractRuleImpl] = {
    'sf.duration': ExtractRuleImpl(re.compile('\\bseizure(?:[-‐-―\\s])free\\s+(?:for\\s+)?(?:(?:over|more\\s+than|at\\s+least|nearly|almost|around|about|approximately|the\\s+past)\\s+)*(?P<count>(?:(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few)(?:\\s+(?:to|or)\\s+(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few)|\\s*[-–—]\\s*(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))?))\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b', re.IGNORECASE), _build_sf_with_duration, exclude=(_is_seizure_free_distractor_context,)),
    'sf.zero_count': ExtractRuleImpl(re.compile('\\b(?:0|zero)\\s+(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus))\\b', re.IGNORECASE), _build_zero_count),
    'sf.no_seizures_duration': ExtractRuleImpl(re.compile('\\bno\\s+(?:further\\s+)?(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus))(?:\\s+for\\s+(?:over\\s+)?(?P<count>(?:(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few)(?:\\s+(?:to|or)\\s+(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few)|\\s*[-–—]\\s*(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))?))\\s+(?P<unit>day|week|month|year|days|weeks|months|years))?\\b', re.IGNORECASE), _build_no_seizures_duration, exclude=(_is_nonclinical_zero_context,)),
    'sf.no_had_duration': ExtractRuleImpl(re.compile("\\b(?:(?:has|have|had)\\s+not\\s+had\\s+(?:any\\s+|any\\s+more\\s+|one\\s+of\\s+(?:his|her|their)\\s+(?:bigger|larger|major)\\s+|a\\s+)?(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus))|(?:hasn't|haven't|hadn't)\\s+(?:had\\s+)?(?:any\\s+|a\\s+)?(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus))|(?:they|these)\\s+(?:have\\s+|has\\s+)?(?:not\\s+happen(?:ed)?|haven't\\s+happened|hasn't\\s+happened))\\s+(?:now\\s+)?for\\s+(?:around\\s+|about\\s+|at\\s+least\\s+|over\\s+|more\\s+than\\s+)?(?P<count>(?:(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few)(?:\\s+(?:to|or)\\s+(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few)|\\s*[-–—]\\s*(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))?))\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b", re.IGNORECASE), _build_no_had_duration),
    'sf.control_phrase': ExtractRuleImpl(re.compile('\\b(?:complete\\s+seizure\\s+control|seizure\\s+freedom(?:\\s+(?:continues|maintained|achieved))?|free\\s+of\\s+(?:his|her|their|all)?\\s*(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|no\\s+clinical\\s+seizures|no\\s+recorded\\s+(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|no\\s+events\\s+of\\s+concern|no\\s+breakthrough\\s+(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|interval\\s+history\\s+negative\\s+for\\s+seizures|has\\s+not\\s+(?:experienced|reported|had)\\s+any\\s+(?:further\\s+)?(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus))\\s+(?:are|is|seem|seems|remain|remains)\\s+(?:completely\\s+)?(?:well\\s+)?under\\s+control)\\b', re.IGNORECASE), _build_control_phrase, exclude=(_is_nonclinical_zero_context,)),
    'sf.bare': ExtractRuleImpl(re.compile('\\bseizure(?:[-‐-―\\s])free\\b', re.IGNORECASE), _build_sf_bare, exclude=(_is_sf_bare_distractor, _is_seizure_free_distractor_context,)),
}


def __getattr__(name: str):
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(name)
    from .extract_reexports import extract_reexport

    return extract_reexport(name)
