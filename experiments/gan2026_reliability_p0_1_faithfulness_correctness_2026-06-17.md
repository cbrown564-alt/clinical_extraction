# P0.1 — Faithfulness x Correctness 2x2 + Over-Inference Rate

Date: 2026-06-17  ·  Model calls: 0 (deterministic replay)

Canonical subject: single GPT structured-event pass on `gpt-4.1-mini`, read from the `v0_reference` layer (decision 0018). The full-gpt-4.1 V12 `final` layer appears only as a tagged comparator.


## validation750 (n=750)

- **Faithfulness rate (subject, v0_reference):** 691/750 = 92.1%
- Faithfulness `[comparator: V12-full-gpt4.1]`: 703/750 = 93.7%
- Purist accuracy (subject): 661/750 = 88.1%

| | Purist correct | Purist wrong |
|---|:--:|:--:|
| **Evidence faithful** | 611 | **80** (faithful-but-wrong) |
| **Evidence unfaithful** | 50 | 9 |

The faithful-but-wrong cell = **80** rows (10.7% of all; 11.6% of faithful rows). Exact-span evidence does not imply correct selection — the thesis cell.

- **Over-inference on unknown-gold rows:** 16/170 = 9.4% over-read (→rate 12, →seizure-free 4).

## test450 (n=450)

- **Faithfulness rate (subject, v0_reference):** 418/450 = 92.9%
- Faithfulness `[comparator: V12-full-gpt4.1]`: 423/450 = 94.0%
- Purist accuracy (subject): 364/450 = 80.9%

| | Purist correct | Purist wrong |
|---|:--:|:--:|
| **Evidence faithful** | 338 | **80** (faithful-but-wrong) |
| **Evidence unfaithful** | 26 | 6 |

The faithful-but-wrong cell = **80** rows (17.8% of all; 19.1% of faithful rows). Exact-span evidence does not imply correct selection — the thesis cell.

- **Over-inference on unknown-gold rows:** 13/102 = 12.7% over-read (→rate 12, →seizure-free 1).

---

Headline: faithfulness is high on the production path, but the faithful-but-wrong cell is non-empty on both splits — the system grounds its evidence yet still over-selects, which is exactly the unknown-vs-rate over-inference the strand named. Faithfulness (grounding) and task correctness (selection) are distinct reliability axes.
