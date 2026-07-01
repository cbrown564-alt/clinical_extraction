# Documentation Canon Index

Last updated: 2026-07-01

Routing index for **substantial canon documents** produced by the documentation
consolidation program. Full tier model: [`docs/NAVIGATION.md`](../NAVIGATION.md).

Wave 3 adds **workstream canons** for long experiment tails. Structural merge of
all design/research into this folder is **deferred** — canons stay at their natural
paths until a later migration.

---

## Wave 2 — Cross-cutting canons

| Canon | Path |
| --- | --- |
| Paper claims & provenance | [`docs/research/PAPER_CANON.md`](../research/PAPER_CANON.md) |
| ExECT evaluation & scoring | [`docs/research/exectv2_evaluation_canon.md`](../research/exectv2_evaluation_canon.md) |
| Gan closeout & The Wall | [`docs/research/gan2026/GAN2026_RESEARCH_CANON.md`](../research/gan2026/GAN2026_RESEARCH_CANON.md) |
| ExECT closeout evidence | [`docs/experiments/exectv2/CLOSEOUT_EVIDENCE_CANON.md`](../experiments/exectv2/CLOSEOUT_EVIDENCE_CANON.md) |
| GEPA negative program | [`docs/research/exectv2_gepa_canon.md`](../research/exectv2_gepa_canon.md) |

---

## Wave 3 — Workstream canons

| Workstream | Path | Absorbs (approx files) |
| --- | --- | ---: |
| Gan validation750 verifier iteration | [`docs/experiments/gan2026/VALIDATION750_CANON.md`](../experiments/gan2026/VALIDATION750_CANON.md) | 31 |
| Gan RQ1–RQ10 component mechanics | [`docs/experiments/gan2026/COMPONENT_MECHANICS_CANON.md`](../experiments/gan2026/COMPONENT_MECHANICS_CANON.md) | 31 |
| ExECT holistic assembly v01–v08 ladder | [`docs/experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md`](../experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md) | 14 (v01–v07 + EAs) |

---

## Control plane

| Doc | Path |
| --- | --- |
| Thread map (5 reading paths) | [`docs/THREAD_MAP.md`](../THREAD_MAP.md) |
| Active roadmap | [`docs/plans/ACTIVE_ROADMAP.md`](../plans/ACTIVE_ROADMAP.md) |
| Design spine index | [`docs/design/README.md`](../design/README.md) |
| Archive policy (future moves) | [`docs/archive/README.md`](../archive/README.md) |

---

## Reading order by job

| Job | Read |
| --- | --- |
| Write paper claims | PAPER_CANON → evaluation_canon → CLOSEOUT → GAN canon |
| Interpret Gan validation750 / RQ | GAN canon → VALIDATION750 → COMPONENT_MECHANICS |
| Understand ExECT v08 lineage | HOLISTIC_ASSEMBLY_LADDER → CLOSEOUT → evaluation_canon |
| Onboard to repo | THREAD_MAP → pick thread → relevant canon from this index |

---

## Stub convention

Absorbed source files keep full detail but carry a top banner:

```markdown
> **Superseded for navigation —** canonical summary: [`CANON.md`](CANON.md). …
```

Frozen artifact paths are never renamed when stubbing.
