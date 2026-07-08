# Results — SF magnitude-complement probe (2026-07-08)

Date: 2026-07-08. Owner: ExECTv2 workstream.
Hypothesis: `sf_magnitude_complement_2026-07-08` → **COMPLEMENT TRAILS RULES**
(the predeclared band (c) negative; the magnitude recall gap is a genuine
capacity gap that no contract design closes).
Driver: `scripts/run_exectv2_sf_magnitude_complement.py` (13 gpt-4.1-mini calls,
dev140, temp 0, cached, replay mode over the saved v08 hybrid artifact).
Predeclaration: `exectv2_sf_magnitude_complement_predeclaration_2026-07-08.md`.

## Headline

**Restricting the closed-option selector to a magnitude-only menu on the
letters where the deterministic magnitude regexes had no match does NOT beat
the rules — it trails them (magnitude F1 0.9244 vs 0.9447, −0.0203). The
selector's precision edge, measured at 0.9515 on the full direction-in-play
set by the deconflation probe, does NOT transfer to the no-match subset: on
those hard letters the complement's magnitude precision drops to 0.9016 —
below both the rules (0.9328) and the standalone selector (0.9515) — and it
introduces 4 new false positives. The no-match letters are exactly where the
LLM's magnitude judgment is weakest. The magnitude recall gap is a genuine
capacity gap that no contract design recovers.**

This lands in the **predeclared band (c)** — the cleanest negative. The
deconflation probe's decomposition predicted the selector's precision edge
*could* transfer to a complement design; this probe tests that prediction
directly and **refutes it**.

## The numbers

Three arms, scored through `score_frequency_state`. The rules arm is the v08
hybrid baseline (reproduced in-run); the selector arm is the integration
probe's saved artifact (the deconflation probe's selector column); the
complement arm is this run (magnitude-only selector, fires only on the 13
no-magnitude-regex-match letters).

| Arm | `state_profile_magnitude` F1 | precision | recall | tp / fp / fn |
| --- | ---: | ---: | ---: | --- |
| **Rules (v08 hybrid)** | **0.9447** | 0.9328 | 0.9569 | 111 / 8 / 5 |
| **Selector (integration, 5-label)** | 0.8950 | **0.9515** | 0.8448 | 98 / 5 / 18 |
| **Complement (this probe, 3-label, no-match subset)** | **0.9244** | 0.9016 | 0.9483 | 110 / 12 / 6 |

The conflated and blind metrics (the full bracket):

| Arm | `state_profile_directional` (conflated) | `state_profile` (blind) |
| --- | ---: | ---: |
| Rules (v08 hybrid) | **0.8897** (tp=125 fp=16 fn=15) | 0.9338 |
| Complement (this probe) | 0.8602 (tp=120 fp=19 fn=20) | **0.9338** (byte-identical) |

### Anchor reproduction (contract check)

All three baseline anchors reproduced to ≤ 0.0001 drift (directional 0.8897,
magnitude 0.9447, state_profile 0.9338). `state_profile` (the direction- and
magnitude-blind metric) is **byte-identical** after the complement override
(0.9338, tp=127 fp=9 fn=9) — the complement touched only the magnitude axis on
the no-match subset, exactly the isolation the integration probe's replay mode
and the deconflation probe's byte-identical check established. **No contract
failure.**

### Predeclared outcome verdict

| Outcome band | Verdict | This run |
| --- | --- | --- |
| Complement magnitude F1 > 0.9447 + 0.005 AND state_profile byte-identical | COMPLEMENT BEATS RULES | ✗ (0.9244) |
| Complement magnitude F1 within ±0.005 of 0.9447 | COMPLEMENT APPROACHES RULES | ✗ (0.9244) |
| **Complement magnitude F1 < 0.9447 − 0.005** | **COMPLEMENT TRAILS RULES** | **✓ (0.9244; −0.0203)** |
| state_profile regresses > 0.005 or anchor fails | CONTRACT FAILURE | ✗ (byte-identical; anchors exact) |

## The complement subset (the count the integration doc estimated, now measured)

The integration results doc cited "the 21/25 letters with no deterministic
cue" as a prose claim (not artifact-emitted). This run **measures** it for
the magnitude axis: of the 25 direction-in-play letters, **12 carry a
magnitude regex match** (`change.frequent` or `change.infrequent`) and **13
do not**. The complement fires on those 13. (The integration doc's "21/25"
figure was for the broader "any direction cue" reading of "no deterministic
cue," not the magnitude-only reading this probe gates on — see the trigger
design choice in the predeclaration. The 13 measured here is the magnitude-
axis-specific count the complement design requires.)

The selector emitted a non-Same magnitude on 9 of the 13 letters
(`Infrequent` 8, `Frequent` 1); all 13 were `single_candidate` mode (no
abstentions). So the selector was willing to answer the magnitude question
on 9/13 of the no-match letters — but its answers were wrong often enough
that the net effect is negative.

## What the decomposition shows

**The precision edge did not transfer (the key finding).** The deconflation
probe measured the selector's magnitude precision at 0.9515 on the full
direction-in-play set and flagged it as "the cleaner production story" —
"when the selector *does* emit a magnitude it is right, but it emits far
fewer." This probe tests the production implication: restrict the selector
to the no-match subset (where it can only help, never duplicate the rules)
and see if the precision edge holds. **It does not.** The complement's
magnitude precision is **0.9016** — below the rules' 0.9328 and well below
the standalone selector's 0.9515. The 0.9515 figure was a property of the
selector *on the letters it chose to answer under the 5-label contract*; the
no-match subset is a different, harder set, and the selector's precision edge
is conditional on the easy letters the rules already cover.

**Recall nearly matches, precision drops.** The complement recovers 110/116
magnitude facts (recall 0.9483) — close to the rules' 111/116 (recall 0.9569),
a gap of just one true positive. But it adds 4 false positives (12 vs the
rules' 8), and that precision loss dominates: the F1 drops from 0.9447 to
0.9244. The complement's failure mode is over-emission on the hard letters,
not under-emission — the opposite of the standalone selector's recall-driven
failure. A magnitude-only menu did not fix the underlying judgment problem;
it changed its shape from "abstain too much" (recall) to "assert too much"
(precision), on the harder subset.

**The direction axis also regressed.** The complement's `state_profile_directional`
dropped from 0.8897 to 0.8602 (−0.0295) because overwriting `FrequencyChange`
with a magnitude label on the 13 no-match letters reclassifies those mentions
on the conflated direction axis too (the deconflation probe's magnitude→direction
projection sends them to `same`, but the *conflated* metric still scores the
literal label). This is expected and not the verdict driver (the verdict is on
the magnitude axis); it confirms the complement is a magnitude-axis intervention
with side effects on the conflated metric, consistent with the deconflation
probe's two-axis framing.

## Why this is the production-pathway close-out

This was pathway #1 — the highest-leverage of the four 07-08 follow-ups
because it was the only one that *could* yield a genuine production
improvement (a deterministic-LLM complementarity result). The deconflation
probe's decomposition made the motivation precise: the selector drops 13
magnitude facts the rules catch (recall deficit) but emits them more
accurately when it does (precision edge), and the rules have no regex match
on a substantial share of letters. A complement design — selector fires only
where the rules are silent — is the obvious way to exploit that asymmetry.

**This probe refutes that exploitation.** The precision edge is a selection
effect, not a transferable property: the selector was accurate on the easy
magnitude letters, and the no-match subset is the hard ones where it is not.
No contract design (5-label direction menu, 3-label magnitude menu, full
replacement, complement-on-no-match) recovers the magnitude recall gap
without paying a larger precision cost. The deterministic `rules/change.py`
magnitude regexes remain the magnitude source of record, and the 0.9447
magnitude F1 stands as the ceiling on this surface under the current
architecture.

## Implications for the manuscript

1. **The SF magnitude-axis story is now closed as a negative.** The
   deconflation probe added a 2-axis attribution table (direction 0.8953 /
   0.8727; magnitude 0.9447 / 0.8950). This probe adds the third column — the
   complement (magnitude 0.9244) — and the honest claim: *restricting the LLM
   to the letters where the deterministic magnitude regexes are silent does
   not help; the selector's precision edge is a selection effect that does
   not transfer to the hard cases.* The deterministic rules own the magnitude
   axis, full stop.
2. **The "deterministic-LLM complementarity" framing is not available for SF
   magnitude.** The Rx split-dependent inversion (07-03) is the one place
   where a deterministic-LLM ensemble has a non-trivial complementarity
   argument; this probe confirms SF magnitude is not a second such place. The
   manuscript should not claim complementarity on SF.
3. **The 0.9447 magnitude F1 is the ceiling.** The manuscript should state it
   alongside the conflated `state_profile_directional` (0.8897) as the
   production reference, and note that the complement probe confirmed it is
   not improvable by LLM augmentation on the no-match subset.

## Limitations and honest caveats

- **dev140 only.** The input artifact is dev140; test59 is frozen. All gaps
  are dev140 numbers.
- **Replay artifact, not a live run.** The complement loads the saved v08
  hybrid SF artifact and overwrites `FrequencyChange` on the 13 no-match
  letters; it does not re-run the assessment stage. The assessment-stage
  keep/drop decisions are inherited from v08 unchanged. The `state_profile`
  byte-identical check confirms the override touched only the magnitude axis.
- **Single model, single temperature.** gpt-4.1-mini at temp 0. The
  complement's precision drop (0.9515 → 0.9016) is a property of this model
  on these letters; a different model might transfer the precision edge. But
  the deconflation probe's precision figure was also gpt-4.1-mini, so the
  within-model comparison (precision edge does not transfer) is valid.
- **The magnitude-only menu removes the direction labels by construction.**
  This is the design choice that makes the complement a clean magnitude-axis
  test, but it also means the selector cannot recover a direction fact even
  if one were recoverable — the direction axis is out of scope here (the
  deconflation probe isolated a residual +0.0226 direction gap that remains
  open under a separate pathway).
- **The trigger is "magnitude regex had no match," confirmed as the design
  choice.** A wider trigger (any change.* regex) would fire on fewer letters
  and conflate magnitude/direction coverage; the magnitude-only trigger
  isolates the axis this probe is designed to measure.
- **13 no-match letters is a small n.** The precision drop (4 new false
  positives) is mechanistically clean but the absolute counts are small; the
  verdict (TRAILS) is robust to ±1-2 fp, but the exact −0.0203 magnitude delta
  should be read as a small-n measurement, not a precise effect size.

## What this is NOT

- Not a production change. Nothing is wired into `run_split`; the v08 artifact
  is untouched. The outcome closes the complement pathway as a negative.
- Not a re-run of the integration probe. The integration probe replaced the
  rules everywhere with a 5-label direction selector; this probe restricts a
  3-label magnitude selector to the no-match subset. Different question,
  contract, trigger, and result.
- Not a gold-schema change. Gold is frozen; the magnitude menu is a
  prediction-side contract; the cited `state_profile_magnitude` metric is
  unchanged.
- Not a direction-axis probe. The residual +0.0226 direction gap the
  deconflation probe isolated is out of scope; the complement asks a
  magnitude-only question on a magnitude-only menu.
- Not a claim that no LLM design could ever improve SF magnitude. It is a
  claim that *this* design (closed-option complement on the no-match subset,
  gpt-4.1-mini) does not, and that the selector's measured precision edge is
  a selection effect — the obvious exploitation does not work.

## Artifacts / Provenance

- Driver: `scripts/run_exectv2_sf_magnitude_complement.py` (13 gpt-4.1-mini
  calls, dev140, temp 0, cached, replay mode).
- Summary:
  `experiments/exectv2_sf_magnitude_complement_summary_20260708.json`
  (baseline + complement PRF1 on all four metrics; the in-run anchor
  reproduction; the complement subset count; the verdict band).
- Ledger: `experiments/exectv2_sf_magnitude_complement_ledger_20260708.jsonl`
  (one row per no-match mention the selector fired on: letter_id,
  prior_frequency_change, selected_candidate_id, selection_mode,
  assembled_magnitude, menu_labels).
- Predictions: `experiments/exectv2_sf_magnitude_complement_dev140_20260708.jsonl`
  (the overridden artifact, via `write_jsonl`).
- Key builders: `build_magnitude_menu`, `has_magnitude_regex_match`,
  `ClosedOptionMagnitudeSelector` + `ClosedOptionMagnitudeSelectorSignature`,
  `MAGNITUDE_VOCAB`, `MAGNITUDE_RULE_IDS`
  (`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/hybrid/closed_option_direction.py`,
  additive alongside the existing direction functions; `parse_selection` +
  `assemble_direction` reused unchanged).
- Tests: `tests/test_exectv2_sf_closed_option_hybrid_integration.py`
  (10 new tests in `TestBuildMagnitudeMenu` + `TestHasMagnitudeRegexMatch` +
  `TestMagnitudeAssembleReuse` classes; the file's total is now 28).
- Input artifact: `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl`
  (the same rules-arm artifact the deconflation probe reads).
- Prior art: `sf_direction_vocab_deconflation_2026-07-08` (registry entry 38,
  the decomposition that motivated this probe); `sf_closed_option_hybrid_integration_2026-07-06`
  (registry entry 35, the replay-mode template this driver mirrors).
- Split discipline: dev140 only; 13 LLM calls; no test59 / full-200 row
  inspection.
