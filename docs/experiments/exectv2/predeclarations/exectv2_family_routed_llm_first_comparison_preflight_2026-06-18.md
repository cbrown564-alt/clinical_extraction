# ExECTv2 Family-Routed LLM-First Comparison Preflight

Date: 2026-06-18
Status: GO - adapter, authorization, and dev-ladder replay completed.

## Decision

The predeclared family-routed dev ladder was authorized and replayed without
model calls over `pilot25 -> dev140`.

The routed adapter/runner is implemented at
`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/llm_family_routed_llm_first.py`.
The predeclaration status explicitly authorizes `pilot25 -> dev140` while
keeping full-200/test blocked. The dev140 readout is:
`docs/experiments/exectv2/key_entities/exectv2_family_routed_llm_first_comparison_2026-06-18.md`.

## Gate Checklist

| Gate | Current state | Required before run |
| --- | --- | --- |
| Plan 11 replay complete | Present | Keep as source plan. |
| Routed comparison predeclaration | Authorized | `pilot25 -> dev140` only; full-200/test still blocked. |
| SF event/state schema design | Present | Source design retained. |
| SF schema base classes | Present | Reuse `ClinicalFindingsRecord`, `EventFrameRecord`, and `ClinicalFindingRecord`. |
| Plan 11 routed adapter/schema contract | Implemented | Mapped shared P/I/D pass plus SF event/state route into the Plan 11 layer ladder. |
| Explicit dev-ladder authorization | Present | Predeclaration status authorizes `pilot25 -> dev140`. |
| Holdout/full-200 authorization | Blocked | Not authorized by this predeclaration. |

## Harness And Outputs

The preflight harness lives in:

- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/family_routed_preflight.py`
- `tests/test_exectv2_family_routed_preflight.py`

The executed replay artifacts are:

- `experiments/exectv2_family_routed_llm_first_pilot25_gpt41mini_20260618.json`
- `experiments/exectv2_family_routed_llm_first_pilot25_gpt41mini_20260618.jsonl`
- `experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_20260618.json`
- `experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_20260618.jsonl`
- `docs/experiments/exectv2/key_entities/exectv2_family_routed_llm_first_comparison_2026-06-18.md`

## Result

The dev140 four-family headline improved from `0.4313` for the single all-entities
LLM pass to `0.5592` for the family-routed candidate. SeizureFrequency improved
from `0.0118` to `0.6321`, clearing the predeclared `0.60` SF threshold.

The result is a qualified architecture win, not a clean LLM-first benchmark
claim. The routed candidate is labeled `llm_first_with_hybrid_sf_route` because
the SF source has deterministic candidate/projection and unknown-suppression
layers.

Do not run Gan `test450`, ExECTv2 full-200/test, holdout row-level review, or a
full-200 audit from this predeclaration. Full-200/test work requires a separate
frozen protocol and explicit authorization.
