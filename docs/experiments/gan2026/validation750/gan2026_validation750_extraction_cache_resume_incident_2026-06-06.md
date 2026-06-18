# Gan 2026 Validation750 Extraction Cache/Resume Incident

Date: 2026-06-06

Status: recovery complete; runner fix implemented for review.

## Scope

This report records the validation750 extracted-candidate schema run incident
encountered during the component architecture reset mechanics expansion. It is
about experiment-runner durability and artifact recovery. It does not make a
benchmark-comparable claim and does not authorize locked-test work.

## Incident

The intended run was a validation750 mechanics expansion of the
`llm_extracted_candidate_schema_probe` pipeline:

- model: `openai/gpt-4.1-mini`;
- prompt/schema version: `gan2026_extracted_candidate_schema_probe_v6`;
- split: first 750 rows of `validation` from `gan2026_split_v1`;
- claim boundary: schema-fit candidate extraction only; no scoring and no final
  labels.

The first long run reached a checkpoint of 675/750 rows before the shell command
timed out. The checkpoint artifact at that point contained the expected partial
JSONL and Markdown report.

When the same 750-row command was rerun, the experiment runner started again at
row 1 instead of resuming from the existing JSONL. Its progress checkpoint then
overwrote the previous 675-row JSONL with a new shorter 50-row JSONL. The
result was an apparent loss of the 625 materialized rows between the surviving
first 50 rows and the separately completed final 75 rows.

## Root Cause

The shared LLM pipeline CLI relied on DSPy/LiteLLM cache for request-level
reuse, but it had no artifact-level resume behavior.

Concretely:

- `--jsonl` was used both as the final output and as the progress checkpoint
  path;
- a rerun always passed the full requested record list to the pipeline;
- checkpoint writing used normal write mode and rewrote the target JSONL with
  the rows completed in the current process;
- the runner did not inspect existing `source_row_index` rows before starting;
- if DSPy cache missed or was slow, the runner still replayed from row 1 and
  could overwrite a longer partial artifact with a shorter one.

The cache itself did exist. It stored SQLite-backed pickled LiteLLM
`ModelResponse` values under `C:\Users\cbrow\.dspy_cache`. However, that cache
is request-level and opaque to the experiment artifact layer. It is not a safe
substitute for runner-level resume.

## Recovery

No ordinary backup, temp file, or `.bak` copy of the 675-row checkpoint was
found.

Recovery used three sources:

- surviving overwritten main artifact:
  `experiments/gan2026_extracted_candidate_schema_probe_validation750_gpt41mini_v6_2026-06-06.jsonl`
  with 50 rows;
- targeted final-75 artifact:
  `experiments/gan2026_extracted_candidate_schema_probe_validation750_gpt41mini_v6_rows676_750_2026-06-06.jsonl`
  with 75 rows;
- DSPy cache reconstruction for rows no longer present in the JSONL.

The cache reconstruction parsed today’s cached `gpt-4.1-mini` model responses,
validated the `candidate_draft_set`, extracted candidate evidence snippets, and
mapped each response back to validation750 records only when evidence snippets
uniquely identified one row. That recovered 582 of the 625 missing rows.

The remaining 43 rows could not be uniquely reconstructed from cached evidence,
so they were rerun live as a targeted recovery slice:

- `experiments/gan2026_extracted_candidate_schema_probe_validation750_gpt41mini_v6_remaining43_2026-06-06.jsonl`

The final combined extraction artifact was then assembled in validation750 row
order from:

- first 50 surviving rows;
- 582 cache-recovered rows;
- 43 targeted live recovery rows;
- final 75 targeted live rows.

Final combined artifact:

- `experiments/gan2026_extracted_candidate_schema_probe_validation750_gpt41mini_v6_combined_2026-06-06.jsonl`
- `experiments/gan2026_extracted_candidate_schema_probe_validation750_gpt41mini_v6_combined_2026-06-06.md`

Combined summary:

- rows: 750;
- candidate sets: 750;
- total candidates: 1,408;
- call failures: 0;
- parse/validation issue rows: 42;
- detail failure rows: 0;
- evidence error rows: 27;
- source phrase error rows: 30;
- rows with no candidates: 17.

The downstream deterministic+LLM CandidateSet union was then generated:

- `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.jsonl`
- `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.json`
- `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.md`

Union summary:

- rows: 750;
- total candidates: 1,834;
- missing LLM candidate-set rows: 0;
- LLM call-error rows: 0;
- LLM parse/validation issue rows: 42;
- rows with no candidates: 10;
- merged duplicate candidates: 42;
- merged nested duplicate candidates: 625.

## Fix Implemented

The shared LLM pipeline CLI now supports explicit artifact-level resume via
`--resume-existing`.

Resume behavior:

- loads existing rows from the target `--jsonl` when present;
- reads completed `source_row_index` values;
- skips already completed records before calling the pipeline;
- writes progress checkpoints to `.resume-part` files, not the final target;
- combines existing and newly produced rows in requested split order only after
  the resumed run succeeds;
- recomputes the final summary from combined rows for pipelines that expose a
  summarizer;
- errors if duplicate or missing `source_row_index` rows would produce an
  unsafe combined artifact.

This fix addresses the real failure mode: partial artifact overwrite. DSPy
cache can still reduce call cost, but artifact correctness no longer depends on
cache hits.

## Verification

Focused CLI tests were updated to cover resume behavior:

- existing JSONL rows are skipped;
- resumed progress uses `.resume-part` checkpoint paths;
- final JSONL/report receive the combined rows;
- summary is recomputed over the combined artifact.

Test command:

```powershell
$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_llm_pipeline_cli.py -q
```

Result:

- 7 passed;
- 11 DSPy deprecation warnings unrelated to this change.

## Operational Guidance

For broad live LLM runs, use:

```powershell
--resume-existing --progress-every 25
```

Do not rerun a broad pipeline against an existing partial JSONL without
`--resume-existing`. If a command times out, inspect the target JSONL row count
and resume with the same output path plus `--resume-existing`.

If recovery from cache is ever needed again, treat it as an emergency recovery
path only. Cache reconstruction should require unique row mapping and should
write a separate recovery artifact before any combined artifact is assembled.
