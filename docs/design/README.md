# Design Documentation Index

Durable architecture and evaluation design. For **active work**, see
[`docs/plans/ACTIVE_ROADMAP.md`](../plans/ACTIVE_ROADMAP.md). For **reading by
research thread**, see [`docs/THREAD_MAP.md`](../THREAD_MAP.md).

## Spine documents (read these first)

| Document | Owns |
| --- | --- |
| [`reliability_thesis.md`](reliability_thesis.md) | Project-level reliability claim, success criteria, cross-task thesis |
| [`architecture.md`](architecture.md) | Package layers, task boundaries, component homes |
| [`component_evidence_attribution_architecture.md`](component_evidence_attribution_architecture.md) | Component ownership, promotion gates, ablation contract |
| [`data_contract.md`](data_contract.md) | Shared data and label contracts |
| [`deterministic_projection_rule_taxonomy.md`](deterministic_projection_rule_taxonomy.md) | Projection/repair rule categories and score-line attribution |

## Task-specific design

| Document | Task |
| --- | --- |
| [`gan2026_pipeline_v1.md`](gan2026_pipeline_v1.md) | Gan pipeline (superseded direction — see ADR 0009) |
| [`gan2026_*`](.) | Normalization, splits, rule register, resolve label, validation protocols |
| [`exectv2_component_ablation_contract_2026-06-24.md`](exectv2_component_ablation_contract_2026-06-24.md) | ExECTv2 component-off replay contract |
| [`gan2026_component_ablation_contract_2026-06-24.md`](gan2026_component_ablation_contract_2026-06-24.md) | Gan component-off replay contract |
| [`brief_role_crosswalk.md`](brief_role_crosswalk.md) | Supervisor brief roles → actual architecture |

## Decisions

Architecture decision records live in [`docs/decisions/`](../decisions/) (append-only,
38 records). Highest-signal for current work: 0009 (staged hybrid), 0014 (Evidence
Trace Check), 0027 (clinical recovery headline), 0030 (four indicators), 0032 (Plan 11
spine), 0037 (SF `state_profile`).

## Consolidation note

Future waves will merge spine + task-specific material into `docs/canon/` structural
documents. Until then, this index is the routing surface. Do not add new files here
without updating this README — prefer ADRs for new durable decisions.
