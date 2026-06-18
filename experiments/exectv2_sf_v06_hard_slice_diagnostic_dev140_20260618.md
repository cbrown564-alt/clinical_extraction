# ExECTv2 SF v0.6 Hard-Slice Diagnostic

- Generated: `2026-06-18`
- JSON: `experiments\exectv2_sf_v06_hard_slice_diagnostic_dev140_20260618.json`
- Source JSONL: `experiments\exectv2_hybrid_sf_state_projection_v06_combined_dev140_20260618.jsonl`
- Split: `dev`
- Letters: 140

## Residual By State

| State | FN | FP |
| --- | ---: | ---: |
| active-rate | 17 | 19 |
| seizure-free | 11 | 17 |
| unknown | 8 | 22 |

## Unknown-State Hard Slice

- Unknown residual events: 30
- Gold misses: 8
- Predicted over-emissions: 22

| Bucket | Count |
| --- | ---: |
| `unknown_fp.state_swap_against_gold_active-rate` | 7 |
| `unknown_fp.generic_named_ownership_gap` | 5 |
| `unknown_fp.grounded_scope_overemit` | 4 |
| `unknown_fn.state_swap_with_predicted_active-rate` | 3 |
| `unknown_fp.state_swap_against_gold_seizure-free` | 3 |
| `unknown_fn.change_candidate_available_not_selected` | 2 |
| `unknown_fn.no_matching_candidate_or_type` | 2 |
| `unknown_fp.unsupported_or_conditional_change` | 2 |
| `unknown_fn.generic_named_ownership_gap` | 1 |
| `unknown_fp.drug_response_scope` | 1 |

## Read

The remaining SF blocker is now concentrated in unknown-state precision. v0.6 recovered many unknown misses, but the residual is asymmetric: 22 predicted unknown over-emissions versus 8 gold unknown misses.

The biggest buckets are grounded scope/ownership disagreements, not render failures. This argues against another broad unknown/change recovery rule. A further loop would need a predeclared hard-slice intervention aimed at high-precision unknown suppression, with a stop rule if active-rate or seizure-free recall regresses.

Supported claim:

> After v0.6, the remaining SF blocker is not broad state recall. Unknown-state recall is high enough to expose a precision problem: 22 unknown over-emissions versus 8 unknown misses.

Not supported:

> Another broad unknown/change recovery rule is likely to clear the 0.8 gate without collateral precision loss.

## Examples: `unknown_fn.change_candidate_available_not_selected`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0049 | gold | absence |  | ["cui", "C0494475"]/active-rate:generalised tonic clonic seizures; ["cui", "C0494475"]/active-rate:generalised tonic clonic seizures; ["cui", "C0494475"]/unknown:generalised tonic clonic seizures |
| EA0049 | gold | myoclonic-jerks |  | ["cui", "C0494475"]/active-rate:generalised tonic clonic seizures; ["cui", "C0494475"]/active-rate:generalised tonic clonic seizures; ["cui", "C0494475"]/unknown:generalised tonic clonic seizures |

## Examples: `unknown_fn.generic_named_ownership_gap`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0050 | gold | absences |  | ["cui", "C0494475"]/active-rate:generalised tonic clonic seizures; ["cui", "C0036572"]/unknown:seizures |

## Examples: `unknown_fn.no_matching_candidate_or_type`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0128 | gold | myoclonic-jerks |  | ["cui", "C0494475"]/seizure-free:generalised tonic clonic seizures |
| EA0184 | gold | typical-absences |  | ["cui", "C0494475"]/active-rate:generalised tonic clonic seizures; ["cui", "C0563606"]/unknown:absences |

## Examples: `unknown_fn.state_swap_with_predicted_active-rate`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0087 | gold | generalised |  | ["cui", "C0494475"]/active-rate:generalised tonic clonic seizures |
| EA0111 | gold | seizures |  | ["cui", "C0036572"]/active-rate:seizures |
| EA0198 | gold | seizures |  | ["cui", "C0036572"]/active-rate:seizure; ["cui", "C0036572"]/active-rate:seizures |

## Examples: `unknown_fp.drug_response_scope`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0040 | predicted | seizures | Since the last consultation you have started him on lamotrigine, and this has helped his seizures. |  |

## Examples: `unknown_fp.generic_named_ownership_gap`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0096 | predicted | seizures | His control had deteriorated prior to increasing the valproate but had then improved to the odd stare only | ["cui", "C0494475"]/active-rate:generalised-tonic-clonic-seizures; ["cui", "C0563606"]/unknown:absences |
| EA0121 | predicted | focal seizures with altered awareness | These can occur in clusters very frequently so that he doesn’t really recover consciousness. | ["cui", "C0036572"]/unknown:seizures; ["cui", "C0877017"]/seizure-free:focal-to-bilateral-convulsive-seizure |
| EA0131 | predicted | generalised tonic clonic seizures | She is having quite a number of generalised tonic clonic seizures which her partner described to me today. | ["cui", "C0036572"]/unknown:seizures |
| EA0131 | predicted | convulsive seizures | Howevere this has to be balanced against the risks of frequent convulsive seizures which do carry the risk of serious injury and death. | ["cui", "C0036572"]/unknown:seizures |
| EA0135 | predicted | seizures | After a fairly long period of around 6 months without having seizures unfortunately Mr Francis had a cluster of seizures over the weekend. | ["cui", "C3203523"]/active-rate:cluster-of-seizures |

## Examples: `unknown_fp.grounded_scope_overemit`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0078 | predicted | seizures | Her seizures are reasonably controlled by her low mood as well as some agitation is causing her some distress. |  |
| EA0158 | predicted | focal motor seizures | She also gets focal motor seizures where her right arm will twitch continually, sometimes for up to 5 hours. | ["cui", "C0270834"]/active-rate:focal-seizures-with-altered-awareness; ["cui", "C0234533"]/active-rate:generalised-seizure |
| EA0166 | predicted | seizures | Although her jerks have improved significantly they are still occurring around once a month. |  |
| EA0184 | predicted | absences | His brother said that he has had three generalised tonic clonic seizures and more of his typical absences since the last clinic appointment. | ["cui", "C0494475"]/active-rate:generalised-tonic-clonic-seizure; ["cui", "C4316903"]/unknown:typical-absences |

## Examples: `unknown_fp.state_swap_against_gold_active-rate`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0087 | predicted | myoclonic jerks | She felt that things were much better as her myoclonic jerks have almost stopped. | ["cui", "C0027066"]/active-rate:myoclonic-jerks |
| EA0096 | predicted | generalised tonic clonic seizures | On Sunday and Monday, he was having generalised tonic clonic seizures in the night and frequent drops and absences throughout the day | ["cui", "C0494475"]/active-rate:generalised-tonic-clonic-seizures |
| EA0110 | predicted | seizures | Once her seizures are controlled Sodium Valproate should be reduced to nil gradually. | ["cui", "C0036572"]/active-rate:seizures |
| EA0117 | predicted | seizures | she is still struggling with seizures, which are occurring on a weekly basis | ["cui", "C0036572"]/active-rate:seizures |
| EA0151 | predicted | seizures | This is unusual as before this her seizures have been relatively well controlled. | ["cui", "C0036572"]/active-rate:seizures |

## Examples: `unknown_fp.state_swap_against_gold_seizure-free`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0063 | predicted | seizures | I explained the lamotrigine was generally thought to be safe in pregnancy and so given her background of frequent seizures it would be important to continue the medication should she become pregnant. | ["cui", "C0036572"]/seizure-free:seizures; ["cui", "C0036572"]/seizure-free:seizures |
| EA0137 | predicted | seizures | She thinks that this may have helped her seizures and interestingly her mood has improved since taking the lamotrigine. | ["cui", "C0036572"]/seizure-free:seizure |
| EA0186 | predicted | focal motor seizures | These were happening frequently before he started the medication. | ["cui", "C0016399"]/seizure-free:focal |

## Examples: `unknown_fp.unsupported_or_conditional_change`

| Letter | Side | Text | Evidence | Opposite |
| --- | --- | --- | --- | --- |
| EA0079 | predicted | seizures | His epilepsy has been stable over the last few years | ["cui", "C0494475"]/active-rate:generalised |
| EA0199 | predicted | seizures | He is getting around 2 seizures per month at the moment which is good for him as previously he has had several seizures per week | ["cui", "C0036572"]/active-rate:seizures |
