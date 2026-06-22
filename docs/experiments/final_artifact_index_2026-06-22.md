# Final Artifact Index

Date: 2026-06-22

Scope: Phase 0 closeout index for the final comparison set across Gan 2026,
ExECTv2 GPT-4.1-mini controls, DeepSeek diagnostics, and Qwen diagnostics.

This index freezes the evidence spine before any repository simplification. It
does not authorize deleting, moving, or renaming canonical artifacts. It also
does not promote dev25 diagnostics to dev140, full-200, locked-test, or
benchmark claims.

## Claim Boundary

- Gan 2026 reliability artifacts remain the mature reliability package.
- ExECTv2 v08 and v09 partial hybrid are dev140 component-attributed controls.
- DeepSeek and Qwen rows are dev25 diagnostic cross-model evidence unless a
  later predeclared gate promotes them.
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

### ExECTv2 DeepSeek v0.9.7 Dev25 Diagnostic

| Field | Value |
| --- | --- |
| Candidate | `exectv2_holistic_finding_assembly_v097_deepseek_dev25` |
| Model | `deepseek/deepseek-chat` |
| Split and row count | `dev25`, 25 letters |
| Scorer/view | `headline_target` clinical headline |
| Config | `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v097_deepseek_dev25.yaml` |
| Source JSONL | `experiments/exectv2_llm_only_key_entities_structured_v097_dev25_deepseek_chat_20260622.jsonl` |
| Report | `experiments/exectv2_holistic_finding_assembly_v097_deepseek_dev25_20260622.md` |
| JSON | `experiments/exectv2_holistic_finding_assembly_v097_deepseek_dev25_20260622.json` |
| JSONL | `experiments/exectv2_holistic_finding_assembly_v097_deepseek_dev25_20260622.jsonl` |
| Claim boundary | Hosted-DeepSeek v0.9.7 live dev25 diagnostic |
| Promotion decision | Diagnostic comparator; not a v08 replacement |
| Row-level inspection | Dev25 row-level inspection allowed |

Headline scores: overall `0.8707`; Diagnosis `0.8456`; SeizureFrequency
`0.7586`; Prescription `0.9610`; Investigations `0.9091`. Assembly lens
diagnostics record zero call failures, zero parse/schema failures, and exact
evidence rate `1.0000`.

Stable hashes:

| Path | SHA-256 |
| --- | --- |
| `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v097_deepseek_dev25.yaml` | `5142093422ec652e062f04f6970280d9fe5cd868edc745c8117a8d7bb127e487` |
| `experiments/exectv2_llm_only_key_entities_structured_v097_dev25_deepseek_chat_20260622.jsonl` | `b18528d3a27c827b2f4ea722e6997a7851f0e9bf2ff3d4e74417b9f0779355ae` |
| `experiments/exectv2_holistic_finding_assembly_v097_deepseek_dev25_20260622.json` | `190c4a55fbccec4d21a0840ca0576a4865a2ca7f5757e59715347c209e45c6c5` |
| `experiments/exectv2_holistic_finding_assembly_v097_deepseek_dev25_20260622.jsonl` | `23f2018acdb8e75e345ae18124b02a40b7dd11c43f2bb637fce56900c58c0c36` |

### ExECTv2 Qwen Diagnostic Rows

#### Best Completed No-Call Reparse

| Field | Value |
| --- | --- |
| Candidate | `exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25` |
| Model | `ollama_chat/qwen3.6:35b` source artifact, no-call schema-repair reparse |
| Split and row count | `dev25`, 25 letters |
| Scorer/view | `headline_target` clinical headline |
| Config | `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25.yaml` |
| Source JSONL | `experiments/exectv2_llm_only_key_entities_structured_v096_schema_repair_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` |
| Report | `experiments/exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25_20260622.md` |
| JSON/JSONL | `experiments/exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25_20260622.json`, `experiments/exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25_20260622.jsonl` |
| Claim boundary | Diagnostic no-call local-Qwen reparse |
| Promotion decision | Do not promote |
| Row-level inspection | Dev25 row-level inspection allowed |

Headline scores: overall `0.8082`; Diagnosis `0.8112`; SeizureFrequency
`0.6429`; Prescription `0.8608`; Investigations `0.9268`.

#### Latest Completed Compact Dict-Repair Run

| Field | Value |
| --- | --- |
| Candidate | `exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25` |
| Model | `ollama_chat/qwen3.6:35b` |
| Split and row count | `dev25`, 25 letters |
| Scorer/view | `headline_target` clinical headline |
| Source JSONL | `experiments/exectv2_llm_only_key_entities_structured_v097_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_dictrepair_20260622.jsonl` |
| Report | `experiments/exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25_20260622.md` |
| JSON | `experiments/exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25_20260622.json` |
| JSONL | `experiments/exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25_20260622.jsonl` |
| Claim boundary | Local-Qwen v0.9.7 qwen-compact live dev25 with ctx12288, max_tokens2500, standard dictionary repair |
| Promotion decision | Do not promote |
| Row-level inspection | Dev25 row-level inspection allowed |

Headline scores: overall `0.7995`; Diagnosis `0.7755`; SeizureFrequency
`0.5882`; Prescription `0.9487`; Investigations `0.8163`. Lens diagnostics
record one parse/schema failure in each family surface and exact evidence rate
`1.0000`.

Stable hashes:

| Path | SHA-256 |
| --- | --- |
| `experiments/exectv2_llm_only_key_entities_structured_v097_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_dictrepair_20260622.jsonl` | `a6d0ee782c527be976277e5a90a2d78a3cd1fac8c4d5976a863d849a4d36b0fd` |
| `experiments/exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25_20260622.json` | `db0d27936ce9a4f7726a4a2d53a7f02fc7423689b8dd02e78b6f5a0a4ee26d5e` |
| `experiments/exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25_20260622.jsonl` | `67665a3492ad6038721e86af1ec2a6310b5bf299f9d615b4554eb8848d21aae9` |

## Non-Canonical, Scratch, Or Superseded Artifacts

- `experiments/exectv2_holistic_finding_assembly_v098_deepseek_dev25_20260622.*`
  and `experiments/exectv2_holistic_finding_assembly_v098_deepseek_reparse_dev25_20260622.*`
  are diagnostic successors observed in the repo, but Phase 0 keeps v0.9.7 as
  the indexed DeepSeek row named by the consolidation plan. Review them before
  any replacement or paper table update.
- Superseded Qwen prompt/profile iterations under
  `experiments/exectv2_llm_only_key_entities_structured_v09*` through `v096*`
  remain scratch or diagnostic unless listed above.
- Dev1/dev5 smoke assemblies are scratch/engineering diagnostics unless linked
  from a promotion report.
- Local logs such as `*.out.log` and `*.err.log` are operational scratch once
  their summary status is captured.

## Pending Refresh Slots

- DeepSeek dev140: no escalation is authorized by this index. A dev140 run needs
  a written purpose, scorer surface, stop rule, and row-inspection boundary.
- Qwen dev25/dev140: the latest completed compact dict-repair dev25 row is
  diagnostic and not promotion evidence. Further Qwen iteration should stop
  unless a predeclared portability question justifies it.
- Full hashes: stable key artifacts are hashed above. If files are moved,
  copied, or refreshed, update this index before cleanup.

