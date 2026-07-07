"""Tests for the external-signal feature construction used by the calibration redesign.

These cover the deterministic core (the cross-model agreement cluster metric and the
self-consistency entropy statistic) with small hand-built fixtures, plus a join-sanity
smoke test gated on the dev140 artifacts being present. The portability category of the
rule families here is ``gan2026_specific`` (replay over saved same-core model-swap and
multi-temperature dev140 artifacts), matching the calibration strengthening plan.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability import (
    external_signals,
)


def _mention(entity: str, text: str, attributes: dict | None = None) -> dict:
    return {"entity": entity, "text": text, "attributes": attributes or {}}


def _row(letter_id: str, mentions: list[dict]) -> dict:
    return {"letter_id": letter_id, "predicted_mentions": mentions}


# --------------------------------------------------------------------------- #
# Cross-model agreement cluster metric
# --------------------------------------------------------------------------- #


def test_largest_identical_cluster_is_three_when_all_models_agree() -> None:
    """Three models producing the same headline keyset cluster at agreement=3."""

    mentions = [_mention("SeizureFrequency", "monthly", {"NumberOfSeizures": "1"})]
    rows = {
        "gpt41mini": [_row("EA0001", mentions)],
        "deepseek": [_row("EA0001", mentions)],
        "qwen36": [_row("EA0001", mentions)],
    }
    table = external_signals.cross_model_agreement_table(rows)
    assert table[("EA0001", "SeizureFrequency")] == {
        "agreement": 3,
        "risk": 0.0,
    }


def test_largest_identical_cluster_is_one_when_all_three_differ() -> None:
    """Three mutually-distinct keysets give the smallest cluster size, agreement=1."""

    rows = {
        "gpt41mini": [
            _row("EA0001", [_mention("SeizureFrequency", "daily", {"NumberOfSeizures": "30"})])
        ],
        "deepseek": [
            _row("EA0001", [_mention("SeizureFrequency", "weekly", {"NumberOfSeizures": "4"})])
        ],
        "qwen36": [
            _row("EA0001", [_mention("SeizureFrequency", "none", {"NumberOfSeizures": "0"})])
        ],
    }
    table = external_signals.cross_model_agreement_table(rows)
    assert table[("EA0001", "SeizureFrequency")]["agreement"] == 1
    # Risk is rounded to 4 decimals; tolerate that precision.
    assert table[("EA0001", "SeizureFrequency")]["risk"] == pytest.approx(2 / 3, abs=1e-4)


def test_two_of_three_agreement_cluster_is_two() -> None:
    """When two models agree and one differs, the largest cluster has size 2."""

    shared = [_mention("SeizureFrequency", "weekly", {"NumberOfSeizures": "4"})]
    rows = {
        "gpt41mini": [_row("EA0001", shared)],
        "deepseek": [_row("EA0001", shared)],
        "qwen36": [
            _row("EA0001", [_mention("SeizureFrequency", "daily", {"NumberOfSeizures": "30"})])
        ],
    }
    table = external_signals.cross_model_agreement_table(rows)
    assert table[("EA0001", "SeizureFrequency")]["agreement"] == 2
    # Risk is rounded to 4 decimals; tolerate that precision.
    assert table[("EA0001", "SeizureFrequency")]["risk"] == pytest.approx(1 / 3, abs=1e-4)


def test_cross_model_agreement_covers_all_target_families() -> None:
    """The table reports a risk per (letter, family) for every target family."""

    mentions = [
        _mention("Diagnosis", "epilepsy"),
        _mention("SeizureFrequency", "monthly", {"NumberOfSeizures": "1"}),
        _mention("Prescription", "levetiracetam"),
        _mention("Investigations", "eeg"),
    ]
    rows = {cand: [_row("EA0001", mentions)] for cand in ("gpt41mini", "deepseek", "qwen36")}
    table = external_signals.cross_model_agreement_table(rows)
    for family in ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations"):
        assert ("EA0001", family) in table


# --------------------------------------------------------------------------- #
# Self-consistency entropy
# --------------------------------------------------------------------------- #


def test_self_consistency_entropy_is_zero_when_all_runs_agree() -> None:
    """Four temperature runs producing identical state sets give entropy 0."""

    mentions = [_mention("SeizureFrequency", "monthly", {"NumberOfSeizures": "1"})]
    runs = [_row("EA0001", mentions) for _ in range(4)]
    table = external_signals.self_consistency_entropy_table(runs)
    assert table[("EA0001", "SeizureFrequency")] == pytest.approx(0.0)


def test_self_consistency_entropy_is_maximal_when_runs_all_differ() -> None:
    """Four runs each producing a distinct state maximizes the normalized entropy."""

    states = [
        ("one", "1"),
        ("two", "2"),
        ("three", "3"),
        ("four", "4"),
    ]
    runs = [
        _row("EA0001", [_mention("SeizureFrequency", txt, {"NumberOfSeizures": n})])
        for txt, n in states
    ]
    table = external_signals.self_consistency_entropy_table(runs)
    # Four equally-sized distinct clusters across 4 runs -> normalized entropy 1.0.
    assert table[("EA0001", "SeizureFrequency")] == pytest.approx(1.0, abs=1e-4)


def test_self_consistency_entropy_is_mid_when_runs_split_two_and_two() -> None:
    """A 2/2 split across four runs gives a normalized entropy of 0.5."""

    a = [_mention("SeizureFrequency", "monthly", {"NumberOfSeizures": "1"})]
    b = [_mention("SeizureFrequency", "daily", {"NumberOfSeizures": "30"})]
    runs = [_row("EA0001", a), _row("EA0001", a), _row("EA0001", b), _row("EA0001", b)]
    table = external_signals.self_consistency_entropy_table(runs)
    # Two equally-sized clusters across 4 runs -> H = log(2), normalized by log(4) = 0.5.
    assert table[("EA0001", "SeizureFrequency")] == pytest.approx(0.5, abs=1e-4)


# --------------------------------------------------------------------------- #
# AUROC (delegated to reliability_common, but pin the contract)
# --------------------------------------------------------------------------- #


def test_auroc_ranks_errors_above_corrects() -> None:
    """AUROC is 1.0 when every error has a strictly higher risk than every correct."""

    scores = [0.9, 0.8, 0.2, 0.1]
    labels = [True, True, False, False]  # True = error
    assert external_signals.auroc(scores, labels) == pytest.approx(1.0)


def test_auroc_is_half_for_uninformative_scores() -> None:
    """Tied scores across both classes give AUROC 0.5."""

    scores = [0.5, 0.5, 0.5, 0.5]
    labels = [True, True, False, False]
    assert external_signals.auroc(scores, labels) == pytest.approx(0.5)


# --------------------------------------------------------------------------- #
# Dev140 artifact join-sanity (smoke, gated on artifact presence)
# --------------------------------------------------------------------------- #


_REPO_ROOT = Path(__file__).resolve().parents[1]
_CROSS_MODEL_ARTIFACTS = (
    _REPO_ROOT / "experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140_20260625.jsonl",
    _REPO_ROOT / "experiments/exectv2_2call_no_sf_adjudicator_deepseek_dev140_20260625.jsonl",
    _REPO_ROOT / "experiments/exectv2_2call_no_sf_adjudicator_qwen36_dev140_20260625.jsonl",
)


@pytest.mark.skipif(
    not all(p.exists() for p in _CROSS_MODEL_ARTIFACTS),
    reason="dev140 same-core model-swap artifacts not available",
)
def test_cross_model_agreement_loads_dev140_with_non_degenerate_distribution() -> None:
    """The dev140 cross-model feature covers the shared letter space and is not
    degenerate at agreement=3 for every cell (the wall-transfer probe already showed
    a real spread on SeizureFrequency; this is the generalization sanity check)."""

    table = external_signals.load_dev140_cross_model_agreement()
    families = {family for _, family in table}
    assert families == {"Diagnosis", "SeizureFrequency", "Prescription", "Investigations"}
    agreement_counts = {
        3: 0,
        2: 0,
        1: 0,
    }
    for entry in table.values():
        agreement_counts[entry["agreement"]] = agreement_counts.get(entry["agreement"], 0) + 1
    # Not every cell is full agreement (would make the feature useless by construction).
    assert agreement_counts[3] < len(table)
