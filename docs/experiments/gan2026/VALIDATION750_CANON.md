# Gan Validation750 Workstream Canon

Last updated: 2026-07-01

**Scope:** Reset-thread validation750 verifier iteration (v6 cluster, June 2026).
**Claim boundary:** Validation-development only — not benchmark-comparable, not
holdout promotion.

**Parent canon:** [`docs/canon/06_gan_clinical_policy.md`](../../canon/06_gan_clinical_policy.md)  
**Long tail:** 31 files in [`validation750/`](validation750/) (stubbed; detail retained)

---

## What this workstream tested

After the architecture reset, the validation750 surface became the primary
**stage-owned hybrid** development ladder: clinical assessment → projection →
render → routed verifier actions. The v6 thread asked:

1. Does a **first verifier** improve Purist accuracy without changing coverage?
2. Should verifier policy be **action-only** or **forced-choice**?
3. Which **deterministic projection rules** (cluster cadence, YTD denominator) are
   safe to promote?
4. Do **HN1 null-reduction** slices improve proxy null-render burden?

---

## Top-line outcome (pre → post)

From [`validation750/gan2026_validation750_pre_post_comparison_2026-06-07.md`](validation750/gan2026_validation750_pre_post_comparison_2026-06-07.md):

| Surface | Pre baseline | Saved post-task |
| --- | ---: | ---: |
| Purist correct (scored) | 488 | **504 (+16)** |
| Purist accuracy (scored) | 84.14% | **86.90%** |
| Pragmatic correct | 520 | 527 (+7) |
| Rendered / null / scored rows | 580 / 170 / 580 | **unchanged** |

Coverage stable; gains are **narrow label corrections**, not new renders.

### Promoted rules (visible aggregate)

| Rule | Rows touched | Purist W→C | Purist C→W |
| --- | ---: | ---: | ---: |
| `cluster_cadence_default_multiple_per_cluster_v0` | 30 | 13 | 3 |
| `date_anchored_ytd_denominator_v0` | 8 | 6 | 0 |

Fresh workspace replay (498 Purist correct) confirms saved bundle is reproducible
within small drift — not a promotion artifact.

---

## Verifier policy decision

From [`validation750/gan2026_validation750_verifier_action_policy_decision_v6_2026-06-06.md`](validation750/gan2026_validation750_verifier_action_policy_decision_v6_2026-06-06.md):

**Decision:** Primary policy is **`action_only`** (affirm / reject / abstain /
human_review / escalate).

**Forced choice** retained as diagnostic only — it selects prediction-bearing
candidates on ambiguous routed rows and crosses the reset boundary the thread
was trying to preserve.

Action-only run (clean 56-row surface): 56/56 parseable; main ambiguity outcomes
include human_review and abstain buckets — operationally clean.

---

## Component ablation (v6 surface)

First component ablation on validation750 v6 (`first_component_ablation_table_v6`,
`first_component_ablation_report_surface_v6`): documents which hybrid components
move Purist vs pragmatic lines on the reset pipeline. Use alongside
[`COMPONENT_MECHANICS_CANON.md`](COMPONENT_MECHANICS_CANON.md) for RQ cross-links.

---

## Null reduction & HN1 slices

| Phase | Doc | Role |
| --- | --- | --- |
| Baseline proxy slices | `null_reduction_slices_baseline_2026-06-07.md` | Pre-HN1 null-render burden |
| After HN1 multimonth | `null_reduction_slices_after_hn1_multimonth_*.md` | Contract evaluation |
| HN1 recovery reads | `hn1_frequency_value_recovery_slice_read`, month-bucket eval | Frequency-value recovery mechanics |

These are **proxy slice** evaluations — guide rule promotion, not holdout claims.

---

## Incident & operational notes

- **Extraction cache/resume incident** (`extraction_cache_resume_incident_2026-06-06.md`) — replay hygiene; does not change aggregate conclusions when recovered artifacts used.

---

## Artifact pointers (machine)

| Artifact | Role |
| --- | --- |
| `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0.json` | Pre baseline |
| `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.json` | Saved post-task |
| `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_current_compare_2026-06-07.json` | Fresh replay |

Registry rows may cite sibling paths under `experiments/gan2026_*` — grep registry
for `validation750` when reproducing.

---

## How to read the 31-file bucket

| Category | Files (approx) | Read canon section |
| --- | ---: | --- |
| Pre/post + policy decisions | 3 | Top-line, Verifier policy |
| First verifier live/saved/input variants | 8 | Verifier policy (diagnostic duplicates) |
| Component ablation + accounting | 4 | Component ablation |
| Null/HN1 slices | 6 | Null reduction |
| Taxonomies + diagnostics | 10 | Long tail — open only for row-level audit |

**Start here** instead of reading slice readouts sequentially.

---

## Related reading

- [`COMPONENT_MECHANICS_CANON.md`](COMPONENT_MECHANICS_CANON.md) — RQ1–RQ10 answers
- [`docs/canon/06_gan_clinical_policy.md`](../../canon/06_gan_clinical_policy.md) — promoted SE vs hybrid ceiling
- [`docs/THREAD_MAP.md`](../../THREAD_MAP.md) T1 long tail
