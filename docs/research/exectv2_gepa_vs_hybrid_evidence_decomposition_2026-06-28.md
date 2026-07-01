> **Superseded for navigation —** canonical summary: [`../../canon/08_gepa.md`](../../canon/08_gepa.md). Hybrid vs GEPA decomposition (use canon for corrected attribution). Full detail retained below.

# GEPA vs hybrid: the gap is LLM evidence retrieval, not deterministic rules

Status: **CLOSED diagnostic. Diagnosis-specific framing CORRECTED (2026-06-30); SeizureFrequency
framing PARTIALLY CORRECTED (2026-06-30).** The §3/§4 Diagnosis numbers below ("Dx misses are
dominated by genuine non-retrieval, 56/101") were computed by a coarse, text-overlap-only check
with no cardinality distinction and no clinical adjudication. A row-level re-examination
(`docs/experiments/exectv2/diagnosis/exectv2_dx_ev_recall_consolidation_check_2026-06-30.md`),
run after the same-date Diagnosis canonical row-adjudication found 85.2% of the *scored*
`clinical_headline` Diagnosis gap is gold multiplicity, asked whether that consolidation mechanism
also inflates *this* doc's evidence-recall gap. **It does, substantially:** of the 92 Diagnosis
`clinical_headline` misses, only **6.5%** are unambiguous genuine retrieval failures (no
phrase-overlapping prediction exists anywhere, and a clinician agrees the model erred); **93.5%**
are cardinality artifacts (the model's text was retrieved but credited to another gold annotation),
already-credited `source_near` true positives despite the concept-key mismatch, or genuine
phrase-divergence that is nonetheless clinically defensible (gold split one diagnostic statement
into a generic + specific tag; the model's one consolidated tag is reasonable).

A follow-up same-day extension
(`docs/experiments/exectv2/seizure_frequency/exectv2_sf_ev_recall_consolidation_check_2026-06-30.md`)
ran the analogous (freshly adjudicated, since no prior per-case verdict existed for this population)
check on SeizureFrequency's 72 `source_near` misses: **the same mechanism also inflates SF's
evidence-recall gap, though less completely than Dx's** — 61–83% (two readings; both clear the >50%
threshold) are cardinality artifacts or clinically-defensible consolidation, but a materially larger
genuine-error residual survives than Dx's (28/72 = 38.9% plain-verdict `GOLD_RIGHT`, vs Dx's 7.6%).

A second follow-up, same date
(`docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md`), completed
the sweep across all four `KEY_FAMILIES` with Prescription and Investigations — entities the
`clinical_headline` metric scores **per-occurrence**, not deduped, so the Dx/SF mechanism was not
guaranteed to transfer. It produced a **split result**: **Investigations needs no correction** — a
clean negative (25.9–29.6%, both readings, the lowest H-inflated share of any family checked), with
every `H2_GENUINE_DIVERGENCE` case (19/19) adjudicated a genuine miss, concentrated specifically in
**EEG under-extraction when an MRI is also present in the same letter** (a sharper, more actionable
target than this doc's aggregate "genuine non-retrieval" framing implied). **Prescription gets a
partial correction via a different mechanism than Dx/SF**: it crosses the H-inflated threshold but
only barely (52.2%, one case from the null), and two-thirds of its inflated bucket is not gold
multiplicity but **spelling/transcription divergence** (gold-span typos, letter-text typos, or a
brand/generic name split) that breaks `source_near`'s literal substring check even when every
structured attribute (CUI, dose, frequency) matches exactly between gold and prediction — a
measurement-mechanics finding distinct from the consolidation finding, pointing toward fuzzy/CUI-aware
evidence matching rather than consolidation-aware re-keying as the fix.

The doc's text below is left unedited as the historical record of what was measured at the time
(BP9), but its "genuine non-retrieval" framing should not be cited for Diagnosis, SeizureFrequency,
or Prescription without these corrections — the §5 "actionable lever for GEPA is retrieval, not
re-keying" conclusion **does not hold as stated for Diagnosis** (re-keying, already executed via
`exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` Phase 3, 0.703→0.792, was the correctly-shaped
fix), **holds only partially for SF** (re-keying captures the majority of SF's apparent gap too, but
a real, non-trivial genuine-retrieval residual remains, larger than Dx's), **holds in a modified
form for Prescription** (the residual is real but the lever is fuzzy-matching evidence credit, not
consolidation-aware keying), and **holds as originally stated for Investigations** (genuine
retrieval gap, validated rather than corrected, now localized specifically to EEG extraction).
Original status: **CLOSED diagnostic.** Date: 2026-06-28. Owner: ExECTv2 GEPA workstream.

Builds on / answers a question left open by
`docs/research/exectv2_sf_representation_not_recall_2026-06-28.md` (§10–§11, "the gap to
the hybrid is genuine, precision-preserving recall recovery"). That doc localized the SF
edge; this one decomposes the **whole** GEPA→hybrid gap across all four families into its
two candidate causes, by question:

> Q1. How much of the score is **deterministic rules recovering information the model
>     completely missed** (read the letter, add a fact)?
> Q2. How much can the GEPA score be improved by **re-using the evidence the model
>     already retrieved** (re-key, no new extraction)?

All numbers are zero-LLM, on the two best saved dev140 runs, reproduced by one committed
script: `experiments/exectv2_gepa_vs_hybrid_evidence_decomposition.py`.

- GEPA best: `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` (strict headline **0.731**)
- v08 hybrid: `exectv2_holistic_finding_assembly_v08_dev140_20260621` (strict headline **0.920**)

## 0. TL;DR

**The GEPA→hybrid gap (0.731 → 0.920 = +0.189) is almost entirely LLM evidence
*retrieval*, not deterministic post-processing.** The hybrid's four focused per-family
LLM producers retrieve overlapping evidence for **88%** of gold facts; GEPA's single
multi-family pass retrieves only **69%**. That evidence-recall gap (**+0.190**) matches the
F1 gap (0.189) almost exactly.

- **Q1 — deterministic recovery of missed info is small and Diagnosis-only.** The
  hybrid's entire deterministic stack lifts its own LLM producers **0.862 → 0.920
  (+0.058)**, and only **+0.017** of that is *recovering information the LLM missed*
  (reading the letter to add facts: 26 facts added, 25 correct, **all Diagnosis** heading
  recovery). The other +0.041 is *re-keying* retrieved evidence (dictionary CUI
  normalization, also all Diagnosis). **SeizureFrequency, Prescription, Investigations get
  ZERO from determinism** — their high hybrid scores (0.926 / 0.936 / 0.913) are produced
  entirely by the focused LLM lanes.
- **Q2 — re-using GEPA's retrieved evidence has a hard ceiling below the hybrid.** Of
  GEPA's 216 missed gold units, **51% have overlapping retrieved evidence (re-keyable)**
  and **49% are genuinely not retrieved**. A perfect re-keyer (oracle, no new extraction)
  lifts GEPA **0.731 → 0.854 (+0.123 upper bound)** — and the realistic, *validated* slice
  is about half that (SF state representation alone is +0.121 SF ≈ +0.03 aggregate). Even
  the oracle ceiling (0.854) stays **below the hybrid (0.920)**: the residual 0.066 is gold
  GEPA never surfaced.

**Synthesis:** deterministic rules are a thin, Diagnosis-specific veneer (~+0.06, mostly
CUI re-keying). The hybrid's dominance is bought with **more, focused LLM extraction**
(4 per-family producers vs 1 multi-family pass). To close the gap, GEPA must **retrieve
more evidence**, not re-process what it has.

## 1. The two architectures, as scored here

| | GEPA best | v08 hybrid |
| --- | --- | --- |
| LLM extraction | **one** multi-family de-dup pass (instruction-optimized) | **four** focused per-family producer lanes (Dx / SF / Rx / Inv) + verify/arbitrate |
| Deterministic stack | parse → evidence-gate → dedup adapter → scorer | parse → evidence-gate → **dictionary CUI normalize → residual benchmark/heading recovery → convention cleanup** |
| Strict headline F1 | 0.731 | 0.920 |

The hybrid exposes its deterministic pipeline as a `prediction_surfaces` ladder, which lets
us score each stage and attribute the lift. Strict headline = micro-F1 over the four
canonical `clinical_headline` family scorers (identical to the GEPA metric / dedup runner).

## 2. Q1 — the hybrid's deterministic stack, stage by stage (dev140)

Scoring each hybrid surface through the same aggregate scorer:

| surface (cumulative) | strict F1 | Dx | SF | Rx | Inv | what it is |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `source_scored` (raw LLM producers) | 0.862 | 0.757 | 0.926 | 0.936 | 0.913 | LLM evidence, minimally formatted |
| `evidence_valid` | 0.862 | 0.757 | 0.926 | 0.936 | 0.913 | drop evidence-gate failures (no-op here) |
| `dictionary_normalized` | 0.903 | 0.861 | 0.926 | 0.936 | 0.913 | **deterministic re-keying** (CUI) |
| `residual_benchmark_added` | 0.920 | 0.909 | 0.926 | 0.936 | 0.913 | **deterministic letter-recovery** |
| `final` | 0.920 | 0.909 | 0.926 | 0.936 | 0.913 | convention cleanup (no-op here) |

Reading the deltas:

- **+0.041 is re-keying retrieved evidence** (`dictionary_normalized`): deterministic CUI
  normalization, applied **entirely to Diagnosis** (0.757 → 0.861). It re-uses what the LLM
  retrieved; it does not read the letter for new facts.
- **+0.017 is recovery of MISSED information** (`residual_benchmark_added`): rules that read
  the letter (heading recovery / residual benchmark repair) and **add** facts the LLM did
  not emit — **26 facts added across dev140, 25 (96%) landing on a gold concept**, all
  Diagnosis (0.861 → 0.909). Zero facts dropped by cleanup at this stage.
- **SF / Rx / Inv are flat across the entire stack.** The deterministic rules touch only
  Diagnosis. SeizureFrequency's 0.926 — the column the whole "SF plateau" investigation was
  about — comes **100% from the focused SF LLM lane, 0% from determinism.**

**Q1 answer:** deterministic recovery of information the model completely missed is worth
**+0.017 of the hybrid's 0.920** (≈ 1.8% of its score), and it is entirely Diagnosis
heading recovery. Determinism's larger role (+0.041) is re-keying, not recovery — and the
hybrid's edge over GEPA is neither: it is the focused producers retrieving more evidence
(§4).

## 3. Q2 — re-using the evidence GEPA already retrieved

Decomposing GEPA's strict-headline **false negatives** (the recall deficit) by whether an
overlapping same-family prediction exists — nested by construction (we only inspect FNs):

| family | FN units | mis-keyed (re-keyable) | genuinely not retrieved |
| --- | ---: | ---: | ---: |
| Diagnosis | 101 | 45 | 56 |
| SeizureFrequency | 76 | 57 | 19 |
| Prescription | 15 | 3 | 12 |
| Investigations | 24 | 5 | 19 |
| **TOTAL** | **216** | **110 (51%)** | **106 (49%)** |

**Half of GEPA's misses are re-keyable, half are genuinely not retrieved.** The re-keyable
half concentrates in SeizureFrequency (75% of its FN) — the type-CUI-granularity +
state-representation tax already established in the SF doc. Diagnosis, Prescription, and
Investigations misses are dominated by genuine non-retrieval (Dx 56/101, Rx 12/15, Inv
19/24): the model never surfaces the co-present concept / drug / investigation.

**Oracle re-key ceiling** (credit every mis-keyed FN and every overlapping spurious FP —
i.e. a perfect re-keyer that fixes CUI granularity, state, dose, negation, multiplicity,
with no new extraction):

| family | strict F1 | oracle re-key F1 | Δ |
| --- | ---: | ---: | ---: |
| Diagnosis | 0.662 | 0.806 | +0.144 |
| SeizureFrequency | 0.592 | 0.819 | +0.227 |
| Prescription | 0.877 | 0.929 | +0.052 |
| Investigations | 0.858 | 0.888 | +0.029 |
| **aggregate** | **0.731** | **0.854** | **+0.123** |

The oracle is a strict **upper bound** and is optimistic: it credits any text overlap even
when the distinguishing attribute isn't actually recoverable (e.g. a generic "epilepsy"
prediction "covers" gold "temporal lobe epilepsy" by substring; SF oracle 0.819 exceeds the
*validated* state_profile 0.713). The realistic, validated achievable slice is roughly half
the oracle — for SF, the change-aware state profile is **0.592 → 0.713 (+0.121 SF,
≈ +0.03 aggregate)**.

**Q2 answer:** re-using GEPA's retrieved evidence can buy **at most +0.123** (oracle),
realistically **~+0.03–0.05** aggregate (dominated by the SF state re-key). **Even the
oracle ceiling (0.854) is below the hybrid (0.920).** The residual **0.066** is gold GEPA
never retrieved — unreachable by any re-keying; it needs new extraction.

## 4. Cross-architecture — where the 0.189 gap actually lives

Evidence-presence recall (`source_near` same-entity text-overlap: did the system retrieve
*any* overlapping prediction for each gold fact, representation aside):

| system | strict F1 | evidence-recall | attr-agree on overlaps |
| --- | ---: | ---: | ---: |
| GEPA best | 0.731 | **0.694** | 0.344 |
| hybrid `source_scored` (LLM only) | 0.862 | **0.867** | 0.520 |
| hybrid `final` | 0.920 | **0.883** | 0.505 |

The decisive line: **GEPA retrieves evidence for 69% of gold; the hybrid's raw LLM lanes
already retrieve 87%** (the deterministic stack adds only +0.016 more evidence-recall, via
heading recovery). The evidence-recall gap GEPA→hybrid is **+0.190 ≈ the F1 gap 0.189.**

So the gap is, to first order, a single quantity: **the hybrid's four focused per-family
LLM producers surface clinical facts that GEPA's one multi-family pass does not.** This is
an extraction-budget / focus difference (≈4× the LLM calls, per-family prompts), not a
deterministic-rules difference. It also explains the earlier-localized SF edge: the hybrid's
SF lane retrieves the change-class and the per-type multiplicity that the single pass
collapses.

### 4.1 Is the retrieved evidence the LLM's, or shuffled in by the deterministic stage?

Almost entirely the LLM's. Counting gold mentions (of 934) with overlapping retrieved
evidence at each hybrid surface isolates exactly where the evidence enters:

| surface | gold mentions w/ evidence | ev-recall | net change |
| --- | ---: | ---: | --- |
| LLM producers (`source_scored`) | **810** | **0.867** | the focused calls, before any deterministic step |
| evidence gate (`evidence_valid`) | 810 | 0.867 | 0 |
| dictionary normalize (`dictionary_normalized`) | 804 | 0.861 | **−6** (re-keying, not new evidence) |
| residual/heading recovery (`residual_benchmark_added`) | 825 | 0.883 | **+21** (deterministic letter-recovery) |
| final | 825 | 0.883 | — |

- **810 of the 825 gold mentions with retrieved evidence (98%) are captured by the LLM
  producers alone.** The lanes reach 0.867 evidence-recall before any deterministic step.
- The deterministic stack's **net** contribution to evidence-recall is **+15 mentions
  (+0.016)**: heading/residual recovery adds 21 (the same Dx facts as §2's 26-added/25-TP),
  while dictionary normalization *removes* 6.
- The −6 is instructive: normalization **lowers** raw text-overlap recall (it rewrites
  concept text to canonical form, moving it off a substring match with the gold span) even
  as it **raises** the scored F1 (+0.041), because the canonical text matches the gold
  *scoring key* better. Normalization trades raw evidence-overlap for key-correctness; it
  adds no evidence.

Mapped onto the cross-architecture gap, the hybrid's retrieval advantage over GEPA
(648 → 825 gold mentions, +0.190) splits as **LLM producers 648 → 810 (+162, ≈91%)** and
**deterministic recovery 810 → 825 (+15, ≈9%)**. The producers are the engine.

## 5. Implications

1. **The hybrid is not "a single model plus clever deterministic recovery."** Determinism
   contributes ~+0.06, almost all Diagnosis CUI re-keying; only ~+0.017 is recovering
   missed information. The hybrid wins by **extracting more with focused LLM lanes.**
2. **GEPA's ceiling on a single pass is real and ~0.85 even with a perfect re-keyer.** The
   ~0.066 residual to the hybrid is genuine non-retrieval; instruction tuning over one pass
   cannot reach it (consistent with the SF P2 plateau at 0.741 fair / 0.597 strict).
3. **The actionable lever for GEPA is retrieval, not re-keying.** The single highest-value
   re-key (SF state representation, +0.121 SF) is worth taking via the eval pivot
   (state_profile, P1) and a change-aware schema, but to approach 0.9 GEPA must adopt the
   hybrid's structural move: **per-family focused extraction** (multi-stage / multi-lane
   GEPA program), where the gain lives. This re-confirms the single-model plateau synthesis:
   the residual gap is architectural (multi-lane extraction), reachable only by GEPA over a
   multi-stage program, not by instruction tuning of one pass.

## 6. Artifacts

- `experiments/exectv2_gepa_vs_hybrid_evidence_decomposition.py` — reproduces every number
  above: surface ladder, evidence-presence recall, FN re-key/genuine split, oracle ceiling.
  Run: `uv run python experiments/exectv2_gepa_vs_hybrid_evidence_decomposition.py`.
- Alongside `exectv2_sf_representation_analysis.py` (SF-only relaxation ladder) and
  `exectv2_genuine_recall_analysis.py` (Dx/SF genuine-miss characterization).
