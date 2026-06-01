# Project Status

Last updated: 2026-06-01

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving transparent evidence
trails, ablations, and conservative benchmark language.

## Current Strategy

Use Gan 2026 as the first controlled extraction surface. Keep data loading,
label normalization, scoring, split discipline, and deterministic-rule behavior
explicit before optimizing LLM or DSPy components.

Deterministic V1 is frozen as a comparator. New candidate work should stay
LLM-first: model extraction and clinical selection produce the prediction, while
deterministic code is limited to validation, Gan-compatible normalization,
strict format repair, arithmetic repair, and named ablated modules.

## Recent Context

- Locked split `gan2026_split_v1`: 300 train, 750 validation, 450 holdout;
  LLM/DSPy work escalates 25 -> 50 -> 250 validation rows; test is not tuning.
- Deterministic V1 is frozen as a comparator: 0.9293/0.9387 validation and
  0.7600/0.7867 on its one locked-test Purist/Pragmatic evaluation.
- Structured v0.5 reached 675/750 Purist = 0.9000 on full validation, but audit
  classified it as repair-heavy hybrid behavior rather than clean LLM-first.
- Clean attribution separates raw LLM selection, strict format repair, and
  frozen scorer-facing policy: 34/50 raw, 41/50 strict, 43/50 clean Purist.
- `gan2026_section_claim_table_v0` passed its 25-row gate for a live 50-row
  comparison, but the 50-row artifact remains diagnostic: 50/50 structured,
  173/176 exact claim evidence, 48/50 selected evidence, raw/strict/clean
  Purist 25/38/43 of 50, and 20 raw scorer-format failures. Failure review
  kept v0 diagnostic and chose prompt/schema revision before any escalation.
- `gan2026_section_claim_table_v1` fixed v0 raw-label collapse on 50 validation
  rows: 50/50 structured, 151/153 exact claim evidence, 50/50 selected evidence,
  50/50 raw scorable, and raw/strict/clean Purist 47/50. It is not 250-ready:
  rows 187, 704, and 1165 expose prompt-fixable final-query conversions.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md`, clean-policy note,
  gold-normalization policy question, and next-architecture decision.
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/section_claim_table.py`
- Current artifacts: clean-policy ladder, direct-citation rows, comparisons,
  and section-claim-table 25/50-row diagnostics under `experiments/`.

## Active Priorities

1. Keep deterministic V1 frozen and put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic-state-changing
   repair needs separate naming, ablation, and claim language.
3. Keep section-claim-table 25/50 diagnostics ahead of any 250-row escalation.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Make a small section-claim-table v2 prompt/schema revision for v1 50-row
  misses: cluster cadence as ordinary frequency, `twice a month` as
  `2 per month`, and preserving `5 to 7 per 3 week` instead of vague multiple.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Freeze a single repair-heavy hybrid candidate and run a locked-test evaluation
  only once the protocol, artifacts, and no-retuning rule are recorded; compare
  test drift against deterministic V1's 0.9293 validation to 0.7600 test drop.
- Design LLM-replacement ablations for deterministic post-processing modules:
  selected-evidence derivation first, then temporal/event-state modules, with
  validation score, repair attribution, evidence validity, and variance across
  saved-output replays reported separately.
- Use direct-citation row tables as the gate for clean-policy expansion.
- Do not run section-claim-table 250 rows until a 50-row artifact passes the
  documented decision gate.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Added structured LLM extraction, repair attribution audits,
  direct-citation row tables, clean scorer-facing policy tests, and the living
  observatory notebook.
- 2026-06-01: Implemented `gan2026_section_claim_table_v0`, ran 25/50-row
  validation diagnostics, and reviewed 50-row failures in
  `experiments/gan2026_section_claim_table_validation50_failure_review_2026-06-01.md`;
  v0 stays diagnostic and v1 prompt/schema revision is next.
- 2026-06-01: Implemented `gan2026_section_claim_table_v1` prompt/schema and ran
  25/50-row validation diagnostics in
  `experiments/gan2026_section_claim_table_validation50_gpt41mini_v1_2026-06-01.md`;
  v1 fixed raw scorer-format collapse but needs a v2 final-query tweak before
  250-row escalation.

## Immediate Next Step

Implement the section-claim-table v2 prompt/schema tweak for rows 187, 704, and
1165, then rerun the 25/50 validation ladder before any 250-row escalation.
