# ExECTv2 Cross-Model Closeout

Date: 2026-06-22

Scope: Phase 0 comparison across the current GPT-4.1-mini dev140 controls and
the available DeepSeek/Qwen dev25 diagnostics. This is a no-call report built
from existing artifacts.

## Claim Boundary

- v08 and v09 partial hybrid are dev140 component-attributed controls.
- DeepSeek and Qwen rows are dev25 diagnostics and are not comparable as
  replacements for dev140 controls.
- No row in this report is a full-200, holdout, locked-test, or benchmark claim.
- Row-level dev140/dev25 inspection is allowed for the listed development
  surfaces only.

## Comparison Table

| Candidate | Model | Architecture family | Split/stage | Calls complete | Call failures | Parse/schema failures | Exact evidence rate | Overall F1 | Dx | SF | Rx | Inv | Companion surface | Decision | Claim boundary |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `exectv2_holistic_finding_assembly_v08_dev140` | GPT-4.1-mini-family lanes | Holistic finding assembly, focused lanes | dev140 | no-call replay | 0 | 0 | 1.0000 | 0.9152 | 0.9083 | 0.9053 | 0.9357 | 0.9132 | SF active-rate fidelity `0.5969`; evidence-valid overall `0.8872` | Performance control | Dev-only component evidence |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | GPT-4.1-mini-family lanes | Partial hybrid simplification | dev140 | no-call replay | 0 | 0 | 1.0000 | 0.9059 | 0.9083 | 0.9053 | 0.9357 | 0.8549 | Simplifies Investigations stack; evidence-valid overall `0.8779` | Simplicity control | Dev-only simplification evidence |
| `exectv2_holistic_finding_assembly_v097_deepseek_dev25` | `deepseek/deepseek-chat` | Single GPT-style key-family ledger plus standard dictionaries | dev25 | 25 | 0 | 0 in assembly lens diagnostics | 1.0000 | 0.8707 | 0.8456 | 0.7586 | 0.9610 | 0.9091 | Source JSONL has one nonfatal parse-error row; assembly scored cleanly | Diagnostic comparator | Hosted-DeepSeek v0.9.7 live dev25 |
| `exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25` | `ollama_chat/qwen3.6:35b` | No-call schema-repair reparse plus standard dictionaries | dev25 | no-call reparse | 0 | 0 in assembly lens diagnostics | 1.0000 | 0.8082 | 0.8112 | 0.6429 | 0.8608 | 0.9268 | SF active-rate fidelity `0.3750` | Diagnostic, do not promote | Local-Qwen v0.9.6 schema-repair reparse |
| `exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25` | `ollama_chat/qwen3.6:35b` | Qwen compact live dev25 plus dictionary repair | dev25 | 25 | 0 | 1 per family lens surface | 1.0000 | 0.7995 | 0.7755 | 0.5882 | 0.9487 | 0.8163 | SF active-rate fidelity `0.2424`; source JSONL has two parse-error rows | Diagnostic, do not promote | Local-Qwen v0.9.7 qwen-compact live dev25 |

## What Transfers Across Models

- Exact-evidence enforcement transfers well after assembly/lens replay. The
  selected DeepSeek and Qwen assemblies have exact evidence rate `1.0000` on
  the scored mentions reported by their assembly diagnostics.
- Prescription is the most portable family. DeepSeek reaches `0.9610`, and the
  latest Qwen compact dict-repair reaches `0.9487`, both above the v08
  Prescription control.
- Investigations can be strong in non-GPT rows, but the result is unstable:
  DeepSeek v0.9.7 reaches `0.9091`, Qwen v0.9.6 reaches `0.9268`, and Qwen
  v0.9.7 compact drops to `0.8163`.

## What Does Not Transfer

- SeizureFrequency remains the least portable family. DeepSeek v0.9.7 reaches
  `0.7586`; Qwen v0.9.6 reaches `0.6429`; Qwen v0.9.7 compact reaches `0.5882`.
  None are dev140 escalation evidence.
- Diagnosis remains below the v08/v09 control outside GPT-4.1-mini. DeepSeek is
  the strongest non-GPT diagnostic at `0.8456`, but still misses the `0.900`
  family target.
- Compact prompting did not produce a better Qwen comparator. It improved some
  operational constraints, but the completed dev25 assembly fell below the
  earlier v0.9.6 no-call reparse.

## Model-Stable Families

- Prescription is model-stable enough to use as portability evidence.
- Exact evidence is stable after deterministic validation/lens replay, but this
  is an assembly property and should not be credited as raw model correctness.
- Investigations is partly stable, but Qwen compact regression means it should
  stay diagnostic until a same-surface row confirms stability.

## Families Requiring Focused Architecture

- Diagnosis still benefits from focused reconciliation and convention handling.
- SeizureFrequency still requires focused state selection, active-rate fidelity
  controls, and arbitration. Single-model ledger transfer does not carry the
  v08 SF result.
- Prescription deterministic regimen repair remains prediction-bearing and must
  stay described as a component, not hidden as incidental formatting.

## Why v08 Remains The Control

v08 is the only row in this report with all four official ExECTv2 Plan 11
families above `0.900` on dev140: Diagnosis `0.9083`, SeizureFrequency
`0.9053`, Prescription `0.9357`, and Investigations `0.9132`. It is also the
most complete component-evidence package: config, report, JSON/JSONL, error
ledger, provenance sidecars, and reliability plan already exist.

## Why v09 Partial Hybrid Remains The Simplification Option

v09 partial hybrid keeps the focused Diagnosis, focused SeizureFrequency, and
deterministic Prescription components while dropping the v08 Investigations
verifier/arbitration stack. It still reaches `0.9059` overall on dev140. The
tradeoff is clear: simplicity improves, but Investigations falls to `0.8549`,
so it is a simplicity control rather than the performance control.

## What Would Justify Non-GPT Dev140 Escalation

A DeepSeek or Qwen dev140 escalation should be written before execution and
should name one of these purposes:

- Paper-facing cross-model evidence despite known under-target Dx/SF families.
- A predeclared test of whether dev25 Diagnosis/SF gaps shrink on dev140.
- A review-routing/agreement analysis that needs a larger aligned surface.

Minimum gates before escalation:

- zero call failures, or explicitly recoverable call failures;
- zero unrepaired parse/schema failures on the declared scorer surface;
- exact evidence near `1.0000`, with family-level explanation for any drops;
- Diagnosis and SeizureFrequency plausibly competitive with v09 partial hybrid;
- no hidden ExECTv2 full-200 or holdout row-level inspection.

## Pending Refresh

- If DeepSeek v0.9.8 diagnostics replace v0.9.7 in the final table, update this
  report and the artifact index together. The v0.9.8 dev25 artifact exists in
  the repo but is not selected by this Phase 0 report.
- If any new Qwen diagnostic is run, compare it to both v0.9.6 no-call reparse
  and v0.9.7 compact dict-repair before changing the Qwen row.
- No new model calls were required for this Phase 0 report.

