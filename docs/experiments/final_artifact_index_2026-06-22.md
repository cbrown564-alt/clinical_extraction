# Final Artifact Index

Date: 2026-06-22

Scope: Phase 0 closeout index for the final comparison set across Gan 2026,
ExECTv2 GPT-4.1-mini controls, and completed DeepSeek/Qwen dev140 diagnostics.

This index freezes the evidence spine before any repository simplification. It
does not authorize deleting, moving, or renaming canonical artifacts. It also
does not promote diagnostic dev140 rows to performance-control, full-200,
locked-test, or benchmark claims.

## Claim Boundary

- Gan 2026 reliability artifacts remain the mature reliability package.
- ExECTv2 v08 and v09 partial hybrid are dev140 component-attributed controls.
- DeepSeek v0.9.16 and Qwen v0.9.22 are completed dev140 diagnostic
  cross-model architecture evidence. Both final reports keep `do-not-promote`
  gate decisions.
- ExECTv2 holdout/full-200 row-level inspection remains blocked without a frozen
  protocol.

## Canonical Artifact Groups

### Gan 2026 Reliability Package

| Field | Value |
| --- | --- |
| Candidate | Gan 2026 reliability master scorecard |
| Model | GPT-4.1-mini plus recorded comparators, as stated in scorecard sub-artifacts |
| Split and row count | Validation and locked-test surfaces, per source artifact |
| Scorer/view | Purist, Pragmatic, risk coverage, calibration, robustness, operational, semantic entropy |
| Report | `experiments/gan2026_reliability_master_scorecard_2026-06-17.md` |
| Machine-readable output | `experiments/gan2026_reliability_master_scorecard_2026-06-17.json` |
| Claim boundary | Reliability evidence package; locked-test row-level failures are not a development surface |
| Promotion decision | Canonical Gan reliability subject |
| Row-level inspection | Validation row-level artifacts allowed; Gan locked-test row-level inspection is not allowed for development |

Stable hashes:

| Path | SHA-256 |
| --- | --- |
| `experiments/gan2026_reliability_master_scorecard_2026-06-17.md` | `d216037daadb6ecc10115d732d9b937cabdfd6c5634774c117f8b69d4fa03eca` |
| `experiments/gan2026_reliability_master_scorecard_2026-06-17.json` | `4e9851af071441e92119f82d616801d8c09f13f614b584dd0215afce14f08074` |

### ExECTv2 v08 Dev140 Control

| Field | Value |
| --- | --- |
| Candidate | `exectv2_holistic_finding_assembly_v08_dev140` |
| Model | GPT-4.1-mini-family source lanes plus deterministic assembly/lenses |
| Split and row count | `dev140`, 140 letters |
| Scorer/view | `headline_target` clinical headline; companion views include evidence-valid, raw-lane, benchmark/CUI, and fidelity surfaces |
| Config | `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml` |
| Report | `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md` |
| JSON | `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json` |
| JSONL | `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl` |
| Error ledger | `experiments/exectv2_holistic_finding_assembly_v08_error_ledger_dev140_20260621.md` |
| Claim boundary | Dev-only component-attributed architecture evidence; not a benchmark, full-200, or locked-test claim |
| Promotion decision | Current ExECTv2 performance control |
| Row-level inspection | Dev140 row-level inspection allowed; holdout/full-200 row-level inspection not allowed without frozen protocol |

Headline scores: overall `0.9152`; Diagnosis `0.9083`; SeizureFrequency
`0.9053`; Prescription `0.9357`; Investigations `0.9132`.

Stable hashes:

| Path | SHA-256 |
| --- | --- |
| `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml` | `4123e7f3cfe8107ba1cf8f4da968542cf1d9ba35cd29f0ed1b2031d5f539f072` |
| `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json` | `d94964fc18f56b23a390b0531e6a0fdc2d5d10fdfa072b1eaef211ca4e5ae0bf` |
| `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl` | `d2998dcacb06df24a19257b03ee019611a899b2b6291dcb7d77f6c853b3049f4` |
| `experiments/exectv2_holistic_finding_assembly_v08_error_ledger_dev140_20260621.json` | `22ffdec5a67cb2efc18f928e33983ef62faf2c26d333906ae3ecacca2bba02b6` |

### ExECTv2 v09 Partial Hybrid Simplification

| Field | Value |
| --- | --- |
| Candidate | `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` |
| Model | GPT-4.1-mini single-pass Investigations plus focused Diagnosis/SF lanes and deterministic Prescription repair |
| Split and row count | `dev140`, 140 letters |
| Scorer/view | `headline_target` clinical headline |
| Config | `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.yaml` |
| Report | `docs/experiments/exectv2/key_entities/exectv2_v09_single_gpt_simplification_study_dev140_20260621.md` and `experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.md` |
| JSON | `experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.json` |
| JSONL | `experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.jsonl` |
| Claim boundary | Dev-only simplification evidence; not a v08 replacement on all family surfaces |
| Promotion decision | Simplicity control, not performance control |
| Row-level inspection | Dev140 row-level inspection allowed |

Headline scores: overall `0.9059`; Diagnosis `0.9083`; SeizureFrequency
`0.9053`; Prescription `0.9357`; Investigations `0.8549`.

Stable hashes:

| Path | SHA-256 |
| --- | --- |
| `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.yaml` | `b3c80b9bca4e8f37eeb2cb3daba21f89c2c818564c165c04081835313ac9975a` |
| `experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.json` | `111cd7b2fea115666dc8cba1de3a8fbcc4b59833c0b3d5dbad83d7e693507d22` |
| `experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.jsonl` | `9c95388ff034a6bda33507b181779538a86743709de858aca43713816db1438b` |

### ExECTv2 DeepSeek v0.9.16 Dev140 Diagnostic

| Field | Value |
| --- | --- |
| Candidate | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` |
| Model | `deepseek/deepseek-chat` source artifact; no-call same-raw assembly reparse |
| Split and row count | `dev140`, 140 letters |
| Scorer/view | `headline_target` clinical headline |
| Config | `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140.yaml` |
| Source JSONL | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` |
| Report | `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.md` |
| JSON | `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.json` |
| JSONL | `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.jsonl` |
| Error ledger | `experiments/exectv2_v0916_deepseek_reparse_dev140_error_ledger_20260622.md` |
| Claim boundary | `diagnostic-same-raw-deepseek-v0910-through-v0916-dictionary-dev140` |
| Promotion decision | Final hosted non-GPT diagnostic comparator; do not promote |
| Row-level inspection | Dev140 row-level inspection allowed; holdout/full-200 row-level inspection not allowed without frozen protocol |

Headline scores: overall `0.9010`; Diagnosis `0.8828`; SeizureFrequency
`0.8675`; Prescription `0.9430`; Investigations `0.9231`. Companion surfaces:
evidence-valid overall `0.8554`, benchmark raw `0.3445`, benchmark after
CUI/projection `0.3889`, Diagnosis concept-negation `0.8828`, and
SeizureFrequency active-rate fidelity `0.6057`. Assembly lens diagnostics
record zero call failures, zero parse/schema failures, and exact evidence rate
`1.0000`. Gate summary remains `do-not-promote` because Prescription and
Investigations changed-row controls fail despite strong overall performance.

Stable hashes:

| Path | SHA-256 |
| --- | --- |
| `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140.yaml` | `f294f3faf2a14e95d3fe4ffb50dd5f589ffb28a4b83eedc70da46cef28362eed` |
| `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `bd30bfb220ff4fc146b6e38a81d790c839257d7056a31e279330ee6ae32f8dbc` |
| `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.md` | `26aa290febe1d80131603a7a4d8d43af8280315f9c082a083797a5e95fdc7b51` |
| `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.json` | `d068de67bc5ce83d8ae9ebd217a47ae63207be933c2e752ccf9b03d517937a92` |
| `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.jsonl` | `4ccadc9ebd793f19f00c1788fb346c4fda6fb46e9f81e79e8aefa595a89d5fb6` |
| `experiments/exectv2_v0916_deepseek_reparse_dev140_error_ledger_20260622.json` | `3d05abf161a91563ccb4da5d0277c552aecdc250c335e74c2e74ecac3d52e9e4` |

### ExECTv2 Qwen v0.9.22 Dev140 Diagnostic

| Field | Value |
| --- | --- |
| Candidate | `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` |
| Model | `ollama_chat/qwen3.6:35b` source artifact; compact prompt with no-call residual-repair assembly reparse |
| Split and row count | `dev140`, 140 letters |
| Scorer/view | `headline_target` clinical headline |
| Config | `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140.yaml` |
| Source JSONL | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` |
| Report | `experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.md` |
| JSON | `experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.json` |
| JSONL | `experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.jsonl` |
| Error ledger | `experiments/exectv2_v0922_qwencompact_residualrepair_dev140_error_ledger_20260622.md` |
| Claim boundary | `local-qwen-v0910-qwen-compact-live-dev140-ctx12288-maxtok2500-standard-dictionary-residual-repair-v13` |
| Promotion decision | Final local-model diagnostic comparator; do not promote |
| Row-level inspection | Dev140 row-level inspection allowed; holdout/full-200 row-level inspection not allowed without frozen protocol |

Headline scores: overall `0.9001`; Diagnosis `0.8563`; SeizureFrequency
`0.8908`; Prescription `0.9343`; Investigations `0.9579`. Companion surfaces:
evidence-valid overall `0.8567`, benchmark raw `0.2441`, benchmark after
CUI/projection `0.3144`, Diagnosis concept-negation `0.8563`, and
SeizureFrequency active-rate fidelity `0.3618`. Assembly lens diagnostics
record zero call failures, ten parse/schema failures on each shared family
surface, and exact evidence rate `1.0000`. Gate summary remains
`do-not-promote` because Prescription and Investigations changed-row controls
fail and active-rate fidelity remains weak.

Stable hashes:

| Path | SHA-256 |
| --- | --- |
| `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140.yaml` | `6ad15e94611aa5bf4061d7203944345ff9a4b96fd20f3151dc57ac6f0aa82cef` |
| `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `161e3e68b7cb7d67c1fabb0eb479c1de77dd7e9bd36fa6c86b31847b907955a0` |
| `experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.md` | `dffc4151e06aec42ee4e1f0e3daab74acb0e7a9f3594d1c0d6c558a3c5cda903` |
| `experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.json` | `25a7b847c0016de8ff39ab29f251437e5be476a31211f7a0ac7cc06fbaa297f0` |
| `experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.jsonl` | `af0a0e328aba5b5ad14fe64ee03de94a99b259bc28cd51bbfa49f6ec18eb73fe` |
| `experiments/exectv2_v0922_qwencompact_residualrepair_dev140_error_ledger_20260622.json` | `c9334e930a52d27e5b8ba93e9aab45c7e97fcb303a90680b46c78cabfe1ac9d6` |

## Non-Canonical, Scratch, Or Superseded Artifacts

- `experiments/exectv2_holistic_finding_assembly_v097_deepseek_dev25_20260622.*`
  is superseded in the selected evidence set by the final v0.9.16 DeepSeek
  dev140 diagnostic row.
- `experiments/exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25_20260622.*`
  and `experiments/exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25_20260622.*`
  are superseded in the selected evidence set by the final v0.9.22 Qwen dev140
  diagnostic row.
- `experiments/exectv2_holistic_finding_assembly_v098_deepseek_dev25_20260622.*`
  and `experiments/exectv2_holistic_finding_assembly_v098_deepseek_reparse_dev25_20260622.*`
  are superseded diagnostics and are not part of the final selected set.
- Superseded Qwen prompt/profile iterations under
  `experiments/exectv2_llm_only_key_entities_structured_v09*` through `v096*`
  remain scratch or diagnostic unless listed above.
- Dev1/dev5 smoke assemblies are scratch/engineering diagnostics unless linked
  from a promotion report.
- Local logs such as `*.out.log` and `*.err.log` are operational scratch once
  their summary status is captured.

## Pending Refresh Slots

- DeepSeek/Qwen dev140 diagnostics are now indexed as final selected diagnostic
  architecture rows. They do not promote to performance controls.
- Frontend static data and registry rows should be refreshed separately if the
  app is expected to show the final v0.9.16/v0.9.22 dev140 diagnostics.
- Full hashes: stable key artifacts are hashed above. If files are moved,
  copied, or refreshed, update this index before cleanup.
