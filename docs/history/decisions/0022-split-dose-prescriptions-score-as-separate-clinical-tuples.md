# Split-Dose Prescriptions Score as Separate Clinical Tuples

Date: 2026-06-17


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

For ExECTv2 Prescription component scoring, split-dose schedules such as one morning dose and a different evening dose must be represented as separate bound regimen tuples, one per dose slot. This preserves the clinically actionable regimen structure while leaving one-mention versus multi-mention formatting to the benchmark projection and split/merge diagnostic layer.
