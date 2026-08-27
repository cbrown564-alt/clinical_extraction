# Protocol: Gemini 3.7 Flash Gan LLM-only v0.8 on `dev750` and `test450`

Date: 2026-08-13
Status: complete; `dev750` inspectable and `test450` aggregate-only
Report: [2026-08-13 report](gemini37flash_llm_only_dev750_test450_2026-08-13.md)
Authorization: [PROJECT_STATUS](../../../PROJECT_STATUS.md) next item 1; user
requested `gan2026_llm_only_canonical_pipeline_v0.8` on inspectable `dev750`
and aggregate-only `test450` with Gemini 3.7 Flash.
Decision: [0051](../../decisions/0051-gemini-37-flash-succeeds-gpt41mini-six-model-slot.md)
Does not change: [decision 0050](../../decisions/0050-current-stack-hybrid-primary-fills.md)
hybrid fills, [decision 0052](../../decisions/0052-gemini-37-flash-holdout-six-model-slot.md)
hybrid holdout slot, Decision 0046 Sol method identity, or GPT-4.1-mini scores.

Parents:
[successor protocol](../shared/six_model_gemini37flash_successor_protocol_2026-08-13.md),
[July 18 LLM-only arm](../../experiments/gan2026/gan2026_six_model_validation_comparison_protocol_2026-07-18.md),
[August 1 LLM-only test450 panel](../../experiments/gan2026/gan2026_six_model_llm_only_test450_protocol_2026-08-01.md).

## Question

How does Gemini 3.7 Flash (`reasoning_effort=low`) score on Gan `dev750` and
locked `test450` under the matched LLM-only pipeline
`gan2026_llm_only_canonical_pipeline_v0.8`?

This is a successor-roster `llm` cell. It is not a no-call replay of
GPT-4.1-mini raws, not a hybrid `llm_with_rules` cell, and not a rewrite of
the 1 August six-model LLM-only panel.

## Data and row policy

| Split | Manifest | Rows | Row policy | Out of scope |
| --- | --- | ---: | --- | --- |
| `validation` (`dev750`) | `gan2026_split_v1` | 750 | development row-level | locked `test450` inspection |
| `test` (`test450`) | `gan2026_split_v1` | 450 | aggregate-only | any holdout identifier, note, prediction, evidence, error, or row table |

The runner may read locked notes only to make the frozen `test450` calls.
No holdout identifier, note, prediction, evidence, error, changed row, or
model-specific failure may be inspected or copied into a report.

## Frozen condition

| Field | Value |
| --- | --- |
| Model | `gemini/gemini-3.7-flash` |
| Thinking | `GEMINI_REASONING_EFFORT=low` |
| Temperature | `0` |
| Max tokens | 16,000 |
| Cache | off |
| Pipeline | `llm` / retained ID `llm_only_canonical_pipeline` |
| Prompt | `gan2026_llm_only_canonical_pipeline_v0.8` |
| Repair | `model_selected_evidence_benchmark_adapter` (label repair, evidence containment, scoring) |
| Scorer | Purist primary; Pragmatic side-car |

No prompt, scorer, repair, or split change after calls begin. A call or parse
failure stays a failure in the aggregate. Resume is allowed only for the same
frozen condition and dated artifact path. A defect starts a new development
candidate; it does not license holdout repair.

ExECT has no second live call. Decision 0041/0046 LLM-only is the
`raw_lane_score` of the already-on-disk one-call packages (`dev140` **0.8444**,
`test60` **0.82`). Those numbers are recorded as successor llm-only peers
without new ExECT calls.

## Artifacts

| Role | Path |
| --- | --- |
| Config | `configs/gan2026/six_model_llm_only_gemini37flash_20260813.json` |
| `dev750` rows (explorer / July 18 LLM-only tree) | `experiments/gan2026_six_model_validation_20260718/gemini37flash--llm_only.jsonl` |
| `dev750` report | `experiments/gan2026_six_model_llm_only_gemini37flash_20260813/validation750.report.md` |
| `test450` sealed dump | `scratch/holdout/gemini37flash_llm_only_20260813/gan_test450/sealed_rows.jsonl` |
| `test450` aggregate markdown | `scratch/holdout/gemini37flash_llm_only_20260813/gan_test450/aggregate.md` |
| Machine summary | `experiments/gan2026_six_model_llm_only_gemini37flash_20260813/summary.json` |
| Study report | `docs/research/gan2026/gemini37flash_llm_only_dev750_test450_2026-08-13.md` |

Full live `test450` dumps stay under `scratch/holdout/`. Only aggregate
counts, scores, failure totals, and timing may leave that directory.

## Commands

Smoke (one `dev750` row; not a score):

```bash
GEMINI_REASONING_EFFORT=low .venv/bin/python scripts/run_gan2026_llm_only_condition.py \
  --prompt-version gan2026_llm_only_canonical_pipeline_v0.8 \
  --pipeline llm --split validation --limit 1 \
  --model gemini/gemini-3.7-flash --temperature 0 --max-tokens 16000 \
  --disable-dspy-cache \
  --jsonl scratch/validation/gemini37flash_llm_only_20260813/smoke_dev1.jsonl \
  --markdown scratch/validation/gemini37flash_llm_only_20260813/smoke_dev1.md
```

`dev750` live cell:

```bash
GEMINI_REASONING_EFFORT=low .venv/bin/python scripts/run_gan2026_llm_only_condition.py \
  --prompt-version gan2026_llm_only_canonical_pipeline_v0.8 \
  --pipeline llm --split validation \
  --model gemini/gemini-3.7-flash --temperature 0 --max-tokens 16000 \
  --disable-dspy-cache --progress-every 25 --resume-existing \
  --escalation-reason "Decision 0051 successor Gemini 3.7 Flash live llm-only dev750 cell" \
  --jsonl experiments/gan2026_six_model_validation_20260718/gemini37flash--llm_only.jsonl \
  --markdown experiments/gan2026_six_model_llm_only_gemini37flash_20260813/validation750.report.md
```

`test450` live cell (this file is the required `--frozen-test-protocol`):

```bash
GEMINI_REASONING_EFFORT=low .venv/bin/python scripts/run_gan2026_llm_only_condition.py \
  --prompt-version gan2026_llm_only_canonical_pipeline_v0.8 \
  --pipeline llm --split test \
  --frozen-test-protocol docs/research/gan2026/gemini37flash_llm_only_dev750_test450_protocol_2026-08-13.md \
  --model gemini/gemini-3.7-flash --temperature 0 --max-tokens 16000 \
  --disable-dspy-cache --progress-every 25 --resume-existing \
  --jsonl scratch/holdout/gemini37flash_llm_only_20260813/gan_test450/sealed_rows.jsonl \
  --markdown scratch/holdout/gemini37flash_llm_only_20260813/gan_test450/aggregate.md
```

## Readouts

- `dev750`: Purist and Pragmatic correct counts on all 750 rows; inspectable
  row report allowed.
- `test450`: Purist and Pragmatic correct counts on all 450 rows; operational
  call/parse totals and wall time. No `## Rows` table.
- Explorer: rebuild `frontend/public/mock-data/pipeline-families.json` after
  `dev750` completes so the Gemini LLM-only slot is served.

## Stop rule and claim boundary

Run each cell once. Report `dev750` as inspectable development evidence and
`test450` as aggregate-only holdout. Do not copy GPT-4.1-mini scores. Do not
promote these cells as Decision 0050 / 0052 hybrid fills or as the paper
method-identity row. Sol remains the paper method-identity row. Not clinical
validation.
