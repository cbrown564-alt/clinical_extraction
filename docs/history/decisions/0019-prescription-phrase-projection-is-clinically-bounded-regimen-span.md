# Prescription Phrase Projection Is the Clinically Bounded Regimen Span

Date: 2026-06-17


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

For ExECTv2 Prescription, the benchmark-facing mention text must be the clinically bounded medication regimen span, excluding section headings, list labels, and surrounding sentence context. This preserves the clinical object being extracted (active anti-seizure medication regimen with dose/unit/frequency) while treating wider or section-prefixed gold spans as phrase-projection convention to be measured and ablated separately from clinical component recovery.
