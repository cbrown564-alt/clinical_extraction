# Gan 2026 Hybrid — Comprehensive Row-Level Error Analysis (validation750)

Date: 2026-06-16

Cycle C4. Validation-only, no model calls. Source: the consensus + fresh
agreement selector v0.9 no-call replay
(`experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl`,
733/750), cross-checked against `experiments/_c1_no_correct_rows_extract.json` and
the v0.9 residual audit. Purpose: ground the optimization experiments in row-level
evidence (per user instruction).

## Headline split

17 selected-wrong rows: **6 selector-addressable** (a correct component exists,
unselected) and **11 component-generation-required** (no component is
Purist-correct). The 11 are exactly the residual-audit set; selector oracle ceiling
is 739/750. The component-generation residual concentrates in `band_unknown`
(8/11). Selected-wrong by band: unknown 10, monthly 3, submonthly 2, weekly 2.

## Ranked failure clusters

| Rank | Clinical mechanism | Rows | Bound by | Transfer | Why the model errs |
| --- | --- | --- | --- | --- | --- |
| 1 | **Seizure-free over-inference** (last-event date → quantified seizure-free duration), gold=unknown | 11216, 11254, 11272, 5534 (+14821 selector-side) | generation (+1 selector) | **Generalisable** — "last seizure DATE, none since" is canonical in real letters | Converts a single dated last-event + "no further events" into a quantified duration; cannot withhold when only one anchor event exists. |
| 2 | **Underspecified/provoked count → quantified rate**, gold=unknown | 6321, 6368, 14025 (+3356, 7168 selector-side) | generation (+2 selector) | **Generalisable** — provoked/situational counts pervasive in real letters | Reads an explicit count+window describing provoked/transient events and emits a habitual rate; does not recognise a provoked count is not a habitual frequency. |
| 3 | **Cluster-axis flattening** (cadence kept, per-cluster burden dropped) | 9937, 9943 | generation | **Generalisable** | Encodes the cluster interval but drops the multiple-per-cluster axis, landing a band low. |
| 4 | **Denominator/window error on a genuine rate** | 13209 | generation | **Generalisable** | Anchors on the salient recent cadence instead of the actual once-in-8-months rate. |
| 5 | **Highest-semiology / denominator conflict** (correct fresh exists, selector kept deterministic) | 6153, 7615, 9496 | selector | Mostly synthetic-artifact | A correct fresh component exists but the selector kept the deterministic baseline. Not a generation gap. |

Cluster 5 (+14821, 3356, 7168) = the 6 selector-addressable rows; low transfer
value.

## Test-error extrapolation (which mechanisms drive the unmeasured ~71 test errors)

Validation is saturated (17 wrong) but the holdout has ~71 wrong, so the test
residual is dominated by **generation** failures, not selector ties. Ranked by
share of the generation residual and gold-stratum mass:

1. **Seizure-free over-inference (Cluster 1)** — highest leverage; `band_unknown`
   is ~23% of validation and the largest no-correct cluster, most under-sampled
   relative to its true frequency, most KCL-generalisable.
2. **Underspecified/provoked count → rate (Cluster 2)** — pervasive in real
   letters; the robustness battery Panels A/B fail here.
3. **Cluster-axis flattening (Cluster 3)** — named weakest battery axis; smaller
   count but high per-row failure rate when a cluster is present.
4. **Denominator/window errors (Cluster 4)** — `band_weekly` is the named
   family-transition regression band.

Selector-addressable failures are NOT expected to dominate test: at full holdout
deterministic/consensus borrowing overfits (protocol Insight 1), so the selector
residual does not scale up the way the generation residual does.

## Prioritized experiment plan (drove C5–C7)

1. **Cluster 1 first** (highest leverage, most generalisable, evidence problem not
   contract problem): stop the fresh-evidence reasoner turning a single dated
   last-event into a quantified duration. **Critical guardrail:** confidence-gate
   any coerce-to-unknown — the un-gated version regressed the bare labeler −106
   (C3). → became C5 (triage scaffold; rejected −81) and the basis for C7.
2. Cluster 3 cluster-axis retention as a narrow additive gate (no unknown-coercion)
   → became C6 (gap-robust but +0 test).
3. Cluster 2 provoked-count, gated tightest (highest regression risk).

> Epilogue: C5/C6/C7 executed this plan. C7's structural finding (the correct
> `unknown` rows are feature-identical to genuine-rate rows on every inference-time
> signal) explains why Clusters 1–2 are not closable via selection on
> gpt-4.1-mini. See `docs/research/gan2026_f1_dynamic_workflow_night_synthesis_2026-06-16.md`.
