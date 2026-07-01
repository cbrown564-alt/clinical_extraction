# Documentation Canon Index

Last updated: 2026-07-01

Routing index for **structural canons (01–10)** and **workstream canons** produced
by the documentation consolidation program. Full tier model:
[`docs/NAVIGATION.md`](../NAVIGATION.md).

Legacy paths under `docs/research/` and `docs/experiments/` redirect here (Wave 4).

---

## Structural canons (01–10)

| # | Topic | Path |
| --- | --- | --- |
| 01 | System architecture & three families | [`01_system_architecture.md`](01_system_architecture.md) |
| 02 | Pipeline spine (Gan + ExECT Plan 11) | [`02_pipeline_spine.md`](02_pipeline_spine.md) |
| 03 | Evidence, claims & frozen artifacts | [`03_evidence_claims_frozen.md`](03_evidence_claims_frozen.md) |
| 04 | Scoring surfaces & gold principles | [`04_scoring.md`](04_scoring.md) |
| 05 | Ceilings & The Wall | [`05_ceilings_wall.md`](05_ceilings_wall.md) |
| 06 | Gan clinical policy & closeout | [`06_gan_clinical_policy.md`](06_gan_clinical_policy.md) |
| 07 | ExECT Plan 11 closeout evidence | [`07_exect_plan11.md`](07_exect_plan11.md) |
| 08 | GEPA closed negative program | [`08_gepa.md`](08_gepa.md) |
| 09 | Cross-task reliability | [`09_cross_task_reliability.md`](09_cross_task_reliability.md) |
| 10 | Paper claims & provenance | [`10_paper_provenance.md`](10_paper_provenance.md) |

---

## Workstream canons

| Workstream | Path | Absorbs (approx files) |
| --- | --- | ---: |
| Gan validation750 verifier iteration | [`../experiments/gan2026/VALIDATION750_CANON.md`](../experiments/gan2026/VALIDATION750_CANON.md) | 31 (archived) |
| Gan RQ1–RQ10 component mechanics | [`../experiments/gan2026/COMPONENT_MECHANICS_CANON.md`](../experiments/gan2026/COMPONENT_MECHANICS_CANON.md) | 31 (archived) |
| ExECT holistic assembly v01–v08 | [`../experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md`](../experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md) | 13 (archived v01–v07) |
| ExECT Diagnosis family ladder | [`workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md`](workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md) | 15 |
| ExECT SF state adjudicator ladder | [`workstreams/SF_ADJUDICATOR_LADDER_CANON.md`](workstreams/SF_ADJUDICATOR_LADDER_CANON.md) | 5 |
| Self-consistency / entropy reliability | [`workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md`](workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md) | 13 |

Wave 4 archived iteration narratives under [`docs/archive/`](../archive/README.md).

---

## Control plane

| Doc | Path |
| --- | --- |
| Thread map (5 reading paths) | [`docs/THREAD_MAP.md`](../THREAD_MAP.md) |
| Active roadmap | [`docs/plans/ACTIVE_ROADMAP.md`](../plans/ACTIVE_ROADMAP.md) |
| Design spine index | [`docs/design/README.md`](../design/README.md) |
| Archive policy & layout | [`docs/archive/README.md`](../archive/README.md) |

---

## Reading order by job

| Job | Read |
| --- | --- |
| Write paper claims | 10 → 04 → 07 → 06 |
| Interpret Gan validation750 / RQ | 06 → VALIDATION750 → COMPONENT_MECHANICS |
| Understand ExECT v08 lineage | HOLISTIC_ASSEMBLY_LADDER → 07 → 04 |
| Diagnosis / SF family iteration | workstreams/DIAGNOSIS or SF → 05 (gold-quality) |
| Reliability / self-consistency | 09 → 05 → SELF_CONSISTENCY canon |
| Onboard to repo | THREAD_MAP → pick thread → canon from this index |

---

## Legacy redirects (Wave 4)

| Former path | New canonical path |
| --- | --- |
| `docs/research/PAPER_CANON.md` | [`10_paper_provenance.md`](10_paper_provenance.md) |
| `docs/research/exectv2_evaluation_canon.md` | [`04_scoring.md`](04_scoring.md) |
| `docs/research/gan2026/GAN2026_RESEARCH_CANON.md` | [`06_gan_clinical_policy.md`](06_gan_clinical_policy.md) |
| `docs/experiments/exectv2/CLOSEOUT_EVIDENCE_CANON.md` | [`07_exect_plan11.md`](07_exect_plan11.md) |
| `docs/research/exectv2_gepa_canon.md` | [`08_gepa.md`](08_gepa.md) |

---

## Stub convention

Absorbed source files keep full detail (or archive redirect) with a top banner:

```markdown
> **Superseded for navigation —** canonical summary: [`CANON.md`](CANON.md). …
```

Frozen artifact paths are never renamed when stubbing or archiving.
