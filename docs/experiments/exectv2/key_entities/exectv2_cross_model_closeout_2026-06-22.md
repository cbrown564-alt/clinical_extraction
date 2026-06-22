# ExECTv2 Cross-Model Closeout

Date: 2026-06-22

Scope: Phase 0 comparison across the current GPT-4.1-mini dev140 controls and
the completed DeepSeek/Qwen dev140 diagnostics. This is a no-call report built
from existing artifacts.

## Claim Boundary

- v08 and v09 partial hybrid are dev140 component-attributed controls.
- DeepSeek v0.9.16 and Qwen v0.9.22 are completed dev140 diagnostic
  architecture rows. Their final reports keep `do-not-promote` gate decisions.
- No row in this report is a full-200, holdout, locked-test, or benchmark claim.
- Row-level dev140 inspection is allowed for the listed development surfaces
  only; holdout/full-200 row-level inspection remains blocked without protocol.

## Comparison Table

| Candidate | Model | Architecture family | Split/stage | Calls complete | Call failures | Parse/schema failures | Exact evidence rate | Overall F1 | Dx | SF | Rx | Inv | Companion surface | Decision | Claim boundary |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `exectv2_holistic_finding_assembly_v08_dev140` | GPT-4.1-mini-family lanes | Holistic finding assembly, focused lanes | dev140 | no-call replay | 0 | 0 | 1.0000 | 0.9152 | 0.9083 | 0.9053 | 0.9357 | 0.9132 | SF active-rate fidelity `0.5969`; evidence-valid overall `0.8872` | Performance control | Dev-only component evidence |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | GPT-4.1-mini-family lanes | Partial hybrid simplification | dev140 | no-call replay | 0 | 0 | 1.0000 | 0.9059 | 0.9083 | 0.9053 | 0.9357 | 0.8549 | Simplifies Investigations stack; evidence-valid overall `0.8779` | Simplicity control | Dev-only simplification evidence |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | `deepseek/deepseek-chat` | Single GPT-style key-family ledger plus standard dictionaries/lenses | dev140 | source 140; assembly no-call replay | 0 | 0 | 1.0000 | 0.9010 | 0.8828 | 0.8675 | 0.9430 | 0.9231 | evidence-valid overall `0.8554`; SF active-rate fidelity `0.6057`; raw candidate `0.0000`; changed-row controls fail Rx 35 and Inv 6 | Final diagnostic, do not promote | `diagnostic-same-raw-deepseek-v0910-through-v0916-dictionary-dev140` |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | `ollama_chat/qwen3.6:35b` | Compact local-model ledger plus standard dictionaries/lenses and residual repair | dev140 | source 140; assembly no-call replay | 0 | 10 per family lens surface | 1.0000 | 0.9001 | 0.8563 | 0.8908 | 0.9343 | 0.9579 | evidence-valid overall `0.8567`; SF active-rate fidelity `0.3618`; raw candidate `0.0000`; changed-row controls fail Rx 29 and Inv 48 | Final diagnostic, do not promote | `local-qwen-v0910-qwen-compact-live-dev140-ctx12288-maxtok2500-standard-dictionary-residual-repair-v13` |

## What Transfers Across Models

- Exact-evidence enforcement transfers well after assembly/lens replay. The
  final DeepSeek and Qwen dev140 assemblies have exact evidence rate `1.0000`
  on the scored mentions reported by their assembly diagnostics.
- Prescription is the most portable family. DeepSeek v0.9.16 reaches `0.9430`,
  and Qwen v0.9.22 reaches `0.9343`, both close to or above the v08
  Prescription control.
- Investigations is strong in the final non-GPT dev140 rows: DeepSeek reaches
  `0.9231`, and Qwen reaches `0.9579`. This supports model-portability
  evidence for the family, with the caveat that Qwen's score is repair-mediated.
- Non-GPT architectures can reach the `0.900` overall range on dev140 after
  standard dictionaries and residual lenses, but this is architecture evidence,
  not raw-model-only evidence.

## What Does Not Transfer

- Diagnosis remains below the v08/v09 control outside GPT-4.1-mini. DeepSeek
  reaches `0.8828`, and Qwen reaches `0.8563`, so neither clears the family
  target.
- SeizureFrequency headline improves materially at dev140 scale, especially for
  Qwen, but still trails v08/v09: DeepSeek reaches `0.8675`, and Qwen reaches
  `0.8908` versus the GPT control at `0.9053`.
- SeizureFrequency active-rate fidelity remains weak. DeepSeek reaches
  `0.6057`, roughly tied with the GPT control, while Qwen remains poor at
  `0.3618`.
- Qwen still carries an operational burden: the final assembly reports ten
  parse/schema failures per family lens surface, and the useful score depends
  on residual repair.

## Model-Stable Families

- Prescription is model-stable enough to use as portability evidence.
- Investigations is model-stable enough in the final dev140 rows to use as
  portability evidence, while preserving the repair-mediated caveat for Qwen.
- Exact evidence is stable after deterministic validation/lens replay, but this
  is an assembly property and should not be credited as raw model correctness.

## Families Requiring Focused Architecture

- Diagnosis still benefits from focused reconciliation and convention handling.
- SeizureFrequency still requires focused state selection, active-rate fidelity
  controls, and arbitration. The final non-GPT rows improve headline SF but do
  not fully carry the v08 SF result.
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

## Why Final Non-GPT Dev140 Rows Do Not Promote

DeepSeek and Qwen are now final dev140 diagnostic comparators rather than
pending dev25 signals. They strengthen the cross-model story, but they do not
replace v08:

- v08 remains the only row with all four target families above `0.900`.
- DeepSeek v0.9.16 misses Diagnosis and SeizureFrequency family targets.
- Qwen v0.9.22 misses Diagnosis, has weak active-rate fidelity, and carries ten
  parse/schema failures per family lens surface.
- Both final non-GPT reports have `raw_candidate` score view `0.0000`; the
  meaningful scores are after standard dictionary/lens rendering.
- Both final non-GPT reports fail changed-row controls for Prescription and
  Investigations.

## Superseded Diagnostics

Earlier DeepSeek v0.9.7 dev25, Qwen v0.9.6 schema-repair reparse dev25, and
Qwen v0.9.7 compact dict-repair dev25 rows remain useful path evidence, but the
selected non-GPT comparison rows are now the final v0.9.16 DeepSeek dev140 and
v0.9.22 Qwen dev140 diagnostics.
