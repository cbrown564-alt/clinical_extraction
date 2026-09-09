# 0014: Call the deterministic evidence step “evidence trace check”

Date: 2026-06-07
Status: accepted


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

The fourth step in the retained rules pipeline is named **evidence trace check**.
It asks whether selected evidence appears verbatim in the note and records a
diagnostic clinical assessment. It does not affirm, reject, abstain, or route a
row for review.

The word “verification” remains reserved for code that makes those decisions.
Using it for a substring check would imply behavior that does not exist. A
future decision-making verifier would be a new feature and require its own
decision record and tests.
