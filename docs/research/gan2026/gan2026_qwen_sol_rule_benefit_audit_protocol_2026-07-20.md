# Gan 2026 Qwen versus GPT-5.6 Sol rule-benefit audit protocol

Date: 2026-07-20  
Status: frozen before saved-output analysis

## Primary question

Why does the matched six-model Gan `dev750` table show a larger difference
between `llm_only` and `llm_with_rules` for Qwen 3.6:35B than for GPT-5.6 Sol,
and is that difference evidence that the deterministic policy overfits Qwen?

The audit separates two comparisons that the aggregate table can otherwise
conflate:

1. the matched but different-prompt `llm_only` and `llm_with_rules` methods;
2. the model prediction boundary and final deterministic result within each
   saved method output.

## Data and inspection policy

- Dataset: Gan 2026.
- Split: `dev750` (`validation750` in retained artifact identifiers).
- Manifest: `gan2026_split_v1`.
- Row policy: development row-level inspection is permitted.
- Model calls: none; saved outputs only.
- Models: `ollama_chat/qwen3.6:35b` and `openai/gpt-5.6-sol`.
- Scorer: Gan Purist primary; Pragmatic is retained but not used to define the
  error-row set.
- Gan `test450` is excluded from row inspection.

## Inputs

- `experiments/gan2026_six_model_validation_20260718/qwen36_35b--llm_only.jsonl`
- `experiments/gan2026_six_model_validation_20260718/qwen36_35b--llm_with_rules.jsonl`
- `experiments/gan2026_six_model_validation_20260718/gpt56sol--llm_only.jsonl`
- `experiments/gan2026_six_model_validation_20260718/gpt56sol--llm_with_rules.jsonl`
- `experiments/gan2026_six_model_post_panel_attribution_20260720.json`

## Row set and required fields

Include every `source_row_index` where either model is Purist-wrong in either
final scored method. For each included row retain:

- gold label and score category;
- direct-label raw model label, final adapter label, correctness, evidence,
  rationale, and adapter events;
- event-ledger raw selected label, final deterministic label, correctness,
  selected evidence, rationale, extracted event summary, semantic events,
  first-failure owner, and clinical subproblem;
- a row-specific comment that distinguishes model selection failure,
  deterministic rescue, deterministic regression, and unresolved failure; and
- an explicit flag when a raw Purist-correct answer becomes wrong after fixed
  code.

## Aggregate analysis

Report:

- matched `llm_only` to `llm_with_rules` wrong-to-correct and
  correct-to-wrong transitions;
- within-method raw-boundary to final rescues and regressions;
- final head-to-head overlap;
- evidence validity and error ownership;
- clinical-subproblem breakdown; and
- what the saved development and aggregate-only test results can and cannot
  say about model-specific or policy-level overfitting.

## Stop rule and claim boundary

Stop if the four artifacts do not contain the same 750 unique manifest rows or
if the attribution artifact cannot align them. This study is a no-call
development mechanism audit. It may diagnose why the table differs and expose
direct deterministic regressions. It cannot establish clinical validity,
model-neutral capability, pristine holdout generalization, or absence of
policy-level validation tuning. Aggregate test results may be cited only as a
limited anti-overfit check; test rows must not be opened.

