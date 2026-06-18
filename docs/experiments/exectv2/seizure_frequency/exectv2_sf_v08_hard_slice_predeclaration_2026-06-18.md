# ExECTv2 SF v0.8 Hard-Slice Predeclaration

Date: 2026-06-18
Scope: SeizureFrequency v0.7 residuals on dev140.
Status: predeclared diagnostic; no prediction-bearing rule change.

## Objective

Build a dev140-only hard-slice panel over the remaining SeizureFrequency
clinical-recovery residual after v0.7. The purpose is to decide whether any
future v0.8 prediction-bearing change is attributable, finite, and safer than
leaving v0.7 as the promoted SF route.

This document predeclares the diagnostic before any new SF prediction rule. It
does not authorize a rule implementation, a model call, a full-200 audit, or
test/holdout row-level inspection.

## Fixed Baseline

Primary baseline:
`experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl`

Residual ledger:
`experiments/exectv2_key_entities_clinical_error_ledger_v07sf_dev140_20260618.json`

Human readout:
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_v07_residual_diagnostic_2026-06-18.md`

Current SeizureFrequency clinical-recovery headline:

| F1 | Precision | Recall | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.7824 | 0.7588 | 0.8075 | 151 | 48 | 36 |

Residual by side/state:

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold/candidate_miss | 17 | 11 | 8 |
| predicted/wrong_detail_selection | 19 | 17 | 12 |

## Residual Unit

The diagnostic unit is an unmatched SeizureFrequency clinical-recovery key from
the v0.7 ledger, paired within the same letter when an opposite-side residual
shares state, CUI/phrase ownership, evidence neighborhood, or candidate source.

For each residual unit, record:

- `letter_id`
- `side`: `gold` or `predicted`
- `state`: `active-rate`, `seizure-free`, or `unknown`
- normalized type key or CUI/phrase key
- evidence text when present in the prediction artifact
- opposite-side residual summary from the same letter
- candidate-span availability and candidate lane, if present
- bucket from the taxonomy below
- possible action class: `add`, `drop`, `repair_state`, `repair_ownership`,
  `repair_benchmark_format`, or `no_action`
- portability category for any possible future action

The diagnostic may inspect dev140 gold residuals because it is offline error
analysis. Any future rule must be implemented without gold access.

## Hard-Slice Taxonomy

Each residual unit must receive exactly one primary bucket. Secondary tags are
allowed only for explanation; promotion gates use the primary bucket.

| Bucket | Operational definition | Future action category |
| --- | --- | --- |
| `generic_named_ownership` | Gold and prediction disagree on generic `seizure(s)` versus a named seizure type while carrying the same broad state and compatible local evidence. Includes named-to-generic and generic-to-named swaps. | `seizure_frequency` unless the action only changes CUI/phrase rendering, then `benchmark_format` |
| `state_swap` | Gold and prediction share a plausible seizure anchor or type but disagree on active-rate, seizure-free, or unknown state. | `seizure_frequency` |
| `seizure_free_cui_convention` | Clinical seizure-free meaning is aligned, but the residual is driven by generic seizure CUI `C0036572` versus seizure-free concept `C1299590`, or phrase rendering of `seizure free` versus `seizure(s)`. | `benchmark_format` unless the rule changes whether an event is seizure-free |
| `diagnosis_context_span` | The candidate/prediction is triggered by diagnosis, syndrome, semiology description, risk/advice, family history, photosensitivity, treatment-response context, or other non-frequency context span. | usually `seizure_frequency` suppression; may be `no_action` if no non-gold feature is finite |
| `true_candidate_gap` | Gold frequency fact has no matching candidate span, no same-letter opposite-side state/ownership pair, and no finite non-gold cue currently exposed in the v0.7 artifact. | no direct rule until candidate-generation evidence is designed separately |
| `other_or_ambiguous` | Residual cannot be assigned reproducibly to one of the above buckets. | no action |

Tie-break order:

1. Use `seizure_free_cui_convention` before `generic_named_ownership` when the
   only material difference is `C0036572` versus `C1299590` for seizure-free
   meaning.
2. Use `state_swap` before ownership when the same seizure type has opposing
   active-rate, seizure-free, or unknown state.
3. Use `diagnosis_context_span` before `true_candidate_gap` when the prediction
   evidence is source-near but clinically not a frequency assertion.
4. Use `true_candidate_gap` only when no existing candidate or prediction-side
   evidence exposes a finite intervention surface.

## Minimum Panel

The diagnostic must include all v0.7 SeizureFrequency residual units from the
clinical-recovery ledger, not a convenience sample. It must also report a
paired-letter summary so a row with both a miss and an over-emission is visible
as a possible substitution, not two unrelated errors.

Required tables:

- bucket counts by side and state;
- bucket counts by CUI/phrase family;
- top letter-level pair patterns, such as active-rate gold versus unknown
  prediction;
- possible-fix counts by action class;
- examples limited to dev140 rows and labeled as development-only.

## Promotion Gate For Any Future v0.8 Rule

A later prediction-bearing v0.8 rule may be proposed only if one primary bucket
meets all conditions:

- at least 5 possible fixes in the bucket;
- at least 80 percent of sampled bucket examples share one explicit non-gold
  feature available in the v0.7 artifact;
- the proposed rule has one named action and one portability category;
- the proposed rule can be replayed as an ablation against unchanged v0.7 input;
- the rule has a stop condition protecting active-rate and seizure-free recall;
- expected collateral risk is stated for every other bucket.

Promotion after replay requires:

- headline SF F1 improves by at least `0.010`;
- the target bucket's FP or FN count improves by at least `5`;
- active-rate recall drops by no more than `0.005`;
- seizure-free recall drops by no more than `0.005`;
- unknown FN count increases by no more than `2`;
- evidence validity remains at least `0.99`;
- every changed prediction has a named rule/action count;
- benchmark-format-only changes are reported separately from clinical SF state
  changes.

## Stop Rules

Reject a future v0.8 rule if any condition holds:

- it uses gold labels at prediction time;
- it broadens generic recovery or suppression beyond the predeclared bucket;
- it blends benchmark CUI convention repair with clinical state repair without
  separable ablation counts;
- it regresses active-rate or seizure-free recall beyond the gate;
- the apparent gain comes mainly from `other_or_ambiguous`;
- examples require full-200, test, Gan holdout, or external model inspection.

## Allowed Next Work

Allowed:

- write an offline dev140 diagnostic script or notebook that reads only the
  fixed v0.7 artifacts and emits the required tables;
- add tests for that diagnostic if it becomes executable code;
- manually review dev140 residual examples only for taxonomy assignment;
- update documentation with the diagnostic output.

Not allowed:

- model calls;
- new prediction-bearing SF rules;
- full-200 or test/holdout inspection;
- Gan `test450` row-level inspection;
- changing scoring or evaluation semantics.

## Claim Boundaries

Supported by completing this predeclaration:

> The next SeizureFrequency step is a pre-change dev140 residual taxonomy that
> separates clinical state/ownership failures from benchmark-format convention
> failures before any v0.8 rule is attempted.

Not supported:

> v0.8 improves SeizureFrequency.

> Any specific residual bucket is large or clean enough for implementation.

> The current dev140 result generalizes beyond the development surface.
