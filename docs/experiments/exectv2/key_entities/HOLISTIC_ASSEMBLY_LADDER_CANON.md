# ExECTv2 Holistic Finding Assembly Ladder Canon

Last updated: 2026-07-06

## What this is

The **v01–v08 ladder** replays the same frozen per-family producer outputs on
**dev140** (140 development letters) with **no live model calls**. Each step
changes only **which lens stack** scores Diagnosis, SeizureFrequency,
Prescription, and Investigations — same producers, different assembly rules.

**v08** is the **production control** (frozen performance baseline). Unless a
section explicitly cites full-200 or holdout work, all headline numbers here are
**dev140 only**.

**Long tail:** 15 files in [`key_entities/`](.) (v01–v07 + phase error analyses stubbed)

---

## Ladder table (`clinical_headline` overall F1)

| Version | Gate / theme | Overall | Dx | SF | Rx | Inv | Δ overall vs prev |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **v01** | promote-dev-holistic-finding-assembly | 0.8006 | 0.7572 | 0.8068 | 0.8214 | 0.8615 | — |
| **v02** | revise-dev-diagnosis-heading-recovery | 0.8038 | 0.7658 | 0.8068 | 0.8214 | 0.8615 | +0.0032 |
| **v03** | (Dx phase2 lens) | 0.8130 | 0.7894 | 0.8068 | 0.8214 | 0.8615 | +0.0092 |
| **v04** | (Dx phase3) | 0.8278 | 0.8301 | 0.8068 | 0.8214 | 0.8615 | +0.0148 |
| **v05** | (Dx phase4) | 0.8576 | 0.9083 | 0.8068 | 0.8214 | 0.8615 | +0.0298 |
| **v06** | SF phase1 lens | 0.8789 | 0.9083 | **0.9053** | 0.8214 | 0.8615 | +0.0213 |
| **v07** | Inv phase1 lens | 0.8873 | 0.9083 | 0.9053 | 0.8214 | 0.9132 | +0.0084 |
| **v08** | **performance control** | **0.9152** | 0.9083 | 0.9053 | **0.9357** | 0.9132 | +0.0279 |

Sources: `exectv2_holistic_finding_assembly_v{01..08}_dev140_20260621.md`

---

## Version notes (what changed)

| Version | Primary delta |
| --- | --- |
| **v01→v02** | Diagnosis lens: `diagnosis_hierarchy_negation_v01` → `diagnosis_heading_recovery_v02` |
| **v03–v05** | Diagnosis specialist stack iterations (phase 2–4 error analyses in long tail) |
| **v05→v06** | SF lens upgrade — SF headline jumps to 0.9053 |
| **v06→v07** | Investigations lens — Inv 0.8615 → 0.9132 |
| **v07→v08** | Prescription lens — Rx 0.8214 → 0.9357; overall crosses 0.900 all four families |

**v08 frozen path:** `exectv2_holistic_finding_assembly_v08_dev140_20260621.md` (+ JSON/JSONL in `final_artifact_index`).

---

## Promotion gates (v08)

From v08 dev140 report:

- All four key families **>0.900** on `clinical_headline`  
- Do-not-promote caveat: changed-row controls can still fail Rx/Inv despite headline  
- Full-200 and holdout: separate predeclarations in CLOSEOUT canon  

---

## Phase error analyses (long tail)

Per-family phase reports (`*_phase*_error_analysis_20260621.md`) document **row-level**
residuals for each ladder step. Use when debugging a specific family regression;
**do not** cite phase reports for headline numbers — use ladder table above.

| Family | Phase reports |
| --- | --- |
| Diagnosis | v02 phase1, v03 phase2, v04 phase3, v05 phase4 |
| SeizureFrequency | v06 phase1 |
| Investigations | v07 phase1 |
| Prescription | v08 phase1 |

---

## What v01–v07 files are for now

- **Historical ladder evidence** for Plan 11 / ADR 0032  
- **Stubbed** with navigation banner → this canon  
- **Not deleted** — registry and replay scripts may reference paths  

---

## Related reading

- [`docs/canon/07_exect_plan11.md`](../../canon/07_exect_plan11.md) — v08 production control + full-200  
- [`docs/canon/04_scoring.md`](../../canon/04_scoring.md) — scoring surfaces  
- [`docs/decisions/0032-clinical-finding-assembly-is-the-exectv2-plan11-spine.md`](../../../decisions/0032-clinical-finding-assembly-is-the-exectv2-plan11-spine.md) — ADR 0032 (Plan 11 assembly spine)
