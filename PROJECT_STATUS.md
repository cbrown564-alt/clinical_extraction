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
- V1 deterministic recall now covers validation-derived interval, recent-window, distributed event-count, and common seizure-free patterns including `every N days/weeks/months`, `every other`, `occurring only every other month`, `once/twice a month`, adverbial `weekly/monthly/yearly/bimonthly`, `occur daily`, qualified daily forms such as `myoclonic jerk daily`, `tonic-clonic daily`, `tonic-clonic every night`, and `focal cognitive monthly`, `every night`, direct `N per quarter`, period-first count windows such as `This week ... 3 or 4 focal impaired awareness seizures` and `Over the past month ... 3 to 4 seizures`, qualified seizure-type count windows such as `7 to 9 focal onset seizures in three weeks`, `six or eight petit mal over the past month`, and `3 or 5 tonic-clonic over the past month`, implicit one-unit windows such as `two or four seizures over the past year`, same-day count windows such as `1 tonic-clonic seizures yesterday`, summed same-window seizure-type counts such as `one tonic-clonic and six petit mal in last week`, contextual period-first counts such as `over the past three months ... two ... and four ...`, passive count windows such as `Over the past six weeks, four episodes have occurred`, validation-derived cluster phrases such as `Monthly clusters, typically 6 to 7 seizures over 24 h`, `2 clusters this month; each ≈five absences`, `run ... with three short episodes occurring on separate days`, `cluster ... on multiple days`, and `two myoclonic clusters over the past three weeks`, seizure-day shorthand such as `Seizure days: six/30 this month` and `About three seizure days per week`, compact `TC`/`sz`/`abs` shorthand such as `TC *nine/mo`, `TC nine/mo`, `sz ×nine/mo`, `abs 8 monthly`, and `q2 - 3wk`, status-epilepticus count windows, diary date lists such as `Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24`, monthly count logs such as `Seizure: 2022: Jan x1, Feb x0, ...`, sparse full-month logs such as `2025: January 0; February 1; ...`, increasing month-count trends such as `Frequency has increased: July x 3; August x 4; September x 5`, last/prior event interval summaries, median inter-seizure interval statements, interval-range statements, `once in a fortnight` / `every second week`, standalone `Every N days on average`, isolated `single ... event last month`, long-window `three events in that timeframe`, trigger/assertion-heavy validation phrases such as `there have been four brief episodes`, `occurring approximately twice weekly`, `three clusters ... each comprising two to four`, parenthesized distributed counts with auras, short recorded month logs, and `seven brief seizures recorded in 2024 so far`, historical-frequency suppression for `Prior to this` contexts, `up to seven in bad weeks`, `free of seizures for N years`, and `no seizures since`.
- First-pass missed-frequency remediation added support for descriptor-only seizure rates (`rate of three to five focal sensory per week`, `records five focal automatisms per week`, `reports 2 to 4 focal non-motor per week`) and cluster-count phrases with unspecified size (`Weekly morning clusters reported`, `two/three clusters this quarter`, `nocturnal clusters 3×/month`, and `last month ≈N clusters`).
- V1 validation result is 0.6293 Purist micro F1/accuracy on 750 validation rows; evidence validity remains 750/750.
- Validation failures are currently dominated by 101 missed frequency-evidence rows, 70 wrong-frequency-bucket rows, 53 missed seizure-free/no-event rows, 43 overpredicted-frequency rows, and 11 frequency-predicted-as-seizure-free rows; 154 incorrect rows have zero non-fallback clinical candidates, making extraction recall and temporal/assertion classification the dominant next bottlenecks.
- Latest v1 validation refresh is `experiments/gan2026_v1_validation_error_analysis_2026-05-31.md`; the seizure-free temporal guard pass fully corrected rows `13051, 13058, 13149, 13178, 13190, 15404, and 15429`, converted unsafe seizure-free predictions on rows `13008, 13267, 14973, and 15997` into safer no-reference misses, reduced `frequency_predicted_seizure_free` errors from 22 to 11, and validation is at 0.6293 Purist micro F1/accuracy with 750/750 exact selected-evidence validity.
- `pytest` and `ruff` pass in the local `.venv` after validation error-analysis generation.

## Work Board

### Now

- Continue auditing the remaining `frequency_predicted_seizure_free` rows: `14187, 14214, 14250, 14284, 14317, 14383, 14454, 14581, 14611, 14672, and 15317`.
- Continue targeted deterministic remediation on missed-frequency rows that were made safer by seizure-free guardrails: `13008, 13267, 14973, and 15997`.

### Next

- Run an error-analysis refresh after each pass and fold the next unrescued row IDs from the same slice into the same cycle.
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
- 2026-05-31: Fixed adjective-rate evidence extraction, added focused V1 tests and extraction support for every-other-month wording, period-first recent counts, nightly/daily qualified seizure phrases, and validation-derived cluster phrasings; refreshed validation artifacts now show 0.4920 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.
- 2026-05-31: Added focused V1 tests and extraction support for validation-derived month-window semiology counts, monthly cluster summaries, seizure-day shorthand, compact `TC`/`sz` notation, and `up to N in bad weeks`; refreshed validation artifacts now show 0.5213 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.
- 2026-05-31: Added focused V1 tests and extraction support for compact `abs` monthly counts, compact `qN-unit` intervals, status-epilepticus count windows, diary date lists, and monthly count logs; refreshed validation artifacts now show 0.5413 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.
- 2026-05-31: Added focused V1 tests and extraction support for median inter-seizure intervals, interval-range phrasing, fortnight/every-second-week wording, standalone `Every N days on average`, isolated single-event recent counts, long-window `three events in that timeframe`, and historical-frequency suppression; refreshed validation artifacts now show 0.5587 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.
- 2026-05-31: Added focused V1 tests and extraction support for contextual period-first event counts, passive count windows, trigger-linked sparse month logs, increasing month-count trends, last/prior event intervals, and cluster-over-period summaries; rows 5763, 5791, 5837, 5866, 5995, 6065, 6112, and 6251 are now correct, refreshed validation artifacts show 0.5733 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.
- 2026-05-31: Added focused V1 tests and extraction support for trigger/assertion-heavy frequency rows covering fortnight counts, `there have been` period-first counts, `twice weekly`, cluster `each comprising` patterns, parenthesized distributed auras, short recorded month logs, and year-so-far counts; rows 6509, 6701, 6952, 7167, 7196, 7275, 7401, and 9002 are now correct, refreshed validation artifacts show 0.5813 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.
- 2026-05-31: Reviewed the latest validation artifacts and confirmed the first-pass target rows (9287, 9299, 9300, 10003, 10047, 10063, 10097, 10237, and 10245) remain unresolved misses.
- 2026-05-31: Added focused V1 tests and extraction support for descriptor-only seizure-rate phrases and unspecified-size cluster-count phrases; rows 9287, 9299, 9300, 10003, 10047, 10063, 10097, 10237, and 10245 are now correct, refreshed validation artifacts show 0.6027 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.
- 2026-05-31: Completed second-pass remediation for the cluster-heavy target slice (rows 10383, 10434, 10517, 10630, 10673, 10807, 10829, 10873, 10894, 10896, 10902, 10965, 10967, and 11197); refreshed validation shows 0.6200 Purist micro F1/accuracy with 0.6200 precision/recall and same-cluster/size evidence captured correctly for all 14 rows.
- 2026-05-31: Added temporal/assertion guards for seizure-free distractors plus remission-breakthrough and cyclic-cluster extraction support; rows 13051, 13058, 13149, 13178, 13190, 15404, and 15429 are now correct, refreshed validation shows 0.6293 Purist micro F1/accuracy with 750/750 exact selected-evidence validity, and full `pytest`/Ruff pass.

## Immediate Next Step

Continue the remaining `frequency_predicted_seizure_free` audit, focusing on “since then / no further events since” rows that need current burst/date-list extraction rather than broad seizure-free suppression.
