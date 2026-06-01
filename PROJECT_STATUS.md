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
- The current report raises two generalisation questions: whether the
  repair-heavy hybrid holds on the 450-row locked test split, and whether LLM
  replacements for deterministic post-processing modules preserve validation
  gains without adding hidden variance.
- Clean attribution separates raw LLM selection, strict format repair, and
  frozen scorer-facing policy: 34/50 raw, 41/50 strict, 43/50 clean Purist.
- The frozen clean policy is limited to table-backed scorer-facing families;
  upper-bound, temporal, diary, evidence-state, and cluster-reconstruction
  behavior stay out of the clean path as named modules.
- `gan2026_section_claim_table_v0` schema/prompt tightening plus same-raw replay
  removed parse/schema blockers on the 25-row smoke: 25/25 structured, 87/89
  exact claim evidence, 23/25 selected evidence, raw/strict/clean Purist
  12/20/22 of 25. Keep diagnostic: 2 evidence/final-query rows and 12 raw
  scorer-format failures remain review gates before 50-row escalation.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md`,
  `docs/research/gan2026_gold_normalization_policy_question_2026-06-01.md`,
  `docs/research/gan2026_clean_policy_attribution_note_2026-06-01.md`,
  `docs/research/gan2026_next_architecture_decision_2026-06-01.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`
- Current artifacts: clean-policy ladder, direct-citation rows, comparisons,
  and section-claim-table 25-row smoke under `experiments/`.

## Active Priorities

1. Keep deterministic V1 frozen and put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic-state-changing
   repair needs separate naming, ablation, and claim language.
3. Keep `gan2026_section_claim_table_v0` diagnostic until the 25-row schema,
   evidence, and scorer-format failures are reviewed.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Make generalisation checks explicit: frozen-candidate holdout evaluation and
   LLM-vs-deterministic module replacement ablations should be planned before
   paper-facing claims.
6. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Review the replayed `gan2026_section_claim_table_v0` failure details for the
  remaining selected-evidence rows and raw scorer-format families.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Keep upper-bound, diary, temporal, evidence-state, and cluster
  reconstruction behavior as named ablated modules.
- Freeze a single repair-heavy hybrid candidate and run a locked-test evaluation
  only once the protocol, artifacts, and no-retuning rule are recorded; compare
  test drift against deterministic V1's 0.9293 validation to 0.7600 test drop.
- Design LLM-replacement ablations for deterministic post-processing modules:
  selected-evidence derivation first, then temporal/event-state modules, with
  validation score, repair attribution, evidence validity, and variance across
  saved-output replays reported separately.
- Use direct-citation row tables as the gate for clean-policy expansion.
- Decide whether the section-and-claim branch earns a 50-row comparison from
  the repaired 25-row artifact; do not jump directly to 250 rows.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Added structured LLM extraction, repair attribution audits,
  direct-citation row tables, v0.2/v0.4 comparisons, clean scorer-facing policy
  tests, and the living observatory notebook.
- 2026-06-01: Implemented `gan2026_section_claim_table_v0` with CLI/tests and a
  25-row validation smoke plus corrected no-call replay; branch remains
  diagnostic pending schema/prompt tightening.
- 2026-06-01: Tightened section-claim-table enum/list prompt guidance and
  schema-shape repair, added reviewable evidence/scorer-format failure details,
  and replayed the same 25 raw outputs with 0 parse/schema blockers.

## Immediate Next Step

Review the section-claim-table failure-detail table and decide whether the
remaining 2 evidence rows plus 12 raw scorer-format failures are acceptable for
a live 50-row comparison, or require another prompt-only replay first.
