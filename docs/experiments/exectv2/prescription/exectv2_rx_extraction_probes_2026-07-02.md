# ExECTv2 Prescription extraction-behavior probes (#2, #3)

Phase 2 of the pipeline assumption audit
(`docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md`). Two COSTED,
gated hand-tuned instruction probes on `openai/gpt-4.1-mini`, **dev140 only**.

- Driver: `experiments/exectv2_rx_extraction_probes_2026-07-02.py`
- Scorer (consumed, not modified): `score_prescription_components(...).clinical_headline`
  (finalized: clause-scope + valproate/brand lexicon fixes already landed).
- Canonical comparison run:
  `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`.

## Method

The canonical run is a per-family GEPA program. Each family's clinical_headline is
scored independently, so this probe reconstructs **only** the evolved Prescription
predictor (verbatim from the canonical `.instruction.txt`) and scores **only**
Prescription clinical_headline -- a faithful, 4x-cheaper subset. Arms are paired and
run under identical conditions (temp 0, LM cache OFF, 140 dev letters each), so a
probe delta is measured against a FRESH matched baseline, not the historical number.

Arms:
- `baseline` -- canonical evolved Rx instruction, unchanged (fresh live run).
- `probe2_current_vs_future` -- baseline + the #2 delta.
- `probe3_aed_only` -- baseline + the #3 delta.
- `probe23_combined` -- baseline + both deltas (cheap sanity arm).

The cached-canonical prediction set (the historical 0.9122) is also re-scored with
the current scorer as a **secondary reference** (validated: it reproduces 0.9122
exactly, tp=187 fp=17 fn=19).

## Predeclarations (written BEFORE running the live arms)

### Probe #2 -- `rx_current_vs_future_dose_conflation_2026-07-02`

Instruction delta (appended to the evolved Rx instruction): teach the extractor to
(a) assert the CURRENT regimen from the letter's current-medication list/header;
(b) never emit a proposed titration/target dose ("increase to ...", "so that he is
on X", "target dose", "titrate up to") as a current fact or let it overwrite the
current dose; (c) split a "morning + nocte" pair into two once-daily (freq 1) facts,
and treat a nocte/od dose as once-daily not twice-daily.

**Kill criterion.** Primary metric = net dev140 Prescription clinical_headline F1
vs the FRESH matched baseline. Mechanism check = EA0021's true current dose recovered
(the `('ordinary','sodium-valproate','800','mg','1')` FN) AND its future-target FP
(`...,'800','mg','2')`) removed.
- **CONFIRMED** iff net dF1 >= +0.004 AND the EA0021 mechanism is realized AND no net
  precision regression.
- **PARTIAL** iff the EA0021 mechanism is realized on the targeted letter but net dF1
  is within the noise band (|dF1| < 0.004) because collateral perturbation on other
  letters cancels it (works locally, no net metric win).
- **NULL** iff |dF1| < 0.004 AND the mechanism is not realized.
- **REFUTED** iff net dF1 <= -0.004 (net harm) or precision materially regresses.

### Probe #3 -- `rx_non_aed_over_extraction_2026-07-02`

Instruction delta: emit prescription facts ONLY for anti-epileptic drugs; explicitly
exclude comorbidity meds (clopidogrel, aspirin, ramipril, amlodipine, statins,
metformin, warfarin, thyroxine, ...) even when a current dose+frequency are stated.

**Kill criterion.** Primary metric = net dev140 Prescription clinical_headline F1 vs
the fresh matched baseline. Mechanism check = the non-AED FPs (EA0073 clopidogrel
and any similar) removed.
- **CONFIRMED** iff net dF1 >= +0.004 AND non-AED FPs removed AND no net recall
  regression.
- **PARTIAL** iff non-AED FPs are removed but net dF1 is within the noise band.
- **NULL** iff |dF1| < 0.004 AND no non-AED FP was removed.
- **REFUTED** iff net dF1 <= -0.004 or recall materially regresses.

Noise context: the fresh-baseline-vs-cached-canonical F1 gap is reported as the
empirical run-to-run noise floor; an effect inside that floor cannot be CONFIRMED.

## Results

Live run 2026-07-02, `openai/gpt-4.1-mini`, temp 0, cache OFF, 140 dev letters/arm
(560 extraction calls total). All arms scored with the finalized
`score_prescription_components(...).clinical_headline`.

| Arm | P | R | F1 | tp | fp | fn | dF1 vs fresh baseline | letters changed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cached-canonical reference (0.9122) | 0.9167 | 0.9078 | **0.9122** | 187 | 17 | 19 | (secondary ref) | -- |
| `baseline` (fresh matched) | 0.9118 | 0.9029 | **0.9073** | 186 | 18 | 20 | -- | -- |
| `probe2_current_vs_future` | 0.9372 | 0.9417 | **0.9395** | 194 | 13 | 12 | **+0.0322** | 11 |
| `probe3_aed_only` | 0.9639 | 0.9078 | **0.9350** | 187 | 7 | 19 | **+0.0277** | 14 |
| `probe23_combined` | 0.9795 | 0.9272 | **0.9526** | 191 | 4 | 15 | **+0.0453** | 16 |

**Noise floor.** Fresh baseline (0.9073) minus cached canonical (0.9122) = -0.0049.
This is the empirical run-to-run variance of gpt-4.1-mini at temp 0 on this surface
(1 fewer tp, 1 more fp, 1 more fn). Both probe effects are 6-7x this floor and their
metric *signature* matches their mechanism (probe #2 is recall-driven, probe #3 is
precision-driven), so the aggregate effects are robustly attributable even though
individual borderline letters also drift with run-to-run noise.

### Probe #2 verdict: CONFIRMED

Net dF1 = **+0.0322** (>> +0.004), recall-driven (tp 186->194, fn 20->12), fp also
down 18->13. Mechanism realized on the marquee letters:

- **EA0021** (the predeclared case): baseline emitted `sodium-valproate 800mg x2`
  (the future-target `800mg bd` conflated as current). Arm corrected it to
  `sodium-valproate 800mg x1` (the true current `800mg nocte`, once-daily). Exactly
  the predeclared mechanism -- future-target FP removed, true current dose recovered.
- **EA0038**: baseline dropped all three current carbamazepine doses
  (`400mg/400mg/200mg`, the documented omission); the "assert the letter's current
  medication list" framing recovered all three (+3 tp).
- Several letters (EA0078/EA0114/EA0148/EA0153) shed a spurious future-target fact.
- One collateral cost: **EA0152** -- the "split morning+night into separate facts"
  rule mis-fired on a dose *range* (`clobazam 10-20mg` -> two facts `10mg`+`20mg`),
  +1 fp. Net across the 11 changed letters is strongly positive (+8 tp, -5 fp, -8 fn).

### Probe #3 verdict: CONFIRMED

Net dF1 = **+0.0277** (>> +0.004), precision-driven (fp 18->7; precision 0.912->0.964);
recall ~flat. Mechanism realized:

- **EA0073** (the predeclared case): baseline emitted clopidogrel + metformin +
  ramipril (3 non-AED FPs, gold=[]); arm emits [] -- all three comorbidity meds
  removed.
- **EA0133**: baseline emitted clopidogrel + ramipril + simvastatin alongside the two
  real AEDs; arm removed all three non-AEDs and kept both AEDs.
- ~11 non-AED FPs removed across EA0073/EA0133/EA0120/EA0135/EA0152/EA0153.

**Honest cost (recorded, not spun).** The AED-only framing is not free: it dropped
genuinely-prescribed AEDs on **EA0025** (lamotrigine x2, both in gold and both AEDs)
and **EA0012** (carbamazepine 600mg, in gold), and added one spurious AED on EA0132
(eslicarbazepine). These drops are collateral behavior-shift, not misclassification
(all three drugs are on the delta's own AED whitelist). Net recall stayed flat
(tp 186->187) only because these AED losses were offset by AED recoveries elsewhere
that are partly run-to-run variance. The reliably mechanism-attributable effect of
probe #3 is the **precision** gain from non-AED removal; the recall side is noisy.
The probe is still CONFIRMED (net dF1 well above floor, non-AED FPs removed, no net
recall regression), but a production version should scope the AED gate more tightly
to avoid the borderline AED drops.

### Combined arm

Stacking both deltas reaches **0.9526** (dF1 +0.0453; fp down to 4, tp 191): the two
effects are largely orthogonal (precision from #3, recall from #2) and compose.

### Interpretation

Both #2 and #3 are genuine, mechanism-confirmed **model-weakness** fixes (route 2 in
the audit taxonomy), addressing the Prescription family's documented genuine-model-
error cases (EA0021 current-vs-future, EA0073 non-AED over-extraction). They are
hand-tuned instruction deltas measured on dev140; they are NOT a shipped prompt and
have NOT been evaluated on test/holdout. A production adoption would fold these deltas
into the canonical per-family Rx instruction and re-run the full 4-family program, and
should tighten probe #3's AED gate against the EA0025/EA0012 borderline drops.

## Prediction artifacts (for registration by the owner)

Written under `experiments/exectv2_rx_extraction_probes_2026-07-02/`:
`raw_baseline.json`, `raw_probe2_current_vs_future.json`, `raw_probe3_aed_only.json`,
`raw_probe23_combined.json` (per-letter model output), and `results.json` (scores +
per-letter diffs). Proposed run ids: `exectv2_rx_probe_baseline_gpt41mini_20260702`,
`exectv2_rx_probe2_current_vs_future_gpt41mini_20260702`,
`exectv2_rx_probe3_aed_only_gpt41mini_20260702`,
`exectv2_rx_probe23_combined_gpt41mini_20260702` (dev split, clinical_headline only).

