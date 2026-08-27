# Protocol: mention-unit v2 leftover-form v2 knobs on Luna `dev140`

Date: 2026-08-16  
Status: complete; four-arm **revise**  
Result: [leftover-form v2](mention_unit_v2_leftover_form_v2_luna_dev140_2026-08-16.md)  
Prior: [leftover-form v1](mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

Fork A stays. Mention-unit v2 language stays frozen. Default encoder
stays `landed`. Decision 0050 and `test60` are unchanged. No new
model calls.

Leftover-form v1 recovered SF-with-count **58 → 130** and
Investigations Unknown **61 → 2**. The remaining 104 unparsed counts
are a different parse question. This study tests four named knobs
independently against leftover-form v1. It does not stack them.

## Primary question

On the saved mention-unit v2 hybrid raws, which one leftover-form
parse change recovers remaining SeizureFrequency form, or keeps a
case-only name that exact substring dropped, without searching the
letter?

Each arm answers one knob. A later stack is a new protocol.

## Arms

| Arm | Encoder | One knob |
| --- | --- | --- |
| `leftover_form` | `exectv2_mention_unit_leftover_form_v1` | Fixed comparator. Unchanged. |
| `intervening` | `leftover_form_intervening` | Count near `seizures` / `absences` / `jerks` with typed words in between, plus `N times a unit` and `N in the last …`. Duration years stay out. |
| `implicit_period` | `leftover_form_implicit_period` | Bare `every week/year` and named `daily` with no number become count 1 plus period. `every N weeks` stays with the landed interval completer. |
| `casefold` | `leftover_form_casefold` | Case-insensitive letter membership for `clinical_name` and `evidence`. Exact match still wins. Plural, paraphrase, and absent names stay dropped. |
| `last_event` | `leftover_form_last_event` | Widen leftover last-event / seizure-free cues to `seizure last month`, `event last week`, `no events since`, and `seizures free` / `seizrue free`. Do not add qualitative change. |

Landed and saved `llm` stay recorded context. Do not change
`materialize_mention_unit` default.

## Data and scoring

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Split: `dev140`. Development rows may be inspected. `test60` is not
  authorized.
- Input: saved mention-unit v2 `dev140` `rows.jsonl` only. Replay
  hybrid `raw_output`. `model_calls` must be 0.
- Do not treat the leftover-form damage catalog as a tuning set.
  Rules come from the leftover-word contract, List 11, and the
  already-landed last-event / interval encoder.
- Primary, per arm versus leftover-form v1: SF mentions with a
  count; remaining `count_unparsed`; for `casefold`,
  `text_not_substring_drop`.
- Secondary: four-family `clinical_headline` (context), empty-gold
  SF extras, names rewritten, Investigations Unknown, ECG /
  non-targets, `suppress_uncoded_sf`.

## Stop rule

Score each arm against leftover-form v1 before the next.

- **answer** if the named leftover class moves in the intended
  direction, extras do not rise versus leftover-form v1, names are
  not rewritten more, and ECG stays out.
- **reject** if the named leftover class does not move.
- **revise** if extras rise, duration tokens become counts, ECG is
  emitted, or names are rewritten more.
- **blocked_by_instrumentation** if leftover-form v1 rematerialization
  cannot reproduce the saved leftover-form census (SF-with-count
  130; Investigations Unknown 2).

Do not promote an arm to the default encoder. Do not start
mention-unit v3 or Fork B. Do not inspect `test60`. Do not retune
the prompt. Do not stack winning arms in this study.

## Minimal implementation change

Add four named leftover-form encoder variants beside unchanged
`leftover_form` v1. Case-fold lives only on the `casefold` arm
inside mention-unit materialization. It must not change
`evidence_is_substring` for landed or leftover-form v1.

## Artifact contract

Study directory:
`experiments/exectv2_mention_unit_v2_leftover_form_v2_luna_dev140_20260816/`.

Write `comparison.json`, `rows.jsonl`, and `damage_catalog.json`.
One object per development letter with leftover-form v1 and the
four candidate rematerializations. `model_calls` must be 0.

## Claim boundary

A `dev140` remasure of saved mention-unit v2 hybrid raws. It is not
clinical validation, holdout evidence, a Decision 0050 change, or
authorization to inspect `test60`.
