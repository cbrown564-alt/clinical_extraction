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

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`, `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md`,
  `docs/research/gan2026_gold_normalization_policy_question_2026-06-01.md`,
  `docs/research/gan2026_clean_policy_attribution_note_2026-06-01.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`
- Current artifacts: clean policy freeze ladder, direct-citation row tables, and
  v0.2/v0.4 comparison under `experiments/`.

## Active Priorities

1. Keep deterministic V1 frozen and put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic-state-changing
   repair needs separate naming, ablation, and claim language.
3. Use `gan2026_clean_policy_freeze_ladder_v0` before promoting semantic repair,
   selector guidance, or a new architecture family.
4. Separate benchmark gold-normalization policy from clinical reasoning while
   preserving source-near traces.
5. Treat the clean scorer-facing policy as frozen unless a new direct-citation
   review justifies another family.

## Work Board

### Now

- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.
- Use direct-citation row tables as the gate for any future policy expansion.
- Choose the next LLM-first architecture comparison surface before any 250-row
  escalation.

### Next

- Keep upper-bound, diary, temporal, evidence-state, and cluster
  reconstruction behavior as named ablated modules.
- If useful, run a focused 25- or 50-row comparison for the selected next
  architecture before any 250-row escalation.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline permits.

### Done Recently

- 2026-06-01: Added staged structured LLM extraction, repair-family attribution
  audit, strict format-only replay, validation direct-citation row tables,
  v0.2/v0.4 comparison, and the living observatory notebook.
- 2026-06-01: Implemented table-backed clean scorer-facing policy families with
  tests; full suite passes (`560 passed`) and Ruff passes.
- 2026-06-01: Froze the clean scorer-facing policy with
  `gan2026_clean_policy_freeze_ladder_v0` and added the clean-policy
  attribution note.

## Immediate Next Step

Choose the next LLM-first architecture comparison and, if useful, run a focused
25- or 50-row development-split comparison before any 250-row escalation.
