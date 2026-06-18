"""Step-1 replay decomposition for the simplest-near-ceiling architecture plan.

Decomposes the V12 fresh-evidence hybrid's validation750 Purist into the marginal
contribution of each architectural layer, using ONLY saved artifact data — no new
model calls, no test exposure. Reuses the per-layer Purist scores and recorded
guard-fallback reasons already materialised in the V12 validation artifact.

Plan: docs/research/gan2026/architecture/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md

Usage:
    uv run python experiments/build_gan2026_simplest_arch_decomposition_v1.py
"""

from __future__ import annotations

import collections
import json
from pathlib import Path
from typing import Any

ARTIFACT = Path(
    "experiments/"
    "gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl"
)
REPORT = Path(
    "experiments/"
    "gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16.md"
)


def _purist(layer: dict[str, Any] | None) -> bool:
    return bool(((layer or {}).get("comparison") or {}).get("purist_correct"))


def main() -> None:
    rows = [json.loads(line) for line in ARTIFACT.read_text(encoding="utf-8").splitlines() if line.strip()]
    n = len(rows)

    # Ladder-middle layers (all free from saved scores).
    v0 = raw = fmt = fin = 0
    # Replace/keep decomposition vs GPT-only V0.
    helped = hurt = neutral = 0
    keep_correct = keep_wrong = 0
    # Guard fallback detail and per-guard marginal (final vs format-only on fired rows).
    gate_detail: collections.Counter[str] = collections.Counter()
    guard_marginal: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])

    for r in rows:
        sl = r.get("score_layers") or {}
        v0c = _purist(r.get("v0_reference"))
        rawc = _purist(sl.get("raw_model"))
        fmtc = _purist(sl.get("format_only"))
        finc = _purist(sl.get("final"))
        v0 += v0c
        raw += rawc
        fmt += fmtc
        fin += finc

        action = (r.get("fresh_evidence_decision_record") or {}).get("action")
        if action == "replace_with_fresh_evidence_final":
            if finc and not v0c:
                helped += 1
            elif v0c and not finc:
                hurt += 1
            else:
                neutral += 1
        else:
            keep_correct += int(finc)
            keep_wrong += int(not finc)

        for event in r.get("action_render_events") or []:
            text = str(event)
            if "gate_fallback" in text:
                # e.g. "fresh_evidence_gate_fallback: original_seizure_free_to_unknown..."
                reason = text.split(":", 2)[1].strip() if ":" in text else text
                gate_detail[reason] += 1
                # Guard ON => final (fallback to original); guard OFF => format-only (model replacement).
                guard_marginal[reason][0] += int(finc)
                guard_marginal[reason][1] += int(fmtc)

    lines = [
        "# Gan 2026 — Simplest-Architecture Step-1 Decomposition (validation750)",
        "",
        "Date: 2026-06-16",
        "",
        "Replay-only decomposition of the V12 fresh-evidence hybrid; no model calls,",
        "no test exposure. Source artifact:",
        f"`{ARTIFACT}` ({n} rows).",
        "",
        "Plan: `docs/research/gan2026/architecture/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md`.",
        "",
        "## Ladder-middle Purist (each layer a superset of the one above)",
        "",
        "| Layer | Model passes | Purist | Δ vs above |",
        "| --- | ---: | ---: | ---: |",
        f"| GPT structured-event only (`v0_reference`) | 1 | {v0}/{n} = {v0/n:.3f} | — |",
        f"| + fresh-evidence reasoner, raw | 3+reasoner | {raw}/{n} = {raw/n:.3f} | {raw - v0:+d} |",
        f"| + format-only label repair | 3+reasoner | {fmt}/{n} = {fmt/n:.3f} | {fmt - raw:+d} |",
        f"| + full deterministic guard layer (`final`) | 3+reasoner | {fin}/{n} = {fin/n:.3f} | {fin - fmt:+d} |",
        "",
        f"Reasoner net vs GPT-only: **{fin - v0:+d}** rows. "
        f"Deterministic guard layer net: **{fin - fmt:+d}** rows.",
        "",
        "## Where the reasoner's lift comes from (action decomposition vs GPT-only)",
        "",
        f"- Replace actions: **{helped} helped** (V0 wrong → final right), "
        f"**{hurt} hurt** (V0 right → final wrong), {neutral} neutral "
        f"→ net **{helped - hurt:+d}**.",
        f"- Keep actions: {keep_correct} correct, {keep_wrong} wrong.",
        "",
        "## Deterministic guard layer — per-guard marginal (rows where the guard fired)",
        "",
        "Guard ON = fall back to GPT original; guard OFF = keep the model's replacement.",
        "Marginal = (correct with guard) − (correct without).",
        "",
        "| Guard reason | Rows fired | Correct ON | Correct OFF | Marginal |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for reason, count in gate_detail.most_common():
        on, off = guard_marginal[reason]
        lines.append(f"| {reason} | {count} | {on} | {off} | {on - off:+d} |")
    total_fired = sum(gate_detail.values())
    lines += [
        "",
        f"Total guard fallbacks fired: **{total_fired}** of {n} rows "
        f"({total_fired / n:.1%}).",
        "",
        "## Reading",
        "",
        "- On validation750 the **reasoner's replace mechanism** is the engine of the",
        "  lift over a single GPT structured-event pass; the **deterministic guard",
        "  layer is near-inert here** (fires on a handful of rows).",
        "- This does NOT clear the guards: the synthesis established that validation",
        "  under-samples the clinical-wall cases the guards target, which are",
        "  concentrated in test450. Guard value can only be read on test.",
        "- The live questions for Step 2 (validation-only): does a **GPT-trace-only",
        "  reasoner** (drop Qwen+DeepSeek from the prompt; 1 model reused) retain the",
        f"  reasoner's {fin - v0:+d}-row lift? If so, 3 models collapse to 1.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT}")
    print(f"GPT-only {v0}/{n}={v0/n:.3f}  raw {raw}/{n}  fmt {fmt}/{n}  final {fin}/{n}={fin/n:.3f}")
    print(f"reasoner net {fin - v0:+d}  guard net {fin - fmt:+d}  guards fired {total_fired}")


if __name__ == "__main__":
    main()
