"""Tests for the precision-gated per-band decision selector (brief step 2).

These pin the behaviour the brief depends on: changed-label precision is the
*selector* trigger, not raw agreement. A boundary band whose switches break at
least as many already-correct rows as they fix (low precision / negative net
gain) has its switches suppressed back to the baseline, while a clean, high
-precision band keeps them. The leave-one-out estimate guards against a band
being credited for a single switch whose own outcome set its gate.
"""

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_transitions import (
    CONSENSUS_PATHS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.precision_gated_selector import (
    summarize_precision_gated_selector,
)


def _row(
    *,
    band: str,
    transition: str,
    label_changed: bool,
    baseline_correct: bool,
    candidate_correct: bool,
) -> dict:
    """A consensus-shaped replay row reduced to what the selector reads."""

    return {
        "hidden_families": [band],
        "consensus_transition": {
            "purist_transition": transition,
            "label_changed": label_changed,
        },
        "baseline_comparison": {"purist_correct": baseline_correct},
        "consensus_comparison": {"purist_correct": candidate_correct},
    }


def _switch(band: str, transition: str) -> dict:
    """A switched row whose baseline/candidate correctness follows the transition."""

    baseline_correct = transition in ("correct_to_correct", "correct_to_wrong")
    candidate_correct = transition in ("correct_to_correct", "wrong_to_correct")
    return _row(
        band=band,
        transition=transition,
        label_changed=True,
        baseline_correct=baseline_correct,
        candidate_correct=candidate_correct,
    )


def _summarize(rows: list[dict], **kwargs) -> dict:
    return summarize_precision_gated_selector(rows, **CONSENSUS_PATHS, **kwargs)


def test_clean_band_is_allowed_and_keeps_its_switches() -> None:
    rows = [_switch("band_daily", "wrong_to_correct") for _ in range(6)]
    result = _summarize(rows)

    assert result["bands"]["band_daily"]["allowed"] is True
    assert result["bands"]["band_daily"]["changed_label_precision"] == 1.0
    assert result["switches_kept"] == 6
    assert result["gated_net_purist_gain"] == 6
    # Gated matches the ungated candidate when every band is clean.
    assert result["gated_purist_correct"] == result["raw_candidate_purist_correct"]


def test_low_precision_band_is_suppressed_back_to_baseline() -> None:
    # band_weekly: 5 fixes, 8 breaks -> precision 5/13 and net -3. The selector
    # must revert it, recovering the 8 broken rows; band_daily stays.
    rows = [_switch("band_weekly", "wrong_to_correct") for _ in range(5)]
    rows += [_switch("band_weekly", "correct_to_wrong") for _ in range(8)]
    rows += [_switch("band_daily", "wrong_to_correct") for _ in range(6)]
    result = _summarize(rows)

    assert result["bands"]["band_weekly"]["allowed"] is False
    assert result["bands"]["band_daily"]["allowed"] is True
    assert result["allowed_bands"] == ["band_daily"]
    assert result["suppressed_bands"] == ["band_weekly"]
    # Raw candidate rides band_daily's +6 over band_weekly's -3 -> net +3.
    assert result["raw_candidate_net_purist_gain"] == 3
    # Gated keeps only band_daily's clean +6.
    assert result["gated_net_purist_gain"] == 6
    assert result["regressions_suppressed"] == 8
    assert result["fixes_forgone"] == 5
    assert result["switches_kept"] == 6
    assert result["switches_suppressed"] == 13


def test_category_neutral_churn_is_suppressed() -> None:
    # A band whose only switches leave the Purist bucket unchanged: precision 0,
    # net 0. The "should never be a change" case -> suppressed as neutral churn.
    rows = [_switch("band_unknown", "wrong_to_wrong") for _ in range(4)]
    result = _summarize(rows)

    assert result["bands"]["band_unknown"]["allowed"] is False
    assert result["neutral_churn_suppressed"] == 4
    assert result["switches_kept"] == 0
    assert result["gated_net_purist_gain"] == 0


def test_unswitched_rows_are_untouched_by_the_gate() -> None:
    rows = [
        _row(
            band="band_monthly",
            transition="correct_to_correct",
            label_changed=False,
            baseline_correct=True,
            candidate_correct=True,
        )
        for _ in range(3)
    ]
    result = _summarize(rows)

    assert result["switches_total"] == 0
    assert result["bands"] == {}
    assert result["gated_purist_correct"] == 3
    assert result["gated_net_purist_gain"] == 0


def test_leave_one_out_drops_a_single_unbacked_switch() -> None:
    # One lone fix in a band: the band-level policy would allow it, but with the
    # row left out there is no evidence, so LOO refuses it. This is the honesty
    # check against a band credited for the very switch that set its gate.
    rows = [_switch("band_submonthly", "wrong_to_correct")]
    result = _summarize(rows)

    assert result["bands"]["band_submonthly"]["allowed"] is True
    assert result["gated_net_purist_gain"] == 1
    assert result["leave_one_out"]["switches_kept"] == 0
    assert result["leave_one_out"]["gated_net_purist_gain"] == 0
    assert result["leave_one_out"]["net_gain_sign_matches_band_policy"] is False


def test_leave_one_out_keeps_a_well_supported_band() -> None:
    rows = [_switch("band_daily", "wrong_to_correct") for _ in range(6)]
    result = _summarize(rows)

    # Removing any one of six unanimous fixes still leaves precision 1.0.
    assert result["leave_one_out"]["switches_kept"] == 6
    assert result["leave_one_out"]["gated_net_purist_gain"] == 6
    assert result["leave_one_out"]["net_gain_sign_matches_band_policy"] is True


def test_custom_precision_bar_is_honoured() -> None:
    # Precision 0.7 band: passes the default 0.5 bar, fails a tightened 0.8.
    rows = [_switch("band_monthly", "wrong_to_correct") for _ in range(7)]
    rows += [_switch("band_monthly", "correct_to_wrong") for _ in range(3)]
    assert _summarize(rows)["bands"]["band_monthly"]["allowed"] is True
    tightened = _summarize(rows, min_changed_label_precision=0.8)
    assert tightened["bands"]["band_monthly"]["allowed"] is False
    assert tightened["switches_kept"] == 0
