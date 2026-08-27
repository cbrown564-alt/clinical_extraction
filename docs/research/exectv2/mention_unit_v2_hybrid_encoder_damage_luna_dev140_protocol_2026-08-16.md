# ExECT mention-unit v2 hybrid encoder damage — `dev140` protocol

Date: 2026-08-16  
Status: complete; **answer**  
Prior: [mention-unit v2 `dev140`](mention_unit_v2_fork_a_luna_dev140_2026-08-16.md)  
Extras: [empty-gold extras catalog](mention_unit_v2_empty_gold_sf_extras_luna_dev140_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

Fork A stays. Decision 0050 and `test60` are unchanged. This study
does not retune the prompt or the landed encoder. No new model calls.

## Primary question

On the saved mention-unit v2 `dev140` rows, which named hybrid rules
lose SeizureFrequency form or Investigations results that the matched
`llm` lane already scored from the same frozen language?

The transfer report left this as expected leftover: hybrid SF
**0.3167** versus `llm` **0.6225**, Investigations **0.4788** versus
**0.9027**. Names were copied. This catalog asks whether the landed
encoder is the owner of those family drops.

## Data and row policy

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Split: `dev140`. Development rows may be inspected. `test60` is not
  authorized.
- Input: saved mention-unit v2 `dev140` `rows.jsonl` only. No
  rematerialization that changes those predictions. No new calls.

## Candidate and fixed comparators

- Candidate: mention-unit v2 `llm_with_rules` semantic facts, rule
  traces, and scored mentions.
- Fixed: mention-unit v2 `llm` scored mentions on the same letters.
  These are matched independent calls, not one raw through two
  projectors.
- Control hybrid and v4 stay recorded context from the transfer study.

## Classes

| Class | Meaning |
| --- | --- |
| `count_unparsed` | Hybrid SF mention lacks a count or range attribute |
| `result_unknown` | Hybrid Investigations mention has an `Unknown` result |
| `suppress_uncoded_sf` | `suppress_uncoded_or_noise_sf` deleted the item before encoding |
| `text_not_substring_drop` | Hybrid SF fact dropped because `clinical_name` is not a letter substring |
| `name_rewritten` | Hybrid scorer text differs from emitted `clinical_name` |

`last_event_zero` is recorded as an overlay. It is not automatically
damage: last-event language is supposed to become `NumberOfSeizures=0`.

## Scoring

Primary: class counts; hybrid versus `llm` SF mentions with a count;
hybrid versus `llm` Investigations Normal/Abnormal versus Unknown.

Secondary: whether suppressed names are gold SF units; whether
`clinical_name` was kept. Headline F1 is context.

## Minimal implementation change

Add a no-call catalog script that reads the saved rows. Do not change
gold, the selected stack, the v2 prompt, or the encoder.

## Required checks and stop rules

- `model_calls` must be 0.
- `answer` if one or two named mechanisms own the SF and
  Investigations family drops.
- `revise` if the drops do not partition into the classes above.
- Do not retune the prompt or the encoder from this catalog. Do not
  start mention-unit v3 or Fork B. Do not inspect `test60`.

Stop with `answer`, `revise`, `reject`, or `blocked_by_instrumentation`.

## Artifact contract

Study directory:
`experiments/exectv2_mention_unit_v2_hybrid_encoder_damage_luna_dev140_20260816/`.

Write `damage_catalog.json` with class counts, per-item records, and
the claim boundary.

## Claim boundary

A development catalog of mention-unit v2 hybrid encoder leftover. It
is not clinical validation, holdout evidence, or a Decision 0050
change.
