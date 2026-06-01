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
- Section-claim-table v3 passed the 50-row gate, then hit a revise-only 250-row
  result: 248/250 structured, 0 call failures, 217/250 raw Purist, 218/250 clean
  Purist, and 224/250 clean Pragmatic.
- The v3 250-row artifact is a revise signal, not a promotion signal; the family
  review recommends a narrow v4 restart at the 25/50 validation gate.
- A research-drift audit found the project mostly aligned, with watches on prompt
  taxonomy, hybrid repair claims, one core/task boundary leak, and CLI ladder
  enforcement.
- Section-claim-table v4 now carries an explicit prompt-policy taxonomy in its
  prompt payload and run metadata so Gan-facing prompt fixes are named,
  categorized, and ablatable like controlled variables.
- Section-claim-table v4 schema-output blocker is fixed. The corrected 25-row
  validation smoke passed: 25/25 structured, 0 call/schema failures, 25/25 raw
  and clean Purist/Pragmatic, 25/25 selected evidence exact, and 65/66 claim
  evidence exact; one non-selected row-182 claim evidence mismatch remains
  reviewable.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/section_claim_table.py`
- Latest review: `experiments/gan2026_section_claim_table_validation250_v3_failure_review_2026-06-01.md`
- Latest run: `experiments/gan2026_section_claim_table_validation25_gpt41mini_v4_2026-06-01.md`
- Drift audit: `docs/research/gan2026_research_drift_audit_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen; put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic repair needs
   separate naming, ablation, and claim language.
3. Treat section-claim-table v3 as a revise-only diagnostic; no further scale-up
   until a revised candidate passes the 25/50 gate.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Run and review the section-claim-table v4 50-row validation gate with 25-row
  output reuse.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Move or remove `core.schemas.SeizureEvent` so `core/` stays task-neutral.
- Add a validation-ladder guard or warning to `llm_pipeline_cli.py` for broad
  validation runs without an escalation reason.
- Design LLM-replacement ablations for deterministic post-processing modules,
  reporting score, repair attribution, evidence validity, and replay variance.
- Use direct-citation row tables as the gate for clean-policy expansion.
- Do not run section-claim-table beyond 250 rows until v4 passes the 50-row gate
  and a written decision gate justifies another 250-row diagnostic.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Fixed the v4 schema-output blocker by removing an output-tempting
  schema note, reran the corrected 25-row validation smoke, and recorded a clean
  25/25 raw and clean Purist/Pragmatic result with one non-selected claim
  evidence exactness issue.
- 2026-06-01: Added section-claim-table v4 prompt-policy IDs for schema, evidence,
  Gan label formatting, cluster, selection, boundary, exclusion, and maximum-burden
  prompt behavior.
- 2026-06-01: Added a research-drift audit and turned the findings into board
  tasks: v4 schema blocker, prompt taxonomy, core-boundary cleanup, CLI ladder
  guard, and continued hybrid repair claim discipline.
- 2026-06-01: Completed the v2/v3 section-claim-table ladder, v3 250-row family
  review, structured LLM repair-attribution audits, clean-policy diagnostics, and
  v0/v1 comparison artifacts.

## Immediate Next Step

Run the section-claim-table v4 50-row validation gate with 25-row output reuse,
then review row-level failures before deciding whether another 250-row diagnostic
is justified.
