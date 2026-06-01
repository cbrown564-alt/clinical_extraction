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

- Locked split `gan2026_split_v1`: 300 train, 750 validation, 450 final holdout.
  LLM/DSPy work escalates 25 -> 50 -> 250 validation rows; the test split has
  been touched once and must not become a tuning surface.
- Deterministic V1 is a frozen comparator: 0.9293/0.9387 validation and
  0.7600/0.7867 on its one locked-test Purist/Pragmatic evaluation.
- Structured v0.5 reached 675/750 Purist = 0.9000 on full validation, but audit
  classified it as repair-heavy hybrid behavior, not clean LLM-first completion.
- Clean claim language treats raw LLM final-label selection as the attribution
  baseline; selected-evidence repair, diary arithmetic, cluster conversion, and
  clinical-selection overrides are named deterministic modules.
- `gan2026_clean_policy_freeze_ladder_v0`: same-raw-output validation replay
  reports raw, strict format-only, and frozen clean policy separately. On 50 rows:
  raw 34/50 Purist (0.6800), strict 41/50 (0.8200), clean 43/50 (0.8600),
  0 clean parse failures, 50/50 exact evidence, 2 clean improvements, 0
  regressions.
- The frozen clean scorer-facing policy includes only the table-backed families
  for vague quantity with explicit denominator, period shorthand, cluster syntax
  grammar, and single total/window phrasing. Upper-bound, temporal, diary,
  evidence-state, and cluster-reconstruction behavior stay out of the clean path.
- v0.2/v0.4 250-row comparison rejected broader v0.4 selector guidance:
  v0.4 fixed 1 v0.2 miss but introduced 5 additional Purist misses.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`, `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md`,
  `docs/research/gan2026_gold_normalization_policy_question_2026-06-01.md`
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

- Draft the short attribution note explaining why further score gains should
  come from model selection/prompting or named ablations, not clean-policy creep.
- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.
- Use direct-citation row tables as the gate for any future policy expansion.

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
  `gan2026_clean_policy_freeze_ladder_v0`; next move is the attribution note.

## Immediate Next Step

Draft the attribution note that locks clean scorer-facing normalization as a
frozen scorer policy and routes further score gains to model selection/prompting
or explicitly named ablated modules.
