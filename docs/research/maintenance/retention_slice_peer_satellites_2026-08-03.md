# Decision 0048 retention slice: peer-satellite documentation cull

Date: 2026-08-03  
Status: **5 peer satellites deleted** after living-cited rebinds  
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md)  
Prior: [documentation corpus slice](retention_slice_documentation_corpus_2026-08-03.md)

## Method

1. Rebind living-cited synthesis pages and canon workstream links off satellite
   reports.
2. Delete docs that then had no living-owner citation and no hard caller
   (script, test, config, or machine-artifact protocol/report field).

## Rebinds

| Living-cited or owner surface | Change |
| --- | --- |
| `docs/research/six_model_comparison_report_2026-07-18.md` | Dropped projection-floor report link; dated-count + replay remain |
| `docs/research/why_the_error_floor_persists_2026-07-31.md` | Evidence owners point at Luna summary, dated-count, machine dirs |
| `docs/research/gan2026_luna_prompt_variants_report_2026-07-30.md` | Residual follow-up cites dated-count + comparison, not residual report |
| `docs/canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md` | Audit substrate → machine JSON artifact |
| Gan floor protocols | Parent/absorbed links retargeted to living-cited Luna/dated-count owners |

## Deleted

| Path | Reason |
| --- | --- |
| `docs/research/gan2026_luna_projection_antiregression_floor_report_2026-07-31.md` | Satellite after rebind; protocol + replay JSON remain |
| `docs/experiments/exectv2/reliability/exectv2_deepseek_v4_flash_0731_holdout_rerun_protocol_2026-07-31.md` | No living owner or hard caller |
| `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_interpretation_audit_protocol_2026-07-14.md` | Canon retargeted to machine JSON |
| `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_interpretation_audit_substrate_results_2026-07-14.md` | Same |
| `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_resolution_protocol_2026-07-14.md` | No living owner or hard caller |

Recovery: Git history.

## Explicitly kept

- `docs/research/gan2026_luna_prompt_variants_residual_analysis_2026-07-31.md` and
  its protocol: machine artifact
  `experiments/gan2026_luna_prompt_variants_dev750_20260730/residual_summary.json`
  names both paths.
- Projection and dated-count **protocols**: named by machine replay/protocol
  fields or still supporting the absorbed-floor story after parent rebinds.
- Quarantined Qwen/Sol research reports: hard-called by analyze scripts.

## Retained-evidence update

`docs/research/six_model_comparison_report_2026-07-18.md` is a retained
artifact. After the owner-link rebind, its fingerprint in
`docs/experiments/retained_evidence_manifest.json` was updated to the new
canonical LF hash/size. No clinical scores or selected reference cells changed.

## Deferred

- Broader protocol cull for absorbed studies that lack machine protocol fields.
- README currency pass.
- Thinning ACTIVE_ROADMAP completed-section evidence links (still living-owner
  keep-alives for closed Luna/error-floor owners).
