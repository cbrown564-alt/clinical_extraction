# Gan 2026 RQ1/RQ2 Component-Control Matrix

Pre-call condition matrix for isolated single-task controls and paired-task overload controls. The JSONL row grain is one source row by panel by condition.

- Date: `2026-06-04`
- Matrix rows: 875
- Source rows represented: 115
- Conditions: 7
- JSONL artifact: `experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.json`

## Conditions

| Condition | Task | Rows | Source rows | Overload |
| --- | --- | ---: | ---: | --- |
| `candidate_conditioned_evidence_only` | `evidence_selection` | 125 | 115 | `False` |
| `candidate_only` | `candidate_generation` | 125 | 115 | `False` |
| `candidate_plus_evidence` | `candidate_generation+evidence_selection` | 125 | 115 | `True` |
| `candidate_plus_evidence_plus_projection` | `candidate_generation+evidence_selection+projection` | 125 | 115 | `True` |
| `evidence_plus_projection` | `evidence_selection+projection` | 125 | 115 | `True` |
| `gold_query_evidence_only` | `evidence_selection` | 125 | 115 | `False` |
| `projection_only` | `projection` | 125 | 115 | `False` |

## Required Empty Output Slots

Each JSONL row reserves fields for component output, exact evidence/source-id status, deterministic comparator label, gold label, hidden-family tags, metric fields, first-failure owner, and row-level notes. Fresh model-call runners should fill those fields without changing row membership.

## Claim Boundary

Pre-call matrix for isolated and paired-task overload controls. Rows record prompt/schema obligations but do not contain fresh model outputs.
