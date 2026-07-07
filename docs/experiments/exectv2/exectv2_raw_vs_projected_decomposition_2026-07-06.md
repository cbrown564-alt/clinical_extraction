# Raw-vs-projected decomposition — results

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `rx_dx_sf_inv_raw_vs_projected_decomposition_2026-07-06` — **RESOLVED**
(the deterministic contribution to the cited `clinical_headline` is now stated
per family; attribution discipline met; the dspy "bridge-inflation" critique is
preempted by surfacing the decomposition rather than hiding it).
Driver: `experiments/exectv2_raw_vs_projected_decomposition_2026-07-06.py`
(zero LLM calls; reads registry-tracked assembly artifacts).
Umbrella plan: item 5 of `docs/plans/predecessor_synthesis_followups_2026-07-06.md`.

## Headline

**How much of the cited 0.9189 (dev140) / 0.8680 (full-200) `clinical_headline`
is raw producer emission vs deterministic lens vs benchmark bridge?** The answer
is **family-specific**, and the family specificity is the sharper finding:

| Surface (dev140 overall) | F1 | share of the cited headline |
| --- | ---: | --- |
| **RAW** (producer-lane emission, pre-lens) | 0.8475 | 92.2% |
| **POST-LENS** (+ deterministic reconciliation) | 0.8913 | 97.0% |
| **HEADLINE** (+ bridge, de-dup, CUI projection) | 0.9189 | 100% |

The deterministic layer (lens + bridge together) contributes **+0.0714 dev140 /
+0.0563 full-200** to the cited headline — real and non-trivial, but far smaller
than dspy's flat "~24-point bridge contribution." **It is not a single bridge
effect.** It splits cleanly by family into two distinct mechanisms (Dx = lens;
SF = bridge), with two families (Rx, Inv) getting zero lift. Surfacing this is
the attribution-discipline deliverable the research protocol requires: an
LLM-first claim must show what the model selected before deterministic semantic
repair, and this decomposition is that disclosure for the system-wide headline.

## The numbers

### dev140 (cited overall `clinical_headline` = 0.9189)

| Family | RAW | POST-LENS | HEADLINE | R→P (lens) | P→H (bridge) | R→H (total) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 0.7790 | 0.8984 | 0.8984 | **+0.1194** | +0.0000 | +0.1194 |
| SeizureFrequency | 0.7836 | 0.7836 | 0.9080 | +0.0000 | **+0.1244** | +0.1244 |
| Prescription | 0.9615 | 0.9615 | 0.9615 | +0.0000 | +0.0000 | +0.0000 |
| Investigations | 0.9132 | 0.9132 | 0.9132 | +0.0000 | +0.0000 | +0.0000 |
| **OVERALL** | **0.8475** | **0.8913** | **0.9189** | **+0.0438** | **+0.0276** | **+0.0714** |

### full-200 (cited overall `clinical_headline` = 0.8680)

| Family | RAW | POST-LENS | HEADLINE | R→P (lens) | P→H (bridge) | R→H (total) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 0.7818 | 0.8546 | 0.8546 | **+0.0728** | +0.0000 | +0.0728 |
| SeizureFrequency | 0.6592 | 0.6592 | 0.7842 | +0.0000 | **+0.1250** | +0.1250 |
| Prescription | 0.9278 | 0.9278 | 0.9278 | +0.0000 | +0.0000 | +0.0000 |
| Investigations | 0.9213 | 0.9213 | 0.9213 | +0.0000 | +0.0000 | +0.0000 |
| **OVERALL** | **0.8117** | **0.8383** | **0.8680** | **+0.0266** | **+0.0297** | **+0.0563** |

> The headline column reproduces the cited 0.9189 / 0.8680 **exactly** (probe
> self-check `PASS` on both splits) — these are not re-derived estimates; they
> are the registry-tracked P7 treatment runs' own `score_ladder` surfaces
> (`raw_lane_score` / `materialized_surfaces.residual_benchmark_added` /
> `headline_target`), read out and packaged. Per-family precision/recall/tp/fp/fn
> for every cell are in the JSON artifact.

## Per-family mechanism (the attribution story)

The lift does not come from one place. It splits by family into two clean
mechanisms, with two families getting none:

1. **Diagnosis — the lift is the deterministic dictionary lens (+0.1194 dev / +0.0728 full).**
   Post-lens already equals headline (P→H = +0.0000). The lens drops the generic
   "epilepsy" anchor (which over-credits any epilepsy letter), rewrites benchmark
   conventions to their canonical forms, and adds a residual + generic-epilepsy
   companion. This is a **deterministic-reconciliation contribution**, not a
   bridge effect — and it is exactly the kind of "deterministic semantic repair"
   the attribution rule is about. The raw Dx emission (0.7790 dev / 0.7818 full)
   is the number to state alongside the headline for any LLM-first Dx claim.

2. **SeizureFrequency — the lift is the CUI-projection bridge + de-dup (+0.1244 dev / +0.1250 full).**
   Post-lens equals raw (R→P = +0.0000); the **entire** SF lift lives in stage 3
   (P→H). SF's frequency-type key uses CUI as seizure-type identity, so the CUI
   bridge materially changes which SF facts match gold. **This is the
   projection-heavy number dspy warns about** ("benchmark-aligned numbers are
   real and useful, but the open work is raw ceilings, not stack polishing").
   The raw SF emission (0.7836 dev / 0.6592 full) — especially the full-200
   0.6592 — is the uncomfortable number this decomposition surfaces. It must be
   stated alongside the headline.

3. **Prescription — no lift (+0.0000 both splits).** Raw == headline. This is the
   deterministic-owned ceiling item 4 confirmed from the other direction: the
   producer's emission carries through the assembly unchanged, so the headline
   *is* the raw number. (Item 4 showed the deterministic extractor alone
   reproduces the cited 0.9615 / 0.9278 exactly; this row shows nothing is added
   downstream either.)

4. **Investigations — no lift (+0.0000 both splits).** Raw == headline. The
   hybrid arbitration's output carries through unchanged.

**Combined read.** Two families (Dx, SF) account for ~100% of the deterministic
lift; two families (Rx, Inv) account for none. The two lifting families lift via
*different* deterministic stages (Dx = lens, SF = bridge). So there is no single
"the deterministic layer contributes X" number that is honest — the honest
statement is per-family, and it is what this table gives.

## The caveat that must be footnoted (not hidden)

**"RAW" is post-producer, not raw vanilla-LLM.** The dev140 producers are
themselves hybrid routes, not single calls:

| Family | Producer (dev140) | Model | Lane character |
| --- | --- | --- | --- |
| Diagnosis | `exectv2_hybrid_diagnosis_reconciler_v01` | gpt-4.1-mini | hybrid LLM reconciler |
| SeizureFrequency | `exectv2_hybrid_sf_union_arbitration_v08` | gpt-4.1-mini + deterministic | hybrid union arbitration |
| Investigations | `exectv2_llm_investigations_arbitration_v02` | gpt-4.1-mini | LLM verifier + deterministic arbitration |
| Prescription | `exectv2_deterministic_prescription_repair_v03` | none | fully deterministic |

So "RAW" = "the producer-lane's selected facts as emitted to the assembly" — the
prediction-bearing layer's output before deterministic lens/bridge. This is the
surface the research-protocol attribution rule asks for ("what the model selected
before deterministic semantic repair"), and it is the honest upper bound on the
LLM/producers' direct contribution to the headline. **But it is not
commensurable with dspy's "raw S1" (a single vanilla call).** dspy's literal
68.6% → 92.3% (+24pp) figure does not transfer; what transfers is the *shape*
(projection-bearing headline sits materially above raw emission) and the *policy*
(state the raw number alongside the headline). The per-family shape above is the
commensurable contribution.

## Comparison to dspy's bridge-inflation critique

dspy's finding: raw S1 extraction 68.6% micro-F1 → 92.3% after benchmark bridges
(+~24pp), "too large to call raw extraction 'solved.'" dissertation-recursive
reinforces this ("scorer was materially broken for the first half of the
project").

**What transfers:** the *shape*. Our headline (0.9189 dev / 0.8680 full) sits
materially above raw (0.8475 / 0.8117) — +0.0714 / +0.0563 overall. The critique's
*policy* (state the raw number; do not present a projection-bearing headline as
raw extraction) applies, and this decomposition is our compliance.

**What does not transfer:** the *magnitude and the mechanism*. dspy's +~24pp is a
single flat bridge effect; ours is +0.0714 / +0.0563 split across two families by
two different deterministic stages. dspy's "raw" is a single vanilla call; ours is
a post-producer (often hybrid) emission. So:
- We **do not** claim "raw extraction is solved" — the raw SF 0.6592 full-200 in
  particular is not a solved number, and this doc states it.
- We **do** claim the projection contribution is bounded, family-attributed, and
  disclosed — which is the strongest available defense against the critique. The
  deterministic layer is a *contribution* (real, +0.0714 / +0.0563), not a fig
  leaf; the manuscript must show it, not hide it.

## Implications for the manuscript

1. **State the raw number alongside the headline, per family.** The manuscript's
   §4 headline table should carry a raw-emission column (or a clearly-cited
   companion table) so a reader sees Dx 0.7790→0.8984, SF 0.7836→0.9080,
   Rx/Inv unchanged. Hiding the raw column inherits dspy's critique; surfacing it
   preempts the critique.
2. **Attribute the lift by family and stage, not as one number.** "The
   deterministic layer contributes +0.0714" is true but misleading; "Dx lift is
   the dictionary lens (+0.1194 dev); SF lift is the CUI-projection bridge
   (+0.1244 dev); Rx/Inv get no lift" is the honest, mechanism-bearing
   statement. This is the §4.2 attribution paragraph.
3. **Footnote the "raw = post-producer" caveat.** Our raw is not dspy's raw;
   state the commensurability limit explicitly so the comparison is not
   over-read.
4. **The SF full-200 raw (0.6592) is the uncomfortable number.** It is more
   reason to state it, not less — it localizes where the projection layer is
   doing the most work and where raw extraction is genuinely not solved. This is
   consistent with the existing SF gold-quality-ceiling framing (SF §canonical
   row analysis): the gap is partly gold-quality, partly projection, and the raw
   number makes the projection share visible.

## Drop-in §4 paragraph

> The cited `clinical_headline` (0.9189 dev140 / 0.8680 full-200) is a
> de-duplicated, projection-bearing recovery surface. To attribute it honestly
> we decompose it per family into raw producer emission, post-deterministic-lens,
> and post-bridge headline (Table X). The deterministic layer contributes
> +0.0714 (dev140) / +0.0563 (full-200) overall — real, but smaller than the
> ~24-point bridge contribution reported in comparable stacked-baseline
> decompositions, and split cleanly by family: Diagnosis lift (+0.1194 dev) is
> the deterministic dictionary lens (convention rewriting, generic-anchor
> removal); SeizureFrequency lift (+0.1244 dev) is the CUI-projection bridge and
> de-duplication, which materially changes seizure-type identity matching;
> Prescription and Investigations receive no lift (raw == headline). Raw
> producer emission — the prediction-bearing layer's output before deterministic
> semantic repair — is 0.8475 (dev140) / 0.8117 (full-200) overall; the lowest
> raw family is SeizureFrequency (0.7836 dev / 0.6592 full), consistent with its
> gold-quality-ceiling framing. (Note: our "raw" is the hybrid producer lane's
> emission, not a single vanilla call, and is therefore not directly
> commensurable with single-call raw-ExECT figures in prior work; the
> per-family shape, not the absolute gap, is the commensurable contribution.)

## Limitations and honest caveats

- **This is a single-system decomposition, not a cross-system claim.** It
  decomposes the v08 hybrid assembly's headline. Other architectures (LLM-only,
  GEPA) have different raw/headline gaps and would need their own decomposition.
- **Raw is post-producer.** See §The caveat that must be footnoted. The Dx/SF/Inv
  producers are hybrid routes; only Rx is fully deterministic. The raw column is
  the prediction-bearing layer's emission, not a model-only ceiling.
- **The lens-vs-bridge attribution is stage-based, not component-isolated.**
  "POST-LENS" bundles the full deterministic reconciliation pass
  (`residual_benchmark_added` surface); it is not a per-lens-rule ablation. The
  finer component-off decomposition already exists
  (`experiments/exectv2_component_off_replay_dev140_20260626.md`) and is
  complementary — this doc is the family × stage framing for the manuscript;
  that one is the per-component delta.
- **full-200 is aggregate-only** per claim_policy. The per-family full-200 cells
  are aggregate tp/fp/fn (no row-level inspection); the source JSON contains
  only aggregates, so no row-level boundary is crossed.
- **This probe reads registry-tracked artifacts; it does not re-score.** The
  three surfaces were already computed through the same family scorers in the
  P7 treatment runs. The probe's self-check (headline column reproduces
  0.9189 / 0.8680) confirms it read the right artifact.

## What this is NOT

- Not a claim that raw extraction is "solved" — raw SF full-200 is 0.6592, which
  is not solved.
- Not a claim that the deterministic layer is a fig leaf — it contributes
  +0.0714 / +0.0563, which is real and must be shown.
- Not a re-run of the assembly. The cited numbers are the registry-tracked P7
  treatment runs; this probe packages their existing `score_ladder` surfaces.
- Not commensurable with dspy's single-call raw figure — see the caveat.

## Artifacts / Provenance

- Driver: `experiments/exectv2_raw_vs_projected_decomposition_2026-07-06.py`
  (zero LLM calls; reads registry-tracked artifacts).
- JSON: `experiments/exectv2_raw_vs_projected_decomposition_2026-07-06.json`
  (per-family × {raw, post-lens, headline} × {f1, precision, recall, tp/fp/fn} ×
  {dev140, full200}; overall rows; self-check status).
- Source artifacts (registry-tracked, the runs that produced the cited
  0.9189 / 0.8680):
  `experiments/exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_20260702.json`,
  `experiments/exectv2_holistic_finding_assembly_v08_full200_p7_treatment_20260702.json`
  (registry ids `..._dev140_p7fix_gpt41mini_20260702`,
  `..._full200_p7fix_gpt41mini_20260702`).
- Score-ladder surface keys read: `raw_lane_score` (RAW),
  `materialized_surfaces.residual_benchmark_added` (POST-LENS),
  `headline_target` (HEADLINE) — all computed through the same family scorers
  (`score_prescription_components`, `score_frequency_state`,
  `score_investigations_components`, `score_concept_identity`).
- Complementary per-component decomposition:
  `experiments/exectv2_component_off_replay_dev140_20260626.md`.
- Prescription-specific analogue (item 4):
  `docs/experiments/exectv2/prescription/exectv2_medication_no_model_oracle_2026-07-06.md`.
- Umbrella: `docs/plans/predecessor_synthesis_followups_2026-07-06.md` (item 5).
- Split discipline: dev140 + full-200, both reading registry-tracked aggregate
  scores — no live predictions, no row-level full-200 inspection. Cost: 0 LLM
  calls.
