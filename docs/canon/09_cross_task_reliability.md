# 09 — Cross-Task Reliability

Last updated: 2026-07-01

**Structural canon slot:** reliability evidence that spans Gan and ExECTv2.

---

## Project reliability thesis

Primary question: where does **confident over-reading** live, and can
forward-observable signals route it without gold?

Vocabulary and success criteria: [`docs/design/reliability_thesis.md`](../design/reliability_thesis.md).

The Wall (Gan) and gold-quality ceiling (ExECT) are **distinct mechanisms** —
see [`05_ceilings_wall.md`](05_ceilings_wall.md).

---

## Cross-task component ablation (2026-06-27)

`docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`:

| Component | ExECTv2 dev140 Δ | Gan validation750 Δ |
| --- | ---: | ---: |
| `evidence_validation` | 0.0000 | 0.0000 |
| `standard_dictionary` | +0.0389 | +0.0293 |

**Manuscript (C2):** Shared format layers carry cross-task dividend; evidence gate
is inert on both tasks.

---

## ExECT self-consistency / entropy (2026-06-25)

Lean candidate: `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`.

| Panel | Rows | Exact agreement | Mean entropy | Notes |
| --- | ---: | ---: | ---: | --- |
| **entropy_dev140_temps** (primary) | 140 | **0.8857** | **0.1905** | Temps 0.3–1.0; semantic stability |
| hard50_temp0 | 50 | 0.9217 | 0.1261 | Temp-0 reproducibility |
| smoke1_temp0 | 1 | 0.7500 | 0.2500 | Pipeline smoke only |

**Interpretation:** High agreement does not imply correctness — unanimous-but-wrong
cells are the ExECT analogue of Gan's confident residual. Majority 4/4 accuracy
0.7925; 3/4 bucket only 0.3529.

Full workstream canon: [`workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md`](workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md).

---

## Trust annex (closeout)

From [`07_exect_plan11.md`](07_exect_plan11.md) § Reliability annex:

| Dimension | Result | Deployment read |
| --- | --- | --- |
| Calibration ECE | 0.0432 | Shallow (Brier Δ 0.0142) |
| Review routing | 97% burden / 90% catch | Review-nearly-everything |
| Robustness hard-slice | F1 0.8336 | Passed |
| Wall transfer (ExECT SF) | 6/9 checks | Suggestive, small-n |

---

## Related reading

- [`06_gan_clinical_policy.md`](06_gan_clinical_policy.md) — Gan reliability programs  
- [`07_exect_plan11.md`](07_exect_plan11.md) — full-200 frozen aggregates  
- [`10_paper_provenance.md`](10_paper_provenance.md) — C3, C5 claim boundaries  
