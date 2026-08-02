# Documentation navigation

Short map of the supervisor path and worker doors. Historical experiment
catalogs are not listed here; find them through paper claim status, the
retained-evidence index, the regeneration ledger, or the decision/report that
owns the claim. Short task routes live in [THREAD_MAP.md](THREAD_MAP.md).

## Supervisor handoff

Start with [README.md](../README.md). The supervisor path covers the one-sentence
claim, five-stage pipeline diagram, six selected methods, frontend demonstration,
six-path teaching case, canonical results report, evidence and limits, and exact
reproduction instructions.

The direct handoff links are [six-path walkthrough](architecture/teaching_cases/six_paths.md),
[frontend startup](../frontend/README.md), [canonical results](research/six_model_comparison_report_2026-07-18.md),
[claim limits](canon/10_paper_provenance.md), and [exact no-call replay](../scripts/verify_reference_evidence.py).

## Current work

| Need | Read |
| --- | --- |
| Current outcome and checks | [project status](../PROJECT_STATUS.md) |
| Ordered next work | [active roadmap](plans/ACTIVE_ROADMAP.md) |
| Current refactor scope and completion gate | [Decision 0048](decisions/0048-comprehension-and-handoff-refactor.md) |
| Pytest suite as research-validity firewall | [Decision 0049](decisions/0049-pytest-research-validity-firewall.md) |
| Regeneration and historical-artifact triage | [regeneration guide](REGENERATION.md) |
| Restricted external-validation run gate | [readiness template](runbooks/external_validation_readiness.md) |
| Short reading paths | [THREAD_MAP](THREAD_MAP.md) |

## How the pipelines work

| Need | Read |
| --- | --- |
| How a record moves through any selected method | [architecture index](architecture/README.md) |
| The whole system on one page | [two tasks x three methods](architecture/diagrams/overview.md) |
| Which stages may change a clinical answer, anywhere | [ownership matrix](architecture/diagrams/ownership_matrix.md) |
| One method in depth, with a code map | [method cards](architecture/README.md#method-cards) |
| A real letter moving stage by stage | [Gan teaching case](architecture/teaching_cases/gan2026.md) and [ExECT teaching case](architecture/teaching_cases/exectv2.md) |
| Machine-readable stage definitions | `src/clinical_extraction/architecture/manifests/` |

## Evidence pointer block

| Need | Read |
| --- | --- |
| Selected files, hashes, and replay requirements | [retained evidence index](experiments/retained_evidence_manifest.md) |
| Strength of paper claims | [paper claim status](canon/10_paper_provenance.md) |
| Canonical six-model results | [comparison report](research/six_model_comparison_report_2026-07-18.md) |

Detailed experiment history is intentionally absent from the active index. Use
Git history and the owning claim documents when the selected evidence is not
enough.
