# ExECTv2 SF v0.8 Hard-Slice Panel

- Generated: `2026-06-18`
- Split: `dev`
- Scope: dev140 SF v0.7 residual hard-slice diagnostic only
- JSON: `experiments\exectv2_sf_v08_hard_slice_panel_dev140_20260618.json`
- Source ledger: `experiments\exectv2_key_entities_clinical_error_ledger_v07sf_dev140_20260618.json`
- Source JSONL: `experiments\exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl`
- Rows: 140
- Residual records: 82
- Residual units: 84

## Bucket Counts By Side And State

| Bucket | Side/State | Count |
| --- | --- | ---: |
| `diagnosis_context_span` | gold/active-rate | 9 |
| `diagnosis_context_span` | gold/seizure-free | 5 |
| `diagnosis_context_span` | gold/unknown | 6 |
| `diagnosis_context_span` | predicted/active-rate | 8 |
| `diagnosis_context_span` | predicted/seizure-free | 9 |
| `diagnosis_context_span` | predicted/unknown | 4 |
| `generic_named_ownership` | gold/active-rate | 2 |
| `generic_named_ownership` | predicted/active-rate | 2 |
| `other_or_ambiguous` | gold/active-rate | 2 |
| `other_or_ambiguous` | gold/seizure-free | 1 |
| `other_or_ambiguous` | predicted/active-rate | 7 |
| `other_or_ambiguous` | predicted/seizure-free | 3 |
| `other_or_ambiguous` | predicted/unknown | 3 |
| `seizure_free_cui_convention` | gold/seizure-free | 4 |
| `seizure_free_cui_convention` | predicted/seizure-free | 5 |
| `state_swap` | gold/active-rate | 3 |
| `state_swap` | gold/seizure-free | 1 |
| `state_swap` | gold/unknown | 1 |
| `state_swap` | predicted/active-rate | 2 |
| `state_swap` | predicted/unknown | 5 |
| `true_candidate_gap` | gold/active-rate | 1 |
| `true_candidate_gap` | gold/unknown | 1 |

## Bucket Counts By Type Family

| Bucket | Type family | Count |
| --- | --- | ---: |
| `diagnosis_context_span` | named_cui | 23 |
| `diagnosis_context_span` | generic_seizure | 13 |
| `diagnosis_context_span` | phrase | 3 |
| `diagnosis_context_span` | seizure_free_concept | 2 |
| `generic_named_ownership` | generic_seizure | 2 |
| `generic_named_ownership` | named_cui | 2 |
| `other_or_ambiguous` | generic_seizure | 8 |
| `other_or_ambiguous` | named_cui | 5 |
| `other_or_ambiguous` | phrase | 2 |
| `other_or_ambiguous` | seizure_free_concept | 1 |
| `seizure_free_cui_convention` | seizure_free_concept | 5 |
| `seizure_free_cui_convention` | generic_seizure | 4 |
| `state_swap` | named_cui | 8 |
| `state_swap` | generic_seizure | 4 |
| `true_candidate_gap` | named_cui | 2 |

## Possible Fix Counts

| Action | Count |
| --- | ---: |
| `no_action` | 35 |
| `drop` | 21 |
| `repair_state` | 12 |
| `repair_benchmark_format` | 9 |
| `repair_ownership` | 4 |
| `add` | 3 |

## Candidate Lanes By Bucket

| Bucket | Lane | Count |
| --- | --- | ---: |
| `diagnosis_context_span` | active_rate | 14 |
| `diagnosis_context_span` | none | 12 |
| `diagnosis_context_span` | seizure_free | 11 |
| `diagnosis_context_span` | qualitative_change | 4 |
| `diagnosis_context_span` | reject | 1 |
| `generic_named_ownership` | active_rate | 4 |
| `other_or_ambiguous` | active_rate | 8 |
| `other_or_ambiguous` | seizure_free | 3 |
| `other_or_ambiguous` | none | 2 |
| `other_or_ambiguous` | qualitative_change | 2 |
| `other_or_ambiguous` | reject | 1 |
| `other_or_ambiguous` | reject_or_seizure_free | 1 |
| `seizure_free_cui_convention` | seizure_free | 9 |
| `seizure_free_cui_convention` | reject | 3 |
| `state_swap` | none | 7 |
| `state_swap` | active_rate | 3 |
| `state_swap` | qualitative_change | 2 |
| `state_swap` | reject | 1 |
| `true_candidate_gap` | none | 2 |

## Top Letter Pair Patterns

| Pattern | Count | Letters |
| --- | ---: | --- |
| `predicted:active-rate` | 11 | EA0057, EA0085, EA0114, EA0146, EA0148, EA0153, EA0162, EA0172, EA0200 |
| `gold:active-rate -> predicted:active-rate` | 8 | EA0047, EA0110, EA0169, EA0181 |
| `gold:active-rate -> predicted:unknown` | 8 | EA0096, EA0117, EA0158 |
| `predicted:seizure-free` | 7 | EA0005, EA0071, EA0113, EA0126, EA0160, EA0171, EA0176 |
| `gold:seizure-free` | 6 | EA0011, EA0063, EA0137, EA0168, EA0186, EA0191 |
| `gold:active-rate` | 6 | EA0054, EA0056, EA0108, EA0119 |
| `gold:seizure-free -> predicted:seizure-free` | 6 | EA0127, EA0180, EA0190 |
| `gold:active-rate+unknown` | 5 | EA0049, EA0050 |
| `gold:seizure-free -> predicted:active-rate+seizure-free` | 5 | EA0143 |
| `gold:active-rate -> predicted:seizure-free` | 4 | EA0006, EA0038 |
| `predicted:unknown` | 4 | EA0131, EA0135, EA0166, EA0197 |
| `gold:unknown -> predicted:seizure-free+unknown` | 3 | EA0087 |
| `gold:seizure-free -> predicted:active-rate+unknown` | 3 | EA0121 |
| `predicted:active-rate+seizure-free` | 2 | EA0092 |
| `gold:unknown` | 2 | EA0111, EA0128 |
| `gold:unknown -> predicted:unknown` | 2 | EA0184 |
| `gold:unknown -> predicted:active-rate` | 2 | EA0198 |

## Read

The v0.8 work completed a pre-change dev140 residual panel that separates clinical SF state/ownership failures from benchmark-format convention and context-span residuals.

Not supported:
The panel does not show that v0.8 improves SeizureFrequency and does not authorize a prediction-bearing SF rule.

## Examples By Bucket

### `diagnosis_context_span`

| Letter | Side | State | Type family | Action | Evidence | Opposite |
| --- | --- | --- | --- | --- | --- | --- |
| EA0005 | predicted | seizure-free | named_cui | drop | Generalised tonic clonic seizure |  |
| EA0006 | gold | active-rate | named_cui | no_action | generalised-tonic-clonic-seizures-2014 | predicted/seizure-free/seizure_free_concept |
| EA0006 | predicted | seizure-free | seizure_free_concept | drop | seizure free | gold/active-rate/named_cui |
| EA0011 | gold | seizure-free | named_cui | no_action | Focal-to-bilateral-convulsive-seizure |  |
| EA0038 | predicted | seizure-free | seizure_free_concept | drop | seizure free | gold/active-rate/named_cui |

### `generic_named_ownership`

| Letter | Side | State | Type family | Action | Evidence | Opposite |
| --- | --- | --- | --- | --- | --- | --- |
| EA0169 | gold | active-rate | generic_seizure | repair_ownership | seizures | predicted/active-rate/named_cui |
| EA0169 | predicted | active-rate | named_cui | repair_ownership | focal dyscognitive seizures | gold/active-rate/generic_seizure |
| EA0181 | gold | active-rate | generic_seizure | repair_ownership | seizures- | predicted/active-rate/named_cui |
| EA0181 | predicted | active-rate | named_cui | repair_ownership | focal dyscognitive seizures | gold/active-rate/generic_seizure |

### `other_or_ambiguous`

| Letter | Side | State | Type family | Action | Evidence | Opposite |
| --- | --- | --- | --- | --- | --- | --- |
| EA0056 | gold | active-rate | named_cui | add | secondary-generalised-seizures |  |
| EA0057 | predicted | active-rate | named_cui | no_action | focal motor seizures |  |
| EA0071 | predicted | seizure-free | generic_seizure | no_action | seizure |  |
| EA0085 | predicted | active-rate | generic_seizure | no_action | seizures |  |
| EA0087 | predicted | unknown | named_cui | no_action | myoclonic jerks | gold/unknown/named_cui |

### `seizure_free_cui_convention`

| Letter | Side | State | Type family | Action | Evidence | Opposite |
| --- | --- | --- | --- | --- | --- | --- |
| EA0127 | gold | seizure-free | seizure_free_concept | repair_benchmark_format | seizures-free. | predicted/seizure-free/generic_seizure |
| EA0127 | predicted | seizure-free | generic_seizure | repair_benchmark_format | seizures | gold/seizure-free/seizure_free_concept |
| EA0143 | gold | seizure-free | generic_seizure | repair_benchmark_format | seizure- | predicted/active-rate/named_cui; predicted/seizure-free/seizure_free_concept; predicted/seizure-free/named_cui |
| EA0143 | predicted | seizure-free | seizure_free_concept | repair_benchmark_format | seizure-free | gold/seizure-free/generic_seizure |
| EA0180 | gold | seizure-free | seizure_free_concept | repair_benchmark_format | seizrue-free | predicted/seizure-free/generic_seizure |

### `state_swap`

| Letter | Side | State | Type family | Action | Evidence | Opposite |
| --- | --- | --- | --- | --- | --- | --- |
| EA0096 | gold | active-rate | named_cui | repair_state | generalised-tonic-clonic-seizures | predicted/unknown/named_cui; predicted/unknown/generic_seizure |
| EA0096 | predicted | unknown | named_cui | repair_state | generalised tonic clonic seizures | gold/active-rate/named_cui |
| EA0117 | gold | active-rate | generic_seizure | repair_state | seizures | predicted/unknown/generic_seizure |
| EA0117 | predicted | unknown | generic_seizure | repair_state | seizures | gold/active-rate/generic_seizure |
| EA0121 | gold | seizure-free | named_cui | repair_state | focal-to-bilateral-convulsive-seizure | predicted/unknown/named_cui; predicted/active-rate/named_cui |

### `true_candidate_gap`

| Letter | Side | State | Type family | Action | Evidence | Opposite |
| --- | --- | --- | --- | --- | --- | --- |
| EA0038 | gold | active-rate | named_cui | no_action | generalised-tonic-chronic-seizure | predicted/seizure-free/seizure_free_concept |
| EA0087 | gold | unknown | named_cui | no_action | generalised-tonic-clinic-seizure | predicted/unknown/named_cui; predicted/seizure-free/seizure_free_concept |
