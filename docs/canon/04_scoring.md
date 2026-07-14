# 04 — ExECT scoring and annotation evidence

Last updated: 2026-07-14

## Score hierarchy

| Score | Question | Use |
| --- | --- | --- |
| `clinical_headline` | Were the right clinical facts recovered across the four key families? | Primary project comparison |
| Family headline | Was the family-specific clinical object recovered? | Family analysis |
| SeizureFrequency state profile | Was the consolidated burden state recovered? | SF-family development |
| Phrase, CUI, and full attribute bundle | Does output match the published benchmark representation? | Paper-comparable companion |
| Evidence groundedness | Is the cited evidence present after neutral text repair? | Fidelity |

Do not describe `clinical_headline` as a reproduction of the published strict
benchmark. The deterministic reference still needs full phrase/CUI/attribute
engineering before that claim can be made.

## Retained reference results

| Architecture | Split | Primary result |
| --- | --- | ---: |
| Deterministic all nine | dev140 | strict benchmark item F1 0.3548 |
| GEPA LLM-only | dev140 | `clinical_headline` F1 0.7393 |
| Hybrid v08 | dev140 | `clinical_headline` F1 0.9189 |

Exact scorer versions and companion results are in the
[manifest](../experiments/retained_evidence_manifest.md).

## Annotation evidence

The retained evidence includes:

- [Diagnosis canonical row analysis](../experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md);
- [SeizureFrequency canonical row analysis](../experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md);
- [blind replication report](../experiments/exectv2/reliability/exectv2_gold_quality_adjudication_blind_replication_2026-07-01.md);
- four family ledgers under `experiments/gold_case_ledger_*.jsonl`;
- `experiments/gold_data_issues.jsonl`; and
- the extracted annotation guideline source.

These are internal adjudication records. They support bounded claims about
annotation multiplicity, representation, ambiguity, and concrete defects. They
do not provide independent clinical validation.

## Open requirements

- implement and test deterministic phrase/CUI/full-attribute scoring;
- verify the published IAA method against the primary source;
- consolidate cited annotation issues into one generated taxonomy with scoring
  effects and review status.

