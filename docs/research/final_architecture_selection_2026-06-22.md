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
- Mark dev25 non-GPT rows as diagnostic unless a predeclared escalation gate
  promotes them.

## Selected Set

| Role | Architecture | Model | Surface | Claim boundary | Why selected |
| --- | --- | --- | --- | --- | --- |
| Gan reliability subject | Gan 2026 canonical reliability package | GPT-4.1-mini plus recorded comparators | Validation and locked-test reliability artifacts | Reliability package, with locked-test row-level guardrails | Mature reliability story and reusable scorecard pattern. |
| ExECTv2 performance control | `exectv2_holistic_finding_assembly_v08_dev140` | GPT-4.1-mini-family source lanes | dev140 | Dev-only component evidence | Only current ExECTv2 row with all four target families above `0.900`. |
| ExECTv2 simplicity control | `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | GPT-4.1-mini-family source lanes | dev140 | Dev-only simplification evidence | Retains overall `0.9059` while dropping the v08 Investigations stack. |
| ExECTv2 hosted non-GPT comparator | `exectv2_holistic_finding_assembly_v097_deepseek_dev25` | `deepseek/deepseek-chat` | dev25 | Diagnostic | Strong Prescription/Investigations and clean evidence; Diagnosis/SF below target. |
| ExECTv2 local-model comparator | Qwen diagnostic pair: v0.9.6 no-call reparse and v0.9.7 compact dict-repair | `ollama_chat/qwen3.6:35b` | dev25 | Diagnostic | Shows local-model portability/runtime limits; no dev140 promotion evidence. |

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

DeepSeek v0.9.7 dev25 and Qwen dev25 diagnostics. They show that exact evidence
and Prescription transfer better than Diagnosis and SeizureFrequency. They are
not promotion candidates.

### Which Components Are Prediction-Bearing?

- Diagnosis reconciliation and convention handling.
- SeizureFrequency state selection, active-rate arbitration, and dictionary
  lenses.
- Prescription regimen repair and current-vs-plan decisions.
- Investigations result-state lenses or prompt-owned pass-through decisions.
- Standard dictionary repair when it changes clinical mention identity,
  attributes, or scorer-facing family membership.

### Which Deterministic Layers Are Benchmark-Format Only?

Only transformations that preserve an already selected clinical fact and adjust
accepted surface syntax, finite ontology codes, unit spelling, JSON/schema
compatibility, or scorer-required rendering should be described as
benchmark-format or format-only. Any deterministic step that changes the
selected clinical fact remains prediction-bearing.

## Rejected Or Superseded Branches

- Pure single-GPT plus dictionary v09 on GPT-4.1-mini: rejected as performance
  control because it scored `0.7552`.
- Qwen compact profile as promotion path: rejected after completed dev25
  assembly scored `0.7995`, with Diagnosis `0.7755` and SF `0.5882`.
- DeepSeek v0.9.7 as replacement: rejected as v08 replacement because Diagnosis
  `0.8456` and SF `0.7586` remain below target.
- Dev1/dev5 smoke runs: scratch diagnostics only.
- DeepSeek v0.9.8 artifacts observed in the repo: diagnostic successors that
  require an explicit replacement decision before entering the selected set.

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

