# ExECTv2 Benchmark CUI-Projection Ablation

- Source: `experiments\exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl`

CUI projection is a deterministic post-step; the benchmark (with-CUI) headline minus the semantic (CUI-dropped) headline is its credit, never LLM clinical reasoning. Closing a coverage gap is in-sample CUI lookup, a documented projection artifact.

| Entity | Pred | CUI coverage | Gold CUI density | Overlaps | CUI agreement | CUIPhrase agreement |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 26 | 0.65 (17/26) | 1.00 (31/31) | 25 | 0.82 (14/17) | 0.71 (12/17) |
| Diagnosis | 154 | 0.46 (71/154) | 1.00 (404/405) | 124 | 0.80 (56/70) | 0.91 (64/70) |
| EpilepsyCause | 59 | 0.24 (14/59) | 1.00 (21/21) | 17 | 1.00 (12/12) | 0.83 (10/12) |
| Investigations | 178 | 0.92 (163/178) | 1.00 (136/136) | 121 | 0.82 (98/120) | 0.65 (78/120) |
| Onset | 91 | 0.44 (40/91) | 1.00 (17/17) | 14 | 1.00 (10/10) | 1.00 (10/10) |
| PatientHistory | 380 | 0.25 (96/380) | 1.00 (466/466) | 168 | 0.92 (76/83) | 0.76 (63/83) |
| Prescription | 230 | 0.97 (224/230) | 1.00 (206/206) | 186 | 0.99 (183/184) | 0.99 (183/184) |
| SeizureFrequency | 164 | 0.74 (121/164) | 1.00 (187/187) | 116 | 0.85 (91/107) | 0.66 (71/107) |
| WhenDiagnosed | 44 | 1.00 (44/44) | 1.00 (11/11) | 11 | 1.00 (11/11) | 1.00 (11/11) |
| overall | 1326 | 0.60 (790/1326) | 1.00 (1479/1480) | 782 | 0.90 (551/614) | 0.82 (502/614) |
