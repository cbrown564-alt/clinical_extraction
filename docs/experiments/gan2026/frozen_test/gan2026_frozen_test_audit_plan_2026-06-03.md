# Gan 2026 Frozen-Test Audit Plan

- Date: 2026-06-03
- Candidate: `hybrid_parallel_state_candidate_reasoner`
- Prompt/version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split manifest: `gan2026_split_v1`
- Test surface: locked `test` split, 450 rows
- Current frozen-context commit: `f2256a3` plus the reporting-only gate-label fix in this work item
- Validation basis: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_safety_floor_interpretation_2026-06-03.md`

## Status

This plan permits a future frozen-test generalization audit only after the
candidate implementation, scorer, repair policy, model configuration, artifact
paths, and inspection policy below are frozen. The current validation result is
a hybrid deterministic-safety-floor development result, not a benchmark claim and
not an LLM-first claim.

## Thermonuclear Review

Reviewed scope:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/hybrid_parallel_state_candidate_reasoner.py`
- `tests/test_gan2026_hybrid_parallel_state_candidate_reasoner.py`
- validation750 safety-floor reports and interpretation artifacts
- split and saturated-validation protocol docs

Finding fixed before this plan:

- Full validation reports reused the validation25 smoke-gate label and could say
  `promote_to_50` on a 750-row development artifact. This was a reporting and
  claim-language risk, not a scoring change. The summary now exposes
  `run_gate_outcome` with size-aware labels while preserving
  `validation25_smoke_outcome` as a compatibility alias.

Residual risks:

- The final prediction-bearing behavior is effectively the deterministic top
  candidate whenever the adjudicator disagrees after repair. Holdout language
  must describe this as a deterministic-safety-floor hybrid audit.
- The LLM candidate selector still has 11 validation750 schema failures. This
  does not block the safety-floor audit if it remains a sidecar, but it blocks
  LLM-first or LLM-heavy claims.
- Remaining validation misses are known development failures. They may define
  post-hoc interpretation categories, but they must not be used to alter the
  frozen test policy.

## Frozen Inputs

Before running locked test, record these exact values in the run artifact:

- repo commit hash and dirty-worktree status;
- `gan2026_split_v1` manifest path and hash;
- scorer module/version and Purist/Pragmatic normalization policy;
- candidate module path and prompt version;
- model id, temperature, max tokens, DSPy cache setting, API base, and run mode;
- deterministic safety-floor policy enabled exactly as validation750 v2 replay;
- no additional prompt, parser, schema-repair, scorer, evidence, or deterministic
  rule changes after this plan unless the audit is explicitly cancelled.

## Pre-Run Checks

Required checks before any locked-test command:

- `python -m pytest tests/test_gan2026_hybrid_parallel_state_candidate_reasoner.py`
- a clean `git status --short`, or an explicit list of frozen uncommitted files;
- artifact paths selected before execution, including JSONL, Markdown report, and
  any live-call log;
- confirmation that no test row text, label, or row-level failure has been
  inspected for tuning.

## Allowed Test Readout

After the locked-test run, the first readout may include only:

- aggregate Purist and Pragmatic for each named score layer;
- counts for structured LLM candidates, structured adjudicator records, call
  failures, parse/schema failures, exact selected evidence, valid source ids,
  deterministic-correct regressions, adapter raw-correct-to-wrong, and
  deterministic safety-floor fallbacks;
- predeclared provenance counts by selected source type;
- predeclared slice aggregates listed below.

## Predeclared Slices

Slices may be computed on locked test only from gold metadata or source-text
patterns declared here, not from inspecting test failures:

- label kind: frequency, seizure-free, unknown;
- numeric rate labels versus vague rate labels;
- seizure-free duration labels shorter than one year versus one year or longer;
- rows with explicit current-state markers such as `current`, `currently`,
  `now`, or `at present`;
- rows with historical/negated distractor markers such as `previously`,
  `history of`, `no`, `denies`, or `last`;
- rows where the deterministic safety floor fires versus rows where it does not.

Report each slice with row count, Purist, Pragmatic, evidence exactness, source-id
validity, and deterministic-correct regression count. Do not list test row ids in
the first readout unless the audit is explicitly moved into post-hoc final
evaluation analysis.

## Stop Rules

Promote as a final holdout result only if:

- the run was executed under the frozen inputs above;
- no locked-test row-level inspection occurred before aggregate and slice
  summaries were recorded;
- selected evidence and source-id validity remain audit-grade;
- deterministic-correct regressions remain zero or are fully explained as
  scorer/contract defects without tuning.

Reject or mark revise-only if:

- the run needs any code, prompt, scorer, repair, model, or threshold change;
- evidence/source-id validity breaks in a systemic way;
- the result requires row-level locked-test tuning to understand or improve it;
- claim language would need to hide that the final policy is the deterministic
  safety floor.

Any change after a rejected/revise-only holdout starts a new validation-cycle
candidate. It must not be patched directly against locked-test failures.
