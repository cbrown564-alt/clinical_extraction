# Restore sealed holdout ledgers for category cuts

Date: 2026-08-06  
Status: complete on this checkout — sealed trees present; bucket arms unlocked  
Parent study: [holdout category aggregates](../research/shared/six_model_holdout_category_aggregates_2026-08-06.md)  
Unlock protocol: [blocked-arm unlock](../research/shared/six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md)

## Why this note exists

The sealed holdout category-aggregates study answered ExECT `test60` **family**
lenses from public panels. Gan `test450` **a_priori bucket** scores and ExECT
**letter-bucket** scores needed gitignored prediction ledgers under `scratch/`.

This runbook records how to restore those ledgers and finish Phase-C-style
machine-only scoring. It does not authorize human inspection of locked rows.

## What “Phase-C style” means here

Follow the Decision 0046 Phase C **pattern** (see
[primary-method surface protocol](../experiments/exectv2/reliability/exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)):

- the machine may read sealed holdout predictions and locked gold to score;
- public `experiments/` / docs outputs must stay aggregate-only;
- no letter IDs, `source_row_index`, notes, predictions, or failure examples
  may leave `scratch/`.

This is **not** a re-run of the already-complete ExECT rules-only Phase C
artifact.

## Current machine status (2026-08-06)

On this checkout (`clinical_extraction`):

- `scratch/holdout/` is **present**
- `scratch/local_queue/` holdout trees are **present**
- Minimum Gan hybrid / llm-only / ExECT sealed ledgers are present
- ExECT stage-panel aggregate SHA-256 pointers **HASH_OK**
- Bucket arms unlocked via
  `scripts/build_six_model_holdout_category_aggregates.py` under the unlock
  protocol (machine-only scoring; no public row content)

`docs/REGENERATION.md` notes that governed `scratch/` holdout locations were
not deleted during cleanup. If another machine lacks these trees, copy from a
backup of this disk or another holdout machine that retained them.

## Minimum trees to restore

Prefer a full copy of `scratch/holdout/` and `scratch/local_queue/`. Minimum
for unlocking the blocked category-cut arms:

### Gan hybrid `test450` (a_priori × llm_with_rules)

| Path |
| --- |
| `scratch/holdout/gan2026_matched_v05/gpt41mini/rows.jsonl` |
| `scratch/holdout/gan2026_matched_v05/gpt56luna/rows.jsonl` |
| `scratch/holdout/gan2026_matched_v05/gpt56sol/rows.jsonl` |
| `scratch/holdout/gan2026_matched_v05/deepseek_v4_flash/rows.jsonl` |
| `scratch/holdout/gan2026_matched_v05_local/qwen36_35b/rows.jsonl` |
| `scratch/holdout/gan2026_matched_v05_local/gemma4_26b/rows.jsonl` |

Pointer owner:
`experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json`
(`test450_aggregate.*.source_artifact`). Hybrid bucket scoring no-call replays
these raw outputs through current `hybrid_full_stack` and fidelity-checks
`after_purist`.

### Gan llm-only `test450` (a_priori × llm)

| Path / root |
| --- |
| `scratch/holdout/gan2026_six_model_llm_only_test450_20260801/{slug}/` |
| DeepSeek separate root recorded in `configs/gan2026/six_model_llm_only_test450_20260801.json` |

### ExECT `test60` (letter-bucket × surface)

| Path / root |
| --- |
| `scratch/holdout/exectv2_test60/{slug}/` (hosted) |
| `scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol/` |
| `scratch/local_queue/qwen36_35b_exect/test60/` |
| `scratch/local_queue/gemma4_26b_exect/test60/` |

Hash pointer owner:
`experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json`
(`aggregate_source.local_path` / `sha256`). Broader inventory:
`experiments/hosted_holdout_panels_20260715.json`, `configs/holdout/*.json`.

## Checklist on the other machine

1. Confirm the sealed trees still exist:
   ```bash
   ls -la scratch/holdout | head
   ls -la scratch/local_queue | head
   ```
2. Confirm the minimum Gan hybrid `rows.jsonl` files above are present.
3. Confirm ExECT aggregate JSON files still match recorded SHA-256 values when
   practical (stage panel / hosted panel).
4. Copy or rsync into the target repo root **without opening row JSONL for review**.
5. On the target machine, re-check presence only (path exists / hash), not row
   contents.
6. Run `scripts/build_six_model_holdout_category_aggregates.py` under the unlock
   protocol; confirm fidelity gates and
   `scripts/check_locked_aggregate_safety.py`.

## After restore: scoring gate

1. Predeclare a short extension protocol (blocked-arm unlock only).
2. Score gold buckets × sealed predictions in-process.
3. Emit public aggregates only; keep the artifact in
   `scripts/check_locked_aggregate_safety.py`.
4. Cross-check overall Purist / clinical-headline against existing panels
   before trusting bucket tables.
5. Update the holdout category-aggregates report and `PROJECT_STATUS.md`.

Completed on this checkout 2026-08-06.

## Hard boundaries

| Allowed | Not allowed |
| --- | --- |
| Copy sealed trees under `scratch/` | Commit sealed trees to Git |
| Machine-only aggregate scoring | Human failure analysis of test rows |
| Public bucket × model tables | Examples, notes, predictions in docs |
| Hash / overall-panel fidelity checks | Tuning repairs or prompts from holdout |

## If the sealed trees are gone

Do not invent per-bucket holdout scores from overall panels. Leave the Gan
a_priori / ExECT letter-bucket arms blocked and keep the family-level holdout
lenses already published.

## Owners

- Study: [holdout category aggregates](../research/shared/six_model_holdout_category_aggregates_2026-08-06.md)
- Unlock protocol: [blocked-arm unlock](../research/shared/six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md)
- Pattern precedent: [Decision 0046 Phase C](../experiments/exectv2/reliability/exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)
- Safety checker: `scripts/check_locked_aggregate_safety.py`
- Scratch policy: [REGENERATION.md](../REGENERATION.md), root `.gitignore` (`scratch/*`)
