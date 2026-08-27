# Protocol: ExECT cheap-stack further prune, one cut at a time, Luna `dev20`

Date: 2026-08-16  
Status: **complete**; all three arms are **low_value** versus cleaned cheap  
Parent: [cleaned cheap-stack remasure](v0924_cheap_stack_plain_luna_dev20_2026-08-16.md)  
Assignment: [prompt variant slots](prompt_variant_slots_2026-08-16.md)

The cleaned cheap stack is the retained cheap variant, not the default.
It is **load_bearing** versus `v0.9.24` on frozen Luna `dev20`
(SeizureFrequency −0.0929) and on authorized `dev140` (exact net −6).
This study asks whether three leftover choruses inside that cheap
payload are still needed. Each cut is a separate arm. Do not stack
them. `v0.9.24` stays the default. Slot 2 stays `v0.9.40`. `test60`
is sealed. Decision 0050 is unchanged. Do not start `dev140` from
these results.

## Primary question

On the same frozen 20-letter Luna pool, does **one** further cut of
the cleaned cheap stack stay under the leave-one-out stop bars versus
the current cleaned cheap stack?

That asks whether the named chorus is still needed inside the cheap
variant. It does not ask whether a smaller stack should replace
`v0.9.24`.

## Arms

Run in this order. Score the finished arm before starting the next.
All three run even if an earlier arm is load_bearing.

| Order | Arm | Prompt identity | Cut |
| ---: | --- | --- | --- |
| — | `v0924_head` | saved `v0.9.24` through HEAD | 0 calls |
| — | `plain_cheap` | saved cleaned `v0.9.40` through HEAD | 0 calls |
| 1 | `ix_pending` | `v0.9.41_cheap_drop_ix_pending_repeat` | Drop the three investigation-pending restatements. Keep the pending-cue list and the no-bare/duplicate test-name rule. |
| 2 | `scaffold_reprint` | `v0.9.42_cheap_drop_scaffold_reprint` | Drop rule 1's category-id reprint, shorten the decision loop so it does not repeat the task, and drop model-facing `prompt_version` / `letter_id`. |
| 3 | `refuse_chorus` | `v0.9.43_cheap_collapse_refuse` | Replace the ten Diagnosis/SeizureFrequency refuse restatements with one refuse rule. Keep negated resemblance, pointing phrases, and the two bare seizure-free rules. |

Do not change the live cheap identity. These three IDs are study-only.

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
  `experiments/exectv2_v0924_cheap_stack_plain_luna_dev20_20260816/plain_cheap/structured.jsonl`,
  replayed through unchanged HEAD assembly.
- Secondary comparator: saved `v0.9.24` raws from
  `experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816/v0924_head/structured.jsonl`.
- Primary: four-family `clinical_headline` F1 versus cleaned cheap.
- Secondary: family F1, four-family letter exact, parse/schema
  failures, changed-row direction, and the same scores versus
  `v0.9.24`. EA0004 and EA0010 remain contamination letters; report
  them separately; do not retune from those two letters.

## Stop rule

Same bars as the leave-one-out series, scored against the cleaned
cheap stack:

- **low_value** if hybrid headline drop < 0.05, no family drop ≥ 0.08,
  and net four-family exact losses < 3.
- **load_bearing** if any of those bars fail. That chorus stays in the
  cheap stack.
- **revise** if parse/schema failures appear or the payload contract
  drifted.

Report the same bars versus `v0.9.24`, but do not use that comparison
to keep or drop a chorus. The cheap stack is already load_bearing
versus the selected prompt.

Do not promote. Do not change the default. Do not change slot 2.
Do not start `dev140` from any arm.

## Minimal implementation change

Register three study-only prompt identities on top of the cleaned
cheap stack. Apply exactly one named further prune after the existing
language pass. Call `set_active_prompt_version` only inside the live
arm, then restore `v0.9.24`. Use `.venv`.

## Artifact contract

Study directory:
`experiments/exectv2_v0924_cheap_further_prune_luna_dev20_20260816/`.

Write `comparison.json` plus the structured sidecars and HEAD
assembly needed to recompute the table. One row per frozen letter.
Record prompt identity, call mode, cache state, parse/schema events,
family scores, and changed-row direction. Update the artifact after
each scored arm. Do not overwrite earlier cheap-stack artifacts.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not a slot-2 change, not holdout evidence,
and not a Decision 0050 change.
