# Project Status

Last updated: 2026-06-19

## Active Objective

ExECTv2 Plan 11 targets exactly four indicators: `Diagnosis`,
`SeizureFrequency`, `Prescription`, and `Investigations`, via a hybrid pipeline:
one LLM call per letter for candidate generation/selection, followed by
deterministic normalization and projection with explicit attribution.

The old "`>0.900` headline cleared" framing is retired as a success criterion.
Phase 0 showed that the headline key is a redefined, lenient target surface, not
a benchmark/paper-comparable result. The current objective is a clinically
faithful per-indicator scorer: headline plus fidelity companions
(`Diagnosis` `concept_negation`, `SeizureFrequency` `active_rate_fidelity`),
judged for generalization and attribution rather than headline F1 alone.

## Current Read

Phase 0 dual scoring on the exact v0.42 saved dev25 predictions:

| Surface | Overall F1 | Interpretation |
| --- | ---: | --- |
| Headline key | 0.9487 | Lenient redefined target surface. |
| Benchmark key, raw | 0.3675 | Paper-comparable key, near established ceiling. |
| Benchmark key, after CUI projection | 0.3816 | CUI projection recovers only +0.0141. |

Per-indicator headline-to-benchmark gaps from Phase 0:

| Indicator | Headline | Benchmark | Gap |
| --- | ---: | ---: | ---: |
| Diagnosis | 0.9376 | 0.2857 | +0.6519 |
| SeizureFrequency | 0.9811 | 0.6885 | +0.2926 |
| Prescription | 0.9250 | 0.1205 | +0.8045 |
| Investigations | 0.9756 | 0.5854 | +0.3902 |

Phase 1 no-call generalization check:
`docs/experiments/exectv2/key_entities/exectv2_phase1_dual_scoring_generalization_report_20260619.md`.
No exact v0.42 local-Qwen dev140 single-call replay artifact exists. Existing
dev140 target comparators are the safest held-out development warning signal:
best headline overall is `0.7301` (`deterministic_all9`) and best focused routed
hybrid headline is `0.7081`; benchmark-after-CUI is `0.3540` for deterministic
and `0.2316` for focused routed hybrid. Only Prescription clears `>0.900` on
existing dev140 target artifacts.

Conclusion: reject the v0.42 headline generalization claim as currently
supported. v0.42 remains a dev25 no-call projection artifact on a lenient
headline key.

## Recent Context

- 2026-06-19: Coordinated three parallel Codex workstreams and integrated the
  useful outputs back into this checkout.
- Phase 1 dual scoring/generalization report rejects promotion of the dev25
  v0.42 headline result; no live dev140 calls were run.
- SF v0.8 hard-slice gate decision:
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_v08_hard_slice_gate_decision_2026-06-19.md`.
  No bucket/action class clears the predeclared attribution,
  non-gold-feature, and stop-rule gates. Stop v0.8 as diagnostic-only; no SF
  prediction rule is authorized.
- Projection-family overfit audit:
  `docs/experiments/exectv2/key_entities/exectv2_phase2_projection_family_overfit_audit_20260619.md`.
  Saved `gate_warnings` show many broad normalization families, but several
  v0.42-added projection families fire on one dev25 letter each and should be
  quarantined until ablated.
- Two clinical-fidelity companions are wired into the scorer and target report:
  Diagnosis `concept_negation` and SeizureFrequency `active_rate_fidelity`.
  On the v0.42 dev25 replay, Diagnosis `concept_negation` is `0.9376`; SF
  `active_rate_fidelity` is `0.7879` versus headline `0.9630`, a gap of about
  `0.18`.
- Local `ollama_chat/qwen3.6:35b` is installed and usable only CPU-side on this
  laptop (`CLINICAL_EXTRACTION_OLLAMA_NUM_GPU=0`,
  `CLINICAL_EXTRACTION_OLLAMA_NUM_CTX=16384`) because GPU loading OOMs on the
  8 GB RTX 4070 Laptop GPU.

## Active Priorities

1. Do not resume projection-rule optimization on the headline key until
   attribution and generalization are explicit.
2. Treat all v0.21-v0.42 "cleared four" artifacts as qualified dev evidence on a
   lenient key, not benchmark claims.
3. Build projection-rule attribution before adding, cutting, or promoting more
   deterministic repair families.
4. Any future exact v0.42 dev140 local-Qwen run must be predeclared with cost,
   purpose, model/runtime settings, scorer surfaces, and stop rule. It is not a
   silent promotion gate.

## Work Board

### Now

- Build a projection-rule registry/attribution sidecar for v0.39-v0.42 target
  projection families. At minimum record rule id, entity, portability category,
  enabled switch, changed rows, wrong-to-correct and correct-to-wrong counts,
  and effects on `concept_negation` / `active_rate_fidelity`.
- Quarantine one-letter v0.42 projection families before any promotion claim:
  remote-last-seizure state, controlled-state from Diagnosis context, frequent
  myoclonic-jerk projection, infrequent-context state, and phrase-specific
  `last clinic`/date repairs. Decide keep/cut via same-raw ablation, not new
  headline tuning.
- Decide whether an exact v0.42 dev140 local-Qwen single-call run is worth the
  spend. If yes, write the predeclaration first; if no, keep existing dev140
  comparators as the warning signal.

### Next

- Add explicit rule-family switches or an audit-only replay path so projection
  families can be ablated without editing prediction behavior.
- If a dev140 run is predeclared, run with local Qwen CPU settings
  (`num_gpu=0`, `num_ctx=16384`) and report both headline and benchmark keys
  plus clinical-fidelity companions.
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

- 2026-06-19: Phase 1 no-call dual scoring/generalization report completed; no
  exact v0.42 dev140 artifact exists, and existing dev140 target comparators do
  not support the dev25 headline generalization claim.
- 2026-06-19: SF v0.8 hard-slice gate rejected for prediction-bearing
  implementation; retain as diagnostic-only.
- 2026-06-19: Projection-family warning audit completed from saved
  `gate_warnings`; one-letter v0.42 projection families flagged for quarantine.
- 2026-06-19: Phase 0 metric reconciliation retired the `>0.900` headline claim
  as benchmark-comparable evidence.
- 2026-06-19: Clinical-fidelity companions added to scorer/reporting.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence, selected
  events, or transitions for development.
- Keep claims attribution-clean across `rules_only`, `llm_first`, and `hybrid`.
  Deterministic certainty/CUI/format repairs are controlled projection layers.
- Do not add more letter-specific projection patches without an attribution
  ablation and explicit portability category.
