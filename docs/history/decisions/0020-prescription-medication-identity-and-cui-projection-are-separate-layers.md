# Prescription Medication Identity and CUI Projection Are Separate Layers

Date: 2026-06-17


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

For ExECTv2 Prescription, clinical medication identity must canonicalize brand names, generic names, and common spelling variants for component scoring, while a separate benchmark projection layer emits the ExECT-facing `DrugName` and CUI convention. This keeps clinically correct regimen recovery distinct from ontology and benchmark-format alignment, so CUI or brand/generic projection gains are reported as projection gains rather than hidden extraction improvements.
