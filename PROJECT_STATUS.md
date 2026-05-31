# Project Status

Last updated: 2026-05-31

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can exceed 0.9 Purist F1 on development surfaces while preserving enough structure to support future clinical extraction tasks.

The current research aim is a paper-quality hybrid deterministic-LLM system with transparent evidence trails, component-level ablations, and conservative benchmark claims.

## Current Strategy

Use the Gan 2026 task as the first controlled extraction surface. Keep data loading, label normalization, scoring, split discipline, and deterministic-rule behavior explicit before optimizing LLM or DSPy components.

Treat deterministic rules as a frozen, ablatable comparator rather than an endlessly expanding solution. Future gains should come from validation-only reasoning experiments, better candidate adjudication, and documented rule/category effects.

## Recent Context

- The project skeleton, Gan 2026 task module, docs, runbook, split protocol, and local `.venv` are in place.
- Gan-compatible loading and scoring are reproduced for all 1,500 local rows, including gold-label parsing, monthly scorer values, semantic label records, quality flags, and author-style prediction-label repair.
- The locked split manifest is `data/Gan (2026)/splits/gan2026_split_v1.json`: 300 train rows, 750 validation rows, and 450 final holdout rows. Development should stay on train/validation.
- Deterministic V1 is implemented in `gan2026.pipeline_v1` with candidate events, normalized events, final-selection diagnostics, and exact selected-evidence validation.
- V1 was validation-saturated through hand-rule work, then frozen. The best recorded saturated validation artifact reports 0.9280 Purist micro F1/accuracy on 750 validation rows with 750/750 exact selected-evidence validity.
- V1 was evaluated once on the locked test split without inspecting test-row failures: 0.7600 Purist micro F1/accuracy, 0.7867 Pragmatic micro F1/accuracy, and 450/450 exact selected-evidence validity. This indicates substantial validation-surface overfit.
- The deterministic-rule catalogue now exposes rule metadata, portability categories, selected-candidate diagnostics, group/rule-ID ablations, temporal-selection ablations, and traceable benchmark-repair steps.
- The latest validation-only deterministic ablation report records the current working-tree baseline as 0.9120 Purist micro F1/accuracy and 0.9213 Pragmatic micro F1/accuracy with 750/750 exact evidence validity. The 0.9280 versus 0.9120 drift must be resolved before paper-facing performance claims.

## Key References

- Split protocol: `docs/design/gan2026_split_protocol.md`
- Model strategy: `docs/design/model_strategy.md`
- Deterministic rule review: `docs/research/gan2026_deterministic_rule_review_2026-05-31.md`
- Rule-catalogue change report: `docs/research/deterministic_rule_catalogue_change_report_2026-05-31.md`
- Validation ablation interpretation: `docs/research/gan2026_validation_ablation_interpretation_2026-05-31.md`
- Saturated validation analysis: `experiments/gan2026_v1_validation_error_analysis_2026-05-31.md`
- Frozen test holdout: `experiments/gan2026_v1_test_holdout_2026-05-31.md`
- Validation ablation report: `experiments/gan2026_v1_validation_ablation_2026-05-31.md`
- Ablation changed rows: `experiments/gan2026_v1_validation_ablation_changed_rows_2026-05-31.csv`

## Active Priorities

1. Resolve the validation-baseline drift between the saturated 0.9280 artifact and the latest 0.9120 ablation baseline.
2. Keep deterministic V1 frozen as a controlled comparator; put any new deterministic changes into a separate, explicitly ablated candidate.
3. Start validation-only LLM/DSPy work on residual reasoning families:
   temporal/current-versus-historical selection, seizure-free versus unknown/no-reference assertions, trigger-conditioned events, semiology reconciliation, non-epileptic or EEG-only mapping, and cluster-detail interpretation.
4. Mine ablation changed rows where disabling deterministic groups improves correctness. These are high-value prompt, adjudicator, and error-taxonomy examples.
5. Maintain conservative benchmark language: the test split has been touched once for frozen-context evaluation and must not become a tuning surface.

## Work Board

### Now

- Verify whether the 0.9280 to 0.9120 validation drift is expected working-tree drift, artifact/version mismatch, or a behavior regression.
- Build the first validation-only LLM/DSPy reasoning experiment around deterministic V1 predictions and candidate diagnostics.
- Mine `experiments/gan2026_v1_validation_ablation_changed_rows_2026-05-31.csv` for deterministic-overreach examples.

### Next

- Convert mined ablation rows into a small validation-only prompt/adjudicator development set.
- Wrap or replace the final-selection tuple priority with an explicit decision record over assertion, temporality, semiology, event target, window, normalized rate, and uncertainty.
- Add paraphrase and adversarial tests for portable-rate expressions and seizure-free/no-event assertions.
- Start a living notebook for loading, gold-label distribution, scoring, and failure slices.
- Prepare controlled model-comparison scaffolding with exact model metadata in every run artifact.

### Blocked

- Final benchmark-comparison language is blocked until the replication surface and paper comparability are explicit.
- Further holdout analysis is blocked by the locked-test discipline; do not inspect test-row failures during candidate development.

### Backlog

- Add run-record metadata templates under `experiments/`.
- Refine heuristic row-level error slices into audited causal labels with examples.
- Add broader DSPy event extraction and clinical reasoner modules after the first reasoning experiment.
- Run controlled Qwen 3.6:35b local-model comparisons after model-comparison scaffolding is ready.
- Consider DSPy GEPA with GPT-5.4 as teacher only after stable artifacts and failure slices exist.

### Done Recently

- 2026-05-31: Reproduced Gan 2026 loading, normalization, split handling, author-style scoring behavior, and prediction-label repair under tests.
- 2026-05-31: Implemented schema-shaped deterministic V1 with evidence validation and row-level validation error-analysis artifacts.
- 2026-05-31: Saturated deterministic V1 on validation through focused hand-rule work, reaching a recorded 0.9280 Purist micro F1/accuracy with exact evidence validity.
- 2026-05-31: Froze deterministic V1 after a one-time locked-test evaluation showed 0.7600 Purist micro F1/accuracy and clear validation overfit.
- 2026-05-31: Refactored deterministic rules into metadata-rich, ablatable catalogues covering portable rates, seizure-free/no-event assertions, clusters, diary/log aggregation, Gan shorthand, temporal selection, and benchmark repair.
- 2026-05-31: Ran validation-only deterministic-rule ablations; strongest aggregate dependencies were portable-rate extraction, temporal selection, and seizure-free/no-event assertions.
- 2026-05-31: Interpreted the ablation results and shifted the next plan toward validation-only LLM/DSPy reasoning rather than more unbounded hand rules.

## Immediate Next Step

Resolve the validation-baseline drift, then start the first validation-only LLM/DSPy reasoning experiment using deterministic V1 outputs and ablation-changed rows as context.
