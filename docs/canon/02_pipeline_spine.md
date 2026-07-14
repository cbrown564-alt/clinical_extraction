# 02 — Pipeline stages

Last updated: 2026-07-14

This document names the stages shared by the retained Gan and ExECT reference
systems. Exact source, configuration, scorer, test, and replay paths live in the
[retained evidence manifest](../experiments/retained_evidence_manifest.md).

## Gan 2026

```text
letter
  → clinical assessment or structured event extraction
  → deterministic selection and normalization
  → Gan label rendering
  → Purist and Pragmatic scoring
```

The retained comparison contains rules-only, single-pass LLM-only, and
single-pass hybrid cells. The multi-trace V12 result is saved aggregate ceiling
evidence, not an executable reference cell.

## ExECTv2

```text
letter
  → family producers
  → Diagnosis, SeizureFrequency, Prescription, and Investigations transforms
  → clinical finding assembly
  → clinical_headline and companion scoring
```

The retained comparison contains the deterministic all-nine baseline, the GEPA
LLM-only negative comparator, and holistic finding assembly v08.

## Stage ownership

| Stage | Owner |
| --- | --- |
| Data and split policy | Task data modules and checked split manifests |
| Extraction | Deterministic or LLM task modules |
| Clinical selection | Task-specific deterministic or hybrid modules |
| Normalization and projection | Task deterministic modules |
| Evidence and schema checks | Shared core plus task contracts |
| Scoring | Gan or ExECT scorer packages |
| Artifact identity | Retained evidence manifest |
| Claim strength | [Paper claims register](10_paper_provenance.md) |

## Frozen reduced architecture

Freeze `reduced_reference_architecture_20260714` pins the executable source at
commit `465621341c6af59f2fc028be7bf5f9e325739c50`. The v3 retained-evidence
manifest additionally fingerprints the dependency lock, prompts, scorers,
split policies, repair policies, model policy, and CI workflow.

This freeze governs new evidence; it does not turn every retained historical
run into a symmetric comparison. In particular, the retained ExECT
three-model package used model-specific temperature and Qwen prompt/format
conditions. Its bounded transfer claim remains valid, but a strict six-model
claim requires six predeclared runtime conditions under the frozen two-call
core described in [the model policy](../design/model_strategy.md).

Any semantic prompt, scorer, split, repair, model-route, or component-graph
change requires a new freeze ID and complete replay. The freeze itself does not
authorize model calls.

The retained cross-task ablation found normalization gains of +0.0389 on ExECT
dev140 and +0.0293 on Gan validation750. The evidence check changed neither
headline score on those replays. That score result does not make the evidence
check unnecessary; rejection and repair behavior still needs direct tests.

