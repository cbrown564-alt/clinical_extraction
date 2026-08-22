# Gan candidate-suggestion protocol

Date: 2026-08-20
Status: development
Owner: this file
Identity: `gan_llm_pre_post` (paper rung 5, `llm_pre_post`)

## Question

If the Gan hybrid request is given the same deterministic candidate
quotes that `gan_rules` already extracts, does the model keep, reject,
split, or merge those rows and still scan the rest of the letter so
that the later clinical post stack is working from a better event
list?

This is a new request. It is not a replay of `gan_llm_with_rules`.

## Why it matters

Rungs 2–4 share one saved `gan_llm_with_rules` output and vary only
rule depth after the call. ExECT already suggests candidates before
generation. Gan does not. The five-rung table needs a Gan pre-suggestion
cell before any claim that the two tasks use the same rule-help ladder.

## Dataset and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `dev750` (`gan2026_split_v1` validation) |
| Row policy | Development review permitted |
| Holdout | Luna `test450` finished. Aggregate-only. Do not inspect rows. Do not start Grok rung-5 unless asked. |
| Comparator | Replay of the same `dev750` letters through rungs 2–4 from saved Grok `gan_llm_with_rules` raw output |
| Iterator model | GPT-5.6 Luna (`gpt56luna`) |
| Cited model | Not decided. Luna is the development iterator, not automatically the cited model. |

## Candidate and prompt

- Reuse `extract_stage` / `deterministic_candidate_set_from_raw`. Do not
  invent a second rules engine.
- Same event and selection schema as `prompt_llm_with_rules.py`.
- Suggested rows: `kind`, `evidence` (exact quote), `name_hint`.
- Ask the model to keep, reject, split, or merge each suggested row,
  then scan the rest of the letter.
- Same post stack as rung 4 (`hybrid_full_stack`).

## Scorer

Gan Purist accuracy on `dev750`. Secondary: Pragmatic accuracy, scorable
count, hop log (`answer_states`). A recorded hop is not a clinically
correct step. Development hop shares are not holdout component estimates.

## Iteration order

1. Freeze the candidate payload and keep/reject language on a 12-letter
   Luna development slice (`source_row_index` order from validation).
2. Named hard slice `luna_hybrid_misses`: the 87 living Luna
   `gan_llm_with_rules` `dev750` Purist misses. Comparator is that
   same hybrid cell on the same letters. Question: how many of those
   misses does pre-suggest recover, and are the recoveries schema,
   selection, or dialect?
3. Full Luna `dev750` only if the hard slice changes the reading.
4. Only then decide Grok / Gemini / holdout.

Do not overlap another Luna job on `OPENAI_API_KEY`.

## Stop rule

- Slice: stop if suggested rows are empty on notes that `gan_rules`
  scores, or if the rendered payload names the dataset or includes
  research envelope keys.
- Hard slice: stop after the 87-letter comparison is written. Do not
  retune the prompt from those misses into a second call on the same
  87. Do not treat a recovery rate on this slice as a `dev750` score.
- Full cell: stop after the Luna `dev750` comparison and hop
  audit. Do not retune the prompt from those misses.
- Holdout: stop after the Luna `test450` aggregate. Do not
  inspect rows. Do not retune from holdout. Do not start Grok
  unless asked.

## Claim boundary

If Luna `dev750` beats the Grok rung-4 replay, that is a development
mechanism result about pre-suggestion on this prompt. It is not a
holdout estimate and not a Grok result. Luna `test450` is an
aggregate-only holdout cell for this prompt. It is not a Grok
result and is not promoted.

## Slice freeze (2026-08-20)

Luna 12-letter development slice: 12/12 parsed, 12/12 Purist, no
format retry. First-row payload keys are task, instructions, schemas,
suggested evidence, note. Suggested row used `kind`, `evidence`,
`name_hint` from `extract_stage`. Keep/reject language present. No
dataset name. Prompt frozen. Do not cite the interrupted
`experiments/paper/` partial as a cell.

## Hard slice (2026-08-20)

Luna `luna_hybrid_misses` finished: 87/87 calls, 0 call failures.
Artifact: `experiments/paper/gan_llm_pre_post/gpt56luna/slice_luna_hybrid_misses/dev750/`.
Purist 35/87, Pragmatic 45/87. Living Luna hybrid is 0/87 here by
construction. Deterministic `gan_rules` is 73/87 on the same IDs.

Of the 35 recoveries: 1 schema (hybrid unscorable), 16 dialect or
count-form (mostly `multiple per week` / `multiple per cluster` to a
count), 18 selection (mostly seizure-free / no-reference / unknown
to a count the rules already had). 33 of 35 recoveries are also
rules-correct. Two beat rules (10996, 15834). 40 rules-correct
letters remain wrong; 36 of 52 remaining misses share the living
hybrid label. Not a `dev750` score. No prompt retune from these
52.

## Full Luna `dev750` (2026-08-20)

Luna `gan_llm_pre_post` finished: 750/750 rows, 700 new calls, 50
resumed, 0 call failures. Artifact:
`experiments/paper/gan_llm_pre_post/gpt56luna/dev750/`.
Purist 0.90, Pragmatic 0.92. Living Luna
hybrid is 0.88. Rules-only is 0.91. Grok rung-4 replay is
0.90. 4 invalid JSON. Not holdout. Not a Grok cell.

Hop audit: 64/74 misses are already wrong at model selection.
Post first-failure harms are 3 monthly-diary and 3
selected-evidence. Ranked rule work: (1) do not rewrite
`no_reference` from the word *daily*; (2) do not replace a
typical-month rate with a summed diary; (3) sum every stated
month in selected evidence; (4) do not veto a countable diary
for vague seizure-free; (5) three dated events are a count over
the dated span. Residual jerk, post-change burst, dated
sequence, usual interval, and typical-over-ytd helped and never
harmed. Unused event `raw_value` never Purist-matched gold on a
miss.

## Luna `test450` (2026-08-20)

Luna `gan_llm_pre_post` finished: 450/450 calls, 0 reused, 0
call failures. Promoted to
`paper_experiments/gan/gan_llm_pre_post/gpt56luna/test450/`.
Purist 0.82, Pragmatic 0.84. 2 parse or
validation failures. Locked Grok rung 4 is 0.83. Aggregate
only. Not a Grok cell. Do not inspect rows. Do not retune from
this cell.

## Prompt audit

Rendered payload inspected on the placeholder note
`Present seizure frequency: two seizures per month.`

- Model-facing: task, instructions, schemas, suggested evidence, note.
- Parser-facing: event field names and kind lists reused from the
  living hybrid schema.
- Research-facing keys (`prompt_version`, `source_row_index`, `Gan`)
  are not in the payload.
- New instructions use ordinary verbs (read, treat, keep, reject,
  split, merge, scan, return).
- `source-near` remains only on the reused hybrid schema fields.

## Commands

```bash
source .venv/bin/activate
python -m clinical_extraction.paper verify --method gan_llm_pre_post --split dev750 --model gpt56luna
python -m clinical_extraction.paper run --method gan_llm_pre_post --model gpt56luna --split dev750 --live --slice luna_hybrid_misses --progress-every 5
```
