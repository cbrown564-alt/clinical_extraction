# 0043: Use prompt v0.5 for the hosted Gan model comparison

Date: 2026-07-16
Status: accepted and implemented for the six-model test450 panel; six-model
dev750 coverage pending

## Decision

The primary Gan `llm_with_rules` comparison uses
`gan2026_hybrid_structured_events_v0.5` for every model: GPT-4.1-mini,
GPT-5.6 Luna, GPT-5.6 Sol, DeepSeek V4 Flash, Qwen 3.6:35B, and Gemma 4 26B.

Prompt v0.5 is the only prompt version selected for primary six-model
`llm_with_rules` results in comparison reports, paper claims, reliability
scorecards, and retained-evidence summaries. The complete v0.5 test450 panel is
the selected aggregate panel. A matched six-model v0.5 dev750 panel remains
required.

The completed v0.7 panel remains frozen evidence for that exact prompt and is
not deleted or relabelled. It is quarantined from primary results.

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
- Models: the six hosted and local conditions named above.
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

## Completed test protocol

The required prompt restoration, fingerprinting, reconciliation, frozen
protocols, pilots, and six test450 conditions are complete. The selected
aggregate owner is
`experiments/gan2026_matched_v05_test450_aggregate_20260716.json`.

## Required development coverage

The next Gan six-model development comparison must run the same v0.5 prompt,
event-ledger schema, `hybrid_full_stack` repair policy, split manifest, and
scorers on all 750 development rows for every model. Historical or partial
artifacts may be used only when a no-call reconciliation establishes the same
prompt payload and replays the saved raw output through the selected current
non-prompt stack.

Until that panel is complete:

- do not substitute v0.7 dev750 results into a v0.5 comparison;
- do not publish a six-model `llm_with_rules` dev750 ranking;
- keep the existing complete v0.7 development panel diagnostic and historical;
- report the missing v0.5 dev750 coverage explicitly.

## Consequences

- The v0.7 panel remains valid evidence for v0.7 and must stay distinguishable
  from the v0.5 panel.
- v0.7 must not supply a primary score, model ranking, reliability cell,
  cross-task headline, paper table, or development-to-test comparison.
- A short historical note may state that v0.7 improved Qwen relative to v0.5
  while reducing the other five models' test450 Purist scores. This is an
  aggregate prompt-interaction diagnostic, not a recommended prompt or a
  row-level mechanism claim.
- No result may be moved between prompt-version tables.
- The historical `364/450` result is no longer described as v0.6.
- v0.6 and v0.7 remain available for diagnostic or explicitly model-specific
  studies, but not as the default shared prompt for this hosted comparison.
- A six-model v0.5 ranking does not become a model-neutral capability ranking:
  provider and repeated-holdout limitations still apply.

Evidence owners:

- [Gan results and holdout rules](../canon/06_gan_clinical_policy.md)
- [Matched v0.5 hosted protocol](../experiments/gan2026/gan2026_matched_v05_test450_protocol_2026-07-16.md)
- [Matched v0.5 local extension](../experiments/gan2026/gan2026_matched_v05_local_test450_and_qwen_val750_protocol_2026-07-18.md)
- [Retained evidence manifest](../experiments/retained_evidence_manifest.md)
