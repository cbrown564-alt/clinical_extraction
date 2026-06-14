"""Held-out-family cross-validation promotion gate.

This is checklist step 1 of the 2026-06-14 next-phase brief, unblocked by the
sharpened boundary taxonomy. The brief's Insight 1 is that the architecture that
"won" validation (unanimous-exact consensus, the only run to clear 700/750) was
the worst generalizer of the LLM-centred options: its aggregate validation gain
was borrowed from deterministic, validation-tuned components and did not survive
holdout. The prescription is to *promote candidates on within-validation
cross-family stability* (hold out clinical families, not just rows) so a
candidate cannot be promoted on a number that will not survive distribution
shift.

This module operationalizes that. It consumes the per-family transition summary
(``family_transitions.summarize_transitions_by_family``), restricts to the
partitioning boundary bands (which, unlike the overlapping qualitative families,
exactly partition the scored rows), and runs leave-one-band-out CV:

- For each fold the held-out band's own transitions are the *generalization*
  estimate; the union of the remaining bands is the *retained* (selection) set.
- A candidate is ``gap_robust`` only if no held-out band silently regresses
  (net Purist gain >= 0) and, where it makes label changes, its changed-label
  precision clears the selector-quality bar. This folds Insight 2 into the gate:
  changed-label precision is the trigger, not raw agreement or aggregate count.

The aggregate net gain is reported alongside the worst held-out fold precisely so
the two can be compared: a positive aggregate with a regressing held-out band is
exactly the overfit signature the brief warns against.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.labels import BOUNDARY_BANDS

# A changed-label precision below this means a band breaks at least as many
# already-correct rows as it fixes among the rows it touches. Below the bar a
# band's changes are net selector noise (Insight 2). Parameterised so a future
# freeze can tighten it without editing the gate.
DEFAULT_MIN_CHANGED_LABEL_PRECISION = 0.5


def _empty_fold() -> dict[str, int]:
    return {
        "rows": 0,
        "changed_labels": 0,
        "wrong_to_correct": 0,
        "correct_to_wrong": 0,
    }


def _accumulate(into: dict[str, int], stats: Mapping[str, Any]) -> None:
    into["rows"] += int(stats.get("rows") or 0)
    into["changed_labels"] += int(stats.get("changed_labels") or 0)
    into["wrong_to_correct"] += int(stats.get("wrong_to_correct") or 0)
    into["correct_to_wrong"] += int(stats.get("correct_to_wrong") or 0)


def _finalize(stats: Mapping[str, int]) -> dict[str, Any]:
    changed = stats["changed_labels"]
    wrong_to_correct = stats["wrong_to_correct"]
    correct_to_wrong = stats["correct_to_wrong"]
    return {
        "rows": stats["rows"],
        "changed_labels": changed,
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "net_purist_gain": wrong_to_correct - correct_to_wrong,
        "changed_label_precision": (
            round(wrong_to_correct / changed, 4) if changed else None
        ),
    }


def summarize_family_holdout_cv(
    summary_by_family: Mapping[str, Any],
    *,
    fold_families: Sequence[str] = BOUNDARY_BANDS,
    min_changed_label_precision: float = DEFAULT_MIN_CHANGED_LABEL_PRECISION,
) -> dict[str, Any]:
    """Leave-one-band-out promotion verdict over a per-family transition summary.

    ``summary_by_family`` is the dict returned by
    ``family_transitions.summarize_transitions_by_family`` (it must carry a
    ``families`` map). Only the partitioning ``fold_families`` are used as folds,
    so the held-out/retained split is an exact partition of the scored rows; any
    overlapping qualitative families in the input are ignored here on purpose.

    Returns the aggregate over the partition, a per-fold held-out-vs-retained
    breakdown, the worst held-out fold, and a ``gap_robust`` verdict with
    human-readable ``reasons`` for any gate failure.
    """

    families = summary_by_family.get("families")
    if not isinstance(families, Mapping):
        raise ValueError("summary_by_family must contain a 'families' mapping")

    present = [name for name in fold_families if name in families]
    aggregate = _empty_fold()
    for name in present:
        _accumulate(aggregate, families[name])
    aggregate_final = _finalize(aggregate)

    folds: list[dict[str, Any]] = []
    for held_out in present:
        held_stats = _empty_fold()
        _accumulate(held_stats, families[held_out])
        retained_stats = _empty_fold()
        for other in present:
            if other != held_out:
                _accumulate(retained_stats, families[other])
        folds.append(
            {
                "held_out_family": held_out,
                "held_out": _finalize(held_stats),
                "retained": _finalize(retained_stats),
            }
        )

    reasons: list[str] = []
    regressing: list[str] = []
    low_precision: list[str] = []
    worst_fold: dict[str, Any] | None = None
    for fold in folds:
        held = fold["held_out"]
        name = fold["held_out_family"]
        if worst_fold is None or held["net_purist_gain"] < worst_fold["net_purist_gain"]:
            worst_fold = {"family": name, "net_purist_gain": held["net_purist_gain"]}
        if held["net_purist_gain"] < 0:
            regressing.append(name)
        precision = held["changed_label_precision"]
        if (
            held["changed_labels"] > 0
            and precision is not None
            and precision < min_changed_label_precision
        ):
            low_precision.append(name)

    if not present:
        reasons.append("no partitioning fold families present; cannot assess holdout")
    if aggregate_final["net_purist_gain"] <= 0:
        reasons.append(
            f"aggregate net Purist gain {aggregate_final['net_purist_gain']} <= 0"
        )
    if regressing:
        reasons.append(
            "held-out bands regress (net Purist gain < 0): " + ", ".join(regressing)
        )
    if low_precision:
        reasons.append(
            "held-out bands below changed-label precision "
            f"{min_changed_label_precision}: " + ", ".join(low_precision)
        )

    gap_robust = bool(present) and not reasons

    return {
        "fold_kind": "leave_one_boundary_band_out",
        "min_changed_label_precision": min_changed_label_precision,
        "fold_families_present": present,
        "fold_families_absent": [
            name for name in fold_families if name not in families
        ],
        "aggregate": aggregate_final,
        "folds": folds,
        "worst_held_out_fold": worst_fold,
        "regressing_held_out_families": regressing,
        "low_precision_held_out_families": low_precision,
        "gap_robust": gap_robust,
        "reasons": reasons,
        "note": (
            "Promotion gate: a candidate is gap_robust only if every held-out "
            "boundary band holds up (net Purist gain >= 0 and, where it changes "
            "labels, changed-label precision >= the bar). A positive aggregate "
            "with a regressing held-out band is the overfit signature the "
            "next-phase brief warns against."
        ),
    }
