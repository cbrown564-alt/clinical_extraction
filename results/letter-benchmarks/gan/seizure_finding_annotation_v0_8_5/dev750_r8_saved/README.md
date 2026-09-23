# Unscored within-cluster spans: saved R8 development replay

This additive revision follows the [v0.8.4 saved-R8 comparison](../../seizure_finding_annotation_v0_8_4/dev750_r8_saved/README.md)
for Gan 2026 **synthetic dev750**. The v0.8.4 reference, raw R8 outputs,
earlier scores and locked split remain unchanged. No model was called. All 750
development letters were rescored; the same 714 saved R8 inventories are usable
and 36 remain invalid.

The repeatable producer is `scripts/benchmarks/revise_findings_v085.py`. It
records **18 source-backed edits across 18 letters** in the local
`runs/seizure_finding_annotation_v0_8_5/dev750_r8_saved/claim_adjudications.jsonl`.
Each removes a within-cluster span such as `a day`, `within 24 hours`, or
`within half an hour` from structured `period`; the exact evidence quotation
still contains that span. The versioned `finding_v085_v1` scorer ignores an
emitted cluster period when gold has no observation period. It requires the
stated cluster count, size and cadence to agree and continues to score a
cluster count's observation window, such as `two clusters this month`.

| Saved R8 versus development gold | v0.8.4 | v0.8.5 |
| --- | ---: | ---: |
| Gold findings | 1,524 | 1,524 |
| Matched | 994 | 994 |
| Extra R8 findings | 447 | 447 |
| Missed gold findings | 530 | 530 |
| Precision | 69.0% | 69.0% |
| Recall | 65.2% | 65.2% |

None of the 18 span edits changes a saved R8 match. The scorer checks stated
count, size and cadence; it treats qualitative `multiple` as redundant when
gold says only `clusters` and gives no size (15697 and 16574). It does not
credit an invented numeric size or a different cadence. The unchanged totals
are a **scorer and reference comparison**, not a new model result. The workbench view is
`http://localhost:3000/workbench?dataset=ganR8&version=v085`.

[15442](http://localhost:3000/workbench?dataset=ganR8&version=v085&letter=15442)
retains “a day with multiple events, typically two tonic seizures” in evidence
but has no scored `period`; the size is two seizures per cluster. Other
within-cluster examples include [15497](http://localhost:3000/workbench?dataset=ganR8&version=v085&letter=15497)
(five within 24 hours) and [16757](http://localhost:3000/workbench?dataset=ganR8&version=v085&letter=16757)
(six within half an hour). [11131](http://localhost:3000/workbench?dataset=ganR8&version=v085&letter=11131)
keeps `this month` as the scored window for two cluster days with three to four
seizures per cluster. [10618](http://localhost:3000/workbench?dataset=ganR8&version=v085&letter=10618)
keeps `within a fortnight` as the scored window for two observed clusters.
Do not infer a daily cluster span when the source gives none.

The [annotation guide](../../../../../docs/research/gan2026/seizure_finding_annotation_v08.md)
owns the intended rule. The R9 prompt candidate includes it but has not been
run. Prior references, including v0.8.4, remain independently reproducible.
