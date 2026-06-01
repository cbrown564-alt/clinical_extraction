# Project Status

Last updated: 2026-06-01

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least 0.9000 Purist F1 on development surfaces while preserving enough structure to support future clinical extraction tasks.

The current research aim is a paper-quality hybrid deterministic-LLM system with transparent evidence trails, component-level ablations, and conservative benchmark claims.

## Current Strategy

Use the Gan 2026 task as the first controlled extraction surface. Keep data loading, label normalization, scoring, split discipline, and deterministic-rule behavior explicit before optimizing LLM or DSPy components.

Treat deterministic rules as a frozen, ablatable comparator rather than an endlessly expanding solution. The active candidate architecture should stay LLM-first: model extraction and/or clinical reasoning produce the prediction-bearing interpretation, while deterministic code is limited to schema validation, evidence validation, Gan-compatible normalization, arithmetic repair, benchmark-format repair, and scoring.

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
  documented reason that 250 rows are insufficient. The shared Gan LLM CLI
  runner defaults to 10-row progress/checkpoint emission for all bound pipelines.
- A first note-only LLM-first validation-prefix run over 250 rows used GPT-4.1
  mini and no deterministic V1 candidates. After shared schema alias repair and
  Gan label repair through `normalize.py`, the artifact reports 250/250 decision
  records, 0 call failures, 0 blocking parse/schema failures, 0.9520 Purist
  accuracy/micro-F1 proxy, 0.9560 Pragmatic accuracy, 113 deterministic repair
  notes, and 86/250 exact evidence substrings. This is useful signal but below
  a full validation-split claim; the next architecture should move from direct
  note-to-label extraction toward structured event extraction plus clinical
  selection before any rare 750-row validation run.
- The rare full-validation escalation of that direct note-to-label pipeline is
  now complete and rejects the direct architecture as a goal candidate: 750/750
  validation rows, GPT-4.1 mini, no deterministic V1 candidates, 610 reused raw
  outputs from checkpoints, 0 call failures, 41 schema/parse failures, 0.6733
  Purist accuracy/micro-F1 proxy, 0.7253 Pragmatic accuracy, and 670/750 exact
  evidence substrings. The 250-row prefix was not representative. The main
  failure families are schema brittleness, seizure-free-vs-unknown/current
  assertion errors, no-reference/unknown confusions, cluster-detail failures, and
  broad clinical selection/temporality misses.
- Design concern to revisit: early LLM results suggest the full V1-style event
  schema and metadata burden may ask too much of the model in one pass. This is
  not a critical flaw, but the next structured extractor should consider a
  slimmer first-pass schema that captures essential clinical facts and evidence
  before adding richer metadata through validation or follow-up reasoning.
- The staged structured LLM-first extractor uses a slimmer source-near event
  schema plus LLM clinical selection, with shared `schema_repair.py` for
  payload/schema aliases and `normalize.py` for Gan-compatible label repair. Its
  strongest standard-gate result so far is the v0.2 raw-output 250-row reparse
  with current bounded repairs: 250/250 structured rows, 0 parse/schema
  failures, 242/250 exact selection evidence substrings, and 0.9800 Purist
  accuracy / 0.9840 Pragmatic accuracy. This clears the 250-row development
  gate but is not a full validation-split claim.
- A rare full-validation completion of the staged structured pipeline reached
  the numeric validation threshold exactly: 750/750 validation rows, 675/750
  Purist correct = 0.9000 Purist accuracy/micro-F1 proxy, 690/750 Pragmatic
  correct = 0.9200, 0 call failures, 0 parse/schema failures, and 714/750 exact
  selected-evidence substrings. The repair audit and decision retrospective now
  classify this as a hybrid structured GPT-4.1 mini plus Gan-specific
  post-processing development artifact, not a clean LLM-first objective
  completion.
- A v0.4 structured selector revision added explicit benchmark-window guidance:
  do not let current seizure-free status erase a recent countable last-event
  window, and select the most frequent current/recent seizure-like event rather
  than the clinically most severe subtype. It cleared the standard ladder through
  25-row and 50-row live runs at 1.0000 Purist with no parse failures. The
  250-row live development run reached 0.9480 Purist/Pragmatic, and a no-call
  reparse after selected-evidence repair reached 0.9520 Purist/0.9560
  Pragmatic. This is a useful candidate but not a promotion over the v0.2
  250-row result; compare error families before any broader escalation.

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
- LLM-first full-validation diagnostic run: `experiments/gan2026_llm_first_validation750_gpt41mini_v01_2026-06-01.md`
- LLM-first full-validation JSONL: `experiments/gan2026_llm_first_validation750_gpt41mini_v01_2026-06-01.jsonl`
- Structured LLM-first scaffold: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`
- General Gan LLM pipeline CLI harness: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_pipeline_cli.py`
- Structured LLM-first 25-row smoke run: `experiments/gan2026_llm_structured_validation25_gpt41mini_v01_2026-06-01.md`
- Structured LLM-first 25-row JSONL: `experiments/gan2026_llm_structured_validation25_gpt41mini_v01_2026-06-01.jsonl`
- Structured LLM-first 250-row standard-gate reparse: `experiments/gan2026_llm_structured_validation250_gpt41mini_v02_reparse_current_2026-06-01.md`
- Structured LLM-first 720-row no-call replay: `experiments/gan2026_llm_structured_validation720_gpt41mini_v05_reparse_current2_2026-06-01.md`
- Structured LLM-first rare 750-row completion: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.md`
- Structured LLM-first repair audit: `experiments/gan2026_llm_structured_validation750_v05_repair_audit_2026-06-01.md`
- Structured LLM-first decision retrospective: `experiments/gan2026_llm_structured_decision_retrospective_2026-06-01.md`
- Structured LLM-first repair ablation: `experiments/gan2026_llm_structured_validation750_v05_repair_ablation_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen as a controlled comparator; put any new deterministic changes into a separate, explicitly ablated candidate.
2. Enforce the architecture gate before the metric gate: no result satisfies the
   LLM-first objective if semantic-state-changing repair is included without
   separate naming, ablation, and claim language.
3. Start validation-only LLM/DSPy work on residual reasoning families:
   temporal/current-versus-historical selection, seizure-free versus unknown/no-reference assertions, trigger-conditioned events, semiology reconciliation, non-epileptic or EEG-only mapping, and cluster-detail interpretation.
4. Use the 25/50/250 validation ladder for LLM/DSPy and hybrid architecture
   comparisons; do not run all 750 validation rows unless the experiment artifact
   states why the 250-row slice is insufficient. New LLM pipelines should use the
   general Gan LLM CLI runner instead of copying runner behavior.
5. Use the mined ablation dev set as the seed surface for prompt, adjudicator, and error-taxonomy experiments.
6. Maintain conservative benchmark language: the test split has been touched once for frozen-context evaluation and must not become a tuning surface.

## Work Board

### Now

- Classify v0.5 repair families from the no-call ablation: keep
  benchmark-format repairs separate from source-evidence arithmetic and
  deterministic clinical-selection overrides.
- Decide which high-concern families should be disabled for a clean LLM-first
  selector claim versus promoted as explicit deterministic candidate modules
  with separate ablations.
- Keep the staged output contract: minimal source-near event facts first,
  deterministic normalization/validation second, and LLM clinical selection
  last. Avoid drifting back to a deterministic-candidate-first pipeline.
- Revisit whether the V1 candidate-event schema should be staged: minimal
  source-near event extraction first, then deterministic/schema-validation
  enrichment or a second LLM reasoning step for metadata that proved too heavy
  for direct extraction.

### Next

- Run a clean-architecture no-call replay with only accepted format-preserving
  normalization enabled, then use that score as the LLM-first attribution
  baseline.
- Re-run the standard 25/50/250 ladder on the cleaned architecture before any
  further 750-row validation claim.
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
  prefix artifact with 0.9520 Purist accuracy/micro-F1 proxy and 0.9560 Pragmatic
  accuracy after selected-evidence label repair; direct note-to-label extraction
  clears the standard 250-row development gate but is not a full validation-split
  claim.
- 2026-06-01: Tightened selected-evidence Gan label repair for cluster-rate-only
  evidence, implicit monthly cluster detail, yesterday-as-one-day windows, and
  LLM final labels with event descriptions plus a per-window denominator. The
  remaining 250-row misses are now mostly clinical selection/temporality issues
  rather than formatter failures.
- 2026-06-01: Added a reusable Gan LLM pipeline CLI harness with artifact-level
  raw-output reuse, DSPy cache control, progress emission, and 10-row
  checkpointing. The LLM-first CLI is now a thin binding over the shared CLI.
- 2026-06-01: Tightened the reusable Gan LLM CLI into an explicitly general
  runner for any LLM/DSPy Gan pipeline. Concrete pipeline CLIs now supply a
  `GanLlmPipelineCliSpec`; the runner owns split loading, raw-output reuse, DSPy
  cache control, progress cadence, and checkpoint paths.
- 2026-06-01: Ran the rare full-validation direct note-to-label diagnostic:
  0.6733 Purist and 0.7253 Pragmatic on 750 validation rows, with 0 call failures
  but 41 schema/parse failures. This rejects direct note-to-label extraction as
  the final architecture and makes the staged structured extractor the next
  priority.
- 2026-06-01: Added the first staged LLM-first structured extractor scaffold:
  a slim source-near event schema, LLM clinical selection, deterministic
  normalization of selected LLM evidence through `normalize.py`, shared
  structured schema alias repair through `schema_repair.py`, and a thin CLI
  binding over the general Gan LLM pipeline CLI.
- 2026-06-01: Ran the standard 25-row live smoke for the staged structured
  extractor with GPT-4.1 mini: 25/25 structured records, 0 call failures,
  0 parse/schema failures, 25/25 exact selection-evidence substrings, 11
  deterministic label repair notes, and 1.0000 Purist/Pragmatic accuracy on the
  smoke slice. This clears smoke only; it is not a broad validation claim.
- 2026-06-01: Ran the staged structured extractor through the standard ladder:
  50-row v0.2 live result reached 1.0000 Purist/Pragmatic, and the 250-row
  v0.2 no-call reparse reached 0.9640 Purist/Pragmatic with 0 parse/schema
  failures. A rare full-validation escalation initially fell below target, then
  selected-evidence repairs for `multiple per day`, month-colon diary counts,
  current non-epileptic events, post-medication-change bursts, and dated event
  sequences recovered no-call checkpoints to 0.9034 at 580 rows, 0.9051 at 590
  rows, 0.9017 at 600 rows, and 0.9032 at 620 rows. The next live 20-row tail
  pocket dropped the 640-row continuation to 0.8844 Purist/0.8953 Pragmatic
  with 0 parse/schema failures; stop spending live calls until the
  selector/schema is revised.
- 2026-06-01: Added v0.4 structured selector guidance for Gan benchmark-window
  selection and highest-frequency current event selection, plus bounded repairs
  for elapsed last-event windows, dated "since then" jerk counts, upper-bound
  bad-week rates, single count-over-window labels, and cluster-on-multiple-days
  evidence. Live v0.4 cleared 25/50 at 1.0000 and produced a 250-row development
  result of 0.9480 Purist, improving to 0.9520 after no-call repair reparse. This
  is below the v0.2 250-row result, so v0.4 should be treated as diagnostic until
  its gains/losses are compared row-by-row.
- 2026-06-01: Re-established the LLM/DSPy runner as a general Gan CLI harness
  for any LLM pipeline, not a structured-extractor-specific runner, and kept
  concrete pipelines as thin bindings. The runner emits progress/checkpoint
  artifacts every 10 rows by default and supports raw-output reuse alongside
  DSPy cache control.
- 2026-06-01: Added bounded shared normalization repairs for selected-evidence
  cluster cycles, event-days-per-week labels, daily myoclonic clusters, and
  monthly diary strings, plus LLM-extracted-event monthly-diary aggregation in
  the structured pipeline. Follow-on no-call and live continuations reached
  0.9083 Purist at 720 rows and exactly 0.9000 Purist at 750 validation rows,
  with 0 call failures and 0 parse/schema failures.
- 2026-06-01: Recorded the successful rare structured LLM-first validation
  completion:
  `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.md`
  reports 675/750 Purist correct = 0.9000, 690/750 Pragmatic correct = 0.9200,
  714/750 exact selected-evidence substrings, and 720 reused raw outputs. This
  reached the numeric threshold, but the repair audit and decision retrospective
  reclassify it as a repair-heavy hybrid development artifact whose LLM-only
  contribution is not isolated.
- 2026-06-01: Added the v0.5 repair audit correction path to the work board,
  made structured-parser repair families configurable, added a no-call repair
  ablation runner, and generated
  `experiments/gan2026_llm_structured_validation750_v05_repair_ablation_2026-06-01.md`
  over the 650 saved raw outputs from the audited artifact. Current-code replay
  shows raw LLM final labels at 0.6062 Purist, basic repair at 0.7092,
  selected-evidence repair at 0.8400, and the full current stack at 0.9046
  Purist on that 650-row validation-development surface.

## Immediate Next Step

Use the repair ablation to classify each repair family as benchmark-format
normalization, source-evidence arithmetic, or deterministic clinical-selection
override; then update v0.5 claim language and choose the clean-claim
configuration for the next no-call replay.
