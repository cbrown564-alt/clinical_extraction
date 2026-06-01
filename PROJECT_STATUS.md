# Project Status

Last updated: 2026-06-01

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving transparent evidence
trails, ablations, and conservative benchmark language.

## Current Strategy

Use Gan 2026 as the first controlled extraction surface. Organize experiments
by research family: `rules_only`, `llm_only`, and `hybrid`. Deterministic V1 is
frozen as the `rules_only_v1` comparator; LLM-only candidates must keep the LLM
prediction-bearing; hybrid candidates must name component order, semantic
ownership, and deterministic repair boundaries explicitly.

## Recent Context

- Locked split `gan2026_split_v1`: 300 train, 750 validation, 450 holdout;
  LLM/DSPy work escalates 25 -> 50 -> 250 validation rows; test is not tuning.
- Deterministic V1 is frozen as a comparator: 0.9293/0.9387 validation and
  0.7600/0.7867 on its one locked-test Purist/Pragmatic evaluation.
- Structured v0.5 reached 675/750 Purist = 0.9000 on full validation, but audit
  classified it as repair-heavy hybrid behavior rather than clean LLM-first.
- LLM-only claim-table selector v3 hit a revise-only 250-row result: 248/250 structured,
  217/250 raw Purist, 218/250 clean Purist, and 224/250 clean Pragmatic.
- LLM-only claim-table selector v4 completed its 250-row validation diagnostic: 248/250
  structured, 0 call failures, 2 parse/schema failures, 226/250 raw Purist,
  229/250 clean Purist, 236/250 clean Pragmatic, and 247/250 selected evidence
  exact. It clears 0.9000 as a development diagnostic but is not a promotion
  signal because 32 rows change downstream and failure families remain.
- A retry variant differed by one row (230/250 clean Purist), so treat v4 as a
  revise signal with small live-tail variance rather than a scale-up candidate.
- A no-call schema replay of LLM-only claim-table selector v4 repaired non-semantic output
  shape issues: 250/250 structured, 0 parse/schema failures, 231/250 clean
  Purist, and 238/250 clean Pragmatic. This improves the architecture gate but
  does not change the revise decision because semantic failure families remain.
- Hybrid rules-candidates LLM adjudicator v0.1 now has a split-wide
  runner and validation ladder artifacts. Its 250-row schema replay reached
  243/250 Purist and 244/250 Pragmatic with 0 parse failures, candidate-set
  Purist recall 246/250, and three deterministic-correct to adjudicator-wrong
  regressions. It is the strongest current validation candidate but still needs
  failure review and ablations before any holdout freeze.
- Hybrid rules-candidates LLM adjudicator v0.1 full-validation schema replay reached 680/750 Purist and
  689/750 Pragmatic with 0 parse failures, but it underperformed deterministic
  top on the same rows (697/750 Purist) because the adjudicator had 24
  deterministic-correct regressions against 7 corrections. Revise before
  holdout; v0.1 is not a frozen test candidate.
- LLM-only claim-table selector v4 full validation collapsed to 528/750 clean Purist and
  577/750 clean Pragmatic. Reject v4 for holdout and redesign v5 around
  cluster-axis preservation, boundary-state selection, and selector ablation.
- Added unified component-ablation tooling for the three key experiment
  families: rules-only, LLM-only, and hybrid, with order/ownership captured for
  LLM-then-deterministic and deterministic-then-LLM conditions.
  It normalizes deterministic replay and saved JSONL artifacts into shared
  condition summaries for attribution, repair, and adjudicator comparisons.
- Routine LLM experiments now use one cache-first CLI,
  `gan2026-llm-experiment`, with `--pipeline` selection. DSPy cache is on by
  default; saved-output replay is reserved for explicit offline artifact
  analysis rather than normal experiment execution.
- Shared schema repair is alias-only again; parser-owned defaults live with the
  hybrid adjudicator parser, `core.schemas` is task-neutral, and mypy is clean
  across all 35 source files.
- LLM-only structured-events repair attribution now has named modes:
  `raw_model`, `strict_format`, `clean_scorer_facing`,
  `selected_evidence_derivation`, `hybrid_full_stack`, and `custom`; run
  metadata, reports, and repair ablations expose the resolved mode.
- The codebase thermonuclear review consolidation phase has started: shared
  Git/Python run metadata and common report-provenance rendering now live in
  task-level helpers used by the current LLM-only and hybrid Gan runners.
- Phase 5 behavior-preserving splits have moved stable concepts out of the
  largest files: Gan label parsing, clean gold policy, selected-evidence
  derivation, benchmark prediction repair, deterministic temporal helpers,
  deterministic final selection, and LLM structured-events temporal helpers.
  LLM structured-events monthly-diary repair arithmetic now also has a dedicated
  helper module. Public repair/parser APIs remain in place; scorer behavior is
  unchanged.
- Phase 5 also split deterministic V1 candidate extraction out of
  `pipeline_v1.py` into `deterministic_extraction.py`. The pipeline shell now
  owns schemas, run orchestration, candidate event materialization,
  normalization, and final selection wiring, while the extracted module owns
  deterministic regex/rule candidate discovery and evidence text helpers.
  Behavior is preserved; Ruff, mypy, focused deterministic tests, and full
  pytest are green.
- The deterministic extraction split has continued with small ownership
  modules for candidate pruning, note/evidence text handling, and Gan frequency
  token/label formatting. After the latest rate-discovery extraction,
  `deterministic_extraction.py` owns rule-family orchestration but no longer
  owns generic evidence cleanup, duplicate/contained-candidate pruning,
  count/unit label formatting, or inline rate discovery.
- Phase 5 extracted inline deterministic rate discovery into
  `deterministic_rate_extraction.py`. `deterministic_extraction.py` is now a
  compact rule-family orchestrator for cluster, seizure-free, rate, and unknown
  candidates, while rate-specific regex discovery, diary rate hooks, shorthand
  rate hooks, temporal rate arithmetic, and medication/dose distractor filtering
  live behind the rate extraction module. Behavior is preserved; Ruff, mypy,
  focused deterministic tests, and full pytest are green.
- Phase 5 has also extracted the remaining LLM structured-events semantic
  repair families into `llm_structured_repair_families.py`. The structured
  events runner now owns prompt/run/parse/report orchestration, while usual
  interval, breakthrough-after-seizure-free, non-epileptic override, residual
  jerk, post-change burst, dated-sequence, and elapsed-anchor repairs live in
  one typed helper module. Behavior is preserved; Ruff, mypy, focused
  structured-events tests, and full pytest are green.
- Phase 5 continued with a claim-table parser ownership split:
  `claim_table_parser.py` now owns the LLM-only claim-table Pydantic records,
  model-shape/schema repair, and selected-claim validation. The claim-table
  runner now owns prompt/run/scoring/report orchestration. Behavior is
  preserved; Ruff, mypy, focused claim-table tests, and full pytest are green.
- Phase 5 continued with a hybrid adjudicator parser ownership split:
  `hybrid_adjudicator_parser.py` now owns the hybrid adjudicator Pydantic
  decision record, model-shape/schema repair, parser-owned defaults, final-label
  repair, and scorable-label validation. The hybrid runner keeps prompt/run/
  scoring/report orchestration. Behavior is preserved; focused hybrid tests,
  Ruff, mypy, and full pytest are green.
- Phase 5 continued with a claim-table report ownership split:
  `claim_table_report.py` now owns the LLM-only claim-table Markdown report and
  review-table formatting helpers. The claim-table runner keeps prompt/run/
  scoring orchestration and exposes the same `write_report` entry point.
  Behavior is preserved; focused claim-table tests, Ruff, mypy, and full pytest
  are green.
- Phase 5 continued with a hybrid adjudicator report ownership split:
  `hybrid_adjudicator_report.py` now owns both hybrid adjudicator Markdown
  report writers and report-only interpretation/formatting helpers. The hybrid
  runner keeps prompt/run/scoring orchestration and exposes the same report
  entry points. Behavior is preserved; focused hybrid tests, Ruff, mypy, and
  full pytest are green.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Core LLM-only code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_only_claim_table_selector.py`
- Core hybrid code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid_rules_candidates_llm_adjudicator.py`
- Latest LLM-only claim-table selector run: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`
- Latest LLM-only claim-table selector full-validation review: `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`
- Latest hybrid rules-candidates LLM adjudicator run: `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`
- Latest hybrid rules-candidates LLM adjudicator review: `experiments/gan2026_arch2_validation250_v01_failure_review_2026-06-01.md`
- Latest hybrid rules-candidates LLM adjudicator full-validation review: `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`
- Latest v3 LLM-only claim-table selector review: `experiments/gan2026_section_claim_table_validation250_v3_failure_review_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen; put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic repair needs
   separate naming, ablation, and claim language.
3. Treat LLM-only claim-table selector v3 as a revise-only diagnostic.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Continue the codebase thermonuclear review Phase 5 behavior splits without
  changing scorer behavior: next candidates are the remaining large LLM
  structured-events runner, artifact-analysis helpers, or other ownership
  splits.
- Design hybrid rules-candidates LLM adjudicator v0.2 as a conservative/targeted adjudicator with
  deterministic fallback and named overreach-family gates; repeat 25/50/250.
- Design LLM-only claim-table selector v5 as claim-table plus constrained selector, with
  cluster-axis and boundary-state fields; repeat 25/50/250.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Add component ablations for hybrid rules-candidates LLM adjudicator v0.2 and
  LLM-only claim-table selector v5 before
  any holdout evaluation: raw/model, strict/schema repair, deterministic fallback
  or selector, and clean scorer-facing policy.
- Design LLM-replacement ablations for deterministic post-processing modules,
  reporting score, repair attribution, evidence validity, and replay variance.
- Consolidate any remaining saved-output replay helpers into dedicated artifact
  analysis modules so pipeline runners stay cache-first and live-run oriented.
- Extend named repair-mode metadata beyond structured-events where downstream
  repair layers can blur raw, strict, clean, selected-evidence, and hybrid
  attribution.
- Do not run LLM-only claim-table selector beyond 250 rows until v5 passes the 25/50 ladder
  and a written decision justifies another 250-row diagnostic.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Completed the LLM-only claim-table selector v4 250-row validation diagnostic;
  it reached 229/250 clean Purist but remains a revise signal due to parse/schema,
  cluster-axis, seizure-free/unknown boundary, denominator, and repair-attribution
  issues.
- 2026-06-01: Added and ran the hybrid rules-candidates LLM adjudicator
  harness through 25/50/250 validation; schema replay reached 243/250 Purist with
  0 parse failures and identified candidate-recall misses plus three adjudicator
  regressions as the next review surface.
- 2026-06-01: Ran full validation for hybrid rules-candidates LLM adjudicator v0.1
  and LLM-only claim-table selector v4. The hybrid clears 0.9 after schema replay
  but underperforms deterministic top; claim-table v4 falls to 0.704 clean Purist
  and is rejected for holdout.
- 2026-06-01: Fixed the v4 schema-output blocker, added prompt-policy IDs, and
  reran the corrected 25-row smoke at 25/25 raw and clean Purist/Pragmatic.
- 2026-06-01: Added a research-drift audit, completed the v2/v3 LLM-only claim-table selector
  ladder and review, and produced structured LLM repair-attribution artifacts.
- 2026-06-01: Added cross-architecture component-ablation tooling with JSON and
  Markdown outputs, covering deterministic rule-group ablations, saved LLM-first
  or structured LLM artifacts, and hybrid candidate-adjudicator deterministic-top versus
  adjudicator-final comparisons.
- 2026-06-01: Consolidated routine Gan LLM experiments into one
  `gan2026-llm-experiment --pipeline ...` CLI, including hybrid candidate adjudication, and
  removed artifact replay from the normal CLI surface in favor of DSPy cache
  reuse.
- 2026-06-01: Restored green tests after the codebase thermonuclear review's
  schema-repair finding: shared repair no longer adds parser-owned defaults,
  hybrid adjudicator defaulting is explicit, and broad validation CLI runs now
  require `--escalation-reason`.
- 2026-06-01: Removed unused seizure-specific schema types from `core.schemas`,
  added a task-neutral core-schema invariant test, and reduced `python -m mypy src`
  from 31 errors to clean.
- 2026-06-01: Added named repair modes to the structured-events LLM path and
  repair-ablation outputs, with tests proving clean scorer-facing mode does not
  silently use the hybrid semantic repair stack; Ruff, mypy, and full pytest are
  green.
- 2026-06-01: Began Phase 4 of the codebase thermonuclear review by extracting
  common Gan LLM run metadata into `run_metadata.py` and wiring direct-labeler,
  structured-events, claim-table selector, and hybrid adjudicator runners
  through it; focused tests, Ruff, mypy, and full pytest are green.
- 2026-06-01: Continued the codebase thermonuclear review consolidation by
  extracting common Gan LLM Markdown report provenance/write helpers into
  `reports.py` and wiring direct-labeler, structured-events, claim-table
  selector, and hybrid adjudicator reports through them; Ruff, mypy, and full
  pytest are green.
- 2026-06-01: Continued Phase 5 with behavior-preserving ownership splits:
  `label_parser.py`, `gold_policy.py`, `selected_evidence_derivation.py`,
  `benchmark_prediction_repair.py`, deterministic `temporal.py`,
  `deterministic_selection.py`, `llm_structured_temporal.py`, and
  `llm_structured_monthly_diary.py`. Each slice added or preserved focused
  ownership-boundary tests; Ruff, mypy, and full pytest are green after the
  latest slice.
- 2026-06-01: Continued Phase 5 by extracting deterministic V1 candidate
  discovery from `pipeline_v1.py` into `deterministic_extraction.py`, keeping
  compatibility re-exports for existing temporal-helper tests. Verification:
  `python -m ruff check .`, `python -m mypy src`,
  `python -m pytest tests/test_gan2026_pipeline_v1.py -q`, and
  `python -m pytest -q` are green (`595 passed`, 11 third-party DSPy
  deprecation warnings).
- 2026-06-01: Continued Phase 5 by extracting deterministic helper ownership
  from `deterministic_extraction.py` into `deterministic_text.py`,
  `deterministic_candidate_pruning.py`, and
  `deterministic_frequency_tokens.py`. The remaining extractor is 1191 lines,
  down from 1440 after the prior split. Verification: `python -m ruff check .`,
  `python -m mypy src`, `python -m pytest tests/test_gan2026_pipeline_v1.py -q`,
  and `python -m pytest -q` are green (`595 passed`, 11 third-party DSPy
  deprecation warnings).
- 2026-06-01: Continued Phase 5 by extracting inline deterministic rate
  discovery from `deterministic_extraction.py` into
  `deterministic_rate_extraction.py`. The extractor is now 283 lines and the
  rate module is 893 lines. Verification: `python -m ruff check .`,
  `python -m mypy src`, `python -m pytest tests/test_gan2026_pipeline_v1.py -q`,
  and `python -m pytest -q` are green (`595 passed`, 11 third-party DSPy
  deprecation warnings).
- 2026-06-01: Continued Phase 5 by extracting LLM structured-events semantic
  repair families from `llm_only_structured_events.py` into
  `llm_structured_repair_families.py`. The runner is now 1054 lines and the new
  repair-family module is 646 lines. Verification: `python -m ruff check .`,
  `python -m mypy src`,
  `python -m pytest tests/test_gan2026_llm_only_structured_events.py -q`, and
  `python -m pytest -q` are green (`595 passed`, 11 third-party DSPy
  deprecation warnings).
- 2026-06-01: Continued Phase 5 by extracting the LLM-only claim-table parser
  from `llm_only_claim_table_selector.py` into `claim_table_parser.py`. The
  runner is now 1018 lines and the parser module is 223 lines. Verification:
  `python -m ruff check .`, `python -m mypy src`,
  `python -m pytest tests/test_gan2026_llm_only_claim_table_selector.py -q`,
  and `python -m pytest -q` are green (`595 passed`, 11 third-party DSPy
  deprecation warnings).
- 2026-06-01: Continued Phase 5 by extracting the hybrid adjudicator parser
  from `hybrid_rules_candidates_llm_adjudicator.py` into
  `hybrid_adjudicator_parser.py`. The runner is now 1049 lines and the parser
  module is 102 lines. Verification: `python -m ruff check .`,
  `python -m mypy src`,
  `python -m pytest tests/test_gan2026_hybrid_rules_candidates_llm_adjudicator.py -q`,
  and `python -m pytest -q` are green (`595 passed`, 11 third-party DSPy
  deprecation warnings).
- 2026-06-01: Continued Phase 5 by extracting the LLM-only claim-table report
  writer from `llm_only_claim_table_selector.py` into `claim_table_report.py`.
  The runner is now 826 lines and the report module is 217 lines. Verification:
  `python -m ruff check .`, `python -m mypy src`,
  `python -m pytest tests/test_gan2026_llm_only_claim_table_selector.py -q`,
  and `python -m pytest -q` are green (`595 passed`, 11 third-party DSPy
  deprecation warnings).
- 2026-06-01: Continued Phase 5 by extracting the hybrid adjudicator report
  writers from `hybrid_rules_candidates_llm_adjudicator.py` into
  `hybrid_adjudicator_report.py`. The runner is now 843 lines and the report
  module is 218 lines. Verification: `python -m ruff check .`,
  `python -m mypy src`,
  `python -m pytest tests/test_gan2026_hybrid_rules_candidates_llm_adjudicator.py -q`,
  and `python -m pytest -q` are green (`595 passed`, 11 third-party DSPy
  deprecation warnings).

## Immediate Next Step

Continue the Phase 5 behavior-preserving splits from the remaining large
behavior modules, with the LLM structured-events runner or artifact-analysis
helpers as likely next ownership splits before returning to the validation-only
v0.2/v5 experiment cycle. Do not inspect holdout rows.
