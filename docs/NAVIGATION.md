# Documentation navigation

Updated: 2026-09-11. These links describe current locations. Proposed destinations
and the move sequence are in the [project plan](plans/ACTIVE_ROADMAP.md).

## Active project

| Need | Owner |
| --- | --- |
| Strand A manuscript argument and planned exhibits | [One-call paper outline](../publications/jamia-one-shot/README.md) |
| Strand A comparisons, capability thresholds and configuration exploration | [Draft evaluation protocol](research/gan2026/one_shot_paper_protocol.md) |
| Project purpose and current repository layout | [README](../README.md) |
| Three-strand programme, DSPy/GEPA evidence, reconstruction strategy and longitudinal timeline | [Active roadmap](plans/ACTIVE_ROADMAP.md) |
| Worked architecture examples, proposed interfaces and first implementation slice | [Software architecture](design/architecture.md) |
| Migration evidence and approved legacy-support dispositions | [Migration record and investigation](research/maintenance/repository_migration_2026-09-08.md#7-legacy-support-investigation-2026-09-13) |
| Current task state and verification (local checkout) | [Project status](../PROJECT_STATUS.md) |
| Working rules and research safeguards | [AGENTS](../AGENTS.md) |
| Document ownership and archiving procedure | [Documentation lifecycle](runbooks/documentation_lifecycle.md) |

| Longitudinal subject | Owner |
| --- | --- |
| Cohort queries, evidence cutoffs, endpoint, seed eligibility and pilot criteria | [Task definition](longitudinal/task_definition.md) |
| Prior-work comparison, publication versions and source-use findings | [Literature rationale](reference/longitudinal_epilepsy_rationale.md) |
| Three-letter example, filtered inputs and expected query answers | [Authored patient 001](../examples/longitudinal/authored_patient_001/README.md) |
| Annotation meaning, uncertainty and relationship rules | [Annotation guide v0.3](longitudinal/annotation_guide.md) |
| Provisional annotation structure | [Annotation schema v0.3](longitudinal/annotation.schema.json) |
| Authored pilot coverage and gaps | [Pilot coverage](longitudinal/pilot_coverage_matrix.md) |
| Pilot corrections, temporal/link review, field comparison and effort limits | [Pilot review](longitudinal/pilot_disagreement_report.md) |
| Seed-free generation procedure, source restrictions and effort policy | [Generation protocol](longitudinal/generation_protocol.md) |
| Completed staged generation, reviewed cases, revisions and exact replay | [Phase 3 generation record](../results/longitudinal/generation_v0.1/README.md) |
| Prototype evaluation, saved-extraction comparisons and attribution policy | [Evaluation protocol](longitudinal/evaluation_protocol.md) |
| Working patient viewer, cohort queries, component results and verification | [Phase 4 prototype](../results/longitudinal/prototype_v0.1/README.md) |

[Generation protocol](longitudinal/generation_protocol.md) owns the Phase 3 procedure,
source-use conditions and the prospective effort procedure. The seed-free 1 → 5 → 12
batch is complete, with 36 letters and 240 references regenerated exactly from saved
outputs. All records remain development-only with shared ancestry and same-assistant
review. The generation record retains revisions and 33 query-diagnostic mismatches.
The Phase 4 evaluation protocol governs the saved-output prototype comparison;
a frozen Phase 7 model comparison is still future work. The roadmap owns work order, not a duplicate
query specification. No longitudinal benchmark result is available. The 12-case
pilot has completed Phase 2: coverage acceptance, independent AI dry runs, temporal
and link review, measured AI wall time by activity and all-query field comparison.
Phase 4 implements complete query execution and both patient views. Expert
validation and human effort remain later work;
source-attribution and semantic alternatives are explicit in the pilot review. Unsupported earlier
P2.6 measurements remain withdrawn.

## Existing letter-benchmark evidence

These records retain their Gan/ExECT meaning. They are context and reusable
engineering evidence, not evaluations of patient-history reconstruction.

| Need | Current owner or entry |
| --- | --- |
| Dissertation scope and paper reading order | [Paper keep-set](paper/README.md) / [Dissertation publication](../publications/dissertation/) |
| Gan-only manuscript decision | [Gan is the dissertation paper](paper/decisions/gan-is-the-dissertation-paper.md) |
| Retained benchmark policies | [Gan 2026](benchmarks/gan2026/README.md), [ExECTv2](benchmarks/exectv2/README.md) |
| Existing dataset description | [Dataset description](research/shared/dataset_description_2026-08-26.md) |
| What the gold labels preserve or discard | [Annotation policy comparison](research/shared/what_the_two_golds_already_decided_2026-08-17.md) |
| Current manuscript methods & notes | [Dissertation notes](../publications/dissertation/notes/) |
| Saved results and inventory | [Letter benchmarks](../results/letter-benchmarks/README.md), [inventory](../results/letter-benchmarks/inventory.json) |
| Wider Gan/ExECT model comparison | [Three variables](research/shared/three_variables_rules_model_thinking_2026-08-23.md) |
| Study protocols and writing sources | [Research entry](research/README.md) |
| Shared and task-specific design references | [Design entry](design/README.md) |
| Implemented stage diagrams and teaching cases | [Generated architecture](architecture/README.md) |
| Locked-holdout policy | [Aggregate-only holdout](paper/decisions/holdout-is-aggregate-only.md) |
| Test admission and tiers | [Pytest firewall](paper/decisions/pytest-is-the-research-validity-firewall.md) |
| Historical numbered decisions | [Decision history](history/decisions.md) |
| Historical canon (superseded) | [Historical canon](history/canon/) |
| Historical plans (superseded) | [Historical plans](history/plans/) |


Some older indexes, experiment plans and claim documents disagree with later
manuscript decisions. Follow the paper keep-set for manuscript scope and the new
roadmap for current work. Do not resume a run because a historical page lists it
as missing. Phase 0 classifies and rehomes the remaining conflicting material.
