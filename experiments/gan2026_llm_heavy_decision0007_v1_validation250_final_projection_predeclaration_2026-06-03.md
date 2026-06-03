# Gan 2026 Decision 0007 v1 Validation250 Final-Projection Predeclaration

- Date: 2026-06-03
- Candidate: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Prompt/program version: `gan2026_llm_heavy_evidence_selection_deterministic_adapters_v1`
- Typed output schema version: `selected_fact_operands_v1`
- Split: first 250 `validation` rows under `gan2026_split_v1`
- Model: `openai/gpt-4.1-mini`
- Planned mode: live validation250, followed by same-raw-output no-call replay
- Primary LLM-heavy score layer: `benchmark_convention_adapter`
- Audited hybrid/projection score layer: `final_projected_label`
- Claim language: validation development artifact only; not a benchmark result,
  not a holdout result, and not an LLM-first threshold claim.

## Decision

Predeclare Decision 0007 validation250, but do not promote
`final_projected_label` as the primary LLM-heavy score layer.

The validation250 run is allowed only as a targeted attribution and
projection-family stress test. `final_projected_label` must be reported as a
named deterministic projection layer over model-selected labels, operands, and
selected evidence. If it changes semantic kind, denominator/window policy,
current-versus-historical precedence, vague/exact category, or benchmark-row
family behavior, the row counts as deterministic semantic projection rather
than format-only repair.

## Rationale

The validation50 final-projected replay reached 50/50 Purist and 50/50
Pragmatic from the same saved GPT-4.1 mini outputs, with 50/50 structured typed
outputs, 49/50 exact selected evidence, 49/50 selected operand completeness, and
0 selected fact trace mismatches. The gain over the mechanical/benchmark
adapter layer came from six raw/mechanical-wrong to final-correct changes and
zero final-projection regressions on the prefix.

That prefix is saturated and too small to support promotion by aggregate score.
The useful validation250 question is narrower: whether the same projection
families remain high-precision when applied to a larger development slice, and
whether they mostly render from an LLM-owned clinical selection or quietly become
the prediction-bearing interpreter.

## Frozen Inputs

Before running validation250, freeze and record:

- repo commit hash and dirty-worktree note;
- split manifest path and hash for `gan2026_split_v1`;
- candidate module path and prompt/program version;
- model id, temperature, max tokens, API base, DSPy cache setting, and run mode;
- scorer/mapping policy and prediction-repair policy;
- projection-family implementation and family names listed below;
- output paths for live JSONL, no-call replay JSONL, Markdown report, and any
  live-call log.

No prompt, schema, scorer, normalization, adapter, or projection-family change
may be made after the live run and before the no-call replay. Any change cancels
this predeclaration and requires a new one.

## Score Layers To Report

Report all layers on the same 250 rows:

- `raw_model_parser_label`
- `raw_model_clinical_selection`
- `format_only_repair`
- `mechanical_adapter_label`
- `benchmark_convention_adapter`
- `final_projected_label`

For each layer, report scorable count, Purist, Pragmatic, exact normalized-label
matches when available, and rows changed from the previous layer.

## Final-Projection Families

The validation250 artifact must record counts, row ids, labels before/after,
and transition type for each family:

- `clean_scorer_facing_policy`: no additional semantic projection beyond the
  scorer-facing adapter.
- `raw_label_fallback`: preserve a scorable raw model label when mechanical
  operands are incomplete.
- `selected_evidence_bimonthly_policy`: map selected evidence using Gan's
  bimonthly convention, expected as `1 per 2 month`.
- `selected_evidence_current_monthly_precedence`: prefer an explicitly current
  monthly state over a historical or year-to-date count inside the selected
  evidence.
- `selected_evidence_every_other_interval`: render selected evidence such as
  `every other day` as an interval label.
- `selected_evidence_upper_bound_policy`: preserve scorer-facing numeric upper
  bounds such as `<= four per day` when the selected fact supports that reading.
- `selected_evidence_vague_weekday_policy`: keep vague weekday evidence such as
  `most weekdays` in Gan's vague-frequency category when the gold convention
  expects broad `multiple per week` behavior.
- `new_or_uncategorized_projection`: any row changed by logic not listed above.
  Presence of this family is a stop-rule failure unless the row remains
  diagnostic-only and is excluded from promotion language.

## Transition Counts

The report must include:

- rows changed by each layer;
- raw-wrong to final-correct;
- raw-correct to final-wrong;
- mechanical-wrong to final-correct;
- mechanical-correct to final-wrong;
- Purist category changes;
- Pragmatic category changes;
- semantic-kind changes;
- normalized-label exact changes;
- selected evidence exactness failures;
- selected fact trace mismatches;
- selected operand incompleteness;
- adapter parse failures and call/schema failures.

## Inspection Policy

Inspect only validation rows. Do not inspect train or locked-test rows.

Required row-level inspection:

- every `final_projected_label` row whose label differs from
  `benchmark_convention_adapter`;
- every raw-correct to final-wrong or mechanical-correct to final-wrong row;
- every row in `new_or_uncategorized_projection`;
- every selected-evidence exactness failure;
- every selected fact trace mismatch;
- every selected operand incompleteness row;
- every call, schema, parse, or scorable-label failure.

Optional inspection may sample unchanged correct rows for trace sanity, but it
must not be used to introduce a new projection family after the run.

## Promotion Criteria

Promote Decision 0007 v1 to the next development decision only if all are true:

- structured typed outputs are at least 248/250;
- call failures are 0/250;
- adapter parse failures are no more than 2/250;
- selected evidence exactness is at least 245/250 after source-checked
  nonsemantic evidence-copy repair;
- selected fact trace mismatches are 0/250;
- selected operand completeness is at least 245/250;
- `benchmark_convention_adapter` Purist is at least 220/250 and has no more than
  2 raw-correct to adapter-wrong regressions;
- `final_projected_label` Purist is at least 235/250;
- `final_projected_label` mechanical-correct to final-wrong regressions are no
  more than 1/250;
- at least 80% of final-projection corrections are attributable to the
  predeclared projection families, not `new_or_uncategorized_projection`;
- evidence/source trace remains sufficient to explain every projected change.

Promotion language must be one of:

- "LLM-heavy clinical selection with deterministic adapters" for the
  `benchmark_convention_adapter` layer;
- "hybrid LLM-selected plus deterministic final-projection development result"
  for the `final_projected_label` layer.

Do not claim that `final_projected_label` is an LLM-first or pure LLM-heavy
threshold result.

## Revise Or Reject Criteria

Mark the result revise-only or rejected if any occur:

- schema, call, parse, evidence, trace, or operand failures form a systemic
  family;
- projection introduces more than 1 mechanical-correct to final-wrong
  regression;
- `new_or_uncategorized_projection` is needed to make the aggregate look
  successful;
- the final-projection gains mostly come from deterministic clinical selection
  that the model did not expose in selected evidence or typed operands;
- row-level inspection suggests a projection family is Gan-template-specific
  without a named research-only caveat;
- claim language would need to hide deterministic semantic projection.

If rejected, do not patch the validation250 result in place. Write an error
analysis and return to a smaller validation or hard-slice design.

## Expected Learning Value

This run should decide whether Decision 0007 v1 is:

- a healthy LLM-heavy clinical-selection architecture with deterministic
  adapters but limited final-label performance;
- a useful hybrid architecture whose deterministic projection layer is explicit,
  high-precision, and ablatable;
- or a saturated-prefix artifact that needs hard-slice/component-stress work
  instead of broader aggregate validation.

The result should also provide a paper-facing attribution table separating raw
model labels, format-only repair, mechanical adapters, benchmark conventions,
and deterministic semantic projection.
