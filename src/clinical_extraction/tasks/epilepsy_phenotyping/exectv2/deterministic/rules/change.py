"""FrequencyChange extraction rules for ExECTv2.

Gold closed vocab: {Decreased, Frequent, Increased, Infrequent, Same}.
These rules extract mentions where the dominant clinical information is a
direction-of-change rather than a count — e.g. "frequency has decreased".
"""
from __future__ import annotations

import re

from clinical_extraction.tasks.shared.epilepsy.terms import QUALIFIED_SEIZURE_TERMS, SEIZURE_TERMS

from ..candidates import AttributeExtraction, AttributeKind
from ..normalizer import clean_span
from ..rule_metadata import (
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

_SEIZURE_NOUN = rf"(?:seizure|{SEIZURE_TERMS})\s+(?:frequency|rate|burden|control)"


def _change_candidate(
    match: re.Match[str],
    change_value: str,
    rule_id: str,
) -> AttributeExtraction:
    evidence = clean_span(match.group(0))
    return AttributeExtraction(
        evidence=evidence,
        span=(match.start(), match.end()),
        attributes={"FrequencyChange": change_value},
        kind=AttributeKind.FREQUENCY_CHANGE,
        rule_id=rule_id,
        rule_group=RuleGroup.FREQUENCY_CHANGE,
        portability=Portability.CLINICAL_EPILEPSY,
    )


# ---------------------------------------------------------------------------
# Decreased
# ---------------------------------------------------------------------------

def _build_decreased(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Decreased", "change.decreased")


DECREASED_RULE = RuleSpec(
    rule_id="change.decreased",
    group=RuleGroup.FREQUENCY_CHANGE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Seizure frequency decreased / improved / reduced.",
    pattern=re.compile(
        rf"\b(?:"
        rf"(?:{_SEIZURE_NOUN}|seizures?|episodes?|events?)\s+"
        rf"(?:(?:has|have)\s+)?(?:decreased|reduced|improved|declined|lessened)|"
        rf"(?:decreased|reduced|improvement\s+in)\s+(?:{_SEIZURE_NOUN}|seizure\s+(?:frequency|burden)|seizures?)|"
        rf"(?:{_SEIZURE_NOUN}|seizures?)\s+(?:are|is)\s+(?:decreased|reduced|better\s+controlled|less\s+frequent)"
        rf")\b",
        re.IGNORECASE,
    ),
    build=_build_decreased,
    examples=(
        RuleExample(
            text="Seizure frequency has decreased since starting lamotrigine.",
            expected_evidence="Seizure frequency has decreased",
            expected_attributes={"FrequencyChange": "Decreased"},
        ),
        RuleExample(
            text="There has been a reduction in seizure frequency.",
            expected_evidence="reduction in seizure frequency",
            expected_attributes={"FrequencyChange": "Decreased"},
        ),
    ),
    provenance="Clinical epilepsy FrequencyChange=Decreased patterns.",
)


# ---------------------------------------------------------------------------
# Increased
# ---------------------------------------------------------------------------

def _build_increased(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Increased", "change.increased")


INCREASED_RULE = RuleSpec(
    rule_id="change.increased",
    group=RuleGroup.FREQUENCY_CHANGE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Seizure frequency increased / worsened.",
    pattern=re.compile(
        rf"\b(?:"
        rf"(?:{_SEIZURE_NOUN}|seizures?|episodes?|events?)\s+"
        rf"(?:(?:has|have)\s+)?(?:increased|worsened|escalated|risen)|"
        rf"(?:increased|increase\s+in|worsening\s+of)\s+(?:{_SEIZURE_NOUN}|seizures?)|"
        rf"(?:{_SEIZURE_NOUN}|seizures?)\s+(?:are|is)\s+(?:increased|more\s+frequent|worse)"
        rf")\b",
        re.IGNORECASE,
    ),
    build=_build_increased,
    examples=(
        RuleExample(
            text="Seizure frequency has increased over the past 3 months.",
            expected_evidence="Seizure frequency has increased",
            expected_attributes={"FrequencyChange": "Increased"},
        ),
    ),
    provenance="Clinical epilepsy FrequencyChange=Increased patterns.",
)


# ---------------------------------------------------------------------------
# Same / Unchanged
# ---------------------------------------------------------------------------

def _build_same(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Same", "change.same")


SAME_RULE = RuleSpec(
    rule_id="change.same",
    group=RuleGroup.FREQUENCY_CHANGE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Seizure frequency unchanged / same / stable.",
    pattern=re.compile(
        rf"\b(?:"
        rf"(?:{_SEIZURE_NOUN}|seizures?)\s+(?:(?:remain(?:s)?|are|is)\s+)?(?:unchanged|stable|the\s+same)|"
        rf"no\s+change\s+in\s+(?:{_SEIZURE_NOUN}|seizure\s+(?:frequency|pattern))|"
        rf"(?:unchanged|stable)\s+(?:{_SEIZURE_NOUN}|seizure\s+(?:frequency|pattern))"
        rf")\b",
        re.IGNORECASE,
    ),
    build=_build_same,
    examples=(
        RuleExample(
            text="Seizure frequency remains unchanged.",
            expected_evidence="Seizure frequency remains unchanged",
            expected_attributes={"FrequencyChange": "Same"},
        ),
        RuleExample(
            text="No change in seizure frequency noted.",
            expected_evidence="No change in seizure frequency",
            expected_attributes={"FrequencyChange": "Same"},
        ),
    ),
    provenance="Clinical epilepsy FrequencyChange=Same patterns.",
)


# ---------------------------------------------------------------------------
# Infrequent
# ---------------------------------------------------------------------------

def _build_infrequent(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Infrequent", "change.infrequent")


INFREQUENT_RULE = RuleSpec(
    rule_id="change.infrequent",
    group=RuleGroup.FREQUENCY_CHANGE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Seizures described as infrequent.",
    pattern=re.compile(
        rf"\b(?:infrequent|infrequently|rare)\s+(?:{QUALIFIED_SEIZURE_TERMS}|seizures?|episodes?)\b"
        rf"|\b(?:{QUALIFIED_SEIZURE_TERMS}|seizures?|episodes?)\s+(?:are\s+)?(?:infrequent|rare)\b",
        re.IGNORECASE,
    ),
    build=_build_infrequent,
    examples=(
        RuleExample(
            text="Infrequent focal seizures noted in the review period.",
            expected_evidence="Infrequent focal seizures",
            expected_attributes={"FrequencyChange": "Infrequent"},
        ),
    ),
    provenance="Clinical epilepsy FrequencyChange=Infrequent patterns.",
)


# ---------------------------------------------------------------------------
# Frequent
# ---------------------------------------------------------------------------

def _build_frequent(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Frequent", "change.frequent")


FREQUENT_RULE = RuleSpec(
    rule_id="change.frequent",
    group=RuleGroup.FREQUENCY_CHANGE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Seizures described as frequent / high frequency.",
    pattern=re.compile(
        rf"\b(?:frequent|frequently|high.?frequency)\s+(?:{QUALIFIED_SEIZURE_TERMS}|seizures?|episodes?)\b"
        rf"|\b(?:{QUALIFIED_SEIZURE_TERMS}|seizures?|episodes?)\s+(?:are\s+)?(?:frequent|occurring\s+frequently)\b",
        re.IGNORECASE,
    ),
    build=_build_frequent,
    examples=(
        RuleExample(
            text="Frequent tonic-clonic seizures are reported.",
            expected_evidence="Frequent tonic-clonic seizures",
            expected_attributes={"FrequencyChange": "Frequent"},
        ),
    ),
    provenance="Clinical epilepsy FrequencyChange=Frequent patterns.",
)


# ---------------------------------------------------------------------------
# Ordered rule list
# ---------------------------------------------------------------------------

CHANGE_RULES: list[RuleSpec] = [
    DECREASED_RULE,
    INCREASED_RULE,
    SAME_RULE,
    INFREQUENT_RULE,
    FREQUENT_RULE,
]
