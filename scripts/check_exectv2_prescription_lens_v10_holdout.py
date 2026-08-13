#!/usr/bin/env python3
"""Prescription lens v10 vs v09 confirmation on the sealed ExECT test59 holdout.

Predeclared protocol:
docs/research/exectv2/exectv2_prescription_lens_v10_holdout_confirmation_protocol_2026-08-10.md

Machine-only scoring under the Decision 0046 Phase C pattern. Zero model calls:
an ordered no-call replay of retained ``*_structured.jsonl`` holdout sidecars
through the current deterministic stages.

Two passes, because the v09 arm must be the *real* pre-change implementation
rather than a re-implementation of it:

    # on the current (v10) tree
    uv run python scripts/check_exectv2_prescription_lens_v10_holdout.py --capture v10_shipped
    git stash push -- src/          # restore the v09 lens
    uv run python scripts/check_exectv2_prescription_lens_v10_holdout.py --capture v09_previous
    git stash pop
    uv run python scripts/check_exectv2_prescription_lens_v10_holdout.py --combine

Row policy: per-cell captures are written under ``scratch/`` only (gitignored).
The combined artifact in ``experiments/`` is aggregate-only -- no letter id, row
index, note text, prediction, or failure example.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/"
    "exectv2_prescription_lens_v10_holdout_confirmation_protocol_2026-08-10.md"
)
OUT = REPO_ROOT / "experiments" / "exectv2_prescription_lens_v10_holdout_20260810.json"
CAPTURE_DIR = REPO_ROOT / "scratch" / "prescription_lens_v10_holdout"
ARMS = ("v09_previous", "v10_shipped")

HOLDOUT_ROOTS: dict[str, Path] = {
    "gpt41mini": REPO_ROOT / "scratch/holdout/exectv2_test60/gpt41mini",
    "gpt56luna": REPO_ROOT / "scratch/holdout/exectv2_test60/gpt56luna",
    # The panel's aggregate_source for Sol is the credit_v2 re-run; the original
    # exectv2_test60/gpt56sol tree is superseded and has 40/59 empty event rows.
    "gpt56sol": REPO_ROOT / "scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol",
    "deepseek_v4_flash": REPO_ROOT / "scratch/holdout/exectv2_test60/deepseek_v4_flash",
    "qwen36_35b": REPO_ROOT / "scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b",
    "gemma4_26b": REPO_ROOT / "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b",
}

_CF_PATH = REPO_ROOT / "scripts/build_exectv2_prescription_lens_counterfactual.py"
_SPEC = importlib.util.spec_from_file_location("exect_rx_counterfactual", _CF_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot import replay helpers from {_CF_PATH}")
cf = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cf)

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (  # noqa: E402
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (  # noqa: E402
    aggregate_scores,
    annotation_from_mapping,
    clinical_headline_scores,
    headline_keys,
)


def capture(arm: str) -> int:
    """Replay one arm on the current tree; persist per-cell keys under scratch/."""

    missing = [slug for slug, root in HOLDOUT_ROOTS.items() if not root.is_dir()]
    if missing:
        print(f"sealed holdout trees absent for: {missing}")
        print("see docs/runbooks/restore_sealed_holdout_ledgers_for_category_cuts.md")
        return 2

    letters = {letter.letter_id: letter for letter in load_letters_for_split("test")}
    cells: list[dict[str, Any]] = []
    unreplayable = 0

    for slug, root in HOLDOUT_ROOTS.items():
        structured_rows = cf.hs._read_jsonl(root / f"{slug}_structured.jsonl")
        sealed_rows = {
            str(row["letter_id"]): row
            for row in cf.hs._read_jsonl(root / f"{slug}_sealed_rows.jsonl")
        }
        for structured_row in structured_rows:
            letter_id = str(structured_row["letter_id"])
            letter = letters.get(letter_id)
            sealed = sealed_rows.get(letter_id)
            if letter is None or sealed is None:
                continue
            gold = list(sealed.get("gold_mentions") or [])
            replay = cf.replay_letter_arm(
                structured_row, letter, gold_mentions=gold, prescription_arm="default_on"
            )
            if not replay.get("replayable"):
                unreplayable += 1
                continue
            cells.append(
                {
                    "model_slug": slug,
                    "letter_id": letter_id,
                    "gold_mentions": gold,
                    "gold_keys": headline_keys(
                        {"gold_mentions": gold, "predicted_mentions": []},
                        "Prescription",
                        field="gold_mentions",
                    ),
                    "rx_keys": replay["final_keys"],
                    "mode": replay["final_mode"],
                    "mentions": replay["final_mentions"],
                    "retained_rx_keys": headline_keys(
                        sealed, "Prescription", field="predicted_mentions"
                    ),
                }
            )

    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    path = CAPTURE_DIR / f"{arm}.json"
    path.write_text(
        json.dumps({"arm": arm, "unreplayable": unreplayable, "cells": cells}),
        encoding="utf-8",
    )
    print(f"captured arm={arm} cells={len(cells)} unreplayable={unreplayable} -> scratch/")
    return 0


def _score(cells: list[dict[str, Any]]) -> dict[str, Any]:
    gold_letters = [
        ExectLetter(
            letter_id=c["letter_id"],
            note_text="",
            annotations=tuple(annotation_from_mapping(m) for m in c["gold_mentions"]),
        )
        for c in cells
    ]
    pred_letters = [
        ExectLetter(
            letter_id=c["letter_id"],
            note_text="",
            annotations=tuple(annotation_from_mapping(m) for m in c["mentions"]),
        )
        for c in cells
    ]
    family = clinical_headline_scores(gold_letters, pred_letters)
    overall = aggregate_scores(family.values())
    return {
        "prescription_f1": round(float(family["Prescription"]["f1"]), 4),
        "four_family_f1": round(float(overall["f1"]), 4),
    }


def _micro(cells: list[dict[str, Any]]) -> dict[str, Any]:
    tp = fp = fn = exact = 0
    for c in cells:
        gold, pred = Counter(c["gold_keys"]), Counter(c["rx_keys"])
        hit = sum((gold & pred).values())
        tp += hit
        fp += sum(pred.values()) - hit
        fn += sum(gold.values()) - hit
        exact += int(c["mode"] in ("correct_nonempty", "correct_empty"))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "prescription_precision": round(precision, 4),
        "prescription_recall": round(recall, 4),
        "prescription_micro_f1": round(f1, 4),
        "prescription_exact_rate": round(exact / len(cells), 4) if cells else None,
    }


def combine() -> int:
    loaded: dict[str, Any] = {}
    for arm in ARMS:
        path = CAPTURE_DIR / f"{arm}.json"
        if not path.is_file():
            print(f"missing capture for {arm}; run --capture {arm} on the matching tree")
            return 2
        loaded[arm] = json.loads(path.read_text(encoding="utf-8"))

    keyed = {
        arm: {(c["model_slug"], c["letter_id"]): c for c in loaded[arm]["cells"]}
        for arm in ARMS
    }
    shared = sorted(set(keyed[ARMS[0]]) & set(keyed[ARMS[1]]))
    if not shared:
        print("no overlapping cells between arms")
        return 2

    slugs = list(HOLDOUT_ROOTS)
    summary: dict[str, Any] = {}
    per_model: dict[str, Any] = {slug: {} for slug in slugs}
    for arm in ARMS:
        cells = [keyed[arm][k] for k in shared]
        summary[arm] = {
            **_micro(cells),
            "prescription_f1_mean_over_models": None,
            "four_family_f1_mean_over_models": None,
        }
        rx_means, ff_means = [], []
        for slug in slugs:
            subset = [c for c in cells if c["model_slug"] == slug]
            if not subset:
                continue
            scored = _score(subset)
            per_model[slug][arm] = {
                **scored,
                "prescription_exact_rate": _micro(subset)["prescription_exact_rate"],
                "n": len(subset),
            }
            rx_means.append(scored["prescription_f1"])
            ff_means.append(scored["four_family_f1"])
        summary[arm]["prescription_f1_mean_over_models"] = round(
            sum(rx_means) / len(rx_means), 4
        )
        summary[arm]["four_family_f1_mean_over_models"] = round(
            sum(ff_means) / len(ff_means), 4
        )

    changed = sum(
        1
        for k in shared
        if Counter(keyed["v10_shipped"][k]["rx_keys"])
        != Counter(keyed["v09_previous"][k]["rx_keys"])
    )
    fidelity = sum(
        1
        for k in shared
        if cf.stage._key_sig(keyed["v09_previous"][k]["rx_keys"])
        == cf.stage._key_sig(keyed["v09_previous"][k]["retained_rx_keys"])
    )

    d_exact = (
        summary["v10_shipped"]["prescription_exact_rate"]
        - summary["v09_previous"]["prescription_exact_rate"]
    )
    d_f1 = (
        summary["v10_shipped"]["prescription_micro_f1"]
        - summary["v09_previous"]["prescription_micro_f1"]
    )
    confirmed = d_exact >= 0 and d_f1 >= -0.005

    artifact = {
        "schema_version": "exectv2.prescription_lens_v10_holdout.v1",
        "date": "2026-08-10",
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "test59",
        "row_policy": "aggregate_only",
        "model_calls": 0,
        "replay": "ordered no-call replay of retained sealed structured sidecars",
        "arm_provenance": {
            "v10_shipped": "current tree",
            "v09_previous": "pre-change tree restored via git stash; not a re-implementation",
        },
        "n_letter_model_cells": len(shared),
        "n_unreplayable": {arm: loaded[arm]["unreplayable"] for arm in ARMS},
        "cells_changed_by_the_two_removed_rules": changed,
        "fidelity": {
            "v09_arm_matches_retained_sealed_rx_keys": fidelity,
            "checked": len(shared),
            "rate": round(fidelity / len(shared), 4),
        },
        "arms": summary,
        "by_model": per_model,
        "predeclared_kill_criterion": {
            "confirm_if": "exactness delta >= 0 and prescription micro F1 delta >= -0.005",
            "exactness_delta": round(d_exact, 4),
            "prescription_micro_f1_delta": round(d_f1, 4),
            "verdict": "CONFIRMED" if confirmed else "REFUTED",
        },
        "claim_boundary": (
            "Predeclared holdout confirmation of an already-selected dev140 "
            "simplification. Aggregate-only. No tuning. Not clinical validation "
            "and not the published ExECT benchmark."
        ),
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")

    print(f"cells={len(shared)} changed_by_removed_rules={changed}")
    print(f"v09 fidelity vs retained sealed Rx keys: {artifact['fidelity']['rate']}")
    for arm in ARMS:
        a = summary[arm]
        print(
            f"{arm:14s} P={a['prescription_precision']:.4f} R={a['prescription_recall']:.4f} "
            f"RxF1={a['prescription_micro_f1']:.4f} exact={a['prescription_exact_rate']:.4f} "
            f"four_family={a['four_family_f1_mean_over_models']:.4f}"
        )
    print(f"delta exactness={d_exact:+.4f}  delta RxF1={d_f1:+.4f}")
    print(f"VERDICT: {artifact['predeclared_kill_criterion']['verdict']}")
    print(f"wrote {OUT.relative_to(REPO_ROOT)}")
    return 0 if confirmed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", choices=ARMS, help="replay one arm on the current tree")
    group.add_argument("--combine", action="store_true", help="score both captures")
    args = parser.parse_args()
    return capture(args.capture) if args.capture else combine()


if __name__ == "__main__":
    raise SystemExit(main())
