# Gan 2026 LLM-Heavy Decision 0007 v1 Validation50 Interpretation

- Date: 2026-06-03
- Live artifact: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation50_gpt41mini_v1_live_2026-06-03.md`
- No-call replay artifact: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation50_gpt41mini_v1_replay_2026-06-03.md`
- Predeclaration: `experiments/gan2026_llm_heavy_decision0007_v1_validation50_predeclaration_2026-06-03.md`
- Decision: revise before validation250; do not promote from this validation50.

## Result Against Stop Rule

The live validation50 run completed with 50/50 structured outputs, 0 call
failures, and 0 adapter parse failures. A source-checked no-call replay repairs
malformed or case-only evidence copies, raising selected-evidence exactness from
47/50 live to 49/50 replay.

The candidate does not meet the predeclared validation50 promotion rule:

- selected evidence exact after repair: 49/50, passes the 48/50 minimum;
- selected fact trace mismatches: 0/50, passes;
- selected operand completeness: 49/50, passes the 48/50 minimum;
- raw parser-label Purist: 44/50, below the 47/50 minimum;
- mechanical adapter Purist: 44/50, below the 47/50 minimum;
- mechanical adapter raw-correct to wrong: 1/50, fails the required 0/50.

## Failure Rows

- `10`: upper-bound `≤ four per day` rendered as `multiple per day`, while gold
  is `4 per day`.
- `743`: raw label `multiple per shift` is scorer-compatible, but the typed
  frequency operands omit a denominator unit, so the mechanical adapter cannot
  render a label.
- `744`: selected weekday pattern is rendered as `4 to 5 per 7 day`, while gold
  expects broad `multiple per week`.
- `763`: selected label is correct, but selected evidence stitches
  non-contiguous note clauses; this remains the one true evidence exactness
  failure after repair.
- `816`: selected evidence includes both current monthly seizures and four
  seizures in 2017; the model chooses `4 per year` despite gold `1 per month`.
- `959`: `bimonthly` is represented as a range `1 to 2 per 1 to 2 month`,
  missing the benchmark convention `1 per 2 month`.
- `987`: `bimonthly` is represented as `2 per 1 to 2 month`, also missing the
  benchmark convention `1 per 2 month`.

## Next Repair

Revise the LLM-heavy contract before any validation250 run. The highest-yield
repairs are:

- bimonthly benchmark-convention operands;
- vague/weekday frequency operands such as `most weekdays`;
- source-evidence contiguity enforcement;
- upper-bound semantics for `≤ N per period`;
- adapter fallback behavior for raw-correct labels when operands are incomplete.
