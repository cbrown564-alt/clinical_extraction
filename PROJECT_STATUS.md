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
- The frozen clean policy is limited to table-backed scorer-facing families;
  upper-bound, temporal, diary, evidence-state, and cluster-reconstruction
  behavior stay out of the clean path as named modules.
- `gan2026_section_claim_table_v0` has schema/pipeline/CLI plus a 25-row smoke:
  21/25 structured, 73/75 exact claim evidence, raw/strict/clean Purist
  9/16/18 of 25. Keep diagnostic: 4 parse/schema, 6 final-query/evidence, and
  15 raw scorer-format failures block 50-row escalation.

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
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Review the 25-row `gan2026_section_claim_table_v0` failure rows and tighten
  schema/prompt guidance for remaining enum/list aliases and selected evidence.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Keep upper-bound, diary, temporal, evidence-state, and cluster
  reconstruction behavior as named ablated modules.
- Use direct-citation row tables as the gate for clean-policy expansion.
- Decide whether the section-and-claim branch earns a 50-row comparison from
  the 25-row artifact; do not jump directly to 250 rows.
- Re-run the same 25-row raw-output replay after schema/prompt tightening before
  any new live 50-row comparison.

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

## Immediate Next Step

Inspect the section-claim-table 25-row failure rows and update the prompt/schema
repair boundary so enum/list aliases, selected evidence, and raw scorer-format
failures are reviewable before deciding on any 50-row escalation.
