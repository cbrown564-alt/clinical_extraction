# Cell 3 find vs selected-evidence candidate volume on Gan `dev750`

Date: 2026-08-29
Status: development answer
Protocol:
[candidate-volume protocol](gan_cell3_candidate_volume_dev750_protocol_2026-08-29.md)
Artifact:
[`gan_cell3_candidate_volume_dev750_2026-08-29.json`](gan_cell3_candidate_volume_dev750_2026-08-29.json)
Owners: [six-model roster](../../paper/decisions/six-model-roster.md),
[codebook rung replay](gan_cell3_codebook_roster_replay_2026-08-28.md)

This is a no-call replay of the living six-model cell 3 stack on Gan
`dev750`: `gan_llm_extract` → `gan_rules_encode` →
`llm_select_after_codebook`. Find volume is the event list written by
that extract call. Selected-evidence volume is
`len(selected_event_ids)` from the same call. `test450` was not loaded
for row work.

## Answer

Every roster model writes a small find ledger and then proposes a
near-single-event selected-evidence set. On `dev750`, mean find events
range from **1.98** (DeepSeek) to **2.46** (Luna). Mean selected-evidence
events range from **1.01** (Gemma) to **1.24** (Qwen / Luna). The
median selected set is **1** for all six models.

The find call, not later rule select, does that narrowing. Across all
six models, selected-event ids never change from extract to the living
select stop.

For Gemini, gold Purist band changes how wide find is, not how many
events stay selected. Daily gold has the widest find (**2.74**, median
**3**, range **1–6**) and the tightest selected set (**1.07**, median
**1**, range **1–3**). Unknown and no-reference golds have the
narrowest find (**1.77** / **1.82**, median **2**, ranges **1–5** /
**1–4**) and still keep about **1.24** / **1.26** selected events
(median **1**).

The four-band Pragmatic collapse keeps that story. Frequent gold
(n=387) find mean **2.30** (median **2**, **1–6**); Infrequent (n=124)
**2.40** (median **2**, **1–5**). Unknown and no-seizure stay at
**1.77** / **1.82**. Selected medians remain **1** in every Pragmatic
band.

## Protocol in one line

- Dataset / split: Gan 2026 `dev750` (`gan2026_split_v1` / machine
  `validation`). Development inspection permitted.
- Component: cell-3 find (`gan_llm_extract`).
- Counts: `predicted_candidate_count` vs `len(selected_event_ids)` on
  the `llm_extract` rung.
- Gemini slice: gold Purist and Pragmatic categories from living
  `map_purist` / `map_pragmatic` on `gold_monthly_frequency`.
- Replay: saved rungs; zero model calls.
- Companion: `test450` find totals from existing `comparison.json`
  only.

## 1. Six-model volume on `dev750`

| Model | Find total | Find mean | Find median | Find min–max | Selected total | Selected mean | Selected median | Selected min–max | Selected / find | Rows selected < find |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gemini 3.7 Flash | 1619 | **2.16** | 2 | 1–6 | 900 | **1.20** | 1 | 0–4 | 0.56 | 462 / 750 |
| Grok 4.6 | 1813 | **2.42** | 2 | 1–6 | 917 | **1.22** | 1 | 1–4 | 0.51 | 537 / 750 |
| GPT-5.6 Luna | 1842 | **2.46** | 2 | 1–12 | 928 | **1.24** | 1 | 1–4 | 0.50 | 493 / 750 |
| DeepSeek V4 Flash | 1482 | **1.98** | 2 | 0–8 | 795 | **1.06** | 1 | 0–4 | 0.54 | 431 / 750 |
| Qwen 3.8 27B | 1687 | **2.25** | 2 | 0–13 | 930 | **1.24** | 1 | 0–4 | 0.55 | 465 / 750 |
| Gemma 4 26B | 1763 | **2.35** | 2 | 0–8 | 754 | **1.01** | 1 | 0–3 | 0.43 | 607 / 750 |

No model proposes more selected ids than find events. Empty find ledgers
are rare and local-model-skewed: Gemini and Grok **0**, Luna **0**,
DeepSeek **2**, Qwen **7**, Gemma **13**. Those empty finds are also the
empty selected-evidence rows.

Select-stop Purist on this split is recorded only as context, not as a
volume result: Grok **0.876**, Gemini **0.865**, DeepSeek **0.824**,
Luna **0.819**, Qwen **0.765**, Gemma **0.752**. Wider find is not the
same as a higher select stop. Luna writes the most find events and is
mid-pack on Purist. Gemma writes a wide ledger, then keeps almost
exactly one event, and has the lowest select stop.

## 2. Gemini by gold Purist category

Support is gold Purist occupancy on `dev750`. Display names match
`PURIST_DISPLAY_LABELS`.

| Gold Purist category | n | Find mean | Find median | Find min–max | Selected mean | Selected median | Selected min–max | Selected / find |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Daily | 81 | **2.74** | 3 | 1–6 | **1.07** | 1 | 1–3 | 0.39 |
| More than weekly, less than daily | 196 | **2.11** | 2 | 1–5 | **1.10** | 1 | 0–3 | 0.52 |
| Once a week | 11 | **2.55** | 2 | 1–5 | **1.27** | 1 | 1–2 | 0.50 |
| More than monthly, less than weekly | 99 | **2.30** | 2 | 1–5 | **1.29** | 1 | 1–4 | 0.56 |
| Once a month | 34 | **2.09** | 2 | 1–4 | **1.21** | 1 | 1–3 | 0.58 |
| More than 6 months, less than monthly | 79 | **2.58** | 3 | 1–5 | **1.30** | 1 | 1–3 | 0.50 |
| Once every 6 months | 6 | **1.83** | 2 | 1–3 | **1.00** | 1 | 1–1 | 0.55 |
| Less than once every 6 months | 5 | **2.40** | 2 | 2–3 | **1.40** | 1 | 1–2 | 0.58 |
| Unknown | 127 | **1.77** | 2 | 1–5 | **1.24** | 1 | 0–3 | 0.70 |
| No seizure frequency reference | 112 | **1.82** | 2 | 1–4 | **1.26** | 1 | 1–3 | 0.69 |
| **All rows** | **750** | **2.16** | **2** | **1–6** | **1.20** | **1** | **0–4** | **0.56** |

The two n<15 bands (`Once every 6 months`, `Less than once every 6
months`) are occupancy, not a second finding.

The pattern that is large enough to read:

- Counted high-rate gold (Daily) produces the most competing find
  events (median **3**, up to **6**) and then almost always keeps one
  (selected max **3**).
- Sentinel gold (Unknown, no-reference) produces fewer find events
  (median **2**, max **5** / **4**) and keeps a larger share of them.
  The selected set is still about one event, not a wide committee
  (selected max **3**).
- Mid-rate counted gold sits between those poles. Selected means stay
  in **1.10–1.30**; selected medians stay **1**.

## 3. Gemini by gold Pragmatic category

Support is gold Pragmatic occupancy on the same 750 rows. Display names
match `PRAGMATIC_DISPLAY_LABELS`. Frequent is the living collapse of
the four high-rate Purist bands (Daily through more-than-monthly);
Infrequent is the four monthly-or-sparser counted bands.

| Gold Pragmatic category | n | Find mean | Find median | Find min–max | Selected mean | Selected median | Selected min–max | Selected / find |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Frequent | 387 | **2.30** | 2 | 1–6 | **1.15** | 1 | 0–4 | 0.50 |
| Infrequent | 124 | **2.40** | 2 | 1–5 | **1.27** | 1 | 1–3 | 0.53 |
| Unknown | 127 | **1.77** | 2 | 1–5 | **1.24** | 1 | 0–3 | 0.70 |
| No seizure | 112 | **1.82** | 2 | 1–4 | **1.26** | 1 | 1–3 | 0.69 |
| **All rows** | **750** | **2.16** | **2** | **1–6** | **1.20** | **1** | **0–4** | **0.56** |

Pragmatic does not hide a second selected-set size. Frequent and
Infrequent find medians are both **2**; selected medians are both **1**.
The Purist Daily tail (find median **3**) is absorbed into Frequent
without moving that band’s median. The only Pragmatic contrast that
survives is the same sentinel vs counted split already visible in
Purist: Unknown and no-seizure find less and keep a larger share.

## 4. What the unused Gemini find events are

Gemini find histogram on `dev750`: **1** event on 216 rows, **2** on
292, **3** on 167, **4** on 59, **5** on 14, **6** on 2. Selected
histogram: **1** on 625 rows, **2** on 95, **3** on 27, **4** on 1,
**0** on 2.

The 719 events not in `selected_event_ids` appear in the living hops
graph as `unused_candidate`. Their kinds:

| Unused candidate kind | Count |
| --- | ---: |
| `frequency_rate` | 294 |
| `seizure_free` | 197 |
| `last_event_only` | 104 |
| `unknown_frequency` | 74 |
| `cluster_frequency` | 50 |
| **All unused** | **719** |

The leftover ledger is mostly a second rate, a seizure-free interval, or
a last-event span, not a cluster-only problem.

Extract Purist falls as find count rises (**0.91** at 1 event, **0.66**
at 3, **0.59** at 4). Living rule select recovers part of that
(**0.94**, **0.80**, **0.80**) without changing selected-event ids. That
matches the earlier encode→select study: select rewrites the label on
the same selected events.

## 5. `test450` find-only companion

These means use only promoted `comparison.json` find totals. There is
no `scored.jsonl` on those rungs, so selected-evidence means are not
reported. No holdout row was inspected.

| Model | Find total | Find mean |
| --- | ---: | ---: |
| Gemini 3.7 Flash | 985 | 2.19 |
| Grok 4.6 | 1063 | 2.36 |
| GPT-5.6 Luna | 1102 | 2.45 |
| DeepSeek V4 Flash | 1267 | 2.82 |
| Qwen 3.8 27B | 1004 | 2.23 |
| Gemma 4 26B | 1068 | 2.37 |

Five models stay within **0.06** of their `dev750` find mean. DeepSeek
does not: **1.98** on `dev750` vs **2.82** on `test450`. That split
difference is an aggregate observation only. It is not a selected-
evidence result and is not a holdout mechanism claim.

## Attribution

The volume difference between find and selected evidence is a property
of the find call. Encode and living rule select do not add or drop
selected-event ids on this split. Later select-stop Purist movement is
label rewrite on that already-narrowed set, as in
[Gemini cell 3 encode→select](../paper/gan_gemini_cell3_encode_to_select_dev750_2026-08-29.md).

## Claim boundary

Development description of cell-3 candidate volume on `dev750`. It does
not support a new six-model score, a holdout selected-evidence mean, or
an LLM-select claim. Select here remains recorded rules after codebook
encode.

## Decision

Cell 3 models already behave like a recall-then-narrow find: about two
events written, about one proposed as selected evidence. Gemini’s
Purist bands change the width of the unused leftover, not the
selected-set size; Pragmatic keeps that conclusion at four bands. If a
later study wants a wider find ledger, that is a find-prompt or
find-schema change, not a select-family change.

## Next action

Keep cited cell-3 rows as they are. Use this volume table when reading
six-model score gaps: Gemma’s collapse to one selected event, and
DeepSeek’s `dev750` vs `test450` find-mean split, are the two volume
facts that can change an interpretation. Do not start holdout
selected-evidence scoring without a predeclared aggregate-only artifact.
