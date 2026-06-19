# Project Status

Last updated: 2026-06-19

## Active Objective

ExECTv2 Plan 11 targets exactly four indicators: `Diagnosis`,
`SeizureFrequency`, `Prescription`, and `Investigations`. The current objective
is attribution-clean clinical scoring, not headline F1 alone: headline key plus
fidelity companions (`Diagnosis.concept_negation`,
`SeizureFrequency.active_rate_fidelity`) and explicit projection provenance.

The old "`>0.900` headline cleared" framing is retired as a success criterion.
Phase 0 showed that the headline key is a redefined, lenient target surface, not
a benchmark/paper-comparable result.

## Current Read

Phase 0 dual scoring on exact v0.42 saved dev25 predictions: headline `0.9487`,
benchmark raw `0.3675`, benchmark after CUI `0.3816`. Per-indicator
headline-to-benchmark gaps are large: Diagnosis `+0.6519`, SeizureFrequency
`+0.2926`, Prescription `+0.8045`, Investigations `+0.3902`.

Phase 1 no-call generalization report:
`docs/experiments/exectv2/key_entities/exectv2_phase1_dual_scoring_generalization_report_20260619.md`.
No exact v0.42 local-Qwen dev140 artifact exists. Existing dev140 target
comparators remain the held-out warning signal: best headline overall `0.7301`
(`deterministic_all9`), best focused routed hybrid headline `0.7081`,
benchmark-after-CUI `0.3540` deterministic / `0.2316` focused routed hybrid,
and only Prescription clears `>0.900`.

Conclusion: reject the v0.42 headline generalization claim as currently
supported. The exact v0.42 dev140 local-Qwen run is no-go/deferred until
same-raw projection attribution exists:
`docs/experiments/exectv2/key_entities/exectv2_v042_dev140_local_qwen_run_decision_20260619.md`.

## Recent Context

- Projection-rule attribution sidecar:
  `docs/experiments/exectv2/key_entities/exectv2_projection_rule_attribution_sidecar_dev25_20260619.md`.
  It summarizes saved v0.39-v0.42 dev25 `gate_warnings`, portability category,
  changed rows, correction/regression counts, and fidelity effects. Counts are
  same-row warning-family attribution, not isolated rule-disable ablations.
- One-letter v0.42 projection families are quarantined by default with explicit
  audit replay switches for same-raw ablation. This covers remote-last-seizure
  state, controlled-state from Diagnosis context, frequent myoclonic jerks,
  infrequent-context state, phrase-specific `last clinic` repairs, and
  Christmas/date projection.
- Projection-family overfit audit:
  `docs/experiments/exectv2/key_entities/exectv2_phase2_projection_family_overfit_audit_20260619.md`.
- SF v0.8 hard-slice gate:
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_v08_hard_slice_gate_decision_2026-06-19.md`.
  Rejected for prediction-bearing implementation; retain diagnostic-only.
- Local `ollama_chat/qwen3.6:35b` is usable CPU-side only on this laptop
  (`num_gpu=0`, `num_ctx=16384`); GPU loading OOMs on the 8 GB RTX 4070.

## Active Priorities

1. Do not resume projection-rule optimization on the headline key until
   attribution and generalization are explicit.
2. Treat all v0.21-v0.42 "cleared four" artifacts as qualified dev evidence on
   a lenient key, not benchmark claims.
3. Use the projection-rule attribution sidecar and audit replay switches before
   adding, cutting, or promoting deterministic repair families.
4. Any future exact v0.42 dev140 local-Qwen run must be predeclared with cost,
   purpose, runtime settings, scorer surfaces, and stop rule.

## Work Board

### Now

- Build a same-raw ablation replay for the quarantined v0.42 projection
  families, comparing default quarantine versus `audit_only_projection_replay`
  on saved dev25 raw outputs. Report keep/cut decisions by rule family using
  headline, benchmark, `Diagnosis.concept_negation`, and
  `SeizureFrequency.active_rate_fidelity`; do not run new LLM calls.

### Next

- Reconsider the exact v0.42 dev140 local-Qwen run only after the same-raw
  ablation replay identifies which projection families are portable enough to
  keep. If predeclared then, run with local Qwen CPU settings (`num_gpu=0`,
  `num_ctx=16384`) and report headline, benchmark, `concept_negation`, and
  `active_rate_fidelity`.
- Revisit the clinical target definition after attribution: Prescription and
  Investigations may be clinically better represented by the headline key,
  while SeizureFrequency needs active-rate fidelity and Diagnosis needs
  negation-aware validation.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- New ExECTv2 full-200 audits need benchmark-beating GPT-first dev evidence and
  a predeclared aggregate readout.

### Done Recently

- 2026-06-19: Coordinated three parallel Codex workstreams and integrated the
  useful outputs back into this checkout.
- 2026-06-19: Projection-rule registry/attribution sidecar added and generated
  from saved v0.39-v0.42 dev25 target artifacts.
- 2026-06-19: Quarantined one-letter v0.42 projection families by default and
  added explicit audit replay switches.
- 2026-06-19: Exact v0.42 dev140 local-Qwen run decision completed; no-go/defer
  until attribution.
- 2026-06-19: Phase 1 generalization, Phase 0 metric reconciliation, SF v0.8
  gate, and projection-family warning audit completed.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Keep claims attribution-clean across `rules_only`, `llm_first`, and `hybrid`.
  Deterministic certainty/CUI/format repairs are controlled projection layers.
- Do not add more letter-specific projection patches without an attribution
  ablation and explicit portability category.
