"""ExECTv2 deterministic SeizureFrequency extraction pipeline.

Anchor + association pipeline (Phase 2):

  text → anchor rules → resolve overlapping anchors
       → rate/seizure-free/change rules → resolve overlapping attribute extractions
       → associate each attribute extraction with its nearest anchor
       → emit one PredictedMention per anchor that gathered attributes

In the gold annotation scheme, ``SeizureFrequency.text`` is a seizure-type /
event-description phrase (the "anchor"), while frequency information (counts,
periods, change direction) is encoded purely as attributes. Anchors with no
nearby frequency information are dropped — they are not SeizureFrequency
mentions in this scheme.

Usage::

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
        extract_seizure_frequency,
        run_on_letters,
    )
    letters = load_letters()
    predicted = run_on_letters(letters)
"""
from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    SEIZURE_FREQUENCY,
    ExectLetter,
)

from .association import associate_attributes_to_anchors
from .candidates import AnchorCandidate, AttributeExtraction
from .lexicon import assign_cui
from .overlap import resolve_overlapping_anchors, resolve_overlapping_attributes
from .rule_metadata import DEFAULT_ABLATION, AblationConfig, ExtractionContext
from .rules.anchor import ANCHOR_RULES
from .rules.change import CHANGE_RULES
from .rules.rate import RATE_RULES
from .rules.seizure_free import SEIZURE_FREE_RULES
from .rules.temporal import TEMPORAL_RULES


def _collect_anchors(text: str, ablation: AblationConfig) -> list[AnchorCandidate]:
    ctx = ExtractionContext(text=text)
    results: list[AnchorCandidate] = []
    for spec in ANCHOR_RULES:
        results.extend(c for c in spec.apply(ctx, ablation) if isinstance(c, AnchorCandidate))
    return resolve_overlapping_anchors(results)


def _collect_attributes(text: str, ablation: AblationConfig) -> list[AttributeExtraction]:
    ctx = ExtractionContext(text=text)
    results: list[AttributeExtraction] = []
    for rule_set in (RATE_RULES, SEIZURE_FREE_RULES, CHANGE_RULES, TEMPORAL_RULES):
        for spec in rule_set:
            results.extend(
                c for c in spec.apply(ctx, ablation) if isinstance(c, AttributeExtraction)
            )
    return resolve_overlapping_attributes(results)


_COUNT_ATTRS = ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")
_PLURAL_SEIZURE_NOUN = re.compile(r"\b(?:seizures|absences|jerks)\b", re.IGNORECASE)
_SINGULAR_SEIZURE_NOUN = re.compile(r"\b(?:seizure|absence|jerk)\b", re.IGNORECASE)
# A negated frequency statement implies zero events, not the default plural=2.
# "no (further) seizures since …", "has not had any …", "remains seizure free",
# "denies …", "without …". Checked in a window just before the anchor.
_NEGATION_CUE = re.compile(
    r"\b(?:no|not|none|never|without|nil|denies|denied|negative\s+for)\b",
    re.IGNORECASE,
)


def _apply_implied_count(
    anchor: AnchorCandidate, attributes: dict[str, str], text: str = ""
) -> dict[str, str]:
    """Guideline v9 L989: when a frequency statement carries no explicit count
    and no other quantifier, a plural 'seizures' implies NumberOfSeizures=2 and a
    singular 'seizure' implies 1. Only applied to mentions that already have a
    frequency attribute (period/date/change), so it never fabricates mentions —
    it fills the implied count gold annotates by default.

    Exception: if the statement is negated (a negation cue sits just before the
    anchor, e.g. "no further seizures since …"), the implied count is 0, not the
    positive default — gold annotates "no seizures since <point in time>" as
    NumberOfSeizures=0 (L249), and the default plural=2 was the single largest
    source of count-value misses on temporal mentions."""
    if any(k in attributes for k in _COUNT_ATTRS) or "FrequencyChange" in attributes:
        return attributes
    phrase = anchor.text.lower()
    if not (_PLURAL_SEIZURE_NOUN.search(phrase) or _SINGULAR_SEIZURE_NOUN.search(phrase)):
        return attributes
    window = text[max(0, anchor.span[0] - 30): anchor.span[0]]
    if _NEGATION_CUE.search(window):
        implied = "0"
    elif _PLURAL_SEIZURE_NOUN.search(phrase):
        implied = "2"
    else:
        implied = "1"
    return {**attributes, "NumberOfSeizures": implied}


def _is_bare_nonzero_count(attributes: dict[str, str]) -> bool:
    """A count with no time frame is not a frequency statement (guideline L255).
    Gold never carries a bare nonzero NumberOfSeizures — a frequency needs a
    period/date/change/point-in-time. Bare NumberOfSeizures=0 IS valid (L53:
    "0 with no time period or point in time"), so it is kept."""
    return set(attributes) == {"NumberOfSeizures"} and attributes["NumberOfSeizures"] != "0"


def _with_cui(anchor: AnchorCandidate, attributes: dict[str, str]) -> dict[str, str]:
    """Attach the seizure-type CUI (and mirrored CUIPhrase) when the anchor
    phrase is in the lexicon. Gold annotates a CUI on every SF mention, so this
    is what makes the benchmark-comparable match config score non-zero. An
    out-of-lexicon phrase is left without a CUI rather than guessing."""
    cui = assign_cui(anchor.text)
    if cui is None:
        return attributes
    return {**attributes, "CUI": cui, "CUIPhrase": anchor.text}


def _mention_from_pair(anchor: AnchorCandidate, attributes: dict[str, str]) -> PredictedMention:
    return PredictedMention(
        entity=SEIZURE_FREQUENCY,
        text=anchor.text,
        attributes=_with_cui(anchor, attributes),
        evidence=anchor.evidence,
        component_owner="deterministic",
    )


def extract_seizure_frequency(
    letter: ExectLetter,
    ablation: AblationConfig = DEFAULT_ABLATION,
) -> PredictedLetter:
    """Extract all SeizureFrequency mentions from one letter.

    Steps:
    1. Apply anchor rules; resolve overlapping anchor spans (longest wins).
    2. Apply rate/seizure-free/change rules; resolve overlapping attribute
       extractions (most attributes wins).
    3. Associate each attribute extraction with its nearest anchor.
    4. Emit one PredictedMention per anchor that gathered attributes.
    """
    text = letter.note_text
    anchors = _collect_anchors(text, ablation)
    attributes = _collect_attributes(text, ablation)

    # Safety filter: evidence must be a verbatim substring.
    anchors = [a for a in anchors if a.evidence and a.evidence in text]
    attributes = [a for a in attributes if a.evidence and a.evidence in text]

    pairs = associate_attributes_to_anchors(anchors, attributes, text)
    mentions = tuple(
        _mention_from_pair(anchor, merged)
        for anchor, attrs in pairs
        for merged in (_apply_implied_count(anchor, attrs, text),)
        if not _is_bare_nonzero_count(merged)
    )
    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=mentions,
        diagnostics={
            "rule_set": "deterministic_sf_v2_anchor_association",
            "anchor_count": len(anchors),
            "attribute_count": len(attributes),
            "mention_count": len(mentions),
        },
    )


def run_on_letters(
    letters: Sequence[ExectLetter],
    ablation: AblationConfig = DEFAULT_ABLATION,
) -> list[PredictedLetter]:
    """Run the SF deterministic pipeline on every letter."""
    return [extract_seizure_frequency(letter, ablation) for letter in letters]
