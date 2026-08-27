# Development six-model trees for the workbench

The explorer reads **development** six-model trees from `experiments/`,
not from `scratch/`. Holdout trees stay in `scratch/holdout/` and
`experiments/current_stack/sidecars/` and are not served as row-level
replay.

## Gan `dev750`

`frontend/components/architect/TraceControls.tsx` disables an option when
`availability === "not_retained"`.

The API sets that flag when a condition fails completeness in
`src/clinical_extraction/trace_explorer/gan2026_comparison.py`: missing
file, wrong row count, index mismatch, or missing
`gan2026.row_trace.v1` traces.

- Config:
  `configs/gan2026/six_model_validation_comparison_20260718.json`
- Hybrid and LLM-only `dev750` row forests were removed in the 16 Aug
  living-stack freeze. The picker still lists the six successor models;
  availability is `not_retained` until a new development tree is bound.
  Recover the 13 Aug / 18 July forests from Git history for a local demo.

Slugs: `gpt56luna`, `gemini37flash`, `gpt56sol`, `deepseek_v4_flash`,
`qwen36_35b`, `gemma4_26b`. Methods: `llm_with_rules`, `llm_only`.
GPT-4.1-mini remains a historical artifact and is not in the picker.

A cell is replayable only if the file is a real JSONL payload (not a
Git LFS pointer), has exactly 750 validation rows, and every row carries
`gan2026.row_trace.v1` with `method` matching the cell.

Hybrid answers are the 13 Aug current-stack no-call replay through HEAD
repairs. They are not the July 18 saved finals. LLM-only stays on the
July 18 tree.

## ExECT `dev140`

ExECT is a separate catalog, not the Gan pipeline picker.

- Source package:
  `experiments/exectv2_six_model_single_call_{slug}_dev140_20260715.json`
  (Gemini 3.7 Flash uses the 20260813 successor package)
  and the matching `.jsonl` (plus `_structured.jsonl` sidecars)
- Compact frontend projection:
  `frontend/public/mock-data/exectv2/runs.json`
- Builder:
  `python scripts/build_trace_explorer_exectv2_comparison.py`

The catalog is 12 model cells (six models × `llm_with_rules` / `llm`)
plus live `rules`. DeepSeek in this July 15 package is the pre-0731
cell. Holdout ExECT stays under `scratch/holdout/` and
`experiments/current_stack/sidecars/exect_test60/`.

Rebuild the projection only after the source package changes:

```powershell
.venv\Scripts\python.exe scripts/build_trace_explorer_exectv2_comparison.py
```

## Check

From the repository root:

```bash
# Living ExECT assembly files used by the catalog
for slug in gpt56luna gemini37flash gpt56sol deepseek_v4_flash qwen36_35b gemma4_26b; do
  if [ "$slug" = "gemini37flash" ]; then
    p="experiments/exectv2_six_model_single_call_${slug}_dev140_20260813.jsonl"
  elif [ "$slug" = "deepseek_v4_flash" ]; then
    p="experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.jsonl"
  else
    p="experiments/exectv2_six_model_single_call_${slug}_dev140_20260715.jsonl"
  fi
  if [ -f "$p" ]; then
    n=$(wc -l < "$p" | tr -d ' ')
    echo "EXECT PRESENT  ${n}  ${p}"
  else
    echo "EXECT MISSING              ${p}"
  fi
done

# Living holdout remasure inputs
python scripts/run_current_stack.py check
```

## Related

- Workbench start: [frontend/README.md](../../frontend/README.md)
- Current-stack replay procedure:
  [current_stack_six_model_replay.md](current_stack_six_model_replay.md)
