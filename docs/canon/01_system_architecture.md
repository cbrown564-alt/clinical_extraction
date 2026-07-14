# 01 — Software structure

Last updated: 2026-07-14

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

See [software design](../design/architecture.md),
[component attribution](../design/component_evidence_attribution_architecture.md),
and [model policy](../design/model_strategy.md).
