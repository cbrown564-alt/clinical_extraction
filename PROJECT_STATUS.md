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
- Clean attribution separates raw LLM selection, strict format repair, and
  frozen scorer-facing policy: 34/50 raw, 41/50 strict, 43/50 clean Purist.
- Section-claim-table v3 hit a revise-only 250-row result: 248/250 structured,
  217/250 raw Purist, 218/250 clean Purist, and 224/250 clean Pragmatic.
- A research-drift audit found the project mostly aligned, with watches on prompt
  taxonomy, hybrid repair claims, one core/task boundary leak, and CLI ladder
  enforcement.
- Section-claim-table v4 passed the 50-row architecture gate with 25-row output
  reuse: 50/50 structured, 0 call/schema failures, 49/50 raw/clean Purist,
  50/50 raw/clean Pragmatic, 50/50 selected evidence exact, and 132/135 claim
  evidence exact.
- The v4 50-row miss is row 1046, where the model collapsed the uncertain range
  `3 or 5 seizures last month` to `5 per month` instead of the gold interval
  `3 to 5 per month`; treat interval preservation under uncertainty as a 250-row
  watch item, not a scorer-policy change.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/section_claim_table.py`
- Latest gated run: `experiments/gan2026_section_claim_table_validation50_gpt41mini_v4_2026-06-01.md`
- Latest v3 review: `experiments/gan2026_section_claim_table_validation250_v3_failure_review_2026-06-01.md`
- Drift audit: `docs/research/gan2026_research_drift_audit_2026-06-01.md`

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

- Run one section-claim-table v4 250-row validation diagnostic with 50-row output
  reuse, preserving the frozen clean scorer-facing policy.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Review v4 250-row row-level failures before any prompt or repair change,
  especially uncertain count ranges that may collapse intervals to maximum burden.
- Move or remove `core.schemas.SeizureEvent` so `core/` stays task-neutral.
- Design LLM-replacement ablations for deterministic post-processing modules,
  reporting score, repair attribution, evidence validity, and replay variance.
- Add a validation-ladder guard or warning to `llm_pipeline_cli.py` for broad
  validation runs without an escalation reason.
- Use direct-citation row tables as the gate for clean-policy expansion.
- Do not run section-claim-table beyond 250 rows until the v4 250-row diagnostic
  has a written review and decision.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Ran and reviewed the section-claim-table v4 50-row validation
  gate with 25-row reuse; the report records a pass decision for one 250-row
  diagnostic, with row 1046 interval collapse as the main watch item.
- 2026-06-01: Fixed the v4 schema-output blocker, added prompt-policy IDs, and
  reran the corrected 25-row smoke at 25/25 raw and clean Purist/Pragmatic.
- 2026-06-01: Added a research-drift audit, completed the v2/v3 section-claim-table
  ladder and review, and produced structured LLM repair-attribution artifacts.

## Immediate Next Step

Run one section-claim-table v4 250-row validation diagnostic with 50-row output
reuse, then review row-level failures before any prompt, repair, policy, or
scale-up decision.
