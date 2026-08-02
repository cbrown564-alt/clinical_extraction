# Decision 0048 retention slice: ExECT candidate config trees

Date: 2026-08-02
Status: closed audit
Owner: Decision 0048 bounded cleanup
Scope: `configs/exectv2/model_swap/`, `configs/exectv2/diagnosis_ablation/`,
`configs/exectv2/finding_assembly/` (excluding `six_model_comparison/`)

## Method

Traced every tracked file in the three directories against:

1. `docs/experiments/retained_evidence_manifest.json` (architecture freeze,
   reference cells, evidence packages)
2. Six reference-cell replay closures
3. Active `configs/exectv2/six_model_comparison/` configs (read-only; not edited)
4. Architecture manifests under `src/clinical_extraction/architecture/manifests/`
5. Replay and check scripts under `scripts/`
6. Focused tests under `tests/`
7. Runbooks under `docs/runbooks/`
8. Git history for files already removed from `main`

Historical decision or experiment markdown that merely mentions a path was not
treated as a keep signal unless a replay, check, test, or manifest closure still
loads the file.

## Outcome

No additional deletions in this slice. `main` already retains exactly five config
files across the three trees; each has at least one live replay, check, test, or
manifest reference. Seventy-nine sibling candidate configs were removed in earlier
commits (`8d808656`, `99809443`) before this audit.

## Deleted in this slice

None. Prior removals documented below for recovery context.

### Previously removed (not present on `main` at audit time)

| Path | Removed in | Why safe then |
| --- | --- | --- |
| 74 files under `configs/exectv2/finding_assembly/` (v01–v099 iteration manifests, hybrid variants, DeepSeek/Qwen compact trials) | `8d808656` | Closed candidate family; no retained-evidence manifest, reference-cell, or focused-test closure |
| `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_gpt41mini_full200.json` | `99809443` | Aggregate-only full-200 predeclaration; not in manifest dev140 replay closure |
| `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_deepseek_full200.json` | `99809443` | Same |
| `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200.json` | `99809443` | Same |
| `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_dev140.json` | `99809443` | Superseded by repair v02 config retained in manifest |
| `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_repair_v01_dev140.json` | `99809443` | Superseded by repair v02 config retained in manifest |

Experiment JSON under `experiments/` may still name removed full-200 or v01 paths
as historical metadata; those artifacts are replay-only records, not config loaders.

## Kept files (current `main` inventory)

### `configs/exectv2/finding_assembly/`

| File | Action | Reference evidence |
| --- | --- | --- |
| `exectv2_holistic_finding_assembly_v08_p7_dev140.yaml` | **KEEP** | Listed in `retained_evidence_manifest.json` architecture freeze and `exectv2_hybrid_reference` reference cell; `verification.inputs.path` for no-call replay; `tests/test_retained_evidence_manifest.py::test_hybrid_reference_manifest_keeps_all_finding_assembly_inputs`; governing tests in `exectv2_llm_with_rules.json` manifest; producer closure via `run_finding_assembly.py` |

### `configs/exectv2/model_swap/`

| File | Action | Reference evidence |
| --- | --- | --- |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140.json` | **KEEP** | `retained_evidence_manifest.json` architecture freeze + `exectv2_model_transfer_subject` package; `tests/test_retained_evidence_manifest.py::test_model_transfer_package_keeps_permitted_dev_replay_inputs`; `scripts/run_exectv2_2call_model_swap.py`; `src/.../reports/model_swap.py` (`DEFAULT_CONFIG_DIR`); LFS replay artifact `experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140_20260625.jsonl` |
| `exectv2_2call_no_sf_adjudicator_deepseek_dev140.json` | **KEEP** | Same manifest and test closure as GPT row; `run_exectv2_2call_model_swap.py`; LFS replay artifact for DeepSeek dev140 |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140.json` | **KEEP** | Same manifest and test closure; repair v02 is the retained Qwen swap identity; LFS replay artifact for Qwen repair v02 dev140 |

### `configs/exectv2/diagnosis_ablation/`

| File | Action | Reference evidence |
| --- | --- | --- |
| `gpt41mini_single_call_dev140.json` | **KEEP** | Not in retained-evidence manifest, but loaded by `scripts/check_exectv2_gpt41mini_single_call_diagnosis_ablation.py` (`CANDIDATE_CONFIG_PATH`); asserted in `tests/test_exectv2_gpt41mini_single_call_diagnosis_ablation.py::test_retained_single_call_config_is_attributable_and_uses_one_model_pass`; experiment record `experiments/exectv2_gpt41mini_single_call_diagnosis_ablation_dev140_20260715.json` |

## Stale path mentions (no keep signal)

These paths appear in frontend mock fixtures or closed experiment JSON but have no
tracked config file and no replay loader:

- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml` — superseded by v08_p7 manifest; mock registry only
- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.yaml` — removed in `8d808656`; mock registry only
- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140.yaml` — removed in `8d808656`; mock registry only
- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140.yaml` — removed in `8d808656`; mock registry only

Cleaning mock registry strings is out of scope for this config-tree slice.

## Verification run

```powershell
.venv\Scripts\python.exe -m pytest tests/test_retained_evidence_manifest.py tests/test_exectv2_gpt41mini_single_call_diagnosis_ablation.py tests/test_exectv2_same_core_model_swap.py -q
.venv\Scripts\python.exe scripts/check_retained_evidence_manifest.py
```

## Recovery

Removed configs remain recoverable from Git history (`8d808656`, `99809443`) if a
named replay study requires them. Do not restore without a predeclared protocol and
manifest update.
