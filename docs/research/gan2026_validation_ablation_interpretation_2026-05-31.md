# Gan 2026 Validation Ablation Interpretation

Date: 2026-05-31

Primary artifact:
`experiments/gan2026_v1_validation_ablation_2026-05-31.md`

Changed-row artifact:
`experiments/gan2026_v1_validation_ablation_changed_rows_2026-05-31.csv`

This note interprets the validation-only deterministic rule ablation. It is not
a held-out benchmark claim. The frozen deterministic V1 test holdout remains
0.7600 Purist micro F1/accuracy and should not be used for development tuning.

## Executive Interpretation

The ablation turns deterministic V1 from a high-scoring but validation-saturated
rule stack into a controlled diagnostic object. The main result is not that V1
is a final system. The main result is that we can now see which deterministic
mechanisms are carrying validation performance and which mechanisms are likely
overreaching.

The ablation supports the current project thesis: deterministic rules are useful
and auditable, but the remaining path to a more credible system should come from
structured selection and hybrid clinical reasoning, not from more unbounded
hand-written regex rules.

## Main Signals

The latest ablation run reports a current working-tree validation baseline of
0.9293 Purist micro F1/accuracy and 0.9387 Pragmatic micro F1/accuracy on 750
validation rows, with 750/750 exact selected-evidence validity.

Disabling portable-rate expressions has the largest extraction effect: 183 rows
change and Purist micro F1 falls to 0.7627. This shows that ordinary rate and
interval expressions are the most important deterministic substrate. It also
means these rules deserve the strongest portability, paraphrase, and adversarial
testing.

Disabling temporal selection changes 135 rows and drops Purist micro F1 to
0.7787. Final candidate choice is therefore not a minor implementation detail.
It is a core model component. Any next candidate should treat selection as an
explicit reasoning surface over assertion, temporality, semiology, target event,
window, normalized rate, and uncertainty.

Disabling seizure-free/no-event assertions changes 131 rows and drops Purist
micro F1 to 0.8107. This group is important but clinically brittle. The changed
rows show cases where disabling seizure-free logic turns false seizure-free
predictions into gold-unknown or no-reference predictions. That is a strong
signal that absence, remission, current-control, and uncertainty should move
toward a clinical reasoner or adjudicator rather than more broad catch-all
absence patterns.

Cluster arithmetic and diary/log aggregation are narrower but meaningful
contributors. Disabling them drops Purist micro F1 to 0.8600 and 0.8507,
respectively. These groups appear to support specialized expression families
that are clinically real but phrase-sensitive. They should remain ablatable and
should be tested for whether gains transfer beyond exact Gan wording.

Gan-specific shorthand helps but is not the main performance story. Disabling it
drops Purist micro F1 to 0.9027. This supports keeping the group isolated as
dataset-specific benchmark support rather than presenting it as general clinical
logic.

Benchmark repair changes 6 labels but does not move aggregate Purist or
Pragmatic F1 in this run. It should remain isolated and traceable as benchmark
formatting support, not as a scientific performance driver.

Date-duration utilities do not change rows under group ablation in this report.
They appear to remain helper-backed support rather than an independently
executable extraction surface.

## Drift Resolution

The earlier 0.9280 versus 0.9120 validation-baseline discrepancy was a behavior
regression introduced during diary/log rule-catalogue refactoring. Sparse monthly
timeline patterns from saturated V1 were not fully carried forward into
`gan2026.rules.diary`, causing 13 formerly correct validation rows to fall back
to no-reference predictions. Restoring those patterns as catalogued
`RuleSpec`s, with focused tests, raises the current working-tree validation
baseline to 0.9293 Purist micro F1/accuracy and preserves 750/750 exact
selected-evidence validity.

## Research Implications

The strongest paper-facing interpretation is that deterministic V1 reached high
validation performance by accumulating many useful but partly brittle rules. The
ablation makes those rules inspectable, grouped, and measurable. That is a
better research object than an opaque regex stack.

The held-out drop to 0.7600 Purist micro F1/accuracy remains central context. In
combination with the ablation, it suggests that deterministic saturation learned
many validation-surface phrase families but did not produce robust general
clinical reasoning.

The next credible system should preserve deterministic extraction as a strong
candidate generator and evidence collector, then add an explicit reasoning layer
for the cases where rules over-select, misinterpret currentness, confuse
seizure-free with unknown/no-reference, or mishandle semiology and clusters.

## Recommended Actions

1. Keep deterministic V1 frozen as the saturated hand-rule baseline.
2. Mine the changed-row CSV for rows where disabling a deterministic group
   improves correctness. These are valuable examples of deterministic overreach.
3. Build a small validation-only prompt/adjudicator development set from those
   rows, preserving the deterministic candidates, selected evidence, baseline
   prediction, ablated prediction, and gold label.
4. Start validation-only LLM/DSPy experiments on temporal selection,
   seizure-free versus unknown/no-reference, trigger-conditioned events,
   semiology reconciliation, non-epileptic/EEG-only mapping, and cluster-detail
   interpretation.
5. Add paraphrase and adversarial tests for portable-rate expressions and
   seizure-free/no-event assertions, since they are both important and likely to
   overfit exact phrasing.
6. Keep benchmark repair and Gan shorthand explicitly labeled as
   benchmark-specific or dataset-specific support in future tables.

## Bottom Line

This ablation is best interpreted as a promotion of V1 from a saturated
deterministic baseline to a controlled comparator for hybrid experiments. It
does not justify further unbounded hand-rule growth. It does justify the next
phase: preserve the deterministic candidate/evidence substrate, make selection
more explicit, and use validation-only LLM/DSPy reasoning to address the
failure families exposed by ablation.
