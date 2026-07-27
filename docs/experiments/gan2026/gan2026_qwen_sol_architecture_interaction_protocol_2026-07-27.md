# Gan 2026 Qwen versus GPT-5.6 Sol architecture-interaction protocol

Date: 2026-07-27  
Status: frozen before new saved-output analysis

## Primary question

Why does Qwen 3.6:35B score above GPT-5.6 Sol in the Gan 2026
`llm_with_rules` pipeline on `dev750`, even though Sol scores above Qwen in the
matched `llm_only` condition? Does the saved evidence show that the architecture
is specifically fitted to Qwen or to local/smaller models?

## Data and inspection policy

- Dataset: Gan 2026.
- Split: `dev750` (`validation750` in retained artifact identifiers).
- Manifest: `gan2026_split_v1`.
- Row policy: development row-level inspection is permitted.
- Models: `ollama_chat/qwen3.6:35b` and `openai/gpt-5.6-sol`.
- Methods: retained `llm_only` direct-label outputs and retained
  `llm_with_rules` event-ledger outputs.
- Scorer: Gan Purist accuracy primary; Pragmatic retained as secondary context.
- Calls: none; replay and analysis of saved outputs only.
- Exclusion: no `test450` row may be opened or used for mechanism analysis.

## Inputs

- `experiments/gan2026_six_model_validation_20260718/qwen36_35b--llm_only.jsonl`
- `experiments/gan2026_six_model_validation_20260718/qwen36_35b--llm_with_rules.jsonl`
- `experiments/gan2026_six_model_validation_20260718/gpt56sol--llm_only.jsonl`
- `experiments/gan2026_six_model_validation_20260718/gpt56sol--llm_with_rules.jsonl`
- `experiments/gan2026_six_model_post_panel_attribution_20260720.json`
- `experiments/gan2026_qwen_sol_rule_benefit_audit_20260720.json`

## Candidate, comparator, and score layers

The candidate is Qwen and the fixed comparator is Sol. The study must not treat
the `llm_only` to `llm_with_rules` difference as a pure rule ablation because
the methods use different prompts and output representations.

For each model, retain:

1. raw direct-label model selection;
2. direct-label deterministic adapter output;
3. raw event-ledger model selection;
4. event-ledger deterministic semantic output; and
5. final Purist result.

## Required analyses

- Final Qwen-versus-Sol wins, losses, shared successes, and shared failures.
- Direct-label and event-ledger model-boundary behavior separately.
- Same-saved-output wrong-to-correct, correct-to-wrong, and unchanged rows.
- Clinical-subproblem, gold-family, first-failure-owner, evidence-validity,
  and repair-event breakdowns.
- Rows where Qwen finishes correct and Sol finishes wrong, and the reverse.
- Rows where both models expose the same correct clinical fact but fixed code
  changes it incorrectly.
- Rows where the architecture rescues Qwen-specific output forms but not Sol
  forms, and vice versa.
- A separation of model extraction/selection differences from deterministic
  adapter, semantic rule, projection, benchmark-format, and scorer effects.
- A decision table stating what is supported, contradicted, or unmeasured about
  Qwen-specific, local-model, small-model, and Sol-under-optimization claims.

## Machine artifact

One row represents one `dev750` source row. Preserve source row id, gold label
and family, both models' raw and final labels, Purist correctness at every
available layer, exact-evidence status, first-failure owner, clinical
subproblem, deterministic events, and head-to-head outcome.

## Stop rule and claim boundary

Stop if the four retained files do not align to the same 750 unique manifest
rows or if the attribution artifact cannot be joined without ambiguity.
Otherwise report a development mechanism answer. The study may diagnose
model-by-method interaction and named deterministic failure modes. It cannot
establish model-neutral generalization, absence of validation tuning, clinical
validity, or a pristine holdout result. Aggregate `test450` scores may be cited
only as previously retained context.
