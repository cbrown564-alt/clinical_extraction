# Gan 2026 matched hosted v0.7 test450 protocol

Date: 2026-07-15  
Status: complete; six aggregate-only conditions retained
Authorization: the user explicitly requested these runs on 2026-07-15.

## Question and claim boundary

How do the selected six models compare when each uses the same Gan one-call
pipeline, prompt v0.7, repair policy, and scorer?

The result may be reported only as a matched, aggregate-only panel on the
previously used locked holdout. Prompt v0.7 was developed from permitted
validation failures, but test450 has supported sequential aggregate runs and a
small part of one generated row report was accidentally exposed during earlier
documentation work. The panel is therefore not a pristine one-shot or
model-neutral capability ranking. It cannot support row-level analysis,
post-holdout tuning or a model-neutral capability ranking.

## Frozen data, rows, and readout

- Dataset: Gan 2026; split manifest `gan2026_split_v1`; distribution `test450`;
  450 rows.
- Manifest file: `data/Gan (2026)/splits/gan2026_split_v1.json`, canonical
  SHA-256 `c5f512d8744261916bd6d92562430489a3ba0494b0bf7c6575bfaa9e58680143`.
- The runner may read each note only to make the frozen call and score it.
- No held-out identifier, note, prompt instance, raw response, prediction,
  evidence, label, failure, or model-specific row may be inspected or copied
  into a retained report.
- Row JSONL remains sealed under ignored `scratch/holdout/`. The only permitted
  readout is an aggregate with row count, Purist and Pragmatic correct counts
  and accuracy, call failures, parse/schema/label issues, exact-evidence count,
  repair totals, timing, and provider usage when available.
- Cache is disabled. Each condition makes one model call per note. A transport
  failure is a failed call, not permission for an extra successful sample.

## Frozen prompt, pipeline, repair, and scoring

Prompt selection is a required runner argument and must equal
`gan2026_hybrid_structured_events_v0.7` before the CLI loads any note or makes
any call. The rendered model-facing snapshot was inspected under the
plain-language prompt checklist: task text and field descriptions are plain,
research metadata is separated, non-obvious fields are described, and the
snapshot is deterministic. Its canonical LF fingerprint is:

| Role | Path | Canonical SHA-256 | Canonical bytes |
| --- | --- | --- | ---: |
| Rendered prompt | `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.7.txt` | `4ea331bdd24ca70e4fc35f9f6bd502e7a7d0d5a4ffb080d99269a3af89262dda` | 6,450 |
| Pipeline and prompt builder | `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py` | `78126924f5a23052bde9f5c527576386e73c9d3bec3da1748950af563714ce64` | 46,872 |
| Hosted runner | `scripts/run_gan2026_hosted_condition.py` | `56d88e7e9a5cc4c8ea7bdaed2096b7e837cfcc2c032cad854432f423f3ccb0f8` | 2,215 |
| Schema and JSON-dialect repair | `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/schema_repair.py` | `ca239a2cbc626a638b8f27271cad0d1ab4d31605373cf7d3651a9d092caec068` | 8,673 |
| Label and selected-evidence repair | `src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py` | `8ebc5a9b0b08fe787f7074cc4125b58c833839a1d3495ac7cc4119dd009ebcb4` | 8,900 |
| Clinical repair families | `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py` | `a44b34a13084c4ebedfbf9167458033da900854e511d6aca374b038e6a2e6d2e` | 21,266 |
| Monthly-diary repair | `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_monthly_diary.py` | `3fce06b3cde4d82773d87790f88a45797335735b73025e4b76176c66cf38bd45` | 10,736 |
| Temporal helpers | `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_temporal.py` | `d292dba683465f70444028a7ee54844742daefe50e47bac5b8ede38a7edba7a3` | 10,426 |
| Purist and Pragmatic mapping | `src/clinical_extraction/tasks/seizure_frequency/gan2026/labels.py` | `8d79d223e53e8cfdf5a0c4ef19b4864108968f67d9558454f798a7cbe82c715d` | 7,253 |
| Scoring | `src/clinical_extraction/tasks/seizure_frequency/gan2026/evaluate.py` | `ea3fe53c5ec235fd84df8bfe785667418516d34141dd3e0a53fb2f36ecf9fc7a` | 4,439 |

The candidate is the current `llm_with_rules` / `hybrid_structured_events`
pipeline with the default named `hybrid_full_stack` repair configuration.
Raw structured output, JSON-dialect repair, selected-evidence derivation,
clinical repair families, rendered label, and scorer remain separately
recorded. None may vary by model.

The only permitted model-specific adapters are format or transport adapters:

- DSPy/Pydantic structured-output formatting for the frozen schema;
- the existing Python-literal JSON-dialect repair, recorded when used;
- Luna's provider-required temperature `1`;
- Sol's Responses transport with the unsupported temperature field omitted;
- DeepSeek's official `deepseek-v4-flash` route, whose response adapter returns
  final content while the route itself has thinking enabled.

No adapter may select a different clinical fact, change an event, infer a new
label, retry a parsed but clinically undesirable answer, or apply a
model-specific semantic repair.

## Matched conditions

| Condition | Route | Temperature | Output limit | Disposition |
| --- | --- | ---: | ---: | --- |
| GPT-4.1-mini | `openai/gpt-4.1-mini` | 0 | 10,000 | Fresh after pilot |
| GPT-5.6 Luna | `openai/gpt-5.6-luna` | 1 | 10,000 | Retain completed v0.7 run |
| GPT-5.6 Sol | `openai/gpt-5.6-sol`, Responses | omitted | 10,000 | Retain completed v0.7 run |
| DeepSeek V4 Flash | `deepseek/deepseek-v4-flash` | 0 | 32,000 | Fresh after pilot |
| Qwen 3.6:35B | `ollama_chat/qwen3.6:35b`, native Ollama | 0 | recorded local condition | Retain sealed-output aggregate |
| Gemma 4 26B | `ollama_chat/gemma4:26b`, native Ollama | 0 | recorded local condition | Retain sealed-output aggregate |

Configuration:
`configs/holdout/gan2026_matched_v07_hosted_20260715.json`.

The completed Luna and Sol runs are not repeated. Their sealed artifacts and
aggregate results are retained by fingerprint. GPT-4.1-mini and DeepSeek use
new empty output roots and cannot resume any historical test450 artifact.

## Validation pilots and launch gate

Before its test450 call, each fresh condition runs once on the same first five
permitted validation records with the frozen prompt, pipeline, repair, route,
temperature, output limit, and disabled cache. Rows may be stored in ignored
validation scratch, but the gate reads aggregates only.

The pilot passes only if it has 5/5 completed calls, 5/5 structured records,
zero blocking parse/schema/label failures, and 5/5 exact evidence substrings.
Purist or Pragmatic accuracy does not affect the gate. A transport-only defect
may be corrected and the pilot repeated before any test call; any prompt,
schema, clinical-repair, normalization, or scoring defect rejects this
predeclaration and requires a new validation candidate and protocol.

## Artifact schema, metrics, and stop rule

The retained machine-readable panel artifact has one object per model with:
model and route identity, prompt version, token limit, cache state, calls per
note, repair mode, row count, Purist and Pragmatic totals, operational failure
counts, timing when available, sealed-artifact path plus SHA-256 and bytes, and
the protocol and code fingerprints above. It contains no held-out row field.

Primary metric: Purist correct count and accuracy across 450 rows. Secondary:
Pragmatic correct count and accuracy, aggregate call/parse/schema/label issues,
exact-evidence count, repair totals, and timing/provider usage when available.

Run each fresh condition once after its pilot passes. A completed aggregate is
retained regardless of score. A call, parser, schema, evidence, repair, or
scoring defect is recorded and stops that condition; it does not license
test450 repair or rerun. The original hosted launch gate closed when both fresh
hosted conditions completed and all four hosted aggregates were fingerprinted.
The retained study is complete when the Qwen and Gemma aggregate-only local
conditions are also fingerprinted in the common six-model panel.

## User-requested interruption and clean restart amendment

The first matched launch was stopped at the user's request before laptop
shutdown. Its last sealed checkpoints contained 300 GPT-4.1-mini rows and 70
DeepSeek V4 Flash rows. All launcher and interpreter processes were stopped.
Those partial artifacts are rejected: they must not be resumed, scored,
reported, or added to retained evidence.

On the user's explicit 2026-07-15 instruction to restart both hosted runs, the
same two conditions are authorized once more from empty replacement roots:

- `scratch/holdout/gan2026_matched_v07_restart_v2/gpt41mini/`
- `scratch/holdout/gan2026_matched_v07_restart_v2/deepseek_v4_flash/`

The frozen prompt, code fingerprints, routes, temperatures, token limits,
repair/scoring policy, one saved call per note, disabled cache, aggregate-only
readout, and stop rule are unchanged. The earlier validation pilots remain the
launch gate because both passed 5/5 calls, 5/5 structured records, zero
blocking parse/schema/label failures, and 5/5 exact evidence, and no frozen
prompt or implementation file changed afterward. The aborted calls are an
operational cost of interruption and cannot be used in matched cost, token, or
latency claims.

## Aggregate result

Both replacement runs completed. Together with the retained Luna, Sol, Qwen,
and Gemma conditions, the matched six-model panel is complete. No test450 row
was inspected to produce this table. Qwen and Gemma were promoted from
aggregate-only no-call reparses of sealed local outputs; this route difference
is retained as provenance rather than used to downgrade their claim status.

| Model | Purist | Pragmatic | Structured records | Exact evidence | Repair notes | Call failures | Parse/schema/label issues |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 353/450 (0.7844) | 371/450 (0.8244) | 448/450 | 419/450 | 317 | 0 | 2 |
| GPT-5.6 Luna | 352/450 (0.7822) | 365/450 (0.8111) | 447/450 | 446/450 | 305 | 0 | 3 |
| GPT-5.6 Sol | 358/450 (0.7956) | 376/450 (0.8356) | 450/450 | 449/450 | 366 | 0 | 0 |
| DeepSeek V4 Flash | 342/450 (0.7600) | 362/450 (0.8044) | 446/450 | 434/450 | 259 | 0 | 4 |
| Qwen 3.6:35B | 367/450 (0.8156) | 380/450 (0.8444) | 450/450 | 363/450 | 316 | 0 | 0 |
| Gemma 4 26B | 343/450 (0.7622) | 367/450 (0.8156) | 450/450 | 437/450 | 291 | 0 | 0 |

GPT-4.1-mini completed in 2,469.362 seconds (41.156 minutes), and DeepSeek
completed in 11,167.049 seconds (186.117 minutes). These observed times are not
a matched latency comparison because routes, token limits, and provider
conditions differ.

The fresh GPT-4.1-mini and DeepSeek runs used commit `2f709b78` with recorded
uncommitted run-control changes. Their sealed artifacts are retained under the
replacement roots above. The result supports a same-prompt, same-pipeline
six-model comparison with the stated transport and local-reparse caveats; it
does not support row-level error analysis, post-holdout tuning, or a
model-neutral ranking.
