# Gan 2026 Ablation-Machinery Audit (Phase 1 Map)

Date: 2026-06-24

> **Update, 2026-06-24:** the live Component Impact comparison was later trimmed to
> one best performer per family (`deterministic_canonical_pipeline`,
> `hybrid_structured_events`, `llm_only_canonical_pipeline`). The reset-native
> hybrid (`hybrid`) and the direct labeler (`llm_only_direct_labeler`) were dropped
> as redundant. Their per-rung tables below remain as the measured audit record;
> the `disabled_ablation_switches` / `HybridDeepReplayProvider` adapter and the
> direct-labeler wiring were removed from `component_stage_ladder.py` with them.

Scope: the read-only Phase 1 deliverable of the
[component-impact ablation architecture plan](../../../plans/component_impact_ablation_architecture_plan_2026-06-24.md).
It catalogues every mechanism by which a Gan 2026 pipeline stage can be turned
off, maps each architecture's true answer-transforming stages onto those
mechanisms, and names which seam each stage-ladder rung taps. No model calls; no
holdout reads.

## Why the audit existed

The stage-ladder builder originally tapped only one mechanism (the hybrid
deep-replay), so `hybrid_structured_events` and the two `llm_only` configs were
scored from their final answer alone and collapsed into a single uninformative
bar. The fix needed one inventory of "a stage you can turn off" before a single
seam could route every architecture. That inventory is below.

## Ablation mechanisms inventory

| Mechanism | Where | What it turns off | Stage granularity |
| --- | --- | --- | --- |
| `AblationConfig(enabled_groups, disabled_rule_ids)` | `deterministic/rule_metadata.py` | deterministic extraction rule families and the `BENCHMARK_REPAIR` group | rule-group / rule-id |
| `disabled_ablation_switches` | `hybrid/reset_clinical_assessment_pipeline.py` (+ `clinical_assessment_projection_*`) | hybrid normalize / projection / verify-route reset layers | named reset switch |
| `StructuredRepairConfig` | `llm/hybrid_structured_events.py` | structured-events JSON-dialect parse, basic/format label repair, selected-evidence repair, and 8 clinical-pattern repair families | per-repair boolean flag |
| label-repair toggle (implicit) | `llm/llm_only_canonical_pipeline.py`, `llm/llm_only_direct_labeler.py` `parse_decision_json` | the single `repair_prediction_label_with_evidence` pass that turns a raw model label into a scorable Gan label | on/off (re-parse vs raw `final_label`) |
| standalone scripts | `artifact_analysis/reset_stage_component_ablation_v6.py`, `projection_arbitration_ablation.py`, `seizure_free_duration_projection_ablation.py`, `projection_decision_matrix.py` | reset-stage / projection family deltas | bespoke, per-report |

The first four are the live seams the ladder needs. The standalone scripts are
one-off reports over the same underlying switches (`disabled_ablation_switches`
and `StructuredRepairConfig`); they are not separate mechanisms and are left in
place for their historical reports (Open Question 4).

## Per-architecture stage map (confirmed)

Each architecture's producer surface plus its true answer-transforming downstream
stages, the mechanism each rung taps, and the measured replay-only purist
accuracy at that rung (validation 750, no model calls).

### `deterministic_canonical_pipeline` — `AblationConfig` adapter

| Rung | Stage | Mechanism | Purist |
| --- | --- | --- | ---: |
| 0 | Extract + normalize + select | `AblationConfig` w/ `BENCHMARK_REPAIR` off | 0.9093 |
| 1 | Benchmark repair | enable `BENCHMARK_REPAIR` group | 0.9093 |
| 2 | Evidence trace check | exact-substring gate → unknown | 0.9093 |

Flat on purist *category* — the rules already emit clean Gan labels, so repair is
format-level and the gate drops nothing into the wrong category. Honest finding,
confirmed.

### `hybrid` — `disabled_ablation_switches` adapter

| Rung | Stage | Mechanism | Purist |
| --- | --- | --- | ---: |
| 0 | LLM clinical assessment | all reset switches off | 0.6693 |
| 1 | Normalize | enable `_HYBRID_NORMALIZE` | 0.7080 |
| 2 | Projection | enable `_HYBRID_PROJECT` | 0.7253 |
| 3 | Verify / route | enable `_HYBRID_VERIFY` | 0.7253 |

Real build-up: the LLM emits a clinical *assessment*; the deterministic reset
layers render it into a scored label.

### `hybrid_structured_events` — `StructuredRepairConfig` adapter (the gap)

| Rung | Stage | Mechanism (`StructuredRepairConfig`) | Purist |
| --- | --- | --- | ---: |
| 0 | LLM events + selection | JSON-dialect on; all label repair off | 0.6067 |
| 1 | Normalize | `basic_label_repair` | 0.6360 |
| 2 | Evidence projection | `selected_evidence_repair` | 0.7947 |
| 3 | Clinical repair families | 8 pattern families (diary / interval / breakthrough / non-epileptic / residual-jerk / post-change-burst / dated-sequence / elapsed-anchor) | 0.8893 |

This is the architecture the old builder flattened. Replaying
`parse_structured_json` over the saved `raw_output` with the repair config
cumulatively enabled recovers the genuine extract → normalize → project → render
chain. Evidence projection is the biggest single contributor (+0.159).

The named `StructuredRepairConfig` modes (`raw_model`, `strict_format`,
`selected_evidence_derivation`, `hybrid_full_stack`, …) **do** map cleanly onto
these three downstream stages (Open Question 2 resolved): the ladder rungs are
exactly `raw_model` → `+basic_label_repair` → `selected_evidence` → full stack.
JSON-dialect repair is held on at every rung because it is parse-level recovery of
a well-formed answer, not a label transformation.

### `llm_only_canonical_pipeline` / `llm_only_direct_labeler` — label-repair adapter

| Rung | Stage | Mechanism | Purist (canonical / direct) |
| --- | --- | --- | ---: |
| 0 | Model label | raw `final_label` from the parsed JSON | 0.6600 / 0.5733 |
| 1 | Label repair | `repair_prediction_label_with_evidence` | 0.7773 / 0.7547 |

Confirmed (Open Question for `llm_only` in the plan resolved): the downstream is a
single format/evidence label-repair pass, not a multi-stage stack — so a two-rung
ladder is the honest decomposition. The repair contribution is large because the
model frequently emits a clinically-correct but non-canonical label (e.g.
`up to 4 per day`) that scores as unknown until the deterministic layer renders it
in Gan form.

## Consolidation outcome

One seam — `StageLadderProvider` — with four thin adapters
(`DeterministicCanonicalProvider`, `HybridDeepReplayProvider`,
`StructuredEventsProvider`, `LlmOnlyProvider`), one builder
(`build_architecture_ladder`), one surface (`ComponentLadderSurface`). The three
legacy config mechanisms now live behind those adapters rather than as parallel
worlds the builder special-cases. All five architectures score on one identical
validation-750 basis (abstain/null → unknown across all rows).
