# Gan 2026 Staged Hybrid Assembly No-Call Replay

This report assembles saved component artifacts only. It makes no live model calls and does not authorize locked-test inspection, whole-pipeline promotion, or benchmark-comparable language.

## Coverage

The joined assembly has 75 source rows. Selected-state union and suspicious routing cover 75 and 75 rows respectively. The promoted verifier saved replay covers 42 rows, so verifier impact is currently a slice readout, not a full validation750 readout.

## Claim Boundary

Validation-development assembly replay over saved artifacts only. No new live LLM calls, locked-test inspection, whole-pipeline promotion, or benchmark-comparable claim.

## Artifacts

- Assembly JSONL: `experiments/gan2026_staged_hybrid_assembly_no_call_replay_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_staged_hybrid_assembly_no_call_replay_2026-06-04.json`

## Metrics

| Metric | Value |
| --- | ---: |
| selected state rows | 75 |
| suspicious routing rows | 75 |
| projection source id inconsistent rows | 0 |
| suspicious state rows | 44 |
| suspicious route review rows | 9 |
| suspicious route unknown rows | 35 |
| selective verifier rows | 42 |
| selective verifier w to c rows | 7 |
| selective verifier c to w rows | 1 |
| selective verifier c to review rows | 10 |
| selective verifier w to review rows | 3 |
| assembly rows | 75 |
| assembly rows with selected state union | 75 |
| assembly rows with suspicious routing | 75 |
| assembly rows with selective verifier | 42 |

## Component Outputs

| Component | Owner | Rows |
| --- | --- | ---: |
| `selected_state_union` | `hybrid_selected_state_union` | 75 |
| `suspicious_state_routing` | `deterministic_suspicious_state_policy` | 75 |
| `selective_verifier` | `llm_selective_verifier` | 42 |

## Verifier Regression Boundary

The saved promoted-verifier slice still contains C->W rows versus routing: 7168. These remain visible and must be adjudicated or gated before any automatic prediction-bearing full-validation use.
