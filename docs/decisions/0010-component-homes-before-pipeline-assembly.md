# 0010: Component Homes Before Pipeline Assembly

Date: 2026-06-04

## Status

Accepted.

## Decision

Represent each logical clinical-extraction component as an independently
owned module before wiring components together in a pipeline assembly file.

For Gan 2026 and future tasks, a full candidate pipeline should have:

- one clear module or package home for each prediction-bearing or
  evidence-bearing component;
- one explicit assembly module that composes those components into a runnable
  pipeline;
- tests and artifacts that can exercise important components independently
  from the full assembled pipeline;
- file and package names that describe component ownership, not experiment
  chronology.

Pipeline assembly files may orchestrate data flow, policy order, component
configuration, and final artifact writing. They should not become the permanent
home for candidate generation, evidence selection, selected-state carrying,
projection, safety-floor logic, verifier logic, abstention/review policy, or
component-evidence reporting.

## Context

Gan 2026 has gone through rapid experiment-driven development. That was useful:
it produced the current staged hybrid architecture and answered the component
research questions under validation-development constraints. It also left the
codebase with some behavior living in experiment replay modules, some in
analysis modules, some in task packages, and some implicit in artifact
generation scripts.

The next Gan 2026 architecture is explicitly multi-component:

```text
deterministic/state-graph substrate
  + selective LLM boundary candidate proposer
  + candidate-conditioned LLM evidence gate
  + rich selected-state fact carrier
  + deterministic consistency checks
  + gated deterministic projection/rendering
  + selective safety floor
  + selective verifier
  + abstain/review/monitoring policy
  + component evidence matrix
```

That architecture cannot stay clean if these pieces only exist as fragments of
a monolithic runner. The project thesis also requires later movement beyond
Gan seizure frequency into broader clinical extraction tasks, including the
ExECT task family referenced by `docs/research/contribution_thesis.md`. The
file structure should therefore teach the logical structure: what is reusable,
what is seizure-frequency-specific, what is Gan-specific, and what is only
benchmark formatting or experiment replay.

This decision refines ADR 0004. ADR 0004 split Gan 2026 by research boundary.
This ADR adds the rule that individual logical components get independent homes
before a final assembly module composes them.

## Component Home Rule

When adding or promoting a component, first decide its home:

- reusable clinical primitive: `clinical_extraction.core`;
- seizure-frequency behavior that should survive beyond Gan:
  `tasks/seizure_frequency`;
- Gan 2026 data, labels, benchmark policy, or synthetic-letter behavior:
  `tasks/seizure_frequency/gan2026`;
- experiment replay, saved-artifact analysis, or research diagnostics:
  `artifact_analysis` or `experiments`, not the production candidate path;
- final candidate orchestration: a small assembly module under the relevant
  task package.

If a component starts life in `artifact_analysis` during research, promotion
requires moving or extracting the reusable behavior into its component home
before the full pipeline depends on it.

## Gan 2026 Implications

The staged hybrid implementation should be built as a composed candidate, not
as one large new file. Expected homes include:

- deterministic and state-graph substrate in deterministic/state-graph modules;
- selected evidence and projection helpers in selected-evidence/projection
  modules;
- boundary proposer and verifier prompt/runtime logic in narrow LLM component
  modules;
- suspicious-state checks, safety-floor policy, and abstain/review monitoring
  in explicit policy modules;
- component evidence matrix construction in a reporting or evidence-contract
  module;
- one final assembly module that wires the above into the runnable Gan
  validation-development candidate.

Historical experiment names and artifact replay modules may remain for
provenance, but new promoted code should use the clean component names.

## ExECT Implications

The next task should not inherit Gan's experimental clutter. When ExECT work
begins, create the task structure around its logical extraction components from
the start:

- task-specific data contract and scoring policy;
- component homes for extraction, evidence, normalization, selection,
  validation, and reporting;
- a separate assembly file for the first runnable candidate;
- shared primitives promoted to `core` only when they genuinely generalize
  beyond one task.

Gan cleanup should make the eventual ExECT implementation easier to understand,
not merely make Gan tidier for its own sake.

## Consequences

- New assembled Gan work should avoid adding more business logic to broad
  experiment runners.
- Refactors should prefer small component extraction over large package moves
  when behavior is still being stabilized.
- Component tests should come before or alongside pipeline tests so failures
  identify the owner of a regression.
- Pipeline reports should name component owners using the same vocabulary as
  the file structure.
- A component can remain in `artifact_analysis` only while it is diagnostic.
  Once it becomes prediction-bearing in the assembled candidate, it needs a
  proper component home.
- Cleanup is allowed to be incremental. This ADR does not require a large
  behavior-changing reorganization before the staged Gan candidate can be
  assembled.

## Related Artifacts

- `docs/decisions/0004-gan2026-package-organization.md`
- `docs/decisions/0008-component-evidence-contract-for-candidate-promotion.md`
- `docs/decisions/0009-gan2026-staged-hybrid-assembly.md`
- `docs/research/contribution_thesis.md`
- `docs/experiments/gan2026/component_mechanics/gan2026_multi_component_assembly_research_report_2026-06-05.md`
