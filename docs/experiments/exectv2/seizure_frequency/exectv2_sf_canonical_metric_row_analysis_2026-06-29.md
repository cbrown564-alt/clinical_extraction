# SF canonical metric row-analysis — every dev140 row, on exactly the metric we score, stage 1 vs stage 2

Date: 2026-06-29
Scope: **all 140 dev letters**, SeizureFrequency, scored on the **exact metric we evaluate on**
(`state_profile` — the direction-blind, type-agnostic per-letter *set* of
`frequency_state_faithful` states ∈ {active-rate, seizure-free, changed, unknown}). Captures and
projects **both** model stages: stage 1 = the first LLM (`generate`), stage 2 = the verifier
(`verify`). Every gold≠model row is adjudicated clinically and set in stone.

Supersedes the narrow `exectv2_sf_changed_class_row_analysis_2026-06-29.md` (changed-class only).
This is the canonical SF metric analysis: it answers "how often does the first LLM get it wrong",
"is gold always right or is the model sometimes right and scored wrong", and "what is the residual".

Canonical run: the **P2 gpt-4.1-mini two-stage program** (`exectv2_gepa_sf_verify_gpt41mini_20260628`,
evolved instructions, single model for both stages so the stage-1→stage-2 delta isolates the verify
step). Harness: `experiments/exectv2_sf_canonical_row_analysis.py` (re-runs both stages, projects each
through the metric, self-validates the decomposition == `score_frequency_state`). Adjudication:
`experiments/exectv2_sf_canonical_adjudication.py` (53 verdicts → `_sf_canonical/_adjudication.csv`).

---

## 0. TL;DR (the answers, set in stone)

1. **The first LLM (stage 1) gets the per-letter answer wrong ~50% of the time** (exact-match 49.3%,
   71/140; state_profile F1 0.710). The verifier cuts that to **37.9% wrong** (87/140 exact; F1 0.772).
   So the user's "~50% wrong" is precisely the **first LLM's** rate; the verifier helps.
2. **Gold is NOT always right.** Of the verifier's 53 metric-errors, only **15 (28%) are genuine model
   mistakes**. **22 (42%) are the model being clinically correct and scored wrong** because gold
   *under-annotated* the stated frequency (13) or *redundantly double-tagged* a type (9). **16 (30%)
   are genuine ambiguity** (IAA-0.47 coin-flips + gold temporal conventions).
3. **Counting only genuine model errors, the two-stage model is clinically defensible on 125/140 =
   89.3% of letters** — the metric reports 62.1%. The 27-point gap is gold noise, not model error.
4. **The metric itself is noisy.** A faithful re-run of the *same evolved program* scores **0.772**,
   not the logged **0.741**; **41/140 letters (29%) flip state-set across identical-instruction runs**
   from gpt-4.1-mini temp-0 nondeterminism alone. Part of "the wall" is ±0.03 measurement noise.
5. **The verifier is a net good but does real damage:** it fixes 14 letters and **breaks 7** (incl. 3
   where it *deleted a correct seizure-free* via over-zealous non-epileptic suppression).

The standing "we keep hitting a wall at ~0.74–0.78" is now fully explained: the model is already
~89% clinically right; the metric can't see it because **the gold it scores against is itself only
~0.47 self-consistent on this entity.** This is a gold/measurement ceiling, not a model ceiling.

---

## 1. The exact metric (no direction, by design)

`state_profile` (`scoring/seizure_frequency.py:105-146`, ADR 0037 = primary SF metric) is, per letter:
the deduplicated **set** of `frequency_state_faithful(attrs)` over SeizureFrequency entities, scored
by `multiset_prf1` and summed with `sum_prf1`. `frequency_state_faithful` (`:237-260`):

```
any count == 0            -> seizure-free
else any count present    -> active-rate
else FrequencyChange set  -> changed     (direction collapsed away)
else                      -> unknown
```

It is **type-agnostic** (ignores the seizure-type CUI) and **direction-blind** (Increased / Decreased /
Frequent / Infrequent / Same all collapse to the single token `changed`). This is deliberate: it scores
the clinical question "*which frequency states does this letter describe?*", not the annotation
schema's CUI-granularity or direction vocabulary. The prior report's whole subject (direction recovery)
is **not in this metric** — so it cannot be the cause of the plateau, and this analysis ignores it.

The per-letter decomposition in this report is **provably the metric**: the harness asserts the
summed per-letter tp/fp/fn equals `score_frequency_state(...).state_profile` exactly (`True`).

## 2. The metric is noisy — a re-run finding before any conclusion

The logged run is 0.7413. A faithful re-execution of the **same** evolved generate+verify instructions
(gpt-4.1-mini, temp 0, cache on) scores **0.7724**, and its per-letter state-set disagrees with the
logged jsonl on **41/140 letters (29%)**, in both directions (adds `changed`/`active-rate` on some,
removes on others; on several it matches gold where the logged run missed — EA0025, EA0128, EA0169,
EA0181). This is pure gpt-4.1-mini temp-0 nondeterminism (the original run's completions are not in the
local cache). The re-run is now cache-stable and reproducible (byte-identical `_index.json` on repeat),
so it is the fixed artifact for everything below — **but the headline is the noise itself:** at this
scale the SF state_profile carries **~±0.03 run-to-run variance**, so the 0.741 / 0.763 / 0.779 / 0.784
ladder the workstream has been climbing is partly inside the noise band. Any single-number SF
comparison without a re-run band is over-precise.

## 3. Stage 1 vs stage 2 — how often is each wrong (the central question)

| | state_profile F1 | P | R | per-letter EXACT | per-letter WRONG |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Stage 1 — first LLM (`generate`)** | **0.710** | 0.632 | 0.809 | 69/140 = 49.3% | **50.7%** |
| **Stage 2 — verifier (`verify`)** | **0.772** | 0.727 | 0.824 | 87/140 = 62.1% | **37.9%** |

The first LLM is wrong on **just over half** of letters; the verifier removes ~13 points of that,
almost entirely by **precision** (0.63→0.73 — it kills 22 spurious states) while nudging recall up.

**Verify effect, per letter:** fixed **14**, broke **7**, both-already-correct 57, both-still-wrong 41,
changed-but-equal-F1 21. Net **+7 letters / +0.063 F1**. The 7 it broke include **3 regressions where it
deleted a correct `seizure-free`** (EA0102, EA0120 → empty; EA0059 lost a `changed`) — its
non-epileptic/PNES and "current-only" suppression rules over-fire.

**Per-state confusion (stage 2):**

| state | tp | fp | fn | P | R | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 59 | 23 | 3 | 0.72 | 0.95 | 0.82 |
| seizure-free | 36 | 9 | 11 | 0.80 | 0.77 | 0.78 |
| changed | 17 | 10 | 10 | 0.63 | 0.63 | 0.63 |
| unknown | 0 | 0 | 0 | — | — | — |

`active-rate` recall is near-ceiling (0.95) but its precision (0.72) is the single biggest leak (23 FP);
`changed` is the weakest class (0.63/0.63); `unknown` is never emitted (the model always commits to a
state). §6 shows the active-rate FP are mostly **gold under-annotation, not model error.**

## 4. The dominant error mode: gold has NO SF, the model finds a real one

**22 of the 53 stage-2 errors are letters where gold annotates zero SeizureFrequency** but the model
emits one (19 spurious `active-rate`, plus `changed`/`seizure-free`). The reflex reading is "the model
hallucinates / over-emits." The evidence refutes it:

- **These letters carry a definite epilepsy diagnosis.** Of the 22, all but **EA0016** (a single first
  seizure) carry a **Certainty-5, Affirmed `Epilepsy` or `MultipleSeizures` Diagnosis** in gold. So the
  model's own "confirmed-diagnosis gate" (and the metric's
  `_epilepsy_dx_status`) **does not distinguish these from the gold-annotated letters** — the gate is
  aimed at the wrong thing.
- **The frequency is explicitly in the text.** EA0018 "episodes around twice a week", EA0043 "roughly
  every year since 15", EA0109 "2–3 times a week for the last 6 months", EA0146 "6 of these during the
  last year", EA0166 "still occurring around once a month", EA0021/EA0183 "occur 4 to 5 times a year".
  These are real, current, definite-epilepsy frequencies that gold simply did not tag.

So **12 of the 22 gold=[] over-emissions are gold under-annotation (the model is right)**; 5 are genuine
ambiguity (first-seizure-clinic / new-diagnosis establishing events: EA0045, EA0092, EA0116, EA0164,
EA0171); and only **5 are genuine model over-reads** (EA0014 a bare "continues to get seizures" stamped
`changed`; EA0016 a single first event; EA0141 a *lifetime* "at least three seizures" diagnostic count
read as a rate; EA0160 explicitly non-epileptic anxiety events; EA0200 two establishing GTCs at first
diagnosis). This is the IAA-0.47 floor showing up as **systematic gold gaps**, and it is the bulk of the
"precision problem."

## 5. The full per-row adjudication (all 53 metric-errors)

verdict: **G** = GOLD_RIGHT (genuine model error) · **M** = MODEL_DEFENSIBLE (model clinically
right, scored wrong: gold under-annotated or double-tagged) · **B** = BOTH_DEFENSIBLE (IAA ambiguity
or gold temporal convention). `gold / s1 / s2` are the projected state-sets. `‡` = verify regression.

| letter | gold | s1 (LLM-1) | s2 (verify) | V | what they differ on |
| --- | --- | --- | --- | :-: | --- |
| EA0005 | active-rate, seizure-free | active-rate, changed | active-rate | M | gold per-type tags GTC seizure-free; model has the 2/yr rate |
| EA0006 | active-rate | active-rate, seizure-free | seizure-free | B | gold tags "2 GTC in 2014" (historical-dated) active-rate; model tags current "seizure free" |
| EA0010 | seizure-free | active-rate | changed | G | no sz since teens, "stable" → gold free; model over-read "stable" as changed |
| EA0011 | active-rate, changed, seizure-free | active-rate | active-rate, seizure-free | M | gold double-tags FBTC free + changed/Infrequent; model has rate+free |
| EA0014 | (none) | changed | changed | G | "continues to get seizures" — no rate/direction; model stamped changed/increased |
| EA0016 | (none) | active-rate | active-rate | G | single first focal event; not a frequency |
| EA0018 | (none) | active-rate | active-rate | M | definite epilepsy; "twice a week" stated, gold annotated nothing |
| EA0021 | (none) | active-rate, changed | active-rate | M | CPS c5, abnormal EEG; "4–5 times a year", gold annotated nothing |
| EA0022 | changed, seizure-free | seizure-free | seizure-free | B | "completely under control" = gold changed/Infrequent+free; model free |
| EA0038 | active-rate | changed, seizure-free | changed, seizure-free | G | recent GTC = gold active-rate; model tagged the 3-yr-prior free period |
| EA0040 | (none) | active-rate | active-rate | M | symptomatic epilepsy c5, 2 AEDs; "3–4 further episodes" gold omitted |
| EA0043 | (none) | active-rate | active-rate | M | Epilepsy c5; "4 events… every year since 15" gold omitted |
| EA0045 | (none) | active-rate | active-rate | B | focal epilepsy c5 but day-dream events under characterisation |
| EA0046 | seizure-free | changed | active-rate | B | "FBTC last event Oct 2019" — gold seizure-free (last-event), model active-rate |
| EA0056 | active-rate, seizure-free | active-rate | active-rate | M | gold per-type free on the stopped 2ary-gen; model has the active rates |
| EA0059 | changed, seizure-free | changed, seizure-free | seizure-free | B‡ | "well controlled" = gold changed/Infrequent; **verify dropped** the stage-1 changed |
| EA0068 | changed, seizure-free | seizure-free | seizure-free | M | gold tags dx-header word "Infrequent focal seizures" as a changed state |
| EA0082 | active-rate, changed, seizure-free | active-rate, seizure-free | active-rate, seizure-free | M | gold double-tags absences rate(2-3/day)+Frequent; model has rate |
| EA0087 | active-rate, changed | +seizure-free | +seizure-free | G | having MORE GTCs; model over-read "up to five weeks seizure free" between events |
| EA0092 | (none) | changed | active-rate | B | genetic epilepsy c5; "cluster… controlled rapidly" — current but resolved |
| EA0096 | active-rate, changed | +seizure-free | +seizure-free | G | model tagged "I saw no overt seizures" (today's exam) as seizure-free |
| EA0102 | seizure-free | seizure-free | (none) | G‡ | gold free (5yr); **verify deleted** the correct stage-1 free (PNES suppression) |
| EA0104 | (none) | active-rate, seizure-free | changed, seizure-free | M | "smaller versions several times/week" current rate gold omitted |
| EA0106 | active-rate, changed, seizure-free | active-rate | active-rate | M | gold per-type rate+Frequent+free; model emitted the rate only |
| EA0108 | active-rate, changed | active-rate | active-rate | M | gold double-tags rate(2-3/mo)+Increased; model has rate |
| EA0109 | (none) | active-rate | active-rate | M | focal sz c5; "2–3/week for 6 months" rate+increase gold omitted both |
| EA0114 | (none) | active-rate | active-rate | M | focal epilepsy c5; "a couple of focal impaired awareness seizures" gold omitted |
| EA0116 | (none) | (none) | active-rate | B | Virtual First Seizure Clinic; "few episodes from sleep" establishing events |
| EA0120 | seizure-free | seizure-free | (none) | G‡ | gold free; **verify deleted** the correct stage-1 free |
| EA0121 | changed, seizure-free | active-rate | active-rate, changed | B | gold's odd seizure-free on a 2-3/mo type; model has frequent + the rate |
| EA0123 | active-rate, changed | +seizure-free | active-rate, seizure-free | B | gold rate+Decreased("reduced from once a year"); model rate + a historical 4-yr free |
| EA0135 | active-rate | +seizure-free | +seizure-free | G | "6 months without seizures" then a cluster; model tagged the superseded free period |
| EA0136 | changed, seizure-free | active-rate, seizure-free | active-rate, seizure-free | G | model tagged low-BP/syncope events active-rate; missed gold changed/Same |
| EA0137 | active-rate, seizure-free | active-rate | active-rate | M | gold per-type free + 2ary-gen rate(2/yr); model has the rate |
| EA0139 | active-rate | changed | changed | B | "further GTC since I last saw him" — no number/direction; gold rate vs model changed |
| EA0141 | (none) | active-rate | active-rate | G | "at least three seizures he has epilepsy" — lifetime diagnostic count, not a rate |
| EA0143 | seizure-free | active-rate, seizure-free | active-rate, seizure-free | G | "used to happen weekly" but last event >5yr ago; model tagged the historical rate |
| EA0146 | (none) | active-rate | active-rate | M | Epilepsy c5; "6 this year" + "few times every month" gold omitted |
| EA0151 | active-rate | active-rate | active-rate, changed | B | "cluster of 5… unusual as before well controlled" — defensible deterioration |
| EA0153 | (none) | active-rate | active-rate | M | focal epilepsy c5; "1–2 per month for 6 years" gold omitted (MRI/EEG pending) |
| EA0158 | active-rate | active-rate | active-rate, changed | G | two stable rates "continued ever since"; model over-called changed, no direction |
| EA0160 | (none) | seizure-free | seizure-free | G | events "probably anxiety… non-epileptic attacks"; model tagged free on functional |
| EA0162 | seizure-free | active-rate, seizure-free | active-rate, seizure-free | B | alcohol-provoked "cluster of three"; gold discounts as free, model active-rate |
| EA0164 | (none) | active-rate | active-rate | B | epilepsy unclassified (new dx); "5 episodes in last few months" establishing |
| EA0166 | (none) | active-rate | active-rate | M | JME c5; "still occurring around once a month" gold omitted |
| EA0171 | (none) | seizure-free | seizure-free | B | Epilepsy probable focal (new dx); "no further episodes since lamotrigine" gold omitted |
| EA0172 | (none) | active-rate | changed | M | refractory focal epilepsy c5; "ongoing seizures most days" gold omitted (vague) |
| EA0182 | seizure-free | active-rate | active-rate | B | probable TLE only; "single seizure 3 weeks ago" — gold last-event free, model rate |
| EA0183 | (none) | active-rate, changed | active-rate | M | epilepsy c5 (same text as EA0021); "4–5 times a year" gold omitted |
| EA0186 | active-rate, seizure-free | active-rate, changed | active-rate, changed | B | focal-motor "frequent before med, last event 10mo ago" — gold free, model changed |
| EA0197 | active-rate | active-rate, changed | active-rate, changed | M | "baseline 1-2/yr… worse, now 1-2/month" — explicit worsening; gold omitted the change |
| EA0198 | active-rate, changed | active-rate | active-rate | M | gold double-tags rate+Increased("this increase in seizures frequency"); model has rate |
| EA0200 | (none) | active-rate | active-rate | G | new GGE dx; "two events of LOC were GTC" — establishing events, not a treated rate |

## 6. The tally and the mechanism families

| verdict | n | share |
| --- | ---: | ---: |
| **MODEL_DEFENSIBLE** (model right, scored wrong) | **22** | **42%** |
| **BOTH_DEFENSIBLE** (genuine ambiguity / convention) | **16** | **30%** |
| **GOLD_RIGHT** (genuine model error) | **15** | **28%** |

Every error maps to exactly one mechanism family (all 53 accounted, no remainder):

| family | n | verdict | what it is |
| --- | ---: | :-: | --- |
| **Gold under-annotation** | 13 | M | the model retrieves a real, current frequency for definite epilepsy that gold left untagged |
| **Gold redundant multiplicity** | 9 | M | gold double-tags one type (numeric rate **and** a qualitative change, or a dx-header adjective); the model emits one fact, and the state-*set* then scores the other as missing |
| **Genuine IAA-0.47 ambiguity** | 10 | B | "well controlled"/"stable" = free or infrequent? a cluster = a rate or a deterioration? a provoked or first-presentation event = countable or not? — the calls two annotators split on |
| **Gold temporal/keying convention** | 6 | B | gold tags a historical dated count as active-rate, a "last event X ago" as seizure-free, an undirected recurrence as a rate — the model keys them the other way |
| **Genuine model over-read** | 13 | G | historical/superseded rates read as current; inter-event gaps and clinic-exam observations read as seizure-free; single/lifetime/non-epileptic events read as frequencies; undirected statements stamped `changed` |
| **Verify regression** | 2 | G | the verifier deleted a correct stage-1 `seizure-free` (EA0102, EA0120; EA0059 lost a changed) |

**The two metric-artefact families (gold under-annotation + redundant multiplicity = 22 letters, all
MODEL_DEFENSIBLE) are the single largest block — bigger than the genuine-model-error block (15).**

## 7. Is gold always right? — the answer, set in stone

**No.** On the 53 letters where the metric marks the model wrong:
- **28% (15) the model is genuinely wrong** — 13 over-reads + 2 verify regressions. These are the real,
  fixable model errors (mostly: historical/superseded rate vs current state, and clinic-observation or
  inter-event-gap mis-read as seizure freedom).
- **42% (22) the model is clinically right and gold is the problem** — gold either failed to annotate a
  stated frequency (13) or redundantly multi-tagged a type so the set-metric penalises a clean single
  fact (9).
- **30% (16) is a genuine coin-flip** — IAA-0.47 ambiguity (10) or a gold temporal-keying convention (6),
  where neither answer is "correct".

**Counting only genuine model errors, the two-stage model's per-letter answer is clinically defensible
on 125/140 = 89.3% of dev letters.** The metric reports 62.1%. The 27-point gap is the gold's own noise
— consistent with SeizureFrequency being the **2nd-worst-agreed entity in the corpus (human IAA F1 0.47)**.

(34 of the 53 errors fall in the optimizer-seen trainset and 19 in the held-out valset, so the dev140
headline is mildly optimistic, but the error *structure* is the same across both splits.)

## 8. What the residual genuinely is — and what it is not

- **It is not a recall problem.** Stage-2 recall is 0.82 (active-rate 0.95). The model retrieves the
  frequency statements; it over-emits (precision 0.73), and most of that "over-emission" is gold
  under-annotation, not noise.
- **It is not direction.** The metric collapses direction; the plateau exists with direction already
  discarded. (Direction is a separate, unscored axis — see the prior changed-class report — but it is
  **not** what caps `state_profile`.)
- **It is not feedback or determinism.** Phase 5 (feedback precision) and Phase 3b (deterministic
  projection) each bought ~+0.03–0.04, inside the **±0.03 run-to-run noise band** measured in §2.
- **It is ~⅔ a gold-quality ceiling.** 38/53 metric-errors are not model mistakes. A perfect clinical
  reader scores ~0.77–0.80 against *this* gold because the gold is ~0.47 self-consistent. The
  workstream's repeated "wall at ~0.74–0.78" is that ceiling.
- **The genuinely fixable ~28% (15 letters)** splits into two clean, learnable rules and decomposes the
  active-rate precision leak:
  1. **Temporal discipline** (7 letters: EA0038, EA0135, EA0143, EA0006, EA0182, EA0046, EA0123): a
     historical/superseded/last-event frequency is not the *current* state. This is exactly what the
     hybrid's deterministic `_last_event_duration` / change-reject rules encode (Phase 3b), and it is
     the dominant genuine error.
  2. **State-evidence discipline** (6 letters: EA0087, EA0096, EA0010, EA0158, EA0014, EA0160): a
     clinic-exam observation, an inter-event gap, a "stable"/"continues" phrase, or a non-epileptic
     event is not a `seizure-free`/`changed` state.
  3. **Verify regressions** (2): stop the verifier deleting a correct `seizure-free` on PNES/"current-only"
     grounds.

## 9. Corrections to prior conclusions

- **The narrow changed-class report (`exectv2_sf_changed_class_row_analysis`) over-stated genuine error
  at ~52%.** Across *all* states and *all* rows the genuine-model-error share is **28%**, because the
  dominant whole-corpus error (gold=[] over-emission) is mostly **gold under-annotation**, a category the
  changed-only slice never saw. The changed class is the *worst* slice (F1 0.63), not the representative
  one.
- **"SF is a representation/recall plateau" is half-right.** The half that is right: the gap to the
  hybrid is not feedback/determinism. The half that is wrong: it is not primarily *the model's*
  representation — it is **the gold's** (under-annotation + redundant multiplicity + IAA-0.47), which the
  type-agnostic state-set metric cannot launder away.
- **The "confirmed epilepsy diagnosis gate" is mis-targeted.** The gold=[] letters are overwhelmingly
  definite epilepsy, so gating SF on diagnosis certainty does not separate them from gold-annotated
  letters; it suppresses correct facts (the verify regressions) without fixing the real over-reads.

## 10. Recommendation

1. **Stop chasing the `state_profile` number with feedback/demo/determinism iterations** — the remaining
   headroom against this gold (~0.77–0.80) is inside the noise band and ~⅔ gold quality. Report SF with a
   **re-run ±0.03 band**, never a single decimal.
2. **The only attributable model lever left is the 15 genuine errors**, and it is small and rule-shaped:
   wire **temporal discipline** (historical/last-event ≠ current) + **state-evidence discipline**
   (exam/gap/"stable"/non-epileptic ≠ a state) + **stop the verify deletions**. That is the Phase-3b
   deterministic SF projection, already built — the LLM-only route will not out-learn it on these 7+6+2.
3. **The real headline for the thesis is the gold-quality finding, not another SF point:** under the
   metric we score, the two-stage LLM is already ~89% clinically defensible; the benchmark's ~0.77 SF
   ceiling is a property of a 0.47-IAA gold, not of the model. This belongs in the closing
   benchmark-vs-clinical-recovery reconciliation, not in another SF optimisation cycle.

## 11. Artifacts

- Harness (re-runs both stages, projects through the exact metric, self-validates ==
  `score_frequency_state`): `experiments/exectv2_sf_canonical_row_analysis.py`.
- Per-letter index + summary + per-letter substrate: `_sf_canonical/_index.json`,
  `_sf_canonical/_summary.json`, `_sf_canonical/<letter>.md`.
- The 53 clinical verdicts (computed tally, not hand-counted):
  `experiments/exectv2_sf_canonical_adjudication.py` → `_sf_canonical/_adjudication.csv`.
- Canonical run: `experiments/exectv2_gepa_sf_verify_gpt41mini_20260628.{jsonl,instruction.txt,json}`.
- Cross-check (adopted best, final-output only, no re-run): `reasoner_reasoner_ex` 0.784 state_profile
  (`exectv2_gepa_sf_verify_p5_reasoner_reasoner_ex_20260629.jsonl`).
- Supersedes (narrow, changed-only): `exectv2_sf_changed_class_row_analysis_2026-06-29.md`.
- Metric: `scoring/seizure_frequency.py` (`state_profile`, `frequency_state_faithful`); ADR 0037.
