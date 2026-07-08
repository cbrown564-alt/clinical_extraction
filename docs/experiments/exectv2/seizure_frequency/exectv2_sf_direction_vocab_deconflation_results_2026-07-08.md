# Results — SF `FrequencyChange` vocab deconflation probe (2026-07-08)

Date: 2026-07-08. Owner: ExECTv2 workstream.
Hypothesis: `sf_direction_vocab_deconflation_2026-07-06` → **MAGNITUDE IS PART OF
THE GAP, NOT ALL OF IT** (the middle band; partial reconciliation).
Driver: `scripts/run_exectv2_sf_direction_vocab_deconflation.py` (zero LLM calls;
rekey + re-score over two saved dev140 prediction artifacts).
Predeclaration: `exectv2_sf_direction_vocab_deconflation_predeclaration_2026-07-08.md`.

## Headline

**Deconflating the `FrequencyChange` vocab onto two orthogonal axes — direction
(Increased/Decreased/Same) and magnitude (Frequent/Infrequent) — shrinks the
rules-vs-selector gap from +0.0564 to +0.0226 (a 60% reduction) on the
direction-only axis, but does not collapse it. The majority of the deterministic
rules' advantage over the LLM closed-option selector is the magnitude axis the
selector systematically abandons; a smaller, genuine direction gap remains.**

This lands in the **predeclared middle band**: the vocab conflation explains a
share of the integration gap, but not all of it. It neither fully reconciles the
standalone refute (item 2) with the integration negative (the direction gap
does not collapse to zero) nor fully confirms the integration's framing (the
rules do not win on direction alone — most of their lead is magnitude).

## The numbers

Two arms, scored through `score_frequency_state` with the new
`state_profile_direction_deconf` and `state_profile_magnitude` companion metrics
added alongside the unchanged `state_profile_directional`.

| Arm | `state_profile_directional` (conflated) | `state_profile_direction_deconf` (direction-only) | `state_profile_magnitude` (magnitude-only) | `state_profile` (blind) |
| --- | ---: | ---: | ---: | ---: |
| **Rules (v08 hybrid)** | **0.8897** (tp=125 fp=16 fn=15) | **0.8953** (tp=124 fp=14 fn=15) | **0.9447** (tp=111 fp=8 fn=5) | 0.9338 |
| **Selector (closed-option integration)** | **0.8333** (tp=115 fp=21 fn=25) | **0.8727** (tp=120 fp=16 fn=19) | **0.8950** (tp=98 fp=5 fn=18) | 0.9338 |
| **Gap (rules − selector)** | **+0.0564** | **+0.0226** | **+0.0497** | 0.0000 |

### Anchor reproduction (contract check)

Both conflated anchors reproduced to 0.0000 drift: rules
`state_profile_directional` = 0.8897 (the v08 hybrid reference), selector =
0.8333 (the integration probe's result). `state_profile` (the direction- and
magnitude-blind metric) is **byte-identical** across arms (0.9338, tp=127 fp=9
fn=9) — the deconflation touched only the direction/magnitude axes, confirming
the rekey is isolated from scorer drift. **No contract failure.**

### Predeclared outcome verdict

| Outcome band | Verdict | This run |
| --- | --- | --- |
| Direction-deconflated gap collapses to ≤ +0.01 | MEASUREMENT ARTIFACT | ✗ (+0.0226) |
| **Direction-deconflated gap shrinks but stays > +0.01** | **MAGNITUDE IS PART OF THE GAP, NOT ALL OF IT** | **✓ (+0.0226; 60% reduction from +0.0564)** |
| Direction-deconflated gap ≈ +0.0564 (unchanged) | CONFLATION IS NOT THE EXPLANATION | ✗ |
| `state_profile` regresses / anchor fails | CONTRACT FAILURE | ✗ (byte-identical; anchors exact) |

## What the decomposition shows

**Magnitude axis (the larger share).** The rules recover 111/116 magnitude facts
(recall 0.957); the selector recovers 98/116 (recall 0.845) — the selector
**drops 13 magnitude facts** the rules catch. This is the integration ledger's
"selector systematically abandons Frequent/Infrequent" signature
(`Infrequent` 19→0, `Frequent` 16→4 on the direction-in-play mentions), now
measured cleanly and separated from the direction axis. The magnitude gap
(+0.0497) is larger than the conflated gap (+0.0564)... almost as large, because
the magnitude axis has a different denominator shape (only the Frequent/
Infrequent rows populate it; the per-letter presence-set keying differs from
the conflated metric's). The honest reading: **on the magnitude axis, the rules
win by recall (0.957 vs 0.845); the selector's precision is actually higher
(0.9515 vs 0.9328)** — when the selector *does* emit a magnitude, it is right,
but it emits far fewer.

**Direction axis (the residual).** The rules recover 124/139 direction facts
(recall 0.892); the selector recovers 120/139 (recall 0.863) — a smaller,
genuine direction gap. The selector is not merely losing on magnitude; it also
loses ~4 direction facts the rules catch. The direction-deconflated gap (+0.0226)
is the clean measurement of "the deterministic rules are better at direction
itself, controlling for the vocab conflation."

**Net attribution.** Of the +0.0564 conflated gap, roughly two-thirds is
attributable to the magnitude axis (the selector abandoning Frequent/Infrequent)
and roughly one-third to a genuine direction residual. The split is approximate
because the two axes have different key shapes; the precise statement is that
the gap **shrinks 60% when magnitude is removed** and the residual is a real
+0.0226 direction gap.

## Why this is the synthesis probe (and what it resolves)

This probe was designed to resolve the tension between two prior findings:

- **Item 2 (standalone, +0.0552):** the closed-option contract *refutes*
  "fundamental" — on the raw direction-blind artifact, the selector recovers
  direction the free-write contract could not. The gap does not survive a
  generation-contract change.
- **Item 2 follow-up (integration, −0.0563):** the same selector, wired to
  *replace* the deterministic rules on the hybrid lane, *loses*. The gap
  survives replacing the rules.

**This probe tests the third survival question: does the integration gap survive
a scoring-axis change?** The answer: **partially.** It shrinks substantially
(60%) but does not vanish. The reconciliation:

- The integration result's mechanism reading — *"the deterministic rules win
  because they faithfully implement the conflated gold vocab; the LLM answers
  the plain-English direction question, a subset"* — is **partially confirmed**.
  The magnitude axis is exactly the subset the LLM drops, and that is most of
  the gap.
- But the reading is **not fully confirmed**: a residual direction gap remains,
  so the rules are not *only* winning via the vocab conflation. They also make
  better direction calls than the selector on ~4 facts.

The two prior findings are therefore in **partial, not full, reconciliation**.
The standalone refute stands (the contract deploys capacity on the raw
artifact); the integration negative stands (the rules win on the hybrid
substrate); this probe attributes *most* of the integration gap to the vocab
conflation but isolates a real direction residual the conflation does not
explain.

## Implications for the manuscript

1. **The SF section carries a 2-axis attribution table.** Alongside the cited
   `state_profile_directional` (0.8897 rules / 0.8333 selector), report the
   direction-only (0.8953 / 0.8727) and magnitude-only (0.9447 / 0.8950)
   companions. The honest claim: *the deterministic rules' production advantage
   over the LLM selector is ~60% the magnitude axis (which the selector
   systematically abandons) and ~40% a genuine direction residual.*
2. **The "vocab-design finding" from the integration doc is refined, not
   dropped.** The integration results doc framed the rules' win as a vocab-
   conflation artifact. This probe shows that framing is *partially* supported:
   the conflation explains the majority of the gap, but the rules also win on
   direction itself. The manuscript should state both halves rather than
   attributing the whole gap to the vocab.
3. **The magnitude axis is the cleaner production story.** The selector's
   magnitude precision (0.9515) exceeds the rules' (0.9328); its problem is
   recall (drops 13 facts), not correctness. A complement design (selector
   emits magnitude only when the rules have no regex match — the 21/25 letters
   with no deterministic cue flagged in the integration doc) could close the
   magnitude recall gap without sacrificing precision. That design is out of
   scope here but is now precisely motivated by the decomposition.

## Limitations and honest caveats

- **dev140 only.** Both input artifacts are dev140; test59 is frozen. All gaps
  are dev140 numbers.
- **The two axes have different key shapes.** `state_profile_direction_deconf`
  and `state_profile_magnitude` are per-letter presence-set metrics over a
  3-valued (direction) or 3-valued (magnitude: frequent/infrequent/none) vocab,
  deduplicated per letter — the same shape as `state_profile_directional`, but
  the population of keys differs (magnitude has fewer non-`none` entries). The
  gaps are therefore not strictly additive across axes; the "60% / 40%" split is
  a proportional reading of the gap-shrinkage, not a decomposition of a single
  F1 into two independent components. The precise, assumption-free statement is
  the shrinkage: the gap goes from +0.0564 (conflated) to +0.0226 (direction-
  only).
- **The magnitude→direction projection is a frozen choice, not a measured
  fact.** Magnitude labels project to direction `same` (a magnitude statement
  carries no direction signal). The alternative (`unknown`) would change the
  direction-denominator. The predeclaration flagged this as a contract-failure
  trigger if results were sensitive; the result is *not* sensitive to the
  choice in a way that changes the verdict (both projections shrink the gap
  substantially and leave a residual), so `same` stands as the honest encoding.
- **Replay artifacts, not live runs.** The selector's picks are taken from the
  saved integration artifact; no new selector calls fire. The decomposition
  reflects the integration probe's specific selector behavior, not a fresh run.
- **Gold is frozen; the conflation is in the annotation guideline.** This probe
  does not propose re-annotating. The deconflated metrics are *companions* that
  explain the gap; the cited headline metric remains `state_profile_directional`
  (the conflated 5-way metric), unchanged.

## What this is NOT

- Not a gold-schema change. The conflation is in the guideline (Appendix L987,
  "Aligned"); gold is frozen. This is a scoring-side rekey.
- Not a re-test of "fundamental." The standalone probe settled that on the raw
  artifact. This tests the *integration* gap's sensitivity to a scoring-axis
  change.
- Not a re-run of the integration probe. The selector's picks are reused; no
  new LLM calls.
- Not a claim that the magnitude labels are wrong. They are a legitimate part
  of the guideline's `FrequencyChange` semantics; the point is that they are a
  different axis from change-direction, now measured separately.

## Artifacts / Provenance

- Driver: `scripts/run_exectv2_sf_direction_vocab_deconflation.py` (zero LLM
  calls; rekey + re-score over frozen predictions).
- Summary: `experiments/exectv2_sf_direction_vocab_deconflation_summary_20260708.json`
  (conflated + direction-deconf + magnitude-deconf PRF1 for both arms; the
  in-run anchor reproduction; the gap comparison).
- Key builders: `frequency_state_direction_deconf` +
  `frequency_state_magnitude` + the `_score_frequency_state_profile_*` scorers
  (`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/seizure_frequency.py`);
  re-exported from `scoring/__init__.py`. No change to existing functions.
- Tests: `tests/test_exectv2_scoring.py` (6 new tests covering the projection
  functions, the integrated metrics, and the `state_profile`-byte-identical
  guardrail).
- Input artifacts: `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl`
  (rules arm); `experiments/exectv2_sf_closed_option_hybrid_integration_dev140_20260707.jsonl`
  (selector arm — note: the integration results doc cites a `20260706` date; the
  artifact file is dated `20260707`; the numbers reproduce exactly either way).
- Prior art: `sf_closed_option_hybrid_integration_2026-07-06` (registry entry
  35, the integration probe whose mechanism section this test isolates).
- Split discipline: dev140 only; 0 LLM calls; no test59 / full-200 row
  inspection.
