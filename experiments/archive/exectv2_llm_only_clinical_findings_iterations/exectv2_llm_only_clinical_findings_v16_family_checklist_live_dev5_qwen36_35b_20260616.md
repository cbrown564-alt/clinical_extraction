# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v16_family_checklist_live_dev5_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.16`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Verification call failures: 0
- Parse/schema failures: 0
- Verification parse/schema failures: 0
- First-pass findings: 11
- Verified findings: 11
- Final model findings: 11
- Evidence-invalid dropped: 0
- Format-projected mentions: 11
- CUI-projected mentions: 11
- Evidence validity rate: 1.0000

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.909 (P=0.909 R=0.909); per-letter F1=1.000
- sf_semantic per-item F1=0.909 (P=0.909 R=0.909); per-letter F1=1.000
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.909 (P=0.909 R=0.909); per-letter F1=1.000
- sf_semantic per-item F1=0.909 (P=0.909 R=0.909); per-letter F1=1.000
- sf_benchmark per-item F1=0.909 (P=0.909 R=0.909); per-letter F1=1.000
