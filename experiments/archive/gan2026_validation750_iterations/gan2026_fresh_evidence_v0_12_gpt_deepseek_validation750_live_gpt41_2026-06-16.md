# Gan 2026 Fresh-Evidence A4 (GPT + deepseek) — validation750

Date: 2026-06-16

Simplest-near-ceiling plan, A4 rung. validation750 development split (NOT test450). Tests the minimal ensemble: GPT + one peer (2 upstream models). The peer trace is a saved artifact; only the reasoner pass is live.

Plan: `docs/research/gan2026/architecture/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md`
Candidate: `fresh_evidence_reasoner gan2026_fresh_evidence_reasoner_v0_12_two_model (GPT+deepseek) live, temp 0`
Baseline: `fresh_evidence_reasoner v0.4 (3-agent) from gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl` (caveat: v0.4 prompt label).

## Overall Purist (validation750)

- A4 GPT+deepseek Purist: 631 / 750 = 0.841
- v0.4 3-agent baseline Purist: 682 / 750 = 0.909
- Net vs 3-agent baseline: -51 rows (tolerance for knee: -11)
- wrong->correct: 18   correct->wrong: 69

## Comparison to the other rungs (validation750)

| Rung | Models | Purist |
| --- | ---: | ---: |
| GPT structured-event pass (this run's v0_reference) | 1 | 661/750 = 0.881 |
| A3 GPT-only reasoner | 1 | 610/750 = 0.813 |
| **A4 GPT+deepseek reasoner (this run)** | **2** | **631/750 = 0.841** |
| 3-agent reasoner (baseline) | 3 | 682/750 = 0.909 |

Reasoner net vs its own GPT pass: -30 (A3 was -51; 3-agent was +21).

## Action decomposition (A4 vs single GPT pass, this run)

- Replace actions: 34 helped, 64 hurt, 125 neutral (net -30).
- Keep actions: 495 correct, 32 wrong.

## Held-out-family CV (leave-one-boundary-band-out)

**gap_robust: False**
Reasons (empty = clean): ['aggregate net Purist gain -51 <= 0', 'held-out bands regress (net Purist gain < 0): band_zero, band_submonthly, band_monthly, band_weekly, band_daily', 'held-out bands below changed-label precision 0.5: band_zero, band_unknown, band_submonthly, band_monthly, band_weekly, band_daily']
Aggregate: {'rows': 750, 'changed_labels': 144, 'wrong_to_correct': 18, 'correct_to_wrong': 69, 'net_purist_gain': -51, 'changed_label_precision': 0.125}
Worst held-out fold: {'family': 'band_submonthly', 'net_purist_gain': -20}

| Band (held out) | rows | changed | w->c | c->w | net | changed-label prec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| band_zero | 112 | 31 | 1 | 20 | -19 | 0.0323 |
| band_unknown | 170 | 32 | 11 | 2 | +9 | 0.3438 |
| band_submonthly | 87 | 27 | 1 | 21 | -20 | 0.037 |
| band_monthly | 141 | 31 | 4 | 13 | -9 | 0.129 |
| band_weekly | 177 | 18 | 1 | 10 | -9 | 0.0556 |
| band_daily | 63 | 5 | 0 | 3 | -3 | 0.0 |

## Genuine-rate regression check

Genuine-rate rows correct in baseline now wrong: 67 (A3 had 89).

## Decision

**reject_below_tolerance**

Knee rule: promote to robustness battery if net Purist >= -11 (within ~1.5pp of the 3-agent baseline) AND family-CV gap_robust. A4 is one model simpler than the 3-agent baseline. Note: the final architecture choice is the single GPT pass; A4 is run for information on what one peer recovers.
