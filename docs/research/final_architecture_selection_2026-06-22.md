# Final Architecture Selection

Date: 2026-06-22

Scope: Phase 0 selection memo for the architecture set worth carrying into the
closeout reports, frontend review surface, and paper-facing tables.

## Selection Principles

- Carry no more than five architectures into the final narrative.
- Keep performance control, simplicity control, and model-portability evidence
  separate.
- Treat deterministic semantic lenses and repairs as prediction-bearing when
  they select, add, drop, replace, or arbitrate clinical facts.
- Mark non-GPT dev140 rows as diagnostic unless a predeclared promotion gate
  promotes them. The completed DeepSeek/Qwen dev140 reports both remain
  `do-not-promote`.

## Selected Set

| Role | Architecture | Model | Surface | Claim boundary | Why selected |
| --- | --- | --- | --- | --- | --- |
| Gan reliability subject | Gan 2026 canonical reliability package | GPT-4.1-mini plus recorded comparators | Validation and locked-test reliability artifacts | Reliability package, with locked-test row-level guardrails | Mature reliability story and reusable scorecard pattern. |
| ExECTv2 performance control | `exectv2_holistic_finding_assembly_v08_dev140` | GPT-4.1-mini-family source lanes | dev140 | Dev-only component evidence | Only current ExECTv2 row with all four target families above `0.900`. |
| ExECTv2 simplicity control | `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | GPT-4.1-mini-family source lanes | dev140 | Dev-only simplification evidence | Retains overall `0.9059` while dropping the v08 Investigations stack. |
| ExECTv2 hosted non-GPT comparator | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | `deepseek/deepseek-chat` source artifact plus standard dictionary/lenses | dev140 | Diagnostic same-raw architecture evidence; do not promote | Final hosted non-GPT dev140 row: overall `0.9010`, strong Rx/Inv, clean operations, but Dx/SF below target and changed-row controls fail. |
| ExECTv2 local-model comparator | `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | `ollama_chat/qwen3.6:35b` compact source artifact plus standard dictionary/residual-repair lenses | dev140 | Diagnostic local-model architecture evidence; do not promote | Final local-model dev140 row: overall `0.9001`, strong SF headline and best Inv, but Dx below target, active-rate fidelity weak, and parse/schema burden remains. |

## Answers To Closeout Questions

### Which Architecture Is The Performance Control?

`exectv2_holistic_finding_assembly_v08_dev140`. It is the only current ExECTv2
control that clears Diagnosis, SeizureFrequency, Prescription, and
Investigations above `0.900` on dev140.

### Which Architecture Is The Simplicity Control?

`exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140`. It proves the
v08 architecture can be simplified while staying above `0.900` overall, but it
does not replace v08 because Investigations falls to `0.8549`.

### Which Architecture Is The Model-Portability Evidence?

DeepSeek v0.9.16 dev140 and Qwen v0.9.22 dev140 diagnostics. They show that
exact evidence, Prescription, and Investigations transfer better than Diagnosis
and active-rate SeizureFrequency. They are final diagnostic architecture rows,
not promotion candidates.

### Which Components Are Prediction-Bearing?

- Diagnosis reconciliation and convention handling.
- SeizureFrequency state selection, active-rate arbitration, and dictionary
  lenses.
- Prescription regimen repair and current-vs-plan decisions.
- Investigations result-state lenses or prompt-owned pass-through decisions.
- Standard dictionary repair when it changes clinical mention identity,
  attributes, or scorer-facing family membership.
- Residual-repair lenses in the final non-GPT rows, because their
  `raw_candidate` score view is `0.0000` and the meaningful scores are rendered
  after dictionary/lens repair.

### Which Deterministic Layers Are Benchmark-Format Only?

Only transformations that preserve an already selected clinical fact and adjust
accepted surface syntax, finite ontology codes, unit spelling, JSON/schema
compatibility, or scorer-required rendering should be described as
benchmark-format or format-only. Any deterministic step that changes the
selected clinical fact remains prediction-bearing.

## Rejected Or Superseded Branches

- Pure single-GPT plus dictionary v09 on GPT-4.1-mini: rejected as performance
  control because it scored `0.7552`.
- Earlier Qwen compact dev25 profile as promotion path: superseded after final
  v0.9.22 dev140 diagnostic. It remains useful path evidence only.
- Final Qwen v0.9.22 as replacement: rejected as v08 replacement because
  Diagnosis is `0.8563`, active-rate fidelity is `0.3618`, ten parse/schema
  failures remain visible, and changed-row controls fail despite overall
  `0.9001`.
- Earlier DeepSeek v0.9.7 dev25 and v0.9.9 dev25 diagnostics: superseded by the
  final v0.9.16 dev140 diagnostic row.
- Final DeepSeek v0.9.16 as replacement: rejected as v08 replacement because
  Diagnosis `0.8828` and SF `0.8675` remain below target, and changed-row
  controls fail despite overall `0.9010`.
- Dev1/dev5 smoke runs: scratch diagnostics only.
- DeepSeek v0.9.8 artifacts observed in the repo: superseded diagnostics that
  are not part of the selected set.

## Paper Table Shape

Carry the selected set into a compact table with these columns:

- task;
- architecture role;
- candidate;
- model;
- split/stage;
- row count;
- prediction-bearing components;
- overall F1;
- family F1s;
- evidence validity;
- operational status;
- claim boundary.
