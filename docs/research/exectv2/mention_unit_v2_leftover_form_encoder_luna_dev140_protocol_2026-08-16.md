# ExECT mention-unit v2 leftover-form encoder — `dev140` protocol

Date: 2026-08-16  
Status: complete; **answer**  
Result: [leftover-form remasure](mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md)  
Prior: [hybrid encoder damage catalog](mention_unit_v2_hybrid_encoder_damage_luna_dev140_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

Fork A stays. Decision 0050 and `test60` are unchanged. Mention-unit
v2 language stays frozen. This study does not retune the prompt or
the landed encoder. No new model calls.

## Primary question

On the saved mention-unit v2 hybrid raws, does a leftover-form
encoder recover SeizureFrequency count or period and Investigations
results from that item’s `clinical_name` plus `evidence`, without
searching the letter?

The damage catalog is an **answer**: names stay; form does not.
Hybrid SF mentions with a count are **58/232** versus `llm` **224/267**.
Investigations Unknown are **61** versus `llm` **1**. This remasure
asks whether parsing leftover evidence words closes that form gap.
It does not ask whether a new prompt copies names better.

## Data and row policy

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Split: `dev140`. Development rows may be inspected. `test60` is not
  authorized.
- Input: saved mention-unit v2 `dev140` `rows.jsonl` only. Replay
  `raw_output` through `parse_mention_unit_json` and
  `materialize_mention_unit`. Zero new model calls.
- Do not treat the damage-catalog item list as a tuning set. Encoder
  rules come from the signed-off leftover-word contract, List 9, List
  11, and the already-landed interval / last-event encoder.

## Candidate and fixed comparators

- Candidate: the same hybrid raws rematerialized with encoder
  `leftover_form`.
- Fixed landed comparator: the same hybrid raws rematerialized with
  encoder `landed` (current default).
- Fixed `llm`: saved mention-unit v2 `llm` predictions on the same
  letters. Matched independent calls, not one raw through two
  projectors.
- Control hybrid and v4 stay recorded context from the transfer study.
- Default `materialize_mention_unit` stays `landed`. Selected
  `v0.9.24` is unchanged.

## Component under study

Deterministic leftover-form parsing on an already-emitted mention-unit
item. Rules may read that item’s `clinical_name` and exact `evidence`.
They may not search unrelated letter text or grow a new mention set.

The candidate must:

1. Parse leftover count or range and period from `clinical_name` plus
   `evidence` before uncoded-phenomenology suppression. Empty
   attributes must not suppress an item that still has leftover form
   words.
2. Leave `every N days/weeks/months/years` to the landed interval
   completer. Do not encode that `N` as `NumberOfSeizures`.
3. Map leftover word counts through `normalize_count` (List 11). Do
   not encode “four years” as a seizure count.
4. Classify investigation results with the landed List 9 table on that
   item’s name plus evidence when the explicit
   `normal|abnormal|negative|unremarkable` tokens are absent. Keep the
   MRI/CT/EEG modality gate. Drop ECG.
5. Keep last-event language as `NumberOfSeizures=0`. Keep heading
   splits and prescription rules on the landed path.

## Scoring

Primary: hybrid SF mentions with a count; hybrid Investigations
Normal/Abnormal versus Unknown; remaining `count_unparsed`,
`result_unknown`, and `suppress_uncoded_sf` class counts.

Secondary: four-family `clinical_headline`; empty-gold SF extras
versus landed hybrid; `clinical_name` kept versus rewritten;
`text_not_substring_drop`; ECG or other non-targets. Headline F1 is
context, not a promotion bar.

## Minimal implementation change

Add a named `leftover_form` encoder beside default `landed` on
`materialize_mention_unit`. Do not change gold, the selected stack,
the v2 prompt, or default landed encoding used by `v0.9.24`.

## Required checks and stop rules

Before remasure:

- contract tests still pass with default `landed` unchanged;
- new always-on tests pin leftover-form obligations 1–5;
- a remasure smoke writes `model_calls: 0`.

After remasure:

- `answer` if leftover-form raises SF-with-count or lowers
  Investigations Unknown versus landed, the remaining leftover is
  named, and stop checks stay clear;
- `revise` if empty-gold SF extras rise versus landed hybrid, duration
  tokens become counts, ECG is emitted, or names are rewritten more
  than landed;
- `reject` if neither SF-with-count nor Investigations known-result
  moves versus landed;
- `blocked_by_instrumentation` if landed rematerialization cannot
  reproduce the saved hybrid form census;
- do not inspect `test60`;
- do not start mention-unit v3 or Fork B;
- do not promote leftover-form to the default encoder from this
  remasure alone.

Stop with `answer`, `revise`, `reject`, or `blocked_by_instrumentation`.

## Artifact contract

Study directory:
`experiments/exectv2_mention_unit_v2_leftover_form_encoder_luna_dev140_20260816/`.

Write `comparison.json`, `rows.jsonl`, and `damage_catalog.json`. One
JSON object per development row with source row ID, both hybrid
encoders, saved `llm`, rule traces, and scorer views. `model_calls`
must be 0.

## Claim boundary

A `dev140` remasure of saved mention-unit v2 hybrid raws. It is not
clinical validation, holdout evidence, a Decision 0050 change, or
authorization to inspect `test60`.
