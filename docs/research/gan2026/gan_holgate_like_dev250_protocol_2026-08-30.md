# Protocol: Holgate-like dialect on a 250-letter development sample

Date: 2026-08-30
Status: completed 2026-08-30
Report: [dev250 dialect](gan_holgate_like_dev250_2026-08-30.md)
Owner: this file
Related: [prompt-component ablation](gan_extract_prompt_component_ablation_protocol_2026-08-30.md)

## Primary question

On a prespecified 250-letter `dev750` sample, which Holgate-like
written labels fail the living parser only because they follow the
Holgate ask (`I do not know` instead of `unknown`), and which other
recurring forms are the same clinical answer in a different dialect?

The living Purist scorer stays unchanged. This study builds a named
Holgate-dialect projection so the codebook-versus-Holgate comparison
is not an arbitrary format penalty.

## Why it matters

Locked `test450` Holgate-like find was scorable on 172/450. The
prompt tells the model to write `I do not know` when there is no
frequency information. Living parse accepts `unknown` and
`no seizure frequency reference`. Those two sentinels already share
the Purist/Pragmatic unknown band (`monthly_frequency == 1000`).
Punishing `I do not know` is a dialect mismatch, not a clinical
disagreement.

Holdout rows will not be read to invent aliases.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Pool | `dev750` / `gan2026_split_v1` validation |
| Sample | `gan_holgate_like_dev250_v1` (250 letters) |
| Draw | `random.Random(20260830).sample(sorted(validation), 250)`, then sort |
| Row policy | Development review permitted |
| Holdout | `test450` not inspected. After aliases are frozen on this sample, holdout may be reparsed aggregate-only |

Split protocol allows a 250-letter development pass when a smaller
cell has already shown a specific failure. The specific failure here
is the holdout aggregate scorable count, not holdout row review.

## Candidate and comparator

- Candidate find: frozen `gan_llm_extract_holgate_like`
- Model: Gemini 3.7 Flash, temperature 0
- Living parse/score: `label_to_frequency_record` as now
- Later cell-3 replay stays `gan_rules_encode` +
  `llm_select_after_codebook`
- Comparator: the same 250 letters under living codebook find is
  not required for the dialect inventory. Optional later.

## Allowed change

A named projection `holgate_dialect_v1`, applied only when scoring
this ablation. It may:

1. Map Holgate abstention strings the prompt asked for onto
   `unknown` (same Purist band as `no seizure frequency reference`).
2. Map other recurring **format** paraphrases onto an already
   parseable label without changing count, unit, sentinel, or
   seizure-free meaning.

It may not change living codebook scoring, Table 1, or gold.

## Required analysis

On the 250 letters, after the live find:

1. Count scorable versus unscorable under the living parser.
2. Frequency table of unscorable `final_label` strings (no need to
   quote full letters for the first table).
3. For the most common strings, read development notes only as
   needed to decide format-versus-meaning.
4. Freeze `holgate_dialect_v1`.
5. Rescore the 250-letter find (and cell-3 replay) under that
   projection.
6. Aggregate-only reparse of saved `test450` Holgate raws. No row
   inspection.

## Artifact

- Sample: [dev250 indices](gan_holgate_like_dev250_v1.json)
- Live find: `experiments/paper/gan_llm_extract_holgate_like/gemini37flash/dev250_v1/`
- Report and projection owners written after the find

## Stop rule

Stop when the dialect inventory is written and `holgate_dialect_v1`
is frozen or rejected. Negative result: almost all unscorable labels
are genuine clinical misses, not Holgate dialect. Do not retune the
Holgate prompt from these letters. Do not change Table 1.

## Claim boundary

Development answer plus optional holdout aggregate confirmation.
Holgate-permissive scores are a comparison projection, not the
living scorer. Not “Holgate matches codebook” unless the projection
is declared.
