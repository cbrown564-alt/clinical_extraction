# Gemini 3.7 Flash successor holdout protocol

Date: 2026-08-13
Status: complete; aggregate-only
Authorization: the user requested Gemini `test450` and `test60` live cells
and promotion into the living six-model hybrid fills.
Decision: [0051](../../decisions/0051-gemini-37-flash-succeeds-gpt41mini-six-model-slot.md)
Amends: six-model slots in
[decision 0050](../../decisions/0050-current-stack-hybrid-primary-fills.md)
Does not change: Decision 0046 Sol method identity; rules-only or LLM-only fills

## Question

How does Gemini 3.7 Flash (`reasoning_effort=low`) score on the locked Gan
`test450` and ExECT `test60` splits under the same selected hybrid methods
used for the Decision 0051 development cells?

## Frozen data and row policy

- Gan: `gan2026_split_v1` `test` / `test450`, 450 rows.
- ExECT: manifest `test` / `test60`, 59 loadable letters.
- The runner may read locked notes only to make the frozen calls.
- No holdout identifier, note, prediction, evidence, error, changed row, or
  model-specific failure may be inspected or copied into a report.
- Full live dumps stay under `scratch/holdout/gemini37flash_20260813/`.
- Only aggregate counts, scores, failure totals, and timing may leave that
  directory. Stripped sidecars for remasure may be promoted to
  `experiments/current_stack/sidecars/` without note text, gold, or prompts.

## Frozen conditions

- Model: `gemini/gemini-3.7-flash`
- Thinking: `GEMINI_REASONING_EFFORT=low`
- Temperature: `0`
- Cache: off
- Gan: `llm_with_rules`, prompt `gan2026_hybrid_structured_events_v0.5`,
  `hybrid_full_stack`, max tokens 16,000
- ExECT: Decision 0040/0041 one-call, prompt
  `exectv2_hybrid_key_family_event_ledger_v0.9.24`, default/default assembly,
  structured max tokens 16,000

No prompt, scorer, repair, or split change after calls begin. A call or parse
failure stays a failure in the aggregate. Resume is allowed only for the same
frozen condition. A defect starts a new development candidate; it does not
license holdout repair.

## Readouts

- Gan: Purist and Pragmatic correct counts on all 450 rows.
- ExECT: `clinical_headline` overall and four-family F1 on 59 letters.
- Operational: call/parse/schema totals and wall time.

## Stop rule and claim boundary

Run each cell once. Report aggregates only. Sol remains the paper
method-identity row. These cells replace GPT-4.1-mini in the living six-model
hybrid panel. They are not the published ExECT benchmark and not clinical
validation.

## Commands

```bash
GEMINI_REASONING_EFFORT=low .venv/bin/python scripts/run_exectv2_six_model_comparison.py \
  --config configs/exectv2/six_model_comparison/gemini37flash_test60.json \
  --allow-non-dev140 --no-dspy-cache --no-resume --generated-on 2026-08-13 \
  --allow-row-failures --progress-every 10

GEMINI_REASONING_EFFORT=low .venv/bin/python scripts/run_gan2026_v05_hosted_condition.py \
  --prompt-version gan2026_hybrid_structured_events_v0.5 \
  --pipeline llm_with_rules --split test \
  --frozen-test-protocol docs/research/shared/six_model_gemini37flash_holdout_protocol_2026-08-13.md \
  --model gemini/gemini-3.7-flash --temperature 0 --max-tokens 16000 \
  --disable-dspy-cache --progress-every 25 --resume-existing \
  --jsonl scratch/holdout/gemini37flash_20260813/gan_test450/sealed_rows.jsonl \
  --markdown scratch/holdout/gemini37flash_20260813/gan_test450/aggregate.md
```
