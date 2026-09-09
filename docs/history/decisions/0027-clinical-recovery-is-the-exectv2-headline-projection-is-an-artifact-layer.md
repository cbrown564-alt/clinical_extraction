# 0027: ExECT’s primary internal score measures clinical fact recovery

Date: 2026-06-18


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

ExECT uses de-duplicated clinical fact recovery as its primary internal score.
Exact annotation phrases and CUI formatting remain separate published-metric
companions.

The development analysis found high concept overlap but low exact phrase
agreement, and a gold-snapping diagnostic remained far below the published
score. This suggests that exact phrase scoring mixes clinical recovery with
annotation representation. The internal score therefore measures diagnosis
concepts, seizure-frequency state, prescription regimen, and investigation
status in entity-appropriate ways.

This choice gives up direct comparability to the published 0.87 item target.
Phrase, CUI, and full-attribute scores must still be reported when the paper
makes a published-benchmark comparison.
