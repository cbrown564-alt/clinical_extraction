# Protocol: ExECT cheap-stack slot 2 `dev140` remasure

Date: 2026-08-17  
Status: **in progress**; user reassigned slot 2 and authorized this transfer  
Parent: [stacked further prune](v0924_cheap_further_prune_stacked_luna_dev20_2026-08-17.md)  
Assignment: [prompt variant slots](prompt_variant_slots_2026-08-16.md)

The Luna `dev20` stacked further prune stayed **low_value** versus the
cleaned `v0.9.40` cheap stack. That result withheld `dev140` and kept
slot 2 on `v0.9.40`. The user disagrees with that stop and assigns the
stacked identity as slot 2.

This study measures that new slot-2 prompt on `dev140` for three
models. `v0.9.24` stays the live default. Decision 0050 is unchanged.
`test60` is sealed.

## Primary question

On the 140 development letters, how does slot 2
(`v0.9.44_cheap_stack_further_prunes`) score versus each model's saved
`v0.9.24` through unchanged HEAD assembly?

That asks whether the stacked cheap stack stays under the leave-one-out
stop bars on the rest of development, and whether that transfer holds
for Luna, Gemini 3.7 Flash, and Qwen 3.8 27B. It does not ask whether
slot 2 should replace `v0.9.24`.

## Arms

| Arm | Prompt | Calls |
| --- | --- | ---: |
| `v0924_head` | saved same-model `v0.9.24` through HEAD | 0 for Luna and Gemini; Qwen deferred |
| `slot2` | `exectv2_hybrid_key_family_event_ledger_v0.9.44_cheap_stack_further_prunes` | 140 per model |

The candidate is the cleaned cheap stack plus the three scored further
cuts: investigation-pending collapse, scaffold-reprint drop, and
refuse-chorus collapse. That identity is now slot 2. Do not invent a
new prompt version.

## Models

| Slug | Runtime | Temperature | Control sidecar |
| --- | --- | ---: | --- |
| `luna` | `openai/gpt-5.6-luna` | 1.0 | `experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl` |
| `gemini` | `gemini/gemini-3.7-flash` via OpenRouter | 0.0 | `experiments/exectv2_six_model_single_call_gemini37flash_dev140_20260813_structured.jsonl` |
| `qwen` | `ollama_chat/qwen3.8:27b` | 0.0 | deferred; 12 saved letters only |

Qwen is the reserved local successor (`qwen3.8:27b`), not the
six-model `qwen3.6:35b` tag. Completing a same-model `v0.9.24`
sidecar is authorized later and is not required to start the slot-2
run. Do not inspect `test60`. Do not treat this as a Decision 0051
roster swap.

Gemini uses OpenRouter (`OPENROUTER_API_KEY`). Luna uses
`OPENAI_API_KEY`. Qwen is local Ollama.

Cache off. One structured hybrid call per letter. Output budget 16000
tokens. Temperature matches each model's saved `v0.9.24` control,
except Luna stays 1.0 to match the cheap-stack series.

## Data and scoring

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Split: `dev140` (all loadable development letters).
- Development rows may be inspected. `test60` remains aggregate-only
  and is not authorized.
- Control: Luna and Gemini replay saved same-model `v0.9.24`
  structured output through unchanged HEAD assembly. Qwen slot-2
  raws are collected first; the Qwen `v0.9.24` sidecar may be
  completed after. No new Luna or Gemini `v0.9.24` calls.
- Primary: four-family `clinical_headline` F1 versus the saved
  control on the same 140 letters, once that control exists. Qwen
  stop-bar scoring waits for the later sidecar.
- Secondary: family F1, four-family letter exact, parse/schema
  failures, and changed-row direction. Report each model separately.
  Do not pool models into one headline.

## Stop rule

Same bars as the leave-one-out series, scored per model against that
model's saved `v0.9.24`:

- **low_value** if hybrid headline drop < 0.05, no family drop ≥ 0.08,
  and net four-family exact losses < 3.
- **load_bearing** if any of those bars fail. Keep `v0.9.24` as the
  default. Slot 2 stays the retained cheap variant.
- **revise** if parse/schema failures appear or the payload contract
  drifted.

Do not promote slot 2 to the live default from this remasure. Do not
inspect `test60`. A model that stays under the bars is not a selected
stack.

## Minimal implementation change

Write one `dev140` runner with a `--model` switch. Call
`set_active_prompt_version(PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES)`
only inside the candidate arm, then restore `v0.9.24`. Use `.venv`.
Replay each saved control before paying for new calls. Resume from a
partial structured sidecar.

## Artifact contract

Study directories:

- `experiments/exectv2_v0924_cheap_slot2_luna_dev140_20260817/`
- `experiments/exectv2_v0924_cheap_slot2_gemini_dev140_20260817/`
- `experiments/exectv2_v0924_cheap_slot2_qwen_dev140_20260817/`

Write `comparison.json` plus the candidate structured sidecar and HEAD
assembly needed to recompute the table. One row per development
letter. Record prompt identity, model, call mode, cache state,
parse/schema events, family scores, and changed-row direction.
`test60` artifacts are not authorized.

## Claim boundary

A `dev140` result can support a development-transfer decision for the
reassigned cheap slot. It is not clinical validation, not holdout
evidence, and not a Decision 0050 change.
