# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v15_hard_negative_live_dev25_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.15`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Verification call failures: 0
- Parse/schema failures: 0
- Verification parse/schema failures: 0
- First-pass findings: 33
- Verified findings: 27
- Final model findings: 27
- Evidence-invalid dropped: 0
- Format-projected mentions: 27
- CUI-projected mentions: 27
- Evidence validity rate: 1.0000

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.759 (P=0.815 R=0.710); per-letter F1=0.929
- sf_semantic per-item F1=0.724 (P=0.778 R=0.677); per-letter F1=0.889
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.759 (P=0.815 R=0.710); per-letter F1=0.929
- sf_semantic per-item F1=0.724 (P=0.778 R=0.677); per-letter F1=0.889
- sf_benchmark per-item F1=0.724 (P=0.778 R=0.677); per-letter F1=0.889
