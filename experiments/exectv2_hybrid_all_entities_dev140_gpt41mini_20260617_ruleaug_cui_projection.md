# ExECTv2 Benchmark CUI-Projection Ablation

- Source: `experiments\exectv2_hybrid_all_entities_dev140_gpt41mini_20260617_ruleaug.jsonl`

CUI projection is a deterministic post-step; the benchmark (with-CUI) headline minus the semantic (CUI-dropped) headline is its credit, never LLM clinical reasoning. Closing a coverage gap is in-sample CUI lookup, a documented projection artifact.

| Entity | Pred | CUI coverage | Gold CUI density | Overlaps | CUI agreement | CUIPhrase agreement |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 47 | 0.81 (38/47) | 1.00 (31/31) | 30 | 0.82 (18/22) | 0.77 (17/22) |
| Diagnosis | 263 | 0.68 (180/263) | 1.00 (404/405) | 186 | 0.61 (80/132) | 0.65 (86/132) |
| EpilepsyCause | 74 | 0.39 (29/74) | 1.00 (21/21) | 19 | 1.00 (14/14) | 0.86 (12/14) |
| Investigations | 265 | 0.94 (249/265) | 1.00 (136/136) | 132 | 0.76 (100/131) | 0.61 (80/131) |
| Onset | 96 | 0.47 (45/96) | 1.00 (17/17) | 15 | 1.00 (11/11) | 1.00 (11/11) |
| PatientHistory | 517 | 0.45 (233/517) | 1.00 (466/466) | 244 | 0.89 (141/159) | 0.76 (121/159) |
| Prescription | 426 | 0.99 (420/426) | 1.00 (206/206) | 196 | 0.99 (193/194) | 0.99 (192/194) |
| SeizureFrequency | 340 | 0.86 (291/340) | 1.00 (187/187) | 174 | 0.81 (133/165) | 0.65 (107/165) |
| WhenDiagnosed | 55 | 1.00 (55/55) | 1.00 (11/11) | 11 | 1.00 (11/11) | 1.00 (11/11) |
| overall | 2083 | 0.74 (1540/2083) | 1.00 (1479/1480) | 1007 | 0.84 (701/839) | 0.76 (637/839) |
