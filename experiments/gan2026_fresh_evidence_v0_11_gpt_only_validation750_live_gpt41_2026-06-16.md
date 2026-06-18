# Gan 2026 Fresh-Evidence A3 (GPT-trace-only) — validation750

Date: 2026-06-16

Simplest-near-ceiling plan, Step 2. validation750 development split (NOT test450). Tests whether dropping the Qwen + DeepSeek peer traces from the reasoner prompt retains the lift over a single GPT pass.

Plan: `docs/research/gan2026/architecture/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md`
Candidate: `fresh_evidence_reasoner gan2026_fresh_evidence_reasoner_v0_11_gpt_only live, temp 0`
Baseline: `fresh_evidence_reasoner v0.4 (3-agent) from gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl` (caveat: v0.4 prompt label; see header).

## Overall Purist (validation750)

- A3 GPT-only Purist: 610 / 750 = 0.813
- v0.4 3-agent baseline Purist: 682 / 750 = 0.909
- Net vs baseline: -72 rows (tolerance for knee: -11)
- wrong->correct: 19   correct->wrong: 91

## Action decomposition (A3 vs single GPT pass, this run)

- Replace actions: 28 helped, 79 hurt, 90 neutral (net -51).
- Keep actions: 511 correct, 42 wrong.
- GPT-only-pass Purist this run (v0_reference): 661 / 750 = 0.881
- Reasoner net vs its own GPT pass: -51

## Held-out-family CV (leave-one-boundary-band-out)

**gap_robust: False**
Reasons (empty = clean): ['aggregate net Purist gain -72 <= 0', 'held-out bands regress (net Purist gain < 0): band_zero, band_submonthly, band_monthly, band_weekly, band_daily', 'held-out bands below changed-label precision 0.5: band_zero, band_unknown, band_submonthly, band_monthly, band_weekly, band_daily']
Aggregate: {'rows': 750, 'changed_labels': 188, 'wrong_to_correct': 19, 'correct_to_wrong': 91, 'net_purist_gain': -72, 'changed_label_precision': 0.1011}
Worst held-out fold: {'family': 'band_submonthly', 'net_purist_gain': -28}

| Band (held out) | rows | changed | w->c | c->w | net | changed-label prec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| band_zero | 112 | 36 | 1 | 16 | -15 | 0.0278 |
| band_unknown | 170 | 34 | 13 | 2 | +11 | 0.3824 |
| band_submonthly | 87 | 37 | 1 | 29 | -28 | 0.027 |
| band_monthly | 141 | 41 | 3 | 21 | -18 | 0.0732 |
| band_weekly | 177 | 30 | 1 | 15 | -14 | 0.0333 |
| band_daily | 63 | 10 | 0 | 8 | -8 | 0.0 |

## Genuine-rate regression check

Genuine-rate rows correct in baseline now wrong: 89

## Decision

**reject_peers_load_bearing**

Knee rule: promote to robustness battery if net Purist >= -11 (within ~1.5pp) AND family-CV gap_robust. reject_peers_load_bearing if A3 falls more than the tolerance below baseline (the peer ensemble carries the lift). A3 is strictly simpler (1 upstream model vs 3).
