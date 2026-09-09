# Documentation navigation

Updated: 2026-09-09. These links describe current locations. Proposed destinations
and the move sequence are in the [project plan](plans/ACTIVE_ROADMAP.md).

## Active project

| Need | Owner |
| --- | --- |
| Project purpose and current repository layout | [README](../README.md) |
| Scope, full task timeline and repository restructuring | [Active roadmap](plans/ACTIVE_ROADMAP.md) |
| Current task state and verification (local checkout) | [Project status](../PROJECT_STATUS.md) |
| Working rules and research safeguards | [AGENTS](../AGENTS.md) |
| Document ownership and archiving procedure | [Documentation lifecycle](runbooks/documentation_lifecycle.md) |

| Longitudinal subject | Owner |
| --- | --- |
| Cohort queries, evidence cutoffs, endpoint, seed eligibility and pilot criteria | [Task definition](longitudinal/task_definition.md) |
| Prior-work comparison, publication versions and source-use findings | [Literature rationale](reference/longitudinal_epilepsy_rationale.md) |
| Three-letter example, filtered inputs and expected query answers | [Authored patient 001](../examples/longitudinal/authored_patient_001/README.md) |

The annotation guide and generation protocol will be created during Phases 2–3;
the evaluation protocol must be frozen before model comparison. The roadmap owns
work order, not a duplicate query specification. No longitudinal benchmark result
is available. P2.1's authored example is implemented; annotation guidance and
independent review remain ahead.

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
