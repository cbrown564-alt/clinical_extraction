# Gan 2026 six-model post-panel replay and component audit

Generated: 2026-07-20T09:01:11.607176+00:00

Development evidence on `validation750`; no model calls or test rows were used.

## Replay result

| Model | Method | Original valid | Replay valid | Recovered | Answer changes | Rules-correct regressions |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| gpt41mini | `llm_with_rules` | 749/750 | 750/750 | 1 | 0 | 82 |
| gpt41mini | `llm_only` | 750/750 | 750/750 | 0 | 0 | 155 |
| gpt56luna | `llm_with_rules` | 745/750 | 747/750 | 2 | 0 | 91 |
| gpt56luna | `llm_only` | 750/750 | 750/750 | 0 | 0 | 173 |
| gpt56sol | `llm_with_rules` | 750/750 | 750/750 | 0 | 0 | 78 |
| gpt56sol | `llm_only` | 750/750 | 750/750 | 0 | 0 | 141 |
| deepseek_v4_flash | `llm_with_rules` | 749/750 | 750/750 | 1 | 0 | 87 |
| deepseek_v4_flash | `llm_only` | 750/750 | 750/750 | 0 | 0 | 173 |
| qwen36_35b | `llm_with_rules` | 747/750 | 749/750 | 2 | 0 | 69 |
| qwen36_35b | `llm_only` | 735/750 | 735/750 | 0 | 0 | 168 |
| gemma4_26b | `llm_with_rules` | 742/750 | 747/750 | 5 | 0 | 89 |
| gemma4_26b | `llm_only` | 687/750 | 687/750 | 0 | 0 | 215 |

## Score-layer and evidence ladder

| Model | Method | Model boundary correct | Final correct | Model → final changes | Exact evidence |
| --- | --- | ---: | ---: | ---: | ---: |
| gpt41mini | `llm_with_rules` | 333/750 | 653/750 | 544 | 693/750 |
| gpt41mini | `llm_only` | 435/750 | 577/750 | 359 | 702/750 |
| gpt56luna | `llm_with_rules` | 364/750 | 646/750 | 490 | 739/750 |
| gpt56luna | `llm_only` | 445/750 | 558/750 | 258 | 710/750 |
| gpt56sol | `llm_with_rules` | 268/750 | 655/750 | 596 | 750/750 |
| gpt56sol | `llm_only` | 468/750 | 590/750 | 374 | 740/750 |
| deepseek_v4_flash | `llm_with_rules` | 420/750 | 643/750 | 443 | 738/750 |
| deepseek_v4_flash | `llm_only` | 432/750 | 559/750 | 247 | 674/750 |
| qwen36_35b | `llm_with_rules` | 331/750 | 667/750 | 537 | 582/750 |
| qwen36_35b | `llm_only` | 405/750 | 565/750 | 267 | 567/750 |
| gemma4_26b | `llm_with_rules` | 389/750 | 646/750 | 466 | 718/750 |
| gemma4_26b | `llm_only` | 352/750 | 512/750 | 352 | 675/750 |

## Matched method transitions

| Model | Rules rescue | Rules regression | Both correct | Both wrong | Changed rows with valid evidence |
| --- | ---: | ---: | ---: | ---: | ---: |
| gpt41mini | 110 | 34 | 543 | 63 | 128 |
| gpt56luna | 120 | 32 | 526 | 72 | 138 |
| gpt56sol | 96 | 31 | 559 | 64 | 126 |
| deepseek_v4_flash | 115 | 31 | 528 | 76 | 123 |
| qwen36_35b | 125 | 23 | 542 | 60 | 72 |
| gemma4_26b | 168 | 34 | 478 | 70 | 145 |

## First failure owner

- `none`: 6799
- `llm_clinical_selection`: 1449
- `evidence_selection`: 616
- `format_or_schema`: 84
- `deterministic_semantic`: 40
- `model_transport`: 12

## Clinical subproblem distribution

- `rate_denominator`: 3919
- `cluster_or_diary_aggregation`: 1714
- `seizure_free_boundary`: 1575
- `uncertainty_boundary`: 844
- `temporal_selection`: 477
- `competing_event_selection`: 471

## Changed-row ownership

| Model | Model clinical selection | Deterministic semantic |
| --- | ---: | ---: |
| gpt41mini | 13 | 131 |
| gpt56luna | 14 | 138 |
| gpt56sol | 2 | 125 |
| deepseek_v4_flash | 23 | 123 |
| qwen36_35b | 16 | 132 |
| gemma4_26b | 52 | 150 |

## Interpretation

The replay is accepted only if selected-answer changes remain zero. Recovered records are attributed to bounded format/schema repair, not clinical reasoning. Matched method gains are development evidence and retain every deterministic regression and evidence failure in the machine artifact.

## Claim boundary

Development component evidence for the named validation split and frozen routes; not holdout evidence, clinical validation, or a model-neutral ranking.
