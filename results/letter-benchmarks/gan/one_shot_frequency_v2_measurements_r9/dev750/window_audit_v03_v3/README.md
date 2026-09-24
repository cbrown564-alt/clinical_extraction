# R9 compact development mismatch audit and versioned window rescore

This is an offline development analysis of the same 750 synthetic Gan2026
`dev750` first responses. No model call, response repair, reference edit or
test450 inspection was made. The original `finding_compact_v03_v2` score stays in
`../frozen_score/score.json`. The new `score.json` uses
`finding_compact_v03_v3`; local per-letter pairs are under
`runs/one_shot_frequency_v2_measurements_r9/dev750/window_audit_v03_v3/`.

## Predeclared question and permitted change

Question: how much of the low whole-claim score comes from source windows that
name the same relative interval with an optional leading article or `in`/`over`?
The change removes only those prefixes before `past`, `last` or `current` and
keeps the interval word and quantity. It also retains the established
seizure-free anchor comparison (`since March` versus `March`) because the
measurement already records the absence relation. It does not collapse `last`
and `past`, infer a missing window, equate `since March` with `in March` for a
rate or count, or change event and restriction scoring. Exact source evidence
and all other claim components remain required. This is a new scorer version;
it does not revise the original score.

## Source audit

We inspected the reference and prediction fields beside the exact source
quotation and source note for 25 deliberately selected aligned near misses:
eight window, nine event and eight restriction cases. The source IDs below are
Gan synthetic development IDs. They are examples of mechanisms, not a random
sample or a prevalence estimate. The local
`runs/one_shot_frequency_v2_measurements_r9/dev750/window_audit_v03_v3/source_review_sample.jsonl`
records their source hashes, paired claim indices, exact source quotations and
field-level decisions.

| Field | Source IDs | Source-backed decision |
| --- | --- | --- |
| Window | 466, 725, 1694, 1773, 1790, 1794, 2094, 2427 | `past/last ...` and `the past/last ...`, including `over/in the ...`, name the same interval in these notes. The v3 prefix rule covers them without changing the duration. |
| Event | 103, 198, 278, 409, 467, 598, 987, 1573, 2965 | Mixed causes. R9 sometimes declares `overall seizures` when the source/reference leaves the population unspecified (103, 198, 2965), or uses a broader event than a named subtype (467, 598, 987). `events` versus `seizures` (409) and `focal cognitive` versus `focal cognitive seizures` (1573) may be lexical in context, but a blanket alias could erase a real event-population distinction. The scorer leaves these unmatched. |
| Restriction | 725, 1773, 2374, 3949, 5136, 5551, 6029, 8805 | `witnessed by manager` versus `witnessed event by manager` (725) and `recorded during this interval` versus `recorded` (5136) appear equivalent in their notes. Other references use morning timing or triggers as restrictions (1773, 2374, 3949, 5551, 6029), while 8805 has a device/reporting scope that cannot be discarded. The compact guide says to score a qualifier that changes what is counted and treats trigger/time-of-day breakdowns as context. These reference placements need owner adjudication before changing the reference or restriction matcher. |

The sample is sufficient to justify the narrow window equivalence and to reject
blanket event or restriction relaxation. It does not validate all 780 remaining
source-aligned near misses.

## Replay result

| Frozen condition | Whole-claim matches | Precision | Recall | F1 | Source-aligned pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| v2 original | 202 | 15.43% | 16.57% | 15.98% | 1,062 |
| v3 window correction | 282 | 21.54% | 23.13% | 22.31% | 1,062 |

The narrow prefix rule applies to 174 previously window-disagreeing aligned
pairs; other differences prevent many of them from becoming whole-claim
matches. The v3 replay gains 80 matches across 67 letters and loses none; 683 letters
retain the same whole-claim count. Of the original 860 aligned near misses, 686
already agreed on measurement kind and value. In v3, 780 aligned near misses
remain. Their most frequent differing components are event (496), restriction
(286), window (282) and measurement value (148); counts overlap. Event scope
accounts for 289 of the 496 event disagreements. The response validity,
1,309 usable predictions, 1,219 reference claims, native answer score and
US$7.7703174 model charge are unchanged.

## Remaining decisions

Review the source-backed event scope and label conventions, especially
`overall` versus `unspecified`, before defining any alias. Review whether
morning timing and triggers in the compact reference belong in `restriction`
or only in evidence. Any reference change needs a new reference version and
its own rescore. Do not treat the v3 score as a comparable model improvement:
only the scorer changed.
