# 0006: Gate LLM-Heavy V2 On LLM-Owned Selected-Evidence Rendering

Date: 2026-06-02

## Decision

Before starting broad `llm_heavy_clinical_frequency_reasoner_v2` prompt work,
run a validation25 smoke whose only promotion question is whether the model can
own selected-evidence arithmetic and final-label rendering.

The model must emit:

- the parser-ready final Gan label it wants scored;
- the selected source evidence for that label;
- structured operands sufficient to audit the arithmetic or interval rendering;
- a short trace linking the selected event to the final label.

Deterministic code may validate schema, evidence exactness, parser
compatibility, and arithmetic consistency. It must not silently replace the
model's selected label with deterministic selected-evidence arithmetic during
the LLM-heavy score layer. Any deterministic correction remains a named
side-car condition, not the promoted v2 result.

## Context

The saved-output replacement replay over LLM-heavy v1 validation250 showed that
raw and format-only model labels stayed at 188/250 Purist, while deterministic
selected-evidence arithmetic reached 219/250 Purist. That improvement is useful
diagnostic evidence, but it is prediction-bearing post-processing rather than
LLM-owned final-label reasoning.

Decision 0005 keeps arbitrary benchmark-format conventions separate from
clinical reasoning. This decision narrows the next LLM-heavy smoke to the less
arbitrary target first: can the model render the frequency implied by its own
selected evidence without deterministic semantic replacement?

## Validation25 Experiment Unit

- Pipeline: `llm_heavy_clinical_frequency_reasoner_v2`.
- Surface: first 25 rows of Gan 2026 `validation` under `gan2026_split_v1`.
- Model: use the same hosted model family as v1 unless a separate model-choice
  decision is recorded.
- Comparator: rejected v1 validation25 and validation250 attribution layers,
  especially raw/format-only versus selected-evidence arithmetic.
- Primary score: raw model-owned Purist F1 on parser-ready labels.
- Side-car scores: Pragmatic F1, format-only repair, deterministic
  selected-evidence arithmetic, and benchmark-aligned adapter.
- Inspection policy: validation row-level review is allowed for the 25-row smoke;
  no train or locked-test rows are inspected.

## Stop Rule

Promote the replacement path to validation50 only if all of these hold:

- 25/25 hosted calls return structured output with no systemic schema family.
- At least 24/25 raw model labels are parser-compatible before semantic repair.
- At least 23/25 selected evidence spans are exact and source-near.
- Selected-event trace mismatches are 0/25.
- Raw model-owned Purist is at least 20/25, or row review shows that every raw
  miss is a predeclared benchmark-format convention rather than failed
  arithmetic/rendering.
- Deterministic selected-evidence arithmetic improves no more than five rows
  over the raw model-owned label; a larger gap means the replacement failed.
- Any raw-correct to side-car-wrong regression is explained before escalation.

Reject or redesign before validation50 if any of these hold:

- the model needs deterministic arithmetic replacement to clear the target;
- selected evidence is non-exact on more than two rows;
- trace mismatches recur;
- prompt instructions overload simple rows by turning direct daily, weekly, or
  monthly frequencies into more complex labels;
- schema enum drift or parser grammar drift creates a recurring failure family.

## Required Artifact

The validation25 report must include:

- raw model-owned, format-only, selected-evidence-arithmetic, benchmark-aligned,
  and full-stack score layers;
- selected-evidence exactness and selected-event trace mismatch counts;
- row-level labels for raw misses, side-car corrections, and side-car
  regressions;
- a small failure taxonomy separating wrong selected fact, wrong arithmetic,
  wrong rendering, parser/schema issue, and benchmark-format convention;
- explicit claim language stating whether the result is `promote_to_50`,
  `revise`, or `reject`.

## Consequences

Do not use the validation250 selected-evidence arithmetic score as a reason to
call v1 or v2 LLM-heavy successful. That layer remains a deterministic
replacement target until the raw model-owned label carries the same decision.

If the validation25 smoke passes, v2 may proceed to validation50 under the split
ladder. If it fails, the next task is a smaller prompt/schema redesign or a
decision to keep selected-evidence arithmetic as an explicit deterministic
component in a hybrid architecture.
