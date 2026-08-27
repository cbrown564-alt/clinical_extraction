# Protocol: mention-unit v2 leftover-form v3 intervening counts on Luna `dev140`

Date: 2026-08-16  
Status: complete; **answer**  
Result: [leftover-form v3](mention_unit_v2_leftover_form_v3_luna_dev140_2026-08-16.md)  
Prior: [leftover-form v2](mention_unit_v2_leftover_form_v2_luna_dev140_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

Fork A stays. Mention-unit v2 language stays frozen. Default encoder
stays `landed`. Decision 0050 and `test60` are unchanged. No new
model calls. Do not retry implicit period, case-fold, or last-event
in this study.

Leftover-form v2 intervening recovered SF-with-count **130 → 172**
and failed inspection: age, duration / last-event span, and a
calendar date became counts. This study retries intervening counts
only, with the three false-read guards written here before any code.

## Primary question

On the saved mention-unit v2 hybrid raws, do intervening leftover
counts rise versus leftover-form v1 without taking a count from age,
duration / last-event span, or a calendar date?

## Arms

| Arm | Encoder | Role |
| --- | --- | --- |
| leftover-form v1 | `leftover_form` | Fixed comparator. Unchanged. |
| intervening v2 | `leftover_form_intervening` | Recorded unsafe baseline. Unchanged. |
| intervening v3 | `leftover_form_intervening_v3` | Candidate. Same intervening parse as v2, plus the three guards. |

Landed and saved `llm` stay recorded context. Do not change
`materialize_mention_unit` default. Do not retune the v2 intervening
arm; the v2 revise result must stay reproducible.

## False-read guards

Write these into the encoder before remasure. They are general
predicates on the matched count span, not letter-specific patches.

1. Do not take a count from age (`at the age of 3`, `age of 8`).
2. Do not take a count from duration or last-event span
   (`6 months without`, `two weeks ago`, `for around three weeks`).
   A matched number immediately followed by a time unit is a time
   quantity, not a seizure count.
3. Do not take a count from a calendar date (`22 December`).

True recoveries that must still land: `2 febrile seizures`,
`four in the last three weeks`, `a couple of focal impaired
awareness seizures`, `1 since previous appointment`.

Do not treat the leftover-form damage catalog as a tuning set.
Rules come from the leftover-word contract and the three named
guards.

## Data and scoring

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Split: `dev140`. Development rows may be inspected. `test60` is not
  authorized.
- Input: saved mention-unit v2 `dev140` `rows.jsonl` only. Replay
  hybrid `raw_output`. `model_calls` must be 0.
- Primary versus leftover-form v1: SF mentions with a count;
  remaining `count_unparsed`.
- Secondary: four-family `clinical_headline` (context), empty-gold
  SF extras, names rewritten, Investigations Unknown, ECG /
  non-targets.
- Guard check: a newly recovered count is a guard failure when every
  occurrence of that number in the mention haystack
  (`clinical_name` plus evidence) is an age, duration / last-event,
  or calendar span.

## Stop rule

- **answer** if intervening counts rise versus leftover-form v1,
  extras do not rise, names are not rewritten more, ECG stays out,
  and the three false-read classes do not become counts.
- **reject** if SF-with-count does not rise versus leftover-form v1.
- **revise** if extras rise, names are rewritten more, ECG is
  emitted, or any of the three false-read classes still becomes a
  count.
- **blocked_by_instrumentation** if leftover-form v1 rematerialization
  cannot reproduce the saved leftover-form census (SF-with-count
  130; Investigations Unknown 2).

Do not promote leftover-form to the default encoder from this
remasure alone. Do not start mention-unit v3 or Fork B. Do not
inspect `test60`. Do not retune the prompt. Do not stack other v2
knobs.

## Minimal implementation change

Add `leftover_form_intervening_v3` beside unchanged
`leftover_form` and `leftover_form_intervening`. The v3 arm may skip
a guarded span and take a later allowed intervening count in the
same haystack. It must not search the letter.

## Artifact contract

Study directory:
`experiments/exectv2_mention_unit_v2_leftover_form_v3_luna_dev140_20260816/`.

Write `comparison.json`, `rows.jsonl`, and `damage_catalog.json`.
One object per development letter with leftover-form v1, intervening
v2, and intervening v3 rematerializations. `model_calls` must be 0.

## Claim boundary

A `dev140` remasure of saved mention-unit v2 hybrid raws. It is not
clinical validation, holdout evidence, a Decision 0050 change, or
authorization to inspect `test60`.
