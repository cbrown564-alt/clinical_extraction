# P0.4 — Robustness Index + Invariance Flip-Rate

Date: 2026-06-17  ·  Model calls: 0

Robustness index = `mean(overall_pass, minimal_pair_consistency, 1 - max(0, quantify_minus_unknown_gap))` (equal weights, predeclared).

| Candidate | A | B | C | Overall | Min-pair consistency | Overfit gap | **Index** |
|---|---:|---:|---:|---:|---:|---:|---:|
| direct_labeler_v0_5 | 8/12 | 5/7 | 7/8 | 20/27 (74%) | 2/6 (33%) | +0.43 | **0.547** |
| evidence_v0_6 | 9/12 | 5/7 | 8/8 | 22/27 (81%) | 3/6 (50%) | +0.23 | **0.694** |
| evidence_v0_7 | 12/12 | 7/7 | 8/8 | 27/27 (100%) | 6/6 (100%) | +0.00 | **1.000** |

_Panel B/C cases are standalone (pair=null); a literal original<->perturbed paraphrase flip-rate is not computable from the saved artifact. Panel-A flip_to_overfit_rate is the available invariance signal; true paraphrase flip-rate on real rows is P2.3 (budgeted)._

---

**Reading.** The index ranks the candidates the same way the binary `transfers` verdict did, but on a continuum: the overfit gap (quantify-side minus unknown-side accuracy) is the single most diagnostic leg — a positive gap is the over-reading signature, and it is exactly what flagged the v0.6 evidence variant overfit before it scored 351/450 on frozen test. A high OOD pass rate with a large overfit gap (the v0.7 pattern) shows panel pass is necessary but not sufficient.
