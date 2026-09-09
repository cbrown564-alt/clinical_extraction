# Weight-Based Prescription Dosing Is a Separate Diagnostic

Date: 2026-06-17


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

For ExECTv2 Prescription, weight-based dosing statements such as `mg/kg/day` must be reported in a separate diagnostic rather than scored as absolute current-regimen `DrugDose + DoseUnit` tuples. This preserves clinically meaningful dosing evidence while keeping absolute-dose component F1 tied to the measurement object expected by the Prescription regimen score.
