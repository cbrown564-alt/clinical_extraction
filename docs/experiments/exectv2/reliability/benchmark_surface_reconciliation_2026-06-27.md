# ExECTv2 Benchmark-Surface Reconciliation (Portability Decomposition)

- Generated: `2026-06-27`
- Decision: **B** — full-200 reconciliation under holdout protocol, aggregate only
- Row inspection policy: `aggregate_only_no_full200_or_holdout_row_level_inspection`
- No model calls; replay reads saved summary JSON only (no JSONL row inspection)
- Extract script: `scripts/benchmark_surface_reconciliation_extract.py`
- Source replays:
  - dev140: `experiments/exectv2_component_off_replay_dev140_20260626.json`
  - full200: `experiments/exectv2_component_off_replay_full200_20260626.json`
- Category source: `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/component_ablation/definitions.yaml`
- Catalog rows: `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/reliability/catalog.yaml`

## Bottom Line

Toggling off every component tagged `benchmark_format` in `definitions.yaml`
(`residual_semantic_lens`, `headline_projection`) yields the **clinical-recovery**
surface at `dictionary_normalized`. The **headline** surface is
`headline_projection` (full pipeline). On the four-family `clinical_headline`
scorer, benchmark-format layers add **+0.040 to +0.148** overall F1 depending on
model — the headline is not recoverable from clinical facts alone.

The published-benchmark like-for-like comparator (`0.3877` / `0.6972` per
item/letter on dev140, nine entities) remains far below the paper headline
(`0.87` / `0.90`). That gap is orthogonal to the component-ablation delta above:
it measures exact phrase/attribute/CUI reproduction, not the four-family
clinical-recovery scorer.

## Method

1. Load existing one-component-off replay artifacts (dev140 and full200).
2. Filter ablation rows where `component_portability_category == benchmark_format`
   — the category field copied from `definitions.yaml` at replay build time.
3. **Headline F1** = `baseline_aggregate_score.overall.f1` on the
   `headline_projection` ablation row (`baseline_surface: headline_projection`).
4. **Clinical-recovery F1** = `component_off_aggregate_score.overall.f1` on the
   `residual_semantic_lens` ablation row (`component_off_surface:
   dictionary_normalized` — the deepest surface after removing all
   `benchmark_format` layers).
5. **Delta** = headline − clinical-recovery (positive means benchmark-format
   layers raise the score).

No re-scoring, no row-level reads, no new model calls.

## Table 1: dev140 — Model × Headline × Clinical-Recovery (catalog `rich_schema_runs`)

| Model (catalog) | Run | Headline F1 | Clinical-recovery F1 | Δ (format layers) |
| --- | --- | ---: | ---: | ---: |
| GPT-4.1-mini (control) | `exectv2_holistic_finding_assembly_v08_dev140` | 0.9155 | 0.8697 | +0.0458 |
| GPT-4.1-mini (partial hybrid) | `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | 0.9061 | 0.8601 | +0.0460 |
| DeepSeek chat | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | 0.9174 | 0.8334 | +0.0840 |
| Qwen 3.6 35B | `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | 0.9001 | 0.7526 | +0.1475 |

Scorer: four-family `clinical_headline` on dev140 (140 letters). DeepSeek and Qwen
show the largest format-layer lift; Qwen's clinical-recovery base is weakest
(`0.7526`), so format layers contribute nearly **+0.15** of the headline.

## Table 2: full200 — Model × Headline × Clinical-Recovery (same-core adjudicator)

| Model (catalog) | Run | Headline F1 | Clinical-recovery F1 | Δ (format layers) |
| --- | --- | ---: | ---: | ---: |
| GPT-4.1-mini | `exectv2_2call_no_sf_adjudicator_gpt41mini_full200` | 0.8356 | 0.7922 | +0.0434 |
| DeepSeek chat | `exectv2_2call_no_sf_adjudicator_deepseek_full200` | 0.8566 | 0.8110 | +0.0456 |
| Qwen 3.6 35B | `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200` | 0.8197 | 0.7797 | +0.0400 |

Scorer: four-family `clinical_headline` on full200 (200 letters). Format-layer
contribution is **stable at ~+0.04** across models on full200 — smaller than dev140
because the same-core adjudicator stack already bakes in more dictionary recovery
before the format layers.

Protocol: frozen full-200 aggregate readout under
`docs/experiments/exectv2/reliability/exectv2_component_off_full200_predeclaration_2026-06-26.md`.
Preflight passed for all three runs (`split=full200`, `row_count=200`).

## Table 3: dev140 Continuity — Published-Benchmark Like-for-Like (nine entities)

Carried forward from
`docs/research/exectv2_benchmark_surface_overall_2026-06-18.md` for continuity.
Different scorer (exact normalized phrase + all attributes + CUI); not the
four-family `clinical_headline` tables above.

| Surface | Per-item F1 | Per-letter F1 | vs paper (0.87 / 0.90) |
| --- | ---: | ---: | --- |
| Paper (published, full 200) | 0.87 | 0.90 | — |
| Best-of dev140 (rules + hybrid Inv) | **0.3877** | **0.6972** | −0.4823 / −0.2028 |
| Deterministic-only dev140 | 0.3687 | 0.6747 | −0.5013 |
| All-hybrid dev140 | 0.3100 | 0.6454 | −0.5600 |

Source artifact: `experiments/exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json`.

## Rules vs Hybrid Inversion

### Four-family clinical_headline (dev140, v08 rules vs v09 partial hybrid)

On the holistic finding-assembly pair in `catalog.yaml`, **rules wins on both
surfaces** — no headline/clinical-recovery inversion:

| Family | Rules headline | Hybrid headline | Rules clinical-recovery | Hybrid clinical-recovery |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0.9090 | 0.9090 | 0.8614 | 0.8614 |
| SeizureFrequency | 0.9053 | 0.9053 | 0.7814 | 0.7814 |
| Prescription | 0.9357 | 0.9357 | 0.9357 | 0.9357 |
| Investigations | **0.9132** | 0.8549 | **0.9132** | 0.8549 |

Hybrid simplification regresses Investigations (−0.058) identically on headline
and clinical-recovery; other families are unchanged between v08 and v09 on this
split.

### Nine-entity published-benchmark surface (dev140, rules vs hybrid verifiers)

The inversion documented in the 2026-06-18 benchmark-surface read persists and is
the reason benchmark-format layers must be reported separately:

| Family | Rules benchmark item F1 | Hybrid benchmark item F1 | Benchmark winner | Hybrid clinical-recovery (SF only) |
| --- | ---: | ---: | --- | ---: |
| Investigations | 0.3220 | **0.4835** | Hybrid (+0.16) | — |
| Diagnosis | **0.3216** | 0.2834 | Rules | — |
| Prescription | **0.3020** | 0.2477 | Rules | — |
| SeizureFrequency | **0.6921** | 0.3472 | Rules (+0.34) | 0.782 (hybrid CR surface) |

**Inversion:** SeizureFrequency hybrid verifier reaches `0.782` on the
clinical-recovery surface but collapses to `0.347` on the published benchmark
surface — well below deterministic rules at `0.692`. Stacking all four hybrid
verifiers lowers the nine-entity benchmark overall from `0.3687` (deterministic) to
`0.3100` (all-hybrid) even though phrase-only and semantic recall rise.

Combining the two reads: the `benchmark_format` component category in
`definitions.yaml` captures exactly the layers that create this split — residual
semantic recovery and headline projection add four-family headline F1 without
transferring to the published benchmark bundle.

## Proof That `definitions.yaml` Drives Scoring

1. **Category filter is YAML-sourced.** `definitions.yaml` tags only
   `residual_semantic_lens` and `headline_projection` as
   `component_portability_category: benchmark_format`. The extract script loads
   this file and selects ablation rows by that field; no hard-coded component list
   in the reconciliation logic.

2. **Surface keys match YAML boundaries.**

   | Component | Category | Baseline surface | Off surface |
   | --- | --- | --- | --- |
   | `residual_semantic_lens` | `benchmark_format` | `residual_semantic_added` | `dictionary_normalized` |
   | `headline_projection` | `benchmark_format` | `headline_projection` | `residual_semantic_added` |

   Clinical-recovery F1 reads `dictionary_normalized` — the terminal off-surface
   after removing the deepest `benchmark_format` component.

3. **Replay artifacts carry the category.** Each ablation row in the source JSON
   includes `component_portability_category` copied from `definitions.yaml` at
   build time (`scorer_version: exectv2_component_ablation_replay_v20260626`).
   Filtering on that field reproduces the reconciliation table without re-opening
   summaries.

4. **Component deltas decompose the gap.** Per-component contributions from the
   full replay (dev140 GPT v08 example):

   | Component | Category | Contribution Δ |
   | --- | --- | ---: |
   | `residual_semantic_lens` | `benchmark_format` | +0.0175 |
   | `headline_projection` | `benchmark_format` | +0.0283 |
   | **Sum (≈ headline − clinical-recovery)** | | **+0.0458** |

## Claim Boundary

Supported:

> On the four-family `clinical_headline` scorer, removing all `benchmark_format`
> components (per `definitions.yaml`) lowers overall F1 by +0.04 to +0.15 across
> catalog models; the headline is not equal to clinical-recovery.

> The published-benchmark like-for-like dev140 comparator remains `0.3877` /
> `0.6972` per item/letter — roughly 45% of the paper per-item headline.

> Rules beats hybrid on SeizureFrequency benchmark cells while hybrid wins
> clinical-recovery on SF; combining verifiers naively regresses the nine-entity
> benchmark overall.

Not supported:

> Full-200 published-benchmark (nine-entity CUI/phrase) numbers — not computed
> here; full-200 table above is four-family `clinical_headline` only.

> Holdout or row-level failure analysis — excluded by protocol.

## Source Artifacts

- `definitions.yaml` — portability categories and surface boundaries
- `reliability/catalog.yaml` — GPT / DeepSeek / Qwen run paths
- `experiments/exectv2_component_off_replay_dev140_20260626.{json,md}`
- `experiments/exectv2_component_off_replay_full200_20260626.{json,md}`
- `experiments/exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json` — dev140
  `0.3877` / `0.6972` continuity
- `docs/research/exectv2_benchmark_surface_overall_2026-06-18.md` — rules/hybrid
  inversion on published benchmark surface
- `scripts/benchmark_surface_reconciliation_extract.py` — category-filtered extract
- `scripts/build_exectv2_component_off_full200_replay.py` — upstream full-200 replay
