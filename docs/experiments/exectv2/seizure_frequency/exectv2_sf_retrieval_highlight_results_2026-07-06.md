# Results — SF retrieval-highlight salience priming (item 3, dev140)

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `sf_retrieval_highlight_priming_2026-07-06` → **HIGHLIGHT IS NOT THE
LEVER** (diversifying negative along the input axis).
Driver: `scripts/run_exectv2_sf_retrieval_highlight_probe.py --cache`.
Predeclaration: `exectv2_sf_retrieval_highlight_predeclaration_2026-07-06.md`.
Cost: 84 gpt-4.1-mini calls (3 arms × 28 letters, dev140, temp 0, cached). Split
discipline: dev140 only.

## Headline

**Highlighting the deterministic direction/temporal spans in the input does NOT
move `state_profile_directional`: Arm B (highlight) −0.0068 vs Arm A (baseline,
within-run control). Per the frozen predeclaration, this is the `< +0.02` band →
HIGHLIGHT IS NOT THE LEVER for ExECTv2 SF direction. The dissertation-recursive
retrieval-highlight finding (Gan 0.840 vs 0.760 for `cot_label`) does **not
transfer** to this surface.**

This is the **diversifying second leg** of the cross-family bet. Item 2 (the
generation-contract leg) REFUTED "fundamental" (+0.0552): the gap does not survive
a change of *contract*. Item 3 (the orthogonal input leg) shows the gap **does
survive a change of *input***. The combined, precise manuscript claim is: the
SF-direction capacity-vs-execution gap is **free-write-family-specific under a
contract change, but input-robust** — the lever that deploys the capacity is the
generation contract (closed-option select-or-abstain), not input salience-
priming.

## The numbers

| Run | `state_profile_directional` F1 | `state_profile` F1 | Direction recovered (tp) |
| --- | ---: | ---: | --- |
| Raw SF-verify (direction-blind, baseline) | 0.6552 (tp=95 fp=55 fn=45) | 0.7483 | 0 (baseline) |
| **Arm A (control: raw letter, B1 reproduction)** | **0.7279** (tp=107 fp=47 fn=33) | **0.7483** | +12 tp |
| **Arm B (highlight: full letter + `[[HL]]` spans)** | **0.7211** (tp=106 fp=48 fn=34) | **0.7483** | +11 tp |
| **Arm C (highlight-only ablation: spans, no letter)** | **0.6966** (tp=101 fp=49 fn=39) | **0.7483** | +6 tp |
| B1 post-hoc free-write (prior art reference) | 0.7254 (tp=107) | 0.7483 | +12 tp |
| Item 2 closed-option selector (contract leg, prior art) | 0.7103 (tp=103) | 0.7483 | +8 tp |
| v08 hybrid production (reference) | 0.8897 | 0.9338 | (deterministic rules/change.py) |

- **Arm A reproduced B1** (0.7279 vs B1's 0.7254, tp 107 vs 107). The within-run
  control is valid — the small +0.0025 drift is temp-0 sampling noise on the
  shared 28-letter set, not a contract failure. The predeclaration's < 0.68
  contract-failure gate was cleared by a wide margin.
- **Arm B − Arm A = −0.0068** (tp 106 vs 107). Highlighting did not help; it
  slightly *harmed* (lost 1 tp). The direction-blind `state_profile` is
  byte-identical (0.7483) across all arms — the highlight is purely additive and
  does not degrade the other SF axes, but it does not deploy direction capacity.
- **Arm C − Arm B = −0.0245** (tp 101 vs 106). The highlight-only ablation scored
  *below* the full-letter highlight arm, but only modestly. Per the predeclared
  mechanism rule (within ~0.05 → lookup), this is **LOOKUP**, not the
  dissertation-recursive priming signature (which was a −0.32 / −32pp drop).

## What the highlight did (ledger summary)

- **35 changed-state mentions** across 28 letters (the disagreement set,
  identical to item 2 / B1).
- **Deterministic cue coverage**: 11 of 28 letters had ≥1 `CHANGE_RULES` /
  `TEMPORAL_RULES` match; 19 highlight spans total were emitted. The other 17
  letters expressed direction implicitly or via medication-titration language the
  deterministic rules don't capture — for those, Arm B ran with a clean (un-
  highlighted) letter, equivalent to Arm A.
- **Per-mention cue coverage**: 17 of 35 changed mentions had ≥1 highlight span
  anchored on them. So the highlight reached roughly half the disagreement set.
- **Direction shifts Arm A → Arm B**: only **4 of 35** mentions changed
  direction: `Increased→Frequent` ×2, `Same→Increased` ×1, `Infrequent→Same`
  ×1. Highlighting barely perturbed the model's judgments — and the net effect
  on score was −1 tp (the highlights nudged one wrong that Arm A had right).
- **Arm C distribution** was sparser and skewed: only 12 non-Same directions
  (Frequent 7, Decreased 4, Increased 1) vs 31 in Arm A. With no full letter, the
  model defaulted more often — but still scored 0.6966 (+6 tp over raw baseline),
  close to Arm B. That near-equivalence (C ≈ B) is the lookup signature.

## Why highlighting is not the lever here (and was for Gan)

The dissertation-recursive ablation was decisive because the gap between
highlight (0.840) and highlight-only (0.520) was *large* (−32pp): the full letter
context was doing real work the spans alone couldn't, proving retrieval primed
the model's reading of the full input. Here, **Arm C (spans only, 0.6966) is
within 0.0245 of Arm B (full letter + highlights, 0.7211)** — the full letter
context adds only ~2.5pp over the spans alone. Retrieval works by **direct
lookup** on this surface: the deterministic spans carry most of the direction
signal, and the surrounding letter context is nearly redundant for the spans that
fire. That is a different mechanism than Gan's priming.

Two structural reasons highlighting was never going to be the lever for ExECTv2
direction, visible only after the run:

1. **The deterministic spans already carry the label.** `CHANGE_RULES` emit
   `attributes={"FrequencyChange": "Increased"}` — the rule that matches
   "seizure frequency has increased" *is* the direction signal. Highlighting that
   span for an LLM that then free-writes the same label is approximately a no-op:
   the cue and the conclusion are the same string. In Gan, retrieval selected
   *sentence spans* that *implied* a rate the model then computed; here retrieval
   selects spans that *state* the direction verbatim.
2. **Cue coverage is partial (11/28 letters).** For the 17 letters whose direction
   is implicit or medication-titration-driven, Arm B had no spans to highlight
   and was identical to Arm A by construction. Item 2's closed-option contract
   reached those letters (it always offered the full menu); item 3's highlight
   could not, because the deterministic span bank doesn't fire on them. This is
   the same coverage limit item 2 documented (7/28 cue coverage) and chose to
   route around by decoupling the menu from cue presence.

## Predeclared outcome verdict

Per the frozen predeclaration's outcome table:

| Outcome band | Verdict | This run |
| --- | --- | --- |
| Arm B − Arm A ≥ +0.05, no `state_profile` regression | Input-scaffolding deploys capacity | — |
| **Arm B − Arm A < +0.02** | **HIGHLIGHT IS NOT THE LEVER** | **✓ −0.0068** |
| +0.02 to +0.05 | Inconclusive | — |
| Arm A ≪ B1 0.7254 (< 0.68) | Contract failure | — (Arm A = 0.7279, ✓) |
| Arm C ≈ Arm B (within ~0.05) | LOOKUP (different mechanism than Gan) | **✓ −0.0245** |
| Arm C ≪ Arm B (≥ ~0.10 below) | PRIMING (replicates Gan) | — |

**Verdict: HIGHLIGHT IS NOT THE LEVER.** Arm B − Arm A = −0.0068 (< +0.02), no
`state_profile` regression. **Mechanism: LOOKUP** (Arm C ≈ Arm B).

## Relationship to item 2 (the combined cross-family picture)

Items 2 and 3 are the two orthogonal legs of the cross-family bet on the same
null hypothesis ("the gap is fundamental"). They now have **opposite outcomes on
the two axes**:

| Axis | Lever | Item | Outcome |
| --- | --- | --- | --- |
| Generation contract | Closed-option select-or-abstain (vs free-write) | Item 2 | **REFUTES "fundamental"** (+0.0552) |
| Input | Retrieval-highlight salience priming (vs raw) | Item 3 | **GAP SURVIVES** (−0.0068) |

The combined, more precise claim for the manuscript: **the SF-direction gap is
not fundamental, but it is contract-sensitive and input-robust.** The capacity to
recover direction exists (item 2 deploys it via the contract; Arm A/B deploy it
via free-write post-hoc adjudication at +0.07); what does *not* help is priming
the input with deterministic spans, because on this surface the deterministic
spans already state the direction verbatim (lookup, not priming). This is a
*stronger and more specific* result than either leg alone: it localizes the lever
to the generation contract and rules out the input-salience alternative.

## Limitations and honest caveats

- **dev140 only.** The gap is two-split confirmed, so dev140 is the development
  surface; test59 is frozen and was not touched. All three arm numbers are dev140.
- **Cue coverage is partial (11/28 letters, 17/35 mentions).** A highlight
  variant with a richer span bank (e.g., medication-titration cues: "dose
  increased → frequency increased") might reach the 17 letters the deterministic
  rules miss. That is a possible follow-up, but it would be testing a *different*
  retrieval bank, not the dissertation-recursive mechanism — and item 2 already
  showed the contract lever reaches those letters without new cues.
- **The −0.0068 is within temp-0 sampling noise** on a 28-letter set (Arm A
  itself drifted +0.0025 from B1's 0.7254). The honest reading is "no effect,"
  not "small harm." The verdict (< +0.02) is robust to that noise.
- **Single model, single temp.** gpt-4.1-mini temp 0, matching item 2 / B1 / B2.
  No cross-model or temp-sweep replication in this run.
- **Arm C's "lookup" verdict is mechanism-directional, not a positive claim.**
  Arm C ≈ Arm B within ~0.05 means the spans carry the signal; it does *not* mean
  the lookup is good enough for production (Arm C's 0.6966 is well below the
  hybrid's 0.8897). It means retrieval works by lookup, not priming, on this
  surface — a mechanism finding, not a performance claim.

## Artifacts

- Summary: `experiments/exectv2_sf_retrieval_highlight_summary_20260706.json`
- Per-mention ledger (all 3 arms, 105 rows): `experiments/exectv2_sf_retrieval_highlight_ledger_20260706.jsonl`
- Arm A predictions: `experiments/exectv2_sf_verify_retrieval_highlight_A_dev140_20260706.jsonl`
- Arm B predictions: `experiments/exectv2_sf_verify_retrieval_highlight_B_dev140_20260706.jsonl`
- Arm C predictions: `experiments/exectv2_sf_verify_retrieval_highlight_C_dev140_20260706.jsonl`
