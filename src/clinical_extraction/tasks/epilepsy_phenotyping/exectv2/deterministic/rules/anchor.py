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
    RuleGroup,
)
from .extract_impl_types import ExtractRuleImpl

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


# RuleSpec metadata: sf_surface_registry/catalog/extract.yaml
# Assembled via sf_surface_registry/adapters/extraction.py

ANCHOR_EXTRACT_IMPLS: dict[str, ExtractRuleImpl] = {
    "anchor.seizure_type_phrase": ExtractRuleImpl(
        re.compile(
            "\\b(?:cluster\\s+of\\s+)?(?:(?:secondary\\s+generalised|secondary\\s+generalized|generalised\\s+tonic[\\s-]clonic|generalized\\s+tonic[\\s-]clonic|focal\\s+to\\s+bilateral|focal\\s+motor|partial\\s+motor|frontal\\s+lobe|dyscognitive|focal|generalised|generalized|tonic[\\s-]clonic|tonic|clonic|myoclonic|atonic|absence(?:[\\s-]like)?|non[\\s-]?convulsive|convulsive|complex\\s+partial|simple\\s+partial|partial|bilateral|nocturnal|drop)[\\s-]+){0,3}(?:seizures?|absences?|jerks?|convulsions?)(?:\\s+with\\s+(?:loss|altered|impaired)\\s+(?:of\\s+)?awareness)?",
            re.IGNORECASE,
        ),
        _build_seizure_type_anchor,
    ),
    "anchor.seizure_free_phrase": ExtractRuleImpl(
        re.compile("\\bseizure(?:[-‐-―\\s])free\\b", re.IGNORECASE), _build_seizure_free_anchor
    ),
}
