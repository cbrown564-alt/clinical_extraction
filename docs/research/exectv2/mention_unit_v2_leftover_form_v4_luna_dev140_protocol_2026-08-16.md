# Protocol: mention-unit v2 leftover-form v4 remaining leftover-word contracts on Luna `dev140`

Date: 2026-08-16  
Status: complete; episodes **answer**, implicit period v4 **answer**, last-event v4 **revise**  
Result: [leftover-form v4](mention_unit_v2_leftover_form_v4_luna_dev140_2026-08-16.md)  
Prior: [leftover-form v3](mention_unit_v2_leftover_form_v3_luna_dev140_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

Fork A stays. Mention-unit v2 language stays frozen. Default encoder
stays `landed`. Decision 0050 and `test60` are unchanged. No new
model calls. Do not treat the remaining 70 `count_unparsed` rows as
a tuning set. Do not turn qualitative rate or change into a count.
Do not invent a number for an unnumbered cluster.

Leftover-form v3 answered intervening counts with age, duration, and
calendar guards (130 → 164). The leftover is a different word
contract, not a wider intervening net. This study tests three named
contracts independently, each on top of leftover-form v3. It does
not stack them.

## Primary question

On the saved mention-unit v2 hybrid raws, which one remaining
leftover-word contract recovers SeizureFrequency form versus
leftover-form v3 without the false read that already revised that
class?

## Arms

| Arm | Encoder | One contract |
| --- | --- | --- |
| intervening v3 | `leftover_form_intervening_v3` | Fixed comparator. Unchanged. |
| episodes | `leftover_form_episodes_v4` | `events` / `episodes` are seizure-count hosts. |
| implicit period v4 | `leftover_form_implicit_v4` | Bare `every unit`, `daily` / `weekly` / `monthly` / `yearly`, and `on a weekly basis` become count 1 plus period. |
| last-event v4 | `leftover_form_last_event_v4` | Widen last-event / seizure-free zeros, but read cues from evidence only. |

Landed, leftover-form v1, and saved `llm` stay recorded context.
Do not change `materialize_mention_unit` default. Do not retune
unsafe v2 intervening, implicit, or last-event arms.

## False-read guards

Write these into the encoder before remasure. They are general
predicates, not letter-specific patches.

Episodes:

1. Keep the leftover-form v3 age, duration / last-event span, and
   calendar-date guards.
2. Do not take a count from a collapse / faint / fall / syncope
   episode.
3. Do not take a count from `stopped the episodes` / `stopped the
   events`.

Implicit period v4:

1. Do not fill 1 when the period is an `ago` span (`a week ago`).
2. Do not fill 1 when a several-times or `N or M times` rate is
   already in the haystack, and do not overwrite an already-parsed
   count.

Last-event v4:

1. Search last-event / seizure-free cues in evidence only. Do not
   let `clinical_name` glue onto `Last month`.
2. Do not zero when evidence already has `cluster of` plus a number.
3. Do not add qualitative change (`increase`, `worse`) as a zero or
   a count.

True recoveries that must still land: leftover-form v3 intervening
counts; `three or four further episodes`; `Myoclonic jerks daily`
and `every year` as 1/period; `seizrue free` / `No events since
surgery` / `seizure last month` as 0.

## Data and scoring

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Split: `dev140`. Development rows may be inspected. `test60` is not
  authorized.
- Input: saved mention-unit v2 `dev140` `rows.jsonl` only. Replay
  hybrid `raw_output`. `model_calls` must be 0.
- Primary, per arm versus leftover-form v3: SF mentions with a
  count; remaining `count_unparsed`.
- Secondary: four-family `clinical_headline` (context), empty-gold
  SF extras, names rewritten, Investigations Unknown, ECG /
  non-targets.
- Guard check: a newly recovered count is a guard failure when it
  comes from age, duration / last-event span, a calendar date, a
  collapse episode, or `stopped the episodes`.

## Stop rule

Score each arm against leftover-form v3 before the next.

- **answer** if the named leftover class moves in the intended
  direction, extras do not rise versus leftover-form v3, names are
  not rewritten more, ECG stays out, and the named false-read
  classes do not become counts or false zeros.
- **reject** if the named leftover class does not move.
- **revise** if extras rise, names are rewritten more, ECG is
  emitted, a named false-read class fires, implicit 1 lands on
  `ago` or overwrites a several-times rate, or last-event zeros a
  counted cluster.
- **blocked_by_instrumentation** if leftover-form v3 rematerialization
  cannot reproduce the saved leftover-form v3 census (SF-with-count
  164; Investigations Unknown 2).

Do not promote leftover-form to the default encoder. Do not start
mention-unit v3 or Fork B. Do not inspect `test60`. Do not retune
the prompt. Do not stack winning arms in this study.

## Minimal implementation change

Add three named leftover-form encoder variants beside unchanged
`leftover_form_intervening_v3`. Each arm starts from the v3
intervening parse and adds one contract.

## Artifact contract

Study directory:
`experiments/exectv2_mention_unit_v2_leftover_form_v4_luna_dev140_20260816/`.

Write `comparison.json`, `rows.jsonl`, and `damage_catalog.json`.
One object per development letter with leftover-form v3 and the
three candidate rematerializations. `model_calls` must be 0.

## Claim boundary

A `dev140` remasure of saved mention-unit v2 hybrid raws. It is not
clinical validation, holdout evidence, a Decision 0050 change, or
authorization to inspect `test60`.
