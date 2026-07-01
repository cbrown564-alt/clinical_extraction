> **Superseded for navigation —** canonical summary: [`../../canon/04_scoring.md`](../../canon/04_scoring.md). Like-for-like 0.3877 benchmark surface tables. Full detail retained below.

# ExECTv2 Benchmark-Surface Overall: The Like-for-Like Read

Date: 2026-06-18
Scope: All nine entities on dev140, scored on the published benchmark surface
(exact normalized phrase + all attributes + CUI), directly comparable to the
Fonferko-Shadrach 2024 overall headline.
Status: dev140 analysis-only; no full-200 audit. The number is a like-for-like
comparator, not a benchmark-beating claim.

## Bottom Line

The key-family synthesis (`exectv2_final_key_family_architecture_synthesis_2026-06-18`)
reports per-family results on the **clinical-recovery** surface (concept identity,
frequency state, components). That surface is more lenient than, and not
comparable to, the published ExECTv2 headline of **F1 0.87 per item / 0.90 per
letter**, which scores exact normalized phrase plus all attributes plus CUI.

This note produces the missing like-for-like number by merging the current best
per-family predictions into a single all-nine prediction and scoring it through
the same `score_overall` path the deterministic all-9 scorecard and the Phase-7
audit use.

Two findings:

1. The best achievable benchmark-surface overall from current artifacts is
   **0.3877 per item / 0.6972 per letter** on dev140 — roughly **45% of the
   paper's per-item headline**. The gap is structural: it is dominated by exact
   phrase/attribute/CUI fidelity, not by concept recall.
2. **Stacking the hybrid verifiers lowers the benchmark overall**, from
   deterministic-only `0.3687` to all-hybrid `0.3100`, even though the verifiers
   raise phrase-only and semantic. The clinical-recovery gains are orthogonal to,
   and for SeizureFrequency antagonistic with, annotation-format reproduction.

## How The Number Is Produced

`runners/run_hybrid_benchmark_overall.py` overlays the saved per-family hybrid
verifier predictions onto the deterministic all-9 substrate, then scores the
merged all-nine letter set under three configs (phrase-only, semantic, benchmark).
No LLM calls: the four key-family predictions are read from their registered run
JSONL artifacts. `--deterministic-for` selects rules vs hybrid per family, so the
deterministic-only and best-of variants are the same code path.

## Table 1: Overall Benchmark Surface vs Paper (dev140)

| Architecture | Benchmark item F1 | Benchmark letter F1 | Semantic item F1 | Phrase-only item F1 | Δ item vs paper |
| --- | ---: | ---: | ---: | ---: | ---: |
| Paper (published, full 200) | **0.87** | **0.90** | — | — | — |
| Best-of (rules + hybrid Investigations) | **0.3877** | 0.6972 | 0.4008 | 0.4549 | −0.4823 |
| Deterministic-only (today) | 0.3687 | 0.6747 | 0.3815 | 0.4627 | −0.5013 |
| All-hybrid (four verifiers) | 0.3100 | 0.6454 | 0.3890 | 0.4984 | −0.5600 |

Recommended caption:

> The only surface comparable to the 0.87/0.90 headline is the benchmark layer
> (with CUI, all features). The current best all-nine architecture reaches
> `0.3877` per item on dev140. Adding the hybrid verifiers raises phrase-only and
> semantic recall but lowers the benchmark overall, because LLM clinical-recovery
> gains do not reproduce the exact annotation bundle the benchmark scores.

## Table 2: Per-Family Benchmark Cells — Rules vs Hybrid (dev140)

| Family | Deterministic item F1 | Hybrid verifier item F1 | Benchmark winner | Paper item F1 |
| --- | ---: | ---: | --- | ---: |
| Investigations | 0.3220 | **0.4835** | Hybrid (+0.16) | 0.95 |
| Diagnosis | **0.3216** | 0.2834 | Rules | 0.85 |
| Prescription | **0.3020** | 0.2477 | Rules | 0.87 |
| SeizureFrequency | **0.6921** | 0.3472 | Rules (+0.34) | 0.66 |

Recommended caption:

> Only the Investigations verifier improves its benchmark cell over rules. For
> SeizureFrequency the hybrid suppression stack — `0.782` on the clinical-recovery
> surface — collapses to `0.347` on the benchmark surface, well below the
> deterministic `0.692`. The verifiers optimize concept recovery, not exact
> phrase/attribute/CUI reproduction.

## Table 3: Best-of Per-Entity Benchmark vs Paper (dev140)

| Entity | Source | Item F1 | Paper item F1 | Δ vs paper | Letter F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| SeizureFrequency | rules | 0.6921 | 0.66 | **+0.0321** | 0.9247 |
| WhenDiagnosed | rules | 0.8182 | 0.91 | −0.0918 | 0.9000 |
| BirthHistory | rules | 0.5574 | 0.97 | −0.4126 | 0.7317 |
| EpilepsyCause | rules | 0.5333 | 0.90 | −0.3667 | 0.5806 |
| Investigations | hybrid | 0.4835 | 0.95 | −0.4665 | 0.7385 |
| Diagnosis | rules | 0.3216 | 0.85 | −0.5284 | 0.7500 |
| Prescription | rules | 0.3020 | 0.87 | −0.5680 | 0.5223 |
| PatientHistory | rules | 0.2371 | 0.78 | −0.5429 | 0.5475 |
| Onset | rules | 0.2857 | 0.96 | −0.6743 | 0.4167 |

Recommended caption:

> On the benchmark surface, only SeizureFrequency exceeds its published cell
> (`+0.03`, dev140) and WhenDiagnosed is close. Every other family is far below
> the paper, driven by exact phrase/attribute/CUI gaps rather than concept misses.
> SeizureFrequency exceeding its paper cell is a dev140 reading; the full-200 SF
> audit (2026-06-11, older pipeline) was `0.321/0.539`, so this is not yet a
> confirmed full-200 result.

## What The Gap Is Made Of

The phrase-only overall (`0.46`-`0.50`) versus benchmark overall (`0.31`-`0.39`)
spread shows the loss is concentrated in the with-CUI and attribute-bundle
strictness, not in concept recall. The system recovers the clinical content (e.g.
Prescription clinical-headline F1 `0.91` on the deterministic substrate) but does
not reproduce the exact annotation bundle the benchmark scores (Prescription
benchmark `0.30`). The published `0.87` was a rule-based pipeline tuned precisely
to reproduce those bundles.

## Claim Language

Supported:

> On the benchmark surface comparable to the published 0.87/0.90 headline, the
> current best ExECTv2 all-nine architecture reaches `0.3877` per item / `0.6972`
> per letter on dev140 — roughly 45% of the paper's per-item headline.

Supported:

> Adding the hybrid key-family verifiers lowers the benchmark overall relative to
> the deterministic substrate (`0.3687` to `0.3100` per item), because the
> verifiers' clinical-recovery gains do not transfer to exact
> phrase/attribute/CUI reproduction; for SeizureFrequency they actively regress it.

Supported:

> The clinical-recovery surface and the benchmark surface measure different
> objectives. Deterministic projection owns the benchmark surface; the hybrid owns
> clinical recovery. Combining them naively is worse on the benchmark than rules
> alone.

Not supported:

> The key-family architecture approaches the published benchmark headline.

Not supported:

> The hybrid verifiers improve the benchmark-surface overall.

Not supported:

> SeizureFrequency clears its published benchmark cell on the full 200 (only the
> dev140 deterministic reading exceeds it; full-200 is not audited on the current
> pipeline).

## Next Work, If Any

If the benchmark headline is a goal, the lever is deterministic phrase/CUI and
attribute-bundle fidelity — particularly Prescription and Investigations exact
bundles, and PatientHistory recall — not more LLM adjudication. The verifiers
should be scoped to the clinical-recovery objective they serve and kept out of
the benchmark path except for Investigations.

A full-200 benchmark-surface audit of the best-of architecture remains gated under
the standing policy: it requires benchmark-beating dev evidence and a predeclared
locked architecture, neither of which holds. The dev140 number here is a
comparator, not an audit trigger.

## Source Artifacts

- Runner: `runners/run_hybrid_benchmark_overall.py`
- All-hybrid scorecard:
  `experiments/exectv2_hybrid_benchmark_overall_dev_20260618.json` / `.md`
- Best-of scorecard (registered):
  `experiments/exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json` / `.md`
- Registered run: `exectv2_hybrid_benchmark_overall_dev_20260618`
  (best-of config; metrics `benchmark_per_item_f1=0.3877`)
- Deterministic all-9 baseline (2026-06-17):
  `experiments/exectv2_deterministic_all9_dev_20260617.md`
- Key-family synthesis:
  `docs/research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md`
- Benchmark protocol and published cells:
  `docs/plans/exectv2/06_evaluation_and_benchmark_protocol.md`
