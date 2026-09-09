# 01 — Software structure


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

Last updated: 2026-07-15

Shared code lives in `clinical_extraction.core`; task-specific code lives in
`clinical_extraction.tasks`. Gan 2026 extracts seizure frequency. ExECTv2
extends the package to several epilepsy phenotypes.

The research compares three methods:

| Method | Who determines the clinical facts? | Deterministic code after extraction |
| --- | --- | --- |
| Rules only | Deterministic rules | Formats and scores |
| LLM only | A language model | Validates and formats model-selected facts |
| LLM with rules | Model and rules | May normalize, select, or repair clinical meaning |

The code keeps loading, extraction, clinical selection, normalization, evidence
checking, and scoring separate so errors and improvements can be attributed to
the component that caused them.

For the final ExECT model comparison, `LLM with rules` has a stricter family
boundary: the named model supplies the candidate Diagnosis, Seizure Frequency,
Prescription, and Investigations facts. Deterministic clinical changes remain
attributed, but an independent rules-only extractor cannot replace or be
unioned into the named model's result. The selected `v08` score remains a
historical development control and does not meet this final boundary. See
[decision 0040](../../decisions/0040-final-exect-llm-with-rules-family-ownership.md).

The stage-level account of each of these six cells — who owns each change,
which stages may change clinical meaning, and where each runs — is the
[architecture layer](../../architecture/README.md).

See [software design](../../design/architecture.md),
[component attribution](../../design/component_evidence_attribution_architecture.md),
and [model policy](../../design/model_strategy.md).
