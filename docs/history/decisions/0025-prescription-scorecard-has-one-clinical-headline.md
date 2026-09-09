# 0025: Use one primary prescription score

Date: 2026-06-17


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

The primary ExECT prescription score combines accepted current regimens,
including ordinary drug-dose-frequency tuples and rescue medication. Keep drug
identity, dose, stated or defaulted frequency, split/merge behavior, future
medication, weight-based dosing, phrase formatting, and CUI mapping as separate
diagnostics. Partial or formatting-specific gains must not be reported as the
main clinical result.
