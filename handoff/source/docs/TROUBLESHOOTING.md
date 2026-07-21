# Troubleshooting

- `configuration_error`: run `show-config`; set matching `VLLM_*` values. Keys
  are never printed.
- Connection or certificate failure: confirm the approved URL, certificate
  chain, firewall, and endpoint process locally.
- Model mismatch: compare requested and returned identifiers from `check`.
- Unsupported `json_schema`: the client makes one bounded fallback to JSON
  object mode and records two request attempts.
- Reasoning without final content: disable thinking or increase the configured
  completion budget; `check` reports the condition without printing content.
- `schema_validation_failure`: rerun the synthetic `check`; use a private trace
  only inside the approved boundary.
- Truncation: inspect `finish_reason`, then adjust `VLLM_MAX_TOKENS` deliberately.
- `resume_mismatch`: input, route, model, settings, prompts, schemas, rules, or
  package changed. Start a new output rather than mixing runs.
- Existing output: choose a new path or pass `--overwrite` intentionally.

