# Gan semantic family order

Date: 2026-08-20
Status: development answer
Owner: this file
Protocol: [gan_semantic_family_order_protocol_2026-08-20.md](gan_semantic_family_order_protocol_2026-08-20.md)
Artifact: `experiments/paper/gan_semantic_family_order/dev750_adjacent_swaps.json`

## Question

After diary after elapsed-anchor, is any other adjacent pair of
clinical post-stack families in the wrong order?

## Answer

No. On these three saved `dev750` raw files, only the diary /
elapsed-anchor pair is order-sensitive. Every other adjacent swap
is a no-op. Putting diary back before elapsed-anchor is harmful.

## Evidence

Replay of the current post stack. No new model calls. Purist.

| Cell | Default | Other adjacent swaps | Diary before elapsed |
| --- | ---: | --- | --- |
| Grok hybrid | 681/750 | 0 help, 0 harm | 0 help, 2 harm (679) |
| Luna hybrid | 669/750 | 0 help, 0 harm | 0 help, 2 harm (667) |
| Luna pre-post | 683/750 | 0 help, 0 harm | 0 / 0 |

The two harmed letters are the same on Grok and Luna hybrid:
**2932** (`seizure free for 9 month` → `13 per 2 month`) and
**8089** (`seizure free for 16 month` → `1 per 1 month`). Diary
first overwrites a dated freedom window with a countable month
log. Elapsed-anchor first keeps the freedom label, then diary is
vetoed.

Luna pre-post already survives diary-first on those two letters,
so the known pair is not a lift there; it is still required for
the living hybrid cells.

No adjacent swap met the adopt rule (help ≥ 1 and harm = 0 on all
three cells).

## Claim boundary

Development answer on three saved `dev750` files. Adjacent swaps
only. A non-adjacent permutation was not run. Not holdout.

## Decision

Keep the current order. Do not move any other family.
