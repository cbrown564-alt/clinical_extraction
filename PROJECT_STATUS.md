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
  LLM/DSPy work escalates 25 -> 50 -> 250 validation rows.
- Deterministic V1 is a frozen comparator: 0.9293/0.9387 validation
  Purist/Pragmatic, but 0.7600/0.7867 on its one locked-test evaluation.
- Structured v0.5 reached 675/750 Purist = 0.9000 on full validation, but audit
  classified it as repair-heavy hybrid behavior, not clean LLM-first completion.
- Clean claim language treats raw LLM final-label selection as the attribution
  baseline; selected-evidence repair, diary arithmetic, cluster conversion, and
  clinical-selection overrides are named deterministic modules.
- `gan2026_clean_attribution_format50_v0`: raw 34/50 Purist (0.6800), strict
  format-only 41/50 (0.8200), 17 surface repairs, 7 improvements, 0 regressions,
  50/50 exact evidence, and 3 strict parse failures.
- `gan2026_clean_scorer_policy_format50_v0`: clean scorer-facing policy reached
  43/50 Purist (0.8600), 46/50 Pragmatic (0.9200), 0 parse failures, and 50/50
  exact evidence, while bimonthly model-selection misses remain unresolved.
- v0.2/v0.4 250-row error-family comparison found no reason to broaden v0.4
  selector guidance: v0.4 fixed 1 v0.2 miss but introduced 5 additional Purist
  misses; use clean table-backed scorer policy next.
- The clean scorer-facing policy registry now includes the table-backed
  validation families for vague quantity with explicit denominator, period
  shorthand, cluster syntax grammar, and single total/window phrasing, with
  boundary tests that keep upper-bound, temporal, diary, evidence-state, and
  cluster-reconstruction behavior out of the clean path.
- The table-backed implementation intentionally generalizes within the approved
  policy families only; treat the clean scorer-facing policy as frozen unless a
  new direct-citation review justifies another family.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`, `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md`,
  `docs/research/gan2026_gold_normalization_policy_question_2026-06-01.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`
- Current artifacts: clean attribution, clean scorer policy, direct-citation row
  tables, and v0.2/v0.4 comparison under `experiments/`.

## Active Priorities

1. Keep deterministic V1 frozen and put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic-state-changing
   repair needs separate naming, ablation, and claim language.
3. Use `gan2026_clean_attribution_format50_v0` before promoting semantic repair,
   selector guidance, or a new architecture family.
4. Separate benchmark gold-normalization policy from clinical reasoning:
   preserve source-near traces, but match Gan scoring conventions when they are
   explicit and consistent.
5. Maintain conservative benchmark language; the test split has been touched
   once and must not become a tuning surface.
6. Freeze the clean scorer-facing policy before measuring impact; next work
   should quantify attribution, not chase additional validation F1.

## Work Board

### Now

- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.
- Freeze the current clean scorer-facing policy and run a focused 25- or 50-row
  comparison that reports raw, strict format-only, and clean policy separately.
- Use direct-citation row tables as the gate for any future policy expansion.

### Next

- Keep upper-bound, diary, temporal, evidence-state, and cluster
  reconstruction behavior as named ablated modules.
- Draft the short attribution note that explains why further score gains should
  come from model selection/prompting or named ablations, not clean-policy creep.
- If useful, run a focused 25- or 50-row comparison for the selected next
  architecture before any 250-row escalation.

### Blocked

- Final benchmark-comparison language is blocked until the replication surface
  and paper comparability are explicit.
- Further holdout analysis is blocked by locked-test discipline.

### Done Recently

- 2026-06-01: Added staged structured LLM extraction, repair-family attribution
  audit, strict format-only replay, and the living observatory notebook.
- 2026-06-01: Added the first clean scorer-facing gold-policy slice, validation
  direct-citation row tables, and v0.2/v0.4 error-family comparison; broader
  v0.4 selector guidance is rejected as the next step.
- 2026-06-01: Implemented table-backed clean scorer-facing policy families with
  tests; full suite passes (`560 passed`) and Ruff passes.
- 2026-06-01: Recorded that the implementation generalizes only within approved
  scorer-facing families; next moves are freeze, ablate, and report attribution.

## Immediate Next Step

Freeze the current clean scorer-facing policy, then run the focused clean-policy
comparison on the validation ladder with raw, strict format-only, and clean
policy results reported separately.
