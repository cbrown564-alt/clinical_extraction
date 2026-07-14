# 03 — Evidence, Claims & Frozen Artifacts

Last updated: 2026-07-14

**Structural canon slot:** authority stack, frozen paths, and claim boundaries.

---

## Authority stack (highest wins)

The 2026-07-13 surgery audit found that the legacy frozen artifact index did
not reproduce much of its claimed path/hash graph. The replacement manifest
was rebuilt and verified on 2026-07-14. Use this authority order:

1. **Present file plus recomputed hash** — direct evidence that the artifact exists
2. **Verified retained-evidence manifest** — selected evidence, current hashes, and byte sizes
3. **Structural / workstream canons** — this folder
4. **ADRs** — `docs/decisions/`
5. **Registry rows** — claim-of-record metadata for runs, but not proof that an artifact exists
6. **Research syntheses** — dated interpretation under `docs/research/`

The deleted legacy indexes remain available in Git history only. Do not use an
old path reference alone to block deletion or support a paper claim.

---

## Frozen paths (never rename or move)

| Path | Role |
| --- | --- |
| [`docs/experiments/retained_evidence_manifest.md`](../experiments/retained_evidence_manifest.md) | Verified selected evidence; JSON companion owns hashes and byte sizes |
| [`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`](../experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md) | v08 performance control report |
| `experiments/*.md` at repo root | CI allowlist — extend only deliberately |

Machine replay artifacts are retained only when a surviving claim or reference
configuration needs them. Large retained artifacts may live outside primary Git
when the verified manifest records immutable location, checksum, size, schema,
and retrieval instructions.

---

## Claim boundaries by split

| Split | Row inspection | Typical use |
| --- | --- | --- |
| **dev140** | Allowed | v08, GEPA, ablations, family ladders |
| **validation750** | Allowed | Gan component ladder |
| **ExECTv2 full200** | Aggregate only | Development-inclusive full-corpus audit; contains dev140 + held-out test60 |
| **Gan test450** | **Forbidden** (aggregate only) | Author-untouched locked holdout |
| **fixture / smoke** | Panel rules | Hard panels, self-consistency smoke |

From `claim_policy.py` — see [`04_scoring.md`](04_scoring.md) § Claim boundaries.

---

## What may be claimed in the paper

Register: [`10_paper_provenance.md`](10_paper_provenance.md) (C1–C5).

**Do not claim without boundary language:**

- Row-level Gan test450 beyond predeclared aggregates
- ExECTv2 full200 described as an independent holdout rather than a development-inclusive audit
- Benchmark 0.87/0.90 dominance (pivot to capability-first)  
- LLM-only as production control (~0.73 vs hybrid ~0.92)  
- Consensus/fresh selector (CUT)

---

## Archive policy

Wave 4 moves stubbed iteration narratives to [`docs/archive/`](../archive/README.md)
with redirect stubs at original paths. Canon summaries remain the navigation entry.

---

## Related structural canons

- [`10_paper_provenance.md`](10_paper_provenance.md) — claims register  
- [`07_exect_plan11.md`](07_exect_plan11.md) — selected architecture evidence tables  
