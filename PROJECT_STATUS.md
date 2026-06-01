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
- Section-claim-table v2 ran the 25/50 ladder: 50/50 structured, 167/169 exact
  claim evidence, 50/50 selected evidence, raw Purist 45/50, clean Purist 46/50.
  It fixed row 704 but not rows 187 or 1165, so v2 is not 250-ready.
- The v2 failure review localized rows 187 and 1165 to model final-query
  priority errors and row 869 to raw parser-ready wording. A narrow v3
  final-query priority prompt is justified before pausing for ablation work.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md` and clean-policy notes.
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/section_claim_table.py`
- Current artifacts: clean-policy ladder, direct-citation rows, comparisons,
  and section-claim-table 25/50-row diagnostics under `experiments/`.

## Active Priorities

1. Keep deterministic V1 frozen; put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic repair needs
   separate naming, ablation, and claim language.
3. Keep section-claim-table 25/50 diagnostics ahead of 250-row escalation.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Implement a narrow `gan2026_section_claim_table_v3` final-query priority
  prompt and rerun the 25-row validation smoke gate; do not use deterministic
  semantic selection or scorer-facing policy expansion to fix rows 187/1165.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Design LLM-replacement ablations for deterministic post-processing modules,
  reporting score, repair attribution, evidence validity, and replay variance.
- Freeze a single repair-heavy hybrid candidate for locked-test evaluation only
  once the protocol, artifacts, and no-retuning rule are recorded.
- Use direct-citation row tables as the gate for clean-policy expansion.
- Do not run section-claim-table 250 rows until a 50-row artifact passes the
  documented decision gate.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Wrote
  `experiments/gan2026_section_claim_table_validation50_v2_failure_review_2026-06-01.md`;
  decision is a narrow v3 final-query priority prompt, still restarting at the
  25-row validation smoke gate and not promoting v2 to 250 rows.
- 2026-06-01: Implemented section-claim-table v2 and ran 25/50-row diagnostics;
  v2 fixed row 704 but remains diagnostic.
- 2026-06-01: Added structured LLM extraction, repair-attribution audits,
  direct-citation tables, clean-policy tests, v0/v1 diagnostics, and observatory.

## Immediate Next Step

Patch `gan2026_section_claim_table_v3` with the reviewed final-query priorities,
then run the 25-row validation smoke gate and compare rows 187, 869, 1165, and
704 before considering another 50-row diagnostic.
