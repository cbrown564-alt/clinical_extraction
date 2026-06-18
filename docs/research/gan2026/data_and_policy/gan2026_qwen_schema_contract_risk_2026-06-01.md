# Gan 2026 Qwen Schema-Contract Risk Note

Date: 2026-06-01

This is a development-split schema-contract note. It is not a benchmark result,
and it should not be read as a Qwen quality claim. The purpose is to record a
local-model output-contract failure observed during the first Qwen 3.6/Ollama
setup smoke.

## Executive Summary

The corrected native Ollama route worked: `ollama_chat/qwen3.6:35b` at
`http://localhost:11434` with `think=false` returned nonempty content and had no
call failure on the validation1 smoke. The failure was downstream schema
adherence.

Qwen understood the main clinical fact in the row, but it did not obey the
strict output contract. It returned a Python-style single-quoted object, made
`final_query` a natural-language question, and put the structured decision in a
separate `final_selector` object. The parser therefore could not create a
`SectionClaimTableExtractionRecord`, and the row had no scorable final label.

This is likely to recur as schemas become more complex unless Qwen-specific
prompting, constrained decoding, or explicitly named repair ablations are added.

## What We Asked For

The v5 claim-table selector prompt asks the model to:

1. Read the clinical note.
2. Produce a flat `claims` table of source-near seizure-frequency claims.
3. Run a constrained final selector over those claims.
4. Return exactly one strict JSON object with two top-level fields:
   `claims` and `final_query`.

The required `final_query` object must contain structured fields such as:

- `selected_claim_ids`
- `selector_decision`
- `answer_kind`
- `cluster_axis`
- `boundary_state`
- `raw_selected_frequency`
- `final_label`
- `conversion_note`
- `evidence`
- `confidence`
- `rationale`

The parser uses Pydantic models with `extra="forbid"`, so extra fields and
incorrect object shapes are contract failures rather than soft warnings.

## What Qwen Actually Returned

On validation row `10`, the note stated:

```text
On the accommodation logs, the observed frequency is noted as ≤ four per day,
with variable clustering, often in the late afternoon or evening.
```

Qwen returned two reasonable claim rows:

- `c1`: a frequency claim with raw frequency `≤ four per day`.
- `c2`: a cluster-frequency claim for `variable clustering`.

The model then selected `c1` as the best final evidence. Semantically, this was
close to the expected answer family: the gold label is `4 per day`.

However, the raw output shape was:

```text
{'claims': [...],
 'final_query': "What is the patient's current seizure frequency?",
 'final_selector': {
   'claim_ids': ['c1'],
   'final_label': '≤ four per day',
   'reasoning': 'Claim c1 provides the most specific current frequency bound...'
 }}
```

This violates the contract in three important ways.

## Why It Failed

First, the output was not valid JSON. It used single quotes around object keys
and string values. The parser failed at JSON loading with:

```text
invalid_json: Expecting property name enclosed in double quotes
```

Second, `final_query` had the wrong type. The schema requires `final_query` to
be an object containing the structured final answer. Qwen made it a string:

```text
"What is the patient's current seizure frequency?"
```

Third, Qwen invented a sibling object called `final_selector`. This object held
some of the information we wanted, but with different field names:

- `claim_ids` instead of `selected_claim_ids`
- `reasoning` instead of `rationale`
- no `answer_kind`
- no `selector_decision`
- no `cluster_axis`
- no `boundary_state`
- no final exact evidence field
- no `confidence`

Because the parser failed before Pydantic validation, the row never reached the
strict schema-repair layer. Even if quote repair were added, the `final_selector`
alias would need an explicitly named repair policy before it could become a
valid extraction.

## Interpretation

This was not the earlier endpoint failure mode. The bad OpenAI-compatible route
can produce hidden reasoning and empty final assistant content. Here, native
Ollama chat produced nonempty content with thinking disabled. The model simply
did not respect the complex schema.

The useful signal is that Qwen followed the clinical intent better than it
followed the interface contract. That is a different risk from clinical
reasoning failure. For local Qwen experiments, schema adherence should be
measured as a first-class component before quality metrics.

## Expected Risk For Complex Schemas

The v5 schema combines several burdens:

- strict JSON syntax;
- nested object shape;
- enumerated fields;
- source-near claim rows;
- a constrained selector state;
- exact evidence substring requirements;
- Gan-compatible final-label grammar;
- cluster-axis and boundary-state preservation.

Hosted GPT-4.1 mini can still fail these contracts, but the Qwen validation1
smoke suggests local Qwen may be more likely to preserve the conceptual task
while drifting into a locally natural schema. Future Qwen runs should therefore
assume output-contract failures are probable until measured otherwise.

## Required Before Qwen Ladder Runs

Do not run Qwen validation5, validation25, or broader ladders until validation1
passes with one of these named conditions:

1. `qwen_v5_prompt_strict_json`: prompt hardening only, no parser expansion.
2. `qwen_v5_schema_repair_alias_only`: explicitly named repair for JSON/Python
   literal shape and non-semantic selector aliases.
3. `qwen_v5_simplified_schema`: reduced nested schema for Qwen, with a written
   comparison to the full v5 schema.

Any repair condition must report raw output-contract failures separately from
repaired structured records. It must not allow a repaired Qwen run to be
described as clean raw model adherence.

## Suggested Diagnostics

For each future Qwen smoke, report:

- call failures;
- empty assistant-content failures;
- invalid JSON failures;
- top-level shape failures;
- `final_query` type failures;
- invented-field failures;
- enum alias repairs;
- exact evidence substring validity;
- raw versus repaired final-label scorable counts.

This lets the project separate local serving issues, schema-interface issues,
and true clinical-selection errors.

## Claim Language

Use language like:

> Native Ollama chat with Qwen 3.6 produced nonempty output with thinking
> disabled, but the validation1 v5 smoke failed strict schema adherence.

Avoid language like:

> Qwen failed the seizure-frequency task.

The observed failure is narrower and more useful: Qwen likely needs a simpler
or more strongly constrained schema interface before its clinical extraction
quality can be judged.
