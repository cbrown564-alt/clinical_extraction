# Gan 2026 matched hosted v0.5 test450 protocol

Date: 2026-07-16; continuation amendment: 2026-07-17  
Status: predeclared; continuation authorized  
Readout: aggregate-only

## Primary question

How do GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, and DeepSeek
V4 Flash compare when each uses the exact restored Gan structured-events v0.5
payload and the same current non-prompt pipeline?

This is a matched aggregate panel for the named routes and frozen scorer. It is
not a model-neutral capability ranking, clinical validation, or a pristine
one-shot holdout claim. Gan test450 has a prior documentation exposure, so no
row-level output may be inspected, reported, or used for tuning.

## Data, split, and row policy

- Dataset: Gan 2026; manifest `gan2026_split_v1`; distribution `test`; 450 rows.
- Manifest: `data/Gan (2026)/splits/gan2026_split_v1.json`.
- Manifest SHA-256: `5dd39c552bcb60a40f0c79245a9f7346fd27a064cd27263c902e879af3bf7c57`.
- The runner may read each note only to make the frozen call and score it.
- No test-row identifier, note, prediction, evidence, label, model-specific
  failure, or row slice may be printed, copied, or analyzed.
- Raw JSONL checkpoints remain sealed beneath ignored `scratch/holdout/` roots.
  Only aggregate metrics and sealed-artifact fingerprints may leave those roots.

## Candidate and exact v0.5 prompt

Candidate: current `llm_with_rules` / `hybrid_structured_events`, one structured
event call per note, followed by the current format repair, selected-evidence
repair, deterministic clinical repair families, rendering, and frozen Gan
Purist/Pragmatic scoring.

The model-facing prompt is explicitly selectable as
`gan2026_hybrid_structured_events_v0.5`. Its rendered fixture snapshot is:

| Role | Path | SHA-256 | Bytes |
| --- | --- | --- | ---: |
| v0.5 rendered payload | `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.5.txt` | `77a5575244423f989b247ff1e89930c081c0e91a3b19e0ad74687bf40eb90993` | 3,716 |
| v0.5 prompt builder | `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py` | `35fb00839d4e8e53bf4a6309b2096b1419de4601f0b386174beba677894afc5b` | — |

The v0.5 payload is the historical 13-instruction payload: it excludes the
v0.6 seizure-free precedence rule and all v0.7 count-conservation additions.
The exact payload comparison against all 450 retained GPT rows matched 450/450
in the no-call reconciliation recorded in
`experiments/gan2026_v05_gpt41mini_reconciliation_20260716.json`.

## Frozen non-prompt condition

The following files are frozen before fresh calls:

| Role | Path | SHA-256 |
| --- | --- | --- |
| schema and JSON-dialect repair | `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/schema_repair.py` | `cd3c2095fb8923f328a7c5b144c4a38f5ec65be53a65a84d866cc6afcec949fe` |
| label and selected-evidence repair | `src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py` | `f3a11e3480c001b8972bb8f70ddcb674a567418491a61ad983aae50f47c83c4c` |
| Purist/Pragmatic mapping | `src/clinical_extraction/tasks/seizure_frequency/gan2026/labels.py` | `6c1635541403c3cf419595a7883ec8055335facf88af8a62cc175465afb224ba` |
| scorer | `src/clinical_extraction/tasks/seizure_frequency/gan2026/evaluate.py` | `18fdec285a5a80aa92d06bdb6e75f6b6e619d76dfeb1ca5eec0751fe7123c402` |
| v0.5 hosted runner | `scripts/run_gan2026_v05_hosted_condition.py` | `7bcf99fd7327e9ce5f44313ab6996819e397923ac805c9fbd65df7f619dfb013` |

Calls per note: one. DSPy/LiteLLM cache: disabled. Output limit and transport
differences are provider requirements, not clinical or semantic adapters.

## Conditions

| Condition | Route | Temperature | Max tokens | Disposition |
| --- | --- | ---: | ---: | --- |
| GPT-4.1-mini | `openai/gpt-4.1-mini`, OpenAI chat | 0 | 10,000 | Fresh required after failed reconciliation |
| GPT-5.6 Luna | `openai/gpt-5.6-luna`, OpenAI chat | 1 | 10,000 | Fresh after pilot |
| GPT-5.6 Sol | `openai/gpt-5.6-sol`, OpenAI Responses; temperature omitted | omitted | 10,000 | Fresh after pilot |
| DeepSeek V4 Flash | `deepseek/deepseek-v4-flash`, official route | 0 | 32,000 | Fresh after pilot |

## Operational pilots and launch gate

Each condition runs one five-record validation pilot using the same v0.5
prompt, schema, repair, route, temperature, output limit, and disabled cache.
The pilot reads aggregates only and passes only with:

- 5/5 completed calls;
- 5/5 structured records;
- zero blocking parse, schema, or label failures; and
- 5/5 exact evidence substrings.

Pilot accuracy is not a tuning signal. A transport-only defect may be corrected
and the pilot repeated. A prompt, schema, clinical repair, normalization, or
scoring defect rejects this protocol and starts a new candidate; it does not
authorize test450 repair.

## Reuse and stop rule

The retained GPT-4.1-mini `364/450` artifact is not reused. The aggregate-only
no-call reconciliation found exact v0.5 payload matches for 450/450 rows, but
only 435/450 structured-record matches, 170/450 normalized-event matches, and
15 final-label changes; current replay was 366/450 Purist and 383/450
Pragmatic versus stored 364/450 and 381/450. The mismatch is clinically
meaningful under decision 0043, so GPT-4.1-mini is rerun once under this frozen
condition.

After a passing pilot, run each condition once from an empty sealed holdout
root. Retain every completed aggregate regardless of score. A call, parser,
schema, evidence, repair, or scoring defect stops that condition and is
reported as an operational failure; it does not license another test call.

Primary metric: Purist correct count and accuracy over all 450 rows. Secondary:
Pragmatic correct count and accuracy, call failures, parse/schema/label issues,
exact-evidence count, format and semantic repair totals, timing, provider usage
when available, and sealed-artifact SHA-256/byte fingerprints.

Configuration: `configs/holdout/gan2026_matched_v05_hosted_20260716.json`.

## Execution amendment

All four five-record pilots passed the gate. GPT-4.1-mini and Luna completed
their fresh test450 conditions. Their aggregate-only results and sealed artifact
fingerprints are recorded in
`experiments/gan2026_matched_v05_test450_aggregate_20260716.json`.

The combined controller reached its one-hour command timeout while Sol and
DeepSeek were still running. This was an outer shell/controller timeout, not an
intended provider or per-request timeout: the runner did not pass a request
timeout to DSPy/LiteLLM. Luna had completed 450/450; Sol and DeepSeek had
completed 350/450 and 150/450 respectively. Their completed checkpoints are
retained.

On 2026-07-17, aggregate-only continuation was explicitly authorized. The
existing Sol and DeepSeek JSONL files are resumed in place with
`--resume-existing`. The runner validates completed `source_row_index` values,
loads those rows, and calls only the missing 100 Sol rows and 300 DeepSeek
rows. No completed row is recreated, no partial condition is scored, and no
row-level value, failure, slice, or comparison may be inspected or reported.
The continuation uses the same v0.5 prompt, current non-prompt pipeline,
model route, temperature, output limit, disabled cache, split, and scorer.

The two conditions were initially queued sequentially to avoid introducing
additional concurrency pressure. On 2026-07-17, parallel continuation was
explicitly requested and authorized. Each condition remains independently
sealed and uses its own existing checkpoint; no completed row is recreated.
A resumed condition is complete only when its merged artifact contains all
450 unique requested rows and passes aggregate validation. If continuation
fails again, its partial artifact is retained and reported as incomplete; it
is not silently replaced or rerun.

## 2026-07-18 evidence correction and continuation amendment

The Sol continuation completed on 2026-07-17 but was not propagated into the
retained aggregate or project status. Aggregate-only verification on
2026-07-18 confirmed 450 unique test-manifest rows, prompt v0.5 throughout,
373/450 Purist, 384/450 Pragmatic, 450 exact-evidence selections, and zero call
or parse/validation failures.

DeepSeek's first continuation added 200 rows to its 150-row base, leaving 350
unique rows and 100 remaining. The user authorized the remaining calls in
parallel with the local v0.5 queue and explicitly accepted today's shared
schema repair for that continuation. The reported DeepSeek result must come
from a no-call replay of all 450 saved raw outputs through that current schema
repair, not from the mixed intermediate parsed fields. The extension and
replay rules are predeclared in the
[2026-07-18 local and replay protocol](gan2026_matched_v05_local_test450_and_qwen_val750_protocol_2026-07-18.md).

## Completion addendum, 2026-07-20

All six aggregate-only test450 conditions are complete. DeepSeek finished with
450 unique rows and scored 344/450 Purist and 366/450 Pragmatic. The local Qwen
and Gemma extensions completed at 362/450 and 355/450 Purist respectively.
The aggregate artifact records all six scores, operational counts, and sealed-
artifact fingerprints. Completion does not authorize test-row inspection or
failure analysis.
