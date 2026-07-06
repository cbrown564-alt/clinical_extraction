# Collaborator Onboarding — Clinical Extraction

Last updated: 2026-07-06

A single entry point for new collaborators: what this repository is, how the
research is organized, where the evidence lives, and which concepts are hardest
to grasp without context.

**Interactive companion:** open [`collaborator_onboarding.html`](collaborator_onboarding.html)
in a browser for layered architecture diagrams, inspectable evidence panels, and
explorable deep-dives on The Wall, gold-quality ceilings, and pipeline stages.

**Term definitions:** [`docs/reference/plain_language_glossary.md`](reference/plain_language_glossary.md)
— plain display names for codenames (The Wall, ceilings, splits, version codes).

---

## What this project is

Hybrid deterministic–LLM pipelines for extracting structured clinical data from
unstructured epilepsy letters. The long-term goal is a reusable Python package;
the active research phase combines:

1. **Gan 2026** — single-label seizure-frequency extraction on synthetic letters
   (holdout evidence **frozen**; reliability and the confident over-reading limit
   (The Wall) are the headline findings).
2. **ExECTv2** — broad epilepsy phenotyping on de-identified letters (active
   development; `clinical_headline` recovery is the primary scoreboard).

Both tasks share a modular hybrid architecture (rules / LLM-only / hybrid families)
and an evidence-first evaluation discipline.

**Control plane:** [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) →
[`docs/plans/ACTIVE_ROADMAP.md`](plans/ACTIVE_ROADMAP.md) →
[`docs/THREAD_MAP.md`](THREAD_MAP.md).

---

## Research thesis (four contributions)

From [`docs/research/contribution_thesis.md`](research/contribution_thesis.md):

| # | Contribution | What it means in practice |
| --- | --- | --- |
| 1 | Modular breadth and depth | Task boundaries under `tasks/`; reusable primitives in `core/` |
| 2 | Generalisation by design | Rule portability categories; ablation switches; locked splits |
| 3 | Transparency | Intermediate schemas, evidence spans, row-level error artifacts |
| 4 | Rules as controlled variables | Deterministic behavior is categorized, testable, and ablatable |

The paper pivots to **capability-first claims (C1–C5)**, not benchmark dominance.
See [`docs/canon/10_paper_provenance.md`](canon/10_paper_provenance.md).

| Claim | Plain summary |
| --- | --- |
| **C1** | Many benchmark “errors” are label-format issues, not bad extractions (SF ~89% clinically OK vs ~62% strict; diagnosis similar). |
| **C2** | Shared components help both tracks — medical dictionary normalization lifts both; evidence gate does not. |
| **C3** | Track 1’s “confident mistake” pattern may appear in Track 2 seizures (early signal only; automatic abstention not yet useful). |
| **C4** | The pipeline design works across language models — swap models, keep architecture; scores stay in the same band. |
| **C5** | Experiments are pre-registered and test results frozen before claiming them (validation ladder, locked splits, audit policy). |

---

## Two workstreams at a glance

| | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| **Task** | Seizure frequency (single label) | Diagnosis, SF, Rx, Investigations |
| **Data** | Synthetic letters, locked split | De-identified clinical letters |
| **Status** | Holdout frozen; no tuning | v08 holistic assembly is production control |
| **Headline score** | Purist (strict Gan matcher) / Pragmatic on `test450` | `clinical_headline` composite |
| **Key negative** | Confident over-reading limit (The Wall), ~84% Purist ceiling | Annotation-format / gold-quality ceiling on SF & diagnosis |
| **Promoted architecture** | LLM structured-event + deterministic render | Holistic finding assembly v08 |

---

## Three architecture families

Every experiment belongs to one family ([`docs/canon/01_system_architecture.md`](canon/01_system_architecture.md)):

| Family | Clinical fact owner | Format / render |
| --- | --- | --- |
| **rules_only** | Deterministic rules | Adapters only |
| **llm_only** | LLM (single or multi-pass) | Adapters only |
| **hybrid** | Split: producers, verifiers, adjudicators | Explicit projection stages |

**Gan promoted path:** staged hybrid — LLM structured-event extraction, then
deterministic render (not direct labeler, not multi-agent consensus).

**ExECT promoted path:** manifest-driven clinical finding assembly — producers
emit `ClinicalFinding` objects; entity lenses reconcile; views project to
headline or benchmark surfaces.

---

## Pipeline spines

### Gan 2026 (frozen)

```text
letter → clinical assessment → structured events → projection/render → Purist score
```

### ExECTv2 production pipeline (internal: Plan 11)

```text
letter → per-family producers → family lenses (Dx/SF/Rx/Inv) → finding store → headline projection
```

See [`docs/canon/02_pipeline_spine.md`](canon/02_pipeline_spine.md).

---

## Key results (with evidence paths)

### Gan holdout (aggregate-only)

| Role | What it is | Score (Purist / test450) | Notes |
| --- | --- | ---: | --- |
| **Production** | Single GPT-4.1-mini structured-event extractor + deterministic render — the promoted Gan architecture | **364/450 = 0.809** | Frozen reference run (`v0_reference` artifact family) |
| **Ceiling** | V12 fresh-evidence hybrid — best holdout comparator, not production | **379/450 = 0.842** | Upper bound under frozen protocol; gap to production is mostly confident over-reading |
| **Floor** | Rules-only baseline — no LLM clinical facts | 343/450 = 0.762 | Controlled lower bound |

Source: [`docs/canon/06_gan_clinical_policy.md`](canon/06_gan_clinical_policy.md).

### ExECT full-200 (`clinical_headline`, same-core)

| Model | Overall | SF | Notes |
| --- | ---: | ---: | --- |
| GPT-4.1-mini | 0.8356 | 0.7525 | Development model |
| DeepSeek | **0.8566** | 0.7602 | Leads overall |
| Qwen repair v02 | 0.8197 | 0.7020 | Diagnostic |

Artifact: `experiments/exectv2_same_core_model_swap_full200_20260625.json`

### Gold-quality ceiling (C1)

| Family | Metric surface | Clinically defensible | Genuine model error |
| --- | --- | --- | --- |
| SF (dev140) | 62.1% | **89.3%** | 15/53 metric-errors |
| Dx (dev140) | F1 0.6617 | **F1 0.9501** adjusted | 14.8% genuine |

Sources: SF row analysis 2026-06-29; Dx row analysis 2026-06-30.

### Cross-task component dividend (C2)

- `evidence_validation` gate: **Δ=0** on both ExECT dev140 and Gan validation750.
- `standard_dictionary`: **+0.0389** ExECT, **+0.0293** Gan.

Source: `docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`

---

## Hard concepts (read these carefully)

### The Wall (Gan reliability)

**Plain English:** On the hardest Gan letters, the model is **confidently wrong** —
it picks a seizure rate when the note is ambiguous and the correct answer is
“unknown.” No signal we can see at inference time (without peeking at gold labels)
reliably tells us when to abstain. That caps Purist around **~84%**; it is a
**prior** about the task, not a knob to tune away.

**Binding residual** — letters where the gold label is “unknown” but the model emits
a specific rate anyway (the failure mode The Wall describes).

**Forward-observable** — anything you can measure from the model’s outputs and
intermediate artifacts at run time (confidence, agreement across models, entropy,
etc.) — as opposed to hidden gold labels used only for evaluation.

On binding residual rows, **every forward-observable feature** fails to separate
withhold-to-unknown from emit-rate; only hidden gold distinguishes them.

- P0.2: External Risk Score (cross-model agreement strongest leg)
- P2.1: Semantic entropy flat → over-reading is **confident**, not uncertain
- Irreducible residual: 11 validation rows, 8/11 `band_unknown`

Thread: T1 in [`docs/THREAD_MAP.md`](THREAD_MAP.md).

### Gold-quality ceiling (ExECT scoring)

**Plain English:** Distinct from The Wall. The benchmark scorer expects a specific
annotation shape; the model often recovers the right clinical idea in a different
format. Strict F1 then penalizes “format mismatch” as if the concept were missing.

Benchmark F1 fuses target representation, scorer design, and extractor output unit.
Many "errors" are annotation multiplicity or format fidelity gaps, not missing
clinical concepts.

**SF trap:** rescoring same predictions under `state_profile` lifts SF without
changing model output — a representation effect, not recall.

Thread: T2 in [`docs/THREAD_MAP.md`](THREAD_MAP.md).

### Scoring surface hierarchy (ExECT)

| Surface | Use |
| --- | --- |
| `clinical_headline` | **Primary** project scoreboard |
| `state_profile` | Primary for SF-family experiments |
| benchmark / CUI | Diagnostic / comparability only |

Never quote benchmark F1 alone as extractor quality.

---

## Codebase map

```text
src/clinical_extraction/
  core/                         Shared pipeline, schema, evidence, validation
  tasks/seizure_frequency/gan2026/   Gan loader, labels, scoring, pipelines
  tasks/epilepsy_phenotyping/exectv2/  ExECT assembly, lenses, LLM pipelines
  observatory/                  FastAPI inspection server for artifacts

docs/
  canon/01–10                   Structural canon (start here for truth)
  design/                       Architecture notes and ADRs
  experiments/                  Human-readable experiment reports
  research/                     Thesis, synthesis, paper-facing notes
  runbooks/                     Repeatable workflows

experiments/                    Run outputs, registry.jsonl
tests/                          Data contracts and deterministic behavior
```

---

## Five reading threads

| Thread | Question | Start |
| --- | --- | --- |
| **T1** Reliability / The Wall | Can forward signals route binding residuals? | `docs/canon/06_gan_clinical_policy.md` |
| **T2** Clinical recovery | What is the headline score? | `docs/canon/04_scoring.md` |
| **T3** Architecture | What does each stage own? | `docs/design/architecture.md` |
| **T4** Paper closeout | What can we claim? | `docs/canon/10_paper_provenance.md` |
| **T5** Engineering | How do runs get registered? | `docs/runbooks/documentation_lifecycle.md` |

Full hop lists: [`docs/THREAD_MAP.md`](THREAD_MAP.md).

---

## Getting started (engineering)

```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

First milestone: reproduce Gan-compatible data loading, label normalization, and
evaluation locally before optimizing pipelines.

Experiment surface: [`experiments/README.md`](../experiments/README.md).

---

## Claims you must not make

From paper canon — preserve these boundaries:

- Row-level test450 / full-200 inspection beyond predeclared aggregate audits
- Consensus/fresh selector promotion (CUT)
- LLM-only dedup as production control (~0.73 vs ~0.92 hybrid)
- Unqualified "beat 0.87/0.90 benchmark"
- Conflating The Wall with the gold-quality ceiling

---

## Related documents

| Document | Role |
| --- | --- |
| [`CONTEXT.md`](../CONTEXT.md) | Vocabulary and domain terms |
| [`docs/reference/plain_language_glossary.md`](reference/plain_language_glossary.md) | Plain-language term definitions |
| [`README.md`](../README.md) | Repository overview |
| [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) | Live control board |
| [`docs/NAVIGATION.md`](NAVIGATION.md) | Documentation tier model |
