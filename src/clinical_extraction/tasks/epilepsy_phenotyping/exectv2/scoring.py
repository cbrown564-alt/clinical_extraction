from __future__ import annotations

import re
from collections.abc import Callable, Hashable, Iterable, Sequence
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
_LOWERCASE_ATTRIBUTE_VALUES: frozenset[str] = frozenset({"DrugName", "DoseUnit"})
_PRESCRIPTION_ENTITY = "Prescription"
_AS_REQUIRED = "as_required"
_MEDICATION_NAME_ALIASES: dict[str, str] = {
    "brivetiracetam": "brivaracetam",
    "brivitiracetam": "brivaracetam",
    "carbamazapine": "carbamazepine",
    "carbmazapine": "carbamazepine",
    "epilim": "sodium-valproate",
    "epilim-chrono": "sodium-valproate",
    "eplim": "sodium-valproate",
    "episenta": "sodium-valproate",
    "eslicarbazepineacetate": "eslicarbazepine",
    "keppra": "levetiracetam",
    "lamictal": "lamotrigine",
    "phenobarbitone": "phenobarbital",
    "sodiumvalproate": "sodium-valproate",
    "tegretaol": "carbamazepine",
    "tegretol": "carbamazepine",
    "zobisamide": "zonisamide",
    "zonismaide": "zonisamide",
}
_PRESCRIPTION_SOURCE_FREQUENCY = re.compile(
    r"\b(?:prn|p\.r\.n\.|as\s+required|when\s+required|as\s+needed|rescue|"
    r"bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+daily|od|o\.d\.|"
    r"once\s+(?:a\s+)?day|once\s+daily|daily|mane|nocte|nightly|"
    r"morning|afternoon|evening|am|pm|at\s+night|tds|t\.d\.s\.|tid|"
    r"three\s+times\s+(?:a\s+)?day|qds|q\.d\.s\.|qid|"
    r"four\s+times\s+(?:a\s+)?day)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_FUTURE_PLAN = re.compile(
    r"\b(?:commence|start(?:ing)?|increase|increasing|titrate|titration|"
    r"reduce|reducing|target\s+dose|future|option|consider|suggest|"
    r"planned|plan|every\s+(?:two\s+)?weeks|every\s+fortnight|until)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_WEIGHT_BASED_DOSE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g|grams?)\s*/?\s*kg(?:\s*/?\s*day)?\b",
    re.IGNORECASE,
)


def normalize_phrase(text: str) -> str:
    """Normalize an annotated phrase for label matching.

    Gold phrases store spaces as hyphens and sometimes carry quotes (including
    mid-phrase) and case variation. Normalization makes phrase comparison robust
    to those surface differences without relying on (drifted) character offsets."""

    lowered = text.translate(_QUOTES).replace("-", " ").lower()
    return _WHITESPACE.sub(" ", lowered).strip()


def canonicalize_attribute_value(key: str, value: str) -> str:
    """Apply format-only canonicalization before attribute matching.

    This deliberately cannot create a missing attribute or infer a clinical
    category. It only removes quote/whitespace noise and normalizes attributes
    where case is a spelling artifact under the ExECTv2 contract.
    """

    normalized = _WHITESPACE.sub(" ", str(value).translate(_QUOTES)).strip()
    if key in _LOWERCASE_ATTRIBUTE_VALUES:
        normalized = normalized.lower()
    return normalized


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


class PrescriptionComponentScores(BaseModel):
    model_config = {"frozen": True}

    clinical_headline: PRF1
    name: PRF1
    dose: PRF1
    frequency: PRF1
    source_stated_frequency: PRF1
    guideline_defaulted_frequency: PRF1
    complete: PRF1
    ordinary_complete: PRF1
    rescue_regimen: PRF1
    future_medication: PRF1
    weight_based_dosing: PRF1


class PrescriptionBenchmarkProjectionScores(BaseModel):
    model_config = {"frozen": True}

    phrase_scope: PRF1
    semantic_without_cui: PRF1
    benchmark_with_cui: PRF1
    clinical_medication_identity: PRF1
    drugname_cui_projection: PRF1
    source_stated_frequency: PRF1
    guideline_defaulted_frequency: PRF1


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


def canonicalize_medication_name(value: str) -> str:
    """Normalize medication spelling/brand variants for clinical component scoring."""

    normalized = normalize_phrase(value).replace(" ", "-")
    return _MEDICATION_NAME_ALIASES.get(normalized, normalized)


def _prescription_component_key(annotation: ExectAnnotation, component: str) -> Hashable | None:
    attrs = annotation.attributes
    if component == "name":
        value = attrs.get("DrugName")
        return canonicalize_medication_name(value) if value else None
    if component == "dose":
        dose = attrs.get("DrugDose")
        unit = attrs.get("DoseUnit")
        if not dose or not unit:
            return None
        return (
            canonicalize_attribute_value("DrugDose", dose),
            canonicalize_attribute_value("DoseUnit", unit),
        )
    if component == "frequency":
        frequency = attrs.get("Frequency")
        return canonicalize_attribute_value("Frequency", frequency).lower() if frequency else None
    if component == "source_stated_frequency":
        frequency = _prescription_component_key(annotation, "frequency")
        return frequency if frequency and _has_source_stated_frequency(annotation) else None
    if component == "guideline_defaulted_frequency":
        frequency = _prescription_component_key(annotation, "frequency")
        return frequency if frequency and not _has_source_stated_frequency(annotation) else None
    if component == "complete":
        name = _prescription_component_key(annotation, "name")
        dose = _prescription_component_key(annotation, "dose")
        frequency = _prescription_component_key(annotation, "frequency")
        if name is None or dose is None or frequency is None:
            return None
        return (name, *dose, frequency)
    if component == "ordinary_complete":
        complete = _prescription_component_key(annotation, "complete")
        frequency = _prescription_component_key(annotation, "frequency")
        if (
            complete is None
            or frequency == _AS_REQUIRED
            or _is_future_medication(annotation)
            or _is_weight_based_dosing(annotation)
        ):
            return None
        return complete
    if component == "rescue_regimen":
        name = _prescription_component_key(annotation, "name")
        frequency = _prescription_component_key(annotation, "frequency")
        if (
            name is None
            or frequency != _AS_REQUIRED
            or _is_future_medication(annotation)
            or _is_weight_based_dosing(annotation)
        ):
            return None
        return (name, _AS_REQUIRED)
    if component == "clinical_headline":
        rescue = _prescription_component_key(annotation, "rescue_regimen")
        if rescue is not None:
            return ("rescue", *rescue)
        ordinary = _prescription_component_key(annotation, "ordinary_complete")
        if ordinary is not None:
            return ("ordinary", *ordinary)
        return None
    if component == "future_medication":
        if not _is_future_medication(annotation):
            return None
        name = _prescription_component_key(annotation, "name")
        return (name or normalize_phrase(annotation.text), normalize_phrase(annotation.text))
    if component == "weight_based_dosing":
        if not _is_weight_based_dosing(annotation):
            return None
        name = _prescription_component_key(annotation, "name")
        return (name or normalize_phrase(annotation.text), normalize_phrase(annotation.text))
    raise ValueError(f"Unknown prescription component {component!r}")


def score_prescription_components(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PrescriptionComponentScores:
    """Score Prescription clinical headline and diagnostic component layers.

    These diagnostics deliberately ignore mention phrase scope and benchmark CUI
    projection. The clinical headline combines ordinary complete regimen tuples
    with dose-optional rescue regimens; supporting component scores remain
    diagnostic so partial or projection-specific gains are not overstated.
    """

    components = {
        component: _score_prescription_component(gold_letters, pred_letters, component)
        for component in (
            "clinical_headline",
            "name",
            "dose",
            "frequency",
            "source_stated_frequency",
            "guideline_defaulted_frequency",
            "complete",
            "ordinary_complete",
            "rescue_regimen",
            "future_medication",
            "weight_based_dosing",
        )
    }
    return PrescriptionComponentScores(**components)


def score_prescription_benchmark_projection(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PrescriptionBenchmarkProjectionScores:
    """Score Prescription benchmark-format sublayers without changing the headline.

    The projection table separates clinical medication identity from exact
    phrase scope, benchmark-facing DrugName/CUI conventions, and defaulted
    frequency projection. It is diagnostic: gains here should not be reported as
    pure clinical extraction gains.
    """

    return PrescriptionBenchmarkProjectionScores(
        phrase_scope=score_entity(
            gold_letters,
            pred_letters,
            _PRESCRIPTION_ENTITY,
            PHRASE_ONLY,
        ).per_item,
        semantic_without_cui=score_entity(
            gold_letters,
            pred_letters,
            _PRESCRIPTION_ENTITY,
            semantic_config_for(_PRESCRIPTION_ENTITY),
        ).per_item,
        benchmark_with_cui=score_entity(
            gold_letters,
            pred_letters,
            _PRESCRIPTION_ENTITY,
            benchmark_config_for(_PRESCRIPTION_ENTITY),
        ).per_item,
        clinical_medication_identity=_score_prescription_component(
            gold_letters,
            pred_letters,
            "name",
        ),
        drugname_cui_projection=_score_prescription_drugname_cui_projection(
            gold_letters,
            pred_letters,
        ),
        source_stated_frequency=_score_prescription_component(
            gold_letters,
            pred_letters,
            "source_stated_frequency",
        ),
        guideline_defaulted_frequency=_score_prescription_component(
            gold_letters,
            pred_letters,
            "guideline_defaulted_frequency",
        ),
    )


def _has_source_stated_frequency(annotation: ExectAnnotation) -> bool:
    return bool(_PRESCRIPTION_SOURCE_FREQUENCY.search(annotation.text))


def _is_future_medication(annotation: ExectAnnotation) -> bool:
    return bool(_PRESCRIPTION_FUTURE_PLAN.search(annotation.text))


def _is_weight_based_dosing(annotation: ExectAnnotation) -> bool:
    return bool(_PRESCRIPTION_WEIGHT_BASED_DOSE.search(annotation.text))


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


def _prescription_component_keys(
    annotations: Iterable[ExectAnnotation],
    component: str,
) -> list[Hashable]:
    keys: list[Hashable] = []
    for annotation in annotations:
        key = _prescription_component_key(annotation, component)
        if key is not None:
            keys.append(key)
    return keys


def _prescription_drugname_cui_keys(
    annotations: Iterable[ExectAnnotation],
) -> list[Hashable]:
    keys: list[Hashable] = []
    for annotation in annotations:
        attrs = annotation.attributes
        drug_name = attrs.get("DrugName")
        cui = attrs.get("CUI")
        if not drug_name or not cui:
            continue
        keys.append(
            (
                canonicalize_attribute_value("DrugName", drug_name),
                canonicalize_attribute_value("CUI", cui),
            )
        )
    return keys


def _letters_by_id(letters: Sequence[ExectLetter]) -> dict[str, ExectLetter]:
    return {letter.letter_id: letter for letter in letters}


def _score_prescription_component(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    component: str,
) -> PRF1:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _prescription_component_keys(
                gold_by_id[letter_id].entities(_PRESCRIPTION_ENTITY)
                if letter_id in gold_by_id
                else (),
                component,
            ),
            _prescription_component_keys(
                pred_by_id[letter_id].entities(_PRESCRIPTION_ENTITY)
                if letter_id in pred_by_id
                else (),
                component,
            ),
        )
        for letter_id in all_ids
    )


def _score_prescription_drugname_cui_projection(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PRF1:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _prescription_drugname_cui_keys(
                gold_by_id[letter_id].entities(_PRESCRIPTION_ENTITY)
                if letter_id in gold_by_id
                else ()
            ),
            _prescription_drugname_cui_keys(
                pred_by_id[letter_id].entities(_PRESCRIPTION_ENTITY)
                if letter_id in pred_by_id
                else ()
            ),
        )
        for letter_id in all_ids
    )


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
