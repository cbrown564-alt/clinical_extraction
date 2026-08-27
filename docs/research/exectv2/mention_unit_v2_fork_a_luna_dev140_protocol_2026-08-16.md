# ExECT mention-unit v2 — GPT-5.6 Luna `dev140` protocol

Date: 2026-08-16  
Status: complete; **revise**  
Plan: [ExECT LLM representation and hybrid re-evaluation](../../plans/exect_llm_representation_and_hybrid_revaluation_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md)  
Prior result: [mention-unit v2 `dev20`](mention_unit_v2_fork_a_luna_dev20_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)  
Glossary: [CONTEXT.md](../../../CONTEXT.md)

Fork A stays. Decision 0050 and `test60` are unchanged. This study
does not retune the prompt or the landed encoder.

## Primary question

On the 140 development letters, does the frozen clinical-name language
still put gold SeizureFrequency wording in `clinical_name`, and do
empty-gold extras stay down versus the saved v4 and trust-item
comparators on those same letters?

`dev20` answered that this language copies the name on that pool
(12/32 → 24/32 exact on `llm`). This study asks whether that mechanism
holds on the rest of development, not whether a new cue finds EA0009.

Headline F1 is context. A gold unit is copied when `clinical_name`
matches the gold wording or the hyphen-normalized gold phrase. A
sentence that merely contains that wording is not a hit.

## Data and row policy

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Split: `dev140` (all loadable development letters).
- Development rows may be inspected. `test60` remains aggregate-only
  and is not authorized.
- Promote nothing.

## Candidate and fixed comparators

- Candidate: unchanged `exectv2_mention_unit_v2` `llm` and matched
  `llm_with_rules`. Same system line, task, form table, seven cues, and
  landed encoder as the `dev20` answer.
- Fixed mention-unit v1: saved v1 raws on the overlapping frozen
  `dev20` letters only. No new v1 calls. Do not treat a 20-letter
  comparison as a 140-letter result.
- Fixed control: saved GPT-5.6 Luna current-stack `v0.9.24` output on
  these 140 letters, replayed through the unchanged control projection.
- Fixed default v4: saved `exectv2_semantic_inventory_v4` `dev140` raws
  from the projection-damage study, rematerialized with the unchanged
  default projector.
- Fixed trust-item: those same v4 `dev140` raws rematerialized with the
  saved `trust_item` policy. Trust-item is a comparator, not the hybrid
  method.
- One independent model call per method per row. Same model,
  temperature, output budget, and provider route.

## Model and generation

- Model: `openai/gpt-5.6-luna`.
- Temperature: 1.0.
- Maximum output tokens: 2400.
- Cache: disabled for fresh candidate calls.

## Method contracts

Unchanged from the [v2 `dev20` protocol](mention_unit_v2_fork_a_luna_dev20_protocol_2026-08-16.md).
Do not edit model-facing text. Do not add an eighth cue. Do not retune
the landed encoder. Leftover words in hybrid evidence remain expected.

## Scoring

Primary decision metric: gold SeizureFrequency wording as
`clinical_name` on the 140 letters, compared with default v4 and
trust-item on those letters. Also report the overlapping `dev20`
letters against saved mention-unit v1.

Secondary: four-family `clinical_headline` (context only), semantic F1,
family F1, extras versus misses, empty-gold extras, non-target mentions,
hybrid growth from unused letter text, and the unread leftover census
on development rows only.

## Minimal implementation change

Add a `dev140` runner that reuses `exectv2_mention_unit_v2`. Do not
change the prompt, parser, or encoder. Do not change gold, the selected
stack, or the v4 / `trust_item` projectors.

## Required checks and stop rules

Before live calls:

- the existing mention-unit v2 contract tests still pass;
- a prompt-only smoke on this runner writes `model_calls`: 0.

After `dev140`, treat the study as `revise` if any of these hold:

- empty-gold SeizureFrequency extras rise versus default v4 or
  trust-item on the 140 letters;
- empty-gold SeizureFrequency extras on the overlapping 20 rise versus
  saved mention-unit v1;
- ECG or other non-target investigations appear;
- hybrid grows mentions from unused letter text.

A mechanically clean `dev140` that still leaves gold wording uncopied,
or still puts that wording inside a sentence, is a valid
`negative_result`. Headline movement alone does not promote.

Do not repair a miss by inspecting `test60`. Do not retune for EA0009
`cluster-of-seizures`, empty-gold extras, bundled drugs, intervening-word
counts, or the EA0015 EEG Unknown extra.

Stop with `answer`, `negative_result`, `revise`, `reject`, or
`blocked_by_instrumentation`.

## Artifact contract

Study directory:
`experiments/exectv2_mention_unit_v2_luna_dev140_20260816/`.

Write `comparison.json`, `rows.jsonl`, and an emission census. One JSON
object per development row with source row ID, prompt hash, raw model
output, parsed items, evidence checks, semantic view, rule trace,
scorer view, gold-wording emission, and comparator keys. `test60`
artifacts remain unauthorized.

## Claim boundary

A `dev140` result can support a development-transfer decision for this
frozen language. It is not clinical validation, holdout evidence, or a
Decision 0050 change.
