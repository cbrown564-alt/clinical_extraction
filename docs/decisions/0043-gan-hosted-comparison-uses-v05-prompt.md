# 0043: Use prompt v0.5 for the hosted Gan model comparison

Date: 2026-07-16
Status: accepted; protocol and runs pending

## Decision

The next hosted Gan comparison for GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol,
and DeepSeek V4 Flash will use
`gan2026_hybrid_structured_events_v0.5` for every model.

Prompt v0.5 becomes the default comparison prompt for this four-model panel.
The completed v0.7 panel remains frozen evidence for that exact prompt and is
not deleted or relabelled, but it is not the selected default comparison.

## Reason

Prompt v0.5 is the shortest shared structured-events prompt. It defines the
event schema, selection schema, evidence requirement, and common clinical
selection task without the later model-specific policy additions.

Prompt v0.6 added one seizure-free-versus-recent-frequency precedence rule
after DeepSeek Chat validation failures. Prompt v0.7 retained that rule and
added a larger count-conservation policy after DeepSeek Reasoner validation
failures. Those additions may be useful interventions for those exact DeepSeek
conditions, but they make the prompt less neutral as the shared instruction for
a cross-model comparison.

The retained GPT-4.1-mini single-pass result of `364/450` Purist is identified
by its evidence manifest as prompt v0.5. Earlier documents that called this
result v0.6 were incorrect. This result motivates returning to the simpler
prompt, but it does not by itself establish that v0.5 is best for every model.
The new panel is a controlled comparison, not post-hoc proof of a universal
prompt optimum.

## Comparison boundary

- Dataset and split: Gan 2026 `gan2026_split_v1` locked `test450`.
- Models: the four hosted conditions named above.
- Prompt: exact restored v0.5 model-facing payload for every condition.
- Calls: one structured-events call per note; cache disabled.
- Pipeline, repair policy, scorer, row policy, and aggregate report must be
  frozen before any new test call.
- Provider-required transport, temperature, token limit, and thinking
  differences remain visible in the protocol and result.
- Readout remains aggregate-only: Purist and Pragmatic accuracy, structured
  records, exact evidence, repairs, call failures, parse/schema/label issues,
  timing, usage when available, and sealed-artifact fingerprints.
- No test row may be inspected or used to change the prompt, model, parser,
  repair policy, normalization, or scorer.

## Reuse rule for GPT-4.1-mini

The retained `364/450` GPT-4.1-mini artifact may be reused only if a no-call
reconciliation proves that its model-facing v0.5 payload, pipeline behavior,
repair configuration, scorer, split manifest, and row policy match the new
panel. The reconciliation must record exact source identities or demonstrate a
behavior-preserving replay from the retained artifact.

If any clinically meaningful non-prompt component differs, the old score is a
historical comparator rather than a matched panel row. GPT-4.1-mini must then
run fresh under the same frozen v0.5 condition as the other models. A cheaper
panel is not worth a false comparability claim.

## Required next protocol

Before model calls:

1. Restore v0.5 as an explicitly selectable prompt without changing its
   model-facing content.
2. Render and fingerprint the v0.5 payload.
3. Reconcile the retained GPT-4.1-mini condition against the current runner,
   repair stack, scorer, and split policy.
4. Write a dated, aggregate-only test450 protocol that names whether GPT-4.1-mini
   is retained or rerun.
5. Run model-specific validation pilots only to check transport, schema, and
   exact-evidence operation; pilot accuracy must not tune the prompt.
6. Run each authorized fresh hosted condition once from an empty sealed output
   root and retain the completed aggregate regardless of score.

## Consequences

- The v0.7 panel remains valid evidence for v0.7 and must stay distinguishable
  from the new v0.5 panel.
- No result may be moved between prompt-version tables.
- The historical `364/450` result is no longer described as v0.6.
- v0.6 and v0.7 remain available for diagnostic or explicitly model-specific
  studies, but not as the default shared prompt for this hosted comparison.
- A four-model v0.5 ranking does not become a model-neutral capability ranking:
  provider and repeated-holdout limitations still apply.

Evidence owners:

- [Gan results and holdout rules](../canon/06_gan_clinical_policy.md)
- [Matched v0.7 protocol and result](../experiments/gan2026/gan2026_matched_v07_test450_protocol_2026-07-15.md)
- [Retained evidence manifest](../experiments/retained_evidence_manifest.md)
