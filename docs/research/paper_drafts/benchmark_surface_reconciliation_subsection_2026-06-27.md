# Benchmark-Surface Reconciliation
*Paper subsection draft — 2026-06-27*
*Evidence validity: validation-only (`dev140`, 140-letter development split) + frozen aggregate `full-200` (200-letter aggregate split) four-family read*
*Row-inspection policy: aggregate_only_no_full200_or_holdout_row_level_inspection*
*Consumes: M1 (benchmark_surface_reconciliation_2026-06-27.md) + I1 (sf_registry_legacy_delegation_audit_2026-06-27.md)*

---

## 4.x  Benchmark-Surface Reconciliation

### 4.x.1  The Two Surfaces and Why They Diverge

ExECT multi-entity phenotyping (ExECTv2; Fonferko-Shadrach 2024) reports performance on
two distinct scoring surfaces that measure different things and cannot be directly compared:

**Clinical-headline surface** (`clinical_headline`—Diagnosis, SeizureFrequency,
Prescription, and Investigations; four-family scorer). Matches entity
type, normalized phrase, and clinical attributes; disregards raw character offsets and
CUI codes. This is the surface used for the headline F1 figures throughout §4.2 (GPT-4.1-mini
dev140 0.9155; full-200 0.8356–0.8566 across models).

**Published-benchmark surface** (nine-entity CUI + attribute-bundle scorer). Requires
exact phrase reproduction together with full attribute bundles and CUI codes, and was
the success criterion stated in the research thesis (§7: "beat the ExECTv2 per-item /
per-letter F1 benchmark, `0.87` / `0.90`"). These two numbers originate from the
published Gan et al. pipeline, which was tuned specifically to reproduce CUI codes and
attribute bundles against the gold annotation.

The surfaces diverge for a principled reason: the gold character-offset annotations
were made against the original unprocessed clinical letters; subsequent spelling
correction altered the text without updating the offsets (thesis §5). Scoring on raw
spans would therefore systematically penalise correct extractions whose phrase
boundaries were shifted by the correction. The project therefore scores on
entity-plus-label, not on offsets — a methodology consistent with the benchmark
paper's own inter-annotator agreement protocol, which also disregarded CUIs and
compared on phrase selection and attribute classification. The consequence is that
the published pipeline's offset-tuned number is not reproducible on the corrected
surface; no pipeline operating on corrected text can be directly compared to the
`0.87` / `0.90` figures without acknowledging this break.

### 4.x.2  The Like-for-Like Number

On the published-benchmark surface (nine entities, per-item and per-letter F1 with
CUI and full attribute-bundle strictness), the best-of-dev140 like-for-like read is:

| Surface | Per-item F1 | Per-letter F1 | vs. paper (0.87 / 0.90) |
|---------|------------:|---------------:|--------------------------|
| Paper (published, full 200) | 0.87 | 0.90 | — |
| Best-of dev140 (rules + hybrid Inv) | **0.3877** | **0.6972** | −0.48 / −0.20 |
| Deterministic-only dev140 | 0.3687 | 0.6747 | −0.50 / −0.23 |
| All-hybrid dev140 | 0.3100 | 0.6454 | −0.57 / −0.25 |

*Source: `experiments/exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json`;
scorer: exact normalized phrase + all attributes + CUI, nine entities, dev140 (140
letters). Evidence validity: validation-only — not a holdout or full-200 estimate.*

The `0.3877` per-item figure is approximately 45% of the paper headline. The full-200
like-for-like equivalent on the published-benchmark surface has not been computed under
the current freeze protocol; the full-200 tables in §4.2 are four-family
`clinical_headline` only and are not comparable to this number.

This reconciliation supersedes the `exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12.md`
checkpoint, which was explicitly labelled a 60-row exploratory read and not a frozen
audit conclusion. That document should not be cited as evidence for claims about the
published-benchmark gap; the figures above from the 2026-06-18 frozen aggregate read
replace it.

### 4.x.3  What Drives the Gap: CUI / Attribute-Bundle Fidelity Engineering

The 2026-06-18 like-for-like analysis identifies the loss as concentrated in **CUI
reproduction and attribute-bundle strictness**, not in concept recall or entity
recognition. Phrase-only and semantic-recall metrics remain materially higher than the
nine-entity bundle score. For the families where the gap is largest
(Prescription, Investigations, PatientHistory), the lever is deterministic
phrase/CUI/attribute-bundle engineering: catalogued patterns that reproduce the exact
bundle structure the benchmark expects, rather than LLM adjudication.

This is closeable fidelity engineering that was deprioritised in favour of the
clinical-recovery evaluation framework. The honest paper statement is therefore:

> *We evaluate on a label-based surface because spelling correction drifted the gold
> offsets (making the offset-tuned published number non-reproducible on corrected
> text); on the comparable dev140 surface we reach 0.39 per item / 0.70 per letter;
> closing the remaining gap to the published headline requires deterministic
> phrase-and-CUI bundle engineering (CUI normalisation, full attribute serialisation,
> entity-bundle assembly per family) that was explicitly deprioritised as outside the
> clinical-recovery scope of this work.*

This framing is reviewer-proof in a way that the alternative — asserting the benchmark
surface is an artefact — is not, because the project's own analysis confirms the gap
is closeable through named, deterministic work.

### 4.x.4  Rules Beat Hybrid on the Benchmark Surface; the Inversion Is a Finding

An important and non-obvious result emerges when the benchmark surface and the
clinical-headline surface are compared across verifier configurations:

| Family | Rules benchmark item F1 | Hybrid benchmark item F1 | Benchmark winner | Hybrid clinical-recovery |
|--------|------------------------:|-------------------------:|------------------|-------------------------:|
| Investigations | 0.3220 | **0.4835** | Hybrid (+0.16) | — |
| Diagnosis | **0.3216** | 0.2834 | Rules | — |
| Prescription | **0.3020** | 0.2477 | Rules | — |
| SeizureFrequency | **0.6921** | 0.3472 | Rules (+0.34) | 0.782 (hybrid CR surface) |

*Source: `docs/research/exectv2_benchmark_surface_overall_2026-06-18.md`; dev140
validation-only; nine-entity scorer.*

For SeizureFrequency, the hybrid verifier reaches 0.782 on the clinical-recovery
surface — a substantial gain — but collapses to 0.347 on the published benchmark
surface, well below the deterministic rules baseline of 0.692. Stacking all four
hybrid verifiers lowers the nine-entity benchmark overall from 0.3687 (deterministic)
to 0.3100 (all-hybrid), a regression, even though phrase-only and semantic recall
individually improve.

This inversion — hybrid gains clinical-recovery, rules retain benchmark fidelity — is
a genuine finding about the two surfaces, not a measurement artefact. It is captured
by the `benchmark_format` component category in `definitions.yaml`: the
`residual_semantic_lens` and `headline_projection` components add four-family
headline F1 (the clinical recovery that hybrid verifiers promote) without transferring
to the published benchmark bundle scorer, which penalises anything short of exact CUI
and attribute reproduction. The quantitative split is confirmed by the component
ablation:

| Component | Category | Δ (GPT-4.1-mini dev140 v08) |
|-----------|----------|-----------:|
| `residual_semantic_lens` | `benchmark_format` | +0.0175 |
| `headline_projection` | `benchmark_format` | +0.0283 |
| **Sum (≈ headline − clinical-recovery)** | | **+0.0458** |

*Source: `experiments/exectv2_component_off_replay_dev140_20260626.json`; four-family
`clinical_headline` scorer; no model calls, replay-only.*

The benchmark-format layers add 0.04–0.15 overall F1 depending on model (largest for
Qwen 3.6 35B at +0.148), while clinical-recovery drops to as low as 0.7526 for Qwen
without those layers. The headline is not recoverable from clinical facts alone; and
LLM-enriched clinical recovery does not substitute for deterministic bundle
engineering on the published-benchmark scorer.

### 4.x.5  Full-200 Reconciliation (Four-Family Clinical-Headline)

The full-200 component-ablation read (frozen aggregate under the
`exectv2_component_off_full200_predeclaration_2026-06-26.md` protocol; preflight
passed, split=full200, row_count=200) shows format-layer contributions are stable and
smaller on full-200 than on dev140:

| Model | Headline F1 | Clinical-recovery F1 | Δ (format layers) |
|-------|------------:|---------------------:|-------------------:|
| GPT-4.1-mini | 0.8356 | 0.7922 | +0.043 |
| DeepSeek chat | 0.8566 | 0.8110 | +0.046 |
| Qwen 3.6 35B | 0.8197 | 0.7797 | +0.040 |

*Scorer: four-family `clinical_headline`, full-200 (200 letters), same-core
adjudicator stack. Evidence validity: frozen aggregate full-200, no row-level
inspection.*

The smaller delta on full-200 (~+0.04 vs ~+0.04–0.15 on dev140) is consistent with
the same-core adjudicator baking in more dictionary recovery before the format layers
operate. The clinical-recovery floor on full-200 (0.78–0.81) is materially above the
Qwen dev140 clinical-recovery (0.7526), confirming that the larger dev140 gap for
non-primary models is not a general full-200 characteristic.

These full-200 figures are four-family `clinical_headline` only. The full-200
published-benchmark nine-entity CUI score is not computed and is not claimed here.

### 4.x.6  SF-Registry Caveat for Rule-Level Benchmark Claims

Where this subsection cites specific rule families or behavioral attributions for
SeizureFrequency performance, the following caveat applies (from the 2026-06-27
SF-registry legacy delegation audit, I1):

> ExECTv2 consolidates SeizureFrequency surface rules into a single YAML-indexed
> registry (133 rule IDs across extraction, convention repair, and projection) with
> shared regex patterns and phase adapters, but clinical behavior is still split:
> convention rewrite and noise run through catalog-driven builder loops while residual
> additions and operand-format rewrites execute in legacy Stack B modules; extraction
> regex and builders remain in `rules/`; and projection logic — though relocated under
> registry builders — is orchestrated by hand-written adapters rather than
> catalog-driven dispatch.

In particular: the `convention_residual` family (`residual_all_patterns`) delegates
entirely to `_legacy_residual.py` (~905 LOC); `convention_rewrite` has five
operand-format rules still executing in `_legacy_rewrite._sf_operand_format_rewrite`;
and `projection_sf` uses no catalog-driven dispatch loop. Benchmark scores attributed
to "SF rules" therefore reflect this hybrid execution stack, not a fully
catalog-owned, audited rule set. The parity gate (`test_shadow_diff_zero_mismatches`)
covers convention rewrite only; noise, residual, and projection have no shadow-parity
CI coverage as of this audit date.

Rule-level claims (e.g., "rules beat hybrid by 0.34 on SeizureFrequency benchmark
item F1") are aggregate read-outs from the saved replay artifacts and are valid at
that aggregate level; they do not imply that individual rule attributions within the
SF stack are cleanly auditable from the catalog metadata alone.

---

## Evidence Summary

| Claim | Evidence level | Source |
|-------|---------------|--------|
| `0.3877` / `0.6972` dev140 like-for-like | Validation-only, frozen aggregate | `exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json` |
| Rules > hybrid on SF benchmark (+0.34) | Validation-only, frozen aggregate | `exectv2_benchmark_surface_overall_2026-06-18.md` |
| Format layers +0.04–0.15 on clinical-headline | Validation-only, component-off replay | `exectv2_component_off_replay_dev140_20260626.json` |
| Full-200 format-layer delta ~+0.04 | Frozen aggregate full-200 | `exectv2_component_off_replay_full200_20260626.json` |
| Offset-drift non-reproducibility reason | Design thesis | `docs/design/reliability_thesis.md` §5 |
| SF registry delegation depth | Read-only code audit | `sf_registry_legacy_delegation_audit_2026-06-27.md` |
| 60-row checkpoint superseded | Audit labeling | `exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12.md` |

---

*Writing only. No git operations. No row-level reads. No new model calls.*
*Parent task: Wave 2 workstream P1 (paper writing), closing campaign orchestration.*
