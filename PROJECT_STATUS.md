# Project Status

Last updated: 2026-06-20

## Active Objective

ExECTv2 Plan 11 targets exactly four indicators: `Diagnosis`,
`SeizureFrequency`, `Prescription`, and `Investigations`. The current objective
is attribution-clean clinical scoring, not headline F1 alone: report the
headline key with benchmark score, `Diagnosis.concept_negation`,
`SeizureFrequency.active_rate_fidelity`, and projection provenance.

The old "`>0.900` headline cleared" framing is retired. The headline key is a
redefined, lenient target surface, not a benchmark/paper-comparable result.

## Current Read

Exact v0.42 saved dev25 predictions scored headline `0.9487`, benchmark raw
`0.3675`, and benchmark after CUI `0.3816`; the headline-to-benchmark gap is
large and cannot support a benchmark claim.

The predeclared local-Qwen dev140 run now exists:
`experiments/exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.md`.
It used default-quarantined projection families, local `qwen3.6:35b`,
`num_ctx=16384`, and auto partial GPU offload (`num_gpu` unset). Gate summary:
1 call failure, 4 parse/schema failures, 21 evidence-invalid mentions dropped.

Dev140 default-quarantine readout: headline `0.7153`, benchmark `0.2339`,
`Diagnosis.concept_negation` `0.6693`, and
`SeizureFrequency.active_rate_fidelity` `0.2887`. Indicator headline F1:
Diagnosis `0.6693`, SeizureFrequency `0.5572`, Prescription `0.8214`,
Investigations `0.8615`. This is useful attribution data, not a promotion.

Same-raw dev140 family ablation:
`docs/experiments/exectv2/key_entities/exectv2_phase3_family_ablation_same_raw_dev140_qwen36_35b_20260620.md`.
`audit_all` moves benchmark only `0.2339 -> 0.2383`; every positive
single-family effect fires on exactly one dev140 letter. No quarantined family
returns to the default prediction pipeline.

Focused-lane component-evidence replay is complete:
`docs/experiments/exectv2/key_entities/exectv2_focused_lane_component_evidence_v01_dev140_20260620.md`.
The no-call harness combined frozen v0.42 P/I controls with focused Diagnosis
and SF lanes, emitted JSONL/JSON/MD artifacts, and passed the declared dev-only
gates. Headline target `0.8006`; benchmark raw/after-CUI `0.2968/0.3157`;
`Diagnosis.concept_negation` `0.7572`;
`SeizureFrequency.active_rate_fidelity` `0.3931`; P/I controls unchanged.
This promotes the focused-lane architecture only as dev140 component evidence,
not as a benchmark/full-200/test claim.

## Recent Context

- Projection-rule attribution sidecar:
  `docs/experiments/exectv2/key_entities/exectv2_projection_rule_attribution_sidecar_dev25_20260619.md`.
  Counts are same-row warning-family attribution, not isolated rule-disable
  ablations.
- One-letter v0.42 projection families are quarantined by default with explicit
  audit replay switches. Prediction diagnostics record effective switch state.
- Dev25 same-raw ablation:
  `docs/experiments/exectv2/key_entities/exectv2_phase2_family_ablation_same_raw_dev25_20260620.md`.
- SF v0.8 hard-slice gate was rejected for prediction-bearing implementation;
  retain diagnostic-only:
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_v08_hard_slice_gate_decision_2026-06-19.md`.

## Active Priorities

1. Do not restore quarantined projection families by default on single-letter
   benchmark nudges.
2. Treat v0.21-v0.42 "cleared four" artifacts as qualified dev evidence on a
   lenient key, not benchmark claims.
3. Use same-raw ablations and fidelity companions before adding, cutting, or
   promoting deterministic repair families.
4. Any full-200 or locked-test-facing ExECTv2 audit still needs
   benchmark-beating dev evidence and a predeclared aggregate readout.

## Work Board

### Now

- Write the focused-lane promotion boundary/addendum before any broader audit:
  what is promoted (`hybrid_diagnosis_route` + `hybrid_sf_route` with v0.42
  P/I controls), what remains dev-only, and what aggregate/full-200 protocol
  would be required next.

### Next

- If moving beyond dev140, predeclare the exact aggregate/full-200 readout,
  scorer surfaces, runtime/model, stop rule, and no-test-inspection boundary.
- If another live dev140 experiment is proposed, predeclare the exact
  comparison, runtime, scorer surfaces, and stop rule before spending calls.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- New ExECTv2 full-200 audits need benchmark-beating dev evidence and a
  predeclared aggregate readout.

### Done Recently

- 2026-06-20: Built and ran the no-call focused-lane component-evidence
  replay/report harness. It aligns frozen dev140 rows, preserves lane
  provenance, emits JSONL/JSON/MD artifacts, reports the declared score ladder
  and changed-row accounting, and passes the dev-only promotion gates.
- 2026-06-20: Predeclared the focused-lane component-evidence comparison:
  frozen v0.42 P/I controls, focused Diagnosis and SF sources, score ladder,
  P/I regression controls, Diagnosis/SF fidelity gates, and stop rule. No live
  calls authorized until the no-call replay/report harness exists.
- 2026-06-20: Completed the dev140 error-led architecture decision. Result:
  projection promotion stays rejected; next live work must be a predeclared
  focused-lane component-evidence comparison with P/I controls, Diagnosis
  hierarchy reconciliation, and SF span/state adjudication.
- 2026-06-20: Predeclared and ran the exact v0.42 local-Qwen dev140
  default-quarantine condition, then ran same-raw family ablation on the saved
  raw output. Result: no projection-family promotion; all risky families stay
  quarantined/audit-only.
- 2026-06-20: Made `scripts/phase2_family_ablation.py` source/output
  configurable while preserving the dev25 ablation artifact.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Keep claims attribution-clean across `rules_only`, `llm_first`, and `hybrid`.
  Deterministic certainty/CUI/format repairs are controlled projection layers.
- Do not add more letter-specific projection patches without attribution
  ablation, portability category, and focused tests.
