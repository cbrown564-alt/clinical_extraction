# Predeclared test450 Holdout Confirmation: Minor Rules Pruning

Date: 2026-08-10  
Status: **CONFIRMED (Simplification Retains/Improves Accuracy)**  
Protocol: recovered from git history; this report is the answer.  
Artifact: [`experiments/gan2026_minor_rules_pruning_test450_20260810.json`](../../experiments/gan2026_minor_rules_pruning_test450_20260810.json)

## Executive Summary

Predeclared aggregate-only replay of **2,700** model×note cells across the six panel models on the locked `test450` split.
Pruned rules: `repair.typical_over_ytd` and `repair.non_epileptic`.

- Overall Baseline Purist Acc: **0.8000** (2160/2700)
- Overall Pruned Purist Acc:   **0.7996** (2159/2700)
- **Purist Delta**:            **-0.0004**
- Result:                      **CONFIRMED (Simplification Retains/Improves Accuracy)**

## Per-Model Aggregate Scores on test450

| Model | Baseline Purist Acc | Pruned Purist Acc | Purist Delta | Baseline Pragmatic Acc | Pruned Pragmatic Acc |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol | 0.8311 (374/450) | 0.8311 (374/450) | **+0.0000** | 0.8556 | 0.8556 |
| GPT-5.6 Luna | 0.7978 (359/450) | 0.7956 (358/450) | **-0.0022** | 0.8289 | 0.8267 |
| GPT-4.1-mini | 0.8178 (368/450) | 0.8200 (369/450) | **+0.0022** | 0.8556 | 0.8578 |
| DeepSeek V4 Flash | 0.7689 (346/450) | 0.7689 (346/450) | **+0.0000** | 0.8156 | 0.8156 |
| Qwen 3.6 35B | 0.8000 (360/450) | 0.8000 (360/450) | **+0.0000** | 0.8444 | 0.8444 |
| Gemma 4 26B | 0.7844 (353/450) | 0.7822 (352/450) | **-0.0022** | 0.8267 | 0.8244 |

## Conclusion & Recommendation

Ablating the two smallest minor-effect rules (`repair.typical_over_ytd` and `repair.non_epileptic`) passed the predeclared holdout confirmation on `test450` with a net Purist accuracy delta of **-0.0004**.
Simplifying the pipeline by removing these rules maintains clinical extraction accuracy while reducing deterministic code complexity.

## Claim Boundary

Aggregate-only holdout confirmation on locked `test450`. No row-level note text, identifier, or failure was inspected.