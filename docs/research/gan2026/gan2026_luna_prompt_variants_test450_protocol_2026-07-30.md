# Gan 2026 Luna prompt-variant A/B/C test450 protocol

Date: 2026-07-30  
Status: complete; aggregate-only A/B/C test450 panel finalized 2026-07-30  
Readout: aggregate-only  
Parent development panel:
[validation750 A/B/C](gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md)

## Primary question

For GPT-5.6 Luna alone on Gan `test450`, how do the frozen v0.5 control prompt
and the two Luna development prompts compare on LLM-only and LLM-with-rules
Purist accuracy when the schema, repair stack, scorers, and split stay fixed?

This is a Luna-versus-Luna holdout transfer check for prompts selected on
development data. It is not a six-model ranking and does not rewrite the frozen
v0.5 six-model panel.

## Data, split, and row policy

- Dataset: Gan 2026; manifest `gan2026_split_v1`; split `test`; 450 rows.
- Row policy: **aggregate-only**.
- The runner may read each note only to make the frozen call and score it.
- No test-row identifier, note, prediction, evidence, gold label, model-specific
  failure, or hard slice may be printed, copied, analyzed, or used to change a
  prompt, repair, scorer, or conclusion.
- Raw JSONL checkpoints remain sealed under ignored `scratch/holdout/` roots.
  Only aggregate metrics and sealed-artifact fingerprints may leave those roots.

## Fixed conditions

- Model: `openai/gpt-5.6-luna`
- Temperature: `1`
- Max tokens: `10000`
- Cache: disabled
- Repair: `hybrid_full_stack`
- Schema: frozen v0.5 events-plus-selection contract
- Scores: Gan Purist primary; Pragmatic secondary
- Output root:
  `scratch/holdout/gan2026_luna_prompt_variants_test450_20260730/`

## Variants

| ID | Prompt | Call mode |
| --- | --- | --- |
| A | `gan2026_hybrid_structured_events_v0.5` | No-call replay of sealed Luna v0.5 test450 raw outputs |
| B | `gan2026_hybrid_structured_events_v0.8_luna_rate` | Fresh live calls |
| C | `gan2026_hybrid_structured_events_v0.8_luna_current` | Fresh live calls |

A reuse source (sealed):

`scratch/holdout/gan2026_matched_v05/gpt56luna/rows.jsonl`  
SHA-256 `292169c5a3c0f786ace2e9505e40e026c2b55a4cb0a1d73401d8c925a4de06de`

Prompt snapshots:

| Variant | Snapshot | SHA-256 |
| --- | --- | --- |
| A | `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.5.txt` | `77a5575244423f989b247ff1e89930c081c0e91a3b19e0ad74687bf40eb90993` |
| B | `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.8_luna_rate.txt` | `494f1f76f8ca845e43a05e0a91956cc5b812ce4b3323379923b55003f6636a91` |
| C | `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.8_luna_current.txt` | `eb23c98e38bb9dfbacd40fe3604ba734cfdd926e7eb259d2e5f06c11a644238a` |

## Launch gate

The development A/B/C `validation750` panel already completed with dual
readouts and no transport blocker. That substitutes for a new five-record
validation pilot. No prompt text may change after this protocol is frozen.

## Required aggregate readout

For each variant retain only:

- rows completed and unique source-row count;
- call failures and blocking parse/schema failures;
- exact/grounded evidence counts;
- LLM-only Purist correct count;
- LLM-with-rules Purist and Pragmatic correct counts;
- artifact path and SHA-256;
- prompt version and snapshot hash.

Do not retain or report row-level traces outside sealed holdout storage.

## Stop rule

- Complete each variant once under this frozen condition.
- Transport or resume defects may be repaired operationally without inspecting
  clinical failures.
- A prompt, schema, clinical-repair, normalization, or scorer change after
  seeing test aggregates rejects this protocol and starts a new candidate.
- Test aggregates must not be used to choose among B and C or to edit
  instructions.

## Claim boundary

Aggregate-only Luna-versus-Luna transfer evidence on `test450` for the named
prompts and repair stack. It does not establish clinical validation, general
model superiority, or promotion into the frozen six-model v0.5 panel.
