# Project Status

Last updated: 2026-06-01

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving transparent evidence
trails, ablations, and conservative benchmark language.

## Current Strategy

Use Gan 2026 as the first controlled extraction surface. Deterministic V1 is
frozen as a comparator; new candidate work should stay LLM-first, with
deterministic code limited to validation, Gan-compatible normalization, strict
format repair, arithmetic repair, and named ablated modules.

## Recent Context

- Locked split `gan2026_split_v1`: 300 train, 750 validation, 450 holdout;
  LLM/DSPy work escalates 25 -> 50 -> 250 validation rows; test is not tuning.
- Deterministic V1 is frozen as a comparator: 0.9293/0.9387 validation and
  0.7600/0.7867 on its one locked-test Purist/Pragmatic evaluation.
- Structured v0.5 reached 675/750 Purist = 0.9000 on full validation, but audit
  classified it as repair-heavy hybrid behavior rather than clean LLM-first.
- Section-claim-table v3 hit a revise-only 250-row result: 248/250 structured,
  217/250 raw Purist, 218/250 clean Purist, and 224/250 clean Pragmatic.
- Section-claim-table v4 completed its 250-row validation diagnostic: 248/250
  structured, 0 call failures, 2 parse/schema failures, 226/250 raw Purist,
  229/250 clean Purist, 236/250 clean Pragmatic, and 247/250 selected evidence
  exact. It clears 0.9000 as a development diagnostic but is not a promotion
  signal because 32 rows change downstream and failure families remain.
- A retry variant differed by one row (230/250 clean Purist), so treat v4 as a
  revise signal with small live-tail variance rather than a scale-up candidate.
- A no-call schema replay of section-claim-table v4 repaired non-semantic output
  shape issues: 250/250 structured, 0 parse/schema failures, 231/250 clean
  Purist, and 238/250 clean Pragmatic. This improves the architecture gate but
  does not change the revise decision because semantic failure families remain.
- Architecture 2 (deterministic candidates + LLM adjudicator) now has a split-wide
  runner and validation ladder artifacts. Its 250-row schema replay reached
  243/250 Purist and 244/250 Pragmatic with 0 parse failures, candidate-set
  Purist recall 246/250, and three deterministic-correct to adjudicator-wrong
  regressions. It is the strongest current validation candidate but still needs
  failure review and ablations before any holdout freeze.
- Architecture 2 full-validation schema replay reached 680/750 Purist and
  689/750 Pragmatic with 0 parse failures, but it underperformed deterministic
  top on the same rows (697/750 Purist) because the adjudicator had 24
  deterministic-correct regressions against 7 corrections. Revise before
  holdout; v0.1 is not a frozen test candidate.
- Section-claim-table v4 full validation collapsed to 528/750 clean Purist and
  577/750 clean Pragmatic. Reject v4 for holdout and redesign v5 around
  cluster-axis preservation, boundary-state selection, and selector ablation.
- Added unified component-ablation tooling for the three key architecture
  families: deterministic-only, LLM-then-deterministic, and deterministic-then-LLM.
  It normalizes deterministic replay and saved JSONL artifacts into shared
  condition summaries for attribution, repair, and adjudicator comparisons.
- Routine LLM experiments now use one cache-first CLI,
  `gan2026-llm-experiment`, with `--pipeline` selection. DSPy cache is on by
  default; saved-output replay is reserved for explicit offline artifact
  analysis rather than normal experiment execution.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/section_claim_table.py`
- Latest section-table run: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`
- Latest section-table full-validation review: `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`
- Latest Architecture 2 run: `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`
- Latest Architecture 2 review: `experiments/gan2026_arch2_validation250_v01_failure_review_2026-06-01.md`
- Latest Architecture 2 full-validation review: `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`
- Latest v3 review: `experiments/gan2026_section_claim_table_validation250_v3_failure_review_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen; put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic repair needs
   separate naming, ablation, and claim language.
3. Treat section-claim-table v3 as a revise-only diagnostic.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Design Architecture 2 v0.2 as a conservative/targeted adjudicator with
  deterministic fallback and named overreach-family gates; repeat 25/50/250.
- Design section-claim-table v5 as claim-table plus constrained selector, with
  cluster-axis and boundary-state fields; repeat 25/50/250.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Add component ablations for Architecture 2 v0.2 and section-table v5 before
  any holdout evaluation: raw/model, strict/schema repair, deterministic fallback
  or selector, and clean scorer-facing policy.
- Move or remove `core.schemas.SeizureEvent` so `core/` stays task-neutral.
- Design LLM-replacement ablations for deterministic post-processing modules,
  reporting score, repair attribution, evidence validity, and replay variance.
- Add a validation-ladder guard or warning to `llm_pipeline_cli.py` for broad
  validation runs without an escalation reason.
- Consolidate any remaining saved-output replay helpers into dedicated artifact
  analysis modules so pipeline runners stay cache-first and live-run oriented.
- Do not run section-claim-table beyond 250 rows until v5 passes the 25/50 ladder
  and a written decision justifies another 250-row diagnostic.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Completed the section-claim-table v4 250-row validation diagnostic;
  it reached 229/250 clean Purist but remains a revise signal due to parse/schema,
  cluster-axis, seizure-free/unknown boundary, denominator, and repair-attribution
  issues.
- 2026-06-01: Added and ran the Architecture 2 split-wide candidate-adjudicator
  harness through 25/50/250 validation; schema replay reached 243/250 Purist with
  0 parse failures and identified candidate-recall misses plus three adjudicator
  regressions as the next review surface.
- 2026-06-01: Ran full validation for Architecture 2 v0.1 and section-table v4.
  Architecture 2 clears 0.9 after schema replay but underperforms deterministic
  top; section-table v4 falls to 0.704 clean Purist and is rejected for holdout.
- 2026-06-01: Fixed the v4 schema-output blocker, added prompt-policy IDs, and
  reran the corrected 25-row smoke at 25/25 raw and clean Purist/Pragmatic.
- 2026-06-01: Added a research-drift audit, completed the v2/v3 section-claim-table
  ladder and review, and produced structured LLM repair-attribution artifacts.
- 2026-06-01: Added cross-architecture component-ablation tooling with JSON and
  Markdown outputs, covering deterministic rule-group ablations, saved LLM-first
  or structured LLM artifacts, and Architecture 2 deterministic-top versus
  adjudicator-final comparisons.
- 2026-06-01: Consolidated routine Gan LLM experiments into one
  `gan2026-llm-experiment --pipeline ...` CLI, including Architecture 2, and
  removed artifact replay from the normal CLI surface in favor of DSPy cache
  reuse.

## Immediate Next Step

Implement the next validation-only revision cycle: Architecture 2 v0.2
conservative adjudication and section-table v5 constrained selection. Do not
inspect holdout rows.
