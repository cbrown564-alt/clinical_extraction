# Predeclaration — SF magnitude-complement probe (2026-07-08)

Date: 2026-07-08. Owner: ExECTv2 workstream.
Hypothesis: `sf_magnitude_complement_2026-07-08` (PENDING).
Driver: `scripts/run_exectv2_sf_magnitude_complement.py` (~28 gpt-4.1-mini calls,
dev140, temp 0, cached, replay mode over the saved v08 hybrid artifact).
Prior art: `sf_direction_vocab_deconflation_2026-07-08` (registry entry 38,
MAGNITUDE IS PART OF THE GAP, NOT ALL OF IT) — the deconflation probe that
measured the selector's magnitude recall deficit (0.845 vs the rules' 0.957,
13 dropped facts) alongside its *higher* magnitude precision (0.9515 vs
0.9328). This probe tests the production design that decomposition made
precisely motivated.
Umbrella: open follow-up pathway #1 from `PROJECT_STATUS.md` Next (2026-07-08),
the four-pathway queue from the predecessor-synthesis follow-ups
(`docs/plans/predecessor_synthesis_followups_2026-07-06.md`) and the 07-08
deconflation probe.

## Purpose (the question)

The deconflation probe decomposed the rules-vs-selector integration gap
(+0.0564 on the conflated `state_profile_directional`) onto two orthogonal
axes and found **~60% of the gap is the magnitude axis**: the rules recover
111/116 magnitude facts (recall 0.957) while the selector recovers 98/116
(recall 0.845) — the selector **drops 13 magnitude facts** the rules catch.
This is the integration ledger's "selector systematically abandons
Frequent/Infrequent" signature, now measured cleanly and separated from the
direction axis.

But the same decomposition surfaced a sharper, exploitable asymmetry: **when
the selector *does* emit a magnitude it is right more often than the rules**
(magnitude precision 0.9515 vs 0.9328). Its problem is recall, not
correctness. And the deterministic `rules/change.py` magnitude regexes
(`change.frequent` / `change.infrequent`) have no match on a substantial
share of the direction-in-play letters — the integration doc cited "21/25
letters with no deterministic cue" as a prose claim.

**This probe tests the complement design that asymmetry implies:** fire the
closed-option selector **only** on letters where the deterministic magnitude
regexes had no match, asking the LLM a *magnitude-only* question (does this
letter state a frequency-magnitude: Frequent / Infrequent, or neither?), and
let the rules own magnitude everywhere they already fire. The question is:
**does restricting the selector to the no-match subset — where the rules are
silent on magnitude — recover magnitude recall without sacrificing the
selector's precision edge, beating both prior arms?**

This is the highest-leverage production pathway from the 07-08 queue because
it is the one that could yield a *genuine production improvement* (a
deterministic-LLM complementarity result for the paper) rather than only a
diagnostic decomposition.

## Why replay mode, not production wiring (scope freeze)

The integration probe (item 2 follow-up) wired the selector to *replace* the
deterministic rules across the whole hybrid SF lane and lost (−0.0563). That
established that a full replacement is negative-for-production-wiring. This
probe does **not** wire anything into the production `run_split` path: it
loads the saved v08 hybrid SF artifact, fires the magnitude selector once
per no-match letter, overwrites `FrequencyChange` with the magnitude
selection on those letters only, and re-scores. The production lane and the
v08 artifact are untouched and byte-identical. This is a measurement probe
whose outcome decides whether a production-wiring follow-up is worth a
separate predeclaration — it is not that wiring.

## Vocabulary reconciliation (frozen)

The complement uses a **magnitude-only closed vocab**, a strict subset of the
gold `FrequencyChange` vocab (`rules/change.py:3`):

| `FrequencyChange` value | magnitude menu entry? | role |
| --- | --- | --- |
| `Frequent` | yes | the "high frequency" magnitude |
| `Infrequent` | yes | the "low frequency" magnitude |
| `Same` | yes | the neutral / abstain outcome (no magnitude stated) |
| `Increased` | no (direction label) | excluded — the magnitude question is orthogonal to change-direction |
| `Decreased` | no (direction label) | excluded — same |
| `ABSTAIN` | yes (defer) | the dspy G32 defer option |

**The two design choices frozen here:**

1. **Magnitude menu is 3-label + ABSTAIN, never the direction labels.** The
   integration probe's failure mode was the selector reading a conflated
   5-label menu and mapping magnitude labels into direction labels. A
   magnitude-only menu removes that failure mode by construction: the LLM
   cannot emit `Increased`/`Decreased` because they are not on the menu. It
   picks `Frequent`, `Infrequent`, `Same` (no magnitude), or `ABSTAIN`.
2. **The trigger is "magnitude regex had no match," not "any change.* regex
   had no match."** Confirmed as the design choice: a letter is "covered" by
   the rules iff `change.frequent` or `change.infrequent` matched its text
   (checked via `CHANGE_EXTRACT_IMPLS`, the same dict `build_direction_menu`
   already iterates). The complement fires only where the magnitude regexes
   were silent. This isolates the magnitude axis precisely and matches the
   deconflation probe's two-axis framing — a wider trigger (any change.*
   regex) would conflate magnitude and direction coverage and muddy the
   attribution this probe is designed to measure.

## Frozen contract

| Field | Value |
| --- | --- |
| Driver | New `scripts/run_exectv2_sf_magnitude_complement.py` (~28 gpt-4.1-mini calls; replay mode over saved v08 artifact) |
| Input artifact | `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl` (v08 hybrid, magnitude from `rules/change.py`) — the same rules-arm artifact the deconflation probe reads |
| Gold | dev140 gold (unchanged; the frozen annotation set) |
| Scorer (current code) | `score_frequency_state` → all four metrics including `state_profile_magnitude` (the magnitude-only companion the deconflation probe added). No scorer changes. |
| Trigger predicate | New `has_magnitude_regex_match(letter_text) -> bool` in `closed_option_direction.py`: True iff `change.frequent` or `change.infrequent` matched (via `CHANGE_EXTRACT_IMPLS`). Complement fires on the no-match subset of the direction-in-play set. |
| Selector contract | New `build_magnitude_menu` + `ClosedOptionMagnitudeSelector` in `closed_option_direction.py`: magnitude-only menu (Frequent/Infrequent/Same + ABSTAIN), pick-from-menu-or-abstain. Reuses `parse_selection` + `assemble_direction` unchanged (they already work generically on any menu). |
| Split | dev140 only (the input artifact is dev140; test59 frozen) |
| Call count | ~28 gpt-4.1-mini calls (one per no-match direction-in-play letter; cached, temp 0). |
| Row inspection | dev140 only (the direction-in-play set the integration ledger already covers). No test59 / full-200 row inspection. |
| Regression check | (1) `state_profile_directional` reproduces 0.8897 at baseline (drift ≤ 0.0001). (2) `state_profile` byte-identical after the complement override — the complement touches only `FrequencyChange` on the no-match subset, exactly the isolation the integration probe's replay mode established. |

## Predeclared outcomes

Primary comparison = the **complement `state_profile_magnitude` F1** vs the
**rules `state_profile_magnitude` F1 = 0.9447** (tp=111 fp=8 fn=5; precision
0.9328, recall 0.9569 — the deconflation probe's rules-arm number, the
production reference).

Reference numbers (all dev140, the rules arm reproduced in-run):
`state_profile_magnitude` **0.9447**; `state_profile_directional` **0.8897**
(anchor); `state_profile` **0.9338** (byte-identical regression guard).

| Outcome | Verdict | Action |
| --- | --- | --- |
| Complement `state_profile_magnitude` **> 0.9447 + 0.005** AND `state_profile` byte-identical | **COMPLEMENT BEATS RULES** — a genuine production improvement; the selector's precision edge transfers to the no-match letters and its recall recovery more than compensates | Major: a clean "deterministic-LLM complementarity" result for the paper. Candidate for a separate production-wiring predeclaration (the complement becomes a new `direction_selector` mode on `run_split`). Report the magnitude-axis table (rules / selector / complement). |
| Complement `state_profile_magnitude` **within [0.9447 − 0.005, 0.9447 + 0.005]** | **COMPLEMENT APPROACHES RULES** — the selector's precision edge transfers to the no-match letters and recovers some recall, but no net magnitude gain over the rules | Report the decomposition: the selector's precision edge is real but the no-match letters are the hard cases where recall is not recoverable by the contract either. Confirms the magnitude recall gap is a genuine capacity gap, not a contract artifact. Not a production improvement, but sharpens the magnitude-axis attribution. |
| Complement `state_profile_magnitude` **< 0.9447 − 0.005** | **COMPLEMENT TRAILS RULES** — the selector's precision edge does NOT transfer when restricted to the no-match letters; firing on the hard cases costs more than it gains | Report as the cleanest negative: the no-match subset is exactly where the LLM's magnitude judgment is weakest. The magnitude recall gap is a genuine capacity gap that no contract design closes. Closes pathway #1 as a negative. |
| `state_profile` regresses > 0.005, or baseline fails to reproduce 0.8897 | **CONTRACT FAILURE** — the complement touched more than the no-match subset, or the v08 artifact was misread | Abort; re-derive the trigger + override; do not report complement numbers until the anchors reproduce and `state_profile` is byte-identical. |

The interesting bands are **the first two**: the deconflation probe's
decomposition predicted the selector's precision edge (0.9515) *could*
transfer to a complement design, but also that the no-match letters are the
hard cases. The prediction is predeclared, not assumed: if restricting the
selector to the no-match subset costs it the precision advantage (band 3),
the complement is refuted and the magnitude gap is confirmed as a capacity
gap.

## Cost & isolation

- **~28 gpt-4.1-mini calls**, dev140, temp 0, cached, replay mode. One call
  per no-match direction-in-play letter.
- The complement override is applied to a **copy** of the v08 artifact's
  predictions (built into fresh `ExectLetter`s); the v08 artifact file is
  never overwritten.
- `state_profile` byte-identical after the override isolates the change to
  the magnitude axis on the no-match subset — the same isolation the
  integration probe's replay mode and the deconflation probe's byte-
  identical check established.
- dev140 only; no test59 / full-200 row inspection.

## What this is NOT

- **Not a production change.** Nothing is wired into `run_split`. The
  outcome decides whether a production-wiring follow-up is worth a separate
  predeclaration; it is not that wiring.
- **Not a re-run of the integration probe.** The integration probe replaced
  the rules everywhere with a 5-label direction selector and lost. This
  probe restricts a 3-label magnitude selector to the no-match subset — a
  different question, different contract, different trigger.
- **Not a gold-schema change.** Gold is frozen. The magnitude menu is a
  prediction-side contract; the cited `state_profile_magnitude` metric (a
  scoring-side rekey the deconflation probe added) is unchanged.
- **Not a claim the magnitude labels are the lever.** The deconflation probe
  showed they are ~60% of the integration gap; this probe tests whether that
  60% is recoverable by a complement design. It may not be — the no-match
  letters are the hard cases.
- **Not a direction-axis probe.** The complement asks a magnitude-only
  question on a magnitude-only menu. The direction axis (the residual
  +0.0226 the deconflation probe isolated) is out of scope here.

## Provenance / artifacts (to be produced)

- Driver: `scripts/run_exectv2_sf_magnitude_complement.py`.
- Library: `build_magnitude_menu`, `has_magnitude_regex_match`,
  `ClosedOptionMagnitudeSelector` + `ClosedOptionMagnitudeSelectorSignature`,
  `MAGNITUDE_VOCAB`, `MAGNITUDE_RULE_IDS` (added to
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/hybrid/closed_option_direction.py`,
  alongside the existing direction functions; additive only, no change to
  existing functions).
- Tests: new `TestBuildMagnitudeMenu` + `TestHasMagnitudeRegexMatch` classes
  in `tests/test_exectv2_sf_closed_option_hybrid_integration.py` (the
  existing 18-case file for this module).
- Summary: `experiments/exectv2_sf_magnitude_complement_summary_20260708.json`
  (baseline + complement PRF1 on all four metrics; the in-run anchor
  reproduction; the complement subset count; the verdict band).
- Ledger: `experiments/exectv2_sf_magnitude_complement_ledger_20260708.jsonl`
  (one row per no-match letter the selector fired on: letter_id, prior
  FrequencyChange, selected_candidate_id, selection_mode, assembled
  magnitude, menu_labels).
- Predictions: `experiments/exectv2_sf_magnitude_complement_dev140_20260708.jsonl`
  (the overridden artifact, via `write_jsonl`).
- Results doc:
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_magnitude_complement_results_2026-07-08.md`.
- Hypothesis registry entry: `sf_magnitude_complement_2026-07-08`.

## Pre-declaration of the manuscript implication (frozen before results)

Whichever band lands, the result is reportable and sharpens the SF
magnitude-axis story:

- **Band 1 (complement beats rules):** the manuscript carries a
  deterministic-LLM complementarity result — a *new* architectural finding
  (the rules own the magnitude axis where their regexes fire; the LLM
  complements them where they are silent, and the union beats both). This is
  a concrete production improvement to the cited v08 SF number and the
  cleanest positive from the 48-hour probe program.
- **Band 2 (complement approaches):** the manuscript states the selector's
  magnitude precision edge is real but does not yield a net gain when
  restricted to the hard no-match cases — the magnitude recall gap is a
  genuine capacity gap, confirmed from a second angle. Sharpens the
  magnitude-axis attribution table the deconflation probe added.
- **Band 3 (complement trails):** the manuscript states the no-match subset
  is exactly where the LLM's magnitude judgment is weakest; no contract
  design recovers the magnitude recall gap. Closes the complement pathway as
  a negative and consolidates the rules as the magnitude source of record.

Either way the probe converts the deconflation probe's decomposition (a
measurement) into a design test (an intervention), which is the discipline
this workstream requires before a production claim can be considered.
