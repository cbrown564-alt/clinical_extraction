# Protocol: last-event + short well-since select rewrite

Date: 2026-08-29
Status: promoted on living cell-3 select (cited Gemini `test450` 387/450)
Owner: this file
Report: [pragmatic error mode](gan_pragmatic_infrequent_error_mode_2026-08-29.md)
Holdout artifact: [test450 aggregate](gan_last_event_well_since_test450_2026-08-29.json)

## Primary question

On living Gemini cell 3 select, can a gated rewrite turn a short
seizure-free label into `N per <interval>` (or `1 per <interval>`)
when find already has a named last event and a well-since interval,
without converting true seizure-free gold?

## Why this study

Ten dest750 infrequent → no-seizure misses keep a short seizure-free
span after a dated last event. Rules-only recovers eight. A blanket
“seizure-free under 6 months is invalid” rewrite would harm twelve
already-correct `seizure free for 2–5 month` rows against gold
`seizure free for multiple month`.

## Scope

- Dataset: Gan `dev750`. `test450` not loaded.
- Candidate: new select family `last_event_well_since` on
  `llm_select_after_codebook` (default on with other living select
  families). Encode-only modes keep it off.
- No gold at runtime. No new model calls.
- Scorer: living Purist / Pragmatic. Primary: dest750 select
  pragmatic on the ten infrequent → no-seizure rows; secondary:
  full-split Purist/Pragmatic vs living 649 / 665 and zero harm on
  the twelve short-SF-correct rows.
- Gate: current label is numeric `seizure free for N week|month`
  with duration under 6 months; well-since marker; and either a
  day-dated last-event event or an explicit burst count on a
  last-event / frequency event. Week spans of 5 weeks or less rewrite
  to a monthly rate so `1 per 3 week` does not become frequent.
  Burst count is a nearby `N seizures|events|episodes` phrase, not a
  calendar day.

## Stop rule

Accept if dest750 net Purist is not negative and the twelve
short-SF-correct rows stay pragmatic-correct. Reject if any of those
twelve flip. `test450` stays sealed.

## Measured (`dev750`, Gemini extract replay, no new calls)

Replay of saved `gan_llm_extract` raws through living
`llm_select_after_codebook` with the family on, versus the same
replay with it off (identical to stored rung select **649 / 665**).

| Surface | Off (living) | On (candidate) | Δ |
| --- | ---: | ---: | ---: |
| Purist | 649 | 656 | +7 |
| Pragmatic | 665 | 673 | +8 |

- Ten infrequent → no-seizure rows: **7** pragmatic rescues (all
  numeric short-SF letters). The three `seizure free for multiple
  month` letters are unchanged, as gated.
- Twelve short-SF-correct gold-SF rows: **0** pragmatic harms.
- Extra rescues: 1165 (`5 to 7 per 3 week` gold; cluster count over
  a six-week well-since). Score-neutral gold-unknown rewrites:
  11254, 11272 (`1 per 3 month` vs prior short SF).
- 14806 is pragmatic-only (`1 per month` vs gold `1 per 2 month`).

## Holdout replay (`test450`)

Predeclared as aggregate-only confirmation after the `dev750` accept.
Saved `gan_llm_extract` raws through `llm_select_after_codebook` with
the family on versus off. No new model calls. No holdout row ids,
labels, notes, or changed-row lists. Do not retune from this replay.
Cited cell-3 / five-cell tables stay on the sealed rung artifacts.

Measured (family off matches stored rung select **374 / 383**):

| Surface | Off (living) | On (candidate) | Δ |
| --- | ---: | ---: | ---: |
| Purist | 374 | 387 | +13 |
| Pragmatic | 383 | 396 | +13 |

13 labels changed; 13 Purist and 13 Pragmatic gains; 0 losses.
Pragmatic infrequent → no-seizure **13 → 1**; infrequent correct
**49 → 61**. Infrequent → unknown and frequent → unknown stay 16 and
13. Gold seizure-free diagonal stays 57.

## Claim boundary

Development candidate plus holdout aggregate confirmation. Not a
cited score until a separate promotion study. Cited cell-3 `dev750`
649 / 665 and `test450` 374 / 383 stay on the sealed rung artifacts.
