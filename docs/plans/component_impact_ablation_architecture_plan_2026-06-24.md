> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md).

# Component Impact Ablation Architecture Plan

Date: 2026-06-24

Rationalisation status, 2026-06-25: complete. The live source of truth is now
the Gan and ExECTv2 component-ablation contracts plus generated payloads; this
plan is retained as the design/build record. No active work remains from this
plan in the current priority sequence.

> **Update, 2026-06-24 (post-completion):** the live Component Impact comparison was
> trimmed to one best performer per architecture family —
> `deterministic_canonical_pipeline`, `hybrid_structured_events`, and
> `llm_only_canonical_pipeline`. The reset-native hybrid (`hybrid`) and the direct
> labeler (`llm_only_direct_labeler`) were dropped as redundant — each the weaker
> sibling of the kept line on the same validation-750 basis — so the seam now routes
> **three** Gan ladders, not five. The build history below, which exercised all
> five, is retained as the record of the consolidation work; the current set of
> record is the contract, `docs/design/gan2026_component_ablation_contract_2026-06-24.md`.

Scope: a spin-off project to give the Component Impact surface a single, honest,
replay-only ablation architecture that decomposes **every** Gan 2026 pipeline —
and ExECTv2 — into the cumulative per-stage contributions that actually move the
score. It exists because the work so far surfaced a real blocker: several Gan
architectures (most importantly `hybrid_structured_events`) have many
answer-transforming stages that should ablate cleanly, but the project's ablation
machinery is scattered across three unrelated config mechanisms and a pile of
one-off scripts, so the stage-ladder builder collapsed those architectures into a
single uninformative bar. No model calls and no holdout-facing claims are
authorized by this plan.

## Executive Summary

The Component Impact page should answer one question identically for both
datasets: **how much does each component contribute to the final score?** The
honest shape of that answer is a cumulative *stage ladder* — a baseline producer
surface plus the marginal contribution of each downstream stage stacked on top,
rendered as a waterfall.

ExECTv2 already does this well: its saved summaries carry a 7-surface
`score_ladder`, and the frontend renders a rich waterfall. The Gan side does not
yet, and the reason is **not** that Gan's stages are flat. It is that:

1. Gan's ablation seams live in **three different, unrelated mechanisms**
   (`AblationConfig`, `disabled_ablation_switches`, `StructuredRepairConfig`),
   plus several standalone ablation scripts; and
2. the stage-ladder builder only learned how to tap **one** of them (the hybrid
   deep-replay), so it scored the other architectures from their final answer
   only — flattening real, multi-stage pipelines into a single bar.

The fix is an architectural one: define **one stage-ablation seam** that every
architecture's downstream exposes, route all five Gan architectures through it,
and feed the existing unified `ComponentLadder` frontend. `hybrid_structured_events`
is the priority proof case — it reaches ~0.88 purist through a genuine
extract → normalize → project → render chain, and those stages should ablate.

## Status: What Has Been Done

### Frontend (done)

- `frontend/lib/componentLadder.ts` — a dataset-agnostic `ComponentLadder`
  view-model (architectures → stages, each with score, signed delta, per-category
  deltas, component-type tone) plus `adaptExectv2Ladder()`.
- `frontend/components/laboratory/ComponentLadderSurface.tsx` — the single shared
  waterfall surface: a hero final score (2 dp) + biggest-contributor callout, a
  horizontal-waterfall row per stage coloured by component type, deltas in integer
  **points**, a "compare architectures" strip, and a stage-detail collapsible.
- `frontend/components/exectv2/Exectv2ComponentImpact.tsx` — rewired onto the
  shared surface (≈70 lines, down from ≈415). Typecheck clean.

This nails the "look and function the same for both" requirement at the surface
level. The Gan route still renders the old rule-group leave-one-out page and has
not been rewired yet (deliberately — pending the backend below).

### Backend (done — 2026-06-24)

- `src/.../gan2026/artifact_analysis/component_stage_ladder.py` — the Gan
  stage-ladder replay builder, no model calls, now routed through one
  `StageLadderProvider` seam with four thin adapters. Coverage:
  - `deterministic_canonical_pipeline` (`AblationConfig` adapter) — re-run of the
    canonical stages. **Flat** on purist category (0.91 → 0.91 → 0.91) — an honest
    finding, not a gap.
  - `hybrid` (`disabled_ablation_switches` adapter) — cumulative deep-replay.
    **Real build-up**: 0.67 → 0.71 → 0.73 → 0.73.
  - `hybrid_structured_events` (`StructuredRepairConfig` adapter) — **the gap, now
    fixed.** Replays `parse_structured_json` over saved `raw_output` with the repair
    config cumulatively enabled: LLM events+selection 0.61 → +Normalize 0.64 →
    +Evidence projection 0.79 → +Clinical repair families 0.89. Evidence projection
    is the biggest single contributor (+0.159).
  - `llm_only_canonical_pipeline`, `llm_only_direct_labeler` (label-repair adapter)
    — two-rung ladders, model label → label repair: 0.66 → 0.78 and 0.57 → 0.75.
  - All five score on one identical validation-750 basis (abstain/null → unknown).

### Findings that shape this plan

- The hybrid `..._live_candidate_sets_gpt41mini_2026-06-08` artifact was audited
  and is clean (750/750 unique rows, 0 duplicates, 0 gaps, 0 call errors, 1 parse
  error); the deep-replay reproduces the registered Phase-1 report
  (589 rendered / 160 null / 43 routed). No re-run is needed for hybrid.
- The deterministic pipeline's downstream is genuinely flat on purist *category*;
  hybrid's is not. The difference is the producer: rules emit clean labels;
  hybrid's LLM emits an *assessment* the deterministic layers must render. This is
  the thesis ("LLM reasons about clinical truth; deterministic owns
  representation") made visible — and it generalizes the value of showing layers.
- `hybrid_structured_events` (`llm/hybrid_structured_events.py`) has the seams we
  need: `StructuredEventRecord`/`StructuredSelectionRecord` (LLM output),
  `_normalize_event()` → `NormalizedEventRecord`, and a `StructuredRepairConfig`
  with multiple named repair modes. The builder simply never tapped them.

## The Goal

One ablation architecture such that:

1. Every Gan architecture decomposes into a cumulative per-stage purist-accuracy
   ladder, computed **replay-only from saved producer outputs (no model calls)**,
   with each downstream stage independently disable-able.
2. `hybrid_structured_events` shows its real extract → normalize → project →
   render contributions, not a single bar.
3. The five Gan ladders and the four ExECTv2 ladders render through the **same**
   `ComponentLadderSurface`, with the same controls and visual language.
4. The decomposition is honest: stages that genuinely contribute ~0 (e.g. the
   deterministic pipeline's repair) are shown as ~0, and the per-architecture
   scoring basis (especially abstain/null handling) is declared, not hidden.

## Diagnosis: Why We Got Lost

There is no single notion of "a pipeline stage you can turn off." There are at
least three, plus orphaned scripts:

| Mechanism | Where | What it ablates | Used by |
| --- | --- | --- | --- |
| `AblationConfig` (`enabled_groups`, `disabled_rule_ids`) | `deterministic/rule_metadata.py` | deterministic **extraction** rule families | `deterministic*`, old `/run/ablation` |
| `disabled_ablation_switches` | `runner.build_unified_pipeline_artifact` + `clinical_assessment_projection_*` | hybrid **normalize/project/verify** layers | `hybrid` deep-replay |
| `StructuredRepairConfig` (named modes) | `llm/hybrid_structured_events.py` | structured-events **normalize/repair** behaviour | `hybrid_structured_events` |
| `reset_stage_component_ablation_v6.py`, `projection_arbitration_ablation.py`, `seizure_free_duration_projection_ablation.py`, `projection_decision_matrix.py` | `artifact_analysis/` | various reset-stage / projection family deltas | one-off reports |

Each is reasonable in isolation. Together they mean the stage-ladder builder must
learn a bespoke tapping strategy per architecture, and `hybrid_structured_events`
fell through the cracks. The complexity is real and is the thing to reduce.

## The Architectural Idea: One Stage-Ablation Seam

Define a single, small contract that every architecture's **downstream** (the
deterministic part after the producer) implements:

```
StageLadderProvider
  producer_surface()                  -> per-row prediction with all downstream stages OFF
  stages()                            -> ordered [(stage_id, label, component_type)]
  predict(disabled_stage_ids) -> per-row monthly_frequency, replay-only, no model calls
```

The stage-ladder builder then becomes architecture-agnostic: for each architecture
it walks `stages()`, calls `predict()` with a cumulatively shrinking
`disabled_stage_ids`, scores purist accuracy + per-band at each step, and emits the
existing `ComponentLadder` payload. The three legacy mechanisms become **adapters**
behind this seam (an `AblationConfig` adapter, a `disabled_ablation_switches`
adapter, a `StructuredRepairConfig` adapter) rather than three parallel worlds the
builder must special-case.

This is the consolidation: one seam, three thin adapters, one builder, one surface.

## Per-Architecture Stage Maps (to confirm in Phase 1)

| Architecture | Producer | Downstream stages to ablate | Seam today |
| --- | --- | --- | --- |
| `deterministic_canonical_pipeline` | rule extraction+selection | normalize / benchmark-repair / evidence-trace | `AblationConfig` (flat on purist — confirm) |
| `hybrid` | LLM clinical assessment | normalize / projection / verify-route | `disabled_ablation_switches` (working) |
| `hybrid_structured_events` | LLM events + selection | normalize (`_normalize_event`) / repair modes / selection-projection / render | `StructuredRepairConfig` + normalize/selection logic (**not yet tapped**) |
| `llm_only_canonical_pipeline` | single LLM call (rules in prompt) | format repair only? | unknown — confirm in Phase 1 |
| `llm_only_direct_labeler` | single LLM call | format repair only? | unknown — confirm in Phase 1 |

ExECTv2 stays the reference implementation: its `score_ladder` already is a
`StageLadderProvider` in spirit.

## Phased Plan

| Phase | Work | Gate | Status |
| --- | --- | --- | --- |
| 0 | Unified `ComponentLadderSurface`; ExECTv2 rewired; Gan builder for deterministic (flat) + hybrid (deep-replay) | none | ✅ done |
| 1 | **Ablation-machinery audit.** Catalogue every ablation mechanism and script; map each architecture's true answer-transforming stages and which seam each rung taps. One map doc. | read-only | ✅ done — `docs/research/gan2026/architecture/gan2026_ablation_machinery_audit_2026-06-24.md` |
| 2 | **Define the `StageLadderProvider` seam** + adapters (`AblationConfig`, `disabled_ablation_switches`, `StructuredRepairConfig`, label-repair). | additive | ✅ done |
| 3 | **Wire `hybrid_structured_events` through the seam** (priority). Real extract → normalize → project → render purist deltas, replay-only. | validation-only replay | ✅ done — 0.61 → 0.64 → 0.79 → 0.89 |
| 4 | Wire `llm_only_*`; re-express `deterministic_canonical` and `hybrid` through the seam so all five share one code path; retire bespoke tapping. | validation-only replay | ✅ done |
| 5 | **Frontend + contract.** `adaptGan2026Ladder`, `fetchGan2026ComponentAblation`, rewire `GanComponentImpact`; Gan component-type tones; contract doc; tests; register artifacts. | none | ✅ done — contract `docs/design/gan2026_component_ablation_contract_2026-06-24.md` |

## Guardrails (inherited)

- Replay-only. No model calls. The hybrid and structured-events producers are read
  from saved validation750 artifacts; only deterministic downstream stages are
  re-run.
- No invented precision. Where a stage's contribution cannot be cleanly isolated
  from saved artifacts, report it as pending rather than estimate it.
- Declare the per-architecture scoring basis explicitly — in particular the
  abstain/null policy (current builder maps abstain → unknown and scores over all
  750 rows). Keep the basis identical across architectures so the cross-stack
  comparison is apples-to-apples.
- Validation-only. No `test450` read is authorized by this plan.

## Open Questions (resolved 2026-06-24)

1. **Abstain/null basis** — score over all 750 rows with abstain→unknown,
   identically for every architecture, so the cross-stack comparison is
   apples-to-apples. Declared in the contract. (A rendered-basis side-car can be
   added later if hybrid's headline needs it, but the all-rows basis is the single
   declared surface.)
2. **`StructuredRepairConfig` named modes** — they map cleanly onto the
   normalize/project/render boundaries. The ladder rungs are exactly `raw_model` →
   `+basic_label_repair` → `selected_evidence` → full stack; JSON-dialect repair is
   held on at every rung as parse-level recovery, not a label transformation. No
   finer/coarser stage set was needed.
3. **Per-band breakdown** — kept. The Gan ladder carries the six purist boundary
   bands as the family analog, with `category_deltas` per stage, rendered in the
   shared `StageDetail` table.
4. **Legacy one-off scripts** — left in place for their historical reports; they
   are reports over the same `disabled_ablation_switches` / `StructuredRepairConfig`
   switches, not separate mechanisms, so the seam already subsumes them. Retiring
   them is optional cleanup, not required for the consolidation.

## Related

- [[final_project_consolidation_implementation_plan_2026-06-22]]
- ExECTv2 reference: `tasks/epilepsy_phenotyping/exectv2/reports/component_ablation_replay.py`
- ExECTv2 contract: `docs/design/exectv2_component_ablation_contract_2026-06-24.md`
- Three-way architecture comparison:
  `docs/research/gan2026/architecture/gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07.md`
