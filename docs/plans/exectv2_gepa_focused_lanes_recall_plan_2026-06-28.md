# Plan — replicate the hybrid's focused LLM lanes with GEPA (producer-recall, DeepSeek task model)

Status: **DRAFT plan, not started.** Decision gates at the end of Phase 0 and Phase 1.
Owner: ExECTv2 GEPA workstream. Date: 2026-06-28.

Follows from: `docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`.
**Redirects** (does not duplicate): `docs/plans/exectv2_gepa_multistage_program_scope_2026-06-28.md`
— that scope bet on an evolvable **verify** stage (S1) to close the gap; the evidence
decomposition shows the gap is in the **producers** (S0 generate), so this plan puts the
optimization budget there. Verify stays a later, secondary lever.

## 1. Why this exists — the finding that sets the target

The GEPA→hybrid gap (`clinical_headline` 0.731 → 0.920, +0.189) is **almost entirely LLM
evidence retrieval, not deterministic rules**:

- **Evidence-presence recall** (did the system retrieve any overlapping prediction for each
  gold fact) is **GEPA 0.694 vs hybrid 0.883**; that +0.190 gap ≈ the F1 gap 0.189.
- Of the hybrid's 825/934 gold mentions with retrieved evidence, **810 (98%) come from the
  LLM producers alone** (`source_scored` surface, ev-recall 0.867); the entire deterministic
  stack nets only **+15 mentions (+0.016)**, all Diagnosis heading recovery.
- The hybrid's deterministic stack lifts F1 only +0.058 (all Diagnosis: +0.041 CUI re-keying,
  +0.017 letter-recovery). **SF / Rx / Inv get zero from determinism** — their scores come
  entirely from the focused lanes.

So the lever is the **producers**: GEPA's single multi-family pass retrieves evidence for
69% of gold; the hybrid's four focused per-family producers retrieve 87%.

Note the structure is *already* per-family: `gepa/program_multifamily.py` runs four separate
`dspy.Predict` calls (one per family) and got 0.731 / ev-recall 0.694. **The gap is therefore
not "split into lanes" (done) but "make each lane retrieve exhaustively"** — recall-oriented
producers with the right schema, not a precision-balanced single draft.

## 2. Goal, hypotheses, kill-criteria

- **Goal:** lift per-family producer evidence-recall from **0.694 → ≥ 0.80** (toward the
  hybrid 0.867) and `clinical_headline` from **0.731 → ≥ 0.80** on dev140, with a credible
  path toward the hybrid 0.920 — by evolving recall-oriented per-family producers, on a
  **DeepSeek task model**.
- **H-producer (primary):** the lane deficit is recall, caused by (a) anti-recall
  schemas/instructions and (b) a precision-balanced F1 objective that found a parsimonious
  optimum. Fixing the schema (SF structured events + change class; Dx exhaustive co-present
  enumeration) and making the per-lane feedback recall-oriented closes most of the
  evidence-recall gap in a single pass.
- **H-model:** DeepSeek (`deepseek/deepseek-chat`) producers retrieve more evidence than
  gpt-4.1-mini at equal optimization (hand-tuned dev140: DeepSeek 0.745 > mini 0.710).
- **H-union (secondary, Phase 2):** if a single recall-oriented pass plateaus, a
  self-consistency **union** across varying-temperature samples per lane (the structural
  analog of the hybrid's multi-producer merge) supplies the rest of the recall.
- **Kill-criterion (Phase 1):** if recall-oriented DeepSeek producers do not beat 0.731 by
  ≥ +0.03 dev140 **and** lift ev-recall ≥ +0.05, the single-pass producer is not the lever;
  fall through to Phase 2 (union) once, then bank the producer-recall negative.

## 3. North-star metric & instrumentation (Phase 0a)

Every run reports, alongside `clinical_headline`, the **per-family and aggregate
evidence-presence recall** (`source_near` overlap recall) — the quantity this plan moves.
Wire it into `run_gepa._evaluate_program`'s summary (reuse `source_near_diagnostic` exactly
as `experiments/exectv2_gepa_vs_hybrid_evidence_decomposition.py` does). This makes
"did the producers retrieve more?" visible independently of keying, so we never again
confuse a retrieval gain with a re-keying gain.

## 4. Models — get GPT out of the loop

Per the steer to lean less on GPT, run a **full-DeepSeek** configuration:

| role | model | rationale |
| --- | --- | --- |
| task / extraction | `deepseek/deepseek-chat` | strongest hand-tuned dev140 (0.745); cheap enough for 4 lanes × 140 |
| reflection / mutation | `deepseek/deepseek-reasoner` | already the `run_gepa` default; reasoning teacher for instruction evolution |
| comparator only | `openai/gpt-4.1-mini` | the 0.731 baseline; not in the critical path |

Infra is ready: `GepaExperimentConfig.task_model` and `.reflection_model` are already
separate fields (the task LM has been mini while reflection was deepseek-reasoner all along).
Switching the extraction model to DeepSeek is a one-line config change per launcher. Optional
later: `deepseek/deepseek-reasoner` as the *producer* for the Diagnosis lane only (co-present
enumeration is reasoning-shaped), gated on cost.

## 5. Phases

### Phase 0 — instrument + cheap diagnostics (no new optimization)

- **0a. Evidence-recall instrumentation** (§3). Prereq for all gates.
- **0b. Deterministic-stack reuse headroom (zero-LLM).** Re-score the existing 0.731 GEPA
  preds through the hybrid's deterministic dictionary-normalization + heading recovery and
  read the lift. This bounds the *free* model-agnostic gain (the hybrid's +0.058) that GEPA
  could capture by reusing the same projection. **Caveat:** the in-sample concept normalizer
  is leaky/dev-only (see `concept_normalizer.py`, the CUI-stub negative) — report as an
  optimistic upper bound, not a test number.
- **0c. DeepSeek baseline.** Re-run the *existing* `program_multifamily` (no schema change)
  with `task_model=deepseek/deepseek-chat`, same budget as the 0.731 run. Isolates the model
  swap. **Gate:** report ev-recall + headline vs the mini 0.731 / 0.694.

### Phase 1 — recall-oriented per-family producers (the core experiment)

Fix the two recall defects the decomposition + SF doc identified, then evolve under DeepSeek.

1. **SF lane schema** — replace the anti-recall signature ("emit one fact per distinct
   seizure type … do not enumerate") with the **P3 Gan structured-event schema** (per-type
   `events` with `kind ∈ {frequency_rate, cluster_frequency, seizure_free, changed,
   unknown}`, instructed for per-type multiplicity). Already built and validated in
   `experiments/exectv2_sf_gan_representation.py` (lifted change-class recall 0.15 → 0.52);
   port its signature into the SF lane and project through the existing dedup adapter.
2. **Dx lane schema** — instruct **exhaustive co-present enumeration**: emit generic
   epilepsy *and* the specific syndrome *and* each named seizure type; expand discontinuous
   syndromes ("focal epilepsy-Probable temporal" → focal **and** temporal lobe epilepsy).
   This is the consolidation pattern the decomposition flagged (Dx 56/101 genuine misses).
3. **Recall-oriented feedback** — the metric already names missed gold facts (H1); add the
   per-lane **evidence-recall** miss list so reflection optimizes retrieval, not just keying.
   Keep **micro-F1 selection** (the per-family-beta *macro* objective backfired —
   `exectv2_gepa_recall_perfamily`); if extra pressure is needed use a mild global
   `recall_beta≈1.5` (uniform beta=2 helped Dx but over-emitted SF/Inv).
4. Run on `deepseek/deepseek-chat` (or the Phase-0c winner), `minibatch=8`, length penalty
   on, diff-feedback metric. Launcher mirrors `experiments/gepa_multifamily_h2_exectv2.py`.

**Gate (kill-criterion §2):** ≥ 0.761 dev140 headline **and** ev-recall ≥ 0.74, else → Phase 2
once, then bank the negative.

### Phase 2 — structural recall via self-consistency union (only if Phase 1 plateaus)

The hybrid merges multiple raw candidates per lane (`raw_lane_mentions` ≈ 12/letter). Replicate
that with a **union over k=3 varying-temperature samples** per lane, deduplicated by key — the
direct structural analog of the multi-producer merge, and the cleanest way to buy recall
without new prompt content.

- Requires sampling at **varying temperatures, never temp-0** ([[feedback_self_consistency_varying_temperature]]);
  `run_gepa` currently configures one cached temp-0 task LM, so this needs a small
  compile/eval temp-diversity hook (the H3 capability flagged but never built).
- Precision is recovered by the existing dedup adapter + a light **recall-additive verify**
  (P2's validated `program_sf_verify` pattern, generalized per lane — *not* the filter-only
  verify that cut recall in the failed multistage run).
- DeepSeek-reasoner as the Dx producer here is defensible (reasoning helps enumeration), gated
  on cost (k×4 lanes×reasoning is the expensive corner).

### Phase 3 — reuse the deterministic projection stack (cheap, model-agnostic)

Independently of the producer work, pipe the best GEPA producers through the hybrid's
deterministic dictionary-normalization + heading recovery to capture the +0.058 (mostly Dx)
the hybrid gets for free. Low-risk, but carries the same in-sample-normalizer test-safety
caveat (0b); report dev-only with the gap attributed.

## 6. Expected outcome & how it advances the thesis

- If **H-producer holds**: recall-oriented DeepSeek lanes lift ev-recall toward 0.85 and
  headline toward 0.85 (the hybrid's own `source_scored` LLM-only number is 0.862 at
  ev-recall 0.867), with Phase 3 deterministic reuse pushing toward ~0.90 — closing most of
  the architectural gap with **GEPA-evolved producers, no hand-curated verifier corpus.** That
  is the strong positive: the hybrid's edge was extraction recall, and GEPA can learn it.
- If **H-producer fails** (single-pass + union plateau below the hybrid): the residual recall
  is genuinely the hybrid's hand-curated corpus, the clean final architectural negative — but
  now correctly localized to **producer recall**, not the verify stage the prior scope blamed.

Either way the bet is now on the part of the architecture that actually carries the gap.

## 6b. Execution results (2026-06-28/29)

Ran Phase 0a (instrumentation), 0c (DeepSeek baseline), 1 (recall lanes), 3 (deterministic
re-key). Full DeepSeek (task `deepseek-chat`, reflection `deepseek-reasoner`), no GPT in loop.

| config (dev140) | headline | Dx | SF | Rx | Inv | ev-recall | oracle re-key |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mini per-family (prior best) | 0.731 | 0.662 | 0.592 | 0.877 | 0.858 | 0.694 | 0.854 |
| Phase 0c DeepSeek baseline (model swap only) | 0.681 | — | — | — | — | 0.748 | 0.825 |
| Phase 1 DeepSeek recall-lanes | 0.728 | 0.703 | 0.580 | 0.785 | 0.921 | 0.781 | 0.876 |
| **Phase 3 + deterministic Dx+Rx re-key** | **0.763** | **0.792** | 0.580 | 0.804 | 0.921 | 0.771 | — |
| v08 hybrid (target) | 0.920 | 0.909 | 0.926 | 0.936 | 0.913 | 0.883 | — |

**Findings, in plan terms:**
- **H-producer CONFIRMED.** Recall-oriented producers lifted evidence-recall **0.694 → 0.781**
  (+0.087, ~46% to the hybrid) and raised the oracle re-key ceiling **0.854 → 0.876** — the
  extra evidence is real and re-keyable, the decomposition thesis validated live.
- **H-model REFUTED for keying.** DeepSeek-chat is a better *retriever* but a worse *keyer*:
  the model-swap baseline lifted ev-recall (0.748) but **dropped** headline to 0.681 (over-emits,
  precision loss). DeepSeek helps retrieval, costs precision.
- **Phase 1 gate: split** — passed retrieval (ev-recall 0.781 ≥ 0.74), failed headline
  (0.728 < 0.761). The bottleneck moved from retrieval to **keying** — so Phase 2 (union = more
  retrieval) was correctly skipped in favour of Phase 3 (keying).
- **Phase 3 CLEARS the gate and is a new single-model best (0.763 > 0.731).** Deterministic Dx
  convention projection converts the retrieved Dx evidence (Dx **0.703 → 0.792**), and Rx
  convention-noise suppression partly recovers DeepSeek's over-emission (0.785 → 0.804). Zero new
  optimization; reuses the hybrid's existing `deterministic/conventions/*` functions.
- **SF stays 0.580** — ~~deterministic projection cannot touch it (confirmed: the hybrid keyed SF
  in its *producer*, not deterministically)~~. **CORRECTED by Phase 3b (§6c):** the hybrid *does*
  use a deterministic SF state/change projection (`sf_state_projection.py`, 766 lines) plus
  deterministic change extraction (`rules/change.py`); Phase 3 simply never wired them in. Phase 3b
  applied both and lifted SF 0.580 → 0.650 (clinical_headline) / 0.710 → 0.779 (state_profile).

**Caveat:** the deterministic Dx convention layer (`diagnosis_convention_target` alias table +
residual-benchmark patterns) is hand-curated and gold/dev-tuned, so 0.763 is a dev-optimistic
number with in-sample risk on the Dx rules (the standard benchmark-mimicry caveat — cf the prior
CUI-normalizer negative). The *retrieval* gain (ev-recall, oracle ceiling) is model-driven and
does not carry that caveat.

**Net:** full-DeepSeek producers + the existing deterministic stack reach **0.763**, ~0.157 below
the hybrid. The residual is concentrated in **SF** (un-keyable by determinism) and **Rx/Dx**
precision; the lever is now a precision-preserving SF producer/verify, not more retrieval or
more deterministic rules.

### Phase 4 — focused SF producer/verify, change-class precision (run 2026-06-29) = NEGATIVE

`program_sf_verify.py::VERIFY_SEED_V2` (recall-additive + explicit change-boundary discipline) +
`build_sf_verify_metric(change_precision_weight=0.2)` (per-letter change over-call penalty +
change-naming feedback), DeepSeek-chat task / reasoner reflection, 1000 metric calls
(`exectv2_gepa_sf_verify_v2_deepseekchat_20260629`).

| SF program (dev140) | clinical_headline | state_profile | changed R / P |
| --- | ---: | ---: | ---: |
| P2 (mini) | 0.597 | 0.741 | 0.48 / 0.46 |
| recall-lanes SF (DeepSeek) | 0.580 | 0.710 | — |
| **v2 change-precision (DeepSeek)** | **0.534** | **0.702** | **0.56 / 0.48** |
| hybrid | 0.926 | 0.930 | 0.85 / 1.00 |

**Change precision did not move (0.47 → 0.48).** Zero-LLM diagnosis of the 16 change over-call
letters: **9 gold = active-rate** (letter has a rate *and* a directional word — gold's
active-rate-vs-changed choice is a **convention**, not a rule), **5 gold = no SF** (DeepSeek
over-emitting on non-epileptic events), **4 gold = seizure-free**. So the change-precision wall is
~56% convention-boundary confusion + ~31% DeepSeek over-emission — **curated-precision territory,
not a learnable boundary**; a stronger penalty would suppress `changed` broadly and kill recall.
This reconfirms P2's conclusion with a sharper mechanism. v2's SF is *worse* than recall-lanes' SF,
so it is **not integrated**; 0.763 stands.

> **SF verify error analysis (2026-06-29).** A full per-letter, per-state error analysis of
> the P2 mini SF verify run (best: state_profile 0.741) decomposed the 74 errors into four root
> causes: per-type multiplicity failure (28% — model emits one state per type where gold
> multi-tags rate+qualitative), non-epileptic over-emission (31% — confirmed-diagnosis gate
> not followed), temporal confusion (20% — historical vs current), and empty predictions
> (11% — pure generation failures). The dominant finding is that the biggest category is a
> benchmark convention mismatch the instructions address abstractly but the model's
> consolidation instinct overrides — not fixable by instruction tuning alone. Implications for
> the deepseek-reasoner + mini re-runs are analyzed per category.
> Report: `docs/experiments/exectv2/seizure_frequency/exectv2_sf_verify_error_analysis_2026-06-29.md`.

**Arc conclusion (superseded by Phase 3b below).** The GEPA→hybrid gap decomposed cleanly and was attacked at each layer:
retrieval (GEPA recall lanes, ev-recall 0.694→0.781 ✓), keying (deterministic Dx/Rx re-key,
→0.763 ✓), and change-class precision (SF verify ✗ — curated convention GEPA can't learn from the
diff). **~~0.763 is the GEPA + reusable-deterministic single-model ceiling on this surface; the last
~0.16 to the hybrid 0.920 is curated convention precision (SF change-class active-rate-vs-changed +
the seizure-type-CUI granularity lottery) that the hybrid hand-encodes in its example corpus.~~**
Phase 3b (§6c) refuted this: the "curated convention" was reusable deterministic rules Phase 3
never wired in. The new ceiling is **0.781** (state_profile 0.779 for SF). The two remaining options
named here — (a) a hand-curated change-detection example set, or (b) a better-precision keyer model
for SF (GPT-mini) — are **taken up as Phase 5**, expanded with a third lever (per-(type,state) feedback
precision) and explicitly reframed to push the GEPA route without the deterministic SF fallback rather
than to bank the negative. Read Phase 5, not this paragraph, for current forward direction.

### Phase 3b — deterministic SF state/change projection (run 2026-06-29) = POSITIVE

Phase 3 applied Dx+Rx convention projection but left SF untouched, concluding "deterministic
projection cannot touch SF." That conclusion was **wrong**: the hybrid has a full deterministic SF
state/change projection (`deterministic/sf_state_projection.py`, 766 lines, `PROJECTION_VERSION =
exectv2_hybrid_sf_state_projection_v0.6`) plus deterministic change extraction
(`deterministic/rules/change.py`). Phase 3 simply never wired either into the GEPA re-key path
(`exectv2_phase3_deterministic_rekey.py`'s `_apply_projection` only branches on `family ==
"diagnosis"` and `family == "prescription"`; SF hits the fall-through). This phase wires both in
and measures the lift. Script: `experiments/exectv2_phase3b_sf_deterministic_projection.py`.

**Metric note (ADR 0037):** `clinical_headline`'s `_frequency_state`
(`scoring/seizure_frequency.py:218-234`) is count-only and **FrequencyChange-blind** — any `changed`
fact scores as `unknown`. So recall-additive change facts are invisible on clinical_headline and only
visible on `state_profile` (`frequency_state_faithful`, 4-way). Per ADR 0037, **state_profile is now
the primary SF metric.** Both are reported.

| config (dev140) | headline | Dx | SF (headline) | SF (state_profile) | Rx | Inv | ev-recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 1 recall-lanes (replayed) | 0.728 | 0.703 | 0.580 | 0.710 | 0.785 | 0.921 | 0.780 |
| Phase 3 + Dx+Rx re-key | 0.763 | 0.792 | 0.580 | 0.710 | 0.804 | 0.921 | 0.771 |
| **Phase 3b + SF projection** | **0.781** | 0.792 | **0.650** | **0.779** | 0.804 | 0.921 | 0.777 |
| v08 hybrid (target) | 0.920 | 0.909 | 0.926 | 0.930 | 0.936 | 0.913 | 0.883 |

SF state_profile detail:

| config | state_profile F1 | precision | recall |
| --- | ---: | ---: | ---: |
| recall-lanes | 0.710 | 0.60 | 0.88 |
| + SF projection | **0.779** | **0.68** | **0.92** |

Recall-additive change facts added: **18 across 15 letters.** The deterministic `CHANGE_EXTRACT_IMPLS`
regexes (`rules/change.py`) found change statements in the note text the producer missed.

**Findings:**
- **SF projection lifts both metrics.** clinical_headline 0.580 → 0.650 (+0.070) from filter/repair
  (dropping FP active-rates on unlabelled events, advice-only seizure-free, rejected changes).
  state_profile 0.710 → 0.779 (+0.069) from the same filter PLUS 18 recall-additive change facts
  (invisible on clinical_headline).
- **Overall headline reaches 0.781** — a new single-model best, up from Phase 3's 0.763.
- **The plan's "0.763 ceiling" and "curated convention GEPA can't learn" conclusions are refuted.**
  The rules existed and were reusable; Phase 3 simply didn't wire them in. The last ~0.14 to the
  hybrid is now genuinely un-attributed to a known reusable layer.

#### How the three projection types differ

The SF deterministic projection is qualitatively different from the Dx and Rx convention layers.
Dx and Rx are [[Meaning-Preserving Benchmark Projection]] — they change the scored representation
without changing the clinical fact the model selected. The SF projection includes two operations
that go beyond that boundary. Concrete examples from the Phase 3b run:

**Dx projection (RE-KEY): alias rewrite, evidence and clinical meaning preserved.**

| Letter | Model emitted | Projection did | What changed |
| --- | --- | --- | --- |
| EA0007 | concept `"focal onset"`, evidence `"possibly focal onset"` | RE-KEY → `"focal epilepsy"` | Label only (finding → diagnosis convention). Evidence unchanged. Same clinical concept. |
| EA0005 | concept `"epilepsy with generalised tonic clonic seizure alone"` | RE-KEY → `"...seizures alone"` | Singular → plural alias. Evidence unchanged. |

**Dx projection (DROP): convention noise, evidence inspected but not reinterpreted.**

| Letter | Model emitted | Projection did | Why |
| --- | --- | --- | --- |
| EA0009 | concept `"febrile seizures"`, evidence `"2 febrile seizures at the age of 2 months"` | DROP | Pediatric history fact, not a current diagnosis. The model's evidence is accepted; the fact is removed because its *category* is convention noise. |
| EA0006 | concept `"absence like seizures"`, evidence `"absence like seizures 2014"` | DROP | Historical (2014). Temporal marker in the model's own evidence. |

**Rx projection (DROP): planned/historical filter, evidence inspected but not reinterpreted.**

| Letter | Model emitted | Projection did | Why |
| --- | --- | --- | --- |
| EA0043 | drug `"lamotrigine"` 25mg, evidence `"start the dose of lamotrigine of 25 mg once-a-day"` | DROP | Future/titration plan (`"start the dose"`). The model's evidence is accepted; the fact is removed because it is not a current regimen. |
| EA0046 | drug `"Phenytoin"` 100mg, evidence `"Phenytoin 100mg od (reducing as detailed below)"` | DROP | Discontinuing regimen (`"reducing"`). |

**SF projection (FILTER/DROP): same mechanism as Rx — inspects model's evidence, removes.**

| Letter | Model emitted | Projection did | Why |
| --- | --- | --- | --- |
| EA0018 | state `active_rate`, evidence `"she has been getting episodes around twice a week"` | DROP | `"episodes"` is an unlabelled event (no seizure word). Non-epileptic. |
| EA0018 | state `changed`, evidence `"previously she was getting events with coloured objects"` | DROP | `"previously"` matches `_change_reject` historical pattern. |

**SF projection (REPAIR): overrides the model's clinical state interpretation — qualitatively different.**

| Letter | Model emitted | Projection did | Why |
| --- | --- | --- | --- |
| EA0182 | state `active_rate`, evidence `"She reports having a single seizure some 3 weeks ago."` | REPAIR → `seizure_free` | `_last_event_duration` detected `"3 weeks ago"` as a last-event marker. The model read "a single seizure" as an active rate; the deterministic rule reinterprets the temporal anchor to mean the patient has been seizure-free for 3 weeks. **The clinical meaning changes**, not just the label. |

**SF projection (RECALL-ADDITIVE): independent extraction from raw note text — fundamentally different.**

| Letter | Model selected | Projection added | Source |
| --- | --- | --- | --- |
| EA0050 | (nothing for this span) | state `changed`, evidence `"seizures have improved"` | `change.decreased` regex scanned the note text, found `"improved"` near `"seizures"`. The model never selected this evidence. |
| EA0025 | (nothing for this span) | state `changed`, evidence `"frequent myoclonic jerks"` | `change.frequent` regex found `"frequent"` + seizure type. Model missed it. |
| EA0011 | (nothing for this span) | state `changed`, evidence `"infrequent focal to bilateral convulsive seizures"` | `change.infrequent` regex. Model emitted the rate but not the qualitative descriptor. |

**Summary of the distinction:**

| Property | Dx RE-KEY | Dx/Rx DROP | SF DROP | SF REPAIR | SF RECALL-ADDITIVE |
| --- | --- | --- | --- | --- | --- |
| Operates on model's evidence | Yes (preserves) | Yes (inspects, removes) | Yes (inspects, removes) | Yes (preserves) | **No** (scans raw note) |
| Changes clinical meaning | No (label alias) | No (removes fact) | No (removes fact) | **Yes** (state override) | N/A (new fact) |
| Introduces new evidence | No | No | No | No | **Yes** |
| Projection category | Meaning-preserving | Meaning-preserving | Meaning-preserving | **Semantic reinterpretation** | **Independent extraction** |

The SF REPAIR and RECALL-ADDITIVE are defensible in a hybrid system — the hybrid does exactly this
(it runs deterministic extraction alongside LLM extraction and unions them, and its state projection
repairs active-rate → seizure-free from temporal markers). But they are **not** [[Meaning-Preserving
Benchmark Projection]] in the sense ADR 0027 / the glossary defines it: they change the clinical
fact itself, not just its scored representation. This is why Phase 3, which treated all deterministic
operations uniformly as "re-keying," missed them — the assumption that SF projection would be like
Dx/Rx projection (label/alias/filter over model-selected evidence) was wrong. SF projection is a
miniature deterministic extraction pipeline in its own right.

### Phase 5 — keep pushing the GEPA route: feedback precision + hand-curated examples + model swap (run 2026-06-29) = PARTIAL — new LLM-only SF best 0.784, gate not cleared

Phase 3b reached **0.781** overall / **0.779** SF state_profile **by wiring in the deterministic SF
projection** (`sf_state_projection.py` + `rules/change.py`). That is the *with-deterministic-fallback*
line. This plan's thesis is that the GEPA route should be pushed as far as possible **without** that
fallback — Phase 3b's SF projection is a comparison line, not the target. The SF verify error analysis
(`docs/experiments/exectv2/seizure_frequency/exectv2_sf_verify_error_analysis_2026-06-29.md`)
decomposed the LLM-only plateau (best non-deterministic SF: P2 mini **0.741** state_profile / **0.597**
clinical_headline; DeepSeek recall-lanes **0.710** / **0.580**) into four root causes and is the basis
for the three levers below. All three are run as a model matrix; the feedback redesign is the primary
lever, examples and model swap are crossed against it.

**Why current feedback can't target the error classes.** `build_sf_verify_metric`
(`program_sf_verify.py:288-321`) builds feedback at **letter-level state presence** — `gold_states` /
`pred_states` as de-duplicated state sets. It says "MISSED states: [changed]" but never names *which
seizure type*, nor *that the model already emits active_rate for that type and should ALSO emit
changed*. The four categories are invisible or under-specified at that granularity.

| Error category (error analysis §3) | Share | What feedback must say |
| --- | ---: | --- |
| A. Per-type multiplicity | 28% | Per-(seizure_type, state) diff: "for `<type>` you have active_rate AND gold also wants changed — emit BOTH as separate facts." Also name FC=Same ≠ a fact vs FC=Infrequent/Frequent = a fact. |
| B. Non-epileptic / unconfirmed over-emission | 31% | Attach the over-emission *reason*: if the letter has no confirmed-epilepsy Diagnosis entity (or it is negated/suspected), say "no confirmed epilepsy diagnosis on this letter → non-epileptic/suspected events do not count." |
| C. Temporal confusion (rate ↔ free) | 20% | Attach temporal reason: when spurious seizure-free and gold has an active_rate with a past-year/last-event anchor, flag "gold tags the historical rate as active, not the current seizure-free status." |
| D. Empty predictions | 11% | Already covered by the `record is None` "OUTPUT NOT SCORABLE" branch; a reasoning model (deepseek-reasoner) is the structural fix. |

**Hypotheses.**
- **H-feedback (primary):** moving the diff from letter-level state sets to **per-(seizure_type, state)
  keyed facts** and attaching the Cat-B/C *reasons* lets GEPA target the classes it currently can't,
  lifting LLM-only SF state_profile ≥ 0.78 on the same DeepSeek-chat arm — i.e., feedback precision,
  not more retrieval or more rules, is the lever.
- **H-examples (secondary):** a small hand-curated few-shot set demonstrating the exact conventions the
  model's consolidation instinct overrides lifts Cat A and B beyond what feedback alone reaches. These
  are *examples for GEPA to select as demos*, not a hand-written verifier corpus — they teach the
  rate+qualitative=two-facts, FC=Same-is-not-a-fact, confirmed-diagnosis-gate, and historical-vs-current
  conventions. Source letters from the error analysis: EA0108, EA0011 (rate+changed multiplicity),
  EA0007 (FC=Same must NOT be a changed fact), EA0057, EA0018 (confirmed-diagnosis gate), EA0006
  (historical rate tagged active, not current seizure-free).
- **H-model:** deepseek-reasoner as **both** extraction and verify producer (chain-of-thought explicit
  enumeration) helps Cat A/C/D; gpt-4.1-mini as **verify-only** (extraction stays DeepSeek-chat) helps
  Cat B via instruction-following — it already scored 0.741 vs DeepSeek-chat's 0.702 on the prior run.

**Model matrix (crossed against the feedback redesign).** Decision 2026-06-29: skip the
deepseek-chat A0 baseline (H-model already refuted chat as a keyer, §6b) and go straight to a
**deepseek-reasoner extractor** for both arms — CoT enumeration is the structural fix for the
dominant Cat A multiplicity + Cat C/D classes. The verify model is the crossed factor:

| Arm | extraction | verify | rationale |
| --- | --- | --- | --- |
| A1 reasoner-both | deepseek-reasoner | deepseek-reasoner | CoT enumeration for Cat A/C/D end-to-end |
| A2 reasoner+mini | deepseek-reasoner | gpt-4.1-mini | mini verifier (Cat B instruction-following) on the reasoner draft |

crossed with {feedback-only, +H-examples} = **four runs**. Feedback-only is run first per arm
(the attributable primary lever); +examples crosses the hand-curated demos on top.

**Execution status (teed up 2026-06-29).** Feedback redesign IMPLEMENTED and tested
(`build_sf_verify_metric` now builds the diff at per-(seizure_type, state) granularity with the
Cat A/B/C reasons attached; `program_sf_verify.py` + `tests/test_exectv2_gepa_sf_verify.py`).
Per-stage LMs and demos wired into `SfVerifyExtractor` (survive GEPA `build_program`
deepcopy + instruction-only mutation, verified). H-examples in
`gepa/sf_verify_demos.py` (4 compact demos, one per convention, attached to BOTH stages).
Parametrized launcher `experiments/gepa_sf_verify_phase5_exectv2.py`
(`--extraction-model`/`--verify-model`/`--with-examples`, `change_precision_weight=0.0` so
scoring is identical and the lift is attributable to feedback). Overnight orchestrator
`experiments/run_sf_verify_phase5_matrix.ps1` runs all four sequentially (feedback-only first).
Final eval = full dev140; the frozen test split is untouched.

**Gate (kill-criterion).** The LLM-only SF target is **state_profile ≥ 0.80 AND clinical_headline SF
≥ 0.65** on dev140 — both above the best non-deterministic SF run (P2 mini 0.741 / 0.597). Phase 3b's
0.779 / 0.650 (with deterministic projection) is the comparison line, not the gate. If the
feedback-only reasoner arms (A1/A2) do not beat 0.741 state_profile by ≥ +0.03, the feedback lever is
weak: the +H-examples crossing (run in the same matrix) is the fallback. If all four plateau below 0.80
state_profile, the residual is genuinely the deterministic SF projection and Phase 3b's 0.781 stands as
the GEPA+deterministic single-model ceiling; bank the negative with the mechanism localized to
LLM-only SF state precision.

**Scope boundaries.** Phase 5 evolves only the SF verify program's metric feedback and demos, plus the
model config — it does **not** touch the deterministic SF projection (`sf_state_projection.py`,
`rules/change.py`). The reported SF number is the LLM-only number; the Phase-3b-with-projection number
is reported alongside as the deterministic-fallback comparison, never blended.

**Execution results (2026-06-29).** Full doc:
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_verify_phase5_result_2026-06-29.md`. The
post-audit pipeline was re-smoked clean (all 4 arms exit 0, the Cat-B over-emission spiral the audit
targeted is gone), then the matrix ran on full dev140 (minibatch=8, 1000 calls, same
`score_frequency_state` path as P2).

| arm | extract→verify | examples | state_profile | clinical_headline | SP P/R | changed R/P |
| --- | --- | --- | ---: | ---: | --- | --- |
| reasoner→reasoner fb | reasoner→reasoner | no | 0.743 | 0.560 | 0.67/0.83 | 0.56/0.48 |
| reasoner→mini fb | reasoner→mini | no | 0.766 | 0.587 | 0.71/0.83 | 0.52/0.54 |
| **reasoner→reasoner ex** | **reasoner→reasoner** | **yes** | **0.784** | 0.586 | 0.78/0.79 | 0.56/0.56 |
| reasoner→mini ex | reasoner→mini | yes | 0.766 | 0.608 | 0.71/0.83 | 0.63/0.57 |

vs P2 mini 0.741 · Phase 3b **with** projection 0.779 · hybrid 0.930.

- **Gate (`state_profile ≥ 0.80` AND `clin ≥ 0.65`): NOT MET** (best 0.784 / 0.608). Feedback-lever bar
  (+0.03 → 0.771): cleared by **one** arm, and **only with demos** — feedback alone topped out at 0.766
  (+0.025). The +H-examples crossing (the predeclared fallback) supplied the difference.
- **New LLM-only SF best = 0.784**, +0.043 over P2, and **edges past the Phase-3b-with-projection line
  (0.779)** — the LLM-only route now reaches unaided what previously needed the deterministic projection.
- Demos are **decisive for reasoner-verify** (fb 0.743 → ex 0.784) but **inert for mini-verify** (0.766
  both): the reasoner needs concrete convention examples to discipline over-reasoning (error analysis §6
  predicted this); mini already follows the evolved instructions. H-examples ⇒ confirmed; H-feedback
  (primary) ⇒ partial (real but sub-threshold without demos).
- Gain is **precision** (winner P 0.67→0.78, R 0.83→0.79) from Cat-B/C + type-naming discipline. Audited
  all four selected instructions: **none contains the destructive "only emit a rate if there's a change"
  rule** the reasoner-verify reflection proposed during the smoke (valset gate rejected it 0.729 < 0.767;
  it never reached a selected program). The changed class improved across all arms vs P2's 0.473 (best
  reasoner→mini ex 0.63R/0.567P) but remains the drag vs hybrid's 0.85R/1.00P.

**Recommendation / adoption.**
- **Adopt `reasoner_reasoner_ex` (deepseek-reasoner extract + deepseek-reasoner verify + the 4
  hand-curated demos) as the LLM-only SF reference** at **0.784 state_profile** — the new LLM-only best,
  and the proof that the LLM-only route reaches the deterministic-projection line on its own. Its evolved
  prompt is `experiments/exectv2_gepa_sf_verify_p5_reasoner_reasoner_ex_20260629.instruction.txt`.
- For a **deployable** SF number, keep the deterministic SF projection alongside (Phase 3b, 0.779/0.650
  with projection); the two are reported separately, never blended.
- **Do not invest further in single-pass SF feedback tuning** — the ~0.78 LLM-only plateau is firm across
  fb/ex × reasoner/mini, ~0.15 below the hybrid's 0.93. The residual is **multi-lane extraction**
  (evidence-decomposition thesis), not feedback precision or determinism. The next real SF lever is
  architectural, not another feedback/demo iteration.

### Phase 6 — `changed`-class row-by-row adjudication (run 2026-06-29) = REVISES Phase 4 + the "irreducible" framing

Full doc: `docs/experiments/exectv2/seizure_frequency/exectv2_sf_changed_class_row_analysis_2026-06-29.md`.
A zero-LLM quantitative skeleton + five parallel sub-agent clinical adjudications read every dev140
letter where gold OR the model emits a `changed` state (14 misses / 15 over-calls / 13 agreements) on
the P2 mini run. The question: is the `changed` plateau an unlearnable convention boundary (Phase 4's
claim), and does optimising toward gold trade away clinical usefulness?

**Three findings overturn Phase 4's "not a learnable boundary; curated-precision territory".**

1. **The schema is direction-blind, and so are both metrics.** `program_sf_verify.py:58-75` offers only
   `kind = frequency_rate | cluster_frequency | seizure_free | changed` — no direction field. The model
   flags "changed" and the adapter fills `FrequencyChange="Same"` as a default. `state_profile` collapses
   the five-way FC vocab to one `changed` bucket; `clinical_headline` is FC-blind (`changed → unknown`).
   So `FC=Same` on every prediction is a *pipeline default, not the model's judgment*, and **direction is
   neither produced nor scored.** On the 13 agreements the model emitted `Same` while gold was directional
   in 12 — direction recovered 0/12. The "TPs" match only because the metric ignores direction.

2. **The errors decompose ~52% fixable representation defect / ~31% irreducible IAA-0.47 ambiguity /
   ~17% gold-convention friction** — not one wall. Recall misses are 100% lexically present (12/14 a band
   word adjacent to a seizure term; recoverable by the same `rules/change.py` whitelist Phase 3b used).
   Over-calls are 60% genuine error: 6/15 lift `Same` from *medication* language ("dose unchanged") or a
   diagnosis header (a missing **seizure-adjacency** rule), and several flatten clear deteriorations to
   `Same` (the missing **direction**). Only 2/15 over-calls and 9 BOTH_DEFENSIBLE cases are the genuine
   coin-flip the IAA 0.47 measures.

3. **Why two different LLMs (mini, deepseek-chat/-reasoner) plateaued at the same ~0.47:** they inherited
   the *same* representation defect (direction-blind schema + `Same` default + no seizure-adjacency +
   letter-level feedback), not the same irreducible floor. The hybrid's 0.85R/1.00P comes from fixing all
   three (direction-mapped whitelist + adjacency + recall-additive extraction); its 1.00P is partly
   in-sample fitting to this gold.

**Clinical-usefulness verdict (answers the standing question).** Mostly NOT "model more useful, marked
down": precision over-calls are 9/15 NO-LOSS noise, only 2/15 LOSE real info. The hypothesis holds partly
on recall (~36% of misses are gold double-tagging a band on a rate the model already has — convention
padding) and decisively at the **metric level**: the `changed` class scores presence-of-a-band-token, not
direction, so optimising it chases a noisy direction-stripped flag while the actionable signal (Increased
vs Decreased) is unmodelled and unscored.

**Revised next lever (supersedes Phase 5's "architectural, multi-lane extraction" as the *first* SF move).**
Before more extraction, test the representation fix: a **direction-aware SF schema** (five-way `kind`
matching the gold FC vocab) + **seizure-adjacency discipline** + a **direction-sensitive metric**. This
isolates whether the LLM-only route can reach the hybrid's change-class numbers on *direction* — the part
a clinician acts on, which the current schema and benchmark both discard. Phase 5's "stop single-pass SF
feedback tuning" stands (feedback was not the lever); this is a schema/metric change, a different axis.

### Phase 7 — canonical whole-corpus metric row-analysis (run 2026-06-29) = the wall is gold quality, not the model

Full doc: `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`.
Every dev140 letter, on the **exact `state_profile` metric** (direction-blind), with **both** model
stages captured and projected (stage 1 = `generate`, stage 2 = `verify`). Canonical run = the P2
gpt-4.1-mini two-stage program; harness `experiments/exectv2_sf_canonical_row_analysis.py`
(self-validates the per-row decomposition == `score_frequency_state`); 53 disagreement rows adjudicated
clinically in `experiments/exectv2_sf_canonical_adjudication.py`.

- **First LLM (stage 1) is wrong ~50% of letters** (exact 49.3%, F1 0.710); the verifier cuts it to
  37.9% wrong (F1 0.772), almost all via precision; verify **fixes 14, breaks 7** (3 are regressions
  deleting a correct `seizure-free`).
- **Of the 53 metric-errors only 15 (28%) are genuine model mistakes.** 22 (42%) are the model right and
  scored wrong (gold **under-annotated** a stated frequency = 13, or **redundantly double-tagged** a type
  = 9); 16 (30%) are genuine IAA-0.47 ambiguity / gold temporal conventions. **Counting only genuine
  errors the model is clinically defensible on 125/140 = 89.3% of letters** vs the 62.1% the metric reports.
- **The metric is noisy:** a faithful re-run of the *same* program scores 0.772 not the logged 0.741, with
  41/140 letters flipping state-set across identical-instruction runs (gpt-4.1-mini temp-0). The
  0.741→0.763→0.779→0.784 ladder is partly inside a ±0.03 band.
- **Conclusion:** the ~0.74–0.78 SF "wall" is a **gold-quality ceiling** (SeizureFrequency human IAA F1
  = 0.47), not a model ceiling. The only attributable model lever left is the 15 genuine errors, which are
  rule-shaped (temporal discipline + state-evidence discipline + stop the verify deletions) = exactly the
  Phase-3b deterministic SF projection. **Stop single-pass `state_profile` optimisation; report SF with a
  ±0.03 re-run band; move the SF story into the closing benchmark-vs-clinical-recovery reconciliation.**

## 7. Reuse & artifacts

- Reuses unchanged: `program_multifamily.py` (lane structure), `run_gepa.run_experiment`
  (`task_model`/`reflection_model`/`recall_beta` already wired), `gepa/metric.py`
  (diff feedback), the dedup parser/adapter/scorers, `source_near_diagnostic` (ev-recall).
- New: SF lane structured-event signature (port from `exectv2_sf_gan_representation.py`),
  Dx exhaustive-enumeration signature, ev-recall in `run_gepa` summary, per-phase launchers
  mirroring `gepa_multifamily_h2_exectv2.py` with `task_model=deepseek/deepseek-chat`.
- Diagnostic already committed: `experiments/exectv2_gepa_vs_hybrid_evidence_decomposition.py`.
- Phase 3b: `experiments/exectv2_phase3b_sf_deterministic_projection.py` (run script) +
  `experiments/exectv2_phase3b_projection_examples.py` (per-fact projection trace diagnostic) +
  ADR 0037 (`docs/decisions/0037-sf-state-profile-is-primary-clinical-metric.md`).
- Registry note: registration still skipped by the malformed `experiments/registry.jsonl:63`
  (artifacts written regardless) — fix line 63 to re-enable, as for prior arms.
