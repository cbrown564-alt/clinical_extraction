# Gan 2026 Research Canon — Closeout, Architecture & The Wall

Last updated: 2026-07-06

**Absorbs:** [`../research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`](../research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md),  
[`../research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md`](../research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md),  
[`../research/gan2026/error_analysis/gan2026_failure_mode_comparison_table_2026-06-12.md`](../research/gan2026/error_analysis/gan2026_failure_mode_comparison_table_2026-06-12.md),  
[`../research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md`](../research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md).

**Machine scorecard:** [`experiments/gan2026_reliability_master_scorecard_2026-06-17.md`](../../../experiments/gan2026_reliability_master_scorecard_2026-06-17.md)  
**Experiment narratives:** [`docs/experiments/gan2026/`](../experiments/gan2026/)  
**Paper claims:** [`10_paper_provenance.md`](10_paper_provenance.md) C3, C5

---

## Frozen recommendation (unchanged)

**Architectures in one line:** **SE** = LLM structured-event extraction + deterministic
render (`GPT-4.1-mini`). **V12** = same stack + full `GPT-4.1` fresh-evidence reasoner
(3-trace corroboration). **Floor** = rules-only deterministic baseline.

| Role | Architecture | test450 Purist[^purist] | Status |
| --- | --- | ---: | --- |
| **Production / go-forward** | Single GPT structured-event (mini) | **364/450 = 0.809** | Promoted |
| **Ceiling comparator** | V12 fresh-evidence hybrid (full gpt-4.1 reasoner) | **379/450 = 0.842** | Best holdout; +15 rows over SE |
| **Floor** | Deterministic rules_only | 343/450 = 0.762 | Controlled variable |

No further 0.90 optimization on current model family. Forward implementation focus
moved to ExECTv2. **Holdout row-level inspection blocked** — aggregate citation only.

[^purist]: **Purist** = strict 12-band label match on rendered seizure-frequency
category; **Pragmatic** = coarser boundary-band match (six `BOUNDARY_BANDS`). See
[`gan2026_rule_register.md`](../design/gan2026_rule_register.md) §1.4.

---

## Architecture arc (ten variants, five findings)

### Promoted vs rejected (validation → test450)

| Verdict | Mechanism | Why |
| --- | --- | --- |
| **Promoted** | LLM structured-event + deterministic render | Source-near events; 0.881 val / 0.809 test; smallest val→test drop |
| **Rejected** | Direct labeler | 329 correct→wrong vs 26 wrong→correct on val — over-reads history |
| **Rejected** | Hybrid rules+LLM adjudicator | Weaker than SE |
| **Rejected** | Multi-component staged assembly | Clean but low coverage (357/450) |
| **Rejected** | Three-agent exact consensus | Didn't transfer to holdout |
| **Rejected** | V1–V11 agentic ladder | Broad regresses |
| **Ceiling only** | V12 fresh-evidence reasoner | +15 test rows; reasoner needs 3-trace corroboration |

### Five mechanism-level findings

1. **Direct-label prediction is unsafe** under Purist scoring — use LLM output as candidates only.  
2. **Structured-event extraction was the breakthrough** — inspectable intermediate state suppresses over-reading.  
3. **Hybrid/ensemble/guard buys little** — guard near-inert (+6/750); most lift is disciplined replace with 3-trace agreement.  
4. **Corroboration is non-linear** — GPT-only reasoner −51; GPT+DeepSeek −30; full 3-trace +21.  
5. **Provenance caveat** — V12 reasoner on full gpt-4.1; chosen SE pass **mini-verified** on test450.

---

> **The Wall (plain language)**
>
> On the hardest Gan seizure-frequency rows, the model is **confidently wrong**: it
> outputs a specific rate when *unknown* is correct, or stays at *unknown* when a rate is
> warranted. Nothing the system can observe at run time reliably tells those cases apart —
> only the hidden gold label can. That is why ~**0.842** Purist on test450 is treated as a
> **ceiling prior**, not a knob to tune toward 0.90.

## The Wall (reliability headline)

**Definition:** On binding residual rows, the signal separating withhold-to-unknown
from emit-rate is **absent** from every forward-observable feature; only hidden gold
separates them. ~0.842 is a **prior**, not a tuning target.

| Program | Role | Outcome |
| --- | --- | --- |
| **P0.2** risk–coverage | External Risk Score ordering | Strongest leg: cross-model agreement; self-confidence degenerate |
| **P2.1** semantic entropy | Multi-sample probe at residual | H0 publishable: over-reading is **confident** (entropy flat) |

**Irreducible residual:** 11 validation rows, 8/11 `band_unknown` — no Purist-correct
component, no route without gold.

**Distinct from ExECT gold-quality ceiling** — Wall is model/confident over-read on Gan
residual; gold-quality is metric/annotation artifact on ExECT SF/Dx. Mechanisms
converge narratively but live on disjoint slices ([`10_paper_provenance.md`](10_paper_provenance.md)).

---

## Cross-task transfer (C3)

Wall-transfer probe on ExECT SF: **6/9 checks pass**; External Risk AUROC 0.764;
binding-slice abstention AUROC 0.676 (below 0.70 bar). **Suggestive, not definitive**
(small-n: 5 over-reads vs 25 withholds dev140).

Source: `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`.

---

## Evaluation discipline (C5 exemplar)

Demonstrated instances (not asserted):

- Held-out-family CV caught v0.6 overfit before holdout  
- v0.7 test450 regression (−106 rows) caught by protocol  
- Gate 1–4 frozen promotion ladder with explicit stop rules (table below)  
- Predeclared adversarial / hard-slice panels  

| Gate | Plain description | Pass authorizes |
| --- | --- | --- |
| **Gate 1** | Validation hard-slice audit — no brittle regressions in known weak families (changed-label precision, zero correct→wrong) | Gate 2 only; not holdout |
| **Gate 2** | Synthetic/source-near stress panels — selector or mechanism behaves on adversarial component states | Gate 3 only; not holdout |
| **Gate 3** | Test source-symmetry preflight — locked-test components match validation roles; artifacts hash-pinned | Gate 4 only, with explicit user authorization |
| **Gate 4** | Locked test450 aggregate audit — frozen holdout readout; no row-level failure inspection for development | Recording final-evaluation evidence only |

Gate 4: consensus/fresh constrained **failed** holdout; exact-source Gate 4 passed
**aggregate only** (359/450, precision 0.60). Consensus/fresh selector **CUT**
(`docs/research/consensus_fresh_selector_fate_2026-06-27.md`).

---

## Three architecture families (experimental ontology)

From [`../research/contribution_thesis.md`](../../research/contribution_thesis.md):

- **`rules_only`** — deterministic prediction-bearing interpretation (floor 0.762 test450)  
- **`llm_only`** — LLM owns clinical fact; adapters format-only (direct labeler weakest)  
- **`hybrid`** — explicit split: who extracts, who selects, who renders  

Promoted Gan candidate is **staged hybrid** (ADR 0009), not LLM-first V1 doc.

Deterministic canonical fourth stage: **Evidence Trace Check** (ADR 0014) — not hybrid
`Verify` vocabulary.

---

## Selection precedence (canonical rules)

Renamed **R1/R2** (formerly C1/C2 in this canon) to avoid collision with paper claims
C1–C5 ([`10_paper_provenance.md`](10_paper_provenance.md)).

- **R1:** Current positive rate supersedes coexisting current seizure-free (ADR 0016)  
- **R2:** Ontology over-inference guard is graph-path-only (ADR 0017)  

Operative rules: `docs/design/gan2026_rule_register.md`, `gan2026_resolve_label_spec.md`.
Code and ADR comments may still say “C1/C2” for the same rules.

---

## What never graduated to this canon (pointers)

| Topic | Where detail lives |
| --- | --- |
| validation750 verifier v6 iteration (~31 docs) | [`docs/experiments/gan2026/VALIDATION750_CANON.md`](../experiments/gan2026/VALIDATION750_CANON.md) |
| RQ1–RQ10 answers | [`docs/experiments/gan2026/COMPONENT_MECHANICS_CANON.md`](../experiments/gan2026/COMPONENT_MECHANICS_CANON.md) |
| Row-level Gan error analysis | `docs/research/gan2026/../research/gan2026/error_analysis/` + closeout Part III |
| Agentic redo (2026-07-01) | ExECT SF hard panel — task-dependent; see brief crosswalk |

---

## Related reading

- [`docs/design/reliability_thesis.md`](../design/reliability_thesis.md)  
- [`docs/design/gan2026_saturated_validation_protocol.md`](../design/gan2026_saturated_validation_protocol.md)  
- [`04_scoring.md`](04_scoring.md) — ExECT scoring contrast  
- [`docs/THREAD_MAP.md`](../THREAD_MAP.md) T1
