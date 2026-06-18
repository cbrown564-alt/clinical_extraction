# ExECTv2 CUI Missing-Mapping Ledger

- Generated: `2026-06-18`
- Split: `dev` (140 letters)
- Source: existing dev gold replay through `cui_projection_coverage`; no model calls.
- Scope: benchmark-format CUI/CUIPhrase projection after clinical mentions are already selected.
- Guardrail: no Gan `test450` or holdout/test row-level artifacts inspected.

## Summary

- Baseline missing mappings: **184 concepts / 365 mentions**.
- Implemented finite additions: **35 concepts / 203 mentions**.
- Review-needed remainder: **149 concepts / 162 mentions**.

## Action Counts

| Action | Concepts | Mentions |
| --- | ---: | ---: |
| `review_needed_long_tail` | 146 | 153 |
| `implemented_lexicon_addition` | 35 | 203 |
| `review_needed_fragment_or_context_dependent` | 2 | 6 |
| `review_needed_gold_inconsistent` | 1 | 3 |

## Remaining Review-Needed Entity Counts

| Entity | Concepts | Mentions |
| --- | ---: | ---: |
| BirthHistory | 4 | 4 |
| Diagnosis | 39 | 45 |
| EpilepsyCause | 5 | 5 |
| Onset | 9 | 9 |
| PatientHistory | 92 | 99 |

## Implemented Lexicon Additions

All rows below are `benchmark_format_projection_only`: they attach a dev-observed one-to-one CUI after the mention/concept has already been selected. They do not license deterministic clinical concept generation.

| Entity | Concept | Mentions | CUI |
| --- | --- | ---: | --- |
| Diagnosis | generalised tonic clonic seizures | 34 | `C0494475` |
| Diagnosis | focal seizures | 17 | `C0751495` |
| Diagnosis | focal to bilateral convulsive seizures | 16 | `C0877017` |
| Diagnosis | complex partial seizures | 14 | `C0149958` |
| Diagnosis | focal seizures with altered awareness | 14 | `C0270834` |
| Diagnosis | secondary generalised seizures | 12 | `C0270838` |
| Diagnosis | generalised tonic clonic seizure | 9 | `C0494475` |
| Diagnosis | epileptic seizures | 7 | `C4317109` |
| Diagnosis | focal motor seizures | 7 | `C0016399` |
| Diagnosis | generalised seizures | 6 | `C0234533` |
| Diagnosis | secondary generalised tonic clonic seizures | 6 | `C0877017` |
| Diagnosis | epilepsy with generalised tonic clonic seizures alone | 4 | `C0393697` |
| Diagnosis | generalised epilepsy | 4 | `C0014548` |
| Diagnosis | primary generalised epilepsy | 4 | `C0270850` |
| Diagnosis | focal impaired awareness seizures | 3 | `C0270834` |
| Diagnosis | focal to bilateral convulsive seizure | 3 | `C0877017` |
| Diagnosis | genetic generalised epilepsy | 3 | `C0270850` |
| Diagnosis | absence seizures | 2 | `C4316903` |
| Diagnosis | dyscognitive seizures | 2 | `C0270834` |
| Diagnosis | focal seizure | 2 | `C0751495` |
| Diagnosis | frontal lobe epilepsy | 2 | `C0085541` |
| Diagnosis | intractable epilepsy | 2 | `C1096063` |
| Diagnosis | juvenile absence epilepsy | 2 | `C4317339` |
| Diagnosis | occipital lobe epilepsy | 2 | `C0393691` |
| Diagnosis | temporal lobe seizure | 2 | `C0014556` |
| Diagnosis | tonic clonic seizures | 2 | `C0494475` |
| PatientHistory | episodes of loss of consciousness | 4 | `C0041657` |
| PatientHistory | type 1 diabetes | 2 | `C0011854` |
| PatientHistory | episode of loss of consciousness | 1 | `C0041657` |
| PatientHistory | insulin dependent diabetes | 1 | `C0011854` |
| PatientHistory | loss of consciousnes | 1 | `C0041657` |
| PatientHistory | jerks | 4 | `C0231530` |
| PatientHistory | altered awareness | 3 | `C0234428` |
| PatientHistory | déjà vu | 3 | `C0011194` |
| PatientHistory | hemiparesis | 3 | `C0018989` |

## Full Ledger

See `experiments/exectv2_cui_missing_mapping_ledger_dev140_20260618.csv` for all prioritized missing concepts, including benchmark-format candidates left as review-needed.
