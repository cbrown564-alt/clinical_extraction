# ExECTv2 Projection-Gap Ledger

- Generated: `2026-06-17`
- JSON: `experiments\exectv2_projection_gap_ledger_dev.json`
- Split: `dev`
- Letters: 140
- Records: 1455

Diagnostic ledger: every gold false negative and predicted false positive, classified into a layered `gap_family` (which key layer broke) and tagged `miss_kind` candidate-source vs projection by Finding 2's concept-recovery proxy (is the gold CUI present among predictions). The two axes are orthogonal: a phrase+attribute match whose result-specific CUI is absent is an `attribute_bundle` gap but a `candidate_source` miss. Read alongside the three-layer scorecard for headline F1.

## Totals

- Gold misses: 1021
- Projection misses (concept recovered, key differs): 340
- Candidate-source misses (concept absent): 681
- Projection share of gold misses: 0.3330
- Over-emissions (predicted FP): 434

## Per-Entity Regime And Gap Families

| Entity | Regime | Gold misses | Projection | Candidate-source | Proj. share | Phrase | Attr bundle | CUI proj | Over-emit |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | representation_bound | 14 | 12 | 2 | 0.8571 | 4 | 8 | 2 | 3 |
| Diagnosis | recall_bound | 314 | 53 | 261 | 0.1688 | 293 | 15 | 6 | 49 |
| EpilepsyCause | representation_bound | 9 | 6 | 3 | 0.6667 | 7 | 2 | 0 | 10 |
| Investigations | recall_bound | 84 | 24 | 60 | 0.2857 | 39 | 38 | 7 | 90 |
| Onset | mixed | 12 | 7 | 5 | 0.5833 | 10 | 2 | 0 | 11 |
| PatientHistory | recall_bound | 390 | 82 | 308 | 0.2103 | 364 | 25 | 1 | 73 |
| Prescription | representation_bound | 145 | 126 | 19 | 0.8690 | 144 | 1 | 0 | 136 |
| SeizureFrequency | mixed | 51 | 28 | 23 | 0.5490 | 41 | 10 | 0 | 60 |
| WhenDiagnosed | representation_bound | 2 | 2 | 0 | 1.0000 | 2 | 0 | 0 | 2 |

## Prescription Component Families

Prescription benchmark F1 is dominated by phrase altitude, so its row-level gaps above are read with these clinical component families (diagnostic; gains here are projection-format, not medication recovery).

| Family | Item F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| source_stated_frequency | 0.9307 | 0.9495 | 0.9126 | 188 | 10 | 18 |
| guideline_defaulted_frequency | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| rescue_regimen | 0.8333 | 0.8333 | 0.8333 | 5 | 1 | 1 |
| future_medication | 0.2609 | 0.2143 | 0.3333 | 3 | 11 | 6 |
| weight_based_dosing | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 5 |
| phrase_scope | 0.3069 | 0.3131 | 0.3010 | 62 | 136 | 144 |
| drugname_cui_projection | 0.9158 | 0.9343 | 0.8981 | 185 | 13 | 21 |

## Reading

Representation-bound entities (high projection share) move on projection fixes — phrase altitude, casing, attribute/CUI convention — not lexicon breadth. Recall-bound entities (low projection share) need real candidate generation (GPT-first or hybrid). Split/merge and current-regimen errors are visible as Prescription phrase_coverage and over_emission rows plus the component table; first-class split/merge instrumentation is future work.
