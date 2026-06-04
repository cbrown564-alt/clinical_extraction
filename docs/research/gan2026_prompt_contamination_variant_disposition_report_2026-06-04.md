# Gan 2026 Prompt Contamination Variant Disposition Report

Date: 2026-06-04

Status: research disposition and replacement plan. This report does not change
scores, authorize holdout work, or make benchmark-comparable claims.

## Executive Summary

The prompt-language audit found that several LLM variants exposed internal
experiment language, parser vocabulary, metadata, or overgrown instructions in
model-facing payloads. This weakens their value as evidence for a clean
architecture, but it does not make the artifacts useless.

Recommendation:

1. Keep existing prompt-contaminated variants as historical experimental
   conditions.
2. Do not retroactively replace or delete their runs.
3. Demote their interpretation: they are evidence about a specific prompt
   condition, not evidence that the underlying architecture is cleanly good or
   bad.
4. Build new clean successor variants only for roles that still answer an active
   research question.
5. Promote a clean successor only after it passes the validation ladder with
   clean rendered-payload checks, schema validity, exact-evidence review, and
   interpretable failures.

The practical implication is that prompt cleanup should create a small number
of clean successors, not a broad rerun of every historical branch.

## Why Prompt Contamination Matters

The core research thesis requires attribution discipline: if an LLM-only variant
claims the model selected the prediction-bearing clinical state, the prompt
must not blur that task with internal run metadata, scoring policy, parser
implementation language, or experiment-family labels.

The audit found recurring problems:

- metadata such as `prompt_version` and `pipeline_family` inside model-facing
  payloads;
- internal vocabulary such as `source-near`, `operands`, `denominator`,
  `proxy`, `component`, and `benchmark`;
- instructions that tell the model about the experiment rather than the
  clinical task;
- schema field lists without enough plain descriptions for non-obvious fields;
- historical prompts that accumulated narrow prohibitions until the tested task
  was no longer easy to interpret.

These issues can distract the model and make negative results ambiguous. A bad
result may reflect the architecture, the model, the schema, or simply a polluted
prompt. A good result may reflect overfitted prompt policy rather than a robust
clinical extraction role.

## What Not To Do

Do not delete old variants. They are still useful as historical comparators and
as evidence about what happened under their exact prompt conditions.

Do not silently relabel old variants as clean. Their reports and future
summaries should identify them as historical prompt conditions when prompt
contamination was material.

Do not rerun every old variant just because its prompt was messy. Broad reruns
would spend validation budget without answering a focused component question.

Do not use prompt cleanup alone as a promotion argument. A cleaned prompt must
still pass evidence, schema, attribution, and split-discipline gates.

## Variant Disposition

| Variant family | Recommended status | Reason |
| --- | --- | --- |
| `llm_only_minimal_evidence_selector` | Cleaned baseline; eligible for new validation-prefix use after guardrails | Its role is narrow and minimal, so cleanup directly supports an interpretable evidence-selection baseline. |
| Selected-state variants: `llm_only_simplified_selected_state_reasoner`, `llm_only_sparse_operands_selected_state_reasoner`, `llm_only_typed_adapter_reasoner`, `llm_only_typed_operations_reasoner` | Historical comparators plus source material for one clean successor | The family tests an important role, but four parallel variants are too many to carry forward after prompt cleanup. |
| `llm_only_claim_table_selector` | Historical controlled prompt condition | It is intentionally instruction-heavy and useful as a transparency/complementarity comparator, but not as the default clean prompt style. |
| `llm_heavy_clinical_frequency_reasoner` and adapter-heavy LLM variants | Historical controlled prompt conditions unless a specific hypothesis justifies a successor | These prompts test broad LLM ownership and schema rendering, but contamination plus complexity makes immediate reruns low-information. |
| Hybrid adjudicator variants | Historical or controlled hybrid conditions | They ask the model to reason over candidate/provenance structures. That can be valid, but only if the prompt explicitly tests adjudication over internal candidates. |
| Single-task control prompts | Current clean style reference | They separate model-facing task text from research metadata and should guide future replacements. |

## Proposed Clean Successors

### 1. Minimal Evidence Selector

Keep the cleaned minimal evidence selector as the narrow evidence-selection
baseline. It should answer:

> Can a model select exact supporting evidence and a close clinical answer
> without being asked to solve full benchmark rendering?

Use it for evidence quality, ambiguity preservation, and downstream projection
diagnostics. Do not treat its final F1 as the main result.

### 2. Clean Selected-State V1

Build one clean selected-state successor instead of maintaining four equal
selected-state variants.

Recommended shape:

- one clinical note in;
- one selected seizure-frequency state out;
- exact selected evidence;
- short copied source phrase;
- seizure-frequency answer;
- optional typed numeric details with plain descriptions;
- no run metadata in model-facing inputs;
- no model-facing `source-near`, `operands`, `proxy`, `denominator`,
  `benchmark`, `component`, `prompt_version`, `pipeline_family`, or `Gan 2026`;
- parser-facing field names allowed only when descriptions make them clear.

This successor should preserve the useful selected-state idea while removing
unnecessary competition among simplified, sparse, adapter, and operation-heavy
branches.

### 3. Clean Typed-Operations Successor Only If Needed

Create a separate clean typed-operations successor only if the next research
question specifically needs explicit arithmetic/state components.

The hypothesis would be:

> Does typed extraction of count, timeframe, unit, seizure-free duration, and
> cluster details improve projection auditability or fixed-bundle rendering
> compared with a simpler selected-state output?

Without that hypothesis, typed operations should remain a diagnostic branch, not
the next default model path.

## Validation Plan

Use the locked Gan 2026 validation ladder. No test-set use is authorized by this
report.

### Smoke: Validation25

Run each clean successor only after rendered-payload hygiene passes.

Required gates:

- no audited jargon or metadata leaks in rendered model-facing payloads;
- no gold/reference labels in model-facing inputs;
- schema-valid outputs on all or nearly all rows;
- exact selected evidence is inspectable;
- row-level failures are interpretable.

### Early Signal: Validation50

Escalate only if validation25 has no systemic schema, prompt, or evidence
failure.

Required comparison:

- clean successor versus the historical variant it replaces;
- raw and format-only layers separated from deterministic repair/projection;
- exact-evidence rate reported separately from score;
- failure modes classified by clinical subproblem, not only final label.

### Decision Gate Before Validation250

Move to validation250 only if the clean successor answers a durable decision:

- promote clean selected-state v1;
- reject it and keep minimal evidence controls;
- split typed operations into a separate diagnostic successor;
- or design hard-slice panels for a specific failure family.

Aggregate F1 alone is not a sufficient reason to escalate.

## Claim-Language Policy

Use this language for older variants:

> Historical prompt condition. A 2026-06-04 prompt-language audit found
> model-facing internal metadata or jargon leakage, so this result should not be
> treated as clean evidence for the architecture without a cleaned rerun.

Use this language for cleaned successors:

> Clean rendered-payload condition. Prompt metadata is separated from
> model-facing task text; non-obvious schema fields have descriptions; audited
> jargon terms are absent from model-facing instructions.

Use this language for any validation result:

> Validation-development result under `gan2026_split_v1`; not a
> benchmark-comparable or holdout claim.

## Decision

The project should not replace existing variants wholesale. It should preserve
them as historical comparators, mark their prompt-contamination risk, and create
a small set of clean successors where the role still matters.

Immediate next implementation target:

1. keep the cleaned minimal evidence selector as the current minimal baseline;
2. design one `llm_only_clean_selected_state_v1` successor;
3. run rendered-payload tests before any live calls;
4. evaluate through validation25 then validation50 before considering any
   validation250 run.

This protects the research thesis better than either ignoring prompt
contamination or rerunning every historical prompt branch.

## References

- `docs/research/gan2026_prompt_language_audit_2026-06-04.md`
- `docs/research/contribution_thesis.md`
- `docs/design/architecture.md`
- `docs/design/gan2026_split_protocol.md`
- `PROJECT_STATUS.md`
