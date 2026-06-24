# ExECTv2 Component Ablation Contract

Date: 2026-06-24

Scope: final-consolidation Phase 4 defines the replay-only component-impact
contract for ExECTv2. This document is a planning and frontend payload contract,
not an authorization to run full-200 or holdout-facing row-level analysis.

## Claim Boundary

- Allowed now: dev140 replay-only aggregate layer ladders for the frozen v08
  control, v09 partial-hybrid simplification, DeepSeek v0.9.16 diagnostic, and
  Qwen v0.9.22 diagnostic runs, using already available source artifacts.
- Not allowed here: new model calls, post-run tuning from ablation failures, or
  hidden promotion of deterministic rescue layers into an LLM-only score line.
- No full-200 or holdout-facing row-level inspection is introduced by this
  contract.
- Any paper-facing audit beyond dev140 must be predeclared with split, scorer,
  stop rule, aggregate reporting surface, and row-inspection boundary.

## Fixed Component Boundaries

| Boundary | Component type id | Prediction-bearing? | Replay switch shape | Notes |
| --- | --- | --- | --- | --- |
| LLM producers | `llm_producer` | yes | compare raw/source-scored producer surfaces while preserving source artifacts and scorer | Covers focused Diagnosis, SeizureFrequency, Prescription, Investigations, and single-call producer lanes. |
| Deterministic dictionaries | `dictionary` | conditional | compare dictionary-normalized surface against evidence-valid/source-scored surfaces | Dictionary changes may alter CUI/CUIPhrase normalization; reports must state whether the change is benchmark-formatting or clinical meaning. |
| Semantic lenses | `semantic_lens` | yes | compare residual semantic additions against dictionary-normalized surfaces | Includes heading recovery, residual convention recovery, and any add/drop/replace lens that changes clinical facts. |
| Evidence validation | `evidence_validation` | no | compare evidence-valid surface against source-scored mentions | Must report invalid-evidence deltas separately from clinical F1 deltas. |
| Assembly / arbitration | `assembler` | yes | compare final assembly against the previous materialized mention surface | The replay must keep the same upstream candidate files and expose the aggregate layer transition. |
| Deterministic projection | `deterministic_projection` | no unless explicitly promoted | compare headline projection against final assembly | Separates meaning-preserving projection from prediction-bearing semantic add/drop/replace. |

The scorer is not an ablation boundary. It is the declared measurement surface.

## Replay Surfaces

The current replay ladder uses seven ordered surfaces for every architecture:

1. `raw_lane_candidates`
2. `source_scored`
3. `evidence_valid`
4. `dictionary_normalized`
5. `residual_semantic_added`
6. `final_assembly`
7. `headline_projection`

Layer configs are generated as:

```text
configs/exectv2/ablations/{candidate}__layer_{layer_id}.yaml
```

Required config fields:

```yaml
candidate: exectv2_holistic_finding_assembly_v08_dev140
split: dev140
scorer_view: layered_component_impact
source_artifacts:
  baseline_summary: experiments/...
  baseline_assembly: experiments/...
  aggregate_json: experiments/exectv2_component_ablation_replay_dev140_20260624.json
component_boundary: headline_projection
component_type: deterministic_projection
previous_surface: final_assembly
current_surface: headline_projection
row_inspection_policy: aggregate_only
allow_model_calls: false
allow_post_run_tuning: false
claim_boundary: dev140 replay-only aggregate component-impact ladder
```

The current required architecture set is v08, v09 partial hybrid, DeepSeek
v0.9.16, and Qwen v0.9.22. These are aggregate layer replays from saved summary
JSONs, not new one-off model runs.

## Frontend Payload Contract

Component Impact ingests an aggregate payload with this top-level shape:

```json
{
  "artifact_kind": "exectv2_component_ablation_set",
  "dataset": "exectv2",
  "generated_on": "2026-06-24",
  "row_inspection_policy": "aggregate_only",
  "allow_model_calls": false,
  "allow_post_run_tuning": false,
  "claim_boundary": "dev140 replay-only aggregate component-impact ladder",
  "provenance_policy": "format_only_projection_separated_from_semantic_add_drop_replace",
  "layers": [],
  "architectures": [],
  "ablations": []
}
```

Each architecture row contains:

```json
{
  "artifact_kind": "exectv2_component_architecture_ladder",
  "run_id": "exectv2_holistic_finding_assembly_v08_dev140",
  "label": "v08 dev140 control",
  "model": "openai/gpt-4.1-mini",
  "decision": "control",
  "architecture_family": "holistic_finding_assembly",
  "split": "dev140",
  "row_count": 140,
  "final_score": {},
  "layers": [],
  "layer_impacts": [],
  "source_artifacts": [],
  "claim_boundary": "dev140 replay-only aggregate component-impact ladder",
  "row_inspection_policy": "aggregate_only"
}
```

Each impact row contains:

```json
{
  "artifact_kind": "exectv2_component_layer_impact",
  "run_id": "exectv2_holistic_finding_assembly_v08_dev140",
  "layer_id": "headline_projection",
  "layer_label": "Headline projection",
  "component_type": "deterministic_projection",
  "previous_layer_id": "final_assembly",
  "overall_delta_from_previous": 0.0283,
  "family_deltas": {
    "Diagnosis": 0.0,
    "SeizureFrequency": 0.1239,
    "Prescription": 0.0,
    "Investigations": 0.0
  },
  "current_score": {},
  "previous_score": {},
  "claim_boundary": "dev140 replay-only aggregate component-impact ladder",
  "row_inspection_policy": "aggregate_only"
}
```

Frontend rules:

- Show architecture-by-layer ladders first, not reliability evidence.
- Do not label reliability evidence as component impact.
- Do not display an ExECTv2 component as causal impact unless
  `artifact_kind == "exectv2_component_ablation_set"` and the relevant
  `architectures`, `layers`, and `ablations` arrays are present.
- Keep deterministic projection visually distinct from LLM producers,
  dictionaries, semantic lenses, evidence validation, and assembly/arbitration.
- Keep the prior pairwise fields `baseline_run_id`, `ablated_run_id`,
  `component_boundary`, `overall_f1_delta`, and `transition_counts` reserved
  for future true one-component-off replay rows; the current artifact is a
  layer-ladder replay.

## Completion Gate

ExECTv2 Component Impact can remain in ablation mode when:

1. The four selected architecture ladders are generated from saved artifacts
   without model calls.
2. The aggregate payload exposes all seven layers and 28 layer-impact rows.
3. Tests confirm family-level deltas and static frontend parity.
4. The frontend reads the payload instead of inferring causal impact from
   reliability scorecard or cross-model comparison data.

## Generated Replay Artifacts

Generated on 2026-06-24:

- `experiments/exectv2_component_ablation_replay_dev140_20260624.json`
- `experiments/exectv2_component_ablation_replay_dev140_20260624.jsonl`
- `experiments/exectv2_component_ablation_replay_dev140_20260624.md`
- `frontend/public/mock-data/exectv2/component-ablation.json`
- `configs/exectv2/ablations/{candidate}__layer_{layer_id}.yaml`

The committed replay covers four architectures and seven layers, producing 28
aggregate component-impact rows:

| Architecture | Decision | Final F1 | Raw candidates | Dictionary | Final assembly | Headline projection |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `exectv2_holistic_finding_assembly_v08_dev140` | control | 0.9155 | 0.8328 | 0.8697 | 0.8872 | 0.9155 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | simplification | 0.9061 | 0.8231 | 0.8601 | 0.8778 | 0.9061 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | diagnostic | 0.9174 | 0.7498 | 0.8334 | 0.8728 | 0.9174 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | diagnostic | 0.9001 | 0.6406 | 0.7526 | 0.8567 | 0.9001 |

The most visible layer effects are dictionary normalization, residual semantic
additions, and headline projection:

| Architecture | Dictionary delta | Residual semantic delta | Headline projection delta |
| --- | ---: | ---: | ---: |
| v08 control | +0.0389 | +0.0175 | +0.0283 |
| v09 partial hybrid | +0.0390 | +0.0177 | +0.0283 |
| DeepSeek diagnostic | +0.0836 | +0.0394 | +0.0446 |
| Qwen diagnostic | +0.1120 | +0.1041 | +0.0434 |

No full-200 or holdout-facing row-level inspection was introduced.
