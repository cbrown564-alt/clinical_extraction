# ExECTv2 SF Verify Error Analysis — Why the Verifier Plateaus at ~0.74 state_profile

Date: 2026-06-29
Scope: SeizureFrequency GEPA verify programs on dev140.
Runs analyzed: `exectv2_gepa_sf_verify_gpt41mini_20260628` (P2, best: state_profile 0.741,
clinical_headline 0.597) and `exectv2_gepa_sf_verify_v2_deepseekchat_20260629` (Phase 4,
state_profile 0.702, clinical_headline 0.534).
Diagnostic: `experiments/exectv2_sf_verify_error_analysis.py` (reproducible, zero-LLM).

## 1. Question

The SF verify programs — two-stage recall-additive generate→verify, GEPA-optimized on
state_profile — plateau at ~0.74 state_profile F1, ~0.19 below the hybrid's 0.930. The
plan's Phase 4 attributed this to "curated convention GEPA can't learn." Phase 3b refuted
that for the deterministic rules (the rules existed and lifted SF 0.710 → 0.779 when wired in),
but the LLM-only verify performance itself was never decomposed. This report does that:
a full per-letter, per-state error analysis of the best SF verify run, with root-cause
diagnosis for each error category.

## 2. Per-state breakdown (state_profile, per-letter presence)

The 4-way state_profile scores per-letter presence: for each letter, does the system
predict state X? Does gold have state X? (See ADR 0037 — state_profile is now the primary
SF metric.)

| state | TP | FP | FN | P | R | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| seizure-free | 39 | 12 | 8 | 0.76 | 0.83 | **0.796** |
| active-rate | 54 | 17 | 8 | 0.76 | 0.87 | **0.812** |
| changed | 13 | 15 | 14 | 0.46 | 0.48 | **0.473** |
| unknown | 0 | 0 | 0 | — | — | — |

Seizure-free and active-rate are already at ~0.80 F1 — respectable single-model numbers. The
**changed class at 0.473 F1** is the specific cell dragging the aggregate from ~0.93 (hybrid)
to 0.741. The `unknown` state is absent from both gold and predictions in the verify program
(the verifier's schema steers toward concrete kinds, and gold rarely tags unknown when a rate
or change is present).

## 3. The 74 errors decompose into four root causes

| Category | Errors | Root cause | Fixability |
| --- | ---: | --- | --- |
| A. Per-type multiplicity failure | 28% (21) | Model emits one state per type; gold multi-tags | Hard — convention fights consolidation instinct |
| B. Over-emission on non-epileptic/unconfirmed | 31% (23) | Model ignores confirmed-diagnosis gate | Medium — instruction-following failure |
| C. Temporal confusion (rate ↔ free) | 20% (15) | Historical vs current state confusion | Mixed — some gold convention issues |
| D. Pure retrieval failures | 11% (8) | Empty predictions on letters with gold SF | Medium — generation failure |
| Overlap / other | 10% (7) | Cross-category | — |

### 3a. Per-type multiplicity failure — 21 errors

**14 FN_changed** (gold has changed, model misses it) + **7 FP_changed_gold_has_active_rate**
(model emits changed, gold only has active-rate).

This is the single biggest and deepest category. Gold tags BOTH a numeric rate AND a
qualitative descriptor for the same seizure type as separate facts. The model emits one and
stops.

**EA0108** — letter: *"his epilepsy was well controlled until last December when he had a
seizure… Currently his seizures occur 2 to 3 times per month."*
- Gold: active-rate (N=1, 2-3/month) **+** changed (FC=Increased — the worsening from
  well-controlled)
- Pred: active-rate only. The model saw the rate and consolidated; it did not also emit
  the directional change.

**EA0011** — letter: *"infrequent focal to bilateral convulsive seizures having around two
in the year."*
- Gold: active-rate + changed (FC=Infrequent)
- Pred: active-rate + seizure-free. Missed "infrequent" as a separate qualitative fact.

**EA0007** — letter: *"her epilepsy is the best it's ever been. She has seizures every 3 to
4 weeks."*
- Gold: active-rate only (the rate is the dominant signal; gold does not also tag a change)
- Pred: active-rate **+** changed (FC=Same — the model read "the best it's ever been" as a
  stability/change statement)
- All 7 FP_changed_gold_has_active_rate cases have **FC=Same**. The model emits "Same"
  (stable/unchanged) as a changed fact, but gold does not want a separate changed fact when
  a rate is already present.

**Root cause diagnosis.** The evolved instruction says "list the same seizure type more
than once when the letter gives it more than one distinct statement" but provides no concrete
example of rate+qualitative = two facts. The model's consolidation instinct overrides the
abstract instruction. This is **partially a wrong instruction** (needs concrete multiplicity
examples) and **partially a genuinely complex decision**: the convention that FC=Infrequent
is a separate fact from "2 per year" but FC=Same is NOT a separate fact from "every 3 weeks"
is genuinely ambiguous — it requires understanding that a qualitative descriptor adds
information beyond a rate, while a stability statement does not.

### 3b. Over-emission on non-epileptic/unconfirmed — 23 errors

**17 FP_active_rate** + **6 FP_changed_gold_has_no_sf**.

The model emits SF facts on letters where gold has none — typically dissociative seizures,
suspected epilepsy, or unconfirmed events.

**EA0057** — diagnosis: *"Dissociative seizures (non-epileptic attacks)"* + structural
epilepsy. Letter says focal motor seizures stopped 2 years ago.
- Pred: "dissociative seizures" N=1 → active-rate
- Gold: no SF for dissociative events (non-epileptic)

**EA0018** — letter mentions *"episodes around twice a week of an unusual thought."*
- Pred: active-rate
- Gold: no SF (not clearly epileptic)

**EA0141, EA0148** — gold has no SF at all; model emitted active-rate. These are likely
suspected/possible epilepsy cases where the annotator did not tag seizure frequency.

**Root cause diagnosis.** The evolved P2 verify instruction (rule 1) explicitly says *"Only
epileptic seizures with a confirmed diagnosis. A tentative or suspected diagnosis does not
count."* **The instruction is correct; the model is performing it badly.** gpt-4.1-mini does
not reliably distinguish confirmed from suspected epilepsy, and emits on any seizure-adjacent
mention. This is a pure instruction-following failure.

### 3c. Temporal confusion (active-rate ↔ seizure-free) — 15 errors

**12 FP_seizure_free** + **3 of the 8 FN_active_rate** (the remainder of FN_active_rate is
consolidation, not temporal confusion).

The model confuses historical and current states, or seizure-free for one type vs overall.

**EA0006** — letter: *"2 generalised tonic clonic seizures 2014"* and *"he remains seizure
free and is now driving."*
- Gold: active-rate (N=2 — the 2014 seizures are tagged as a count)
- Pred: seizure-free (N=0 — the model read "remains seizure free" as current status)
- The model's reading is clinically more defensible (the patient IS currently seizure-free),
  but gold tags the historical count as active-rate.

**EA0019** — gold: active-rate (N=1). Pred: seizure-free (N=0). Same pattern: the letter
mentions both historical events and current seizure-free status; model picks seizure-free,
gold wants the rate.

**Root cause diagnosis.** **Mixed.** Some are instruction-following failures (the instruction
says "current frequency only" but the model emits historical seizure-free as current). Some
are **gold annotation convention issues** — EA0006 tagging 2014 events as active-rate is
clinically debatable, and the model's seizure-free call is arguably more correct.

### 3d. Pure retrieval failures — 8 errors

The model emitted **nothing** on letters where gold has SF facts.

**EA0025** — letter: *"3-4 generalised tonic chronic seizures per week from May to August.
She also had very frequent myoclonic jerks."*
- Gold: active-rate + changed (FC=Frequent for myoclonic jerks)
- Pred: **empty** — zero SF facts emitted.

**EA0102, EA0120, EA0117, EA0182** — same pattern: gold has SF, model emitted zero.

**Root cause diagnosis.** These are **generation failures**, not keying errors. The model
failed to extract anything from these letters. Possible causes: prompt-length/attention
saturation, or the letter structure not triggering the generation pathway. A reasoning model
(deepseek-reasoner) with explicit chain-of-thought would likely not produce empty output.

## 4. The best evolved prompt — what it instructs

### P2 mini verify instruction (best performer, 0.741 state_profile)

Seven rules evolved by GEPA:

1. **Confirmed-diagnosis-only**: "Only epileptic seizures with a confirmed diagnosis of
   epilepsy. A tentative or suspected diagnosis does not count." (Targets Category B.)
2. **Current-frequency-only**: "Extract statements that describe the current seizure frequency
   at the time of the clinic visit. Do not include historical frequency rates." (Targets
   Category C.)
3. **Strict kind classification**: "frequency_rate: only when the letter gives a specific
   numeric frequency. changed: when the letter explicitly states an increase or decrease
   without a specific numeric rate. Vague qualitative descriptors ('most days', 'often',
   'frequently') do not qualify as frequency_rate." (Targets precision on active-rate.)
4. Exact-substring evidence.
5. Seizure-type naming.
6. Draft handling: keep supported, remove unsupported (non-epileptic, historical, vague),
   add missing.
7. JSON output format.

**What's missing:** No rule or example for per-type multiplicity (Category A). The instruction
says "list more than once" in the generate stage but the verify stage does not enforce it with
a concrete example. No rule disambiguates FC=Same (stability) from genuine change.

### v2 DeepSeek generate instruction (Phase 4, 0.702 state_profile)

The generate instruction evolved heavily (45 lines vs the P2 seed's 5) with detailed
definitions, worked examples, and explicit "do NOT" lists. But the verify instruction stayed
short (4 sentences). The DeepSeek run's generate instruction is more detailed than mini's,
yet it performed **worse** — consistent with the H-model-refuted finding that DeepSeek-chat is
a worse keyer.

## 5. Diagnosis — wrong instructions, bad model performance, or complex decision?

All three, weighted differently by category:

| Category | Wrong instructions? | Model performing badly? | Genuinely complex? |
| --- | --- | --- | --- |
| A. Per-type multiplicity (21) | **Partially** — no concrete rate+qualitative example | No — model follows its (consolidating) instinct | **Yes** — FC=Infrequent is separate from rate, FC=Same is not |
| B. Non-epileptic over-emission (23) | No — instruction is correct | **Yes** — confirmed-diagnosis gate not followed | No |
| C. Temporal confusion (15) | No — instruction says "current only" | **Partially** — historical vs current not distinguished | **Partially** — some gold conventions are debatable |
| D. Empty predictions (8) | No | **Yes** — generation failure | No |

The **dominant finding** is that the biggest error category (A, 28%) is a benchmark convention
mismatch (per-type multiplicity) that the instructions address abstractly but the model's
consolidation instinct overrides. This is not fixable by instruction tuning alone — it needs
either concrete few-shot examples of the rate+qualitative=two-facts pattern, or a reasoning
model that can explicitly enumerate per-type states.

The second-biggest category (B, 31%) is a pure instruction-following failure on the
confirmed-diagnosis gate. gpt-4.1-mini does not reliably distinguish confirmed from suspected
epilepsy. This is fixable with better instruction enforcement or a deterministic
confirmed-diagnosis pre-filter.

## 6. Implications for the next runs

The error decomposition directly informs the planned deepseek-reasoner + gpt-4.1-mini SF
verify runs (state_profile objective, per ADR 0037):

- **deepseek-reasoner** should help with:
  - Category A (chain-of-thought can explicitly enumerate "for each seizure type: is there a
    rate? Is there ALSO a qualitative descriptor?")
  - Category C (better temporal reasoning)
  - Category D (reasoning models rarely produce empty output)
- **gpt-4.1-mini** should help with:
  - Category B (better instruction-following for the confirmed-diagnosis gate — it already
    scored 0.741 vs DeepSeek-chat's 0.702)
- **state_profile as the optimization objective** (ADR 0037) will let GEPA see the changed-class
  errors directly in the feedback, instead of them being invisible on clinical_headline.
  This alone may improve Category A, since the prior runs optimized partly against a metric
  that was blind to changed-class TPs.

## 7. Artifacts

- Error analysis script: `experiments/exectv2_sf_verify_error_analysis.py`
- Analyzed runs:
  - `experiments/exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl` (P2 mini, best)
  - `experiments/exectv2_gepa_sf_verify_gpt41mini_20260628.instruction.txt` (evolved prompt)
  - `experiments/exectv2_gepa_sf_verify_v2_deepseekchat_20260629.jsonl` (Phase 4)
  - `experiments/exectv2_gepa_sf_verify_v2_deepseekchat_20260629.instruction.txt` (evolved prompt)
- Plan context: `docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` §6c (Phase 3b)
- Metric decision: `docs/decisions/0037-sf-state-profile-is-primary-clinical-metric.md`
