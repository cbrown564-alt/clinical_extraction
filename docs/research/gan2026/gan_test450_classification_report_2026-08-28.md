# Gan test450 classification report

Date: 2026-08-28
Status: living class report for five-cell rules; Gemini five-cell select-stop aggregates; historical Sol/Luna appendix
Owner: [five-cell grid](gan_five_cell_grid_2026-08-22.md)
Companion: [Gemini vs Qwen-2.5-14B COT synthetic](gan_gemini_vs_qwen25_14b_cot_synthetic_2026-08-28.md)
Artifact: [gan_test450_classification_report_2026-08-28.json](gan_test450_classification_report_2026-08-28.json)

Split: locked `test` of public `synthetic_data_subset_1500` (`gan2026_split_v1`, n=450).
Not KCH Real(300). Same kind of number as Gan et al. 2026 Tables 4–5: per-class P/R/F1 plus micro-F1.
**Purist micro-F1** is the living primary. **Pragmatic micro-F1** is the companion.
Micro-F1 equals accuracy here (one gold bin, one predicted bin). Accuracy is not printed.
Gold and predicted ε only; no letter text, no row ids.

## Living

Living selected Gan results are **Gemini 3.7 Flash five-cell (select stop)**, prompt v0.5.
The living per-class tables are **five-cell rules** (same cell as Gemini five-cell cell 1).
Gemini five-cell select-stop **Purist micro-F1** aggregates are living.

Decision 0050 / Sol 380/450 / 381/450 are **historical**.
Sol hybrid, Luna llm-only, and the old "Micro-F1 across cells" hybrid/`gan_llm_only` table are **historical** (current-stack / `gan_llm_only`), not the paper comparison.

Gemini five-cell **per-class** P/R is not on disk in
`paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`.
It is not computed here from sealed test450 predicted-label ledgers.

### Gemini five-cell select stop (Purist micro-F1, n=450)

Source: `paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`.
Purist counts only in that sidecar.

| Recognise | Encode | Select | Purist micro-F1 |
| --- | --- | --- | ---: |
| rules | rules | rules | 329/450 = 0.7311 cited 0.73 |
| both | rules | rules | 368/450 = 0.82 |
| LLM | rules | rules (cell 3) | 373/450 = 0.8289 cited 0.83 |
| LLM | LLM | rules | 368/450 = 0.82 |
| LLM | LLM | LLM | 357/450 = 0.79 |

### Already-recorded Pragmatic micro-F1 for those cells

Rules Pragmatic is 341/450 = 0.7578 from this class report (and
[rules-only test450 aggregate](rules_only_test450_aggregate_2026-08-10.md)).
Cell 3 and cell 4 Pragmatic are already recorded on
[codebook-encode holdout](gan_codebook_encode_holdout_2026-08-22.md)
(codebook then select; Select only). Both / rules / rules and LLM / LLM / LLM
Pragmatic select-stop aggregates are **not** already recorded. Those cells are left blank.
Do not invent the missing Gemini five-cell Pragmatic numbers.

| Recognise | Encode | Select | Pragmatic micro-F1 |
| --- | --- | --- | ---: |
| rules | rules | rules | 341/450 = 0.7578 |
| both | rules | rules | — not recorded |
| LLM | rules | rules (cell 3) | 382/450 = 0.8489 cited 0.85 |
| LLM | LLM | rules | 377/450 = 0.8378 cited 0.84 |
| LLM | LLM | LLM | — not recorded |

### rules (living five-cell rules cell)

_rules_only; n=450; dropped=0. Same cell as Gemini five-cell cell 1._

#### Purist

```
Class            Precision    Recall    F1-score   Support
<1/6M              1.0000    0.6667    0.8000         6
=1/6M              0.5000    1.0000    0.6667         1
(1/6M,1/M)         0.7963    0.8269    0.8113        52
=1/M               0.6000    0.4500    0.5143        20
(1/M,1/W)          0.8246    0.7581    0.7899        62
=1/W               0.8571    1.0000    0.9231         6
(1/W,1/D)          0.9167    0.7857    0.8462        98
≥1/D               0.6857    0.6667    0.6761        36
UNK                0.5797    0.7843    0.6667       102
NS                 0.7037    0.5672    0.6281        67
micro-F1           0.7311    0.7311    0.7311       450
macro avg          0.7464    0.7506    0.7322       450
weighted avg       0.7488    0.7311    0.7329       450
```

#### Pragmatic

```
Class            Precision    Recall    F1-score   Support
infrequent         0.7867    0.7468    0.7662        79
frequent           0.8962    0.8119    0.8519       202
UNK                0.5797    0.7843    0.6667       102
NS                 0.7037    0.5672    0.6281        67
micro-F1           0.7578    0.7578    0.7578       450
macro avg          0.7416    0.7275    0.7282       450
weighted avg       0.7766    0.7578    0.7616       450
```

Purist UNK support in this table is 102/450 (22.7%). That is the scored UNK class, not gold-kind `unknown` alone (60/450 in [dataset gold support](../paper/dataset_gold_support_2026-08-22.md)).

## Historical appendix

Sol hybrid and Luna llm-only per-class tables are kept as a historical appendix.
They are current-stack / `gan_llm_only`, not living selected results.

### Sol hybrid (historical)

_llm_with_rules / gpt56sol / current-stack; n=450; dropped=0_

#### Purist

```
Class            Precision    Recall    F1-score   Support
<1/6M              0.5714    0.6667    0.6154         6
=1/6M              0.0000    0.0000    0.0000         1
(1/6M,1/M)         0.8205    0.6154    0.7033        52
=1/M               0.8261    0.9500    0.8837        20
(1/M,1/W)          0.8361    0.8226    0.8293        62
=1/W               0.8333    0.8333    0.8333         6
(1/W,1/D)          0.9681    0.9286    0.9479        98
≥1/D               0.9211    0.9722    0.9459        36
UNK                0.7589    0.8333    0.7944       102
NS                 0.8676    0.8806    0.8741        67
micro-F1           0.8467    0.8467    0.8467       450
macro avg          0.7403    0.7503    0.7427       450
weighted avg       0.8512    0.8467    0.8464       450
```

#### Pragmatic

```
Class            Precision    Recall    F1-score   Support
infrequent         0.8310    0.7468    0.7867        79
frequent           0.9497    0.9356    0.9426       202
UNK                0.7589    0.8333    0.7944       102
NS                 0.8676    0.8806    0.8741        67
micro-F1           0.8711    0.8711    0.8711       450
macro avg          0.8518    0.8491    0.8494       450
weighted avg       0.8734    0.8711    0.8714       450
```

### Luna llm-only (historical)

_llm / gpt56luna; n=450; dropped=0. `gan_llm_only` is not a results column._

#### Purist

```
Class            Precision    Recall    F1-score   Support
<1/6M              1.0000    0.3333    0.5000         6
=1/6M              0.0000    0.0000    0.0000         1
(1/6M,1/M)         0.6765    0.4423    0.5349        52
=1/M               0.6667    0.5000    0.5714        20
(1/M,1/W)          0.8333    0.4839    0.6122        62
=1/W               0.6000    0.5000    0.5455         6
(1/W,1/D)          0.8737    0.8469    0.8601        98
≥1/D               0.9118    0.8611    0.8857        36
UNK                0.5796    0.8922    0.7027       102
NS                 0.7826    0.8060    0.7941        67
micro-F1           0.7267    0.7267    0.7267       450
macro avg          0.6924    0.5666    0.6007       450
weighted avg       0.7551    0.7267    0.7212       450
```

#### Pragmatic

```
Class            Precision    Recall    F1-score   Support
infrequent         0.7222    0.4937    0.5865        79
frequent           0.9529    0.8020    0.8710       202
UNK                0.5796    0.8922    0.7027       102
NS                 0.7826    0.8060    0.7941        67
micro-F1           0.7689    0.7689    0.7689       450
macro avg          0.7593    0.7484    0.7386       450
weighted avg       0.8025    0.7689    0.7714       450
```

### Historical Micro-F1 across cells (current-stack / `gan_llm_only`)

Not the paper comparison. `gan_llm_only` is not a results column.
Sol / current-stack hybrid fills stay historical.

| Cell | n | Purist micro-F1 | Pragmatic micro-F1 |
| --- | ---: | ---: | ---: |
| rules | 450 | 0.7311 | 0.7578 |
| Sol hybrid | 450 | 0.8467 | 0.8711 |
| Luna hybrid | 448 | 0.8170 | 0.8438 |
| Gemini hybrid | 450 | 0.8311 | 0.8578 |
| DeepSeek hybrid | 450 | 0.8133 | 0.8333 |
| Gemma hybrid | 449 | 0.8018 | 0.8396 |
| Qwen hybrid | 449 | 0.8040 | 0.8463 |
| Luna llm-only | 450 | 0.7267 | 0.7689 |
| Gemini llm-only | 440 | 0.7159 | 0.7545 |
| Grok llm-only | 450 | 0.7267 | 0.7600 |
| DeepSeek llm-only | 450 | 0.7489 | 0.7889 |

Gan et al. 2026 abstract (Real(300), 15k synthetic train): Purist 0.788 / Pragmatic 0.847 (Qwen-2.5-14B); MedGemma-4B 0.787 / 0.858.
Those numbers are a different test set. Do not quote them as the same experiment.
The equivalent synthetic-to-synthetic row is in
[Gemini vs Qwen-2.5-14B COT synthetic](gan_gemini_vs_qwen25_14b_cot_synthetic_2026-08-28.md).
