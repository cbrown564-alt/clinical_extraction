"""Tests for the held-out-family CV promotion gate (next-phase brief step 1).

These pin the behaviour the brief depends on: a candidate is only ``gap_robust``
when every held-out boundary band holds up, so an aggregate gain carried by a
couple of bands while another regresses is *not* promotable. They also pin the
held-out-vs-retained partition math, the changed-label precision gate (Insight
2), and graceful handling of inputs that carry no partitioning fold families.
"""

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_cv_promotion import (
    summarize_family_holdout_cv,
)


def _summary(**families: dict[str, int]) -> dict[str, object]:
    """Build a summary_by_family-shaped dict from per-family transition counts.

    Each family value supplies wrong_to_correct / correct_to_wrong / rows;
    changed_labels and net gain are derived the way the real summarizer does.
    """

    built = {}
    for name, raw in families.items():
        wtc = raw.get("wrong_to_correct", 0)
        ctw = raw.get("correct_to_wrong", 0)
        changed = raw.get("changed_labels", wtc + ctw)
        built[name] = {
            "rows": raw.get("rows", 1),
            "changed_labels": changed,
            "wrong_to_correct": wtc,
            "correct_to_wrong": ctw,
            "net_purist_gain": wtc - ctw,
            "changed_label_precision": (round(wtc / changed, 4) if changed else None),
        }
    return {"families": built, "total_rows": 0, "multilabel_note": "n/a"}


def test_gap_robust_when_every_held_out_band_holds_up() -> None:
    summary = _summary(
        band_daily={"wrong_to_correct": 6, "correct_to_wrong": 0},
        band_monthly={"wrong_to_correct": 4, "correct_to_wrong": 1},
    )
    result = summarize_family_holdout_cv(summary)

    assert result["gap_robust"] is True
    assert result["reasons"] == []
    assert result["regressing_held_out_families"] == []
    assert result["aggregate"]["net_purist_gain"] == 9


def test_regressing_held_out_band_blocks_promotion_despite_positive_aggregate() -> None:
    # band_daily carries the aggregate positive; band_weekly silently regresses.
    # This is the brief's overfit signature: promote-on-aggregate would pass,
    # held-out-family CV must not.
    summary = _summary(
        band_daily={"wrong_to_correct": 6, "correct_to_wrong": 0},
        band_weekly={"wrong_to_correct": 5, "correct_to_wrong": 8},
    )
    result = summarize_family_holdout_cv(summary)

    assert result["aggregate"]["net_purist_gain"] == 3  # positive overall
    assert result["gap_robust"] is False
    assert result["regressing_held_out_families"] == ["band_weekly"]
    assert result["worst_held_out_fold"] == {
        "family": "band_weekly",
        "net_purist_gain": -3,
    }
    assert any("regress" in reason for reason in result["reasons"])


def test_low_changed_label_precision_band_is_flagged() -> None:
    # Net gain is non-negative (3 vs 3) so it does not "regress", but precision
    # 0.5 sits at the bar; push one fix to a break to drop below it.
    summary = _summary(
        band_daily={"wrong_to_correct": 5, "correct_to_wrong": 0},
        band_monthly={"wrong_to_correct": 3, "correct_to_wrong": 3, "changed_labels": 9},
    )
    result = summarize_family_holdout_cv(summary)

    # band_monthly precision = 3/9 = 0.33 < 0.5
    assert "band_monthly" in result["low_precision_held_out_families"]
    assert result["gap_robust"] is False
    assert any("precision" in reason for reason in result["reasons"])


def test_held_out_and_retained_partition_the_other_bands() -> None:
    summary = _summary(
        band_zero={"wrong_to_correct": 1, "correct_to_wrong": 0},
        band_monthly={"wrong_to_correct": 2, "correct_to_wrong": 0},
        band_daily={"wrong_to_correct": 3, "correct_to_wrong": 0},
    )
    result = summarize_family_holdout_cv(summary)

    by_held = {fold["held_out_family"]: fold for fold in result["folds"]}
    monthly = by_held["band_monthly"]
    assert monthly["held_out"]["wrong_to_correct"] == 2
    # Retained is the union of the other two bands: 1 + 3.
    assert monthly["retained"]["wrong_to_correct"] == 4
    assert monthly["retained"]["net_purist_gain"] == 4


def test_nonpositive_aggregate_blocks_promotion() -> None:
    summary = _summary(
        band_daily={"wrong_to_correct": 2, "correct_to_wrong": 2},
    )
    result = summarize_family_holdout_cv(summary)

    assert result["aggregate"]["net_purist_gain"] == 0
    assert result["gap_robust"] is False
    assert any("aggregate" in reason for reason in result["reasons"])


def test_absent_fold_families_are_reported() -> None:
    summary = _summary(
        band_daily={"wrong_to_correct": 1, "correct_to_wrong": 0},
    )
    result = summarize_family_holdout_cv(summary)

    assert result["fold_families_present"] == ["band_daily"]
    assert "band_weekly" in result["fold_families_absent"]


def test_qualitative_only_summary_has_no_folds_and_is_not_robust() -> None:
    # Only overlapping qualitative families, no partitioning bands -> no CV folds.
    summary = _summary(
        cluster_burden={"wrong_to_correct": 5, "correct_to_wrong": 0},
    )
    result = summarize_family_holdout_cv(summary)

    assert result["fold_families_present"] == []
    assert result["folds"] == []
    assert result["gap_robust"] is False
    assert any("no partitioning fold families" in reason for reason in result["reasons"])


def test_missing_families_mapping_raises() -> None:
    with pytest.raises(ValueError):
        summarize_family_holdout_cv({"total_rows": 0})


def test_custom_precision_bar_is_honoured() -> None:
    summary = _summary(
        band_daily={"wrong_to_correct": 7, "correct_to_wrong": 3, "changed_labels": 10},
    )
    # precision 0.7: passes the default 0.5 bar but fails a tightened 0.8 bar.
    assert summarize_family_holdout_cv(summary)["gap_robust"] is True
    tightened = summarize_family_holdout_cv(summary, min_changed_label_precision=0.8)
    assert tightened["gap_robust"] is False
    assert "band_daily" in tightened["low_precision_held_out_families"]
