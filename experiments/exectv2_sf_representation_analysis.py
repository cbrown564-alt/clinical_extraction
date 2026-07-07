"""SeizureFrequency: is the ~0.59 'plateau' genuine recall or a representation artifact?

Zero-LLM, read-only analysis on saved GEPA predictions. Produces the numbers behind
``docs/research/exectv2_sf_representation_not_recall_2026-06-28.md``:

1. SF clinical_headline P/R/F1 and a recall/precision loss decomposition (genuine miss
   vs seizure-type-CUI mismatch vs state mismatch) — shows the synthesis's "genuine
   recall" framing measured only the residue after discarding overlap-mismatches.
2. A key-relaxation ladder: (type_cui, state) -> (state,) multiset -> (state,) presence
   per letter [the Gan framing] -> isolates how much of the gap is the type-CUI
   granularity lottery vs gold's exhaustive per-type multiplicity.
3. Per-state presence recall/precision (change-aware 4-way state) — pins the genuine
   residual to active-rate over-calling + the barely-detected 'changed' class.

Usage:
    uv run python experiments/exectv2_sf_representation_analysis.py
    uv run python experiments/exectv2_sf_representation_analysis.py --run <run_id>
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from clinical_extraction.core.scoring import multiset_prf1, sum_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import frequency_state_faithful
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
    _frequency_type_key,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
DEFAULT_RUN = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"


def _pred_letters(run_id: str) -> dict[str, ExectLetter]:
    letters: dict[str, ExectLetter] = {}
    for line in (EXPERIMENTS / f"{run_id}.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        anns = tuple(
            ExectAnnotation(
                entity=m["entity"],
                text=m.get("text", ""),
                attributes={str(k): str(v) for k, v in (m.get("attributes") or {}).items()},
            )
            for m in row.get("predicted_mentions", [])
        )
        letters[row["letter_id"]] = ExectLetter(
            letter_id=row["letter_id"], note_text="", annotations=anns
        )
    return letters


def _overlaps(a: str, b: str) -> bool:
    a, b = normalize_phrase(a), normalize_phrase(b)
    return bool(a and b and (a in b or b in a))


def _sf(letter: ExectLetter | None) -> list[ExectAnnotation]:
    return list(letter.entities("SeizureFrequency")) if letter else []


def _relaxation_ladder(gold: dict, pred: dict) -> None:
    def score(keyfn, dedup: bool):
        def keys(anns):
            ks = [keyfn(a) for a in anns]
            return list(dict.fromkeys(ks)) if dedup else ks

        ids = sorted(gold.keys() | pred.keys())
        return sum_prf1(multiset_prf1(keys(_sf(gold.get(i))), keys(_sf(pred.get(i)))) for i in ids)

    variants = [
        (
            "(type_cui, state)   production clinical_headline",
            lambda a: (_frequency_type_key(a), _frequency_state(a.attributes)),
            True,
        ),
        (
            "(state,) multiset   drop seizure type",
            lambda a: (_frequency_state(a.attributes),),
            False,
        ),
        (
            "(state,) presence   per letter [Gan framing]",
            lambda a: (frequency_state_faithful(a.attributes),),
            True,
        ),
    ]
    print("## Key-relaxation ladder (same predictions)")
    for name, fn, dd in variants:
        prf = score(fn, dd)
        print(f"  {name:48} P={prf.precision:.3f} R={prf.recall:.3f} F1={prf.f1:.3f}")


def _loss_decomposition(gold: dict, pred: dict) -> None:
    tp = fp = fn = 0
    cause: Counter = Counter()
    fp_cause: Counter = Counter()
    n_gold = n_pred = 0
    for lid in sorted(gold.keys() | pred.keys()):
        g_anns, p_anns = _sf(gold.get(lid)), _sf(pred.get(lid))
        n_gold += len(g_anns)
        n_pred += len(p_anns)
        gk = [((_frequency_type_key(a), _frequency_state(a.attributes)), a) for a in g_anns]
        pk = [((_frequency_type_key(a), _frequency_state(a.attributes)), a) for a in p_anns]
        used = [False] * len(pk)
        avail: dict = {}
        for i, (k, _) in enumerate(pk):
            avail.setdefault(k, []).append(i)
        matched = [False] * len(gk)
        for gi, (gkey, _) in enumerate(gk):
            free = [i for i in avail.get(gkey, []) if not used[i]]
            if free:
                used[free[0]] = True
                matched[gi] = True
                tp += 1
        for gi, (gkey, gann) in enumerate(gk):
            if matched[gi]:
                continue
            fn += 1
            same_type = [i for i, (pkey, _) in enumerate(pk) if not used[i] and pkey[0] == gkey[0]]
            phrase_ov = [
                i
                for i, (_, pann) in enumerate(pk)
                if not used[i] and _overlaps(gann.text, pann.text)
            ]
            if same_type:
                cause["state mismatch (same type-key, diff state)"] += 1
                used[same_type[0]] = True
            elif phrase_ov:
                cause["type/CUI mismatch (phrase overlaps, type-key differs)"] += 1
                used[phrase_ov[0]] = True
            else:
                cause["GENUINE miss (no overlapping SF pred)"] += 1
        for pi, (_pkey, pann) in enumerate(pk):
            if used[pi]:
                continue
            fp += 1
            if any(_overlaps(pann.text, gann.text) for _, gann in gk):
                fp_cause["overlapping gold exists (key disagreed)"] += 1
            else:
                fp_cause["spurious (no overlapping gold SF)"] += 1

    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    print(
        f"\n## clinical_headline loss decomposition  P={p:.3f} R={r:.3f} F1={f1:.3f}"
        f"  (gold={n_gold} pred={n_pred} tp={tp} fp={fp} fn={fn})"
    )
    print("  recall loss (FN) by cause:")
    for k, n in cause.most_common():
        print(f"    {k:<50} {n:>4} ({100 * n / fn:.0f}%)")
    print("  precision loss (FP) by cause:")
    for k, n in fp_cause.most_common():
        print(f"    {k:<50} {n:>4} ({100 * n / fp:.0f}%)")


def _per_state(gold: dict, pred: dict) -> None:
    print("\n## per-state presence recall/precision (change-aware 4-way)")
    for st in ("seizure-free", "active-rate", "changed", "unknown"):
        g = p = tp = 0
        for i in gold.keys() | pred.keys():
            gs = {frequency_state_faithful(a.attributes) for a in _sf(gold.get(i))}
            ps = {frequency_state_faithful(a.attributes) for a in _sf(pred.get(i))}
            g += st in gs
            p += st in ps
            tp += st in gs and st in ps
        rec = tp / g if g else 0.0
        prec = tp / p if p else 0.0
        print(
            f"  {st:14} gold_letters={g:3} pred_letters={p:3} recall={rec:.2f} precision={prec:.2f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=DEFAULT_RUN)
    args = parser.parse_args()

    gold = {g.letter_id: g for g in gepa_data.load_dev_letters()}
    pred = _pred_letters(args.run)
    print(f"# SF representation analysis — {args.run} (dev140)\n")
    _relaxation_ladder(gold, pred)
    _loss_decomposition(gold, pred)
    _per_state(gold, pred)


if __name__ == "__main__":
    main()
