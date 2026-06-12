from __future__ import annotations

import re
from collections.abc import Hashable, Iterable, Sequence
from dataclasses import dataclass, field

from pydantic import BaseModel

from clinical_extraction.core.scoring import PRF1, multiset_prf1, prf1_from_counts, sum_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter

# CUIPhrase mirrors the annotated phrase, so including it in the match key is
# redundant with the phrase itself. CUI is a normalization artifact the benchmark
# paper disregarded in inter-annotator agreement; callers who want a CUI-strict
# match can drop it from this set.
DEFAULT_IGNORE_ATTRIBUTES: frozenset[str] = frozenset({"CUIPhrase"})

_QUOTES = str.maketrans("", "", "\"'“”‘’‚‛")
_WHITESPACE = re.compile(r"\s+")


def normalize_phrase(text: str) -> str:
    """Normalize an annotated phrase for label matching.

    Gold phrases store spaces as hyphens and sometimes carry quotes (including
    mid-phrase) and case variation. Normalization makes phrase comparison robust
    to those surface differences without relying on (drifted) character offsets."""

    lowered = text.translate(_QUOTES).replace("-", " ").lower()
    return _WHITESPACE.sub(" ", lowered).strip()


@dataclass(frozen=True)
class MatchConfig:
    """How a predicted mention is judged equal to a gold mention.

    ``include_attributes=True`` requires the full feature set to agree (the
    benchmark's "with all features" validation). ``ignore_attributes`` drops
    attributes that are redundant or out of scope for the match."""

    include_attributes: bool = True
    ignore_attributes: frozenset[str] = field(default=DEFAULT_IGNORE_ATTRIBUTES)


PHRASE_ONLY = MatchConfig(include_attributes=False)
PHRASE_AND_FEATURES = MatchConfig(include_attributes=True)

# Guideline v9 (L17/L19): Certainty and Negation are NOT SeizureFrequency
# features ("We are not allocating Certainty to Seizure Frequency…"; "Negation
# should be assigned to all concepts except Seizure Frequency…"). CUIPhrase
# mirrors the phrase. So the benchmark-comparable SF match ignores these three
# and keeps CUI + semantic attributes. Gold SF mentions that carry
# Certainty/Negation are annotation noise (see the SF guideline-alignment audit).
SF_GUIDELINE_IGNORED: frozenset[str] = frozenset({"CUIPhrase", "Certainty", "Negation"})
SF_BENCHMARK = MatchConfig(include_attributes=True, ignore_attributes=SF_GUIDELINE_IGNORED)
# CUI is now emitted by the deterministic family via deterministic/lexicon.py;
# dropping it (SF_SEMANTIC) scores the semantic attributes alone. The two configs
# coincide today because the lexicon assigns the correct CUI to every
# semantically-matching mention.
SF_SEMANTIC = MatchConfig(
    include_attributes=True,
    ignore_attributes=SF_GUIDELINE_IGNORED | frozenset({"CUI"}),
)


# ── Per-entity match policy (Phase 6 all-9 generalization) ────────────────────
#
# The SF configs above pin one entity's policy. Phase 6 scores all nine entities,
# and each entity's ignored-attribute set is read from its guideline scope, NOT
# inherited from SF (protocol §2). Two facts drive the per-entity policy:
#
#   - CUIPhrase is always ignored (mirrors the phrase; redundant with the key).
#   - Certainty and Negation are in scope for every entity EXCEPT SeizureFrequency
#     (guideline v9 L17/L19: Certainty is not allocated to SF, and Negation is
#     assigned to "all concepts except Seizure Frequency"). Investigations and
#     Prescription never carry them at all (not in their legal-attribute set), so
#     keeping them in the ignore set is a no-op there; listing SF explicitly is
#     what matters.
#
# CUI is kept in the benchmark headline (the published "with all features"
# reading) and dropped in the semantic variant — the same two-tier shape the SF
# audit used, now per entity. The LLM-only family emits no CUI (discoveries D3),
# so its with-CUI headline collapses to 0 on every entity by construction; that
# divergence is surfaced, not hidden (protocol §2), and the semantic config is
# its real attribute-level quality.
_SF_ENTITY_NAME = "SeizureFrequency"


def benchmark_ignore_for(entity: str) -> frozenset[str]:
    """Attributes ignored under the benchmark (with-CUI) match for ``entity``."""
    if entity == _SF_ENTITY_NAME:
        return SF_GUIDELINE_IGNORED
    return DEFAULT_IGNORE_ATTRIBUTES


def semantic_ignore_for(entity: str) -> frozenset[str]:
    """Attributes ignored under the CUI-dropped semantic match for ``entity``."""
    return benchmark_ignore_for(entity) | frozenset({"CUI"})


def benchmark_config_for(entity: str) -> MatchConfig:
    """The benchmark-comparable (with-CUI, all-features) config for ``entity``."""
    return MatchConfig(include_attributes=True, ignore_attributes=benchmark_ignore_for(entity))


def semantic_config_for(entity: str) -> MatchConfig:
    """The CUI-dropped semantic config for ``entity`` (attribute-level quality)."""
    return MatchConfig(include_attributes=True, ignore_attributes=semantic_ignore_for(entity))


class EntityScore(BaseModel):
    model_config = {"frozen": True}

    entity: str
    per_item: PRF1
    per_letter: PRF1


def match_key(annotation: ExectAnnotation, config: MatchConfig = PHRASE_AND_FEATURES) -> Hashable:
    phrase = normalize_phrase(annotation.text)
    if not config.include_attributes:
        return (annotation.entity, phrase)
    attributes = tuple(
        sorted(
            (k, v)
            for k, v in annotation.attributes.items()
            if k not in config.ignore_attributes
        )
    )
    return (annotation.entity, phrase, attributes)


def _keys(annotations: Iterable[ExectAnnotation], config: MatchConfig) -> list[Hashable]:
    return [match_key(a, config) for a in annotations]


def _letters_by_id(letters: Sequence[ExectLetter]) -> dict[str, ExectLetter]:
    return {letter.letter_id: letter for letter in letters}


def score_entity(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entity: str,
    config: MatchConfig = PHRASE_AND_FEATURES,
) -> EntityScore:
    """Score predicted mentions of ``entity`` against gold, per-item and per-letter.

    Per-item (every mention): multiset match within each letter, summed across
    letters into a micro-averaged PRF1. Matching is per-letter so identical
    phrases in different letters never cross-match.

    Per-letter (at least one correct mention): a letter is a true positive when
    gold has the entity and at least one predicted mention matched; a false
    negative when gold has it and none matched; a false positive when gold lacks
    it but a prediction asserts it."""

    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())

    per_letter_item_scores: list[PRF1] = []
    letter_tp = letter_fp = letter_fn = 0

    for letter_id in all_ids:
        gold_mentions = gold_by_id[letter_id].entities(entity) if letter_id in gold_by_id else ()
        pred_mentions = pred_by_id[letter_id].entities(entity) if letter_id in pred_by_id else ()

        item_score = multiset_prf1(_keys(gold_mentions, config), _keys(pred_mentions, config))
        per_letter_item_scores.append(item_score)

        gold_present = len(gold_mentions) > 0
        pred_present = len(pred_mentions) > 0
        any_correct = item_score.tp > 0

        if gold_present and any_correct:
            letter_tp += 1
        elif gold_present:
            letter_fn += 1
        elif pred_present:
            letter_fp += 1

    return EntityScore(
        entity=entity,
        per_item=sum_prf1(per_letter_item_scores),
        per_letter=prf1_from_counts(letter_tp, letter_fp, letter_fn),
    )
