# Gan 2026 Boundary-State Graph Builder Smoke

This is a hosted graph-builder diagnostic, not a benchmark result.

- Prompt version: `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_v0`
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Split: `validation_hard_slices`
- Split manifest: `gan2026_split_v1`
- Rows: 31
- JSONL artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_gpt41mini_live_2026-06-02.jsonl`

## Smoke Summary

- Schema-valid rows: 30/31
- Call failures: 0
- Reused raw outputs: 0
- Exact evidence: 28/29
- Representability gain candidates: 10/31

## Rows

| Source row | Surface role | Gold kind | Parse errors | Gain candidate |
| ---: | --- | --- | --- | --- |
| 338 | validation_boundary_missing | unresolved_multiple | none | True |
| 743 | validation_boundary_missing | unresolved_multiple | none | False |
| 869 | validation_boundary_missing | unresolved_multiple | node[0].evidence_not_exact, node[1].unresolved_multiple_label_invalid:Unparsable label (raw: 'unresolved_multiple' / normalized: 'unresolved_multiple') | False |
| 1317 | validation_boundary_missing | unknown | none | True |
| 1695 | validation_boundary_missing | unresolved_multiple | none | False |
| 1707 | validation_boundary_missing | unresolved_multiple | none | False |
| 2080 | validation_boundary_missing | unresolved_multiple | none | False |
| 2149 | validation_boundary_missing | unknown | none | False |
| 2166 | validation_boundary_missing | unknown | none | False |
| 3356 | validation_boundary_missing | unknown | none | False |
| 3436 | validation_boundary_missing | unknown | none | False |
| 3468 | validation_boundary_missing | unknown | none | False |
| 3493 | validation_boundary_missing | unknown | none | False |
| 3507 | validation_boundary_missing | unknown | none | True |
| 3512 | validation_boundary_missing | unknown | none | True |
| 3528 | validation_boundary_missing | unknown | none | True |
| 3532 | validation_boundary_missing | unknown | none | True |
| 3600 | validation_boundary_missing | unknown | none | True |
| 4690 | validation_boundary_missing | unresolved_multiple | none | False |
| 4694 | validation_boundary_missing | unresolved_multiple | none | True |
| 4700 | validation_boundary_missing | unresolved_multiple | none | False |
| 4709 | validation_boundary_missing | unresolved_multiple | none | False |
| 4731 | validation_boundary_missing | unknown | none | False |
| 4732 | validation_boundary_missing | unknown | none | False |
| 4771 | validation_boundary_missing | unknown | none | False |
| 5476 | validation_boundary_missing | unknown | none | True |
| 5490 | validation_boundary_missing | unknown | none | True |
| 5491 | validation_boundary_missing | unknown | none | False |
| 5504 | validation_boundary_missing | unknown | none | False |
| 5507 | validation_boundary_missing | unknown | none | False |
| 5534 | validation_boundary_missing | unresolved_multiple | none | False |
