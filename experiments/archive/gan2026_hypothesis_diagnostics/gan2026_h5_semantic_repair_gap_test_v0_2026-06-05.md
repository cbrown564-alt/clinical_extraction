# Gan 2026 H5 Semantic Repair Gap Test

Diagnostic attribution only. Locked-test readout is aggregate-only and does not inspect row-level failures.

- Hypothesis: `H5` Deterministic semantic repair masks LLM weakness on validation.
- Split manifest: `gan2026_split_v1`
- Outcome: `partially_supported_revise`
- Locked-test row-level artifacts used: `0`

## Same-Output Validation Ladder

| Layer | Purist proxy | Changed from raw | Raw W->C | Raw C->W | Owner |
| --- | ---: | ---: | ---: | ---: | --- |
| raw_model_selected_label | 0.7520 | 0 | 0 | 0 | llm |
| format_only_repair | 0.7520 | 7 | 0 | 0 | llm |
| selected_evidence_arithmetic_only | 0.8760 | 57 | 32 | 1 | llm_selected_evidence_then_deterministic_arithmetic |
| benchmark_aligned_adapter | 0.8160 | 28 | 16 | 0 | llm_with_named_benchmark_adapter |

## Validation-Test Repair Gain

| Surface | Raw/base proxy | Full repair proxy | Repair gain | Rows |
| --- | ---: | ---: | ---: | ---: |
| Validation750 | 0.7360 | 0.9680 | 0.2320 | 750 |
| Locked test450 | 0.7600 | 0.7933 | 0.0333 | 450 |

- Raw validation-test gap: `-0.0240`
- Full-repair validation-test gap: `0.1747`
- Repair-gain validation minus test: `0.1987`

## Interpretation

H5 is supported in the narrow sense that validation repair layers mask weak raw LLM behavior, but the original primary-signal wording should be revised. The raw/base layer does not show a larger validation-test gap than full repair; instead, validation receives a much larger repair gain than locked test. Treat this as deterministic semantic repair and contract coverage overfitting validation, not as an LLM-owned transfer success.
