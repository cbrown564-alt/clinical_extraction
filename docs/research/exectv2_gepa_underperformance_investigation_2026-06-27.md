# ExECTv2 GEPA under-performance — structural investigation (2026-06-27)

Status: **H1 CONFIRMED (2026-06-27).** The flat result was the harness (uninformative
feedback), not a task ceiling. Enriching the metric's reflection feedback with concrete
per-family gold-vs-pred diffs jumped the mini monolith from **0.628 → 0.702** dev140
clinical_headline — autonomously matching the hand-tuned 0.710 from a 121-token seed.
Both gap families improved (Dx 0.46→0.57, SF 0.54→0.60; Inv 0.79→0.86; precision
0.56→0.75). H2–H5 remain open for the push toward the 0.9155 hybrid. Details below.

## H1 RESULT (confirmed)

| Config (dev140) | overall | Dx | SF | Rx | Inv | precision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pre-H1 GEPA monolith | 0.628 | 0.46 | 0.54 | 0.82 | 0.79 | ~0.56 |
| **H1 diff-feedback (mini)** | **0.702** | **0.57** | **0.60** | **0.84** | **0.86** | **0.75** |
| hand-tuned single prompt | 0.710 | 0.67 | 0.56 | 0.81 | 0.83 | — |
| v08 hybrid | 0.9155 | 0.91 | 0.91 | 0.94 | 0.91 | — |

Mechanism verified: the evolved 576-token instruction now encodes the exact conventions
the diffs exposed — "short canonical concepts (hyphenated, lowercase)", "Diagnosis = only
epileptic seizure types/syndromes, NOT comorbidities", explicit SF state rules — i.e. GEPA
auto-derived the hand-tuned prompt's rules from the diff signal. The precision jump
(0.56→0.75) is the "WRONG you emitted" signal teaching it to stop over-emitting.
Run: `exectv2_gepa_dedup_gpt41mini_h1diff_20260627`; metric change in `gepa/metric.py`
(`_family_diffs` / `_diff_lines`). Original investigation (now resolved for H1) follows.

---

Status (original): **investigation opened; hypotheses to test on return.**

## Why this report exists

GEPA-from-scratch on the ExECTv2 de-dup `clinical_headline` surface produced a flat,
implausible result: every arm landed ~0.63 dev140, **barely above the untuned 121-token
seed (0.619)**, and a per-family multi-signature decomposition did not move it (0.631).
A correctly-wired GEPA reliably yields material gains; a run that does not beat its own
seed is a signal that **the optimization harness — not the task — is the bottleneck**.
This report records what the failure is *not*, the evidence, and a ranked, falsifiable
set of hypotheses for the real cause.

Companion results doc:
`experiments/gepa_overnight_exectv2/GEPA_FROM_SCRATCH_EXECTV2_SYNTHESIS_2026-06-27.md`.
Code under `src/.../epilepsy_phenotyping/exectv2/gepa/`.

## Baseline numbers (dev140 clinical_headline)

| Config | overall | Dx | SF | Rx | Inv |
| --- | ---: | ---: | ---: | ---: | ---: |
| untuned lean seed (121 tok) | 0.619 | 0.45 | 0.55 | 0.76 | 0.78 |
| GEPA monolith (mini) | 0.628 | 0.46 | 0.54 | 0.82 | 0.79 |
| GEPA monolith (deepseek-reasoner) | 0.636 | 0.44 | 0.52 | 0.89 | 0.83 |
| GEPA monolith (mini, no length penalty) | 0.636 | 0.45 | 0.57 | 0.84 | 0.78 |
| GEPA multi-family per-predictor (mini) | 0.631 | 0.43 | 0.52 | 0.89 | 0.80 |
| hand-tuned single prompt (plan 13) | 0.710 | 0.67 | 0.56 | 0.81 | 0.83 |
| v08 hybrid (multi-stage) | 0.9155 | 0.91 | 0.91 | 0.94 | 0.91 |

GEPA's net gain over the seed is **+0.009 to +0.017** — within noise.

## What the failure is NOT (ruled out by cheap diagnostics)

All from read-only analysis of the saved eval JSONL + the scorers (no new LLM calls).

1. **Not a degenerate / no-gradient metric.** 126/140 letters score a *partial* per-letter
   F1 (not 0 or 1); the objective is continuous, not a coarse 0/1 cliff.
2. **Not the per-letter-vs-micro aggregation mismatch.** GEPA optimizes mean-per-letter
   F1 (0.616) which tracks the reported micro F1 (0.628) to within 0.012. Minor.
3. **Not a lack of exploration / cache collapse.** Monolith vs multi-family final
   predictions share only **Jaccard 0.675** — different evolved instructions genuinely
   produce ~32% different `(letter, entity, text)` facts. GEPA *is* moving; it just
   isn't moving *uphill*.
4. **Not scorer over-strictness on Diagnosis.** Lenient source-near phrase-overlap Dx
   F1 = 0.420, identical to the strict concept_negation F1 — Dx loss is not a
   matching-convention artifact at the scorer; the predicted Dx facts don't overlap
   gold even loosely.
5. **Not a representation cap for Dx/Rx/Inv.** "Perfect-input" oracle (gold-derived
   facts through the real parse→adapter→scorer, evidence gate bypassed) recovers
   **Diagnosis 1.0, Prescription 1.0, Investigations 1.0**. The pipeline *can* score a
   perfect Diagnosis — yet GEPA leaves production Dx at 0.43.

**Synthesis of the above:** the harness gives a continuous gradient, GEPA explores a
wide instruction space, and the pipeline can represent the perfect answer for 3 of 4
families — but GEPA still cannot climb. That pattern points squarely at the
**optimization signal** (what the metric tells the reflection LM, and how reliably the
valset selects winners), not at a task or representation ceiling.

## Defects surfaced (need fixing regardless)

- **D1 — SeizureFrequency round-trip scores 0.0 on the perfect-input oracle** (Dx/Rx/Inv
  were 1.0). The gold→`clinical_facts_from_mentions`→adapter→scorer path mis-derives SF
  state, so even a perfect SF answer fails to match. Production SF is ~0.52 (not 0), so
  part of this is the *replay helper* `clinical_facts_from_mentions` specifically; but it
  proves the SF state representation is fragile and the achievable SF ceiling through
  this pipeline is unverified.
- **D2 — evidence gate is unquantified and possibly over-aggressive.** In production it
  drops ~8.5% of emitted facts (884/966 scored). The oracle drop looked like 69% only
  because gold annotation `text` is hyphenated (not an exact substring) — a test
  artifact — but the gate's per-family/per-reason drop profile has never been measured.

## Ranked hypotheses to test (on return)

### H1 (PRIMARY) — The feedback metric is uninformative for reflection
GEPA's entire advantage is the reflective LM reading *what went wrong* and proposing a
targeted instruction edit. The current `metric._feedback` emits only per-family F1
numbers plus generic, static hints ("Diagnosis is a gap family: enumerate every distinct
diagnosis"). **It never shows the reflection LM the specific gold facts that were missed,
the spurious facts emitted, or the expected canonical form.** So for Diagnosis — where
representation is provably fine (oracle 1.0) but production is 0.43 — the reflector cannot
learn that gold wants `"epilepsy"` rather than the model's `"focal epilepsy - probable
temporal"`; it can only add more generic exhortation, which is exactly what the 829-token
evolved Dx instruction contains. This is the most likely single cause and the highest-
leverage fix.
- **Test:** enrich feedback to include, per failing letter, the concrete diff — missed
  gold facts (entity + canonical text), spurious predicted facts, and granularity
  mismatches — then re-run mini monolith at the same budget. **Expected if true:** a
  material jump (esp. Diagnosis) within the first few GEPA iterations.
- **Also:** read the GEPA reflection traces in `experiments/gepa_overnight_exectv2/<run>/`
  (gepa_state.bin / logs) to confirm proposals are generic and untargeted.

### H2 — Selection signal is too noisy: small valset + tiny minibatch
Valset is 50 letters; `reflection_minibatch_size=3`. Real improvements here are ~+0.01–0.03;
if the valset's candidate-to-candidate score noise exceeds that, GEPA's accept/reject
random-walks and the seed survives. The run showed candidate valset scores fluctuating
~0.52–0.59.
- **Test:** measure valset score variance across candidates; raise minibatch to 6–8; try
  multiple GEPA seeds; (dev is only 140 so valset can't grow much without shrinking
  trainset — consider k-fold or a stability analysis instead).

### H3 — temp=0 + cache gives the reflector no behavioral diversity
Task model runs at temperature 0 with cache on, so each instruction yields exactly one
deterministic output. GEPA sees a single point per candidate; the reflector cannot
observe the variance that reveals *why* a rule helps or hurts.
- **Test:** run the optimization phase with task temperature ~0.7 (and cache off for the
  task LM) so each candidate is sampled; keep final eval at temp 0.

### H4 — SeizureFrequency representation is broken (D1) and silently caps the objective
If the SF clinical_fact → headline-key path cannot match gold even on perfect input, then
~25% of the headline is unreachable and GEPA's SF gradient is misleading.
- **Test:** unit-test the SF state round-trip (`_seizure_state_attributes` ↔
  `_fact_state_from_seizure_attrs` ↔ `frequency_state_keys('clinical_headline')`); build a
  clean SF oracle using model-style SF facts (not the replay helper); fix until a perfect
  SF answer scores ~1.0.

### H5 — Benchmark-convention coupling distorts what the model is optimizing toward
The gold Diagnosis uses canonical `CUIPhrase` + concept normalization + in-sample CUI
projection. The free-text model emits clinically-correct but non-canonical concepts. The
*scorer* forgives this loosely (H... actually not — source-near = strict = 0.42), so the
gap is real recall/precision, but the model is never told the target convention/granularity
(ties back to H1). The evidence gate (D2) adds another convention coupling.
- **Test:** instrument evidence-gate drops by family and reason; quantify the achievable
  ceiling with proper-substring gold evidence; consider an auxiliary
  convention-robust scoring surface for the optimization signal while still reporting
  canonical headline.

### H6 — GEPA budget/acceptance mechanics
Confirm GEPA actually proposed and *accepted* enough mutations and that the returned
program is the valset-best. Logs show ~24 candidates and a best-on-valset ≈ seed, which is
consistent with H1/H2 (it tried, nothing beat the seed on the noisy valset) — but verify
there is no early-stop or acceptance bug.
- **Test:** dump the GEPA candidate→valset-score trajectory; confirm monotone best-so-far
  and that `optimized` is the argmax.

### H7 (kept, downgraded) — a genuine partial single-prompt ceiling
Still possible that a single prompt truly cannot reach the hybrid. But the **same base LLM
inside the multi-stage hybrid reaches 0.91**, so the capability exists; this hypothesis is
now secondary to the signal/feedback hypotheses above and should only be credited after
H1–H4 are addressed.

## Recommended order of attack

1. **H1** (enrich reflective feedback with concrete gold-vs-pred diffs) — highest leverage,
   directly explains exploration-without-climbing.
2. **H4 + D1** (fix/verify SF representation) — unblocks ~25% of the headline.
3. **H2/H3** (selection noise + sampling diversity) — make the optimizer able to detect the
   gains H1 unlocks.
4. **D2/H5** (instrument the evidence gate and convention coupling).
5. Re-run mini monolith at medium budget; **success = a clear jump above the 0.71 hand-tuned
   plateau**, concentrated in Diagnosis, confirming the ceiling was the harness not the task.

## Appendix — diagnostic evidence (dev140, no new LLM calls)

```
per-letter F1 distribution (monolith): 4 letters=0.0, 10=1.0, 126 partial   (gradient exists)
mean-per-letter F1 0.616  vs  micro F1 0.628                                 (aggregation: minor)
Diagnosis strict concept_negation F1 0.420  ==  source-near overlap F1 0.420 (not scorer strictness)
monolith vs multi-family predicted-fact Jaccard 0.675                        (instructions change behaviour)
perfect-input oracle, UNGATED: overall 0.786  (Dx 1.0, Rx 1.0, Inv 1.0, SF 0.0)   <-- SF round-trip defect (D1)
perfect-input oracle, GATED:   overall 0.403, 69% facts dropped              (inflated: hyphenated gold evidence; real drop ~8.5%)
```

Reproduce: the ad-hoc diagnostics live in this session's transcript; fold them into a
committed `experiments/exectv2_gepa_diagnostics.py` when the investigation resumes.
