"""No-model seizure-frequency oracle ceiling probe (item 4 extension).

ZERO LLM CALLS. A deterministic replay over gold text.

Motivation (dspy predecessor finding). dspy's E1 "broad payload" covers 100% of
gold at 22.2% precision, localizing the SF problem to *adjudication* (the
broad-payload candidate substrate has perfect recall but floods precision; the
LLM arbitration prunes to the final headline). The implication for our SF lane:
how much of the cited hybrid SF surface does the deterministic extractor own on
its own, and how does the pre-adjudication candidate substrate compare? This is
the direct analogue of
``experiments/exectv2_medication_no_model_oracle_2026-07-06.py`` (the template)
applied to the SeizureFrequency family.

THREE surfaces are scored, in order of how "oracle-like" they are:
  1. ``gold_as_prediction`` -- gold SeizureFrequency annotations copied verbatim
     into the prediction slot. This is the dspy-style scorer-integrity ceiling:
     it tests whether the scoring pipeline preserves gold labels, NOT whether
     extraction is solved. Should be 1.0.
  2. ``deterministic_only`` -- ``extract_seizure_frequency(letter)`` (the final
     SF pipeline, including the keep/drop filter) run as the final system with
     NO lens, NO bridge, NO LLM. This is the real no-model *extraction* ceiling.
  3. ``candidate_substrate`` -- ``build_candidate_set(letter)`` (the pre-
     adjudication high-recall candidate set), scored with every candidate kept
     as a SeizureFrequency mention carrying its deterministic
     ``suggested_attributes``. This is the structural analogue of dspy's E1
     broad payload: it tests whether the candidate substrate's recall is near-
     complete (localizing the problem to adjudication) -- distinct from the
     extraction ceiling above.

Split discipline: dev140 + full-200 are both fine (no live predictions; this is
a deterministic replay over gold text). No split risk. Per claim_policy the
full-200 surface is aggregate-only; the per-letter FN/FP decomposition is
therefore reported for dev140 only (the development surface).

Comparison anchors (cited hybrid/raw SF lane numbers, sourced from
``PROJECT_STATUS.md``):
  - dev140 state_profile F1 0.7483 (registered) / 0.7793 (2026-07-03 re-run)
  - dev140 state_profile_directional F1 0.6552 (raw SF-verify) / 0.8897 (v08
    hybrid, direction sourced from deterministic rules/change.py)

NOTE the SF extractor signature differs from the Rx/Inv pattern: it takes an
``ExectLetter`` (not bare ``note_text``) and returns a ``PredictedLetter`` (not
``tuple[PredictedMention, ...]``). The candidate-substrate surface likewise
operates per-letter. SF has no separate benchmark-projection scorer; the
projection fields (``exact_semantic`` / ``benchmark_with_cui``) live inside the
same ``FrequencyStateScores`` object.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    extract_seizure_frequency,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.candidate_set import (
    build_candidate_set,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_keys,
    score_frequency_state,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
SF_ENTITY = SEIZURE_FREQUENCY.name  # "SeizureFrequency"

# Cited hybrid/raw SF numbers this probe decomposes (see module docstring +
# PROJECT_STATUS.md). Stated for comparison only; not re-run here.
CITED_HYBRID_SF = {
    "dev140_state_profile_f1_registered": 0.7483,
    "dev140_state_profile_f1_rerun_2026_07_03": 0.7793,
    "dev140_state_profile_directional_f1_raw": 0.6552,
    "dev140_state_profile_directional_f1_hybrid": 0.8897,
}

# The FrequencyStateScores fields worth reporting (the projection fields
# exact_semantic / benchmark_with_cui are included for completeness; the
# headline clinical metrics are state_profile / state_profile_directional /
# clinical_headline).
METRIC_ORDER = (
    "clinical_headline",
    "state_profile",
    "state_profile_directional",
    "active_rate",
    "active_rate_fidelity",
    "seizure_free",
    "unknown",
    "exact_semantic",
    "benchmark_with_cui",
)


def _prf1_row(prf1: Any) -> dict[str, Any]:
    return {
        "precision": round(float(prf1.precision), 4),
        "recall": round(float(prf1.recall), 4),
        "f1": round(float(prf1.f1), 4),
        "tp": int(getattr(prf1, "tp", 0)),
        "fp": int(getattr(prf1, "fp", 0)),
        "fn": int(getattr(prf1, "fn", 0)),
    }


def _scores_dict(scores: Any) -> dict[str, dict[str, Any]]:
    return {name: _prf1_row(getattr(scores, name)) for name in METRIC_ORDER}


def gold_as_prediction_letters(gold_letters: Sequence[ExectLetter]) -> list[ExectLetter]:
    """Copy each gold letter's SeizureFrequency annotations verbatim into the
    prediction slot.

    This is the dspy-style scorer-integrity ceiling: it asks "does the scoring
    pipeline reproduce gold labels when handed gold labels?" It is NOT an
    extraction ceiling -- it tests the scorer, not the extractor. The
    deterministic extractor below is the real extraction ceiling.
    """

    out: list[ExectLetter] = []
    for gold in gold_letters:
        gold_sf = [
            ExectAnnotation(
                entity=ann.entity,
                text=ann.text,
                attributes=ann.attributes,
                start_index=ann.start_index,
                end_index=ann.end_index,
                raw_text=ann.raw_text,
            )
            for ann in gold.entities(SF_ENTITY)
        ]
        out.append(
            ExectLetter(
                letter_id=gold.letter_id,
                note_text=gold.note_text,
                annotations=tuple(gold_sf),
            )
        )
    return out


def deterministic_only_letters(gold_letters: Sequence[ExectLetter]) -> list[ExectLetter]:
    """Run the final SF deterministic extractor alone as the final system.

    No lens, no bridge, no benchmark projection, no LLM. This is the no-model
    *extraction* ceiling: the deterministic pipeline's standalone recall/
    precision on the gold text, INCLUDING its own keep/drop filter
    (``_should_keep_mention``). Compares to the cited hybrid ``state_profile``.
    """

    out: list[ExectLetter] = []
    for gold in gold_letters:
        predicted = extract_seizure_frequency(gold)
        out.append(to_exect_letter(predicted, note_text=gold.note_text))
    return out


def candidate_substrate_letters(gold_letters: Sequence[ExectLetter]) -> list[ExectLetter]:
    """Score the pre-adjudication candidate substrate -- dspy's E1 analogue.

    ``build_candidate_set(letter)`` is the high-recall candidate set the hybrid
    assessment LLM is offered: every seizure-type anchor the rules find becomes a
    candidate, INCLUDING anchors with no nearby frequency information (the
    deterministic pipeline drops those; here every candidate is KEPT). This
    surface tests whether the candidate substrate's recall is near-complete on
    gold -- the dspy E1 "broad payload covers 100% of gold" framing -- localizing
    the problem to adjudication rather than extraction.

    Each candidate is emitted as a SeizureFrequency mention carrying its
    deterministic ``suggested_attributes`` verbatim. This is the broadest
    possible payload (no pruning); precision is expected to be low by design.
    """

    out: list[ExectLetter] = []
    for gold in gold_letters:
        candidates = build_candidate_set(gold)
        mentions = tuple(
            PredictedMention(
                entity=SF_ENTITY,
                text=cand.anchor_text,
                attributes=dict(cand.suggested_attributes),
                evidence=cand.evidence,
                component_owner="sf_candidate_substrate",
            )
            for cand in candidates
        )
        predicted = PredictedLetter(letter_id=gold.letter_id, mentions=mentions)
        out.append(to_exect_letter(predicted, note_text=gold.note_text))
    return out


def _multiset_counts(keys: list[Any]) -> dict[Any, int]:
    counts: dict[Any, int] = {}
    for key in keys:
        counts[key] = counts.get(key, 0) + 1
    return counts


def _multiset_sub(a: dict[Any, int], b: dict[Any, int]) -> list[Any]:
    out: list[Any] = []
    for key, n in a.items():
        out.extend([key] * max(0, n - b.get(key, 0)))
    return out


def per_letter_decomposition(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    *,
    metric: str,
) -> dict[str, Any]:
    """For dev140 only: which gold ``metric`` keys are missed (FN) and which
    predicted keys are spurious (FP). Reported for the development surface only
    per split discipline.

    ``metric`` selects the FrequencyStateScores key set to decompose
    (``state_profile`` or ``state_profile_directional``).
    """

    letters: list[dict[str, Any]] = []
    missed_counter: Counter[Any] = Counter()
    spurious_counter: Counter[Any] = Counter()
    for gold, pred in zip(gold_letters, pred_letters, strict=True):
        gold_keys = frequency_state_keys(list(gold.entities(SF_ENTITY)), metric)
        pred_keys = frequency_state_keys(list(pred.entities(SF_ENTITY)), metric)
        gold_counts = _multiset_counts(gold_keys)
        pred_counts = _multiset_counts(pred_keys)
        missed = _multiset_sub(gold_counts, pred_counts)
        spurious = _multiset_sub(pred_counts, gold_counts)
        missed_counter.update(missed)
        spurious_counter.update(spurious)
        letters.append(
            {
                "letter_id": gold.letter_id,
                "gold_n": len(gold_keys),
                "pred_n": len(pred_keys),
                "missed": [str(k) for k in missed],
                "spurious": [str(k) for k in spurious],
            }
        )
    return {
        "metric": metric,
        "per_letter": letters,
        "missed_key_totals": {str(k): n for k, n in missed_counter.most_common()},
        "spurious_key_totals": {str(k): n for k, n in spurious_counter.most_common()},
    }


def score_split(gold_letters: list[ExectLetter], *, surface: str) -> dict[str, Any]:
    if surface == "gold_as_prediction":
        pred_letters = gold_as_prediction_letters(gold_letters)
    elif surface == "deterministic_only":
        pred_letters = deterministic_only_letters(gold_letters)
    elif surface == "candidate_substrate":
        pred_letters = candidate_substrate_letters(gold_letters)
    else:
        raise ValueError(surface)
    scores = score_frequency_state(gold_letters, pred_letters)
    return {
        "row_count": len(gold_letters),
        "frequency_state_scores": _scores_dict(scores),
        "_pred_letters": pred_letters,
    }


def _print_anchors(surface: str) -> None:
    if surface == "deterministic_only":
        sp_reg = CITED_HYBRID_SF["dev140_state_profile_f1_registered"]
        sp_rerun = CITED_HYBRID_SF["dev140_state_profile_f1_rerun_2026_07_03"]
        d_raw = CITED_HYBRID_SF["dev140_state_profile_directional_f1_raw"]
        d_hyb = CITED_HYBRID_SF["dev140_state_profile_directional_f1_hybrid"]
        print(
            f"  {'':22s}  refs: state_profile reg {sp_reg} / rerun {sp_rerun}; "
            f"directional raw {d_raw} / hybrid {d_hyb}"
        )
    elif surface == "candidate_substrate":
        print(f"  {'':22s}  dspy E1 analogue: broad payload expected high-recall / low-precision")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--splits",
        default="dev,full200",
        help="comma-separated subset of {dev, full200}",
    )
    parser.add_argument(
        "--allow-non-dev140",
        action="store_true",
        help="acknowledge full-200 is aggregate-only (required to run full200)",
    )
    args = parser.parse_args()
    splits = [s.strip() for s in args.splits.split(",") if s.strip()]
    if "full200" in splits and not args.allow_non_dev140:
        raise SystemExit(
            "full200 is aggregate-only per claim_policy; pass --allow-non-dev140 to acknowledge."
        )

    results: dict[str, Any] = {
        "run_meta": {
            "probe": "exectv2_sf_no_model_oracle",
            "llm_calls": 0,
            "model": "(model-independent)",
            "surfaces": ["gold_as_prediction", "deterministic_only", "candidate_substrate"],
            "scorer": "score_frequency_state",
            "cited_hybrid_sf_for_comparison": CITED_HYBRID_SF,
            "note": (
                "gold_as_prediction is the dspy-style scorer-integrity ceiling. "
                "deterministic_only is the real no-model extraction ceiling "
                "(extract_seizure_frequency run as the final system, with its "
                "keep/drop filter). candidate_substrate is the dspy E1 analogue: "
                "build_candidate_set with every candidate kept (pre-adjudication)."
            ),
        },
        "splits": {},
    }

    print("=" * 78)
    print("No-model seizure-frequency oracle probe (zero LLM calls)")
    print("=" * 78)

    for split in splits:
        if split == "dev":
            gold_letters = load_letters_for_split("dev")
            label = "dev140"
        elif split == "full200":
            gold_letters = load_letters()
            label = "full200"
        else:
            raise SystemExit(f"unknown split {split!r}")
        print(f"\n--- {label} ({len(gold_letters)} letters) ---")

        split_out: dict[str, Any] = {"label": label, "row_count": len(gold_letters)}
        for surface in ("gold_as_prediction", "deterministic_only", "candidate_substrate"):
            scored = score_split(gold_letters, surface=surface)
            scored.pop("_pred_letters", None)
            fs = scored["frequency_state_scores"]
            for metric in ("state_profile", "state_profile_directional", "clinical_headline"):
                row = fs[metric]
                print(
                    f"  {surface:22s} {metric:26s}: F1={row['f1']:.4f} "
                    f"(tp={row['tp']} fp={row['fp']} fn={row['fn']})"
                )
            _print_anchors(surface)
            split_out[surface] = scored

        # Per-letter FN/FP decomposition: dev140 only (development surface; full-200
        # is aggregate-only per claim_policy). Decompose the deterministic_only
        # extraction ceiling on both headline clinical metrics.
        if split == "dev":
            det_pred = deterministic_only_letters(gold_letters)
            split_out["deterministic_only_dev140_decomposition"] = {
                "state_profile": per_letter_decomposition(
                    gold_letters, det_pred, metric="state_profile"
                ),
                "state_profile_directional": per_letter_decomposition(
                    gold_letters, det_pred, metric="state_profile_directional"
                ),
            }
            # Candidate-substrate recall check: how many gold state_profile keys
            # the broad payload covers (the dspy E1 "100% recall" framing).
            cand_pred = candidate_substrate_letters(gold_letters)
            split_out["candidate_substrate_dev140_decomposition"] = per_letter_decomposition(
                gold_letters, cand_pred, metric="state_profile"
            )

        results["splits"][split] = split_out

    out_path = EXPERIMENTS / "exectv2_sf_no_model_oracle_2026-07-06.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
