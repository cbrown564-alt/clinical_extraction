"""Anchor-phrase detection rules for ExECTv2 SeizureFrequency.

In the gold annotation scheme, ``SeizureFrequency.text`` is a seizure-type /
event-description phrase (e.g. "focal seizures with loss of awareness",
"generalised tonic clonic seizures", "seizure-free") — the frequency
information itself (counts, periods, change direction) is encoded purely as
*attributes*, extracted separately by the rate / seizure-free / change rules
in ``rules/rate.py``, ``rules/seizure_free.py`` and ``rules/change.py`` and
merged onto the nearest anchor by ``association.associate_attributes_to_anchors``.

This module finds the anchor phrases themselves: seizure-type noun phrases
(optionally qualified by a clinical descriptor and/or an "with loss/altered
of awareness" suffix), plus "seizure-free" as its own anchor (gold sometimes
annotates the bare seizure-free phrase as the SeizureFrequency text, with
duration/count folded into attributes).
"""
from __future__ import annotations

import re

from ..candidates import AnchorCandidate
from ..normalizer import clean_span
from ..rule_metadata import (
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

# ---------------------------------------------------------------------------
# Seizure-type descriptors (clinically meaningful pre-modifiers of a seizure
# noun). Multi-word / hyphen-aware alternatives are listed before their
# single-word components so the regex prefers the longer match.
# ---------------------------------------------------------------------------

_DESCRIPTOR = (
    r"secondary\s+generalised|secondary\s+generalized|"
    r"generalised\s+tonic[\s-]clonic|generalized\s+tonic[\s-]clonic|"
    r"focal\s+to\s+bilateral|"
    r"focal\s+motor|partial\s+motor|frontal\s+lobe|dyscognitive|"
    r"focal|"
    r"generalised|generalized|"
    r"tonic[\s-]clonic|tonic|clonic|"
    r"myoclonic|atonic|"
    r"absence(?:[\s-]like)?|"
    r"non[\s-]?convulsive|convulsive|"
    r"complex\s+partial|simple\s+partial|partial|"
    r"bilateral|nocturnal|drop"
)

# "with loss of awareness" but also "with altered/impaired awareness" (no "of") —
# gold's most common qualified phrase is "focal seizures with altered awareness"
# (6 mentions), which has no "of"; requiring it dropped the qualifier and broke
# both phrase match and the CUI lookup.
_AWARENESS_SUFFIX = r"(?:\s+with\s+(?:loss|altered|impaired)\s+(?:of\s+)?awareness)?"

# SF-specific head nouns. Guideline v9 L227: "Seizures, specific seizures,
# absences, and myoclonic jerks are to be annotated. Events, episodes, or other
# slang terms should not." So SF anchors use this narrow set, NOT the shared
# SEIZURE_TERMS (which includes events/episodes/spells/attacks/auras for the
# other tasks). "jerks" is reached via the "myoclonic" descriptor.
_SF_ANCHOR_TERMS = r"seizures?|absences?|jerks?|convulsions?"


def _build_seizure_type_anchor(match: re.Match[str], _ctx: ExtractionContext) -> AnchorCandidate:
    evidence = clean_span(match.group(0))
    return AnchorCandidate(
        text=evidence,
        evidence=evidence,
        span=(match.start(), match.end()),
        rule_id="anchor.seizure_type_phrase",
        rule_group=RuleGroup.ANCHOR_PHRASE,
        portability=Portability.CLINICAL_EPILEPSY,
    )


SEIZURE_TYPE_ANCHOR_RULE = RuleSpec(
    rule_id="anchor.seizure_type_phrase",
    group=RuleGroup.ANCHOR_PHRASE,
    portability=Portability.CLINICAL_EPILEPSY,
    description=(
        "Seizure-type / event-description noun phrase: optional clinical "
        "descriptor(s) + seizure noun + optional 'with loss/altered of "
        "awareness' suffix."
    ),
    pattern=re.compile(
        rf"\b(?:cluster\s+of\s+)?(?:(?:{_DESCRIPTOR})[\s-]+){{0,3}}"
        rf"(?:{_SF_ANCHOR_TERMS}){_AWARENESS_SUFFIX}",
        re.IGNORECASE,
    ),
    build=_build_seizure_type_anchor,
    examples=(
        RuleExample(
            text="focal seizures with loss of awareness approximately 2 to 3 per month.",
            expected_evidence="focal seizures with loss of awareness",
        ),
        RuleExample(
            text="She has generalised tonic clonic seizures occurring twice weekly.",
            expected_evidence="generalised tonic clonic seizures",
        ),
        RuleExample(
            text="Secondary generalised seizures since the last clinic appointment.",
            expected_evidence="Secondary generalised seizures",
        ),
        RuleExample(
            text="Myoclonic jerks have become more frequent.",
            expected_evidence="Myoclonic jerks",
        ),
        RuleExample(
            text="No change in seizures over the last year.",
            expected_evidence="seizures",
        ),
    ),
    provenance="Anchor phrase: seizure-type noun phrase. Generalizes to Phase 6 "
    "Diagnosis-style entity detection.",
)


# ---------------------------------------------------------------------------
# "Seizure-free" as its own anchor phrase.
# ---------------------------------------------------------------------------

def _build_seizure_free_anchor(match: re.Match[str], _ctx: ExtractionContext) -> AnchorCandidate:
    evidence = clean_span(match.group(0))
    return AnchorCandidate(
        text=evidence,
        evidence=evidence,
        span=(match.start(), match.end()),
        rule_id="anchor.seizure_free_phrase",
        rule_group=RuleGroup.ANCHOR_PHRASE,
        portability=Portability.CLINICAL_EPILEPSY,
    )


SEIZURE_FREE_ANCHOR_RULE = RuleSpec(
    rule_id="anchor.seizure_free_phrase",
    group=RuleGroup.ANCHOR_PHRASE,
    portability=Portability.CLINICAL_EPILEPSY,
    description="Bare 'seizure free' / 'seizure-free' as its own anchor phrase.",
    pattern=re.compile(r"\bseizure(?:[-‐-―\s])free\b", re.IGNORECASE),
    build=_build_seizure_free_anchor,
    examples=(
        RuleExample(
            text="She has been seizure-free for 7 months.",
            expected_evidence="seizure-free",
        ),
        RuleExample(
            text="He is currently seizure free.",
            expected_evidence="seizure free",
        ),
    ),
    provenance="Anchor phrase: gold sometimes annotates bare 'seizure-free' as "
    "SeizureFrequency.text with duration folded into attributes.",
)


ANCHOR_RULES: list[RuleSpec] = [
    SEIZURE_TYPE_ANCHOR_RULE,
    SEIZURE_FREE_ANCHOR_RULE,
]
