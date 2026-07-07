# No-model seizure-frequency oracle — results

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `sf_no_model_oracle_2026-07-06` — **RESOLVED** (the SF deterministic
extraction ceiling is at-or-above the cited hybrid clinical metrics; the
candidate-substrate recall is 77%, not dspy's 100% — a real cross-codebase
difference).
Driver: `experiments/exectv2_sf_no_model_oracle_2026-07-06.py` (zero LLM calls;
deterministic replay over gold text).
Umbrella plan: item 4 extension of
`docs/plans/predecessor_synthesis_followups_2026-07-06.md` (open question #3).
Template: `experiments/exectv2_medication_no_model_oracle_2026-07-06.py`.

## Headline

**The SF deterministic extraction ceiling is at-or-above the cited hybrid
clinical metrics.** Running `extract_seizure_frequency` alone (no lens, no
bridge, no LLM) as the final system scores **0.8947 dev140 `state_profile`**
(registered hybrid 0.7483 / re-run 0.7793) and **0.8873 dev140
`state_profile_directional`** (cited v08 hybrid 0.8897, gap **−0.0024**). This is
the **same pattern as the medication oracle** (deterministic ≈ hybrid), not the
Investigations pattern (deterministic ≪ hybrid). The LLM/lens does not own the
SF clinical headline the way it owns Investigations — the deterministic
extractor's own keep/drop filter carries it.

The candidate substrate (dspy's E1 "broad payload" analogue) scores
**0.5211 dev140 `state_profile`** at **77.2% recall / 39.3% precision**. This
*partially* confirms the dspy E1 framing (broad payload → high recall / low
precision → problem localized to adjudication), but **our recall is 77%, not the
100% dspy reports** — a genuine cross-codebase difference, traced below. The
precision (39%) is in the same low regime as dspy's 22%.

This is a **split-invariant, model-independent** ceiling statement on the
deterministic surface: dev140 and full-200 agree in shape (deterministic ≈
hybrid on clinical metrics; candidate substrate high-recall/low-precision).

## The numbers

Three surfaces were scored, in order of how "oracle-like" they are:

| Surface | dev140 `state_profile` | dev140 `state_profile_directional` | dev140 `clinical_headline` | What it tests |
| --- | ---: | ---: | ---: | --- |
| **`gold_as_prediction`** | **1.0000** (136/0/0) | **1.0000** (140/0/0) | **1.0000** (168/0/0) | Scorer integrity: gold copied through the pipeline. Not extraction. |
| **`deterministic_only`** | **0.8947** (119/11/17) | **0.8873** (122/13/18) | **0.8503** (142/24/26) | The real no-model extraction ceiling: `extract_seizure_frequency` run as the final system. |
| **`candidate_substrate`** | 0.5211 (105/162/31) | 0.5098 (104/164/36) | 0.0000 (0/491/168) | dspy E1 analogue: `build_candidate_set` with every candidate kept (pre-adjudication). |
| Cited hybrid `state_profile` (registered) | 0.7483 | — | — | Hybrid lane. |
| Cited hybrid `state_profile` (2026-07-03 re-run) | 0.7793 | — | — | Hybrid lane re-run. |
| Cited hybrid `state_profile_directional` | — | 0.8897 | — | v08 hybrid, direction from `rules/change.py`. |
| Raw SF-verify `state_profile_directional` | — | 0.6552 | — | Direction-blind LLM program. |
| **Gap (deterministic-only − cited hybrid directional)** | — | **−0.0024** | — | **The LLM/lens adds ~nothing to the directional headline.** |

### full-200 (aggregate-only, frozen protocol)

| Surface | full-200 `state_profile` | full-200 `state_profile_directional` | full-200 `clinical_headline` |
| --- | ---: | ---: | ---: |
| `gold_as_prediction` | 1.0000 (201/0/0) | 1.0000 (205/0/0) | 1.0000 (242/0/0) |
| `deterministic_only` | 0.8429 (161/20/40) | 0.8286 (162/24/43) | 0.7712 (182/48/60) |
| `candidate_substrate` | 0.5068 (149/238/52) | 0.4924 (146/242/59) | 0.0022 (1/682/241) |

> **Why three surfaces.** `gold_as_prediction` is the dspy-style scorer-integrity
> ceiling (gold copied through; confirms the scorer preserves the 136 dev140 /
> 201 full-200 gold counts end-to-end). `deterministic_only` is the real
> extraction ceiling the deterministic layer owns (including its own keep/drop
> filter `_should_keep_mention`). `candidate_substrate` is the dspy E1 analogue:
> `build_candidate_set` with every candidate kept (the pre-adjudication broad
> payload), testing whether the candidate substrate's recall is near-complete.
> The interesting numbers are the second and third rows.

### Predeclared outcome bands (from plan item 4 extension)

| Outcome band | Verdict | This run |
| --- | --- | --- |
| deterministic-only ≈ 1.0 | dspy framing applies in the strongest form | ✗ (0.89 state_profile) |
| deterministic-only ≈ cited hybrid | **dspy framing applies; LLM adds nothing to the headline; manuscript says so** | **✓ (gap −0.0024 directional; state_profile det ABOVE cited hybrid)** |
| deterministic-only ≪ cited hybrid | LLM genuinely contributing recall/specificity; positive LLM-value story | ✗ for SF (this is the **Investigations** pattern, not SF) |

The result lands in the **middle band**: the SF deterministic extraction ceiling
matches the cited hybrid directional headline (−0.0024) and **exceeds** the
cited hybrid `state_profile` (0.8947 vs 0.7483 registered / 0.7793 re-run). The
LLM/lens is not the owner of the SF clinical headline.

## Why the deterministic ceiling exceeds the cited registered state_profile

This is the most surprising number in the run and deserves care. The cited
dev140 `state_profile` **0.7483** is the *registered* number
(`exectv2_sf_retrieval_highlight_results_2026-07-06.md`, the surface of record);
the **0.7793** re-run (2026-07-03) is the substrate the direction adjudications
were authored against. The deterministic-only `state_profile` here is **0.8947**
— substantially above both.

The difference is **what is being scored**, not scorer drift (the
`gold_as_prediction` = 1.0 row rules out scorer error):

- The cited 0.7483 / 0.7793 numbers are the **raw SF-verify LLM program** scored
  on `state_profile` — a direction-blind free-write LLM whose `state_profile` is
  genuinely 0.7483. That number is the *baseline* the four SF-direction negatives
  were measured against.
- The deterministic-only 0.8947 here is the **deterministic SF pipeline**
  (`extract_seizure_frequency`, with its keep/drop filter) scored on the same
  `state_profile` metric. The deterministic pipeline's keep/drop filter is a
  genuine recall/precision contributor that the raw LLM program lacks.

**So the cited 0.7483 is the LLM-program baseline, not the deterministic
ceiling.** The deterministic ceiling (0.8947) was not previously stated alongside
it. This probe surfaces that the deterministic SF pipeline is substantially
stronger on `state_profile` than the raw LLM program — which is consistent with
the direction-probe finding that the deterministic `rules/change.py` (0.8897
directional) is the production direction source. The deterministic pipeline owns
both the state and the direction.

> **Implication for attribution.** This probe *is* the attribution-discipline
> deliverable for SF: it shows what the deterministic layer produces *before* any
> LLM or lens is applied. The cited hybrid directional headline (0.8897) is
> deterministic-owned to within −0.0024. Per the research-protocol skill's
> attribution rule, **SF direction is not an LLM-first claim on the hybrid lane**
> — it is a deterministic claim sourced from `rules/change.py`. (The LLM-first
> surface for SF direction is the raw free-write SF-verify program at 0.6552,
> which is where the four negatives were measured.)

## The candidate substrate: dspy E1 framing, partially confirmed

dspy's E1 finding: a broad payload covers **100% of gold at 22.2% precision**,
localizing the SF problem to adjudication (the broad payload has perfect recall;
the LLM arbitration prunes to the headline). Our candidate substrate
(`build_candidate_set` with every candidate kept) scores:

| | Recall | Precision | F1 |
| --- | ---: | ---: | ---: |
| dev140 `state_profile` | **77.2%** (105/136) | **39.3%** (105/267) | 0.5211 |
| full-200 `state_profile` | 74.1% (149/201) | 38.5% (149/387) | 0.5068 |

**Partial confirmation.** The precision is in dspy's low regime (39% vs 22% —
same order: the broad payload floods precision by design). But **the recall is
77%, not 100%**. This is a genuine cross-codebase difference, not a methodological
gap: our candidate substrate does *not* achieve perfect recall on the gold
state_profile keys. The 31 dev140 FN (state_profile) are gold mentions whose
state the candidate substrate's deterministic anchors do not surface — these flow
through to the `additional_mentions` recall path in the hybrid assessment, which
is an LLM contribution this probe does not capture (it is a no-model probe). So
the honest statement is: **the candidate substrate localizes *most* of the
problem to adjudication (77% recall), but not all of it — the residual 23% is
LLM-recall territory.** dspy's clean "100% recall / adjudication-only" framing
does not transfer fully; our SF problem is partly extraction (the candidate
substrate misses gold) and partly adjudication (the candidate substrate floods).

> **The `clinical_headline` 0.0 is expected, not a bug.** The candidate
> substrate's `suggested_attributes` carry frequency-change and (sometimes) rate
> cues, but the `clinical_headline` metric requires count-bearing attributes
> (NumberOfSeizures etc.). Bare anchors without counts key to no headline match.
> This is the design: the candidate substrate is a *recall* scaffold, not a
> headline producer.

## Implications for the manuscript

1. **SF joins Prescription as a deterministic-owned clinical ceiling.** The
   deterministic SF extractor's `state_profile` (0.8947) and
   `state_profile_directional` (0.8873) match or exceed the cited hybrid numbers.
   The manuscript must state the deterministic-only number alongside the hybrid
   headline and attribute the directional headline to `rules/change.py`
   (consistent with the direction-probe synthesis). The SF "LLM extraction"
   framing applies to the *raw free-write* program (0.6552), not the hybrid lane.
2. **The candidate substrate partly confirms dspy's E1 localization.** The broad
   payload is high-recall/low-precision as dspy found, but our recall is 77%, not
   100% — the SF problem is not *purely* adjudication; a residual is LLM-recall.
   Report this as a cross-codebase difference from dspy, not a replication.
3. **Contrast with Investigations (the contribution-bearing family).** Where Inv
   deterministic-only ≪ hybrid (gap −0.40; the LLM/verifier owns the Inv
   headline), SF deterministic-only ≈ hybrid. The three families now decompose:
   **Prescription** deterministic-owned (LLM adds zero to headline), **SF**
   deterministic-owned (LLM adds ~zero to directional headline; candidate
   substrate localizes most-but-not-all to adjudication), **Investigations**
   LLM/contribution-bearing (deterministic ≪ hybrid). This is the cross-family
   attribution picture item 4's template was designed to produce.
4. **Match the dspy "isolated ceiling" methodology for SF.** This probe
   establishes the SF extraction ceiling + candidate-substrate recall. The same
   probe shape now covers all three LLM-touched families (Rx done, Inv done, SF
   done); the ceiling-registry payoff from item 4 is complete.

## Limitations and honest caveats

- **`extract_seizure_frequency` is post-P7 and includes the keep/drop filter.**
  The deterministic ceiling measured here is the *current* deterministic pipeline,
  including the `_should_keep_mention` filter (a deterministic rule). Pre-P7 / pre-
  filter numbers would be lower; the headline statement ("deterministic owns the
  SF clinical ceiling") holds for the current code.
- **`clinical_headline` SF (0.8503 dev) is below `state_profile` (0.8947).** The
  clinical_headline metric is count-only (seizure-free / active-rate / unknown)
  and does not reward direction; `state_profile` is change-aware. The two measure
  different things. Cite the metric appropriate to the claim.
- **The candidate substrate FN decomposition keys are empty in the JSON** because
  `frequency_state_keys` collapses bare-anchor (no-count) mentions to the same
  `unknown` state as some gold, so multiset subtraction yields no missed keys
  even though tp/fp/fn show 31 FN. The aggregate recall (77%) is the load-bearing
  number; the per-key decomposition is supplementary and should be read with that
  keying artifact in mind.
- **dspy's 100% / 22.2% is not directly commensurable.** dspy's E1 broad payload
  is built on a different candidate construction; our `build_candidate_set` is a
  different substrate. We confirm the *shape* (high-recall/low-precision broad
  payload → adjudication-localized) but not the literal numbers, and the recall
  difference (77% vs 100%) is a real cross-codebase gap, not a measurement error.
- **Full-200 row-level inspection is aggregate-only** per claim_policy. The
  per-letter FN/FP decomposition is dev140-only; full-200 is reported as aggregate
  tp/fp/fn.
- **This is a single-family ceiling, not a system-wide claim.** "SF deterministic
  ≈ hybrid" does not generalize to Investigations (where deterministic ≪ hybrid).
  Each family has its own isolated-component ceiling; this is SF's.

## What this is NOT

- Not a claim that SF is "solved" — the deterministic ceiling is 0.89 state /
  0.85 headline, with a traced residual (17 FN + 11 FP state_profile dev140).
- Not a claim that the LLM is useless for SF — the candidate substrate shows a
  23% recall gap the LLM `additional_mentions` path addresses, and the raw
  free-write program is genuinely direction-blind (0.6552). It is a claim that
  the *hybrid lane's* directional headline is deterministic-owned.
- Not a re-run of the hybrid lane. The cited hybrid numbers (0.8897 directional)
  are taken as comparison anchors; this probe scores the deterministic-only and
  candidate-substrate surfaces fresh.
- Not a test of the closed-option direction selector (that is the item 2
  integration follow-up).

## Artifacts / Provenance

- Driver: `experiments/exectv2_sf_no_model_oracle_2026-07-06.py` (zero LLM calls;
  deterministic replay over gold text).
- JSON: `experiments/exectv2_sf_no_model_oracle_2026-07-06.json` (per-metric
  scores for all three surfaces, both splits; dev140 FN/FP decomposition for
  deterministic_only on state_profile + state_profile_directional, and for
  candidate_substrate on state_profile).
- Scorer: `score_frequency_state`
  (`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/seizure_frequency.py`)
  — the same scorer used for the hybrid lanes, no special-casing.
- Extractor: `extract_seizure_frequency`
  (`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/pipeline.py`).
- Candidate substrate: `build_candidate_set`
  (`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/hybrid/candidate_set.py`).
- Comparison anchors: `PROJECT_STATUS.md` (state_profile 0.7483 / 0.7793;
  directional 0.6552 raw / 0.8897 hybrid); the direction-probe results docs.
- Template: `experiments/exectv2_medication_no_model_oracle_2026-07-06.py`.
- Umbrella: `docs/plans/predecessor_synthesis_followups_2026-07-06.md` (item 4,
  open question #3).
- Split discipline: dev140 + full-200, both deterministic replay over gold text —
  no live predictions, no split risk. Cost: 0 LLM calls.
