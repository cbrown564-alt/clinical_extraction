# DeepSeek unknown prompt A/U `dev750` protocol

Date: 2026-07-31  
Status: **stopped (negative)** — UNK-slice pilot insufficient; full-750 aborted  
Parent: [unknown-competence protocol](gan2026_deepseek_unknown_competence_protocol_2026-07-31.md)  
Config: [configs/gan2026/deepseek_unknown_prompt_dev750_20260731.json](../../../configs/gan2026/deepseek_unknown_prompt_dev750_20260731.json)  
Pilot compare: [experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json](../../../experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json)

## Primary question

On hosted DeepSeek V4 Flash and Gan `validation750`, does prompt candidate U
(`v0.8_deepseek_unknown`) improve **LLM-only** unknown-band metrics versus
control A (`v0.5`) without net damage to overall Purist or countable-rate
rows, and does LLM-with-rules under the final `hybrid_full_stack` clear or
approach the collaboration gates?

## Fixed conditions

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `validation750`; row inspection permitted |
| Locked | `test450` sealed; Real(300) not used |
| Model | `deepseek/deepseek-v4-flash` hosted (matched panel route) |
| Temperature / max tokens | `0` / `32000` (match matched v0.5 DeepSeek condition) |
| Schema | v0.5 events-plus-selection unchanged |
| Repair (LLM-with-rules) | Final `hybrid_full_stack` |
| Scorers | Purist primary; Pragmatic secondary; unknown-slice metrics required |
| Cache | disabled for fresh U calls |
| Output root | `scratch/validation/gan2026_deepseek_unknown_prompt_dev750_20260731/` |

## Variants

| ID | Prompt | Calls |
| --- | --- | --- |
| A | `gan2026_hybrid_structured_events_v0.5` | Reuse retained matched v0.5 DeepSeek raw outputs (no-call) |
| U | `gan2026_hybrid_structured_events_v0.8_deepseek_unknown` | Fresh hosted calls on all 750 development rows |

## Required metrics (both arms)

- Overall Purist / Pragmatic
- UNK P/R/F1, UNK accuracy, over-read, false SF, false abstention
  (`scripts/build_gan2026_unknown_slice_metrics.py` or equivalent)
- Changed-row W→C / C→W versus A for LLM-only and LLM-with-rules
- Collaboration gates from the parent protocol

## Stop rule

- **Answer:** U meets LLM-only unknown gates with non-damage, or U fails gates
  but mechanism evidence shows a clear next single revision (at most one).
- **Negative:** U fails LLM-only gates and harms overall Purist or inflates
  false abstention / vague-`multiple` collapses.
- **Reject:** `test450` or Real(300) inspection; kitchen-sink merge with Luna
  B/C without a predeclared follow-up; replacing frozen six-model v0.5.

## Run commands

```powershell
# A — reuse retained v0.5 DeepSeek raws through current hybrid_full_stack (done once)
.venv\Scripts\python.exe scripts\run_gan2026_deepseek_unknown_prompt_dev750.py run --variant A_v05_control

# U pilot — gold Purist-UNK band only (170 rows); resume-safe into the same artifact
.venv\Scripts\python.exe scripts\run_gan2026_deepseek_unknown_prompt_dev750.py run --variant U_deepseek_unknown --row-ids-file configs/gan2026/deepseek_unknown_heavy_slice_dev750_20260731.json

# U full — remaining non-UNK rows after the pilot (750 total)
.venv\Scripts\python.exe scripts\run_gan2026_deepseek_unknown_prompt_dev750.py run --variant U_deepseek_unknown

.venv\Scripts\python.exe scripts\run_gan2026_deepseek_unknown_prompt_dev750.py status
.venv\Scripts\python.exe scripts\run_gan2026_deepseek_unknown_prompt_dev750.py finalize
```

Unknown-heavy slice definition:
[configs/gan2026/deepseek_unknown_heavy_slice_dev750_20260731.json](../../../configs/gan2026/deepseek_unknown_heavy_slice_dev750_20260731.json)
(`gold_monthly_frequency == 1000`, n=170).

## Claim boundary

Hosted DeepSeek development evidence for A versus U. Not local-route evidence,
not Real(300), not six-model panel rewrite.
