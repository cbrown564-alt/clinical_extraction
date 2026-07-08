# Predeclaration — SF `FrequencyChange` vocab deconflation probe (2026-07-08)

Date: 2026-07-08. Owner: ExECTv2 workstream.
Hypothesis: `sf_direction_vocab_deconflation_2026-07-08` (PENDING).
Driver: `scripts/run_exectv2_sf_direction_vocab_deconflation.py` (zero LLM calls;
deterministic rekey + re-score over saved predictions).
Prior art: `sf_closed_option_hybrid_integration_2026-07-06` (registry entry 35,
APPROACHES-but-does-not-match at 0.8333 vs 0.8897, delta −0.0563) — the probe
whose mechanism section diagnosed the conflation this test isolates.
Umbrella: open follow-up to the predecessor-synthesis follow-ups plan
(`docs/plans/predecessor_synthesis_followups_2026-07-06.md` open question #1's
mechanism finding).

## Purpose (the question)

The closed-option hybrid integration found that the LLM selector lands **below**
the deterministic `rules/change.py` (0.8333 vs 0.8897) and attributed the gap to
a **`FrequencyChange` vocab-design conflation**: the attribute's five values mix
**change-direction** (`Increased`/`Decreased`/`Same`) and **frequency-magnitude**
(`Frequent`/`Infrequent`) on a single axis. The deterministic regexes capture
both readings (the `change.frequent`/`change.infrequent` builders exist for the
magnitude reading); the LLM selector, given a menu of all five, systematically
maps the magnitude labels into the direction labels (`Infrequent → Decreased`
14×, `Frequent → Same/Increased/Decreased` 12×).

That results doc stated its mechanism reading was *"a hypothesis, not a proven
cause"* (§Limitations) and that *"a per-row gold audit would confirm it … Such
an audit is out of scope"* — flagging the follow-up this probe now runs.

**This probe is that audit, operationalized.** The question is no longer "does
the selector match the rules on the conflated metric" (answered: no, −0.0563)
but: **when the `FrequencyChange` vocab is projected onto two orthogonal axes —
direction `{increased, decreased, same}` and magnitude `{frequent, infrequent,
none}` — does the rules-vs-selector gap survive the deconflation?**

This is the synthesis probe for the two surprises in the 48-hour window: it
joins (a) the standalone refute of "fundamental" (item 2: the gap does not
survive a generation-contract change) with (b) the integration negative (the gap
*does* survive replacing the rules). It tests whether the integration gap is a
third thing — **a measurement artifact of the conflated gold vocab** — by asking
if it *fails* to survive a scoring-axis change.

## Why a scoring rekey, not a gold-schema change (scope freeze)

The conflation is **baked into the frozen gold**. The annotation guideline
(`docs/research/exectv2_sf_guideline_alignment_2026-06-10.md` §4, citing Appendix
L987) defines the closed vocab
`Decreased/Increased/Same/Infrequent/Frequent` and is marked **Aligned**; §2
even maps `"under control"/"well controlled" ⇒ FrequencyChange=Infrequent`,
putting a magnitude reading into the change-direction field by guideline design.
Gold annotations are frozen (test59 locked; dev140 is the development surface).

**Therefore this probe does not touch gold.** It rekeys the *scoring* of the
*same saved predictions* onto a projected 2-D key derived from the existing
`FrequencyChange` values, then asks whether the rules-vs-selector ordering
inverts. This is the same family of move as the raw-vs-projected decomposition
(item 5): a zero-LLM-call re-scoring over a frozen prediction artifact that
isolates one scoring variable. The frozen benchmark key
(`frequency_state_directional` as currently defined) is **not** changed; this is
an additional projected metric, reported alongside it as a companion (the
`state_profile` / `state_profile_directional` / deconflated bracket).

## Vocabulary reconciliation (frozen)

`rules/change.py:3` documents the gold closed vocab as
`{Decreased, Frequent, Increased, Infrequent, Same}`. The 2-axis projection is:

| `FrequencyChange` value | projected `direction` | projected `magnitude` |
| --- | --- | --- |
| `Increased` | `increased` | `none` |
| `Decreased` | `decreased` | `none` |
| `Same` | `same` | `none` |
| `Frequent` | `same` | `frequent` |
| `Infrequent` | `same` | `infrequent` |
| (absent / count-bearing) | per `frequency_state_directional` today (count-state passthrough) | `none` |

**The two design choices frozen here:**

1. **Magnitude labels project to direction `same`, not `unknown`.** The
   integration ledger showed the LLM reads "Frequent/Infrequent" as a
   magnitude statement with *no change-direction claim*. Projecting to `same`
   is the honest encoding of "a magnitude statement carries no direction signal"
   and keeps the direction axis 3-valued `{increased, decreased, same}`. (An
   `unknown` projection is the alternative; see outcome band "contract failure"
   — if results are sensitive to this choice, both are reported.)
2. **Count-bearing states (`active-rate`/`seizure-free`) pass through
   unchanged** on both axes. `frequency_state_directional`
   (`seizure_frequency.py:314-340`) already returns the count-based state before
   consulting `FrequencyChange`; the deconflation only affects the
   `changed`/directional bucket. This isolates the variable exactly as the
   integration probe's `state_profile`-byte-identical check did.

## Frozen contract

| Field | Value |
| --- | --- |
| Driver | New `scripts/run_exectv2_sf_direction_vocab_deconflation.py` (zero LLM calls; rekey + re-score) |
| Input artifacts (two arms) | **Rules arm:** `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl` (v08 hybrid, direction from `rules/change.py`). **Selector arm:** `experiments/exectv2_sf_closed_option_hybrid_integration_dev140_20260707.jsonl` (same artifact with `FrequencyChange` overwritten by the selector; the integration probe's output). |
| Gold | dev140 gold (unchanged; the frozen annotation set) |
| Scorer (current) | `score_frequency_state` → `state_profile_directional` (the conflated 5-way metric; reproduced on both arms as the baseline anchor — must reproduce 0.8897 rules / 0.8333 selector) |
| Scorer (projected) | New `_frequency_state_direction_deconf_keys` + `_frequency_state_magnitude_keys` key builders, added alongside `frequency_state_directional` in `seizure_frequency.py`; same per-letter dedup + `multiset_prf1` / `sum_prf1` plumbing as the existing profile scorers. Two new metrics: `direction_deconf` and `magnitude_deconf`. |
| Split | dev140 only (both input artifacts are dev140; test59 frozen) |
| Call count | **0 LLM calls.** Pure re-scoring of frozen predictions. |
| Row inspection | dev140 only (the 25 letters / 50 direction-in-play mentions the integration ledger already covers). No test59 / full-200 row inspection. |
| Regression check | `state_profile` (direction- and magnitude-blind) reproduced byte-identical on both arms — confirms the rekey touched only the direction/magnitude axes, nothing else. |

## Predeclared outcomes

Primary comparison = the **direction-deconflated gap**
(`rules.direction_deconf − selector.direction_deconf`) vs the **conflated gap**
(`rules.state_profile_directional − selector.state_profile_directional` =
0.8897 − 0.8333 = **+0.0563**, the integration result).

Reference numbers (all dev140, reproduced in-run): rules conflated **0.8897**;
selector conflated **0.8333**; conflated gap **+0.0563** (rules above selector).

| Outcome | Verdict | Action |
| --- | --- | --- |
| Direction-deconflated gap **collapses to ≤ +0.01** (selector ≈ rules on the direction-only axis) | **GAP IS A MEASUREMENT ARTIFACT of the conflated vocab** — the rules' advantage is the magnitude labels, not direction; on direction alone the selector matches | Major: synthesizes item 2 (contract refutes fundamental) + integration (rules win conflated) into one claim — "the deterministic rules win the *magnitude* axis by faithfully implementing the conflated gold; on the *direction* axis the closed-option selector matches them." Report as the sharper result; the standalone refute and the integration negative are reconciled. |
| Direction-deconflated gap **shrinks but stays > +0.01** (partial: selector closes some, rules still ahead) | **MAGNITUDE IS PART OF THE GAP, NOT ALL OF IT** — the conflation explains a share; a residual direction gap remains | Report the decomposition (how much of +0.0563 is magnitude vs direction); neither fully reconciles the two prior probes nor fully confirms the integration's framing — an honest partial attribution |
| Direction-deconflated gap **≈ +0.0563** (unchanged) | **CONFLATION IS NOT THE EXPLANATION** — the rules win on direction itself, not via the magnitude labels; the integration's "vocab-design finding" is downgraded to "the rules are better at direction, full stop" | Report as a refinement of the integration result: the vocab-conflation mechanism reading is *not* supported once direction is isolated; the standalone refute and integration negative remain in genuine tension (selector matches on raw artifact, loses on hybrid substrate, for reasons other than the vocab) |
| `state_profile` regresses, or either arm fails to reproduce its conflated anchor | **CONTRACT FAILURE** — the rekey touched more than the direction/magnitude axes, or an input artifact was misread | Abort; re-derive the key builders; do not report projected numbers until the anchors reproduce |

The interesting band is the **first two**: the integration result's own
mechanism section predicted the gap is "vocab-shaped," and this probe tests that
prediction directly. The expected outcome (from the ledger distribution shift:
Infrequent→Decreased 14×, Frequent→{Same/Increased/Decreased} 12×) is that
**most of the rules' advantage lives on the magnitude axis** — i.e. the
direction-deconflated gap shrinks substantially — because the selector
systematically abandoned the magnitude labels. But the prediction is
predeclared, not assumed: if the rules also win on pure direction (band 3), the
vocab-conflation reading is refuted and the integration framing stands
strengthened.

### Secondary metric (magnitude axis)

`magnitude_deconf` is reported for completeness but is **not** the verdict
driver. The magnitude axis is where the integration ledger predicts the rules'
advantage concentrates (the selector emitted `Frequent` 4× and `Infrequent` 0×
vs the rules' `Frequent` 16 / `Infrequent` 19). A large magnitude gap with a
collapsed direction gap is the signature of outcome band 1.

## Cost & isolation

- **0 LLM calls.** Both input artifacts are saved predictions; this is a rekey +
  re-score.
- Both arms scored through the *same* new projected key builders — no
  per-arm special-casing. The only difference between arms is the
  `FrequencyChange` provenance (rules vs selector), exactly as in the
  integration probe's replay mode.
- `state_profile` (direction- and magnitude-blind) reproduced byte-identical on
  both arms isolates the rekey from scorer drift.
- dev140 only; no test59 / full-200 row inspection.

## What this is NOT

- **Not a gold-schema change.** Gold is frozen; the conflation is in the
  annotation guideline (Appendix L987, "Aligned"). This projects a scoring key,
  it does not re-annotate.
- **Not a re-test of "fundamental."** The standalone probe (item 2) settled that
  the gap does not survive a generation-contract change on the raw artifact.
  This tests a *different* survival question: does the *integration* gap survive
  a scoring-axis change on the hybrid substrate?
- **Not a re-run of the integration probe.** The selector's picks are taken from
  the saved integration artifact; no new selector calls fire.
- **Not a claim that the magnitude labels are "wrong."** They are a legitimate
  part of the guideline's `FrequencyChange` semantics; the point is that they
  are a *different axis* from change-direction, and the current
  `state_profile_directional` metric scores both on one axis. The projected
  metric separates them to attribute the gap, not to redefine the headline.
- **Not a production change to the headline metric.** `state_profile_directional`
  (the conflated 5-way metric) remains the cited reference; the deconflated
  metrics are companions that *explain* the integration gap, reported alongside
  it (the same bracket shape as `[clinical_headline, state_profile]`).

## Provenance / artifacts (to be produced)

- Driver: `scripts/run_exectv2_sf_direction_vocab_deconflation.py`.
- Key builders: `_frequency_state_direction_deconf_keys` +
  `_frequency_state_magnitude_keys` (added to
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/seizure_frequency.py`,
  alongside `frequency_state_directional`; no change to existing functions).
- Summary: `experiments/exectv2_sf_direction_vocab_deconflation_summary_20260708.json`
  (conflated + direction-deconf + magnitude-deconf PRF1 for both arms; the
  in-run anchor reproduction; the per-mention direction/magnitude projection for
  the 50 direction-in-play mentions).
- Results doc:
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_direction_vocab_deconflation_results_2026-07-08.md`.
- Hypothesis registry entry: `sf_direction_vocab_deconflation_2026-07-08`.

## Pre-declaration of the manuscript implication (frozen before results)

Whichever band lands, the result is reportable and sharpens the SF section:

- **Band 1 (gap collapses):** the manuscript carries a *direction-only* SF
  metric on which the closed-option selector matches the deterministic rules,
  reconciling the standalone refute with the integration negative. The
  deterministic rules' production role is reframed as "they own the magnitude
  axis; direction is a solved sub-problem under either source." This is the
  strongest synthesis of the 48-hour findings.
- **Band 3 (gap unchanged):** the manuscript drops the "vocab-design" framing
  from the integration results doc and states plainly that the deterministic
  rules win on direction itself; the standalone/integration tension is reported
  as an open substrate-dependence (selector matches on raw artifact, loses on
  hybrid), not explained away by the vocab.

Either way the probe converts a hypothesis ("the conflation is the mechanism")
into a measurement, which is the discipline this workstream requires before the
mechanism reading can support a claim.
