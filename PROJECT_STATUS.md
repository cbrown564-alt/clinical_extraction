# Project Status

Last updated: 2026-06-21

## Active Objective

ExECTv2 Plan 11 targets exactly four indicators: `Diagnosis`,
`SeizureFrequency`, `Prescription`, and `Investigations`. The current objective
is attribution-clean clinical scoring and architecture clarity: report the
headline key with benchmark score, `Diagnosis.concept_negation`,
`SeizureFrequency.active_rate_fidelity`, projection provenance, and the finding
assembly source/lens/view path.

The old "`>0.900` headline cleared" framing is retired. The headline key is a
redefined, lenient target surface, not a benchmark/paper-comparable result.

## Current Read

Dev140 v0.42 default-quarantine local-Qwen baseline:
`experiments/exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.md`.
Headline `0.7153`, benchmark `0.2339`,
`Diagnosis.concept_negation` `0.6693`,
`SeizureFrequency.active_rate_fidelity` `0.2887`; indicator headline F1:
Diagnosis `0.6693`, SeizureFrequency `0.5572`, Prescription `0.8214`,
Investigations `0.8615`.

Focused-lane component-evidence replay:
`docs/experiments/exectv2/key_entities/exectv2_focused_lane_component_evidence_v01_dev140_20260620.md`.
The no-call harness combined frozen v0.42 P/I controls with focused Diagnosis
and SF lanes. Headline target `0.8006`; benchmark raw/after-CUI
`0.2968/0.3157`; `Diagnosis.concept_negation` `0.7572`;
`SeizureFrequency.active_rate_fidelity` `0.3931`; P/I controls unchanged.

Holistic finding-assembly replay is complete:
`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v01_dev140_20260621.md`.
It reproduces the focused-lane score ladder from the same frozen source
artifacts while expressing the system as a clinical finding store, entity
lenses, explicit scoring views, and row-level provenance. This is dev-only
component evidence and architecture cleanup, not a benchmark/full-200/test
claim.

## Active Priorities

1. Keep claims attribution-clean across `rules_only`, `llm_first`, and
   `hybrid`; semantic deterministic lens behavior is prediction-bearing.
2. Do not restore quarantined projection families by default on single-letter
   benchmark nudges.
3. Treat v0.21-v0.42 "cleared four" artifacts as qualified dev evidence on a
   lenient key, not benchmark claims.
4. Any full-200 or locked-test-facing ExECTv2 audit still needs
   benchmark-beating dev evidence and a predeclared aggregate readout.

## Work Board

### Now

- Decide whether the next ExECTv2 step is optional behavior-preserving logic
  consolidation into lenses or a predeclared broader audit protocol. Do not
  spend live calls or inspect holdout rows without a written protocol.

### Next

- If moving beyond dev140, predeclare the exact aggregate/full-200 readout,
  scorer surfaces, runtime/model, stop rule, and no-test-inspection boundary.
- If consolidating logic into reusable lenses, require same-source before/after
  output comparison, portability categories, and provenance for each moved
  semantic action.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- New ExECTv2 full-200 audits need benchmark-beating dev evidence and a
  predeclared aggregate readout.

### Done Recently

- 2026-06-21: Completed the ExECTv2 holistic clinical finding assembly refactor:
  added the `assembly/` layer, manifest parser, saved JSONL producers, thin
  entity lenses, scoring views, focused-report wrapper, holistic manifest, ADR
  0032, and dev140 structural replay report. The replay reproduces headline
  `0.8006` with the same four indicator scores and no live calls.
- 2026-06-20: Built and ran the no-call focused-lane component-evidence
  replay/report harness. It aligns frozen dev140 rows, preserves lane
  provenance, emits JSONL/JSON/MD artifacts, reports the declared score ladder
  and changed-row accounting, and passes the dev-only promotion gates.
- 2026-06-20: Completed the v0.42 local-Qwen dev140 default-quarantine run and
  same-raw family ablation; no quarantined projection family returned to the
  default prediction pipeline.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development
  without explicit authorization and a frozen protocol.
- Keep deterministic certainty/CUI/format repairs as controlled projection
  layers, and record semantic add/drop/replace/select actions as
  prediction-bearing provenance.
