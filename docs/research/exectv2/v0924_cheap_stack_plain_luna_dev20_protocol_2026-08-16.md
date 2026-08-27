# Protocol: ExECT cheap-stack plain-language remasure on Luna `dev20`

Date: 2026-08-16  
Status: **complete**; cleaned stack still load_bearing on SF  
Parent: [cheap-stack structural cut](v0924_cheap_stack_luna_dev20_2026-08-16.md)  
Assignment: [prompt variant slots](prompt_variant_slots_2026-08-16.md)

The retained cheap stack dropped the 16 non-SF encoding rules and all
49 examples. That cut is **load_bearing** on SeizureFrequency
(−0.0929). The live cheap payload then had research labels and leftover
jargon removed. This study remasures that cleaned payload. `v0.9.24`
stays the default. `test60` is sealed. Decision 0050 is unchanged.

The pending [cheap-stack `dev140`](v0924_cheap_stack_luna_dev140_protocol_2026-08-16.md)
was authorized for the pre-cleanup wording. It is not this study.

## Primary question

On the same frozen 20-letter Luna pool, does the cleaned cheap stack
stay under the leave-one-out stop bars versus saved `v0.9.24`?

This asks whether the language pass changed the cheap-stack cost. It
does not ask whether a smaller stack or a selected-stack change is
warranted.

## Arms

| Arm | Prompt | Calls |
| --- | --- | ---: |
| `v0924_head` | saved Luna `v0.9.24` through HEAD | 0 |
| `previous_cheap` | saved pre-cleanup cheap-stack raws through HEAD | 0 |
| `plain_cheap` | live `v0.9.40_drop_encoding_non_sf_all_examples` after the language pass | 20 |

The live candidate still drops the 16 non-SF encoding rules and all
49 examples. It keeps the 13 SF encoding rules, all scope rules, and
the remaining scaffold, now in ordinary language. Do not invent a new
prompt-version identity.

## Data and scoring

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Same frozen `dev20` as the structural cheap-stack study: EA0002,
  EA0004, EA0005, EA0006, EA0007, EA0008, EA0009, EA0010, EA0011,
  EA0012, EA0015, EA0016, EA0047, EA0074, EA0093, EA0120, EA0131,
  EA0133, EA0154, EA0158.
- Development rows may be inspected. `test60` remains aggregate-only.
- Model: `openai/gpt-5.6-luna`. Temperature 1.0. Cache off. One
  structured hybrid call per letter. Output budget 16000 tokens.
- Control: saved `v0.9.24` raws from
  `experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816/v0924_head/structured.jsonl`,
  replayed through unchanged HEAD assembly.
- Previous cheap: saved pre-cleanup cheap raws from
  `experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816/drop_encoding_non_sf_all_examples/structured.jsonl`,
  replayed through the same assembly.
- Primary: four-family `clinical_headline` F1 versus saved `v0.9.24`.
- Secondary: family F1, four-family letter exact, parse/schema
  failures, changed-row direction, and the same scores versus
  `previous_cheap`. EA0004 and EA0010 remain contamination letters;
  report them separately; do not retune from those two letters.

## Stop rule

Same bars as the leave-one-out series, scored against `v0.9.24`:

- **low_value** if hybrid headline drop < 0.05, no family drop ≥ 0.08,
  and net four-family exact losses < 3.
- **load_bearing** if any of those bars fail. Keep `v0.9.24` as the
  default. The cheap stack stays the retained cheap variant.
- **revise** if parse/schema failures appear or the payload contract
  drifted.

Do not promote. Do not change the default. Do not start `dev140` from
this result. A SeizureFrequency recovery versus `previous_cheap` is a
development observation, not a selected-stack change.

## Minimal implementation change

Write a focused `dev20` runner. Replay both saved arms before paying
for new calls. Call
`set_active_prompt_version(PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES)`
only inside the live arm, then restore `v0.9.24`. Use `.venv`.

## Artifact contract

Study directory:
`experiments/exectv2_v0924_cheap_stack_plain_luna_dev20_20260816/`.

Write `comparison.json` plus the structured sidecars and HEAD
assembly needed to recompute the table. One row per frozen letter.
Record prompt identity, call mode, cache state, parse/schema events,
family scores, and changed-row direction. Do not overwrite the
structural-cut artifact.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not holdout evidence, and not a Decision
0050 change.
