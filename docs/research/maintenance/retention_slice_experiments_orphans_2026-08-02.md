# Decision 0048 retention slice: experiments/ tier-1 orphans

Date: 2026-08-02  
Status: **deleted**  
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md) broader corpus triage  
Inventory: unreferenced experiments explore (337 tracked files under
`experiments/` + `docs/experiments/`)

## Deleted

| Path | Reason |
| --- | --- |
| `experiments/assets/pipeline_flow/exectv2_modular_trace.png` | Early pipeline-flow PNG; superseded by live frontend + generated architecture |
| `experiments/assets/pipeline_flow/gan_temporal_reconstruction.png` | Same |
| `experiments/assets/pipeline_flow/` and `experiments/assets/` | Removed when empty |
| `experiments/exectv2_luna_prompt_variants_dev140_20260731/panel_joint_archived.jsonl` | Archived joint panel; active `panel.json` / summary retained |
| `experiments/exectv2_luna_prompt_variants_dev140_20260731/panel_summary_joint_archived.json` | Same |
| `experiments/exectv2_luna_prompt_variants_test60_20260731/panel_joint_archived.json` | Same |
| `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_vs_20260715.json` | Superseded duplicate; canonical is `*_vs_20260715_current_rules.json` |
| `experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715_structured.pre_ctx_retry.jsonl` | Retry backup; primary structured JSONL retained |

None appear in `retained_evidence_manifest.json` or as registry selected
artifacts. Recovery: Git history.

## Deferred (judgment)

- ~25–30 intermediate six-model scoring-lane JSONL files (may be needed for
  no-call lane replay; audit scripts before batch delete).
- Unreferenced aggregate JSON summaries without script wiring.
- Protocol docs outside the machine manifest that still own focused evidence
  threads (DeepSeek, Luna, holdout stubs).

## Verification

```powershell
.venv\Scripts\python.exe scripts\check_retained_evidence_manifest.py
```
