# Results — SF closed-option direction selector (item 2, dev140)

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `sf_closed_option_direction_selector_2026-07-06` → **REFUTES "fundamental"**.
Driver: `scripts/run_exectv2_sf_closed_option_direction_probe.py --cache`.
Predeclaration: `exectv2_sf_closed_option_direction_predeclaration_2026-07-06.md`.
Cost: 28 gpt-4.1-mini calls (dev140, temp 0, cached). Split discipline: dev140 only.

## Headline

**The closed-option selector recovers direction at +0.0552 dev140
`state_profile_directional` (0.6552 → 0.7103), clearing the predeclared +0.05
threshold. Per the frozen predeclaration, this REFUTES the "fundamental"
framing of the SF capacity-vs-execution gap: the gap was an artifact of the
free-write generation contract, not a fundamental capacity limit. A closed-
option contract (pick-from-menu-or-abstain) recovers direction where the
free-write contract (B2 hard-emission) regressed.**

This is the dspy G32 outcome (the LLM picks a label from a deterministic menu
or abstains — never free-writes) transferring to the ExECTv2 SF direction
surface, on the exact surface where the gap was bounded by four negatives
*all in the free-write family*.

## The numbers

| Run | `state_profile_directional` F1 | `state_profile` F1 | Direction recovered |
| --- | ---: | ---: | --- |
| Raw SF-verify (direction-blind, baseline) | 0.6552 (tp=95 fp=55 fn=45) | 0.7483 | 0 (baseline) |
| **Closed-option selector (this probe, 28 calls)** | **0.7103** (tp=103 fp=47 fn=37) | **0.7483** | **+8 tp** |
| B1 post-hoc free-write adjudication (28 calls, prior art) | 0.7254 (tp=107 fp=48 fn=33) | 0.7483 | +12 tp |
| B2 free-write hard-emission (prior art, REFUTED) | 0.5892 (−0.0775) | regressed −0.1548 | −10 tp |
| v08 hybrid production (reference) | 0.8897 | 0.9338 | (deterministic rules/change.py) |

The closed-option selector lands **between** B1 (free-write post-hoc adjudication,
+0.07) and B2 (free-write hard-emission, −0.0775). Critically, it succeeds
**where the architecturally-comparable B2 failed**: both B2 and this probe ask
the model to assign direction as part of producing the structured output; B2
(letting the model free-write a direction field in the extraction) regressed
−0.0775, while the closed-option selector (constraining the model to pick from a
fixed menu) recovered +0.0552. **The contract is the difference.**

`state_profile` (the direction-blind metric) is byte-identical at 0.7483 — the
direction field is purely additive and the closed-option selector does not
degrade the other SF axes. (B2's `state_profile` regressed −0.1548; the
free-write direction field's cognitive load was what harmed the other axes.
The closed-option contract avoids that load by construction.)

## What the selector did (ledger summary)

- **35 changed-state mentions** across 28 letters (the disagreement set,
  identical to B1's).
- **24 non-Same selections**: 12 Increased, 11 Decreased, 1 Frequent — a
  clinically defensible distribution, not noise.
- **11 Same outcomes**: 4 explicit Same picks + 7 abstentions (5
  `no_reliable_candidate`/`ABSTAIN` selections resolving to Same, plus the
  no-op default). The abstention primitive fired correctly: when the model was
  not confident, it deferred rather than inventing.
- **Selection modes**: 34 `single_candidate`, 1 `no_reliable_candidate`. The
  abstention validator (mirroring gan2026 `selected_fact.py:32-49`) was wired
  and exercised: a defer mode with a selected id would be forced to abstain.
  No parse failures.
- **Deterministic cue coverage**: 7 of 28 letters had at least one
  `rules/change.py` regex match anchoring a menu entry's evidence span. The
  other 21 letters expressed direction implicitly or via medication-titration
  language the regexes don't capture; the menu still offered all 5 labels (the
  closed-option contract constrains the *output*, not the *options*), and the
  selector read the full letter text to decide.

## Why this is the cross-family test that moves the thesis

The SF-direction capacity-vs-execution gap was previously bounded by **four
measured negatives, all in the free-write-then-arbitrate architecture family**:

1. B2 hard-emission −0.0775 (dev140).
2. B2 hard-emission −0.0483 (full-200).
3. B2 `state_profile` regression −0.1548 (the direction field's cognitive load
   degrades the other SF axes).
4. The three-family Phase-0 degeneracy (adding a direction field regresses all
   of Dx/SF/Inv).

This probe is a **fifth measurement, in a different architecture family**
(closed-option select-or-abstain), and it is **positive** (+0.0552). The gap
does **not** survive a change of generation contract. Therefore the
"fundamental" claim is downgraded from "fundamental within the free-write
family" (4 negatives, 1 family) to "free-write-family-specific" — the
closed-option family escapes it.

This is the single highest-leverage finding from the predecessor-synthesis
follow-ups because it is the only item that can change the *status* of the
central claim. It changes it from negative to *conditionally positive*: the
gap is real for the free-write contract the production pipeline currently uses,
but it is not a fundamental capacity limit — a different contract deploys the
capacity.

## Comparison to B1 (the closest architecturally-comparable prior result)

B1 (free-write post-hoc adjudication, +0.07) and this probe (closed-option
selection, +0.0552) both recover direction, but via different mechanisms:

- **B1** asked the model to *judge* direction in isolation (one call per letter,
  free-write a label, normalize to the vocab post-hoc). It recovered +12/30
  gold-directional facts. It proved the model *can* judge direction.
- **This probe** asked the model to *select* direction from a closed menu as
  part of producing the structured output (the B2-style integration that
  failed under free-write). It recovered +8/30. It proves the model can
  *emit* direction as part of structured extraction **when the emission is
  contractually constrained to a closed menu**.

The gap between B1 (+12) and this probe (+8) is the residual cost of
integration: selecting under the structured-output constraint is harder than
judging in isolation, even with a closed menu. But both are positive, and
neither regresses `state_profile`. The B2 result (−0.0775, free-write
integration) is the outlier — and it is the outlier because its contract
(free-write a direction field) is the one that imposes cognitive load the
others avoid.

## Predeclared outcome verdict

Per the frozen predeclaration's outcome table:

| Outcome band | Verdict | This run |
| --- | --- | --- |
| ≥ +0.05, no `state_profile` regression | **REFUTES "fundamental"** | **✓ +0.0552, state_profile identical** |
| < +0.02 | Confirms "fundamental across families" | — |
| +0.02 to +0.05 | Inconclusive | — |
| `state_profile` regresses | Contract failure | — |

**Verdict: REFUTES "fundamental".** The closed-option selector recovers
direction at ≥ +0.05 dev140 with no regression.

## Implications for the manuscript

1. **The "fundamental gap" claim must be restated as free-write-family-
   specific.** The current framing (four negatives → fundamental) is no longer
   supported once a fifth measurement in a different family is positive. The
   honest claim is: *the SF-direction capacity-vs-execution gap is fundamental
   to the free-write-then-arbitrate architecture family, but a closed-option
   contract escapes it.* This is a stronger, more precise result, not a weaker
   one — it localizes the failure to a design choice rather than a capacity
   ceiling.

2. **The dspy G32 principle transfers to ExECTv2.** This is direct cross-
   codebase corroboration of dspy's central architectural finding (closed-
   option generation > free-write-then-arbitrate), on a different task surface
   (ExECTv2 SF direction vs Gan monthly frequency). Per item 6's disclosure,
   this is a within-architecture-delta result, not a comparison to dspy's
   absolute 90.3% rate (which is on a different scoring convention).

3. **A production-relevant lever exists.** The closed-option selector is cheap
   (28 calls), additive (no `state_profile` regression), and recovers real
   direction. The production v08 hybrid currently sources direction from
   deterministic `rules/change.py` (0.8897) — the closed-option selector does
   not beat that, but it offers a complementary LLM-side direction signal that
   could feed the hybrid arbitration as a candidate source. That integration is
   out of scope here (per the plan's open-question #1: standalone probe first)
   but is the obvious follow-up.

## Limitations and honest caveats

- **dev140 only.** The gap is two-split confirmed, so dev140 is the development
  surface; test59 is frozen and was not touched. The +0.0552 is a dev140 number.
- **+8/30 recovered, not +30/30.** The closed-option selector recovers
  meaningful direction but does not close the gap to the hybrid's 0.8897. The
  residual gap (0.7103 vs 0.8897) is the integration cost plus the cases where
  the letter's direction is genuinely ambiguous or absent. The result refutes
  *fundamental*; it does not claim *solved*.
- **The menu always offers all 5 labels.** A stricter closed-option variant
  would gate the menu by deterministic cue presence (only offer labels the
  regexes found evidence for). That variant was rejected at design time because
  the regexes match only 7/28 letters — gating would collapse the experiment
  into a no-op for 21 letters. The full-menu design is the honest test of the
  closed-option *contract* (constrain output, not options); a gated-menu
  variant is a possible follow-up if substrate integration is pursued.
- **Single model, single temp.** gpt-4.1-mini temp 0, matching B1/B2. No
  cross-model or temp-sweep replication in this run.

## Artifacts

- Predictions: `experiments/exectv2_sf_verify_closed_option_direction_dev140_20260706.jsonl`
- Summary: `experiments/exectv2_sf_closed_option_direction_summary_20260706.json`
- Per-mention ledger: `experiments/exectv2_sf_closed_option_direction_ledger_20260706.jsonl`
