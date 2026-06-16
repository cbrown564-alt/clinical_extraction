# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_target_status_v2_live_dev5_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.8`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Verification call failures: 0
- Parse/schema failures: 0
- Verification parse/schema failures: 0
- First-pass findings: 12
- Verified findings: 9
- Final model findings: 9
- Evidence-invalid dropped: 1
- Format-projected mentions: 8
- CUI-projected mentions: 8
- Evidence validity rate: 0.8889

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.842 (P=1.000 R=0.727); per-letter F1=0.889
- sf_semantic per-item F1=0.842 (P=1.000 R=0.727); per-letter F1=0.889
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.842 (P=1.000 R=0.727); per-letter F1=0.889
- sf_semantic per-item F1=0.842 (P=1.000 R=0.727); per-letter F1=0.889
- sf_benchmark per-item F1=0.842 (P=1.000 R=0.727); per-letter F1=0.889
