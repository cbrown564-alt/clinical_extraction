"""Phase-4 standing guardrail: F2, optimal bipartite matching for source_near.

``_source_near_entity`` (``scoring/match.py``) previously walked gold mentions
in list order and greedily claimed the first unused, phrase-overlapping
prediction (``_first_overlapping_prediction``). Because the compatibility
predicate is a bidirectional substring check, a short generic gold phrase
(e.g. "seizure") can overlap the same prediction a longer, more specific gold
phrase (e.g. "focal seizures with altered awareness") would also match --
whichever gold happened to be processed first claimed it, silently dropping
the specific gold's rightful match (see
``docs/research/exectv2_pipeline_assumption_audit_phase4_guardrail_2026-07-02.md``,
item F2). ``_match_gold_to_predictions`` replaces the per-gold greedy walk
with a whole-letter maximum-cardinality bipartite match (augmenting paths),
tie-broken toward list-position proximity so repeated same-name mentions
(distinguished only by attributes, not text -- e.g. two "Carbamazepine" gold
spans against two "Carbamazepine" predictions differing only in dose) still
pair in document order.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    _match_gold_to_predictions,
)


def _ann(text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity="X", text=text, attributes=dict(attrs))


def test_generic_gold_phrase_no_longer_steals_a_specific_golds_match() -> None:
    """Regression case: dev140 EA0143 (SeizureFrequency).

    Gold: a generic "seizure" fact and a specific "focal seizures with altered
    awareness" fact. Predictions: the matching specific phrase, plus an
    unrelated "secondarily generalised seizures" phrase the generic gold also
    substring-overlaps. The old greedy walk processed the generic gold first,
    let it claim the specific prediction, and left the specific gold
    unmatched (1 of 2 gold facts recovered). The fix must recover both.
    """

    gold = [
        _ann("seizure", NumberOfSeizures="0"),
        _ann("focal-seizures-with-altered-awareness", NumberOfSeizures="0"),
    ]
    predictions = [
        _ann("focal seizures with altered awareness", NumberOfSeizures="0"),
        _ann("secondarily generalised seizures", NumberOfSeizures="0"),
    ]

    matching = _match_gold_to_predictions(gold, predictions)

    assert len(matching) == 2, "both gold facts should be recoverable, not just one"
    # The specific gold must pair with the specific (matching) prediction.
    assert matching[1] == 0
    # The generic gold is left with the only remaining compatible prediction.
    assert matching[0] == 1


def test_old_greedy_walk_would_have_dropped_the_specific_gold() -> None:
    """Proves the fix is load-bearing: reconstruct the pre-F2 greedy walk on
    the same case and show it recovers only 1 of 2 facts."""

    def normalize(text: str) -> str:
        return text.replace("-", " ").lower()

    gold_phrases = ["seizure", "focal seizures with altered awareness"]
    pred_phrases = [
        normalize("focal seizures with altered awareness"),
        normalize("secondarily generalised seizures"),
    ]

    used: set[int] = set()
    matched = 0
    for gold_phrase in gold_phrases:
        for i, pred_phrase in enumerate(pred_phrases):
            if i in used:
                continue
            if gold_phrase in pred_phrase or pred_phrase in gold_phrase:
                used.add(i)
                matched += 1
                break

    assert matched == 1, "the old greedy walk should have stranded the specific gold"


def test_repeated_same_name_mentions_pair_in_document_order() -> None:
    """Two mentions of the same drug, distinguished only by dose (an
    attribute, not text), must pair in the same relative order both lists
    were built in -- not get gratuitously swapped by the matcher.
    """

    gold = [
        _ann("Medication:-Carbamazepine-100mg-am", DrugDose="100"),
        _ann("Carbamazepine", DrugDose="200"),
    ]
    predictions = [
        _ann("Carbamazepine", DrugDose="100"),
        _ann("Carbamazepine", DrugDose="200"),
    ]

    matching = _match_gold_to_predictions(gold, predictions)

    assert matching == {0: 0, 1: 1}


def test_maximum_cardinality_achieved_when_greedy_claim_order_would_strand_a_pair() -> None:
    """Synthetic adversarial case requiring an augmenting-path reassignment.

    Gold A overlaps both predictions; gold B overlaps only prediction 0. A
    matcher that greedily claims prediction 0 for A (processed first) without
    ever reconsidering that claim strands B, even though a valid maximum
    matching (A-P2, B-P1) exists.
    """

    gold = [_ann("seizure"), _ann("focal seizure type")]
    predictions = [_ann("focal seizure type outcome"), _ann("a seizure was noted")]

    matching = _match_gold_to_predictions(gold, predictions)

    assert len(matching) == 2


def test_no_predictions_yields_empty_matching() -> None:
    assert _match_gold_to_predictions([_ann("seizure")], []) == {}


def test_no_gold_yields_empty_matching() -> None:
    assert _match_gold_to_predictions([], [_ann("seizure")]) == {}


def test_empty_phrase_gold_never_matches() -> None:
    gold = [_ann("")]
    predictions = [_ann("seizure")]
    assert _match_gold_to_predictions(gold, predictions) == {}
