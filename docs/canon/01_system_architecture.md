# 01 — System Architecture

Last updated: 2026-07-01

**Structural canon slot:** package layers, task boundaries, and the three architecture
families (rules / LLM-only / hybrid).

---

## Bottom line

The repo grows from benchmark implementations into a reusable clinical extraction
package. Task-neutral primitives live in `clinical_extraction.core`; task-specific
logic lives in `clinical_extraction.tasks`. The first task is `seizure_frequency.gan2026`;
ExECTv2 is the multi-entity extension.

Three **architecture families** (experimental ontology) compare who owns clinical
fact vs format projection:

| Family | Clinical fact owner | Format / render |
| --- | --- | --- |
| **rules_only** | Deterministic rules | Adapters only |
| **llm_only** | Single- or multi-pass LLM | Adapters only |
| **hybrid** | Split: producers, verifiers, adjudicators | Explicit render/projection stages |

---

## Boundary choices (intentional separations)

- Loading from scoring  
- Event extraction from final clinical reasoning  
- Label normalization from metric mapping  
- Evidence validation from correctness evaluation  
- Model selection from prompt/program behavior  
- Experiment output from package source  

Candidate promotion follows the **component evidence contract** — every candidate
must answer which component solved each clinical subproblem, under which evidence
gate, with what regression risk.

---

## Primary sources

| Topic | Document |
| --- | --- |
| Package layers | [`docs/design/architecture.md`](../design/architecture.md) |
| Component evidence contract | [`docs/design/component_evidence_attribution_architecture.md`](../design/component_evidence_attribution_architecture.md) |
| Three families ontology | [`docs/research/contribution_thesis.md`](../research/contribution_thesis.md) |
| Model policy | [`docs/design/model_strategy.md`](../design/model_strategy.md) |
| Gan staged hybrid ADR | [`docs/decisions/0009-gan2026-staged-hybrid-assembly.md`](../decisions/0009-gan2026-staged-hybrid-assembly.md) |

---

## Related structural canons

- [`02_pipeline_spine.md`](02_pipeline_spine.md) — end-to-end pipeline stages  
- [`07_exect_plan11.md`](07_exect_plan11.md) — selected ExECT architectures  
- [`06_gan_clinical_policy.md`](06_gan_clinical_policy.md) — Gan promoted/rejected set  
