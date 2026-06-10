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
    NUMBER_WORD_PATTERN,
    QUALIFIED_SEIZURE_TERMS,
    SEIZURE_TERMS,
)

from ..candidates import AttributeExtraction, AttributeKind
from ..normalizer import clean_span, normalize_count, normalize_unit
from ..rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

_UNIT = r"day|week|month|year|days|weeks|months|years"
_COUNT = NUMBER_TOKEN


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


SF_WITH_DURATION_RULE = RuleSpec(
    rule_id="sf.duration",
    group=RuleGroup.SEIZURE_FREE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Seizure-free with an explicit duration.",
    pattern=re.compile(
        rf"\bseizure(?:[-‐-―\s])free\s+"
        rf"(?:for\s+(?:over\s+)?)?(?:the\s+past\s+)?"
        rf"(?P<count>{_COUNT})\s+(?P<unit>{_UNIT})\b",
        re.IGNORECASE,
    ),
    build=_build_sf_with_duration,
    examples=(
        RuleExample(
            text="She has been seizure free for 3 months.",
            expected_evidence="seizure free for 3 months",
            expected_attributes={"NumberOfSeizures": "0", "NumberOfTimePeriods": "3", "TimePeriod": "Month"},
        ),
        RuleExample(
            text="Patient is seizure-free for 2 years.",
            expected_evidence="seizure-free for 2 years",
            expected_attributes={"NumberOfSeizures": "0", "NumberOfTimePeriods": "2", "TimePeriod": "Year"},
        ),
    ),
    provenance="Adapted from Gan2026 seizure-free rules.",
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


SF_BARE_RULE = RuleSpec(
    rule_id="sf.bare",
    group=RuleGroup.SEIZURE_FREE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Bare seizure-free assertion without duration.",
    pattern=re.compile(
        r"\bseizure(?:[-‐-―\s])free\b",
        re.IGNORECASE,
    ),
    build=_build_sf_bare,
    exclude=(_is_sf_bare_distractor,),
    examples=(
        RuleExample(
            text="He is currently seizure free.",
            expected_evidence="seizure free",
            expected_attributes={"NumberOfSeizures": "0"},
        ),
        RuleExample(
            text="The required seizure-free period for driving is 12 months.",
            anti_example=True,
            note="Administrative required-period mention, not a clinical assertion.",
        ),
    ),
    provenance="Adapted from Gan2026 seizure-free rules.",
)


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


NO_SEIZURES_DURATION_RULE = RuleSpec(
    rule_id="sf.no_seizures_duration",
    group=RuleGroup.SEIZURE_FREE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="'No seizures' with optional duration or 'further' qualifier.",
    pattern=re.compile(
        rf"\bno\s+(?:further\s+)?(?:{QUALIFIED_SEIZURE_TERMS})"
        rf"(?:\s+for\s+(?:over\s+)?(?P<count>{_COUNT})\s+(?P<unit>{_UNIT}))?\b",
        re.IGNORECASE,
    ),
    build=_build_no_seizures_duration,
    examples=(
        RuleExample(
            text="There have been no seizures for 6 months.",
            expected_evidence="no seizures for 6 months",
            expected_attributes={"NumberOfSeizures": "0", "NumberOfTimePeriods": "6", "TimePeriod": "Month"},
        ),
        RuleExample(
            text="No further episodes reported since the last clinic.",
            expected_evidence="no further episodes",
            expected_attributes={"NumberOfSeizures": "0"},
        ),
    ),
    provenance="Adapted from Gan2026 no-event rules.",
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
    rf"has\s+not\s+(?:experienced|reported|had)\s+any\s+(?:{SEIZURE_TERMS})"
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


CONTROL_PHRASE_RULE = RuleSpec(
    rule_id="sf.control_phrase",
    group=RuleGroup.SEIZURE_FREE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Standard clinical control phrases encoding seizure freedom.",
    pattern=_CONTROL_PHRASES,
    build=_build_control_phrase,
    examples=(
        RuleExample(
            text="She demonstrates complete seizure control on current medication.",
            expected_evidence="complete seizure control",
            expected_attributes={"NumberOfSeizures": "0"},
        ),
        RuleExample(
            text="Seizure freedom maintained since starting lamotrigine.",
            expected_evidence="Seizure freedom maintained",
            expected_attributes={"NumberOfSeizures": "0"},
        ),
    ),
    provenance="Adapted from Gan2026 current-control-phrase rules.",
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


ZERO_COUNT_RULE = RuleSpec(
    rule_id="sf.zero_count",
    group=RuleGroup.SEIZURE_FREE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Explicit zero-count expression: '0 seizures' or 'zero seizures'.",
    pattern=re.compile(
        rf"\b(?:0|zero)\s+(?:{QUALIFIED_SEIZURE_TERMS})\b",
        re.IGNORECASE,
    ),
    build=_build_zero_count,
    examples=(
        RuleExample(
            text="She reports 0 seizures this period.",
            expected_evidence="0 seizures",
            expected_attributes={"NumberOfSeizures": "0"},
        ),
    ),
    provenance="Explicit zero-count SF encoding.",
)


# ---------------------------------------------------------------------------
# Ordered rule list (longer/more specific patterns first)
# ---------------------------------------------------------------------------

SEIZURE_FREE_RULES: list[RuleSpec] = [
    SF_WITH_DURATION_RULE,       # duration form before bare form
    ZERO_COUNT_RULE,
    NO_SEIZURES_DURATION_RULE,
    CONTROL_PHRASE_RULE,
    SF_BARE_RULE,                # bare last to avoid shadowing duration form
]
