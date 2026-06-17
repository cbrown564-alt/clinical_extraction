"""P0.8 — Hard50 self-consistency re-tabulation (Consistency, partial).

Reliability scorecard, Phase 0 (zero model budget). Re-tabulates the saved
hard50 self-consistency run (k=4 samples per row, gpt-4.1-mini): per-row majority
fraction and normalized label entropy, and the agreement<->accuracy curve.

IMPORTANT temperature caveat: all four saved samples are temperature 0.0. At
temp-0 the model is near-deterministic (45/50 rows return identical samples), so
this artifact measures *reproducibility / determinism*, NOT genuine self-
consistency — a real self-consistency / semantic-entropy probe must sample at
VARYING temperatures. That varying-temperature run is P2.1 (fresh mini budget);
this no-call re-tabulation cannot substitute for it and does not draw the
"self-consistency is uninformative" conclusion from temp-0 data.

What does survive the caveat: even on the 45 fully-reproducible (temp-0 unanimous)
hard rows, accuracy is only ~0.69 — full reproducibility does not imply
correctness. And 5/50 rows disagree despite identical temperature (temp-0 non-
determinism on hard boundary cases).

No model calls; deterministic re-tabulation.

Usage:
    uv run python experiments/build_gan2026_reliability_p0_8_self_consistency.py
"""

from __future__ import annotations

import collections
import json
import math
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)

OUT_JSON = rc.EXPERIMENTS / "gan2026_reliability_p0_8_self_consistency_hard50_2026-06-17.json"
OUT_MD = rc.EXPERIMENTS / "gan2026_reliability_p0_8_self_consistency_hard50_2026-06-17.md"


def normalized_entropy(labels: list[str]) -> float:
    counts = collections.Counter(labels)
    n = len(labels)
    if n <= 1:
        return 0.0
    h = -sum((c / n) * math.log(c / n) for c in counts.values())
    return h / math.log(n)  # normalize to [0,1] by max entropy log(k)


def main() -> None:
    rows = rc.load_jsonl(rc.HARD50_SELF_CONSISTENCY)
    by_majority: dict[str, list[bool]] = collections.defaultdict(list)
    entropies: list[float] = []
    majority_fracs: list[float] = []
    correctness: list[bool] = []
    non_unanimous = 0

    for r in rows:
        ct = r["condition_trace"]
        calls = ct["model_call_results"]
        labels = [c.get("comparison", {}).get("predicted_purist_category") for c in calls]
        labels = [str(x) for x in labels if x is not None]
        k = len(labels)
        top = max(collections.Counter(labels).values()) if labels else 0
        frac = top / k if k else 0.0
        correct = bool(ct["final_comparison"]["purist_correct"])
        by_majority[f"{top}/{k}"].append(correct)
        entropies.append(normalized_entropy(labels))
        majority_fracs.append(frac)
        correctness.append(correct)
        if top < k:
            non_unanimous += 1

    agreement_curve = {
        bucket: {"n": len(v), "correct": sum(v), "accuracy": sum(v) / len(v)}
        for bucket, v in sorted(by_majority.items(), reverse=True)
    }
    # AUROC of majority fraction for predicting correctness (does self-agreement rank?).
    auroc_self = rc.auroc(majority_fracs, correctness)
    unanimous = agreement_curve.get(f"4/4", {"n": 0, "accuracy": None})

    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_p0_8_self_consistency",
        "date": "2026-06-17",
        "dimensions": ["Consistency"],
        "split": "validation_hard50",
        "n_rows": len(rows),
        "k_samples": 4,
        "sampling_temperature": 0.0,
        "probe_kind": "temp0_reproducibility_determinism (NOT varying-temperature self-consistency)",
        "non_unanimous_rows": non_unanimous,
        "agreement_accuracy_curve": agreement_curve,
        "unanimous_accuracy": unanimous.get("accuracy"),
        "self_agreement_auroc_for_correctness_temp0": auroc_self,
        "mean_normalized_entropy": sum(entropies) / len(entropies),
        "caveat": "All samples temp-0 -> measures reproducibility, not self-consistency. "
        "Genuine self-consistency / semantic entropy requires VARYING temperatures and is "
        "P2.1 (fresh mini budget). n=50 hard slice.",
        "provenance": rc.provenance_block(
            subject="single_se_mini_self_consistency_hard50",
            sources=[rc.HARD50_SELF_CONSISTENCY],
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"  non-unanimous (temp 0): {non_unanimous}/{len(rows)}")
    print(f"  unanimous (4/4) accuracy: {unanimous.get('accuracy')}")
    print(f"  self-agreement AUROC for correctness: {auroc_self}")


def render_md(result: dict[str, Any]) -> str:
    L: list[str] = []
    L.append("# P0.8 — Hard50 Self-Consistency Re-Tabulation (Consistency, partial)\n")
    L.append(f"Date: {result['date']}  ·  n={result['n_rows']} hard rows  ·  "
             f"k={result['k_samples']} samples @ temp {result['sampling_temperature']}  ·  "
             "Model calls: 0\n")
    L.append("## Agreement ↔ accuracy curve\n")
    L.append("| Majority (top/k) | n | Correct | Accuracy |")
    L.append("|---|---:|---:|---:|")
    for bucket, d in result["agreement_accuracy_curve"].items():
        L.append(f"| {bucket} | {d['n']} | {d['correct']} | {d['accuracy']:.1%} |")
    ua = result["unanimous_accuracy"]
    L.append(f"\n> **Temperature caveat.** All samples are temp-0, so this measures "
             "reproducibility/determinism, not self-consistency. Genuine self-consistency "
             "needs VARYING temperatures (P2.1). The reproducibility-conditioned reading "
             "below is what survives that caveat.\n")
    L.append(f"- **Temp-0 unanimous (4/4) accuracy: {ua:.1%}** — even fully reproducible "
             "hard rows are wrong ~31% of the time, so reproducibility ≠ correctness.")
    auroc = result["self_agreement_auroc_for_correctness_temp0"]
    L.append(f"- Temp-0 self-agreement AUROC: "
             f"{'%.4f' % auroc if auroc == auroc else 'n/a'} (uninformative *at temp-0*; "
             "no conclusion drawn about varying-temperature self-consistency).")
    L.append(f"- Temp-0 non-determinism: **{result['non_unanimous_rows']}/{result['n_rows']}** "
             "rows disagree across identical-temperature samples.")
    L.append(f"- Mean normalized label entropy: {result['mean_normalized_entropy']:.3f}\n")
    L.append(f"_{result['caveat']}_\n")
    L.append("---\n")
    L.append(
        "**Reading.** This artifact establishes only that the production path is largely "
        "*reproducible* at temp-0, and that reproducibility does not imply correctness "
        "(unanimous hard rows wrong ~31%). The genuine self-consistency / semantic-entropy "
        "question — does answer instability under VARYING temperature flag the unknown-vs-rate "
        "residual? — is deferred to P2.1, which samples at multiple temperatures.\n"
    )
    return "\n".join(L)


if __name__ == "__main__":
    main()
