# ExECTv2 LLM-Only All Entities Full-200 Rescore Summary

- Rescore type: diagnostic no-call reparse through updated scorer/reporting code
- JSONL: `experiments\exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl`
- Report: `experiments\exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.md`
- Letters: 200
- Call failures: 0
- Parse/schema failures: 0
- Evidence-invalid dropped: 101
- Evidence validity rate: 0.9323

## Headline Scores

| Layer | Item F1 | Item TP | Item FP | Item FN | Letter F1 | Letter TP | Letter FP | Letter FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| semantic | 0.1154 | 201 | 1190 | 1891 | 0.2993 | 176 | 115 | 709 |
| benchmark | 0.0000 | 0 | 1391 | 2092 | 0.0000 | 0 | 115 | 885 |
| phrase_only | 0.1470 | 256 | 1135 | 1836 | 0.3620 | 221 | 115 | 664 |

## Diagnostic Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.5019 | 874 | 517 | 1218 | 0.5686 (497/874) |
