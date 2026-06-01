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
  Purist 25/38/43 of 50, and 20 raw scorer-format failures. Do not escalate to
  250 before reviewing the 50-row failure families.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md`,
  `docs/research/gan2026_gold_normalization_policy_question_2026-06-01.md`,
  `docs/research/gan2026_clean_policy_attribution_note_2026-06-01.md`,
  `docs/research/gan2026_next_architecture_decision_2026-06-01.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`
- Current artifacts: clean-policy ladder, direct-citation rows, comparisons,
  and section-claim-table 25/50-row diagnostics under `experiments/`.

## Active Priorities

1. Keep deterministic V1 frozen and put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic-state-changing
   repair needs separate naming, ablation, and claim language.
3. Keep `gan2026_section_claim_table_v0` diagnostic until the 50-row failure
   families are reviewed.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Review the 50-row `gan2026_section_claim_table_v0` failure families,
  especially raw scorer-format labels, rows 212/665/790/959/1165, and the two
  selected-evidence misses, before any 250-row escalation.
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
- Decide whether the section-and-claim branch needs prompt/schema revision or a
  same-surface replay before a 250-row comparison.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Added structured LLM extraction, repair attribution audits,
  direct-citation row tables, v0.2/v0.4 comparisons, clean scorer-facing policy
  tests, and the living observatory notebook.
- 2026-06-01: Implemented and tightened `gan2026_section_claim_table_v0`, then
  promoted it from 25-row smoke to a live 50-row validation comparison; result
  remains diagnostic, not 250-ready.

## Immediate Next Step

Review the section-claim-table 50-row failure table and decide whether to revise
the prompt/schema for raw Gan-compatible labels and final-query edge cases, or
to keep the branch as a diagnostic comparator without further escalation.
