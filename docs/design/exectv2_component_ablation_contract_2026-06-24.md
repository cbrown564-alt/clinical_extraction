# ExECTv2 Component Ablation Contract

Date: 2026-06-24

Scope: final-consolidation Phase 4 defines the replay-only component-ablation
contract for ExECTv2. This document is a planning and frontend payload contract,
not an authorization to run full-200 or holdout-facing row-level analysis.

## Claim Boundary

- Allowed now: dev140 replay-only ablations for the frozen v08 control and v09
  partial-hybrid simplification, using already available source artifacts.
- Not allowed here: new model calls, post-run tuning from ablation failures, or
  hidden promotion of deterministic rescue layers into an LLM-only score line.
- No full-200 or holdout-facing row-level inspection is introduced by this
  contract.
- Any paper-facing audit beyond dev140 must be predeclared with split, scorer,
  stop rule, aggregate reporting surface, and row-inspection boundary.

## Fixed Component Boundaries

| Boundary | Component type id | Prediction-bearing? | Replay switch shape | Notes |
| --- | --- | --- | --- | --- |
| LLM producers | `llm_producer` | yes | disable one focused producer lane while preserving input letters and scorer | Covers focused Diagnosis, SeizureFrequency, Prescription, Investigations, and single-call producer lanes. |
| Deterministic dictionaries | `dictionary` | conditional | disable one dictionary or alias map while leaving source model outputs fixed | Dictionary changes may alter CUI/CUIPhrase normalization; reports must state whether the change is benchmark-formatting or clinical meaning. |
| Semantic lenses | `semantic_lens` | yes | disable one recovery/reconciler lens and replay assembly from the same upstream candidates | Includes heading recovery, residual convention recovery, and any add/drop/replace lens that changes clinical facts. |
| Evidence validation | `evidence_validation` | no | disable evidence-validity filtering or mark it observe-only | Must report invalid-evidence deltas separately from clinical F1 deltas. |
| Assembly / arbitration | `assembler` | yes | swap or disable union, merge, duplicate handling, or arbitration logic | The replay must keep the same upstream candidate files and expose transition counts. |
| Deterministic projection | `deterministic_projection` | no unless explicitly promoted | disable format-only projection or benchmark repair after model emission | Separates meaning-preserving projection from prediction-bearing semantic add/drop/replace. |

The scorer is not an ablation boundary. It is the declared measurement surface.

## Replay Surfaces

Initial replay configs should be shaped as:

```text
configs/exectv2/ablations/{candidate}__without_{component_boundary}.yaml
```

Required config fields:

```yaml
candidate: exectv2_holistic_finding_assembly_v08_dev140
split: dev140
scorer_view: clinical_recovery
source_artifacts:
  upstream_candidates: experiments/...
  baseline_assembly: experiments/...
component_boundary: deterministic_projection
disabled_components:
  - deterministic_residual_benchmark_repair
row_inspection_policy: aggregate_only
allow_model_calls: false
allow_post_run_tuning: false
```

The v08 and v09 controls are the first required candidates. DeepSeek and Qwen
diagnostic rows may be added only after the v08/v09 replay surface is stable.

## Frontend Payload Contract

Component Impact should ingest an aggregate payload with this shape:

```json
{
  "artifact_kind": "exectv2_component_ablation_summary",
  "dataset": "exectv2",
  "generated_on": "2026-06-24",
  "baseline_run_id": "exectv2_holistic_finding_assembly_v08_dev140",
  "ablated_run_id": "exectv2_holistic_finding_assembly_v08_dev140__without_deterministic_projection",
  "component_boundary": "deterministic_projection",
  "component_type": "deterministic_projection",
  "split": "dev140",
  "scorer_view": "clinical_recovery",
  "row_count": 140,
  "overall_f1_delta": -0.012,
  "family_deltas": {
    "Diagnosis": -0.010,
    "SeizureFrequency": -0.020,
    "Prescription": 0.000,
    "Investigations": 0.000
  },
  "transition_counts": {
    "correct_to_wrong": 0,
    "wrong_to_correct": 0,
    "unchanged_correct": 0,
    "unchanged_wrong": 0
  },
  "provenance_policy": "format_only_projection_separated_from_semantic_add_drop_replace",
  "source_artifacts": [],
  "claim_boundary": "dev140 replay-only aggregate component ablation"
}
```

Frontend rules:

- Show observed architecture deltas and provenance inventory until this payload
  exists.
- Do not label reliability evidence as component impact.
- Do not display an ExECTv2 component as causal impact unless
  `artifact_kind == "exectv2_component_ablation_summary"` and a baseline plus
  ablated run id are present.
- Keep deterministic projection visually distinct from LLM producers,
  dictionaries, semantic lenses, evidence validation, and assembly/arbitration.

## Completion Gate

ExECTv2 Component Impact can move from provenance-only to ablation mode when:

1. v08 and v09 replay configs exist for at least one boundary each.
2. The aggregate payload above is generated from saved artifacts without model
   calls.
3. Tests confirm family-level deltas and transition counts are populated.
4. The frontend reads the payload instead of inferring causal impact from
   reliability scorecard or cross-model comparison data.
