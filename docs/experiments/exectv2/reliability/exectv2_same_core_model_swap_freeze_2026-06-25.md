# ExECTv2 Same-Core Model-Swap Freeze

Date: 2026-06-25

## Decision

The frozen same-core model-swap architecture is:

```text
exectv2_2call_no_sf_adjudicator_model_swap
```

The comparison question is model swap after architecture freeze, not a blend of
model choice and architecture-specific rescue stacks.

## Frozen Component Graph

| Component | Role | Owner |
| --- | --- | --- |
| `structured_key_family_event_ledger` | Live model structured all-family draft. | Model |
| `diagnosis_decomposer` | Live model Diagnosis decomposition over draft/spans. | Model |
| `sf_structured_direct_adapter` | Extract SF mentions from the structured draft. | Deterministic |
| `sf_state_projection` | Project selected structured facts into SF state. | Deterministic |
| `sf_unknown_suppression` | Suppress unsupported unknowns. | Deterministic |
| `sf_union_arbitration` | Merge structured-direct SF with deterministic state evidence. | Deterministic |
| `prescription_deterministic_repair` | Current regimen projection/repair. | Deterministic |
| `finding_assembly` | Common object model, lenses, views, and scorer. | Deterministic assembly |

The required views are `raw_candidate`, `evidence_valid`, `clinical_headline`,
`fidelity_companion`, and `benchmark_cui`. The primary reporting surface is
`clinical_headline` de-duplicated clinical recovery. Strict benchmark/CUI is
diagnostic.

## Allowed Model-Specific Differences

Allowed differences are limited to runtime model identifier, endpoint/runtime
settings, temperature/token/context budgets, prompt wording needed to satisfy
the same JSON contract, format-preserving JSON/schema repair, and runtime
telemetry. Qwen may use the compact structured prompt profile and native
Ollama chat routing with `think=false`.

Not allowed in a same-core row: different component graph, changed entity
lenses, changed scoring view, candidate-backed fact selection, model-specific
semantic repair, changed SF projection/suppression/union policy, changed
Prescription repair policy, or any full-200/holdout row-level failure analysis.

## Frozen Configs

```text
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140.json
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_deepseek_dev140.json
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_dev140.json
```

The configs must have identical `architecture_core_id`,
`live_call_components`, `replayed_components`, producer ids, lenses, views,
split, row count, and scorer surface. They may differ only in model adapter
fields and source artifact paths.

## Development Surface And Inspection Boundary

The first comparison surface is dev140. Full-200 may be used only after a
readiness review passes, and then only under a fresh aggregate-only
predeclaration. ExECTv2 full-200 and holdout row-level failure ledgers remain
blocked.

## Promotion Gates

Before the reliability scorecard can use a final model comparison row, the
same-core readiness report must show:

| Gate | Requirement |
| --- | --- |
| Architecture parity | Same frozen component graph across GPT-4.1-mini, DeepSeek, and Qwen. |
| Attribution clarity | Model-generated structured/Diagnosis facts separated from deterministic projection/repair. |
| Evidence validity | Exact evidence rate reported for every completed model row. |
| Operational stability | Call and parse/schema failures reported and bounded. |
| Family parity | Per-family clinical-headline metrics reported on the same surface. |
| Claim boundary | Dev140, full-200, and holdout surfaces not blended. |

## Historical Diagnostic Boundary

The following rows remain useful historical diagnostics but are not final
same-core model swaps:

- `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140`
- `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140`
- `exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_dev140`
- `exectv2_holistic_finding_assembly_v05_qwen_relaxed_actions_dev140`

These rows can support path evidence and failure-mode history. They must not be
presented as model swaps over the frozen GPT-4.1-mini lean reliability
architecture.

## Current Readiness Status

The GPT-4.1-mini same-core dev140 reference can be replayed from saved
self-consistency producer artifacts. DeepSeek and Qwen same-core dev140 rows
are pending live/replay artifacts and should be run only from the frozen
model-swap configs.
