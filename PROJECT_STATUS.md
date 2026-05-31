# Project Status

Last updated: 2026-05-31

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that exceeds 0.9 purist F1 while preserving enough structure to support future clinical extraction tasks.

## Research Objective

Produce a paper-quality hybrid deterministic-LLM system that demonstrates modular breadth/depth, improved generalisation discipline, transparent per-note reasoning/evidence trails, and rigorous component-level error analysis/ablation.

## Current Strategy

Start with a small package core and a Gan-specific task implementation. Reproduce data loading, label normalization, and scoring before optimizing any DSPy modules.

Treat deterministic rules as controlled variables. Categorize each rule by portability and clinical meaning so experiments can separate general date logic, seizure-frequency logic, Gan-specific synthetic patterns, and benchmark-formatting repairs.

## Active Milestones

1. Port author-provided label repair logic and clarify the remaining normalization policy under tests.
2. Build a simple deterministic baseline.
3. Implement DSPy event extraction and clinical reasoning modules.
4. Add row-level error analysis and a living notebook.
5. Add ablation toggles for deterministic rule categories and DSPy stages.
6. Produce paper-facing tables for component effects, rule effects, failure modes, and evidence validity.

## Current Repo State

- Python package skeleton exists under `src/clinical_extraction`.
- Gan 2026 task module exists under `tasks/seizure_frequency/gan2026`.
- Initial README, architecture notes, pipeline design notes, decision record, and runbook exist.
- Research contribution thesis exists under `docs/research`.
- Git repository has been initialized.
- Local `.venv` has been created with project dev dependencies.
- Gan-compatible data loading and evaluation reproduction is complete for the current JSON surface.
- Loader exposes full note text, gold label/reference, quality flags, raw rows, and parsed monthly gold frequency.
- Gold label parsing now covers all 1,500 local Gan rows under focused tests.
- Loader now preserves normalized gold labels, semantic label kind, yearly bounds, and monthly scorer values separately.
- Locked Gan 2026 split manifest exists at `data/Gan (2026)/splits/gan2026_split_v1.json`: 300 train rows for DSPy GEPA or other optimizers, 750 validation rows for ordinary development, and 450 test rows for final holdout only.
- Split protocol is documented in `docs/design/gan2026_split_protocol.md`, and loader helpers can load manifest-ordered split records.
- Prediction-label repair behavior has been ported into `gan2026.normalize` for common author-script repairs.
- Scoring policy prefers the author evaluation script when it conflicts with CSV-preparation behavior.
- `row_ok=False` rows are included in the development/evaluation surface and retained for stratified analysis.
- Step 1 inspection is documented in `docs/research/gan2026_step1_inspection.md`.
- Ten-letter schema exploration is documented in `docs/research/gan2026_schema_exploration_10_examples.md`.
- Pipeline V1 now specifies richer candidate-event, deterministic-normalization, and final-selection schemas.
- LLM model strategy is documented in `docs/design/model_strategy.md`: GPT-4.1 mini for rapid baseline experiments, Qwen 3.6:35b later for local strong-reasoning tests after a pipeline exceeds 0.8 purist F1, and GPT-5.4 only as a possible DSPy GEPA teacher.
- First schema-shaped deterministic V1 baseline is implemented in `gan2026.pipeline_v1`.
- V1 run record exists at `experiments/gan2026_v1_deterministic_baseline_2026-05-31.md`.
- V1 historical development result on all 1,500 local rows is 0.3120 Purist micro F1/accuracy; future candidate iteration should report validation-split results instead.
- V1 selected-evidence validity is 1,500/1,500 exact source substrings.
- V1 validation-split row-level error analysis exists at `experiments/gan2026_v1_validation_error_analysis_2026-05-31.md`, with CSV rows at `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`.
- The validation error artifact now includes non-fallback clinical candidate counts, selected-evidence type, heuristic clinical mode flags, and likely failed-operation slices.
- V1 deterministic recall now covers validation-derived interval, recent-window, distributed event-count, and common seizure-free patterns including `every N days/weeks/months`, `every other`, `once/twice a month`, adverbial `weekly/monthly/yearly/bimonthly`, `occur daily`, direct `N per quarter`, qualified seizure-type count windows such as `7 to 9 focal onset seizures in three weeks`, implicit one-unit windows such as `two or four seizures over the past year`, same-day count windows such as `1 tonic-clonic seizures yesterday`, summed same-window seizure-type counts such as `one tonic-clonic and six petit mal in last week`, `free of seizures for N years`, and `no seizures since`.
- V1 validation result is 0.4667 Purist micro F1/accuracy on 750 validation rows; evidence validity remains 750/750.
- Validation failures are dominated by 218 missed frequency-evidence rows, 60 wrong-frequency-bucket rows, 56 missed seizure-free/no-event rows, 35 frequency-predicted-as-seizure-free rows, and 31 overpredicted-frequency rows; 272 incorrect rows have zero non-fallback clinical candidates, making extraction recall and temporal/assertion selection the dominant next bottlenecks.
- `pytest` and `ruff` pass in the local `.venv` after validation error-analysis generation.

## Work Board

### Now

- Improve deterministic candidate recall for ordinary frequency evidence before adding LLM reasoning.
- Add focused tests from the refreshed high-priority missed `frequency` rows, especially isolated `bimonthly`, remaining daily phrases, and `this week/month` subtype-count contexts not caught by current regexes.
- Audit why seizure-free recall now creates 35 `frequency_predicted_seizure_free` errors, then add assertion/temporal guards before broadening more no-event phrases.

### Next

- Inspect rows 978, 1223, 1694, 1706, and 2369 from the refreshed validation error table before adding the next recall rules.
- Start a living notebook for loading, gold-label distribution, scoring, and failure slices.
- Use GPT-4.1 mini as the default LLM runtime model for early DSPy experiments and record exact model metadata in run artifacts after deterministic recall is less brittle.

### Blocked

- Final benchmark-comparison language is blocked until replication surface and paper comparability are explicit.

### Backlog

- Add run-record metadata templates under `experiments/`.
- Refine heuristic row-level error slices into audited causal labels with examples once deterministic recall is less sparse.
- Add DSPy event extraction and clinical reasoner modules after deterministic substrate parity.
- After at least one pipeline exceeds 0.8 purist F1, run controlled Qwen 3.6:35b local-model comparisons on the Windows laptop.
- Consider DSPy GEPA with GPT-5.4 as teacher after the hand-built pipeline has stable artifacts and failure slices.

### Done Recently

- 2026-05-31: Created initial package, docs, tests, and Gan 2026 task skeleton.
- 2026-05-31: Added project-specific Codex workflow skills for TDD, kanban/status, experiments, and scoring guardrails.
- 2026-05-31: Created local `.venv`, installed dev dependencies, and verified `pytest`/`ruff`.
- 2026-05-31: Reproduced Gan data loading/evaluation substrate with tested gold-label extraction, monthly frequency parsing, row quality flags, and evaluation helpers.
- 2026-05-31: Documented Step 1 inspection findings, including cluster-policy disagreement, sentinel collapse, misleading `clinic_date` field naming, and 30-day month conversion.
- 2026-05-31: Decided to include `row_ok=False` rows for development/evaluation while retaining the flag for stratified analysis, and to prefer author evaluation-script scoring.
- 2026-05-31: Reconciled normalization sentinels by adding semantic label records and loader fields while preserving Gan scorer collapse to `1000`.
- 2026-05-31: Ported tested author prediction-label repair behavior into `gan2026.normalize`; `pytest` and `ruff` pass.
- 2026-05-31: Worked through 10 Gan letters and updated the V1 pipeline schema toward source-near candidate events, deterministic normalization, and traceable final selection.
- 2026-05-31: Documented LLM model strategy and experiment-metadata requirements.
- 2026-05-31: Implemented the first schema-shaped deterministic V1 baseline with candidate events, normalized events, final selection diagnostics, and exact evidence validation.
- 2026-05-31: Evaluated V1 on all 1,500 local Gan rows: Purist micro F1/accuracy 0.3120, evidence validity 1,500/1,500, with failures dominated by missed frequency/seizure-free evidence.
- 2026-05-31: Added Gan 2026 train/validation/test split protocol and locked `gan2026_split_v1` manifest; updated skills to enforce validation-first development and locked test holdout discipline.
- 2026-05-31: Added reusable Gan row-level error-analysis generation, wrote focused tests, and generated V1 validation artifacts showing 0.3240 Purist micro F1/accuracy with 750/750 exact selected-evidence validity.
- 2026-05-31: Improved V1 deterministic recall for validation-derived implicit interval, adverbial rate, and recent-window count phrases; refreshed validation artifacts now show 0.3893 Purist micro F1/accuracy with 750/750 exact selected-evidence validity.
- 2026-05-31: Upgraded validation error analysis with clinical candidate counts, evidence-source classes, heuristic clinical mode flags, and likely failed-operation counts; focused tests and Ruff pass.
- 2026-05-31: Added focused V1 tests and extraction support for summed distributed same-window event counts plus common seizure-free phrasing with breakthrough-event guard coverage; refreshed validation artifacts now show 0.4400 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.
- 2026-05-31: Added focused V1 tests and extraction support for quarter windows, standalone/occur adjective rates, qualified seizure-type count windows, implicit one-unit `over the past year/month` windows, same-day count windows, and additional seizure-type nouns; refreshed validation artifacts now show 0.4667 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.

## Immediate Next Step

Use the refreshed validation error table's first high-priority missed-frequency rows to add tests for isolated `bimonthly`, remaining daily contexts, and cluster/several-count phrases, while separately auditing seizure-free over-selection before adding more no-event recall.
