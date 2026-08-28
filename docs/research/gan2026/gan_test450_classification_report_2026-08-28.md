# Gan test450 classification report

Date: 2026-08-28
Status: living Gemini five-cell per-class tables for cells 1, 3, and 5
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
The paper per-class tables are cells **1** (rules / rules / rules), **3** (LLM / rules / rules), and **5** (LLM / LLM / LLM).

Decision 0050 / Sol 380/450 / 381/450 are **historical**.
Sol hybrid, Luna llm-only, and the old "Micro-F1 across cells" hybrid/`gan_llm_only` table are **historical** (current-stack / `gan_llm_only`), not the paper comparison.

### Gemini five-cell select stop (Purist micro-F1, n=450)

Living gold is `gold_monthly_frequency` from the current label parser
(Purist UNK support 76/450). Cell 1 is a no-call living rules replay.
The curated sidecar
`paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`
uses the same gold.

| Recognise | Encode | Select | Purist micro-F1 |
| --- | --- | --- | ---: |
| rules | rules | rules | 321/450 = 0.7133 |
| both | rules | rules | 368/450 = 0.8178 cited 0.82 |
| LLM | rules | rules (cell 3) | 373/450 = 0.8289 cited 0.83 |
| LLM | LLM | rules | 368/450 = 0.8178 cited 0.82 |
| LLM | LLM | LLM | 357/450 = 0.7933 cited 0.79 |

### Pragmatic micro-F1 for those cells

Same living gold. Cell 2 is the select stop on saved
`gan_llm_and_rules_extract` (also in that cell's `comparison.json` /
`rule_stops.json`). Cell 5 is the table below.

| Recognise | Encode | Select | Pragmatic micro-F1 |
| --- | --- | --- | ---: |
| rules | rules | rules | 341/450 = 0.7578 |
| both | rules | rules | 380/450 = 0.8444 |
| LLM | rules | rules (cell 3) | 382/450 = 0.8489 cited 0.85 |
| LLM | LLM | rules | 377/450 = 0.8378 cited 0.84 |
| LLM | LLM | LLM | 369/450 = 0.8200 |

### Cell 1 — rules / rules / rules

_Living `gan_rules.run_record`; n=450; dropped=0._
Gold ε is living `gold_monthly_frequency` (Purist UNK support 76/450),
the same bins as cells 3 and 5. See
[dataset gold support](../paper/dataset_gold_support_2026-08-22.md).

#### Purist

```
Class            Precision    Recall    F1-score   Support
<1/6M              1.0000    0.6667    0.8000         6
=1/6M              0.5000    1.0000    0.6667         1
(1/6M,1/M)         0.8000    0.8000    0.8000        55
=1/M               0.5385    0.3889    0.4516        18
(1/M,1/W)          0.7966    0.8103    0.8034        58
=1/W               0.8333    1.0000    0.9091         5
(1/W,1/D)          0.9271    0.7236    0.8128       123
≥1/D               0.6341    0.6341    0.6341        41
UNK                0.5042    0.7895    0.6154        76
NS                 0.6909    0.5672    0.6230        67
micro-F1           0.7133    0.7133    0.7133       450
macro avg          0.7225    0.7380    0.7116       450
weighted avg       0.7449    0.7133    0.7183       450
```

#### Pragmatic

```
Class            Precision    Recall    F1-score   Support
infrequent         0.7838    0.7250    0.7532        80
frequent           0.9158    0.8150    0.8625       227
UNK                0.5042    0.7895    0.6154        76
NS                 0.6909    0.5672    0.6230        67
micro-F1           0.7578    0.7578    0.7578       450
macro avg          0.7237    0.7242    0.7135       450
weighted avg       0.7894    0.7578    0.7657       450
```

### Cell 3 — LLM / rules / rules

_Gemini 3.7 Flash; `gan_llm_extract` then `llm_select_after_codebook`; n=450; dropped=0._
Gold ε is living `gold_monthly_frequency` (Purist UNK support 76/450).
No-call replay of the saved extract. This replay scores **374/450**
Purist and **383/450** Pragmatic. The cited five-cell / codebook-encode
holdout remains **373/450** and **382/450**. Do not retune from the
one-count gap. Do not inspect holdout rows.

#### Purist

```
Class            Precision    Recall    F1-score   Support
<1/6M              0.7500    0.5000    0.6000         6
=1/6M              0.0000    0.0000    0.0000         1
(1/6M,1/M)         0.8750    0.6364    0.7368        55
=1/M               0.9167    0.6111    0.7333        18
(1/M,1/W)          0.8833    0.9138    0.8983        58
=1/W               1.0000    0.6000    0.7500         5
(1/W,1/D)          0.9554    0.8699    0.9106       123
≥1/D               0.9048    0.9268    0.9157        41
UNK                0.6442    0.8816    0.7444        76
NS                 0.7808    0.8507    0.8143        67
micro-F1           0.8311    0.8311    0.8311       450
macro avg          0.7710    0.6790    0.7104       450
weighted avg       0.8472    0.8311    0.8308       450
```

#### Pragmatic

```
Class            Precision    Recall    F1-score   Support
infrequent         0.8750    0.6125    0.7206        80
frequent           0.9677    0.9251    0.9459       227
UNK                0.6442    0.8816    0.7444        76
NS                 0.7808    0.8507    0.8143        67
micro-F1           0.8511    0.8511    0.8511       450
macro avg          0.8169    0.8175    0.8063       450
weighted avg       0.8688    0.8511    0.8522       450
```

### Cell 5 — LLM / LLM / LLM

_Gemini 3.7 Flash; `gan_llm_select_from_extract` on the codebook extract; n=450; dropped=0._
Gold ε is living `gold_monthly_frequency` (Purist UNK support 76/450).
Select-stop labels from the sealed later-stage rows. Purist **357/450**
matches the cited five-cell cell. Pragmatic **369/450**.

#### Purist

```
Class            Precision    Recall    F1-score   Support
<1/6M              1.0000    0.6667    0.8000         6
=1/6M              0.0000    0.0000    0.0000         1
(1/6M,1/M)         0.9444    0.6182    0.7473        55
=1/M               0.6429    0.5000    0.5625        18
(1/M,1/W)          0.8889    0.6897    0.7767        58
=1/W               1.0000    0.6000    0.7500         5
(1/W,1/D)          0.9369    0.8455    0.8889       123
≥1/D               0.9048    0.9268    0.9157        41
UNK                0.6106    0.9079    0.7302        76
NS                 0.6914    0.8358    0.7568        67
micro-F1           0.7933    0.7933    0.7933       450
macro avg          0.7620    0.6591    0.6928       450
weighted avg       0.8248    0.7933    0.7953       450
```

#### Pragmatic

```
Class            Precision    Recall    F1-score   Support
infrequent         0.8727    0.6000    0.7111        80
frequent           0.9751    0.8634    0.9159       227
UNK                0.6106    0.9079    0.7302        76
NS                 0.6914    0.8358    0.7568        67
micro-F1           0.8200    0.8200    0.8200       450
macro avg          0.7875    0.8018    0.7785       450
weighted avg       0.8531    0.8200    0.8244       450
```

Two later-stage rows had no scorable select label. They are counted as
incorrect (not as UNK). That keeps Purist micro-F1 at 357/450.

Gan et al. 2026 abstract (Real(300), 15k synthetic train): Purist 0.788 / Pragmatic 0.847 (Qwen-2.5-14B); MedGemma-4B 0.787 / 0.858.
Those numbers are a different test set. Do not quote them as the same experiment.
The equivalent synthetic-to-synthetic row is in
[Gemini vs Qwen-2.5-14B COT synthetic](gan_gemini_vs_qwen25_14b_cot_synthetic_2026-08-28.md).
