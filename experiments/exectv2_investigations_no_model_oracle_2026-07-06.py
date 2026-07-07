"""No-model investigations oracle ceiling probe (item 4 extension).

ZERO LLM CALLS. A deterministic replay over gold text.

Motivation (dspy predecessor finding). dspy reports near-ceiling isolated
investigations performance (90.4-96.7%). The sharp implication is the same as
the medication oracle: how much of the cited hybrid Investigations
``clinical_headline`` does the deterministic extractor own on its own, with no
LLM, no lens, no bridge? If the deterministic-only extractor already approaches
the cited hybrid number, the Inv story must be framed as "the deterministic
layer carries it; the LLM's value is elsewhere" rather than "the LLM extracts
investigations." This is the direct analogue of
``experiments/exectv2_medication_no_model_oracle_2026-07-06.py`` (the template)
applied to the Investigations family.

Two surfaces are scored, in order of how "oracle-like" they are:
  1. ``gold_as_prediction`` -- gold Investigations annotations copied verbatim
     into the prediction slot. This is the dspy-style scorer-integrity ceiling:
     it tests whether the scoring pipeline preserves gold labels, NOT whether
     extraction is solved. Should be 1.0.
  2. ``deterministic_only`` -- ``_extract_investigations(note_text)`` run as the
     final system with NO lens, NO bridge, NO LLM. This is the real extraction
     ceiling the deterministic layer owns.

Split discipline: dev140 + full-200 are both fine (no live predictions; this is a
deterministic replay over gold text). No split risk. Per claim_policy the full-200
surface is aggregate-only; the per-letter FN/FP decomposition is therefore
reported for dev140 only (the development surface).

Comparison anchors (cited hybrid Inv lane, sourced from
``docs/experiments/exectv2/investigations/exectv2_inv_llm_vs_hybrid_comparator_2026-07-03.md``):
  - dev140 clinical_headline F1 0.9132 (P 0.9380 / R 0.8897, 121/8/15)
  - full-200 clinical_headline F1 0.9213 (P 0.9480 / R 0.8962, 164/9/19)
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    investigations as inv_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    investigation_component_keys,
    score_investigations_components,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
INVESTIGATIONS = "Investigations"

# Cited hybrid-lane numbers this probe decomposes (see module docstring +
# PROJECT_STATUS.md). Stated for comparison only; not re-run here.
CITED_HYBRID_INV = {
    "dev140_clinical_headline_f1": 0.9132,
    "full200_clinical_headline_f1": 0.9213,
}

COMPONENT_ORDER = (
    "clinical_headline",
    "eeg",
    "mri",
    "ct",
    "performed",
    "result",
    "eeg_type",
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


def _components_dict(scores: Any) -> dict[str, dict[str, Any]]:
    return {name: _prf1_row(getattr(scores, name)) for name in COMPONENT_ORDER}


def gold_as_prediction_letters(gold_letters: Sequence[ExectLetter]) -> list[ExectLetter]:
    """Copy each gold letter's Investigations annotations verbatim into the
    prediction slot.

    This is the dspy-style scorer-integrity ceiling: it asks "does the scoring
    pipeline reproduce gold labels when handed gold labels?" It is NOT an
    extraction ceiling -- it tests the scorer, not the extractor. The
    deterministic extractor below is the real extraction ceiling.
    """

    out: list[ExectLetter] = []
    for gold in gold_letters:
        gold_inv = [
            ExectAnnotation(
                entity=ann.entity,
                text=ann.text,
                attributes=ann.attributes,
                start_index=ann.start_index,
                end_index=ann.end_index,
                raw_text=ann.raw_text,
            )
            for ann in gold.entities(INVESTIGATIONS)
        ]
        out.append(
            ExectLetter(
                letter_id=gold.letter_id,
                note_text=gold.note_text,
                annotations=tuple(gold_inv),
            )
        )
    return out


def deterministic_only_letters(gold_letters: Sequence[ExectLetter]) -> list[ExectLetter]:
    """Run the deterministic investigations extractor alone as the final system.

    No lens, no bridge, no benchmark projection, no LLM. This is the no-model
    extraction ceiling: the deterministic layer's standalone recall/precision on
    the gold text. Compares directly to dspy's near-ceiling framing.
    """

    out: list[ExectLetter] = []
    for gold in gold_letters:
        mentions = inv_rules._extract_investigations(gold.note_text)
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
    gold_letters: Sequence[ExectLetter], pred_letters: Sequence[ExectLetter]
) -> dict[str, Any]:
    """For dev140 only: which gold ``clinical_headline`` keys are missed (FN) and
    which predicted keys are spurious (FP). This is the row-level "why not 100%"
    decomposition. Reported for the development surface only per split discipline.
    """

    letters: list[dict[str, Any]] = []
    missed_counter: Counter[Any] = Counter()
    spurious_counter: Counter[Any] = Counter()
    for gold, pred in zip(gold_letters, pred_letters, strict=True):
        # investigation_component_keys takes (annotations, component) -- no
        # note_text arg (unlike prescription_component_keys); the modality keys
        # are derived purely from attributes, not evidence substrings.
        gold_keys = investigation_component_keys(
            list(gold.entities(INVESTIGATIONS)), "clinical_headline"
        )
        pred_keys = investigation_component_keys(
            list(pred.entities(INVESTIGATIONS)), "clinical_headline"
        )
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
        "per_letter": letters,
        "missed_key_totals": {str(k): n for k, n in missed_counter.most_common()},
        "spurious_key_totals": {str(k): n for k, n in spurious_counter.most_common()},
    }


def score_split(gold_letters: list[ExectLetter], *, surface: str) -> dict[str, Any]:
    if surface == "gold_as_prediction":
        pred_letters = gold_as_prediction_letters(gold_letters)
    elif surface == "deterministic_only":
        pred_letters = deterministic_only_letters(gold_letters)
    else:
        raise ValueError(surface)
    components = score_investigations_components(gold_letters, pred_letters)
    return {
        "row_count": len(gold_letters),
        "prescription_component_scores": _components_dict(components),
        # Alias kept for schema-parity with the medication oracle's JSON shape;
        # investigations has no separate benchmark-projection scorer.
        "investigations_component_scores": _components_dict(components),
        "_pred_letters": pred_letters,
    }


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
            "probe": "exectv2_investigations_no_model_oracle",
            "llm_calls": 0,
            "model": "(model-independent)",
            "surfaces": ["gold_as_prediction", "deterministic_only"],
            "scorer": "score_investigations_components",
            "cited_hybrid_inv_for_comparison": CITED_HYBRID_INV,
            "note": (
                "gold_as_prediction is the dspy-style scorer-integrity ceiling "
                "(gold copied through the pipeline; tests the scorer, not extraction). "
                "deterministic_only is the real no-model extraction ceiling "
                "(_extract_investigations run as the final system)."
            ),
        },
        "splits": {},
    }

    print("=" * 78)
    print("No-model investigations oracle probe (zero LLM calls)")
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
        for surface in ("gold_as_prediction", "deterministic_only"):
            scored = score_split(gold_letters, surface=surface)
            scored.pop("_pred_letters", None)
            ch = scored["investigations_component_scores"]["clinical_headline"]
            print(
                f"  {surface:22s}: clinical_headline P={ch['precision']:.4f} "
                f"R={ch['recall']:.4f} F1={ch['f1']:.4f} "
                f"(tp={ch['tp']} fp={ch['fp']} fn={ch['fn']})"
            )
            if surface == "deterministic_only":
                cited_dev = CITED_HYBRID_INV["dev140_clinical_headline_f1"]
                cited_full = CITED_HYBRID_INV["full200_clinical_headline_f1"]
                cited = cited_dev if split == "dev" else cited_full
                gap = round(ch["f1"] - cited, 4)
                print(
                    f"  {'':22s}  gap to cited hybrid Inv clinical_headline ({cited}): {gap:+.4f}"
                )
            split_out[surface] = scored

        # Per-letter FN/FP decomposition: dev140 only (development surface; full-200
        # is aggregate-only per claim_policy).
        if split == "dev":
            det_pred = deterministic_only_letters(gold_letters)
            split_out["deterministic_only_dev140_decomposition"] = per_letter_decomposition(
                gold_letters, det_pred
            )

        results["splits"][split] = split_out

    out_path = EXPERIMENTS / "exectv2_investigations_no_model_oracle_2026-07-06.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
