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
- Section-claim-table v3 passed the 50-row decision gate after the no-call
  rationale-repair replay, then ran the 250-row validation diagnostic with the
  first 50 raw outputs reused. The 250-row result is below target: 248/250
  structured, 0 call failures, 217/250 raw Purist, 218/250 clean Purist, and
  224/250 clean Pragmatic.
- The v3 250-row artifact is a revise signal, not a promotion signal. Failure
  families include cluster-burden under-selection, unknown/no-reference versus
  seizure-free confusion, counted-window mismatches, two schema enum failures,
  and persistent evidence exactness drift on a small slice.
- The 250-row family review recommends a narrow section-claim-table v4 rather
  than promotion or rejection: preserve explicit cluster labels, additive counts,
  schema enums, and no-reference/seizure-free boundaries; restart at 25/50 rows.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md` and clean-policy notes.
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/section_claim_table.py`
- Latest review: `experiments/gan2026_section_claim_table_validation250_v3_failure_review_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen; put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic repair needs
   separate naming, ablation, and claim language.
3. Treat section-claim-table v3 as a revise-only diagnostic; no further scale-up
   or holdout talk until a revised candidate passes the 25/50 gate.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Implement a narrow section-claim-table v4 prompt/schema update from the
  250-row family review, then restart at the 25-row validation gate.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Design LLM-replacement ablations for deterministic post-processing modules,
  reporting score, repair attribution, evidence validity, and replay variance.
- Use direct-citation row tables as the gate for clean-policy expansion.
- Do not run section-claim-table beyond 250 rows until the 250-row failure
  families are reviewed and a revised candidate passes the 25/50 gate again.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Reviewed v3 250-row misses by family and chose a narrow v4 restart
  over promotion or rejection; keep clean scorer-facing policy frozen and restart
  at the 25/50 validation gate.
- 2026-06-01: Ran the v3 50-row review, no-call rationale-repair replay, and
  250-row diagnostic; v3 fixed the reviewed 50-row failures but reached only
  218/250 clean Purist at 250 rows, so it should be revised rather than promoted.
- 2026-06-01: Wrote the v2 failure review, implemented section-claim-table v3,
  and reran the 25/50 validation ladder.
- 2026-06-01: Added structured LLM extraction, repair-attribution audits,
  direct-citation tables, clean-policy tests, v0/v1 diagnostics, and observatory.

## Immediate Next Step

Implement section-claim-table v4 as a narrow prompt/schema update from the
250-row family review, then run the 25-row validation gate before any further
scale-up.
