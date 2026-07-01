# 03 — Evidence, Claims & Frozen Artifacts

Last updated: 2026-07-01

**Structural canon slot:** authority stack, frozen paths, and claim boundaries.

---

## Authority stack (highest wins)

1. **Frozen artifact index** — SHA-256 hashes, promotion-safe paths  
2. **Structural / workstream canons** — this folder  
3. **ADRs** — `docs/decisions/`  
4. **Research syntheses** — dated narrative under `docs/research/`  
5. **Registry rows** — `experiments/registry.jsonl` (claim-of-record for runs)

---

## Frozen paths (never rename or move)

| Path | Role |
| --- | --- |
| [`docs/experiments/final_artifact_index_2026-06-22.md`](../experiments/final_artifact_index_2026-06-22.md) | Master hash table |
| [`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`](../experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md) | v08 performance control report |
| `experiments/*.md` at repo root | CI allowlist — extend only deliberately |

Machine replay artifacts (`experiments/*.jsonl`, `*.json`) are never archived.

---

## Claim boundaries by split

| Split | Row inspection | Typical use |
| --- | --- | --- |
| **dev140** | Allowed | v08, GEPA, ablations, family ladders |
| **validation750** | Allowed | Gan component ladder |
| **full200 / test450** | **Forbidden** (aggregate only) | Model swap, holdout |
| **fixture / smoke** | Panel rules | Hard panels, self-consistency smoke |

From `claim_policy.py` — see [`04_scoring.md`](04_scoring.md) § Claim boundaries.

---

## What may be claimed in the paper

Register: [`10_paper_provenance.md`](10_paper_provenance.md) (C1–C5).

**Do not claim without boundary language:**

- Row-level test450 / full-200 beyond predeclared aggregates  
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
