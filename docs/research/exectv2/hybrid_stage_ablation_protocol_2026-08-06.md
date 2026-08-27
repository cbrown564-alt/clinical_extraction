# Protocol: ExECTv2 llm_with_rules stage ablation

Date: 2026-08-06  
Status: complete; no-call development stage ablation  
Parent: [family error catalog](family_error_catalog_2026-08-06.md)  
Peer: [Gan hybrid stage ablation protocol](../gan2026/hybrid_stage_ablation_protocol_2026-08-06.md)  
Report: [hybrid stage ablation](hybrid_stage_ablation_2026-08-06.md)

## Primary question

Inside retained `llm_with_rules` only (not llm vs hybrid), which observable
pipeline bands and named deterministic stages erase, reshape, or amplify
per-family letter error modes on `dev140`, and which stage is the
**first unit-key changer** on rescued or damaged letters for each clinical
family?

## Why it matters

The [family error catalog](family_error_catalog_2026-08-06.md) treats
family rules as one blob between `raw_lane_mentions` and
`predicted_mentions`. Architecture manifests name ordered clinical stages with
asymmetric family ownership ([Decision 0040](../../decisions/0040-final-exect-llm-with-rules-family-ownership.md)).
Without a band + first-changer reading under **true ordered replay**, hybrid
talk cannot say which stages earn their keep, which create Prescription harm,
or whether Seizure Frequency credit belongs to projection/suppression rather
than the thin SF lens.

## Scope

| Item | Value |
| --- | --- |
| Split | ExECT `dev140`; development inspection permitted |
| Surface | `llm_with_rules` only (six retained single-call structured + SF sidecars) |
| Policy | `StructuredMethodConfig.selected()`: Diagnosis/Prescription `default` / `default`, SF projection ablation `combined` ([0045](../../decisions/0045-exect-default-policy-not-joint-combined.md)) |
| Baseline | earliest replayable saved model surface: `*_structured.jsonl` `structured_events` (or re-parse saved `raw_output` when needed for fidelity), **not** the post-lens `predicted_mentions` |
| Replay mode | **true ordered no-call replay** through current deterministic functions; not provenance reconstruction alone |
| Bands | post-flatten → producer gate → SF clinical → Diagnosis lens → Prescription lens → Investigations lens → evidence gate |
| Stages | `flatten_events` → `project_and_gate` → `sf_state_projection` → `sf_unknown_suppression` → `lens.diagnosis` → `lens.seizure_frequency` → `lens.prescription` → `lens.investigations` → `evidence_requirement` |
| Letter metric | clinical-headline unit-key multiset exactness **per family** (same modes as parent catalog) |
| Competence metric | four-family clinical fact F1 remains Decision 0046; this study does not rewrite primary fills |
| Calls | none |
| Holdout | sealed (`test60` forbidden) |

### Band map

| Band | Stages | Notes |
| --- | --- | --- |
| Post-flatten | `flatten_events` | Model events as mentions before project/gate |
| Producer gate | `project_and_gate` | Attribute enrich + drop no-state SF / modality-only Inv duplicates; mass SF first-changer on this roster |
| SF clinical | `sf_state_projection`, `sf_unknown_suppression` | Further SF clinical work; do **not** credit `lens.seizure_frequency` for this band |
| Diagnosis lens | `lens.diagnosis` | May rewrite, drop, or add concepts under `default` |
| Prescription lens | `lens.prescription` | Bounded regimen correction; known hurt surface |
| Investigations lens | `lens.investigations` | Expect near no-op on this roster |
| Evidence gate | `evidence_requirement` | Hard gate / failure outcome; not a silent drop. Pre-gate quote repair stays a separate six-model story |

Transport (`parse_and_retry`) may appear as a short fidelity appendix when
re-parsing `raw_output`; it is not a primary clinical band.

## Method

1. For each of the six retained models, load the `dev140`
   `*_structured.jsonl` sidecar (and letter gold). Prefer
   `structured_events` as the replay start; re-parse `raw_output` only when
   needed to exercise parse fidelity.
2. Replay in manifest order with **current** selected-policy functions:
   flatten → `to_predicted_letter` / project_and_gate →
   `sf_state_projection.project_row` (`combined`) →
   `sf_unknown_suppression.suppress_row` → register findings →
   Diagnosis / SeizureFrequency / Prescription / Investigations lenses →
   evidence requirement. Record per-family clinical-headline unit keys after
   each prediction-bearing stage.
3. Score letter-exactness and parent-catalog error modes at **band endpoints**,
   stratified by family. Attribute each unit-key-changing hop to its stage;
   credit **first-changer** for rescue (wrong→exact) and harm (exact→wrong)
   per family.
4. Aggregate pooled six-model band mode deltas and stage ledgers **by family**;
   keep up to two development examples per high-volume pathway / stage effect
   (prefer consensus + Sol; saved mention texts only; no full notes).
5. Report fidelity: agreement of replayed finals with retained hybrid
   `predicted_mentions` / parent-catalog `llm_with_rules` surfaces, and note
   any stage that cannot be isolated without instrumentation change (stop as
   blocked rather than silent provenance fallback).
6. Emit one machine-readable artifact and one band + first-changer narrative
   report (sibling to the parent catalog; peer shape to the Gan hybrid stage
   ablation).

## Stop rule

Answer when every family has band-level mode counts, every named clinical
stage has fire / first-changer / help / hurt counts on `dev140`, signature
pathway vignettes cover Diagnosis rescue, SF precision/residual, Prescription
harm, and Investigations no-op (or document a fidelity block), and replay
fidelity is stated in the claim boundary.

## Claim boundary

Development stage ablation inside `llm_with_rules` on `dev140` under true
ordered no-call replay of the selected `default` / `default` policy.
First-changer attribution under ordered replay; not a leave-one-stage-out
factorial. Not a replacement for the parent llm-vs-hybrid catalog scores.
Not holdout competence. Not a Decision 0046 rewrite. Do not transfer Gan
Purist stage credit or band names. Do not treat post-rules exact-evidence
rates near `1.00` as model-quality evidence.
