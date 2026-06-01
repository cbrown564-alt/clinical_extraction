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

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/section_claim_table.py`
- Latest section-table run: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`
- Latest Architecture 2 run: `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`
- Latest Architecture 2 review: `experiments/gan2026_arch2_validation250_v01_failure_review_2026-06-01.md`
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

- Review Architecture 2 250-row failure families, especially candidate-recall
  misses and adjudicator regressions, before any prompt/candidate change.
- Review v4 250-row failure families and write a targeted v5 change hypothesis
  before any semantic prompt/repair change.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Implement a narrow v5 prompt/schema revision only after the failure-family
  review names the intended behavior and ablation category.
- Decide whether Architecture 2 should escalate to full validation after a
  written 250-row review, or whether to first revise the adjudicator prompt for
  broad-burden versus lower-count recent-event regressions.
- Move or remove `core.schemas.SeizureEvent` so `core/` stays task-neutral.
- Design LLM-replacement ablations for deterministic post-processing modules,
  reporting score, repair attribution, evidence validity, and replay variance.
- Add a validation-ladder guard or warning to `llm_pipeline_cli.py` for broad
  validation runs without an escalation reason.
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
- 2026-06-01: Fixed the v4 schema-output blocker, added prompt-policy IDs, and
  reran the corrected 25-row smoke at 25/25 raw and clean Purist/Pragmatic.
- 2026-06-01: Added a research-drift audit, completed the v2/v3 section-claim-table
  ladder and review, and produced structured LLM repair-attribution artifacts.

## Immediate Next Step

Review Architecture 2 250-row failure families and write the promote/revise
decision before full-validation or holdout use; do not inspect holdout rows.
