# Gan 2026 Component Ablation Contract

Date: 2026-06-24

Scope: the replay-only component-impact contract for Gan 2026, the sibling of the
[ExECTv2 component ablation contract](./exectv2_component_ablation_contract_2026-06-24.md).
It defines the one stage-ablation seam every Gan architecture implements, the
frontend payload, and the claim boundary. This is a planning and frontend payload
contract, not an authorization to read `test450` or to inspect rows.

## Claim Boundary

- Allowed now: validation (750) replay-only cumulative purist-accuracy ladders for
  the five Gan architectures, computed from already-saved producer artifacts.
- Not allowed here: new model calls, post-run tuning from ablation deltas, or
  promoting a deterministic repair layer into an "LLM-only" score line without
  declaring it.
- No `test450` holdout read and no row-level inspection is introduced.
- Abstain/null is scored as `unknown` over all 750 rows, identically for every
  architecture, so the cross-stack comparison is apples-to-apples.

## The Stage-Ablation Seam

Every architecture's downstream implements one provider interface
(`StageLadderProvider`):

```text
stages()                        -> ordered [(stage_id, label, component_type, interpretation)]
predict(disabled_stage_ids)     -> per-row monthly_frequency, replay-only, no model calls
golds()                         -> per-row gold monthly_frequency
build()                         -> StageLadder(golds, predictions_by_stage)   # cumulative
```

`build()` walks `stages()` and, at rung *i*, calls `predict()` with every stage
strictly downstream of *i* disabled — so each rung is "the answer with this much
of the deterministic stack on," and the delta versus the previous rung is stage
*i*'s marginal contribution. The three legacy ablation mechanisms are adapters
behind this seam:

| Provider | Adapter for | Architecture(s) |
| --- | --- | --- |
| `DeterministicCanonicalProvider` | `AblationConfig` (`BENCHMARK_REPAIR` group + evidence gate) | `deterministic_canonical_pipeline` |
| `HybridDeepReplayProvider` | `disabled_ablation_switches` (reset normalize/project/verify) | `hybrid` |
| `StructuredEventsProvider` | `StructuredRepairConfig` (normalize / selected-evidence / clinical families) | `hybrid_structured_events` |
| `LlmOnlyProvider` | label-repair toggle (`parse_decision_json` vs raw `final_label`) | `llm_only_canonical_pipeline`, `llm_only_direct_labeler` |

The scorer (purist category accuracy) is not an ablation boundary; it is the
declared measurement surface.

## Replay Surfaces (per architecture)

| Architecture | Stages (cumulative) |
| --- | --- |
| `deterministic_canonical_pipeline` | extract+normalize+select → benchmark-repair → evidence-trace check |
| `hybrid` | LLM assessment → normalize → projection → verify/route |
| `hybrid_structured_events` | LLM events+selection → normalize → evidence projection → clinical repair families |
| `llm_only_canonical_pipeline` | model label → label repair |
| `llm_only_direct_labeler` | model label → label repair |

Producer artifacts (read, never re-run):

- hybrid: `experiments/gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08.jsonl`
- structured-events: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`
- llm-only: `experiments/gan2026_three_way_comparison_validation750_llm_only_{canonical_pipeline,direct_labeler}_gpt41mini_2026-06-07.jsonl`

The deterministic pipeline has no producer artifact — its stages are re-run from
the canonical rule code (no model calls).

## Frontend Payload Contract

Component Impact ingests an aggregate payload with this top-level shape:

```json
{
  "artifact_kind": "gan2026_component_stage_ladder_set",
  "dataset": "gan2026",
  "generated_on": "2026-06-24",
  "metric": "purist_accuracy",
  "metric_label": "Purist accuracy",
  "method": "Cumulative stage ladder",
  "method_note": "validation · replay only · no model calls · 2026-06-24",
  "split": "validation",
  "row_inspection_policy": "aggregate_only",
  "allow_model_calls": false,
  "claim_boundary": "validation replay-only aggregate component-impact ladder",
  "categories": [],
  "architectures": []
}
```

Each architecture row:

```json
{
  "artifact_kind": "gan2026_component_architecture_ladder",
  "run_id": "hybrid_structured_events",
  "label": "Hybrid (LLM extract)",
  "model": "openai/gpt-4.1-mini",
  "decision": "diagnostic",
  "split": "validation",
  "row_count": 750,
  "final_score": 0.8893,
  "stages": [],
  "source_artifacts": [],
  "claim_boundary": "validation replay-only aggregate component-impact ladder",
  "row_inspection_policy": "aggregate_only"
}
```

Each stage row:

```json
{
  "stage_id": "evidence_projection",
  "label": "Evidence projection",
  "component_type": "projection",
  "score": 0.7947,
  "delta_from_previous": 0.1587,
  "is_baseline": false,
  "category_deltas": { "band_zero": 0.0, "band_monthly": 0.0 },
  "interpretation": "Re-derives the label from the selected evidence and note context."
}
```

`categories` are the six purist boundary bands (zero / sub-monthly / monthly /
weekly / daily / unknown), the Gan analog of the ExECTv2 families, carrying the
per-band `category_deltas`.

Frontend rules (mirrors ExECTv2):

- The Gan and ExECTv2 ladders render through the identical `ComponentLadderSurface`
  via `adaptGan2026Ladder` / `adaptExectv2Ladder`.
- Show the cumulative waterfall first; deltas are integer points.
- Keep `llm_assessment`, `normalize`, `projection`, `repair`, `verify_route`, and
  `scorer` visually distinct via the Gan descriptor component-type tones.
- Do not present a stage delta as causal impact unless
  `artifact_kind == "gan2026_component_stage_ladder_set"`.

## Completion Gate

Gan Component Impact is in stage-ladder mode when:

1. All five architecture ladders are generated from saved artifacts without model
   calls, on one identical validation-750 basis.
2. `hybrid_structured_events` shows its real four-stage build-up (not one bar).
3. Tests confirm the moving ladders, the seam baseline, and the shared basis.
4. The Gan laboratory route reads the payload through `ComponentLadderSurface`
   instead of the old rules-only leave-one-out page.

## Generated Replay Artifacts

Generated on 2026-06-24 (no model calls):

- `experiments/gan2026_component_stage_ladder_validation_20260624.json`
- `experiments/gan2026_component_stage_ladder_validation_20260624.md`
- `frontend/public/mock-data/gan2026/component-ablation.json`

Final purist accuracy and stage build-up:

| Architecture | Decision | Final | Stage ladder |
| --- | --- | ---: | --- |
| `deterministic_canonical_pipeline` | control | 0.9093 | 0.91 → 0.91 → 0.91 (flat; rules emit clean labels) |
| `hybrid` | diagnostic | 0.7253 | 0.67 → 0.71 → 0.73 → 0.73 |
| `hybrid_structured_events` | diagnostic | 0.8893 | 0.61 → 0.64 → 0.79 → 0.89 |
| `llm_only_canonical_pipeline` | diagnostic | 0.7773 | 0.66 → 0.78 |
| `llm_only_direct_labeler` | diagnostic | 0.7547 | 0.57 → 0.75 |

No `test450` or holdout-facing row-level inspection was introduced.
