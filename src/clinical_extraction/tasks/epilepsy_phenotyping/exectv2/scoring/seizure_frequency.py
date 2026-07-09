from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping, Sequence

from pydantic import BaseModel

from clinical_extraction.core.scoring import PRF1, multiset_prf1, sum_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    POINT_RANGE_TRIPLES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    _letters_by_id,
    benchmark_config_for,
    score_entity,
    semantic_config_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.normalize import (
    canonicalize_attribute_value,
    canonicalize_point_range_attributes,
)

_SF_POINT_RANGE_TRIPLES = POINT_RANGE_TRIPLES["SeizureFrequency"]

# Rate-bearing attributes for active-rate fidelity: seizure counts and cadence,
# excluding dates / point-in-time so this isolates burden magnitude, not timing.
_FREQUENCY_RATE_ATTRIBUTES: frozenset[str] = frozenset(
    {
        "NumberOfSeizures",
        "LowerNumberOfSeizures",
        "UpperNumberOfSeizures",
        "NumberOfTimePeriods",
        "LowerNumberOfTimePeriods",
        "UpperNumberOfTimePeriods",
        "TimePeriod",
    }
)


class FrequencyStateScores(BaseModel):
    model_config = {"frozen": True}

    clinical_headline: PRF1
    state_profile: PRF1
    state_profile_directional: PRF1
    state_profile_direction_deconf: PRF1
    state_profile_magnitude: PRF1
    active_rate: PRF1
    active_rate_fidelity: PRF1
    seizure_free: PRF1
    unknown: PRF1
    exact_semantic: PRF1
    benchmark_with_cui: PRF1


def score_frequency_state(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> FrequencyStateScores:
    return FrequencyStateScores(
        clinical_headline=_score_frequency_state_component(
            gold_letters,
            pred_letters,
            "clinical_headline",
        ),
        state_profile=_score_frequency_state_profile(gold_letters, pred_letters),
        state_profile_directional=_score_frequency_state_profile_directional(
            gold_letters, pred_letters
        ),
        state_profile_direction_deconf=_score_frequency_state_profile_direction_deconf(
            gold_letters, pred_letters
        ),
        state_profile_magnitude=_score_frequency_state_profile_magnitude(
            gold_letters, pred_letters
        ),
        active_rate=_score_frequency_state_component(gold_letters, pred_letters, "active-rate"),
        active_rate_fidelity=_score_frequency_active_rate_fidelity(gold_letters, pred_letters),
        seizure_free=_score_frequency_state_component(gold_letters, pred_letters, "seizure-free"),
        unknown=_score_frequency_state_component(gold_letters, pred_letters, "unknown"),
        exact_semantic=score_entity(
            gold_letters,
            pred_letters,
            "SeizureFrequency",
            semantic_config_for("SeizureFrequency"),
        ).per_item,
        benchmark_with_cui=score_entity(
            gold_letters,
            pred_letters,
            "SeizureFrequency",
            benchmark_config_for("SeizureFrequency"),
        ).per_item,
    )


def _score_frequency_state_component(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    component: str,
) -> PRF1:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _frequency_state_keys(
                gold_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in gold_by_id
                else (),
                component,
            ),
            _frequency_state_keys(
                pred_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in pred_by_id
                else (),
                component,
            ),
        )
        for letter_id in all_ids
    )


def _score_frequency_state_profile(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PRF1:
    """Clinical-recovery SF metric: the per-letter *state profile*, type-agnostic.

    The ``clinical_headline`` key conditions every fact on the annotator's chosen
    seizure-type CUI and on gold's exhaustive per-type multiplicity (the same seizure
    type tagged once with a numeric rate and again with a qualitative change). Both are
    convention choices, not clinical recovery: a correct frequency statement keyed to a
    clinically-valid but *different* CUI granularity scores zero. This companion scores
    the clinical question Gan asks — *which seizure-frequency states does this letter
    describe?* — by keying only the (change-aware) state, deduplicated per letter. The
    honest SF clinical number is the bracket [clinical_headline, state_profile]; the gap
    is the seizure-type-CUI granularity + multiplicity tax. See
    ``docs/research/exectv2_sf_representation_not_recall_2026-06-28.md``.
    """

    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _frequency_state_profile_keys(
                gold_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in gold_by_id
                else ()
            ),
            _frequency_state_profile_keys(
                pred_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in pred_by_id
                else ()
            ),
        )
        for letter_id in all_ids
    )


def _frequency_state_profile_keys(annotations: Iterable[ExectAnnotation]) -> list[Hashable]:
    """Per-letter presence set of change-aware states (deduplicated, type-agnostic)."""

    return list(dict.fromkeys(frequency_state_faithful(a.attributes) for a in annotations))


def _score_frequency_state_profile_directional(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PRF1:
    """SF-2: direction-sensitive companion to :func:`_score_frequency_state_profile`.

    Same per-letter presence-set shape, but keyed by :func:`frequency_state_directional`
    instead of :func:`frequency_state_faithful`, so a directional disagreement
    (e.g. gold ``increased`` vs. predicted ``same``) counts as a miss instead of
    both collapsing to the same ``changed`` key and scoring a match.
    """

    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _frequency_state_profile_directional_keys(
                gold_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in gold_by_id
                else ()
            ),
            _frequency_state_profile_directional_keys(
                pred_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in pred_by_id
                else ()
            ),
        )
        for letter_id in all_ids
    )


def _frequency_state_profile_directional_keys(
    annotations: Iterable[ExectAnnotation],
) -> list[Hashable]:
    """Per-letter presence set of direction-aware states (deduplicated, type-agnostic)."""

    return list(dict.fromkeys(frequency_state_directional(a.attributes) for a in annotations))


def _frequency_state_keys(
    annotations: Iterable[ExectAnnotation],
    component: str,
) -> list[Hashable]:
    keys: list[Hashable] = []
    for annotation in annotations:
        state = _frequency_state(annotation.attributes)
        if component != "clinical_headline" and component != state:
            continue
        keys.append((_frequency_type_key(annotation), state))
    return list(dict.fromkeys(keys))


def _score_frequency_active_rate_fidelity(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PRF1:
    """Among active-rate states, does the seizure-burden magnitude agree?

    The ``clinical_headline`` key collapses every active rate to the single token
    ``active-rate``, so "2-4 per month" and "6-9 per week" score as the same key.
    This companion keys the rate-bearing attributes (counts + cadence, excluding
    dates) per seizure type, so a wrong rate among matched active states is no
    longer silently forgiven.
    """

    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _frequency_active_rate_keys(
                gold_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in gold_by_id
                else (),
            ),
            _frequency_active_rate_keys(
                pred_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in pred_by_id
                else (),
            ),
        )
        for letter_id in all_ids
    )


def _frequency_active_rate_keys(annotations: Iterable[ExectAnnotation]) -> list[Hashable]:
    keys: list[Hashable] = []
    for annotation in annotations:
        if _frequency_state(annotation.attributes) != "active-rate":
            continue
        canonical_attrs = canonicalize_point_range_attributes(
            annotation.attributes, _SF_POINT_RANGE_TRIPLES
        )
        rate = tuple(
            sorted(
                (key, canonicalize_attribute_value(key, value))
                for key, value in canonical_attrs.items()
                if key in _FREQUENCY_RATE_ATTRIBUTES and value
            )
        )
        keys.append((_frequency_type_key(annotation), rate))
    return list(dict.fromkeys(keys))


def _frequency_type_key(annotation: ExectAnnotation) -> Hashable:
    cui = annotation.attributes.get("CUI")
    if cui:
        return ("cui", canonicalize_attribute_value("CUI", cui))
    return ("phrase", normalize_phrase(annotation.text))


def _count_based_state(attributes: Mapping[str, str]) -> str | None:
    """seizure-free / active-rate from counts alone, or ``None`` when none is present.

    A zero count is only ``seizure-free`` when *no positive count co-occurs*: a
    variable rate such as ``LowerNumberOfSeizures=0``/``UpperNumberOfSeizures=3`` is
    an *active* rate (the patient still has seizures), not seizure freedom. The
    prior ``any(value == "0")``-first test gave the zero precedence over the
    positive bound and mislabelled such ranges as seizure-free.
    """

    count_values = [
        attributes.get("NumberOfSeizures"),
        attributes.get("LowerNumberOfSeizures"),
        attributes.get("UpperNumberOfSeizures"),
    ]
    if any(value not in (None, "", "0") for value in count_values):
        return "active-rate"
    if any(value == "0" for value in count_values if value is not None):
        return "seizure-free"
    return None


def _frequency_state(attributes: Mapping[str, str]) -> str:
    """Convention-strict 3-way state used by ``clinical_headline`` (count-only).

    Kept count-only and ``FrequencyChange``-blind to preserve the frozen benchmark
    key. The change-aware taxonomy lives in :func:`frequency_state_faithful`.
    """

    return _count_based_state(attributes) or "unknown"


def frequency_state_faithful(attributes: Mapping[str, str]) -> str:
    """Change-aware 4-way state: seizure-free / active-rate / changed / unknown.

    Unlike the count-only :func:`_frequency_state`, this credits a reported
    *qualitative change* in seizure frequency (``FrequencyChange``: more/fewer/
    improved/worse) as its own ``changed`` state instead of silently collapsing it to
    ``unknown``. A concrete count takes precedence over a change descriptor (a numeric
    rate or zero is the more specific signal). This matches the adapter round-trip
    taxonomy (``llm/.../facts.py``) and is the basis for the type-agnostic
    ``state_profile`` clinical metric and the GEPA SF feedback labels.
    """

    state = _count_based_state(attributes)
    if state is not None:
        return state
    if attributes.get("FrequencyChange"):
        return "changed"
    return "unknown"


def frequency_state_directional(attributes: Mapping[str, str]) -> str:
    """Direction-aware state: like :func:`frequency_state_faithful`, but the
    undifferentiated ``changed`` bucket is replaced by gold's own five-way
    ``FrequencyChange`` vocabulary (``increased``/``decreased``/``frequent``/
    ``infrequent``/``same``) instead of collapsing every qualitative change to
    one label.

    SF-2 (2026-07-02): the SF Phase 6 changed-class row-adjudication found
    direction neither modelled nor scored at *either* layer -- ``FrequencyChange``
    is a first-class, populated contract attribute (``closed_vocab``
    Decreased/Frequent/Increased/Infrequent/Same) that both the old headline key
    and ``frequency_state_faithful`` discarded down to a single presence flag, so
    a deterioration and an improvement scored identically (direction recovered in
    0/12 gold-directional agreements on the adjudicated sample). See
    ``docs/experiments/exectv2/seizure_frequency/exectv2_sf_changed_class_row_analysis_2026-06-29.md``
    section 10's "direction-aware SF schema + direction-sensitive metric"
    recommendation, which this implements on the scoring side (no re-prediction
    needed -- ``FrequencyChange`` is already populated in stored predictions).
    """

    state = _count_based_state(attributes)
    if state is not None:
        return state
    change = attributes.get("FrequencyChange")
    if change:
        return change.lower()
    return "unknown"


# ---------------------------------------------------------------------------
# SF-3 (2026-07-08): deconflated direction/magnitude projection.
#
# The gold ``FrequencyChange`` vocab (Appendix L987, "Aligned" per
# ``docs/research/exectv2_sf_guideline_alignment_2026-06-10.md``) mixes
# change-direction (Increased/Decreased/Same) and frequency-magnitude
# (Frequent/Infrequent) on a single axis. ``frequency_state_directional`` scores
# both on that one axis, so a model that reads "Frequent/Infrequent" as a
# magnitude (with no direction claim) is scored as a direction *error* relative
# to gold that asserted a direction. The two projections below split the axis so
# the contribution of each dimension can be attributed separately. This is a
# scoring-side rekey over frozen predictions; gold is not re-annotated. See the
# SF-3 predeclaration under
# ``docs/experiments/exectv2/seizure_frequency/``.
# ---------------------------------------------------------------------------

# Values that carry a change-direction signal on the ``FrequencyChange`` axis.
_DIRECTION_VALUES: frozenset[str] = frozenset({"increased", "decreased", "same"})

# Values that carry a frequency-magnitude signal on the ``FrequencyChange`` axis.
_MAGNITUDE_VALUES: frozenset[str] = frozenset({"frequent", "infrequent"})


def frequency_state_direction_deconf(attributes: Mapping[str, str]) -> str:
    """Direction-only projection of the change-aware state.

    Like :func:`frequency_state_directional`, but the magnitude labels
    (``Frequent``/``Infrequent``) project to the direction-neutral ``same``
    bucket rather than their own value: a magnitude statement carries no
    direction signal. Count-bearing states pass through unchanged (the
    deconflation only affects the qualitative-change bucket), so this metric is
    comparable in shape to ``state_profile_directional`` and differs only on the
    magnitude-label rows.
    """

    state = _count_based_state(attributes)
    if state is not None:
        return state
    change = (attributes.get("FrequencyChange") or "").lower()
    if change in _DIRECTION_VALUES:
        return change
    # Magnitude labels (and any unexpected value) carry no direction signal.
    return "same" if change in _MAGNITUDE_VALUES else "unknown"


def frequency_state_magnitude(attributes: Mapping[str, str]) -> str:
    """Magnitude-only projection of the change-aware state.

    The orthogonal complement of :func:`frequency_state_direction_deconf`:
    only the magnitude labels (``Frequent``/``Infrequent``) populate this axis;
    change-direction labels, count-bearing states, and the absent case all
    project to ``none``.
    """

    if _count_based_state(attributes) is not None:
        return "none"
    change = (attributes.get("FrequencyChange") or "").lower()
    if change in _MAGNITUDE_VALUES:
        return change
    return "none"


def _score_frequency_state_profile_direction_deconf(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PRF1:
    """SF-3 direction-only companion: per-letter presence set keyed by
    :func:`frequency_state_direction_deconf`, with the magnitude labels projected
    to the direction-neutral ``same`` bucket."""

    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _frequency_state_profile_direction_deconf_keys(
                gold_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in gold_by_id
                else ()
            ),
            _frequency_state_profile_direction_deconf_keys(
                pred_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in pred_by_id
                else ()
            ),
        )
        for letter_id in all_ids
    )


def _frequency_state_profile_direction_deconf_keys(
    annotations: Iterable[ExectAnnotation],
) -> list[Hashable]:
    """Per-letter presence set of direction-only states (deduplicated)."""

    return list(
        dict.fromkeys(frequency_state_direction_deconf(a.attributes) for a in annotations)
    )


def _score_frequency_state_profile_magnitude(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PRF1:
    """SF-3 magnitude-only companion: per-letter presence set keyed by
    :func:`frequency_state_magnitude`. Only the ``Frequent``/``Infrequent`` labels
    populate this axis; everything else is ``none``."""

    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _frequency_state_profile_magnitude_keys(
                gold_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in gold_by_id
                else ()
            ),
            _frequency_state_profile_magnitude_keys(
                pred_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in pred_by_id
                else ()
            ),
        )
        for letter_id in all_ids
    )


def _frequency_state_profile_magnitude_keys(
    annotations: Iterable[ExectAnnotation],
) -> list[Hashable]:
    """Per-letter presence set of magnitude-only states (deduplicated)."""

    return list(dict.fromkeys(frequency_state_magnitude(a.attributes) for a in annotations))
