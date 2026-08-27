# Protocol: ExECT cheap-stack stacked further prune, Luna `dev20`

Date: 2026-08-17  
Status: **complete**; stacked arm is **low_value** versus cleaned cheap  
Parent: [one-at-a-time further prune](v0924_cheap_further_prune_luna_dev20_2026-08-16.md)  
Assignment: [prompt variant slots](prompt_variant_slots_2026-08-16.md)

The three leftover choruses inside the cleaned cheap stack were each
**low_value** on frozen Luna `dev20` when cut alone. This study applies
all three at once. `v0.9.24` stays the default. Slot 2 stays `v0.9.40`.
`test60` is sealed. Decision 0050 is unchanged. Do not start `dev140`
from this result.

## Primary question

On the same frozen 20-letter Luna pool, does the stacked further prune
of the cleaned cheap stack stay under the leave-one-out stop bars
versus the current cleaned cheap stack?

That asks whether the three low_value choruses remain cheap when
removed together. It does not ask whether the stack should replace
`v0.9.24` or become slot 2.

## Arms

| Arm | Prompt | Calls |
| --- | --- | ---: |
| `v0924_head` | saved `v0.9.24` through HEAD | 0 |
| `plain_cheap` | saved cleaned `v0.9.40` through HEAD | 0 |
| `ix_pending` | saved one-cut raws through HEAD | 0 |
| `scaffold_reprint` | saved one-cut raws through HEAD | 0 |
| `refuse_chorus` | saved one-cut raws through HEAD | 0 |
| `stacked` | live `v0.9.44_cheap_stack_further_prunes` | 20 |

The live candidate starts from the cleaned cheap stack, then applies
all three scored cuts: investigation-pending collapse, scaffold-reprint
drop, and refuse-chorus collapse. Do not change the live cheap
identity. `v0.9.44` is study-only.

## Data and scoring

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Same frozen `dev20`: EA0002, EA0004, EA0005, EA0006, EA0007, EA0008,
  EA0009, EA0010, EA0011, EA0012, EA0015, EA0016, EA0047, EA0074,
  EA0093, EA0120, EA0131, EA0133, EA0154, EA0158.
- Development rows may be inspected. `test60` remains aggregate-only.
- Model: `openai/gpt-5.6-luna`. Temperature 1.0. Cache off. One
  structured hybrid call per letter. Output budget 16000 tokens.
- Control: saved cleaned cheap raws from
  `experiments/exectv2_v0924_cheap_stack_plain_luna_dev20_20260816/plain_cheap/structured.jsonl`.
- One-cut sidecars: saved raws from
  `experiments/exectv2_v0924_cheap_further_prune_luna_dev20_20260816/`.
- Secondary comparator: saved `v0.9.24` raws from
  `experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816/v0924_head/structured.jsonl`.
- Primary: four-family `clinical_headline` F1 versus cleaned cheap.
- Secondary: family F1, four-family letter exact, parse/schema
  failures, changed-row direction, the same scores versus `v0.9.24`,
  and versus the three saved one-cut arms. EA0004 and EA0010 remain
  contamination letters; report them separately; do not retune from
  those two letters.

## Stop rule

Same bars as the leave-one-out series, scored against the cleaned
cheap stack:

- **low_value** if hybrid headline drop < 0.05, no family drop ≥ 0.08,
  and net four-family exact losses < 3.
- **load_bearing** if any of those bars fail. The three choruses
  interact; keep them in the cheap stack.
- **revise** if parse/schema failures appear or the payload contract
  drifted.

Report the same bars versus `v0.9.24` and versus the scaffold-reprint
one-cut, but do not use those comparisons to keep or drop the stack.
Do not promote. Do not change the default. Do not change slot 2.
Do not start `dev140` from this result.

## Minimal implementation change

Register one study-only prompt identity that applies the three already
scored further prunes after the existing language pass. Call
`set_active_prompt_version` only inside the live arm, then restore
`v0.9.24`. Use `.venv`. Replay every saved arm before paying for new
calls.

## Artifact contract

Study directory:
`experiments/exectv2_v0924_cheap_further_prune_stacked_luna_dev20_20260817/`.

Write `comparison.json` plus the structured sidecars and HEAD
assembly needed to recompute the table. One row per frozen letter.
Record prompt identity, call mode, cache state, parse/schema events,
family scores, and changed-row direction. Do not overwrite the
one-at-a-time further-prune artifact.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not a slot-2 change, not holdout evidence,
and not a Decision 0050 change.
