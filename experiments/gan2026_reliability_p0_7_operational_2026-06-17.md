# P0.7 — Operational Integrity + Offline Cost/Latency Reconstruction

Date: 2026-06-17  ·  Model calls: 0 (tiktoken only, no API)

## Operational integrity (recomputed)

| Artifact | Rows | Repair-event rows | Call errors | Model render fails | Unscorable gold | Idx unique |
|---|---:|---:|---:|---:|---:|:--:|
| se_mini_validation750 | 750 | 528 | 0 | 0 | 2 | ✓ |
| reasoner_validation750 | 750 | 750 | 0 | 0 | 2 | ✓ |
| reasoner_test450 | 450 | 450 | 0 | 0 | 2 | ✓ |

- **Totals: 1950 rows, 0 model render failures, 0 call errors**, 6 unscorable-gold exclusions, all source indices unique: True.
- Recoverable deterministic repair events: 5483 (label normalization + decision-field-shape repair; load-bearing per RQ5 ablation, not failures).
- Resumability: `core/run_resume.py (read_completed/pending_items/merge_rows)`.

## Offline cost/token estimate (ESTIMATED, no API)

Basis: tiktoken o200k_base over saved prompt_input_json (input proxy) + raw_output; n=750.

- Prompt tokens: mean 1309, median 1294 (range 918–1877)
- Completion tokens: mean 397, median 400 (range 62–801)
- Assumed rates (USD/1M): input $0.4, output $1.6
- **Estimated cost per 1,000 notes: ~$1.16** (estimate, not billed).

## RQ8 telemetry guard over the reconstructed matrix

- Reconstructed offline: prompt_tokens, completion_tokens, total_tokens, estimated_cost_per_1000_notes_usd
- Still blocked (no offline source): retry_count, wall_clock_latency_seconds
- Status: **partially_reconstructed_offline_estimated** — RQ8 moves from fully blocked to partially reconstructed; latency and retry remain genuinely unmeasured and require a telemetry-instrumented re-pass (P2.2).

---

**Reading.** Operational *integrity* is 5/5 (zero model render failures, zero call errors, unique provenance across every subject row, resumable runners; deterministic repair fires often but always recovers, and the only un-rendered rows are unscorable-gold exclusions). The cost leg is no longer fully dark: token volume and a dollar band are recoverable offline, leaving only wall-clock latency and retry count for a measured re-pass.
