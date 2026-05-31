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
- V1 was validation-saturated through hand-rule work, then frozen. The refreshed validation artifact reports 0.9293 Purist micro F1/accuracy on 750 validation rows with 750/750 exact selected-evidence validity.
- V1 was evaluated once on the locked test split without inspecting test-row failures: 0.7600 Purist micro F1/accuracy, 0.7867 Pragmatic micro F1/accuracy, and 450/450 exact selected-evidence validity. This indicates substantial validation-surface overfit.
- The deterministic-rule catalogue now exposes rule metadata, portability categories, selected-candidate diagnostics, group/rule-ID ablations, temporal-selection ablations, and traceable benchmark-repair steps.
- The validation-baseline drift was traced to diary/log catalogue regression: sparse monthly timeline patterns from saturated V1 were not fully carried into `gan2026.rules.diary`. Restored catalogued rules now produce a current working-tree baseline of 0.9293 Purist micro F1/accuracy and 0.9387 Pragmatic micro F1/accuracy with 750/750 exact evidence validity.
- A first validation-only prompt/adjudicator development set now mines ablation-changed rows into 16 JSONL examples with deterministic V1 candidate diagnostics: 10 deterministic-overreach examples and 6 support controls.
- The first live DSPy final-selection adjudicator run over those 16 examples used GPT-4.1 mini via DSPy. It produced 16/16 parseable decision records with no call failures, but it is diagnostic rather than promotable: 6/16 Purist correct and 10/16 Pragmatic correct, preserving all support controls while failing all deterministic-overreach examples.
- LLM/DSPy validation runs now follow a cost-controlled ladder: 25-row smoke
  test, 50-row meaningful signal, then 250-row development result after a
  decision gate. Full 750-row validation runs should be rare and require a
  documented reason that 250 rows are insufficient.
- A first note-only LLM-first validation-prefix run over 250 rows used GPT-4.1
  mini and no deterministic V1 candidates. After shared schema alias repair and
  Gan label repair through `normalize.py`, the artifact reports 250/250 decision
  records, 0 call failures, 0 blocking parse/schema failures, 0.8200 Purist
  accuracy/micro-F1 proxy, 0.8560 Pragmatic accuracy, 96 deterministic repair
  notes, and 86/250 exact evidence substrings. This is useful signal but below
  the >=0.9000 goal; the next architecture should move from direct note-to-label
  extraction toward structured event extraction plus clinical selection.
- Design concern to revisit: early LLM results suggest the full V1-style event
  schema and metadata burden may ask too much of the model in one pass. This is
  not a critical flaw, but the next structured extractor should consider a
  slimmer first-pass schema that captures essential clinical facts and evidence
  before adding richer metadata through validation or follow-up reasoning.

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
- Prompt/adjudicator development set: `experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.md`
- Prompt/adjudicator JSONL: `experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.jsonl`
- First DSPy adjudicator run: `experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_2026-05-31.md`
- First DSPy adjudicator JSONL: `experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_2026-05-31.jsonl`
- LLM-first 250-row validation-prefix run: `experiments/gan2026_llm_first_validation250_gpt41mini_v01_2026-05-31.md`
- LLM-first 250-row JSONL: `experiments/gan2026_llm_first_validation250_gpt41mini_v01_2026-05-31.jsonl`

## Active Priorities

1. Keep deterministic V1 frozen as a controlled comparator; put any new deterministic changes into a separate, explicitly ablated candidate.
2. Start validation-only LLM/DSPy work on residual reasoning families:
   temporal/current-versus-historical selection, seizure-free versus unknown/no-reference assertions, trigger-conditioned events, semiology reconciliation, non-epileptic or EEG-only mapping, and cluster-detail interpretation.
3. Use the 25/50/250 validation ladder for LLM/DSPy and hybrid architecture
   comparisons; do not run all 750 validation rows unless the experiment artifact
   states why the 250-row slice is insufficient.
4. Use the mined ablation dev set as the seed surface for prompt, adjudicator, and error-taxonomy experiments.
5. Maintain conservative benchmark language: the test split has been touched once for frozen-context evaluation and must not become a tuning surface.

## Work Board

### Now

- Stabilize the LLM-first output contract and shared schema/label repair boundary:
  schema repair should handle payload aliases, while Gan label repair remains in
  `normalize.py`.
- Inspect the 250-row LLM-first failure modes, especially low exact-evidence
  validity and direct note-to-label selection errors, before promoting any
  broader run.
- Build the next architecture as LLM-first structured event extraction plus a
  clinical selector, keeping deterministic V1 only as comparator/diagnostic.
- Revisit whether the V1 candidate-event schema should be staged: minimal
  source-near event extraction first, then deterministic/schema-validation
  enrichment or a second LLM reasoning step for metadata that proved too heavy
  for direct extraction.

### Next

- Wrap or replace the final-selection tuple priority with an explicit decision record in candidate code if the dev-set experiment supports it.
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
- 2026-05-31: Resolved validation-baseline drift by restoring catalogued sparse monthly diary/timeline rules, refreshing validation/error and ablation artifacts, and confirming 0.9293 Purist micro F1/accuracy with exact evidence validity.
- 2026-05-31: Mined validation ablation-changed rows into a 16-example prompt/adjudicator development set with V1 candidate and normalization diagnostics.
- 2026-05-31: Implemented and ran the first live DSPy final-selection adjudicator over the 16-example validation dev set, recording prompt/model metadata and row-level outputs.
- 2026-05-31: Documented the standard LLM/DSPy validation ladder as 25-row smoke,
  50-row meaningful signal, and 250-row development result after a decision gate;
  full 750-row validation runs are now rare and require justification.
- 2026-05-31: Refactored shared schema alias repair away from Gan label repair:
  `schema_repair.py` handles model-output payload aliases, while `normalize.py`
  owns Gan-compatible label repair including selected-evidence formatting.
- 2026-05-31: Ran/reparsed a GPT-4.1 mini note-only LLM-first 250-row validation
  prefix artifact with 0.8200 Purist accuracy/micro-F1 proxy and 0.8560 Pragmatic
  accuracy; direct note-to-label extraction remains below target.

## Immediate Next Step

Audit the first DSPy adjudicator row rationales and convert the deterministic-overreach failures into explicit prompt/schema requirements before any broader validation run.
