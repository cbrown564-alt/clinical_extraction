# The ExECTv2 SeizureFrequency "plateau" is a representation/eval artifact, not a recall ceiling

Status: **OPEN — reopens the SF conclusion of the single-model plateau synthesis.** Date: 2026-06-28.
Owner: ExECTv2 GEPA workstream.

Supersedes (in part): `docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md` §4–§5
(the "genuine recall, hand-rules only" verdict for SeizureFrequency).
Builds on: `docs/research/exectv2_gepa_underperformance_investigation_2026-06-27.md`
(H4/D1 — the perfect model-style SF probe).

## 0. TL;DR

The single-model plateau synthesis closed SeizureFrequency (SF) as *"genuine recall — state
detection, recoverable only by the hybrid's hand-curated rules."* That verdict does not survive
the predictions. **The SF "0.59 plateau" is dominated by two scoring/representation artifacts —
the seizure-type-CUI granularity lottery and gold's exhaustive per-type multiplicity — not by the
model's inability to reason about seizure frequency.** Re-scoring the *same* best-run predictions
under a Gan-style per-letter state profile lifts SF from **0.592 → 0.713** with no change to the
model. The genuine residual is narrow and learnable: the model over-calls `active-rate` (precision
0.66) and barely detects qualitative frequency change (`changed` recall **0.15**) — the exact class
the schema collapses (`changed → unknown`) and the GEPA feedback never names.

This reframes the whole ~0.73 plateau, not just SF: the de-dup `clinical_headline` task instructs
the model to **consolidate** ("emit one fact per distinct seizure type") against a gold convention
that **rewards exhaustive, granularity-specific multi-tagging.** We are both designing the inputs
wrong and evaluating the outputs wrong, and the two compound.

## 1. The contradiction that reopens the case

Two established facts cannot both support the synthesis's conclusion:

- **A perfect model-style SF answer scores 0.979** through the exact production scoring path
  (prior investigation §H4). SF is logged there as "NOT representation-capped; the gap is
  optimization signal, same column as Dx."
- The plateau synthesis reports the SF gap as a **recall ceiling reachable only by hand-rules**,
  on the strength of a script (`exectv2_genuine_recall_analysis.py`) that found "19 genuine misses."

The 19 is an artifact of that script's design: it does
`if any(gp in pp or pp in gp): continue  # convention miss, not genuine` (line 168) — it **discards
every overlap-mismatch by construction** and reports only the residue. A proper multiset
decomposition (below) shows the SF loss is 89 FN / 44 FP, and the *spurious* 44 facts (98% with no
overlapping gold) are the other half of the same coin: the model tags seizure types/contexts the
annotator didn't. The synthesis measured the leftover and named it the whole gap.

## 2. The decomposition (zero-LLM, on the best run's saved predictions)

Run: `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` (dev140, the 0.7313 best).

### 2a. Re-scoring the same predictions under progressively relaxed SF keys

| SF scoring key (identical predictions) | P | R | F1 | Δ |
| --- | ---: | ---: | ---: | ---: |
| `(seizure-type-CUI, state)` — production `clinical_headline` | 0.601 | 0.583 | **0.592** | — |
| `(state,)` multiset — drop seizure type, keep multiplicity | 0.706 | 0.615 | 0.657 | **+0.065** |
| `(state,)` presence per letter — **the Gan framing** | 0.705 | 0.721 | **0.713** | **+0.121** |
| perfect model-style SF (prior §H4 probe) | 0.982 | 0.976 | **0.979** | ceiling |

So the 0.592 decomposes as **~+0.065 seizure-type-CUI granularity** + **~+0.056 exhaustive
per-type multiplicity**, leaving a genuine state-detection residual that is itself dominated by a
schema artifact (next).

### 2b. State distribution — the model tags the wrong *kind* of frequency, not zero frequency

Of **99 letters with gold SF, the model emitted zero SF in only 2.** It emits roughly the right
volume (163 facts vs gold 187) — it is not silent and not under-reasoning.

| state | gold mentions | pred mentions | per-letter presence recall | precision |
| --- | ---: | ---: | ---: | ---: |
| seizure-free | 65 | 53 | 0.79 | 0.80 |
| active-rate | 89 | **104** | 0.92 | **0.66** (over-called) |
| changed (FrequencyChange) | **33** | **6** | **0.15** | 0.67 |

The genuine residual after removing the representation tax is two learnable behaviors:
**over-emitting `active-rate`** and **failing to detect qualitative change** (`changed` recall 0.15;
27 gold letters, the model fires in 6).

### 2c. Why the model misses — concrete cases

- **`EA0119`**: gold tags the **generic** "seizure" (`C0036572`) **four times** (week-rate,
  month-rate, twice "frequent"); model emitted one **specific** "focal seizures with altered
  awareness" (`C0270834`). Same clinical reality, different CUI bucket → 2 FN + 1 FP, zero credit.
- **`EA0049`**: gold tags GTC and myoclonic **twice each** — once with a numeric rate
  (`active-rate`), once as a qualitative change (`FrequencyChange: Frequent` → keyed `unknown`).
  The model emitted one consolidated fact per type; it got the rates right and was *structurally
  guaranteed* to miss the change-keyed duplicates.
- **`EA0181`**: gold "seizures 10–15/day" (generic CUI); model "focal dyscognitive seizures"
  (`C0270834`) — correct clinically, wrong CUI bucket.

## 3. Root causes (with the code receipts)

1. **The seizure-type-CUI granularity lottery.** `_frequency_type_key` (`scoring/seizure_frequency.py:165`)
   keys every SF fact on the annotator's chosen seizure-type CUI. Generic "seizure" vs the specific
   subtype are *both clinically correct*; picking the other one is an automatic FN+FP. (This is the
   same over/under-collapse that made CUI normalization **hurt** Diagnosis in the synthesis.)

2. **Gold's per-type multiplicity vs the de-dup instruction.** After `clinical_headline` dedup, gold
   still carries, per seizure type, two keys: `(type, active/free)` from a numeric rate **and**
   `(type, unknown)` from a separate qualitative descriptor. The SF signature
   (`gepa/program_multifamily.py:60`) says **"emit one fact per distinct seizure type"** — we told
   the model to deduplicate against a target that rewards the opposite.

3. **The qualitative-change class falls through a schema crack.** The model is told to emit `changed`
   (`program_multifamily.py:64`); the adapter maps it to `{FrequencyChange}` (`facts.py:179`); then
   the **scorer's** `_frequency_state` (`scoring/seizure_frequency.py:172`) **ignores FrequencyChange
   entirely** and re-buckets it to `unknown`. There are **two divergent state functions** — the 3-way
   count-only scorer vs the 4-way round-trip at `facts.py:309` — and the scorer is the lossy one, so
   "detecting a change" is never distinguishable from "no information."

4. **The GEPA feedback cannot teach any of this.** `_family_diffs` (`gepa/metric.py:186`) computes
   missed SF units on the deduped CUI keys but renders them via `_label` as **text**
   ("seizure [FrequencyChange=Frequent]"). The reflection LM is shown a text label for what is
   actually a *CUI-granularity* and *multiplicity* failure, and the rendered guidance contradicts the
   standing "one fact per type" instruction. No budget increase could move SF.

## 4. Why Gan ≫ ExECTv2-SF — and it is not the model

Gan scores **one frequency band per case**; ExECTv2 scores **(annotator-CUI, count-state) tuples
with multiplicity**. The score difference is, to first order, the *measurement representation* — the
relaxation table (§2a) proves it: the identical predictions score 0.713 under the Gan-style state
profile vs 0.592 under the strict key. The model is not worse at seizure frequency in ExECTv2; the
ExECTv2 SF surface is a hostile schema for the same clinical quantity.

## 5. Implementation plan

Ranked by leverage × cost. P1 and P4 are implemented in this change set; P2/P3/P5 follow.

### P1 — Re-baseline SF on a clinically-faithful surface *(implemented here)*

Add a **type-agnostic per-letter state profile** (the Gan framing) as a first-class SF clinical
metric alongside the convention-strict `clinical_headline`, mirroring the existing
`active_rate_fidelity` companion precedent. Honor `FrequencyChange` so a detected change is a
real, credited `changed` state.

- `scoring/seizure_frequency.py`: new `frequency_state_faithful` (4-way: seizure-free / active-rate /
  changed / unknown), `_frequency_state_profile_keys` (per-letter presence set), and a
  `state_profile: PRF1` field on `FrequencyStateScores`. `clinical_headline` is **unchanged** and
  retained as the convention-strict companion — we report both, we do not silently swap.
- Auto-surfaces in the clinical-recovery scorecard (`_model_scores_to_dict` iterates `model_fields`).
- Result on the best run: `state_profile` **F1 0.713** vs `clinical_headline` 0.592. The honest
  clinical SF number is the **bracket [0.592, 0.713]**, the gap being the type-CUI granularity tax.

### P4 — Make the SF GEPA feedback teach the convention *(implemented here)*

- `gepa/metric.py`: render the **state class** in SF diff labels (via `frequency_state_faithful`),
  e.g. "absence: changed" / "GTC: active-rate", so reflection sees *what kind* of frequency it
  missed or over-emitted; add explicit guidance that a reported change in frequency
  (more/fewer/improved/worse) is a distinct `changed` fact and that not every mention is an active
  rate. This unblocks a future re-run (P2) from climbing the clinical target.

### P2 — Re-run GEPA against the faithful target *(follow-up)*

Flip the GEPA selection objective / aggregate to use `state_profile` for SF (or a blend), align the
SF signature to the committed convention (drop "one fact per distinct seizure type"; instruct one
assertion per distinct frequency statement incl. qualitative change), and re-run mini at
`minibatch=8`. Expected: SF climbs toward the 0.713+ profile ceiling; the change class recovers.

### P3 — Port the Gan structured-event representation *(RUN 2026-06-28; result in §8)*

Ran a focused Gan-style structured-event SF extractor on ExECTv2 letters, projected through the
existing dedup adapter + scorer. The representation **recovers the change class** (0.15→0.52 recall)
but the aggregate is precision-limited and does **not** alone close the gap. Full result in §8.

### P5 — Decide whether annotator-CUI-mimicry is a valid target *(research-integrity)*

If a clinically-correct SF statement is wrong because the annotator chose a different CUI
granularity, the strict metric measures mimicry, not recovery (the benchmark-vs-clinical-recovery
tension already in the project ledger). Recommended framing: clinical-recovery (state profile)
primary, strict convention as a fidelity companion, gap explicitly attributed.

## 6. Generalization — this is the whole plateau, not just SF

The synthesis's own Diagnosis finding ("the model **consolidates** where gold tags every co-present
concept: *focal epilepsy-Probable temporal* → both focal **and** temporal") is the **identical**
granularity+multiplicity mechanism. So the ~0.73 single-pass plateau across both gap families has
one root cause: the de-dup framing instructs consolidation against an exhaustive multi-tagging
target. The "architectural gap to the hybrid" framing is therefore misleading — the hybrid's edge is
most plausibly hand-coding this convention (re-expansion + CUI granularity via its dictionary), not
multi-stage reasoning that instruction tuning cannot reach.

## 7. Artifacts

Diagnostics (zero-LLM, read-only; one committed script reproduces all numbers below):
`experiments/exectv2_sf_representation_analysis.py` — run
`uv run python experiments/exectv2_sf_representation_analysis.py`:
- SF key-relaxation ladder (`(type,state)` → `(state,)` multiset → presence) = 0.592 / 0.657 / 0.713.
- SF clinical_headline loss decomposition (genuine miss 76% / type-CUI 15% / state 9% of FN; FP 98% spurious).
- Change-aware per-state presence recall (changed recall **0.15**; active-rate precision **0.66**, over-called).

(Alongside the existing `exectv2_genuine_recall_analysis.py` / `exectv2_convention_tax_analysis.py`.)

Code (this change set): `scoring/seizure_frequency.py` (`state_profile`), `scoring/__init__.py`
(export), `gepa/metric.py` (SF feedback), `tests/test_exectv2_scoring.py` (new SF tests).
P3: `experiments/exectv2_sf_gan_representation.py` (+ run
`exectv2_sf_gan_representation_gpt41mini_20260628`).

## 8. P3 result — the Gan structured-event representation (run 2026-06-28)

A focused Gan-style structured-event SF extractor — per-type `events` with `applies_to` + `kind ∈
{frequency_rate, cluster_frequency, seizure_free, changed, unknown}`, instructed for gold's
per-type multiplicity — run on dev140 with the **same** model (gpt-4.1-mini), each event projected
to an ExECTv2 SF fact through the **existing** dedup adapter + scorer. Note this is a **lean,
unoptimized single prompt**, compared against the **GEPA-optimized** de-dup best.

| metric (dev140) | de-dup best (optimized) | P3 Gan-event (lean) |
| --- | ---: | ---: |
| clinical_headline | 0.592 (P0.601 R0.583) | 0.569 (P0.540 R0.601) |
| state_profile | 0.713 (P0.705 R0.721) | **0.708 (P0.665 R0.757)** |

Per-state presence recall — the decisive cell:

| state | de-dup R / P | P3 R / P |
| --- | ---: | ---: |
| seizure-free | 0.79 / 0.80 | 0.79 / 0.73 |
| active-rate | 0.92 / 0.66 | 0.84 / 0.63 |
| **changed** | **0.15 / 0.67** | **0.52 / 0.64** |

**The representation does exactly what it was designed to.** Naming the qualitative-change class
lifts its recall **0.15 → 0.52 (3.5×)** — the de-dup schema's `changed → unknown` collapse *was*
suppressing a real, detectable signal (the input-design half of the premise, confirmed
behaviourally). But the **aggregate is flat** (state_profile 0.708 vs 0.713): the recovered change-
recall is paid for in precision — P3 emits 203 SF facts vs gold 187 (de-dup 163) — and active-rate
recall dips. A single gpt-4.1-mini pass, even with the right schema, sits at the **~0.71
type-agnostic clinical ceiling**; recovering recall costs precision.

**Premise resolved, precisely — both halves confirmed and separated:**
- *Evaluation is wrong*: ~0.12 of the strict 0.59 is the seizure-type-CUI granularity lottery +
  multiplicity (P3's relaxation ladder 0.569→0.708 reproduces it; the tax is **larger** for P3
  because it extracts more *specific* — correct — seizure types that miss gold's generic CUI). Not
  winnable by any extractor; needs the eval pivot (P1/P5).
- *Input design is wrong*: the change class is recoverable by a schema that names it (0.15→0.52).
- *Neither closes the gap to the hybrid's 0.91 alone* on a single pass: the residual is
  **precision-preserving recall recovery** — what the hybrid's curated verifier corpus does. The
  *mechanism* behind the premise is confirmed; the *strong form* ("reschema a single pass to ~0.9")
  does not hold.

**Immediate next diagnostic (cheap, decisive):** re-score the **v08 hybrid's** saved SF predictions
through `state_profile`. If the hybrid is also ~0.71 there, its 0.91 was substantially the CUI/
multiplicity convention tax and the "gap" largely evaporates under the fairer metric — the eval
pivot is then the whole story. If the hybrid holds ~0.9 on `state_profile`, the gap is genuine
precision-preserving recall recovery and the lever is a verify-that-keeps-recall second pass, not
more single-pass schema tuning. This is the single highest-value follow-up.
