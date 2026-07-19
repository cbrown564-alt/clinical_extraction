# Gan 2026 six-model validation comparison protocol

Date: 2026-07-18  
Status: predeclared and user-authorized; calls pending

## Primary question

On the permitted Gan 2026 `validation750` development split, how does the
selected single-pass structured-events `llm_with_rules` method compare with a
matched one-call `llm_only` method across the fixed six-model roster, and which
saved model, deterministic-adapter, deterministic-clinical, evidence, and
scoring steps own their row-level differences?

This full-distribution run is justified despite saturated historical validation
because the missing evidence is not another score for one model. The repository
does not have a matched six-model method-by-model panel or inspectable traces
for all twelve conditions. A hard slice cannot establish that each model ran on
the same 750 manifest rows or populate the Example Explorer across the panel.

## Data and inspection policy

- Dataset: Gan 2026.
- Split: `validation`, 750 development rows.
- Manifest: `gan2026_split_v1` at
  `data/Gan (2026)/splits/gan2026_split_v1.json`.
- Manifest SHA-256:
  `5dd39c552bcb60a40f0c79245a9f7346fd27a064cd27263c902e879af3bf7c57`.
- Row policy: `development_row_level`; note, prediction, evidence, gold, and
  changed-row inspection are permitted.
- Gan `test450` is outside this study and must not be opened or used.

Every completed artifact must contain exactly the manifest's 750 validation
`source_row_index` values once each. The earlier cancelled Qwen v0.7 partial
artifact at 367/750 and the separate Qwen v0.5 validation queue are excluded and
must not be resumed into this comparison.

## Candidate, comparator, and control

### Selected `llm_with_rules` candidate

- Pipeline: `llm_with_rules` / retained ID `hybrid_structured_events`.
- Prompt: `gan2026_hybrid_structured_events_v0.7`.
- One primary structured-event call per note. The retained local transport may
  make a format-only retry only after an eligible malformed-output failure; the
  initial and retry outputs and acceptance event must remain separate.
- Deterministic policy: current `hybrid_full_stack`, including selected-evidence
  repair and the named seizure-frequency repair families.
- The method is LLM with rules. Any deterministic step that changes a selected
  event, state, label kind, count, denominator, time window, cluster meaning, or
  sentinel owns that clinical change.

### Matched `llm_only` comparator

- Pipeline: `llm` / retained ID `llm_only_canonical_pipeline`.
- Prompt: `gan2026_llm_only_canonical_pipeline_v0.8`.
- One model call per note; the model selects the evidence and produces the
  directly rendered final label.
- The frozen model prediction boundary is the schema-valid
  `CanonicalLlmDecisionRecord` before `repair_prediction_label_with_evidence`.
  The saved trace must retain that record, any JSON/schema repair, the
  deterministic selected-evidence/benchmark adapter transition, evidence
  containment, the scored record, and both score views separately.
- No independent deterministic candidate extractor, temporal selector,
  clinical fallback, or event union may enter this condition.

### Fixed rules comparison

The existing deterministic canonical validation750 artifact is the no-call
control. It is not rerun per model. The twelve fresh conditions must retain the
same source-row identity so a later no-call comparison can align them with that
single model-independent control.

## Fixed model conditions

| Model | Route | Temperature | Maximum completion tokens |
| --- | --- | ---: | ---: |
| GPT-4.1-mini | `openai/gpt-4.1-mini`, hosted chat | 0 | 10,000 |
| GPT-5.6 Luna | `openai/gpt-5.6-luna`, hosted chat | 1 | 10,000 |
| GPT-5.6 Sol | `openai/gpt-5.6-sol`, Responses | omitted by adapter | 10,000 |
| DeepSeek V4 Flash, thinking enabled | `deepseek/deepseek-v4-flash`, official hosted route | 0 | 32,000 |
| Qwen 3.6:35B | `ollama_chat/qwen3.6:35b`, native Ollama, `think=false` | 0 | 16,000 |
| Gemma 4 26B | `ollama_chat/gemma4:26b`, native Ollama, `think=false` | 0 | 16,000 |

DSPy/LiteLLM cache is disabled for every fresh pilot and full run. Provider
transport, supported temperature, output ceiling, and local hardware differ by
condition and remain disclosed; no result is a model-neutral capability rank.

Configuration owner:
`configs/gan2026/six_model_validation_comparison_20260718.json`.

## Pilot and execution rule

Run a fresh five-row validation transport/schema pilot for each model-method
pair before its full condition. The pilot must have five completed calls, five
schema-valid model prediction records, five score records, zero call failures,
and five valid `gan2026.row_trace.v1` records. Pilot accuracy is not a gate and
must not change prompts, clinical rules, normalization, labels, or scorers.

After a passing pilot, run all 750 rows once with cache disabled. An interrupted
condition may resume only its own checkpoint after verifying unique manifest
row identity and unchanged configuration. Do not merge another prompt version,
model route, method, or earlier partial artifact.

The local controller waits for the already-authorized v0.5 local holdout/Qwen
queue to finish before using Ollama. Hosted OpenAI conditions run sequentially;
the independent hosted DeepSeek condition may run in parallel.

## Row artifact and Example Explorer contract

Each JSONL row is the machine-readable evidence unit. It must preserve:

- source row identity, split, and manifest;
- rendered prompt and prompt version;
- initial raw model output and any separate format-retry output;
- the schema-valid model prediction before deterministic clinical or benchmark
  adaptation;
- format/schema repair events;
- structured events, normalized events, selected event IDs, selected clinical
  kind, selected evidence, and model label where applicable;
- deterministic selection, benchmark-adapter, and semantic repair transitions
  as separate stages, with before/after labels and rule category;
- final scored record, exact evidence/substring status, Purist and Pragmatic
  projections, gold reference, call failures, parse/schema failures, and retry
  events; and
- `row_trace.schema_version = gan2026.row_trace.v1`, method, and stable field
  references needed by the Gan Example Explorer adapter.

The row trace is instrumentation only. It must not change prompts, model calls,
repairs, labels, or scores. Raw provider text remains untrusted display content.

Planned root:
`scratch/validation/gan2026_six_model_comparison_20260718/{model}/{method}/`.
Each condition retains a five-row pilot, a 750-row JSONL, a Markdown run report,
and an operational log. A later no-call builder may create content-addressed
Explorer projections; it must not replace these source artifacts.

## Metrics and required analysis

Primary: Gan Purist correct count and accuracy over all 750 rows. Secondary:
Pragmatic count and accuracy, schema-valid records, exact selected evidence,
call failures, parse/schema failures, format retries, format repair, semantic
repair, and measured wall-clock timing.

After all twelve runs complete, align rows by model and `source_row_index` and
produce a no-call changed-row comparison containing:

- `llm_only` wrong to `llm_with_rules` correct;
- `llm_only` correct to `llm_with_rules` wrong;
- unchanged-correct and unchanged-wrong counts;
- model-boundary to final-transition counts within each method;
- changed-row exact-evidence accounting;
- deterministic-correct regressions against the fixed rules control; and
- repair, failure, and first-failure-owner breakdowns that the saved trace can
  support without inventing missing ownership.

Aggregate scores alone do not answer the component question. Representative
permitted rows and named hard families may be inspected only after the frozen
twelve-condition artifacts exist; any prompt or rule change begins a new
candidate and does not alter this panel.

## Frozen source identities

The run starts from commit `b9ccd1082c70746c12df60b77cb0cdcd20c62369` plus
the disclosed dirty working tree. The relevant pre-run files are:

| Role | Path | SHA-256 |
| --- | --- | --- |
| Structured-events v0.7 payload | `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events.txt` | `75c2c8f06c752b02223afff80b5d8af5fcba2fcf2d6c3b6f079be24a7f1d09d8` |
| LLM-only v0.8 payload | `tests/snapshots/prompt_contracts/gan2026__llm_only_canonical_pipeline.txt` | `0c42c6722eee9b47f71414a5d4554c0b2156d894b7a4285a94de301cb17e1efd` |
| Structured-events runner and trace instrumentation | `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py` | `bd3cec4ac87c8aae351329e0d00f1951108183855bcf9c5b28a0b1077137be25` |
| LLM-only runner and trace instrumentation | `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_canonical_pipeline.py` | `5593889c5c029d15941759c9e476421d4e38c2d9adaaf3a072aaa03ee79e2acf` |
| Normalization and selected-evidence repair | `src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py` | `f3a11e3480c001b8972bb8f70ddcb674a567418491a61ad983aae50f47c83c4c` |
| Gan category mapping | `src/clinical_extraction/tasks/seizure_frequency/gan2026/labels.py` | `6c1635541403c3cf419595a7883ec8055335facf88af8a62cc175465afb224ba` |
| Gan scorer | `src/clinical_extraction/tasks/seizure_frequency/gan2026/evaluate.py` | `18fdec285a5a80aa92d06bdb6e75f6b6e619d76dfeb1ca5eec0751fe7123c402` |
| Hosted transport wrapper | `scripts/run_gan2026_hosted_condition.py` | `56d88e7e9a5cc4c8ea7bdaed2096b7e837cfcc2c032cad854432f423f3ccb0f8` |
| Comparison controller | `scripts/run_gan2026_six_model_validation_comparison.ps1` | `c57b79a67b61a4aee897cf45efa030f4b0e42768e82e1721e1fb931117fbd32a` |
| Machine configuration | `configs/gan2026/six_model_validation_comparison_20260718.json` | `0231b0eae4c2d8ad3b6231fb9dec237d0a31238c2992b6f178088e16fd81b513` |

If a pilot exposes a transport-only defect, stop before the full condition,
amend this protocol and the hashes, and repeat the pilot. A prompt, clinical
repair, label, scorer, or prediction-boundary change rejects the frozen panel
and requires a new dated protocol.

## Stop rule and claim boundary

Retain every full 750-row condition regardless of score. A complete condition
may contain visible model call or parse failures; those are results, not a
license to retry clinically undesirable output. Stop a condition on controller
failure, missing/duplicate manifest rows, missing trace schema, or a failed
pilot. Preserve partial checkpoints and report the condition incomplete.

This study can provide development component evidence for the named Gan split,
six routes, two prompts, current repair policies, and Purist/Pragmatic scorers.
It is not holdout evidence, clinical validation, broad generalization, a pooled
model ranking, or proof that one method family is universally better. Promotion
requires the declared component analysis, evidence validity, deterministic
regression accounting, and an independently governed holdout decision.
