# ExECTv2 GEPA under-performance — structural investigation (2026-06-27)

Status: **H1 CONFIRMED + H4 REFUTED / D1 RESOLVED (2026-06-27).** The flat result was the
harness (uninformative feedback), not a task ceiling. Enriching the metric's reflection
feedback with concrete per-family gold-vs-pred diffs jumped the mini monolith from
**0.628 → 0.702** dev140 clinical_headline — autonomously matching the hand-tuned 0.710
from a 121-token seed. Both gap families improved (Dx 0.46→0.57, SF 0.54→0.60; Inv
0.79→0.86; precision 0.56→0.75). **H4 is now refuted**: a perfect *model-style* SF answer
scores **F1=0.979** through the production path, so SF is NOT representation-capped — its
~0.60 production number is an optimization-signal gap (same column as Dx), and the
achievable SF ceiling is ~0.98. **H2 confirmed + H6 cleared** (no LLM calls, log parse):
the `minibatch=3` acceptance gate is noise-dominated (gate SE ≈ 0.13 vs ~0.05 real gains,
SNR ≈ 0.37) while best-so-far is monotone and the argmax is returned — the flat headline was
noisy *selection*, not a mechanics bug. **H2 fix RUN (2026-06-28) cleared the plateau**:
`minibatch=8` (gate SE 0.129→0.084) lifted dev140 0.702→**0.7194** — first GEPA-from-scratch
to beat the hand-tuned 0.710, on a big Diagnosis gain (0.57→0.66) — but the single-instruction
monolith trades families (SF 0.60→0.54), pointing at the multi-family program (re-run with the
H1+H2 fixes) as the next lever. H3/H5 still open for the push toward the 0.9155 hybrid.

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

## H4 RESULT (refuted) / D1 (resolved) — SeizureFrequency is NOT representation-capped

Tested per the recommended order (H1 done → H4 next, "unblocks ~25% of the headline").
Committed probe: `experiments/exectv2_gepa_diagnostics.py` (`uv run python …`). It builds a
*perfect model-style* SF answer (one fact per gold SF mention, shaped exactly as the dedup
LLM emits: `seizure_type` + coarse `state`, no raw `attributes` dict) and runs it through
the **same production path the GEPA metric scores** — `clinical_facts_to_mentions` →
`to_predicted_letter_from_mentions` (evidence gate + render-safety gate + CUI projection) →
`to_exect_letter` → `score_frequency_state`.

| dev140 SF clinical_headline | F1 | P | R | active-rate | seizure-free | unknown | dropped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **model-style perfect (valid evidence)** | **0.979** | 0.982 | 0.976 | 1.000 | 0.923 | 1.000 | 0 |
| oracle-replay (full gold attrs preserved) | 0.979 | 0.982 | 0.976 | 1.000 | 0.923 | 1.000 | 0¹ |
| model-style + RAW hyphenated gold text as evidence | 0.627 | 0.963 | 0.464 | 0.461 | 0.415 | 0.667 | 93 |

¹ the 374 "dropped" warnings in the oracle-replay arm are `dropped_model_supplied_projection_attribute: CUI/CUIPhrase` strip notes (2×187), not mention drops; CUI is re-derived by `project_cuis`, so the score is identical.

**Findings:**
- **H4 refuted.** A perfect model-style SF answer scores **0.979**, not anywhere near a cap.
  The coarse state collapse (`_seizure_state_attributes`: active→`{NumberOfSeizures:1}`,
  free→`{:0}`, unknown→`{}`/`FrequencyChange`) round-trips correctly because the
  `clinical_headline` state key only distinguishes seizure-free / active-rate / unknown, and
  gold "unknown"-by-state mentions carry a `FrequencyChange` attribute that keeps them alive
  through the render gate (`_has_sf_state`). Unknown-state recall is 1.000, not the drop I
  feared.
- **D1 resolved — it was an evidence-gate artifact, not a representation defect.** Feeding
  the raw *hyphenated* gold `text` as evidence (spaces rendered as hyphens ⇒ not an exact
  substring) fails the evidence gate for ~50% of SF mentions (94/187 survive ⇒ F1 0.627);
  the prior ad-hoc oracle that reported SF=0.0 evidently fed evidence that matched nothing.
  With a guaranteed-valid evidence substring the true SF representation ceiling (~0.98) shows
  through. (This is also a concrete D2 data point: the evidence gate is exact-substring
  coupled and silently drops non-verbatim evidence — already covered by the metric's
  "evidence must be an exact substring" feedback.)
- **Residual ~0.02 is a gold offset-drift artifact, NOT a fixable projection bug.** The ~5
  misses are seizure-free mentions where the gold annotated *span text* is truncated (e.g.
  "seizure") while its gold CUI is `C1299590` (the literal "seizure free" concept). No
  phrase-projection from the truncated text can recover `C1299590`, because that truncated
  token legitimately maps to the generic `C0036572`. Confirmed by attempting a state-aware
  remap (generic-seizure + seizure-free → `C1299590`): it *regressed* SF 0.979→0.883 because
  gold seizure-free mentions are **dominantly** `C0036572` (only 4 are `C1299590`, per
  `deterministic/lexicon.py`), so the remap broke far more than it fixed — reverted. The
  artifact does not affect the real model path: a model emitting "seizure free" as the
  `seizure_type` projects to `C1299590` correctly. Left as an inherent ~2% oracle ceiling.

**Follow-ups applied (2026-06-27):**
- *Bare-"unknown" SF drop* — a model-emitted SF fact with literal `state="unknown"` maps to
  empty attributes and is silently dropped by the render gate (`_has_sf_state`). It is dormant
  on dev140 (all gold unknowns carry a `FrequencyChange`), but the metric's drop hint
  (`gepa/metric.py:_clinical_hint`) now tells reflection that "every SeizureFrequency fact
  needs a concrete state … a bare 'unknown' state … is dropped" (test
  `test_feedback_warns_on_bare_unknown_seizure_frequency_drop`).
- *CUI-projection residual* — investigated and intentionally NOT changed (see residual bullet
  above; the only candidate fix was a net regression).

**Implication:** SF moves out of the "broken representation (H4)" column into the
"optimization-signal (H1)" column alongside Diagnosis. The production SF gap (≈0.54→0.60) is
reachable model behaviour, not a pipeline ceiling — the headroom to ~0.98 is an optimizer/
feedback problem, consistent with H1 already nudging SF 0.54→0.60. Next per the plan: H2/H3
(selection noise + sampling diversity) so GEPA can detect and bank these gains.

## H2 RESULT (confirmed) / H6 (cleared) — the selection signal is noise-dominated

No new LLM calls: `experiments/exectv2_gepa_diagnostics.py` now parses the saved GEPA run log
(`experiments/gepa_overnight_exectv2/h1_diff_run.log`), which records every accepted
candidate's full 50-letter valset scores plus the accept/aggregate trajectory. From the H1
diff-feedback run (task `gpt-4.1-mini`, `reflection_minibatch_size=3`, valset 50):

| selection quantity | value |
| --- | ---: |
| per-letter score std (median over candidates) | 0.224 |
| SE of valset mean (n=50) | 0.0317 |
| **SE of minibatch mean (n=3) — the acceptance gate** | **0.1293** |
| median \|accepted-step aggregate gain\| | 0.0485 |
| selection SNR — valset (gain/SE) | 1.53 |
| **selection SNR — minibatch (gain/SE)** | **0.37** |
| median per-example minibatch margin vs its SE | 0.058 vs 0.129 |

- **H2 confirmed.** The `reflection_minibatch_size=3` acceptance gate has SE ≈ 0.13, but the
  real per-step gains are ≈ 0.05 — **SNR ≈ 0.37**, so the gate accepts/rejects proposals
  largely by noise (the per-example accept margin 0.058 sits well inside its 0.129 SE). The
  n=50 valset Pareto signal is only marginal (SE 0.032 vs ~0.05 gains, SNR 1.5); the accepted
  aggregate trajectory swings ±0.10–0.19 (e.g. 0.629 → **0.422** → 0.448 → 0.639), far beyond
  the 0.032 SE. GEPA *is* climbing, but through a very noisy sieve — exactly the "explores
  but barely banks gains" pattern, and the lever that throttles how much of H1 it can keep.
- **H6 cleared.** Best-so-far is monotone non-decreasing (seed 0.578 → 0.589 → 0.629 → 0.639
  → 0.676) and the returned program is the valset argmax — no early-stop / acceptance / argmax
  bug. The flatness was the noisy *selection*, not a mechanics defect.

**Fix to test — staged for clean attribution** (H2 and H3 pull opposite ways on selection
*variance*, so do not bundle them blind):
1. **H2 first (`gepa_h2_minibatch_exectv2.py`):** raise `reflection_minibatch_size` 3 → 8
   (halves the gate SE to ≈ 0.078, lifting minibatch SNR ≈ 0.37 → ≈ 0.62), keep task temp 0,
   and bump the budget (`max_metric_calls≈1400`) so the larger minibatch does not cut the
   proposal count. No `run_gepa` code change needed; the diff-feedback metric is now default.
2. **H3 next (only if H2 under-delivers):** run the optimization phase at task temp ≈ 0.7 with
   cache off (reflector sees behavioural diversity), eval still at temp 0 — needs a `run_gepa`
   change to use a separate compile vs eval LM.

**Success = a clear jump above the 0.702 H1 plateau toward the 0.9155 hybrid.**

### H2 fix RUN RESULT (2026-06-28) — cleared the hand-tuned plateau, modestly

`gepa_h2_minibatch_exectv2.py`, `minibatch=8`, task temp 0, `max_metric_calls=1400`,
diff-feedback metric. Run `exectv2_gepa_dedup_gpt41mini_h2mb8_20260628` (41 min):

| dev140 | overall | Dx | SF | Rx | Inv | instr tok |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pre-H1 monolith (mb=3) | 0.628 | 0.46 | 0.54 | 0.82 | 0.79 | — |
| H1 diff (mb=3) | 0.702 | 0.569 | 0.597 | 0.836 | 0.864 | 576 |
| **H2 diff + mb=8** | **0.7194** | **0.662** | 0.540 | 0.850 | 0.862 | 490 |
| hand-tuned single prompt | 0.710 | 0.67 | 0.56 | 0.81 | 0.83 | 121 |

- **H2 confirmed, mechanism verified.** Re-parsing the new log, the gate SE fell exactly as
  predicted: minibatch SE 0.129 (n=3) → **0.084** (n=8). The cleaner gate let GEPA bank a big
  **Diagnosis** gain (0.569 → 0.662) and a smaller Rx gain in a **shorter** prompt (576 → 490
  tok), lifting the headline to **0.7194 — the first GEPA-from-scratch run to beat the
  hand-tuned 0.710 plateau.** This is the payoff the investigation predicted: the cap was the
  harness (H1 feedback + H2 selection), not the task.
- **Two honest caveats.** (1) *Monolith family tradeoff*: the single instruction cannot serve
  all four families at once — Dx +0.093 came with **SF −0.057** (0.597 → 0.540). (2) *Still
  noise-limited*: the per-accepted-step true gains shrank to ~0.019, so even the halved gate
  noise leaves SNR < 1 (minibatch 0.22, valset 0.56). The gate fix helped but did not unlock a
  large climb; the valset-best (0.659) is actually below H1's (0.676) — the dev140 headline rose
  because of the Dx/Rx gains and the shorter prompt, on a different (micro-F1 vs mean-per-letter)
  aggregation.

**Read:** H2 is a real, confirmed win (plateau cleared) but incremental. The now-visible
bottleneck is the **single-instruction tradeoff** (Dx↑ forces SF↓), which points at the
**multi-family multi-signature** program — flat at 0.631 *pre-H1* but never re-run with the
H1 diff-feedback **and** H2 minibatch fixes — as the highest-leverage next step toward 0.9155.
H3 (temp diversity) remains a secondary lever.

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

- **D1 — RESOLVED (2026-06-27): the "SF oracle = 0.0" was an evidence-gate artifact, not a
  representation defect.** A perfect *model-style* SF answer with valid evidence scores
  **0.979** through the production path (see "H4 RESULT" above). The prior oracle reported 0.0
  only because it used non-substring (hyphenated gold-text) evidence, so the evidence gate
  dropped every SF mention. The SF state round-trip is sound; the achievable SF ceiling is
  ~0.98. No fix needed beyond the model emitting verbatim evidence (already in the metric
  feedback). Probe committed: `experiments/exectv2_gepa_diagnostics.py`.
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

### H2 — CONFIRMED (2026-06-27): selection signal is noise-dominated
Valset is 50 letters; `reflection_minibatch_size=3`. **Confirmed** (no LLM calls, log
parse — see "H2 RESULT" above): the minibatch acceptance gate SE ≈ 0.13 dwarfs the ~0.05
real per-step gains (SNR ≈ 0.37); the n=50 valset SE ≈ 0.032 is only marginal (SNR ≈ 1.5).
GEPA accepts/rejects largely by noise. **Fix:** raise minibatch to ~8 (gate SE → ≈ 0.078)
and bump budget to preserve proposal count; bundle with H3 in the next run.

### H3 — temp=0 + cache gives the reflector no behavioral diversity
Task model runs at temperature 0 with cache on, so each instruction yields exactly one
deterministic output. GEPA sees a single point per candidate; the reflector cannot
observe the variance that reveals *why* a rule helps or hurts.
- **Test:** run the optimization phase with task temperature ~0.7 (and cache off for the
  task LM) so each candidate is sampled; keep final eval at temp 0.

### H4 — REFUTED (2026-06-27): SeizureFrequency representation is sound
Hypothesis was that the SF clinical_fact → headline-key path cannot match gold even on
perfect input, making ~25% of the headline unreachable. **Refuted:** the committed probe
(`experiments/exectv2_gepa_diagnostics.py`) builds a clean SF oracle from *model-style*
facts and scores **0.979** dev140 (active-rate 1.0, seizure-free 0.92, unknown 1.0) through
the production `_seizure_state_attributes` ↔ `frequency_state_keys('clinical_headline')`
path. The earlier "SF oracle = 0.0" was an evidence-gate artifact (D1, now resolved). SF's
gap is optimization signal, not representation — fold it into H1/H2/H3, not a pipeline fix.

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

### H6 — CLEARED (2026-06-27): no acceptance/argmax bug
**Cleared** (see "H2 RESULT" above): the candidate→valset trajectory shows best-so-far is
monotone non-decreasing (0.578 → 0.676) and the returned program is the valset argmax. The
flat *headline* was the noisy selection (H2), not a budget/early-stop/acceptance defect.

### H7 (kept, downgraded) — a genuine partial single-prompt ceiling
Still possible that a single prompt truly cannot reach the hybrid. But the **same base LLM
inside the multi-stage hybrid reaches 0.91**, so the capability exists; this hypothesis is
now secondary to the signal/feedback hypotheses above and should only be credited after
H1–H4 are addressed.

## Recommended order of attack

1. ~~**H1**~~ DONE (confirmed) — enriched reflective feedback with concrete gold-vs-pred
   diffs jumped mini monolith 0.628→0.702.
2. ~~**H4 + D1**~~ DONE (H4 refuted, D1 resolved) — SF representation is sound (perfect
   model-style SF = 0.979); SF gap is optimization signal, not a pipeline cap. No fix.
3. ~~**H2/H3**~~ H2 DONE — confirmed by diagnostic (gate SNR 0.37) AND by the fix run
   (`minibatch=8` → dev140 0.702→**0.719**, first to beat hand-tuned 0.710). H6 cleared. The
   monolith now shows a family tradeoff (Dx↑ SF↓). H3 (temp diversity) still open, secondary.
4. **Multi-family re-run** (NEXT, highest leverage) — `program_multifamily.py` was flat 0.631
   *pre-H1*; re-run with the H1 diff-feedback metric + H2 `minibatch=8` so each family gets its
   own evolved instruction (removes the monolith Dx↔SF tradeoff) — the most plausible path past
   0.719 toward 0.9155.
5. **D2/H5** (instrument the evidence gate and convention coupling). Partly evidenced by the
   H4 probe: the gate is exact-substring coupled and drops ~50% of SF on hyphenated evidence.
6. ~~Re-run mini monolith~~ DONE (H2 run, 0.719). Remaining: push past the monolith ceiling via
   the multi-family program (#4) and/or H3.

## Appendix — diagnostic evidence (dev140, no new LLM calls)

```
per-letter F1 distribution (monolith): 4 letters=0.0, 10=1.0, 126 partial   (gradient exists)
mean-per-letter F1 0.616  vs  micro F1 0.628                                 (aggregation: minor)
Diagnosis strict concept_negation F1 0.420  ==  source-near overlap F1 0.420 (not scorer strictness)
monolith vs multi-family predicted-fact Jaccard 0.675                        (instructions change behaviour)
perfect-input oracle, UNGATED: overall 0.786  (Dx 1.0, Rx 1.0, Inv 1.0, SF 0.0)   <-- SF "0.0" was an evidence-gate artifact, see below
perfect-input oracle, GATED:   overall 0.403, 69% facts dropped              (inflated: hyphenated gold evidence; real drop ~8.5%)
perfect MODEL-STYLE SF, valid evidence:  SF 0.979 (active 1.0, free 0.92, unknown 1.0)  <-- H4 refuted, D1 resolved (2026-06-27)
perfect MODEL-STYLE SF, raw hyphenated evidence:  SF 0.627, 93/187 dropped    (the gate, not the representation)
```

Reproduce: `uv run python experiments/exectv2_gepa_diagnostics.py` (committed; currently
implements the H4/D1 SF probe — extend with H2/H3 selection-noise probes as the
investigation continues).
