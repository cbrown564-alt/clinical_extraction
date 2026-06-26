# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v11_live_dev10_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.11`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 10

## Gate Summary

- Call failures: 0
- Verification call failures: 0
- Parse/schema failures: 0
- Verification parse/schema failures: 0
- First-pass findings: 21
- Verified findings: 23
- Final model findings: 23
- Evidence-invalid dropped: 4
- Format-projected mentions: 19
- CUI-projected mentions: 19
- Evidence validity rate: 0.8261

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.829 (P=0.895 R=0.773); per-letter F1=1.000
- sf_semantic per-item F1=0.829 (P=0.895 R=0.773); per-letter F1=1.000
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.829 (P=0.895 R=0.773); per-letter F1=1.000
- sf_semantic per-item F1=0.829 (P=0.895 R=0.773); per-letter F1=1.000
- sf_benchmark per-item F1=0.829 (P=0.895 R=0.773); per-letter F1=1.000
