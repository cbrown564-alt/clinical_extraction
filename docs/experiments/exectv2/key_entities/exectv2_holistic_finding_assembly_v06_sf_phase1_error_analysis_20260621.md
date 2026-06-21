# ExECTv2 Holistic Finding Assembly v06 SeizureFrequency Phase 1 Error Analysis

- Date: `2026-06-21`
- Split: `dev140`
- Current control before phase: `exectv2_holistic_finding_assembly_v05_dev140`
- New candidate: `exectv2_holistic_finding_assembly_v06_dev140`
- SF source artifact: `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl`
- Assembly artifacts: `experiments/exectv2_holistic_finding_assembly_v06_dev140_20260621.jsonl`, `experiments/exectv2_holistic_finding_assembly_v06_dev140_20260621.json`
- Error ledger: `experiments/exectv2_holistic_finding_assembly_v06_error_ledger_dev140_20260621.md`

## Result

| Candidate / surface | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| v05 official assembly headline | 0.8576 | 0.9083 | 0.8068 | 0.8214 | 0.8615 |
| v06 official assembly headline | 0.8789 | 0.9083 | 0.9053 | 0.8214 | 0.8615 |

The official holistic assembly surface now clears the `>0.900` target for
SeizureFrequency: `F1=0.9053`, `P=0.9000`, `R=0.9107`, `TP=153`, `FP=17`,
`FN=15`. The direct SF arbitration artifact scores higher under the standalone
frequency-state scorer: `F1=0.9263`, `P=0.9181`, `R=0.9345`, `TP=157`,
`FP=14`, `FN=11`. Use the assembly score as the family headline for the active
goal and the direct artifact score as component evidence.

## Hypothesis

v05 was not mainly failing because GPT-4.1-mini could not find seizure-frequency
evidence. It was failing because the best GPT lane and the deterministic SF
extractor made complementary type/state errors:

- The intersection of current GPT SF and deterministic SF was almost perfectly
  precise but low recall.
- The union had enough true positives to clear the target but added many false
  positives.
- The dominant FP classes were source-shortened deterministic anchors
  (`seizures`, `seizure`, `absences`, `jerks`), non-target events, historical
  or advice seizure-free language, and anaphoric generic/named ownership errors.
- Several FNs were benchmark-surface mismatches rather than missing evidence:
  `cluster of 3` versus `seizure cluster`, `absences` versus `typical absences`,
  and `these seizures` assigned to a named type when the gold key is generic.

## Ablations

| Ablation | Surface | SF F1 | P | R | TP | FP | FN | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v05 current GPT SF lane | official assembly | 0.8068 | 0.7717 | 0.8452 | 142 | 42 | 26 | High recall but too many state/type FPs. |
| deterministic all-entity SF drop-in | assembly diagnostic | 0.8263 | 0.8313 | 0.8214 | 138 | 28 | 30 | Better precision, still insufficient recall. |
| current and deterministic intersection | assembly diagnostic | 0.8464 | 0.9920 | 0.7381 | 124 | 1 | 44 | Precision oracle; recall too low. |
| current and deterministic union | assembly diagnostic | 0.8041 | 0.7022 | 0.9405 | 158 | 67 | 10 | Recall reserve exists, but unfiltered union is noisy. |
| v08 union arbitration | direct SF artifact | 0.9263 | 0.9181 | 0.9345 | 157 | 14 | 11 | Suppression plus benchmark rewrites solve most union noise. |
| v06 holistic assembly | official assembly | 0.9053 | 0.9000 | 0.9107 | 153 | 17 | 15 | Promoted as dev-only SF phase result. |

## Accepted Rules

The accepted v08 arbitration is a deterministic no-call replay over saved
GPT-4.1-mini SF output and deterministic all-entity SF output. It is
prediction-bearing post-processing, not a pure model gain.

| Rule family | Portability | Count |
| --- | --- | ---: |
| `drop_det_short_generic_anchor` | seizure_frequency | 84 |
| `drop_non_target_event` | seizure_frequency | 9 |
| `drop_historical_or_advice_state` | seizure_frequency | 8 |
| `drop_bare_seizure_free_context` | seizure_frequency | 6 |
| `drop_anaphoric_generic_state` | seizure_frequency | 5 |
| `drop_named_unknown_long_context` | seizure_frequency | 4 |
| `drop_det_generic_short_rate` | seizure_frequency | 3 |
| `drop_diffuse_unknown` | seizure_frequency | 3 |
| `drop_generic_free_history_or_span` | seizure_frequency | 3 |
| `drop_current_bare_named_event` | seizure_frequency | 2 |
| `drop_composite_and_anchor` | seizure_frequency | 1 |
| `drop_contextual_unknown` | seizure_frequency | 1 |
| `drop_seizure_free_active_rate` | seizure_frequency | 1 |
| `rewrite_anaphoric_named_to_generic_seizures` | benchmark_format | 2 |
| `rewrite_absences_to_typical_absences` | benchmark_format | 1 |
| `rewrite_cluster_of_3_to_seizure_cluster` | benchmark_format | 1 |
| `rewrite_up_to_range_lower_zero` | benchmark_format | 1 |

## Residuals

On the direct SF artifact ledger, residual false negatives are now small and
mostly generic seizure states: generic seizure-free (`3`), generic active-rate
(`3`), generic unknown (`2`), plus one each for GTC active-rate, seizure-free
surface `C1299590`, myoclonic-jerk unknown, and typical-absence unknown.

Residual false positives are mostly clinically plausible but benchmark-fragile
cases: exact short deterministic named anchors, one-off event counts, a
drug-change seizure-free phrase with typoed `episodes`, and named active-rate
or unknown states whose gold key is either generic or omitted.

The active-rate fidelity companion remains low in the v06 assembly:
`active_rate_fidelity=0.5969`. The family headline forgives rate magnitude once
type and state match, so the achieved `0.9053` should be described as a
type/state headline result, not a complete quantitative-rate solution.

## Decision

Promote v06 as the current dev-only holistic assembly control for
SeizureFrequency. Do not treat it as holdout evidence. The next family should be
Investigations (`0.8615`), while Prescription (`0.8214`) remains last because it
is expected to have the highest ceiling after dedicated regimen normalization.
