# Rescue Prescriptions Have a Dose-Optional Regimen Shape

Date: 2026-06-17


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

For ExECTv2 Prescription component scoring, rescue or PRN anti-seizure medications must have a distinct regimen component shape: medication identity plus `As_Required`, with dose recorded when stated but not required for rescue-regimen credit. The annotation guideline explicitly allows rescue medications without dose, so treating those facts as ordinary complete-tuple failures would misclassify valid Prescription evidence.
