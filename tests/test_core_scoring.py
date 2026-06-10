from clinical_extraction.core.scoring import (
    f1_score,
    multiset_prf1,
    prf1_from_counts,
    safe_div,
    sum_prf1,
)


def test_safe_div_guards_zero_denominator() -> None:
    assert safe_div(1, 0) == 0.0
    assert safe_div(3, 4) == 0.75


def test_f1_is_harmonic_mean() -> None:
    assert f1_score(1.0, 1.0) == 1.0
    assert f1_score(0.5, 1.0) == 2 * 0.5 * 1.0 / 1.5
    assert f1_score(0.0, 0.0) == 0.0


def test_prf1_from_counts() -> None:
    score = prf1_from_counts(tp=8, fp=2, fn=4)
    assert score.precision == 0.8
    assert score.recall == 8 / 12
    assert score.gold_count == 12
    assert score.pred_count == 10


def test_multiset_prf1_perfect_match() -> None:
    score = multiset_prf1(["a", "b", "b"], ["b", "a", "b"])
    assert (score.tp, score.fp, score.fn) == (3, 0, 0)
    assert score.f1 == 1.0


def test_multiset_prf1_respects_multiplicity() -> None:
    # gold {a, b}; pred {b, b, c}: b matches once (tp), extra b + c are fp, a is fn
    score = multiset_prf1(["a", "b"], ["b", "b", "c"])
    assert (score.tp, score.fp, score.fn) == (1, 2, 1)


def test_multiset_prf1_counts_missing_and_spurious() -> None:
    score = multiset_prf1(["a", "b", "c"], ["a", "x"])
    assert (score.tp, score.fp, score.fn) == (1, 1, 2)


def test_sum_prf1_micro_averages() -> None:
    total = sum_prf1(
        [prf1_from_counts(2, 1, 0), prf1_from_counts(1, 0, 3)]
    )
    assert (total.tp, total.fp, total.fn) == (3, 1, 3)
