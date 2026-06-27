from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Hashable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from pydantic import BaseModel

from clinical_extraction.core.scoring import PRF1, multiset_prf1, prf1_from_counts, sum_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.evaluation import (
    DEFAULT_BENCHMARK_IGNORE_ATTRIBUTES,
    SEIZURE_FREQUENCY_BENCHMARK_IGNORE_ATTRIBUTES,
    benchmark_ignore_attributes_for,
    semantic_ignore_attributes_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    annotation_clinical_concepts,
    collapse_concepts_to_most_specific,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.normalize import (
    canonicalize_attribute_value,
)

# CUIPhrase mirrors the annotated phrase, so including it in the match key is
# redundant with the phrase itself. CUI is a normalization artifact the benchmark
# paper disregarded in inter-annotator agreement; callers who want a CUI-strict
# match can drop it from this set.
DEFAULT_IGNORE_ATTRIBUTES: frozenset[str] = DEFAULT_BENCHMARK_IGNORE_ATTRIBUTES

_PRESCRIPTION_ENTITY = "Prescription"

# Families whose clinical_headline key list applies `dict.fromkeys` and therefore
# collapses same-unit duplicates within a letter. Investigations and Prescription
# append per-occurrence instead (their 136→136 / 206→193 headline deltas are
# unit filtering, not de-duplication), so a repeated unit there is counted.
_DEDUPING_HEADLINE_ENTITIES: frozenset[str] = frozenset({"Diagnosis", "SeizureFrequency"})

#: A mention whose entire headline unit was already contributed by an earlier
#: mention in the same letter+family that the headline *collapses* (Diagnosis,
#: SeizureFrequency) — a Redundant-Convention Duplicate the model is not charged
#: for. Badge: "removed from headline scoring - deduplicated".
HEADLINE_DEDUPLICATED = "deduplicated"
#: A mention that shares its headline unit with another mention in a family the
#: headline counts *per occurrence* (Investigations, Prescription) — a
#: Distinct-Assertion Duplicate the headline genuinely counts. Badge:
#: "distinct assertion — counted".
HEADLINE_DISTINCT_ASSERTION = "distinct_assertion"


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

SF_GUIDELINE_IGNORED: frozenset[str] = SEIZURE_FREQUENCY_BENCHMARK_IGNORE_ATTRIBUTES
SF_BENCHMARK = MatchConfig(include_attributes=True, ignore_attributes=SF_GUIDELINE_IGNORED)
SF_SEMANTIC = MatchConfig(
    include_attributes=True,
    ignore_attributes=semantic_ignore_attributes_for("SeizureFrequency"),
)


def benchmark_ignore_for(entity: str) -> frozenset[str]:
    """Attributes ignored under the benchmark (with-CUI) match for ``entity``."""
    return benchmark_ignore_attributes_for(entity)


def semantic_ignore_for(entity: str) -> frozenset[str]:
    """Attributes ignored under the CUI-dropped semantic match for ``entity``."""
    return semantic_ignore_attributes_for(entity)


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


class OverallScore(BaseModel):
    model_config = {"frozen": True}

    per_item: PRF1
    per_letter: PRF1
    per_entity: dict[str, EntityScore]


class SourceNearEntityDiagnostic(BaseModel):
    model_config = {"frozen": True}

    entity: str
    overlap: PRF1
    attribute_agreement_tp: int
    attribute_agreement_total: int
    attribute_agreement_rate: float


class SourceNearOverallDiagnostic(BaseModel):
    model_config = {"frozen": True}

    overlap: PRF1
    attribute_agreement_tp: int
    attribute_agreement_total: int
    attribute_agreement_rate: float


class SourceNearDiagnostic(BaseModel):
    model_config = {"frozen": True}

    overall: SourceNearOverallDiagnostic
    per_entity: dict[str, SourceNearEntityDiagnostic]


class ClinicalRecoveryPRF1(BaseModel):
    """Precision/recall where recall may use a wider candidate pool than precision."""

    model_config = {"frozen": True}

    tp: int
    precision_tp: int
    recall_tp: int
    fp: int
    fn: int
    pred_count: int
    gold_count: int
    precision: float
    recall: float
    f1: float


class ConceptIdentityScores(BaseModel):
    model_config = {"frozen": True}

    entity: str
    concept_only: ClinicalRecoveryPRF1
    concept_negation: ClinicalRecoveryPRF1
    concept_assertion: ClinicalRecoveryPRF1


def match_key(annotation: ExectAnnotation, config: MatchConfig = PHRASE_AND_FEATURES) -> Hashable:
    phrase = normalize_phrase(annotation.text)
    if not config.include_attributes:
        return (annotation.entity, phrase)
    attributes = tuple(
        sorted(
            (k, canonicalize_attribute_value(k, v))
            for k, v in annotation.attributes.items()
            if k not in config.ignore_attributes
        )
    )
    return (annotation.entity, phrase, attributes)


def score_concept_identity(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entity: str,
) -> ConceptIdentityScores:
    """Score a Class-B clinical concept with entity-agnostic recall.

    Recall is credited from any predicted entity whose normalized clinical
    concept maps to ``entity``. Precision is home-tagged: only predictions emitted
    on ``entity`` enter the precision denominator.
    """

    return ConceptIdentityScores(
        entity=entity,
        concept_only=_score_concept_identity(gold_letters, pred_letters, entity, "concept"),
        concept_negation=_score_concept_identity(
            gold_letters,
            pred_letters,
            entity,
            "negation",
        ),
        concept_assertion=_score_concept_identity(
            gold_letters,
            pred_letters,
            entity,
            "assertion",
        ),
    )


def clinical_headline_unit_keys(
    entity: str,
    annotations: Iterable[ExectAnnotation],
    note_text: str = "",
) -> list[Hashable]:
    """The clinical-recovery headline unit keys the chips score for one family's
    annotations in a letter. ``len(...)`` is that family's headline-unit count
    (de-duplicated for Diagnosis/SeizureFrequency, per-occurrence for
    Investigations/Prescription). Non-target families have no headline unit."""
    if entity == "SeizureFrequency":
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
            _frequency_state_keys,
        )

        return _frequency_state_keys(annotations, "clinical_headline")
    if entity == "Diagnosis":
        return _concept_keys(annotations, "Diagnosis", "concept")
    if entity == "Investigations":
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.investigations import (
            _investigation_component_keys,
        )

        return _investigation_component_keys(annotations, "clinical_headline")
    if entity == _PRESCRIPTION_ENTITY:
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.prescription import (
            _prescription_component_keys,
        )

        return _prescription_component_keys(annotations, "clinical_headline", note_text)
    return []


def headline_duplicate_tags(
    annotations: Sequence[ExectAnnotation],
    note_text: str = "",
) -> list[str | None]:
    """Per-mention duplicate tag against the clinical-recovery headline unit.

    Returns a list aligned with ``annotations``: ``HEADLINE_DEDUPLICATED`` (a
    Redundant-Convention Duplicate the headline collapses), ``HEADLINE_DISTINCT_
    ASSERTION`` (a Distinct-Assertion Duplicate the headline counts per
    occurrence), or ``None`` (the sole/representative carrier of its headline unit,
    or a mention that contributes no headline unit at all). Tagging is grouped by
    family so each family's collapse semantics apply within that family.
    """
    annotations = list(annotations)
    per_mention_keys = [
        clinical_headline_unit_keys(a.entity, [a], note_text) for a in annotations
    ]
    tags: list[str | None] = [None] * len(annotations)
    by_entity: dict[str, list[int]] = {}
    for index, annotation in enumerate(annotations):
        by_entity.setdefault(annotation.entity, []).append(index)
    for entity, indices in by_entity.items():
        if entity in _DEDUPING_HEADLINE_ENTITIES:
            seen: set[Hashable] = set()
            for index in indices:
                keys = per_mention_keys[index]
                if keys and all(key in seen for key in keys):
                    tags[index] = HEADLINE_DEDUPLICATED
                seen.update(keys)
        else:
            counts = Counter(key for index in indices for key in per_mention_keys[index])
            for index in indices:
                keys = per_mention_keys[index]
                if keys and any(counts[key] >= 2 for key in keys):
                    tags[index] = HEADLINE_DISTINCT_ASSERTION
    return tags


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


def score_overall(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entities: Sequence[str],
    config_for: Callable[[str], MatchConfig],
) -> OverallScore:
    """Score all requested entities with micro-averaged overall PRF1.

    Overall per-item F1 sums true/false positives and false negatives over every
    mention of every entity. Overall per-letter F1 sums the same counts over
    every ``(letter, entity)`` presence cell, so a letter can contribute once per
    entity. The benchmark reports only an overall point estimate; this helper
    keeps the same micro-average headline while also returning the per-entity
    breakdown used by the Phase 6 all-entity audit.
    """

    per_entity = {
        entity: score_entity(gold_letters, pred_letters, entity, config_for(entity))
        for entity in entities
    }
    return OverallScore(
        per_item=sum_prf1(score.per_item for score in per_entity.values()),
        per_letter=sum_prf1(score.per_letter for score in per_entity.values()),
        per_entity=per_entity,
    )


def source_near_diagnostic(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entities: Sequence[str],
    config_for: Callable[[str], MatchConfig],
) -> SourceNearDiagnostic:
    """Report same-entity substring-overlap and attribute agreement.

    This is diagnostic only. It answers whether a prediction selected a source-
    near phrase for the same ExECT entity, then separately checks whether the
    non-ignored attributes agree on those overlapped pairs.
    """

    per_entity = {
        entity: _source_near_entity(gold_letters, pred_letters, entity, config_for(entity))
        for entity in entities
    }
    overlap = sum_prf1(score.overlap for score in per_entity.values())
    attr_tp = sum(score.attribute_agreement_tp for score in per_entity.values())
    attr_total = sum(score.attribute_agreement_total for score in per_entity.values())
    overall = SourceNearOverallDiagnostic(
        overlap=overlap,
        attribute_agreement_tp=attr_tp,
        attribute_agreement_total=attr_total,
        attribute_agreement_rate=attr_tp / attr_total if attr_total else 0.0,
    )
    return SourceNearDiagnostic(overall=overall, per_entity=per_entity)


def _attribute_key(annotation: ExectAnnotation, config: MatchConfig) -> Hashable:
    return tuple(
        sorted(
            (k, canonicalize_attribute_value(k, v))
            for k, v in annotation.attributes.items()
            if k not in config.ignore_attributes
        )
    )


def _keys(annotations: Iterable[ExectAnnotation], config: MatchConfig) -> list[Hashable]:
    return [match_key(a, config) for a in annotations]


def _letters_by_id(letters: Sequence[ExectLetter]) -> dict[str, ExectLetter]:
    return {letter.letter_id: letter for letter in letters}


def _score_concept_identity(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entity: str,
    variant: str,
) -> ClinicalRecoveryPRF1:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())

    precision_tp = recall_tp = pred_count = gold_count = 0
    for letter_id in all_ids:
        gold_mentions = (
            gold_by_id[letter_id].entities(entity) if letter_id in gold_by_id else ()
        )
        pred_mentions = pred_by_id[letter_id].annotations if letter_id in pred_by_id else ()
        home_pred_mentions = (
            pred_by_id[letter_id].entities(entity) if letter_id in pred_by_id else ()
        )

        gold = Counter(_concept_keys(gold_mentions, entity, variant))
        recall_pool = Counter(_concept_keys(pred_mentions, entity, variant))
        home_pred = Counter(_concept_keys(home_pred_mentions, entity, variant))

        precision_tp += sum((gold & home_pred).values())
        recall_tp += sum((gold & recall_pool).values())
        pred_count += sum(home_pred.values())
        gold_count += sum(gold.values())

    return _clinical_recovery_prf1(
        precision_tp=precision_tp,
        recall_tp=recall_tp,
        pred_count=pred_count,
        gold_count=gold_count,
    )


def _concept_keys(
    annotations: Iterable[ExectAnnotation],
    entity: str,
    variant: str,
) -> list[Hashable]:
    concepts = collapse_concepts_to_most_specific(
        concept
        for annotation in annotations
        for concept in annotation_clinical_concepts(
            annotation.entity,
            annotation.text,
            annotation.attributes,
        )
        if concept.entity == entity
    )
    if variant == "concept":
        return list(dict.fromkeys(concept.concept_key for concept in concepts))
    if variant == "assertion":
        return [concept.assertion_key for concept in concepts]
    if variant == "negation":
        # Concept identity plus Negation only. Certainty is deliberately excluded
        # because it is deterministically projectable (guideline-rule defaulted),
        # whereas Negation is a genuine context-dependent clinical judgement that
        # the concept_only headline silently forgives.
        return list(
            dict.fromkeys(
                (
                    concept.entity,
                    concept.concept,
                    dict(concept.assertion).get("Negation", "Affirmed"),
                )
                for concept in concepts
            )
        )
    raise ValueError(f"Unknown concept identity variant {variant!r}")


def _clinical_recovery_prf1(
    *,
    precision_tp: int,
    recall_tp: int,
    pred_count: int,
    gold_count: int,
) -> ClinicalRecoveryPRF1:
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return ClinicalRecoveryPRF1(
        tp=recall_tp,
        precision_tp=precision_tp,
        recall_tp=recall_tp,
        fp=max(0, pred_count - precision_tp),
        fn=max(0, gold_count - recall_tp),
        pred_count=pred_count,
        gold_count=gold_count,
        precision=precision,
        recall=recall,
        f1=f1,
    )


def _source_near_entity(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entity: str,
    config: MatchConfig,
) -> SourceNearEntityDiagnostic:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())

    tp = fp = fn = 0
    attr_tp = attr_total = 0
    for letter_id in all_ids:
        gold_mentions = (
            list(gold_by_id[letter_id].entities(entity)) if letter_id in gold_by_id else []
        )
        pred_mentions = (
            list(pred_by_id[letter_id].entities(entity)) if letter_id in pred_by_id else []
        )
        used_pred: set[int] = set()

        for gold in gold_mentions:
            pred_index = _first_overlapping_prediction(gold, pred_mentions, used_pred)
            if pred_index is None:
                fn += 1
                continue

            tp += 1
            used_pred.add(pred_index)
            attr_total += 1
            if _attribute_key(gold, config) == _attribute_key(pred_mentions[pred_index], config):
                attr_tp += 1

        fp += len(pred_mentions) - len(used_pred)

    attr_rate = attr_tp / attr_total if attr_total else 0.0
    return SourceNearEntityDiagnostic(
        entity=entity,
        overlap=prf1_from_counts(tp, fp, fn),
        attribute_agreement_tp=attr_tp,
        attribute_agreement_total=attr_total,
        attribute_agreement_rate=attr_rate,
    )


def _first_overlapping_prediction(
    gold: ExectAnnotation,
    predictions: Sequence[ExectAnnotation],
    used_pred: set[int],
) -> int | None:
    gold_phrase = normalize_phrase(gold.text)
    if not gold_phrase:
        return None
    for i, pred in enumerate(predictions):
        if i in used_pred:
            continue
        pred_phrase = normalize_phrase(pred.text)
        if pred_phrase and (gold_phrase in pred_phrase or pred_phrase in gold_phrase):
            return i
    return None
