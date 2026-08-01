# DeepSeek V4-Flash-0731 holdout re-run protocol

Date: 2026-07-31  
Status: authorized; launches in progress  
Authorization: user requested parallel no-cache re-runs of ExECTv2 `test60`
and Gan `test450` (`llm` and `llm_with_rules`) on the updated
`deepseek-v4-flash` API surface, with no other clinical or prompt changes.

## Question

Under the frozen ExECT and Gan holdout stacks, what aggregate scores does the
2026-07-31 DeepSeek-V4-Flash API revision produce versus the retained July
holdout cells?

## Frozen conditions

Shared:

- Model: `deepseek/deepseek-v4-flash`
- Cache: disabled
- New sealed roots under `scratch/holdout/` dated `20260731` (do not overwrite
  retained July sealed artifacts)
- Aggregate-only readout; no test-row inspection, identifiers, predictions, or
  failure examples in reports

### ExECTv2 test60

- Protocol parent: [hosted test60](exectv2_hosted_test60_protocol_2026-07-15.md)
- Split: `test60`, 59 loadable letters
- Architecture: decision 0040 / 0041 one-call; prompt
  `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Diagnosis/Prescription: `default` / `default`
- Scorer: internal `clinical_headline`
- Structured max tokens: `64000` (same 0731 thinking-budget operational
  amendment as the completed `dev140` re-run; not a prompt or rule change)
- Scratch:
  `scratch/holdout/exectv2_test60_deepseek_v4_flash_0731_20260731/`

### Gan test450 `llm_with_rules`

- Protocol parent:
  [matched v0.5 test450](../../gan2026/gan2026_matched_v05_test450_protocol_2026-07-16.md)
- Split: `test`, 450 rows; manifest `gan2026_split_v1`
- Pipeline: `llm_with_rules` / hybrid structured events
- Prompt: `gan2026_hybrid_structured_events_v0.5`
- Temperature `0`; max tokens `32000`
- Scratch:
  `scratch/holdout/gan2026_test450_deepseek_v4_flash_0731_20260731/llm_with_rules/`

### Gan test450 `llm` (LLM-only)

- Same split and row policy as matched v0.5 test450
- Pipeline: `llm` / `llm_only_canonical_pipeline`
- Prompt: `gan2026_llm_only_canonical_pipeline_v0.8` (retained LLM-only
  comparator prompt; no prompt edit)
- Temperature `0`; max tokens `32000`
- Scratch:
  `scratch/holdout/gan2026_test450_deepseek_v4_flash_0731_20260731/llm/`

## Stop rule and claim boundary

Run each condition once to completion (resume allowed only within the new
dated root). Report aggregate metrics only. This is provider-update holdout
evidence for these exact stacks; it does not rewrite retained July panel cells
unless a later promotion decision says so. Not published-benchmark reproduction
or clinical validation.
