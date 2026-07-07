"""P0.1 — Faithfulness x correctness 2x2 + over-inference rate.

Reliability scorecard, Phase 0 (zero model budget). Joins, per row on the
canonical ``v0_reference`` subject layer (decision 0018 — single GPT
structured-event pass on gpt-4.1-mini), evidence faithfulness with Purist
correctness on both frozen splits. Produces:

  - holdout/validation faithfulness rate as a proper metric on the production path
  - the faithful-but-clinically-wrong cell (the project's whole thesis)
  - the directional over-inference rate on unknown-gold rows

The full-gpt-4.1 V12 ``final``-layer faithfulness (703/750, 423/450) is reported
alongside only as ``[comparator: V12-full-gpt4.1]``.

No model calls; deterministic replay of frozen artifacts.

Usage:
    uv run python experiments/build_gan2026_reliability_p0_1_faithfulness_correctness.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)

OUT_JSON = rc.EXPERIMENTS / "gan2026_reliability_p0_1_faithfulness_correctness_2026-06-17.json"
OUT_MD = rc.EXPERIMENTS / "gan2026_reliability_p0_1_faithfulness_correctness_2026-06-17.md"

UNKNOWN_PURIST = "seizure_freq_unknown"
SEIZURE_FREE_PURIST = "currently_no_seizure"


def analyse_split(name: str, path: Path) -> dict[str, Any]:
    rows = rc.load_jsonl(path)
    n = len(rows)

    # 2x2 faithfulness x correctness on the canonical subject layer.
    cells = {
        "faithful_correct": 0,
        "faithful_wrong": 0,
        "unfaithful_correct": 0,
        "unfaithful_wrong": 0,
    }
    faithful = correct = 0
    # comparator faithfulness (full-gpt-4.1 V12 final-layer flag).
    comparator_faithful = 0

    # over-inference on unknown-gold rows.
    unknown_gold = 0
    unknown_over_read = 0
    over_read_to_rate = 0
    over_read_to_seizure_free = 0

    for row in rows:
        ev = rc.subject_evidence_valid(row)
        ok = rc.subject_purist_correct(row)
        faithful += int(ev)
        correct += int(ok)
        key = ("faithful" if ev else "unfaithful") + ("_correct" if ok else "_wrong")
        cells[key] += 1
        comparator_faithful += int(rc.comparator_final_evidence_valid(row))

        gold = rc.subject_gold_purist(row)
        pred = rc.subject_predicted_purist(row)
        if gold == UNKNOWN_PURIST:
            unknown_gold += 1
            if pred != UNKNOWN_PURIST:
                unknown_over_read += 1
                if pred == SEIZURE_FREE_PURIST:
                    over_read_to_seizure_free += 1
                else:
                    over_read_to_rate += 1

    fc = cells["faithful_correct"]
    fw = cells["faithful_wrong"]
    return {
        "split": name,
        "rows": n,
        "faithfulness_rate": {
            "subject_v0_reference": [faithful, n],
            "comparator_V12_full_gpt4_1_final": [comparator_faithful, n],
        },
        "purist_accuracy_subject": [correct, n],
        "two_by_two": cells,
        "faithful_but_wrong_cell": {
            "count": fw,
            "share_of_faithful": fw / faithful if faithful else None,
            "share_of_all": fw / n if n else None,
            "interpretation": "evidence cited exactly yet clinical label wrong — grounding != selection",
        },
        "faithful_and_correct_cell": {"count": fc, "share_of_all": fc / n if n else None},
        "over_inference_unknown_gold": {
            "unknown_gold_rows": unknown_gold,
            "over_read_any": unknown_over_read,
            "over_read_rate": unknown_over_read / unknown_gold if unknown_gold else None,
            "to_quantified_rate": over_read_to_rate,
            "to_seizure_free": over_read_to_seizure_free,
        },
    }


def render_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# P0.1 — Faithfulness x Correctness 2x2 + Over-Inference Rate\n")
    lines.append(f"Date: {result['date']}  ·  Model calls: 0 (deterministic replay)\n")
    lines.append(
        "Canonical subject: single GPT structured-event pass on `gpt-4.1-mini`, read "
        "from the `v0_reference` layer (decision 0018). The full-gpt-4.1 V12 `final` "
        "layer appears only as a tagged comparator.\n"
    )
    for split in result["splits"]:
        n = split["rows"]
        sf, _ = split["faithfulness_rate"]["subject_v0_reference"]
        cf, _ = split["faithfulness_rate"]["comparator_V12_full_gpt4_1_final"]
        pc, _ = split["purist_accuracy_subject"]
        c = split["two_by_two"]
        lines.append(f"\n## {split['split']} (n={n})\n")
        lines.append(
            f"- **Faithfulness rate (subject, v0_reference):** {sf}/{n} = {rc.fmt_pct(sf, n)}"
        )
        lines.append(
            f"- Faithfulness `[comparator: V12-full-gpt4.1]`: {cf}/{n} = {rc.fmt_pct(cf, n)}"
        )
        lines.append(f"- Purist accuracy (subject): {pc}/{n} = {rc.fmt_pct(pc, n)}\n")
        lines.append("| | Purist correct | Purist wrong |")
        lines.append("|---|:--:|:--:|")
        lines.append(
            f"| **Evidence faithful** | {c['faithful_correct']} | "
            f"**{c['faithful_wrong']}** (faithful-but-wrong) |"
        )
        lines.append(
            f"| **Evidence unfaithful** | {c['unfaithful_correct']} | {c['unfaithful_wrong']} |"
        )
        fbw = split["faithful_but_wrong_cell"]
        lines.append(
            f"\nThe faithful-but-wrong cell = **{fbw['count']}** rows "
            f"({rc.fmt_pct(fbw['count'], n)} of all; "
            f"{fbw['share_of_faithful']:.1%} of faithful rows). "
            "Exact-span evidence does not imply correct selection — the thesis cell.\n"
        )
        oi = split["over_inference_unknown_gold"]
        if oi["unknown_gold_rows"]:
            lines.append(
                f"- **Over-inference on unknown-gold rows:** {oi['over_read_any']}/"
                f"{oi['unknown_gold_rows']} = {rc.fmt_pct(oi['over_read_any'], oi['unknown_gold_rows'])} "
                f"over-read (→rate {oi['to_quantified_rate']}, →seizure-free {oi['to_seizure_free']})."
            )
    lines.append("\n---\n")
    lines.append(
        "Headline: faithfulness is high on the production path, but the faithful-but-wrong "
        "cell is non-empty on both splits — the system grounds its evidence yet still "
        "over-selects, which is exactly the unknown-vs-rate over-inference the strand named. "
        "Faithfulness (grounding) and task correctness (selection) are distinct reliability axes.\n"
    )
    return "\n".join(lines)


def main() -> None:
    splits = [
        analyse_split("validation750", rc.REASONER_VALIDATION750),
        analyse_split("test450", rc.REASONER_TEST450),
    ]
    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_p0_1_faithfulness_correctness",
        "date": "2026-06-17",
        "dimensions": ["Faithfulness", "Factuality", "Task correctness"],
        "provenance": rc.provenance_block(
            subject="single_se_mini_v0_reference",
            sources=[rc.REASONER_VALIDATION750, rc.REASONER_TEST450],
        ),
        "splits": splits,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    for s in splits:
        sf, n = s["faithfulness_rate"]["subject_v0_reference"]
        fbw = s["faithful_but_wrong_cell"]["count"]
        oi = s["over_inference_unknown_gold"]
        print(
            f"  {s['split']}: faithful {sf}/{n} ({rc.fmt_pct(sf, n)}), "
            f"faithful-but-wrong {fbw}, "
            f"unknown over-read {oi['over_read_any']}/{oi['unknown_gold_rows']}"
        )


if __name__ == "__main__":
    main()
