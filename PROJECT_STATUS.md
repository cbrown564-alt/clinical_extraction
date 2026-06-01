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

Deterministic V1 is frozen as a controlled comparator. New candidate work should
stay LLM-first: model extraction and clinical selection produce the prediction,
while deterministic code is limited to validation, Gan-compatible normalization,
strict benchmark-format repair, arithmetic repair, and named ablated modules.

## Recent Context

- Locked split `gan2026_split_v1`: 300 train, 750 validation, 450 final holdout;
  LLM/DSPy work escalates 25 -> 50 -> 250 validation rows, and test must not
  become a tuning surface.
- Deterministic V1 is frozen as a comparator: 0.9293/0.9387 validation and
  0.7600/0.7867 on its one locked-test Purist/Pragmatic evaluation.
- Structured v0.5 reached 675/750 Purist = 0.9000 on full validation, but audit
  classified it as repair-heavy hybrid behavior rather than clean LLM-first.
- Clean attribution now separates raw LLM selection, strict format repair, and
  frozen scorer-facing policy. The 50-row freeze ladder was 34/50 raw, 41/50
  strict, 43/50 clean Purist, with 50/50 exact evidence and no clean regressions.
- The frozen clean policy is limited to table-backed scorer-facing families;
  upper-bound, temporal, diary, evidence-state, and cluster-reconstruction
  behavior stay out of the clean path as named modules.
- Next architecture comparison: `gan2026_section_claim_table_v0`, a flat
  section-and-claim-table LLM-first diagnostic branch documented in
  `docs/research/gan2026_next_architecture_decision_2026-06-01.md`.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`,
  `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md`,
  `docs/research/gan2026_gold_normalization_policy_question_2026-06-01.md`,
  `docs/research/gan2026_clean_policy_attribution_note_2026-06-01.md`,
  `docs/research/gan2026_next_architecture_decision_2026-06-01.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`
- Current artifacts: clean policy freeze ladder, direct-citation row tables, and
  v0.2/v0.4 comparison under `experiments/`.

## Active Priorities

1. Keep deterministic V1 frozen and put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic-state-changing
   repair needs separate naming, ablation, and claim language.
3. Build the next comparison as `gan2026_section_claim_table_v0`; start with a
   25-row validation smoke run before any 50- or 250-row escalation.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Implement the `gan2026_section_claim_table_v0` pipeline as a flat claim table
  plus model query selector.
- Run the first 25-row validation smoke comparison only after report metadata
  can separate claim extraction, final query, repair, and scorer failures.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.

### Next

- Keep upper-bound, diary, temporal, evidence-state, and cluster
  reconstruction behavior as named ablated modules.
- Use direct-citation row tables as the gate for any future clean-policy
  expansion.
- Decide whether the section-and-claim branch earns a 50-row comparison from
  the 25-row artifact; do not jump directly to 250 rows.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Added staged structured LLM extraction, repair attribution audits,
  strict replay, direct-citation row tables, v0.2/v0.4 comparison, and the
  living observatory notebook.
- 2026-06-01: Implemented and froze table-backed clean scorer-facing policy
  families with tests; full suite passes (`560 passed`) and Ruff passes.
- 2026-06-01: Selected `gan2026_section_claim_table_v0` as the next LLM-first
  architecture comparison surface.

## Immediate Next Step

Implement the `gan2026_section_claim_table_v0` schema/pipeline and run a 25-row
validation smoke comparison with component-localized failure reporting before
any 50- or 250-row escalation.
