# Prescription Missing-Frequency Defaults Are Benchmark Projection

Date: 2026-06-17


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

When an ExECTv2 Prescription source span names an anti-seizure medication and dose but does not state a schedule, guideline defaults such as once daily or `As_Required` for rescue-medication conventions must be treated as benchmark projection rather than source-stated frequency extraction. This lets benchmark-facing output follow the annotation guideline while keeping clinical component reports honest about whether the schedule was actually recovered from the letter text.
