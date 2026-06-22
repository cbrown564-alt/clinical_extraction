# LLM Repair Attribution Protocol

Date: 2026-06-22

Scope: ExECTv2 and Gan 2026 LLM-backed extraction runs where deterministic
code runs after a model response. This protocol defines which post-model
actions may be credited as model-preserving normalization and which actions
must remain visible as model errors or hybrid-system behavior.

## Purpose

Recent Qwen diagnostics show that strong headline scores can depend on
deterministic repair. That is acceptable for a deliberately hybrid system, but
it is not acceptable evidence for raw or LLM-first extraction quality.

Future Qwen work may target F1 above `0.900`, but the threshold only counts as
LLM-backed extraction evidence when the score is achieved under the
non-rescuing attribution rules below.

## Core Rule

Deterministic repair may canonicalize a clinical fact the model already
selected. It must not rescue a clinical fact the model missed, choose a missing
clinical state, add ontology companions, or change a clinical category in a way
that affects TP/FN/FP attribution.

If a deterministic action changes the target fact inventory, target state,
clinical category, assertion, negation, certainty, count, period, or final
benchmark label beyond format preservation, the action is prediction-bearing.
Prediction-bearing repair may be reported as hybrid-system behavior, but it
must not be credited as model extraction success.

## Allowed Model-Preserving Repair

These actions may be used in the primary LLM-attributed score when they are
logged with provenance:

- JSON dialect repair and schema parsing that recover the model response
  without changing selected facts.
- Dropping illegal fields that the scoring schema cannot accept, when the field
  is not a target clinical fact.
- Removing unsupported default negatives for unrelated modalities, such as
  `CT_Performed=No` attached to an MRI-only evidence span.
- Canonical spelling and label grammar that preserve the model-selected fact,
  such as `daily` to `1 per day`, plural/singular normalization, or accepted
  unit spelling.
- Dictionary projection for a model-selected finding, such as mapping selected
  `MRI normal` to the benchmark CUI for normal MRI.
- Benchmark-only collapse of non-scored modifiers, such as dropping a fragment
  like `Probable temporal` when it is not a standalone target concept.
- Arithmetic or operand formatting over an already selected fact, such as
  rendering `every 3 to 4 weeks` as `1 per 3 to 4 week`.

These actions still count as deterministic actions in reporting. They are
allowed because they preserve the model's selected clinical fact.

## Disallowed Rescue Repair For LLM-Attributed Scores

These actions must be disabled, ablated out of the primary score, or counted as
model errors when evaluating LLM extraction quality:

- Adding a diagnosis, seizure-frequency state, prescription, or investigation
  that the model did not emit.
- Adding ontology companions or benchmark residual concepts, even when they are
  clinically derivable from the same evidence.
- Choosing an active-rate, seizure-free, unknown, or change-state interpretation
  that the model omitted.
- Filling missing seizure-frequency operands when the model did not select the
  count, period, or state.
- Reclassifying a diagnosis or seizure concept into a different target
  clinical category when that changes scoring.
- Changing certainty, assertion, or negation in a way that affects correctness.
- Dropping a model overcall silently when the overcall is a target clinical
  fact; it may be excluded from the final valid assembly, but it must still be
  counted as a model false positive on the LLM-attributed surface.
- Adding investigation findings, medication regimens, or seizure types from
  source evidence after the model missed them.

These actions may be useful in a hybrid assembly, but the report must label the
result as hybrid or repair-mediated.

## Required Score Surfaces

Every future Qwen run intended to support a model-quality claim must report:

1. `raw_model`: direct parsed model mentions or labels, with no repair beyond
   response capture.
2. `schema_format`: JSON/schema repair and legal-field cleanup only.
3. `model_preserving_canonical`: allowed repairs from this protocol, with no
   fact rescue.
4. `hybrid_full_stack`: all deterministic repairs, including prediction-bearing
   additions or rewrites, reported as a diagnostic companion only.

The promotion-relevant Qwen F1 target is the
`model_preserving_canonical` score. `hybrid_full_stack` may exceed `0.900`, but
that does not satisfy the Qwen LLM-attributed goal.

## Required Transition Accounting

For each run, report counts for:

- parse/schema failures before and after format repair;
- deterministic actions by protocol class;
- model false negatives later rescued by disallowed repair;
- model false positives later dropped by disallowed repair;
- clinical category, assertion, negation, certainty, count, period, and state
  changes;
- raw-wrong to final-correct transitions and raw-correct to final-wrong
  regressions on same raw outputs.

Row-level examples should be included for each disallowed repair family.

## Examples From Current Qwen Review

Allowed with logging:

- Dropping `Probable temporal` as a non-scored diagnosis fragment.
- Removing unsupported `CT_Performed=No` and `EEG_Performed=No` from an MRI
  finding.
- Rewriting `tonic chronic` to `tonic clonic`.
- Mapping selected `MRI normal` and `EEG normal` mentions to benchmark CUIs.
- Converting Gan `daily` to `1 per day`.

Not allowed for LLM-attributed scoring:

- Adding `secondary generalised seizures` when the model missed it.
- Adding `generalised epilepsy` or `generalised tonic clonic seizures` as
  residual benchmark concepts.
- Filling a missing seizure count for `absence like seizures 2014`.
- Adding `focal seizures with altered awareness` from broader focal-epilepsy
  context.
- Adding an abnormal CT finding after the model did not emit it.

## Next Qwen Goal

The next Qwen experiment should iterate prompt/schema/model behavior until the
`model_preserving_canonical` F1 exceeds `0.900` on the declared development
surface. The experiment should improve the model's emitted facts, not add new
deterministic rescue rules.

No-call replays that only add disallowed rescue repair do not count toward this
goal. If the only score above `0.900` is `hybrid_full_stack`, the correct
interpretation is that the hybrid system is strong but Qwen still misses
prediction-bearing facts.
