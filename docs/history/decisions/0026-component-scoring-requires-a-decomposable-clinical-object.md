# Component Scoring Requires a Decomposable Clinical Object

Date: 2026-06-17


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

For ExECTv2 reporting, component scores must be added only when an entity has a real decomposable clinical object, such as a medication regimen, an investigation performed/result/type fact, or seizure-frequency attribute families. Entities whose main errors are phrase scope, assertion, temporal anchoring, or ontology projection must receive diagnostics for those layers rather than artificial component scores created for symmetry across the scorecard.
