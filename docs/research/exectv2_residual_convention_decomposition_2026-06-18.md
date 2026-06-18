# ExECTv2 Residual Convention Decomposition

Date: 2026-06-18
Scope: the two below-target key families — Diagnosis (reconciler v0.1, F1 0.658)
and SeizureFrequency (state adjudicator v0.5, F1 0.721), dev140.
Status: companion analysis to the key-entity architecture research report
(`exectv2_key_entity_architecture_research_report_2026-06-18.md`). Zero model
budget; deterministic re-analysis of existing prediction artifacts.

---

## Why this document exists

The architecture report organizes the entire remaining effort around one
objective: get all four key families above F1 `0.8` on dev140, then freeze. For
Diagnosis and SF that plan assumes the gap to `0.8` is *recoverable* — that more
verifier/adjudicator iteration will close it. The plan never tests that
assumption. It reports the residual as ranked failure *clusters* ("generic
epilepsy over-emission, tonic-clonic over-emission, focal misses") but never asks
the prior question:

> **How much of the Diagnosis/SF residual is the model being clinically right and
> the benchmark convention scoring it wrong — versus the model genuinely failing?**

That fraction decides whether the next loop is worth running. If most of the gap
is convention noise, no amount of clinical prompting converges on it; if most is
genuine, the loop has headroom. This is the ExECTv2 analog of the Gan strand's
"faithful-but-wrong" cell (`gan2026_reliability_scorecard...`, P0.1) — the number
the project built an instrument to see and then stopped computing.

This document computes it.

---

## Method (one paragraph, fully reproducible)

Driver: `experiments/build_exectv2_convention_residual_decomposition.py`. It
reloads the two best candidates' per-letter prediction JSONLs and rebuilds the
false-negative / false-positive residual **using the scorer's own concept
machinery** (`deterministic/normalization.py` concept collapse + hierarchy;
`scoring.py` state/type keys) — so the reconstruction reproduces the published
ledger counts **exactly** (Diagnosis 243 TP / 126 FP / 126 FN; SF 137 TP / 56 FP
/ 50 FN). Each residual event (every FP and every FN) is then classified by a
*same-letter co-occurrence* test into convention-bound vs genuine:

- **assertion / state convention** — the same clinical concept is present on the
  opposite side in the same letter; only the annotation attribute disagrees
  (Diagnosis Certainty/Negation; SF active-rate / seizure-free / unknown state).
- **granularity / ownership** — the opposite side carries an ancestor/descendant
  on the Diagnosis lineage (`DIAGNOSIS_PARENT`), or a generic↔named seizure
  pairing for SF: the fact is captured at the wrong altitude.
- **related-family** (Diagnosis only) — the opposite side carries a clinically
  adjacent epilepsy/seizure-type concept (a softer convention signal).
- **genuine** — no related concept on the opposite side: a true miss (FN) or a
  true over-emission (FP).

Caveats stated up front: matching is greedy and pairs are symmetric; the three
convention buckets are a **lower bound** on convention-boundness (a real
attribute/scope disagreement across different letters cannot be paired and falls
to "genuine"). The "genuine" bucket is **not** fabrication — see next section.

---

## Part I — The decomposition

Evidence validity first, because it determines how to read "genuine":

| Family | Mentions | Evidence-valid | Call/parse errors |
| --- | ---: | ---: | ---: |
| Diagnosis | 438 | 436 (99.5%) | 0 / 0 |
| SeizureFrequency | 193 | 193 (100%) | 0 / 0 |

**There is essentially no hallucination and no render failure.** Every residual
event is grounded in real letter text. So a "genuine over-emission" is the model
confidently extracting a *real* concept the benchmark scoped elsewhere or did not
keep — a selection/scope disagreement, not an invention.

### Diagnosis — 252 residual events (126 FP + 126 FN)

| Bucket | FN | FP | Events | Share |
| --- | ---: | ---: | ---: | ---: |
| assertion convention (Certainty/Negation) | 20 | 20 | 40 | 15.9% |
| granularity (epilepsy lineage altitude) | 9 | 9 | 18 | 7.1% |
| related-family (adjacent seizure-type/epilepsy) | 20 | 20 | 40 | 15.9% |
| **convention-bound subtotal** | **49** | **49** | **98** | **38.9%** |
| genuine (grounded miss / grounded over-emission) | 77 | 77 | 154 | 61.1% |

Strict convention-bound (attribute + altitude only): **23.0%**. Including
related-family adjacency: **38.9%**.

### SeizureFrequency — 106 residual events (56 FP + 50 FN)

| Bucket | FN | FP | Events | Share |
| --- | ---: | ---: | ---: | ---: |
| state convention (active / seizure-free / unknown) | 10 | 10 | 20 | 18.9% |
| generic↔named ownership | 6 | 6 | 12 | 11.3% |
| **convention-bound subtotal** | **16** | **16** | **32** | **30.2%** |
| genuine (grounded miss / grounded over-emission) | 34 | 40 | 74 | 69.8% |

Convention-bound: **30.2%**.

---

## Part II — What it means (the oracle ceiling)

The decomposition refutes the *strong* form of the convention hypothesis floated
in the architecture critique ("most of the gap is convention noise, so 0.658 is
already the clinical ceiling"). It is not most. The **majority** of both
residuals is concept-level — genuine grounded misses and grounded
over-emissions, not attribute/altitude slips.

But the more useful question is the **oracle ceiling**: if a perfect projection
layer resolved *every* convention disagreement on both the precision and recall
side, what F1 would each family reach? (Each resolved pair turns one FP and one
FN into a TP.)

| Family | base | +attribute | +altitude | +family | crosses 0.8? |
| --- | ---: | ---: | ---: | ---: | :---: |
| **Diagnosis** | 0.658 | 0.713 | 0.737 | **0.791** | **No** |
| **SeizureFrequency** | 0.721 | 0.774 (+state) | **0.805** (+ownership) | — | **Yes** |

This is the headline, and it **splits the two families that the architecture
report lumps together as "the hard ones":**

- **SeizureFrequency is convention-bound and reachable.** Its entire gap to `0.8`
  *is* the state + ownership convention. An oracle that decides active-rate vs
  seizure-free vs unknown correctly, and resolves generic-vs-named ownership,
  reaches **0.805** — just over the gate. The implication for the next loop is
  precise: the work is **deterministic state/ownership projection**, not more
  clinical prompting. The signal needed ("is this phrase a rate, a zero, or
  unquantified, and does the generic or the named type own it?") is a small,
  finite decision table, exactly the shape that worked for Medication and
  Investigations. SF v0.6 should be built as a state-projection rule, and it has
  a real chance.

- **Diagnosis is not reachable at 0.8 by convention alignment.** Even an oracle
  that resolves every Certainty/Negation disagreement, every epilepsy-lineage
  altitude slip, **and** every adjacent-family specificity choice reaches only
  **0.791** — below the gate. The binding residual is the 154 grounded
  concept-level events: the model confidently emits clinically real but
  out-of-scope concepts (generic `epilepsy` ×52, `tonic clonic seizures` ×26 over-
  emissions) and misses specific gold types (`focal epilepsy`, `secondary
  generalised`) that carry no related predicted concept in the letter. These are
  not fixable by more reject-prompts without collateral recall loss — the
  combined-verifier collapse (Investigations 0.786→0.496) already demonstrated
  that suppressing confident grounded emissions destroys the family. **0.8 on
  Diagnosis is very likely unreachable by legitimate means on this benchmark
  target.**

Two further cautions tighten the read:

1. **The oracle is itself an over-estimate of what is reachable.** It assumes the
   convention can be fit perfectly on unseen letters. The architecture report's
   own central finding — every dev25 winner collapsed on dev140 (Diagnosis
   0.837→0.616, SF 0.831→0.602) — says convention-fitting does **not** transfer.
   So the real reachable numbers sit *below* 0.791 / 0.805, not at them.

2. **`0.8` is a benchmark-F1 gate, and the last mile is increasingly projection
   engineering.** The SF candidate already reaches 0.805 only with hand-added
   `benchmark_format` lexicon variants. Closing SF's convention gap means more of
   the same. That is legitimate *if* labeled as projection and held out — but it
   is convention coverage, not extraction quality, and should be reported on the
   semantic layer separately (the scorer already supports this).

---

## Part III — Cross-check: the two solved families, and a universal floor

To test whether Medication and Investigations cleared `0.8` because their
residual is structurally easier — rather than by lucky convention alignment — the
same decomposition was run on their best candidates
(`build_exectv2_convention_residual_solved_families.py`, validated: reconstructed
F1 0.817 / 0.872). The "convention" bucket here is component-attribute
disagreement (same drug / same modality on both sides, different
dose/frequency/regimen or performed/result/type); "genuine" is identity present
on only one side.

| Family | F1 | Gold | Miss rate (FN/gold) | Over-emit rate (FP/pred) | **Grounded over-emit (genuineFP/pred)** | Evidence-valid |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Investigations | 0.872 | 136 | 12.5% | 13.1% | **8.0%** | 99.3% |
| Prescription | 0.817 | 193 | 13.5% | 22.7% | **20.4%** | 97.9% |
| SeizureFrequency | 0.721 | 187 | 26.7% | 29.0% | **20.7%** | 100% |
| Diagnosis | 0.658 | 369 | 34.1% | 34.1% | **20.9%** | 99.5% |

The cross-check produced the single most important finding in this analysis, and
it is **not** the one the convention hypothesis predicted:

**The confident grounded over-emission rate is ~20% in three of the four families
— solved and unsolved alike.** Prescription clears `0.8` while over-emitting
grounded, out-of-scope concepts at *the same ~20% rate* as Diagnosis and SF. The
verifier/gate machinery has not moved this floor in any family except
Investigations (whose target is small and bounded enough that even over-emission
stays low). So the "confident over-emission wall" named in the architecture
report is **universal**, not a property of the hard families.

What actually separates solved from unsolved is **recall, not over-emission.**
The component-table families (drug regimen, modality result) have *enumerable*
targets, so the model misses far fewer of them — Prescription 13.5% / Investigations
12.5% miss, versus SF 26.7% / Diagnosis 34.1%. Prescription's high recall (0.865)
carries its F1 over `0.8` *despite* a Diagnosis-level over-emission rate. This
sharpens the report's "component-table tasks are easier" claim into a mechanism:
they are easier on the **recall** axis because the target is closed, not because
they escape the over-emission wall.

Two consequences:

- The ~20% grounded over-emission floor is the real shared ceiling. It is
  grounded (not fabrication) and resisted the whole verifier/gate program, which
  is strong evidence it is a benchmark **annotation-scope** disagreement
  (the model emits a real concept the annotators did not keep on that entity),
  not an extraction defect. Attacking it harder with reject-prompts is the move
  the combined-verifier collapse already refuted.
- Diagnosis is the worst-placed family on *both* axes: ~21% grounded
  over-emission **and** the highest miss rate (34%), on the largest target (369
  golds). This is why its convention-oracle (0.791) cannot reach the gate — even
  perfect convention alignment leaves both a recall hole and the universal
  over-emission floor.

## Part IV — Recommended revision to the next plan

The architecture report's plan ("Diagnosis gate v0.2 with more reject labels; SF
adjudicator v0.6; reassemble; then freeze") treats both families as the same
local-gradient problem. The decomposition says they are not:

1. **SeizureFrequency — continue, but reframe v0.6 as state projection.** The gap
   is a 30%-of-residual, ~0.084-F1 convention slice with a clean oracle at 0.805.
   Build it as a deterministic active/seizure-free/unknown + generic/named
   ownership decision table over the adjudicator's candidate spans, not as more
   prompt prose. **Predeclare the convention rules and hold out before claiming
   the cross.** This is the highest-leverage remaining key-family move.

2. **Diagnosis — stop chasing 0.8; characterize and accept ~0.66–0.74.** The
   oracle proves the gate is out of reach by convention alignment. The honest
   deliverable is the decomposition itself: ~99% grounded, ~23% pure attribute
   convention, the balance a confident grounded scope disagreement with the
   annotation. Report Diagnosis on the **semantic / clinical-recovery layer**
   (concept-only F1 0.713, which the oracle confirms is near the real concept
   ceiling) and state plainly that benchmark-F1 0.8 is a target-construction
   artifact for this entity, mirroring the Gan strand's acceptance of 0.842 as a
   genuine ceiling rather than chasing 0.90.

3. **Before any reassembly, compute the same decomposition on the two *solved*
   families.** Medication (0.817) and Investigations (0.872) cleared with one
   verifier each; confirming their residual is also grounded (not lucky
   convention alignment) would validate that the component-table families are
   structurally easier, not just better-tuned — strengthening the report's
   central structural claim.

---

## Claim language

Supported:

> Across the two below-target ExECTv2 key families, ~99% of the residual is
> grounded in real letter text (zero fabrication). 23% (Diagnosis, attribute +
> altitude) and 30% (SF, state + ownership) of residual events are pure
> annotation-convention disagreements over a concept both sides located; the
> remainder is grounded selection/scope disagreement, not recall failure.

Supported:

> An oracle that resolves every convention disagreement reaches F1 0.805 for
> SeizureFrequency (crossing 0.8) but only 0.791 for Diagnosis (below 0.8). The
> two "hard" families are structurally different: SF's gap is a reachable
> convention-projection problem; Diagnosis's gap is a confident grounded
> over-emission wall that convention alignment cannot clear.

Supported:

> The confident grounded over-emission rate is ~20% in three of four key families
> (Prescription, SF, Diagnosis), independent of whether the family clears `0.8`.
> The verifier/gate program did not move this floor; it is an annotation-scope
> disagreement, not an extraction defect. Solved families clear `0.8` on the
> recall axis (enumerable targets, low miss rate), not by escaping over-emission.

Not supported:

> Diagnosis can reach benchmark-F1 0.8 on dev140 with further verifier/gate
> iteration.

> Medication and Investigations cleared target by avoiding the over-emission
> failure mode. (Prescription over-emits at Diagnosis-level rates; it clears on
> recall.)

---

## Artifacts

- Driver (unsolved families): `experiments/build_exectv2_convention_residual_decomposition.py`
- Driver (solved families cross-check): `experiments/build_exectv2_convention_residual_solved_families.py`
- Results: `experiments/exectv2_convention_residual_decomposition_dev140_20260618.json`,
  `experiments/exectv2_convention_residual_solved_families_dev140_20260618.json`
- Inputs (unchanged):
  `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl`,
  `experiments/exectv2_hybrid_sf_state_adjudicator_v05_dev140_gpt41mini_20260618.jsonl`
- Reconstruction validated against:
  `experiments/exectv2_diagnosis_reconciler_v01_residual_ledger_dev140_20260618.json`,
  `experiments/exectv2_sf_state_adjudicator_v05_residual_ledger_dev140_20260618.json`
- Parent report:
  `docs/research/exectv2_key_entity_architecture_research_report_2026-06-18.md`
