# 02 — Pipeline Spine

Last updated: 2026-07-01

**Structural canon slot:** end-to-end flow from letter text to scored clinical findings.

---

## Gan 2026 spine (frozen)

```
letter → clinical assessment → structured events → projection/render → Purist score
```

Promoted path: **LLM structured-event extraction + deterministic render** (not
direct labeler, not multi-agent consensus). See [`06_gan_clinical_policy.md`](06_gan_clinical_policy.md).

Deterministic fourth stage: **Evidence Trace Check** (ADR 0014) — distinct from
hybrid `Verify` vocabulary.

---

## ExECTv2 Plan 11 spine (production control)

```
letter → per-family producers (JSONL) → family lenses (Dx/SF/Rx/Inv) → clinical finding store → headline projection
```

Frozen performance control: **holistic finding assembly v08** — all four key
families >0.900 on dev140 `clinical_headline`. Replay-only evidence ladder in
[`workstreams/HOLISTIC_ASSEMBLY_LADDER_CANON.md`](workstreams/HOLISTIC_ASSEMBLY_LADDER_CANON.md)
(absorbs v01–v07 iteration).

ADR anchor: [`0032-clinical-finding-assembly-is-the-exectv2-plan11-spine.md`](../decisions/0032-clinical-finding-assembly-is-the-exectv2-plan11-spine.md).

---

## Shared cross-task layers

From cross-task ablation (2026-06-27):

| Component | ExECTv2 dev140 | Gan validation750 |
| --- | ---: | ---: |
| `evidence_validation` gate | Δ=0 (inert) | Δ=0 (inert) |
| `standard_dictionary` / normalize | +0.0389 | +0.0293 |

Evidence gate is structurally present but **does not move headline scores** on
current stacks.

---

## Primary sources

| Topic | Document |
| --- | --- |
| ExECT key-family synthesis | [`docs/research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md`](../research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md) |
| Gan rule register | [`docs/design/gan2026_rule_register.md`](../design/gan2026_rule_register.md) |
| Experiment registry | [`experiments/registry.jsonl`](../../experiments/registry.jsonl) |
| Run validation ladder | [`experiments/README.md`](../../experiments/README.md) |

---

## Related structural canons

- [`01_system_architecture.md`](01_system_architecture.md) — package boundaries  
- [`04_scoring.md`](04_scoring.md) — what gets scored at each stage  
- [`07_exect_plan11.md`](07_exect_plan11.md) — frozen closeout evidence  
