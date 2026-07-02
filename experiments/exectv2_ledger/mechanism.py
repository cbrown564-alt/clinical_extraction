"""The one mechanism/verdict taxonomy every family investigation now shares.

Consolidates what was previously reinvented per script:
``H1_CARDINALITY``/``H2_GENUINE_DIVERGENCE`` (SF, Rx/Inv evidence-recall
checks), a third ``NOT_SOURCE_NEAR_FN`` bucket (Dx evidence-recall check,
different again), and an ad hoc ``H3_ORTHOGRAPHIC`` bolted on afterward
(``exectv2_gold_inflation_mechanical_heuristic.py``) -- none of which agreed
with each other or lived in a shared module. New investigations should
extend this enum rather than invent a fifth local taxonomy.
"""

from __future__ import annotations

from enum import Enum


class Mechanism(str, Enum):
    """Why a clinical_headline disagreement row exists, once adjudicated."""

    #: The model actually failed to extract, normalize, or select correctly.
    GENUINE_MODEL_ERROR = "genuine_model_error"
    #: Gold tags a clinically-equivalent fact more than once (header +
    #: narrative restatement, per-type multiplicity); the model's single
    #: consolidated prediction is defensible. Was ``H1_CARDINALITY``.
    GOLD_MULTIPLICITY_CONSOLIDATION = "gold_multiplicity_consolidation"
    #: Gold or the source letter itself misspells the span; the model's
    #: structured attributes (CUI/dose/frequency) match exactly under a
    #: different surface string. Was the ad hoc ``H3_ORTHOGRAPHIC``.
    GOLD_ORTHOGRAPHIC_TYPO = "gold_orthographic_typo"
    #: Gold simply omits something present and correct in the source text.
    GOLD_UNDER_ANNOTATION = "gold_under_annotation"
    #: The scorer's matching mechanics (not the gold, not the model) produce
    #: a spurious disagreement -- e.g. a literal-substring diagnostic with no
    #: fuzzy tolerance, an offset-corruption artifact, a dedup-convention
    #: mismatch between family and metric.
    SCORER_MECHANICS_ARTIFACT = "scorer_mechanics_artifact"
    #: Genuinely disputable; documented human inter-annotator disagreement,
    #: not resolvable by re-reading the letter more carefully.
    IAA_AMBIGUITY = "iaa_ambiguity"
    #: Default. Must be driven toward zero, not silently left as the answer.
    UNADJUDICATED = "unadjudicated"


class Verdict(str, Enum):
    """Clinical adjudication verdict for a disagreement row.

    Reuses the 3-way taxonomy already proven across the Dx/SF/Rx/Inv
    adjudications, plus the ``UNADJUDICATED`` default this ledger adds so an
    un-reviewed row is visible rather than silently absent.
    """

    GOLD_RIGHT = "gold_right"
    MODEL_DEFENSIBLE = "model_defensible"
    BOTH_DEFENSIBLE = "both_defensible"
    UNADJUDICATED = "unadjudicated"


MECHANISM_VALUES: frozenset[str] = frozenset(m.value for m in Mechanism)
VERDICT_VALUES: frozenset[str] = frozenset(v.value for v in Verdict)
