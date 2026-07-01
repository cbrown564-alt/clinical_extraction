# ExECT SF State Adjudicator Ladder Canon

Last updated: 2026-07-01

**Scope:** SeizureFrequency state-adjudicator iteration v01–v05 on dev140 (June 2026).  
**Claim boundary:** Dev140 development; `state_profile` / clinical-recovery surfaces per ADR 0037.

**Parent canons:** [`04_scoring.md`](../04_scoring.md) · [`05_ceilings_wall.md`](../05_ceilings_wall.md) · [`07_exect_plan11.md`](../07_exect_plan11.md)  
**Long tail:** 5 adjudicator reports in [`docs/experiments/exectv2/seizure_frequency/`](../../experiments/exectv2/seizure_frequency/) (stubbed)

---

## What this workstream tested

Transition from legacy SF verifier v0.4 (~0.623 dev140) to **candidate-span state
adjudication**: typed seizure-state candidates (active-rate, seizure-free, unknown)
reviewed by LLM before headline projection.

Substrate: `exectv2_llm_only_key_entities_structured_v0.5` + `openai/gpt-4.1-mini`.

---

## Adjudicator ladder (dev140 headline F1)

| Version | F1 | P | R | Gate | Notes |
| --- | ---: | ---: | ---: | --- | --- |
| Legacy SF verifier v0.4 | 0.623 | 0.591 | 0.658 | EV 0.9905 | Pre-adjudicator baseline |
| **v0.1** | 0.674 | 0.653 | 0.695 | EV 1.0000 | +0.051 vs v0.4; first clean gate |
| **v0.2** | 0.672 | 0.687 | 0.658 | EV 1.0000 | Precision↑ recall↓ — flat/worse |
| **v0.3** | 0.681 | 0.667 | 0.695 | EV 1.0000 | Unknown F1 improved |
| **v0.4** | 0.707 | 0.704 | 0.711 | EV 1.0000 | Typed metadata before LLM step |
| **v0.5** | **0.721** | 0.710 | 0.733 | EV 1.0000 | **Current numeric candidate** |

All versions remained **below 0.8** clinical-recovery target on dev140.

---

## v0.5 mechanism (canonical dev140 row)

v0.5 adds **seizure-free-anchor guidance**: separates current no-further-seizure
statements from historical best periods, driving advice, and non-seizure episodes.
Extends benchmark-format SF CUI lexicon for residual-supported phrases.

| State slice | v0.4 → v0.5 |
| --- | --- |
| Seizure-free F1 | 0.738 → **0.781** |
| Active-rate F1 | 0.746 → **0.762** |
| Unknown-state F1 | 0.525 → 0.476 (regressed) |

**Next-loop guidance (historical):** recover unknown/change-state phrases without
undoing seizure-free gains.

---

## Holistic assembly supersession

SF headline in production control v08: **0.9053** `clinical_headline` — adjudicator
v0.5 (0.721) was superseded by holistic v06 SF phase1 lens. Ladder canon preserves
**component-attributed** evidence for Plan 11 assembly narrative.

| Holistic version | SF F1 |
| --- | ---: |
| v01–v05 | 0.8068 (flat) |
| v06 | **0.9053** |
| v08 (frozen) | 0.9053 |

---

## Gold-quality ceiling (SF)

Metric-defensible 62.1% vs clinically defensible **89.3%** on dev140 disagreements;
GEPA `state_profile` rescoring 0.592→0.713 on same predictions.

Sources:
- [`exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`](../../experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md)
- [`../08_gepa.md`](../08_gepa.md) § SF representation

---

## Reading order

1. This canon (ladder table)  
2. v0.5 dev140 report (terminal adjudicator row)  
3. Holistic v06 error analysis (if archived — see holistic canon)  
4. SF canonical row analysis (C1)  

---

## Related

- [`SF_ADJUDICATOR_LADDER_CANON.md`](SF_ADJUDICATOR_LADDER_CANON.md) (this doc)  
- [`HOLISTIC_ASSEMBLY_LADDER_CANON.md`](HOLISTIC_ASSEMBLY_LADDER_CANON.md)  
- [`../10_paper_provenance.md`](../10_paper_provenance.md) C1, C3  
