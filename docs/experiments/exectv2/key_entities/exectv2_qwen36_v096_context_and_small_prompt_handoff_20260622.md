# ExECTv2 Qwen3.6 v0.9.6 Context and Small-Prompt Handoff

Generated: 2026-06-22

## Summary

Local Qwen `qwen3.6:35b` is operational through the native Ollama route:
`ollama_chat/qwen3.6:35b`, `api_base=http://localhost:11434`, `think=false`,
DSPy cache disabled, and `CLINICAL_EXTRACTION_OLLAMA_NUM_GPU` unset so Ollama
keeps automatic offload/spill behavior.

The current Qwen single-GPT best checkpoint is still below the target:

| Checkpoint | Split | headline_target F1 | Diagnosis | SeizureFrequency | Prescription | Investigations | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| v0.9.5 same-raw reparse | dev25 | 0.8297 | 0.8104 | 0.6429 | 0.9231 | 0.9500 | do not promote |
| v0.9.6 full prompt | dev5 | 0.9275 | 0.8421 | 0.8750 | 1.0000 | 1.0000 | diagnostic dev5 pass |
| v0.9.6 full prompt | dev25 | 0.7975 | 0.7972 | 0.6429 | 0.8312 | 0.9500 | do not promote |

v0.9.6 improved the tiny dev5 read but did not hold on dev25. The main
blocking families remain SeizureFrequency and Diagnosis; v0.9.6 also regressed
Prescription on dev25 relative to the v0.9.5 reparse checkpoint.

## Context-Window Test

The full v0.9.6 prompt was tested with:

```powershell
.venv\Scripts\python.exe -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_only_key_entities_structured `
  --mode live --split dev --pilot 5 `
  --model ollama_chat/qwen3.6:35b `
  --api-base http://localhost:11434 `
  --temperature 0.0 --max-tokens 2200 `
  --ollama-num-ctx 12288 --no-dspy-cache `
  --progress-every 1 `
  --out-jsonl experiments\exectv2_llm_only_key_entities_structured_v096_dev5_qwen36_35b_ollama_autogpu_ctx12288_maxtok2200_20260622.jsonl
```

Observed runtime state:

- Started around `2026-06-22 09:17:41 +01:00`.
- Ollama reported `CONTEXT 12288`, `PROCESSOR 100% CPU`, model size `23 GB`.
- At `09:25:06`, DSPy warned that an LM response was truncated at
  `max_tokens=2200`.
- First checkpoint landed by `09:30:34`: 1 of 5 letters processed,
  8 scored mentions, 0 call failures, 0 parse failures.
- The run was stopped at `09:33:32` after the user asked to pause and write this
  handoff. The one-row checkpoint was preserved.

Partial row:

| Letter | Raw chars | Scored mentions | Raw mentions | Parse errors | Entities |
| --- | ---: | ---: | ---: | --- | --- |
| EA0002 | 3164 | 8 | 8 | none | Diagnosis, Prescription, SeizureFrequency |

Interpretation: `num_ctx=12288` is probably enough for the full prompt plus
typical output in token-budget terms, but `max_tokens=2200` is too tight for
some letters and the full prompt is extremely slow when Ollama places this model
at `100% CPU`. If continuing the full prompt, use `--progress-every 1` and
consider `max_tokens=3000` with `num_ctx=14336` or `16384`.

## Prompt Size Analysis

Earlier prompt sizing using saved v0.9.6 payloads estimated the full prompt at
about `39.5k-44.2k` characters. A `cl100k_base` proxy estimated max full-prompt
plus output near `12.1k` tokens on dev5/dev25 samples, making `12288` a very
tight but plausible context setting. Exact Qwen tokenization was unavailable
locally because Ollama `/api/tokenize` returned 404 and the environment lacks a
Qwen tokenizer package.

The sharded per-family prompt-only dev5 pass produced much smaller prompts:

| Family | Rows | Min chars | Median chars | Max chars |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 5 | 3667 | 4113 | 4335 |
| SeizureFrequency | 5 | 5861 | 6307 | 6529 |
| Prescription | 5 | 3900 | 4346 | 4568 |
| Investigations | 5 | 3939 | 4385 | 4607 |

This is a roughly 7x to 11x reduction in prompt characters per call versus the
full all-family event ledger. It trades one large call per letter for four small
family calls per letter.

Prompt-only artifacts:

- `experiments/exectv2_llm_only_per_entity_promptonly_dev5_qwen36_35b_ollama_autogpu_ctx12288_maxtok2200_20260622_diagnosis.jsonl`
- `experiments/exectv2_llm_only_per_entity_promptonly_dev5_qwen36_35b_ollama_autogpu_ctx12288_maxtok2200_20260622_seizurefrequency.jsonl`
- `experiments/exectv2_llm_only_per_entity_promptonly_dev5_qwen36_35b_ollama_autogpu_ctx12288_maxtok2200_20260622_prescription.jsonl`
- `experiments/exectv2_llm_only_per_entity_promptonly_dev5_qwen36_35b_ollama_autogpu_ctx12288_maxtok2200_20260622_investigations.jsonl`
- `experiments/exectv2_llm_only_per_entity_promptonly_dev5_qwen36_35b_ollama_autogpu_ctx12288_maxtok2200_20260622_combined.md`

## Code Changes Made

Structured key-family runner:

- Added `--ollama-num-ctx`, setting `CLINICAL_EXTRACTION_OLLAMA_NUM_CTX` without
  setting `CLINICAL_EXTRACTION_OLLAMA_NUM_GPU`.
- Added Windows-safe Qwen artifact slugs.
- Added prompt-profile plumbing, including the rejected `qwen_compact` profile.

Structured key-family engine:

- Current prompt version:
  `exectv2_hybrid_key_family_event_ledger_v0.9.6`.
- Added schema repair for Python-literal JSON-ish payloads.
- Added top-level event-array coercion.
- Added no-mention `family == "reject"` event dropping.
- Added exact model-selected text evidence repair for Prescription/Diagnosis
  only.
- Added v0.9.6 dev-only prompt guidance and examples around SF active-rate
  headings, returned seizures, named anchors, and generic spell-anchor rejects.

Per-entity runner and engine:

- Added `--ollama-num-ctx` to `run_llm_only_per_entity`.
- Made per-entity auto artifact names Windows-safe for `ollama_chat/qwen3.6:35b`.
- Added mention-level `entity`, `component_owner`, and `source_lane` fields to
  per-entity predicted rows so assembly can consume the artifacts directly.
- Added mention-level `entity` to per-entity gold rows.

Dictionary/lens changes:

- Added `normalize_dose_value`.
- Added uneven daily regimen splitting for examples like
  `750mg mane, 500 mg nocte` and `100 mg morning, 175 mg afternoon`.
- Added a guard so already split once-daily dose rows are not split again.

## Verification

Passed before this handoff:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_exectv2_llm_only_key_entities_structured.py tests\test_exectv2_standard_dictionary.py tests\test_exectv2_v09_dictionary_lenses.py tests\test_gan2026_llm_config.py -q
```

Result: `52 passed`.

After the per-entity runner patch:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_exectv2_llm_only_key_entities_structured.py tests\test_gan2026_llm_config.py -q
```

Result: `15 passed`.

Ruff passed on the edited per-entity files:

```powershell
.venv\Scripts\python.exe -m ruff check src\clinical_extraction\tasks\epilepsy_phenotyping\exectv2\runners\run_llm_only_per_entity.py src\clinical_extraction\tasks\epilepsy_phenotyping\exectv2\llm\llm_only_per_entity.py
```

## Recommended Next Session

1. Run the sharded per-family live dev5 probe first. Use `--progress-every 1`,
   `--ollama-num-ctx 12288`, and `--max-tokens 2200`.

```powershell
.venv\Scripts\python.exe -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_only_per_entity `
  --mode live --split dev --pilot 5 `
  --entities Diagnosis SeizureFrequency Prescription Investigations `
  --model ollama_chat/qwen3.6:35b `
  --api-base http://localhost:11434 `
  --temperature 0.0 --max-tokens 2200 `
  --ollama-num-ctx 12288 --no-dspy-cache `
  --progress-every 1 `
  --out-prefix exectv2_llm_only_per_entity_dev5_qwen36_35b_ollama_autogpu_ctx12288_maxtok2200_20260622
```

2. Build a four-producer assembly config using the per-family artifacts:
   Diagnosis with `diagnosis_convention_dictionary_v09`,
   SeizureFrequency with `sf_convention_dictionary_v09`,
   Prescription with `prescription_dictionary_v09`, and Investigations with
   `investigations_passthrough_v09`.

3. Score through `run_finding_assembly`, then run the real-scorer error ledger.

4. Compare the sharded dev5 score and runtime against:
   the full prompt dev5 v0.9.6 `0.9275` at `ctx=16384`, and the interrupted
   full prompt `ctx=12288/max_tokens=2200` timing probe.

5. If sharded dev5 is competitive and materially faster, escalate to dev25.
   Otherwise, keep the full prompt but raise output budget and use `ctx=14336`
   or `16384`.

## Claim Boundary

All results here are dev-only, attribution-clean development evidence. No
full-200 or locked-test claim is made. The sharded per-family approach is still
Qwen-owned LLM extraction, but it is no longer a single call per letter; report
it as a single local-Qwen engine with per-family focused prompts if promoted.
