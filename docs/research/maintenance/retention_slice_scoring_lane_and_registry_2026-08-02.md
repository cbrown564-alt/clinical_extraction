# Decision 0048 retention slice: scoring-lane JSONL + mock registry paths

Date: 2026-08-02  
Status: **applied**  
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md) broader corpus triage

## Scoring-lane / two-call orphans deleted (~99 MB)

### Intermediate `*_sf_structured_direct.jsonl` (10 files)

Zero script/config/authority inbound refs. Intermediate SF lane before
projection/suppression; regenerable from producer structured outputs when a
new study needs them.

### Pre–Decision-0041 two-call package (gpt41mini + Luna)

Deleted raw `.jsonl`, lane JSONL, companion root `.md`, and aggregate `.json`.
Authority reports were already removed in the orphan-docs slice; manifest keeps
the `*_single_call_*` variants only. Allowlist entries removed from
`scripts/doc_hygiene_experiments_root_allowlist.txt`.

### Orphan non-`single_call` structured JSONL (2 files)

`exectv2_six_model_{deepseek_v4_flash,gpt56sol}_dev140_20260715_structured.jsonl`
had no inbound refs; selected six-model replay uses `*_single_call_*_structured.jsonl`.

## Kept (wired)

- Manifest primary `*_single_call_*.jsonl`
- Selected `*_structured.jsonl` and `*_sf_unknown_suppression.jsonl` cited by
  configs, joint-policy replay, DeepSeek/Luna studies, and parity tests
- `*_sf_state_projection_combined.jsonl` + allowlisted companion `.md` for
  selected single-call / DeepSeek packages

## Mock registry `artifact_paths`

Retargeted five historical runs whose `experiments/` / config paths were missing
to the served copies under `frontend/public/mock-data/artifacts/`:

- `gan2026_rules_only_v1_baseline_2026-05-31`
- `exectv2_holistic_finding_assembly_v08_dev140`
- `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140`
- `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140`
- `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140`

Left `…_p7fix_gpt41mini_20260702` pointing at existing `experiments/` /
`configs/` retained-evidence paths.

Frontend selectors now treat `mock-data/artifacts/*.json` as replayable via
`frontend/lib/registryArtifacts.ts` (not only `.jsonl`).

## Verification

```powershell
.venv\Scripts\python.exe scripts\check_retained_evidence_manifest.py
.venv\Scripts\python.exe -m pytest tests/test_trace_explorer_frontend_api.py -q
Set-Location frontend; npm test -- --runInBand --testPathPattern="registryResolver|ganPipelineOptions|exectv2RunOptions"
```
