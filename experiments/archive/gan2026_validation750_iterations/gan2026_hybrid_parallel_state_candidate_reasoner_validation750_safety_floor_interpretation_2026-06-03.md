# Gan 2026 Hybrid Parallel State Candidate Reasoner Validation750 Safety-Floor Interpretation

- Date: 2026-06-03
- Split: `validation` / `gan2026_split_v1`
- Surface: full validation750 development split; no locked-test rows inspected
- Live source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_conservative_live_2026-06-03.jsonl`
- Final no-call replay artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`
- Claim language: hybrid deterministic-safety-floor development result, not an LLM-first result and not a benchmark/holdout claim.

## Result

The patched `hybrid_parallel_state_candidate_reasoner` clears the >0.9000 full-validation development target under the deterministic safety-floor policy:

- `hybrid_adjudicator_with_adapters` Purist: 697/750 (0.9293)
- `hybrid_adjudicator_with_adapters` Pragmatic: 704/750 (0.9387)
- selected evidence exact: 750/750
- selected source ids valid: 750/750
- deterministic-correct regressions: 0
- adapter raw-correct-to-wrong: 0
- deterministic safety-floor fallbacks: 136/750

The prediction-bearing layer now matches the deterministic top candidate when the adjudicator would otherwise disagree. LLM-candidate and graph outputs remain recorded as adjudication context and diagnostic sidecars, but the deterministic top candidate is the safety floor for the final label.

## Failed Earlier Variant

The live full-validation run before the safety-floor replay did not clear the target:

- live `hybrid_adjudicator_with_adapters` Purist: 669/750 (0.8920)
- deterministic-correct regressions: 43
- selected evidence exact: 749/750

The first safety-floor replay crossed the threshold narrowly at 676/750 (0.9013), but evidence-based semantic repair still rewrote deterministic fallback labels on 23 deterministic-correct rows. The final v2 replay bypasses evidence-based semantic repair for deterministic-safety-floor rows, leaving the deterministic label prediction-bearing and auditable.

## Remaining Caveats

- This is a validation development result only. Do not describe it as a benchmark or holdout result.
- The result is not an LLM-heavy or LLM-first success. It is a hybrid result with deterministic semantic participation and deterministic final-label safety floor.
- The LLM candidate selector still has 11 schema-validation failures on validation750, mostly enum drift in candidate `kind` or `assertion_status`.
- Remaining Purist misses: 53/750. The largest category is unknown gold mapped to seizure-free predictions (21 rows).

## Decision

Promote this as the current development candidate satisfying the >0.9000 validation objective, with attribution language locked to hybrid deterministic-safety-floor. The next useful work is component-stress/error analysis and a frozen-test audit plan, not more validation tuning.
