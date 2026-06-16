# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v15_hard_negative_live_dev140_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.15`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Verification call failures: 0
- Parse/schema failures: 0
- Verification parse/schema failures: 4
- First-pass findings: 238
- Verified findings: 196
- Final model findings: 203
- Evidence-invalid dropped: 9
- Format-projected mentions: 194
- CUI-projected mentions: 194
- Evidence validity rate: 0.9557

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.488 (P=0.479 R=0.497); per-letter F1=0.772
- sf_semantic per-item F1=0.304 (P=0.299 R=0.310); per-letter F1=0.522
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.488 (P=0.479 R=0.497); per-letter F1=0.772
- sf_semantic per-item F1=0.304 (P=0.299 R=0.310); per-letter F1=0.522
- sf_benchmark per-item F1=0.304 (P=0.299 R=0.310); per-letter F1=0.522
