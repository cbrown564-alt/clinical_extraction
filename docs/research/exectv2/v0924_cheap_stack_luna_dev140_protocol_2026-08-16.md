# Protocol: ExECT `v0.9.24` cheap-slice stack on Luna `dev140`

Date: 2026-08-16  
Status: **complete**; live transfer scored; **load_bearing**  
Parent: [cheap-stack `dev20`](v0924_cheap_stack_luna_dev20_2026-08-16.md)  
Assignment: [prompt variant slots](prompt_variant_slots_2026-08-16.md)  
Authorization: user authorized this `dev140` transfer on 2026-08-16

The `dev20` cheap stack is **load_bearing** on SeizureFrequency
(−0.0929). The slot assignment withheld `dev140` until authorized.
This study is that transfer measurement. `v0.9.24` stays the default.
`test60` is sealed. Decision 0050 is unchanged.

The live candidate is the cleaned cheap stack. The frozen-20
language scoring is
[plain-language `dev20`](v0924_cheap_stack_plain_luna_dev20_2026-08-16.md).
SeizureFrequency stayed −0.0929 on that pool. This transfer scores
the same live wording on all 140 development letters.

## Primary question

On the 140 development letters, does the retained cheap stack stay
under the leave-one-out stop bars versus saved Luna `v0.9.24`?

`dev20` answered that the four cheap cuts do not stay cheap together
on that pool. This study asks whether the same family bar holds on
the rest of development. It does not ask whether a smaller stack, a
new prompt, or a selected-stack change is warranted.

## Arms

| Arm | Prompt | Calls |
| --- | --- | ---: |
| `v0924_head` | saved Luna `v0.9.24` through HEAD | 0 |
| `drop_encoding_non_sf_all_examples` | `exectv2_hybrid_key_family_event_ledger_v0.9.40_drop_encoding_non_sf_all_examples` | 140 |

The candidate keeps scaffold, the 13 SF encoding rules, and all
scope rules. It drops the 16 diagnosis/Rx/Ix encoding rules and all
49 examples. That identity is already live as slot 2. Do not invent
a new prompt version.

## Data and scoring

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Split: `dev140` (all loadable development letters).
- Development rows may be inspected. `test60` remains aggregate-only
  and is not authorized.
- Model: `openai/gpt-5.6-luna`. Temperature 1.0. Cache off. One
  structured hybrid call per letter. Output budget matches the
  `dev20` cheap-stack run (16000 tokens).
- Control: saved GPT-5.6 Luna current-stack `v0.9.24` structured
  output
  `experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl`,
  replayed through unchanged HEAD assembly. No new `v0.9.24` calls.
- Primary: four-family `clinical_headline` F1 through unchanged HEAD
  assembly, versus that saved control on the same 140 letters.
- Secondary: family F1, four-family letter exact, parse/schema
  failures, and changed-row direction. Report the overlapping frozen
  `dev20` letters separately against the saved cheap-stack `dev20`
  artifact. Do not treat that 20-letter slice as the 140-letter
  result.

## Stop rule

Same bars as the leave-one-out series:

- **low_value** if hybrid headline drop < 0.05, no family drop ≥ 0.08,
  and net four-family exact losses < 3.
- **load_bearing** if any of those bars fail. Keep `v0.9.24` as the
  default. The cheap stack stays the retained cheap variant.
- **revise** if parse/schema failures appear or the payload contract
  drifted.

Do not promote. Do not change the default. Do not start a new cheap
cut from this result. A `dev20` SF drop that shrinks on `dev140` is
still not a selected-stack change.

## Minimal implementation change

Write a focused `dev140` runner for this one arm. Recover live
structured-prompt remasure helpers from git history if that is
faster than a new script. Call
`set_active_prompt_version(PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES)`
only inside the candidate arm, then restore `v0.9.24`. Use
`.venv`. Prefer replaying the saved control before paying for new
calls.

## Artifact contract

Study directory:
`experiments/exectv2_v0924_cheap_stack_luna_dev140_20260816/`.

Write `comparison.json` plus the candidate structured sidecar and
HEAD assembly needed to recompute the table. One row per
development letter. Record prompt identity, call mode, cache state,
parse/schema events, family scores, and changed-row direction.
`test60` artifacts are not authorized.

## Claim boundary

A `dev140` result can support a development-transfer decision for
the retained cheap variant. It is not clinical validation, not
holdout evidence, and not a Decision 0050 change.
