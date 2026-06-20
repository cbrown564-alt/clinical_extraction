# ExECTv2 Focused-Lane Component-Evidence Predeclaration

Date: 2026-06-20

## Decision

Run the next ExECTv2 architecture comparison as a frozen dev140
component-evidence replay, not as another broad prompt revision. The comparison
will preserve the strongest current Prescription and Investigations control
lanes, then test focused Diagnosis hierarchy reconciliation and
SeizureFrequency span/state adjudication with explicit component ownership.

No additional live model calls are authorized by this predeclaration until a
no-call replay/scoring harness can combine the declared JSONL sources and emit
the full score ladder below. If a fresh focused lane is later needed, it must
receive its own addendum with exact command, model, runtime, artifact paths, and
stop rule before calls start.

## Frozen Sources

Same-source row set:

- Split: `dev`
- Rows: first 140 development letters from
  `data/ExECTv2 (2025)/splits/exectv2_split_v1.json`
- Locked surfaces: no `test` split, no full-200 audit, no locked-test row-level
  inspection

Primary control source:

- v0.42 default-quarantine local-Qwen dev140:
  `experiments/exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl`

Focused-route comparators and candidate lanes:

- Diagnosis focused route:
  `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl`
- Diagnosis candidate inputs, if a replay harness needs decomposition
  provenance:
  `experiments/exectv2_llm_diagnosis_verifier_v06_dev140_gpt41mini_20260618.jsonl`,
  `experiments/exectv2_hybrid_diagnosis_decomposer_v01_dev140_gpt41mini_20260618.jsonl`
- SeizureFrequency focused route:
  `experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl`
- SeizureFrequency candidate span/state adjudicator lineage:
  `experiments/exectv2_hybrid_sf_state_adjudicator_v05_dev140_gpt41mini_20260618.jsonl`,
  `experiments/exectv2_hybrid_sf_state_projection_v06_combined_dev140_20260618.jsonl`

Existing no-call routed comparator:

- `experiments/exectv2_family_routed_with_focused_diagnosis_route_dev140_gpt41mini_20260618.jsonl`
- `experiments/exectv2_family_routed_with_focused_diagnosis_route_dev140_gpt41mini_20260618.json`
- Report:
  `docs/experiments/exectv2/key_entities/exectv2_focused_diagnosis_route_no_call_replay_2026-06-18.md`

Baseline comparators:

- v0.42 default-quarantine single-call report:
  `experiments/exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.md`
- deterministic_all9 and earlier route report:
  `docs/experiments/exectv2/key_entities/exectv2_adr0030_target_indicator_report_20260619.md`
- Same-raw projection-family ablation:
  `docs/experiments/exectv2/key_entities/exectv2_phase3_family_ablation_same_raw_dev140_qwen36_35b_20260620.md`

## Candidate Construction

The replay candidate is `focused_lane_component_evidence_v01_dev140`:

- Prescription: take the v0.42 default-quarantine local-Qwen lane unchanged.
  This preserves the current control score, `0.8214`, and its effective
  projection-switch diagnostics.
- Investigations: take the v0.42 default-quarantine local-Qwen lane unchanged.
  This preserves the current control score, `0.8615`, and its effective
  projection-switch diagnostics.
- Diagnosis: take the focused Diagnosis reconciler v0.1 lane, not the broad
  v0.42 Diagnosis output. This tests heading decomposition plus narrative
  seizure-type collection and reconciliation, with negation-aware scoring.
- SeizureFrequency: take the focused SF v0.7 lane, not the broad v0.42 SF
  output. This tests candidate-span/state adjudication plus explicit
  active-rate, seizure-free, unknown, and reject accounting.

The replay harness must align rows by `letter_id`, retain per-source provenance
for every emitted mention, and fail closed if any source is missing a dev140 row
or emits a row that cannot be tied to exact source text.

## Component Ownership

| Lane | Prediction-bearing source | Deterministic layers allowed | Ownership label |
| --- | --- | --- | --- |
| Prescription | v0.42 local-Qwen single-call | evidence validation, schema repair, CUI/projection scoring only | `llm_first_control` |
| Investigations | v0.42 local-Qwen single-call | evidence validation, schema repair, CUI/projection scoring only | `llm_first_control` |
| Diagnosis | focused diagnosis reconciler v0.1 | candidate alignment, evidence validation, benchmark/CUI projection | `hybrid_diagnosis_route` |
| SeizureFrequency | focused SF v0.7 route | state projection, unknown suppression, benchmark/CUI projection | `hybrid_sf_route` |

Any deterministic step that adds, drops, or semantically replaces a clinical
mention must be named in the output and counted as prediction-bearing hybrid
behavior. Format repair, JSON/schema validation, evidence-substring validation,
and benchmark rendering are not allowed to hide semantic replacement.

## Score Ladder

The comparison report must include every surface below:

- Raw lane score before evidence-invalid drops, overall and by indicator.
- Evidence-valid scored output, overall and by indicator.
- CUI/projection companion score, overall and by indicator.
- Headline target F1, overall and by indicator.
- Benchmark raw and benchmark after CUI/projection.
- `Diagnosis.concept_negation`.
- `SeizureFrequency.active_rate_fidelity`.
- Parse/schema failures, call failures, evidence-invalid dropped mentions, and
  exact-evidence rate by lane.
- Changed-row accounting for Diagnosis and SF versus v0.42 default-quarantine
  and versus the existing focused-route comparator.

Headline F1 alone is not a promotion signal.

## Gates

Prescription and Investigations controls:

- No absolute headline F1 regression greater than `0.01` versus the frozen
  v0.42 control lane.
- Any P/I changed row must list source lane, old mention, new mention, evidence,
  and whether the change came from model output or deterministic projection.

Diagnosis:

- Must beat the v0.42 default-quarantine Diagnosis headline `0.6693`.
- Must beat or tie the existing focused-route Diagnosis comparator `0.7127`
  while improving or preserving `Diagnosis.concept_negation`.
- Changed-row accounting must separate hierarchy reconciliation, assertion or
  negation change, duplicate collapse, and projection-only effects.

SeizureFrequency:

- Must beat the v0.42 default-quarantine SeizureFrequency headline `0.5572`.
- Must beat or tie the existing focused-route SF comparator `0.6321`.
- Must improve or preserve `SeizureFrequency.active_rate_fidelity` versus the
  v0.42 default-quarantine value `0.2887`.
- Changed-row accounting must separate active-rate, seizure-free, unknown,
  reject/drop, generic-vs-specific ownership, and projection-only effects.

Aggregate:

- Benchmark movement must be reported, but cannot promote a component if the
  corresponding fidelity companion regresses.
- Single-letter or projection-only wins are diagnostic unless they survive
  changed-row review and portability labeling.
- Quarantined projection families remain disabled by default unless a separate
  same-raw ablation clears the attribution criteria.

## Stop Rule

Promote the focused-lane architecture only if Diagnosis and SeizureFrequency
both clear their declared gates and Prescription/Investigations stay within the
control regression bounds. If either focused lane fails, do not run another
broad dev140 prompt under this predeclaration. Revise the failing lane or add
instrumentation, then write a new predeclaration or addendum before spending
calls.

If the replay harness finds missing rows, malformed source records, or
untraceable evidence, record the run as blocked/invalid rather than patching
artifacts after the fact.

## Required Implementation Before Run

Build a no-call component replay/report harness that can:

- read the frozen lane JSONL sources above;
- align dev140 rows by `letter_id`;
- select lane-specific mentions into one prediction artifact;
- preserve source artifact, source lane, model/runtime, and deterministic
  projection provenance per mention;
- emit JSON/JSONL plus a markdown report with the score ladder and gates above.

The expected output paths are:

- `experiments/exectv2_focused_lane_component_evidence_v01_dev140_20260620.jsonl`
- `experiments/exectv2_focused_lane_component_evidence_v01_dev140_20260620.json`
- `docs/experiments/exectv2/key_entities/exectv2_focused_lane_component_evidence_v01_dev140_20260620.md`

## Claim Language

This is dev-only architecture evidence. Even if the gates clear, the permitted
claim is limited to:

> On dev140, a component-attributed focused-lane replay improved the declared
> Diagnosis and SeizureFrequency fidelity surfaces while preserving
> Prescription/Investigations controls.

It does not authorize a benchmark claim, full-200 audit, or locked-test-facing
analysis without a separate predeclared aggregate readout.
