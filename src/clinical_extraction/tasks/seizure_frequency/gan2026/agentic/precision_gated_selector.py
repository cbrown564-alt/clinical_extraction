"""Precision-gated, per-band decision selector for agentic replay surfaces.

This is checklist step 2 of the 2026-06-14 next-phase brief: *make changed-label
precision the primary selector gate at the decision layer, not just the audit
layer*. Step 1 (``family_cv_promotion``) made changed-label precision a
whole-candidate accept/reject *verdict*; it never changes what the pipeline
emits. This module turns the same signal into a *selector* that actually edits
the output.

The brief's Insight 2 is that three models agreeing tells you the row was easy,
not that the consensus label is correct on a hard row, and that the unanimity
mechanic quietly breaks 16-23 already-correct rows. The prescription: "make
changed-label precision the primary [gate], not raw count. Treat agreement as one
weak feature, not the trigger. A row where agents agree but the baseline was
already right should never be a change."

The decision rule here keeps agreement as the candidate-generating *feature* (the
upstream selector still proposes a switch) but only *applies* a proposed switch
inside boundary bands whose changed-label precision clears a bar and whose net
Purist gain is non-negative. Concretely, the gate is a frozen per-band allow-set:

- A band is ``allowed`` iff, over its switched rows, ``net_purist_gain >= 0`` and
  ``changed_label_precision >= min_changed_label_precision``.
- A proposed switch is kept only when its boundary band is allowed; otherwise the
  decision reverts to the baseline. Category-neutral churn (a label change that
  leaves the Purist bucket unchanged) drags a band's precision below the bar, so
  needless changes get suppressed too — exactly the "should never be a change"
  case.

Gold-leakage discipline mirrors the rest of the family-CV instrumentation. The
allow-set is *learned on validation* and meant to be frozen and applied to a held
-out split, so on validation the headline ``gated`` numbers are in-sample for the
policy. To keep the validation readout honest, ``leave_one_out`` recomputes every
row's gate while excluding that row's own outcome from its band's statistics, so a
band can never be credited for a switch whose own result set the gate. A
band-level gain that survives the leave-one-out estimate is the generalizing one.

The aggregation is schema-agnostic via key paths, identical in spirit to
``family_transitions.summarize_transitions_by_family``, so the structured-event
consensus replay and the V12 fresh-evidence reasoner share one implementation
(pass ``family_transitions.CONSENSUS_PATHS`` / ``FRESH_EVIDENCE_PATHS``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_cv_promotion import (
    DEFAULT_MIN_CHANGED_LABEL_PRECISION,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import BOUNDARY_BANDS

_UNBANDED = "unbanded"


def _dig(row: Mapping[str, Any], path: Sequence[str]) -> Any:
    current: Any = row
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _row_band(families: Sequence[str], fold_set: Sequence[str]) -> str:
    """The row's single partitioning boundary band (first match in fold order)."""

    members = set(families)
    for name in fold_set:
        if name in members:
            return name
    return _UNBANDED


def _band_allowed(
    *,
    changed_labels: int,
    net_purist_gain: int,
    changed_label_precision: float | None,
    min_changed_label_precision: float,
) -> tuple[bool | None, str]:
    """Frozen allow verdict for one band, with a human-readable reason."""

    if changed_labels == 0:
        return None, "no_switches"
    failures: list[str] = []
    if net_purist_gain < 0:
        failures.append(f"net_purist_gain {net_purist_gain} < 0")
    if (
        changed_label_precision is not None
        and changed_label_precision < min_changed_label_precision
    ):
        failures.append(
            f"changed_label_precision {changed_label_precision} "
            f"< {min_changed_label_precision}"
        )
    if failures:
        return False, "; ".join(failures)
    return True, "allowed"


def summarize_precision_gated_selector(
    rows: Sequence[Mapping[str, Any]],
    *,
    transition_path: Sequence[str],
    label_changed_path: Sequence[str],
    baseline_correct_path: Sequence[str],
    candidate_correct_path: Sequence[str],
    families_path: Sequence[str] = ("hidden_families",),
    fold_families: Sequence[str] = BOUNDARY_BANDS,
    min_changed_label_precision: float = DEFAULT_MIN_CHANGED_LABEL_PRECISION,
) -> dict[str, Any]:
    """Apply a per-band changed-label-precision gate to proposed switches.

    Each row supplies (via key paths) its boundary band, whether the candidate
    switched its label, the Purist transition, and the baseline/candidate Purist
    correctness. The function learns a frozen per-band allow-set, applies it, and
    reports the gated outcome against both the baseline and the ungated
    candidate, plus a leave-one-out unbiased estimate of the gated gain.
    """

    # First pass: per-band switch statistics and a tidy per-row view we reuse.
    band_stats: dict[str, dict[str, int]] = {}
    parsed_rows: list[dict[str, Any]] = []
    for row in rows:
        families = _dig(row, families_path) or (_UNBANDED,)
        band = _row_band(list(families), fold_families)
        switched = _dig(row, label_changed_path) is True
        transition = _dig(row, transition_path)
        baseline_correct = _dig(row, baseline_correct_path) is True
        candidate_correct = _dig(row, candidate_correct_path) is True
        parsed_rows.append(
            {
                "band": band,
                "switched": switched,
                "transition": transition,
                "baseline_correct": baseline_correct,
                "candidate_correct": candidate_correct,
            }
        )
        if switched:
            stats = band_stats.setdefault(
                band,
                {"changed_labels": 0, "wrong_to_correct": 0, "correct_to_wrong": 0},
            )
            stats["changed_labels"] += 1
            if transition == "wrong_to_correct":
                stats["wrong_to_correct"] += 1
            elif transition == "correct_to_wrong":
                stats["correct_to_wrong"] += 1

    # Per-band frozen allow verdict.
    bands: dict[str, dict[str, Any]] = {}
    allowed_bands: set[str] = set()
    for band, stats in band_stats.items():
        changed = stats["changed_labels"]
        wtc = stats["wrong_to_correct"]
        ctw = stats["correct_to_wrong"]
        net = wtc - ctw
        precision = round(wtc / changed, 4) if changed else None
        allowed, reason = _band_allowed(
            changed_labels=changed,
            net_purist_gain=net,
            changed_label_precision=precision,
            min_changed_label_precision=min_changed_label_precision,
        )
        bands[band] = {
            "switched_rows": changed,
            "wrong_to_correct": wtc,
            "correct_to_wrong": ctw,
            "net_purist_gain": net,
            "changed_label_precision": precision,
            "allowed": allowed,
            "reason": reason,
        }
        if allowed:
            allowed_bands.add(band)

    # Apply the frozen policy, and the leave-one-out unbiased variant in parallel.
    baseline_correct_total = 0
    candidate_correct_total = 0
    gated_correct_total = 0
    gated_correct_loo_total = 0
    switches_total = 0
    switches_kept = 0
    switches_kept_loo = 0
    regressions_suppressed = 0
    fixes_forgone = 0
    neutral_churn_suppressed = 0
    for parsed in parsed_rows:
        baseline_correct = parsed["baseline_correct"]
        candidate_correct = parsed["candidate_correct"]
        baseline_correct_total += int(baseline_correct)
        candidate_correct_total += int(candidate_correct)
        if not parsed["switched"]:
            # Untouched rows: candidate == baseline, both gates keep them as-is.
            gated_correct_total += int(candidate_correct)
            gated_correct_loo_total += int(candidate_correct)
            continue

        switches_total += 1
        band = parsed["band"]
        transition = parsed["transition"]
        if band in allowed_bands:
            switches_kept += 1
            gated_correct_total += int(candidate_correct)
        else:
            gated_correct_total += int(baseline_correct)
            if transition == "correct_to_wrong":
                regressions_suppressed += 1
            elif transition == "wrong_to_correct":
                fixes_forgone += 1
            else:
                neutral_churn_suppressed += 1

        # Leave-one-out: re-derive the band gate with this row removed so the row
        # never helps decide its own fate.
        stats = band_stats[band]
        changed_o = stats["changed_labels"] - 1
        wtc_o = stats["wrong_to_correct"] - int(transition == "wrong_to_correct")
        ctw_o = stats["correct_to_wrong"] - int(transition == "correct_to_wrong")
        net_o = wtc_o - ctw_o
        precision_o = wtc_o / changed_o if changed_o > 0 else None
        allow_o = (
            changed_o > 0
            and net_o >= 0
            and precision_o is not None
            and precision_o >= min_changed_label_precision
        )
        if allow_o:
            switches_kept_loo += 1
            gated_correct_loo_total += int(candidate_correct)
        else:
            gated_correct_loo_total += int(baseline_correct)

    candidate_net = candidate_correct_total - baseline_correct_total
    gated_net = gated_correct_total - baseline_correct_total
    gated_net_loo = gated_correct_loo_total - baseline_correct_total

    return {
        "selector": "precision_gated_band_selector_v0",
        "min_changed_label_precision": min_changed_label_precision,
        "fold_families_present": [
            name for name in fold_families if name in bands
        ],
        "rows": len(parsed_rows),
        "baseline_purist_correct": baseline_correct_total,
        "raw_candidate_purist_correct": candidate_correct_total,
        "raw_candidate_net_purist_gain": candidate_net,
        "gated_purist_correct": gated_correct_total,
        "gated_net_purist_gain": gated_net,
        "switches_total": switches_total,
        "switches_kept": switches_kept,
        "switches_suppressed": switches_total - switches_kept,
        "regressions_suppressed": regressions_suppressed,
        "fixes_forgone": fixes_forgone,
        "neutral_churn_suppressed": neutral_churn_suppressed,
        "allowed_bands": sorted(allowed_bands),
        "suppressed_bands": sorted(
            band for band, info in bands.items() if info["allowed"] is False
        ),
        "bands": dict(sorted(bands.items())),
        "leave_one_out": {
            "gated_purist_correct": gated_correct_loo_total,
            "gated_net_purist_gain": gated_net_loo,
            "switches_kept": switches_kept_loo,
            "switches_suppressed": switches_total - switches_kept_loo,
            "net_gain_sign_matches_band_policy": (
                (gated_net > 0) == (gated_net_loo > 0)
            ),
            "note": (
                "Unbiased estimate: each row's band gate is recomputed with that "
                "row excluded, so no band is credited for a switch whose own "
                "outcome set its gate. A band-level gain that survives this is the "
                "generalizing one."
            ),
        },
        "note": (
            "Decision-layer gate (next-phase brief step 2): a proposed switch is "
            "applied only inside boundary bands whose changed-label precision "
            f">= {min_changed_label_precision} and whose net Purist gain >= 0. "
            "Agreement proposes; precision decides. The allow-set is learned on "
            "validation and is meant to be frozen before any held-out application."
        ),
    }
