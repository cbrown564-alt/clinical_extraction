# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v16_family_checklist_live_dev10_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.16`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 10

## Gate Summary

- Call failures: 0
- Verification call failures: 0
- Parse/schema failures: 0
- Verification parse/schema failures: 0
- First-pass findings: 22
- Verified findings: 21
- Final model findings: 21
- Evidence-invalid dropped: 0
- Format-projected mentions: 21
- CUI-projected mentions: 21
- Evidence validity rate: 1.0000

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.791 (P=0.809 R=0.773); per-letter F1=1.000
- sf_semantic per-item F1=0.744 (P=0.762 R=0.727); per-letter F1=1.000
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.791 (P=0.809 R=0.773); per-letter F1=1.000
- sf_semantic per-item F1=0.744 (P=0.762 R=0.727); per-letter F1=1.000
- sf_benchmark per-item F1=0.744 (P=0.762 R=0.727); per-letter F1=1.000
