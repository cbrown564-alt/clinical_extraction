# ExECTv2 SF Verify — Phase 5 result: feedback + demos lift LLM-only SF to a new best (0.784), gate not cleared (2026-06-29)

**Branch:** `exectv2-gepa-single-model-plateau-2026-06-28`.
**Scope:** the LLM-only GEPA route on SeizureFrequency, WITHOUT the deterministic SF
projection fallback (`sf_state_projection.py` / `rules/change.py`). The lever is feedback
precision (per-(type,state) diff, four error-class reasons) + reasoner extraction + hand-curated
demos. Scoring is unchanged from P2 so any lift is attributable to feedback/demos/model, not the
metric. Final eval is full dev140; the frozen test split is untouched.

Predecessors / context:
- Handoff + audit: `exectv2_sf_verify_phase5_handoff_2026-06-29.md`.
- Error analysis (motivation): `exectv2_sf_verify_error_analysis_2026-06-29.md`.
- Metric: ADR `0037-sf-state-profile-is-primary-clinical-metric.md` (`state_profile` primary).
- Plan: `docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` §5.

## 1. Results (full dev140, LLM-only, no deterministic projection)

| run | extract→verify | examples | state_profile F1 | (P / R) | clinical_headline F1 | changed R/P |
| --- | --- | --- | ---: | --- | ---: | --- |
| `…p5_reasoner_reasoner_fb` | reasoner→reasoner | no | 0.743 | 0.67 / 0.83 | 0.560 | 0.56 / 0.48 |
| `…p5_reasoner_mini_fb` | reasoner→mini | no | 0.766 | 0.71 / 0.83 | 0.587 | 0.52 / 0.54 |
| **`…p5_reasoner_reasoner_ex`** | **reasoner→reasoner** | **yes** | **0.784** | **0.78 / 0.79** | 0.586 | 0.56 / 0.56 |
| `…p5_reasoner_mini_ex` | reasoner→mini | yes | 0.766 | 0.71 / 0.83 | 0.608 | 0.63 / 0.57 |

Comparators (same `score_frequency_state` / full-dev140 path):
P2 mini **0.741** / 0.597 · recall-lanes 0.710 / 0.580 · Phase 3b **with** deterministic
projection 0.779 / 0.650 · v08 hybrid **0.930** / 0.926 (changed 0.85R/1.00P).

Seeds (attributing the demo contribution): the `fb` seeds score state_profile ~0.662; the `ex`
seeds (same instructions, + demos) score 0.713 (reasoner) / 0.688 (mini) — **demos add ~+0.05 at
the seed before any optimization.**

## 2. Verdict against the gate

**Gate (plan §5): `state_profile ≥ 0.80` AND `clinical_headline SF ≥ 0.65` — NOT MET.**
Best state_profile 0.784 (< 0.80); best clinical_headline 0.608 (< 0.65).

**Feedback-lever bar (`state_profile ≥ 0.771`, +0.03 over P2's 0.741): cleared by ONE arm.**
Only `reasoner_reasoner_ex` (0.784) clears it. The feedback redesign **alone** (the `fb` arms,
no demos) fell just short — best `fb` is `reasoner_mini_fb` at 0.766 (= +0.025). The +0.03 lift
required the hand-curated demos on top of the feedback.

**New LLM-only SF best = 0.784**, +0.043 over P2 (0.741), and **edging past the Phase 3b line
that needed the deterministic SF projection (0.779)** — i.e. the LLM-only route now reaches, on
its own, what previously required the deterministic change/projection rules. Still ~0.15 below
the hybrid (0.930): the plateau is real and architectural.

## 3. What moved the number

1. **Demos are decisive for reasoner-verify, inert for mini-verify.** reasoner→reasoner: `fb`
   0.743 → `ex` **0.784** (+0.041). reasoner→mini: `fb` 0.766 → `ex` 0.766 (no change at the
   optimized level; demos only lifted its *seed*). Clean split — the reasoner needs concrete
   convention examples to discipline its over-reasoning (exactly what the error analysis §6
   predicted); gpt-4.1-mini already follows the GEPA-evolved instructions without them.
2. **The gain is precision, earned legitimately.** The winner's evolved verify instruction adds
   confirmed-epilepsy gating (Cat B), historical-vs-current discipline (Cat C: "do not include
   the very first seizures that led to a new diagnosis as a current rate"), the FC=Same boundary
   (Cat A-FP: "do not use `changed` for 'well controlled' unless it indicates a change"), and
   standard-term type naming. Precision 0.67→0.78 for a modest recall cost 0.83→0.79.
   **Audited:** none of the four selected instructions contains the destructive "only emit a
   frequency_rate if the letter states a change" rule that the reasoner-verify reflection proposed
   during the smoke — GEPA's valset gate rejected it (0.729 < base 0.767) and it never reached a
   selected program. The winner's one rate-exclusion rule is the legitimate Cat-C temporal one.
3. **The changed class improved but remains the drag.** All four arms beat P2's changed 0.473 F1;
   best is `reasoner_mini_ex` at 0.63R/0.567P. Still far from the hybrid's 0.85R/1.00P — the
   change class is the residual gap, as in every prior SF analysis.
4. **Pre-run prior was half right.** Expectation was reasoner→mini would win (mini = better keyer).
   Actual: **mini-verify > reasoner-verify *without* demos** (0.766 vs 0.743), but
   **reasoner-verify > mini-verify *with* demos** (0.784 vs 0.766). Demos flip the ranking.

## 4. Interpretation

Phase 5 is a **partial success**: it set a new LLM-only SF `state_profile` best (0.784), cleared
the +0.03 feedback-lever bar (with demos), and crossed the Phase-3b-with-projection line — but it
did **not** clear the 0.80 / 0.65 gate. Even with reasoner chain-of-thought + per-(type,state)
feedback + hand-curated demos, the LLM-only 2-stage generate→verify program **plateaus ~0.78
state_profile, ~0.15 below the hybrid's 0.930.**

This corroborates the standing synthesis (evidence-decomposition memo, 2026-06-28): the remaining
gap is **evidence retrieval / multi-lane extraction, not feedback precision or determinism.** A
single multi-purpose extract→verify pass — however well-instructed — surfaces less than the
hybrid's focused per-family producers. Closing the rest of the SF gap needs either the
deterministic SF projection (the explicit Phase 5 scope boundary; Phase 3b reached 0.779 with it)
or a genuinely multi-lane LLM extraction architecture, not more instruction/feedback/demo tuning.

## 5. Recommendation

- **Adopt `reasoner_reasoner_ex` as the LLM-only SF reference** (0.784 state_profile): it is the
  new best and proves the LLM-only route reaches the deterministic-projection line unaided.
- **For a deployable SF number, keep the deterministic SF projection** (Phase 3b, 0.779/0.650
  with projection; combine with this verifier's recall and the projection's change-class precision
  for the likely ceiling of the focused-lanes approach).
- **Do not invest further in single-pass SF feedback tuning** — the 0.78 plateau is firm across
  fb/ex × reasoner/mini. The next real lever on SF is architectural (multi-lane), per the
  closing-campaign multi-stage scope doc.

## 6. Artifacts

Per arm (`experiments/exectv2_gepa_sf_verify_p5_{reasoner_reasoner,reasoner_mini}_{fb,ex}_20260629`):
`.json` (summary + comparators), `.jsonl` (140 per-letter preds), `.instruction.txt` (evolved
generate+verify). GEPA logs under `experiments/gepa_overnight_exectv2/<run_id>/`. Driver log:
`experiments/gepa_overnight_exectv2/_full_driver_20260629.log`. Launcher:
`experiments/gepa_sf_verify_phase5_exectv2.py`; orchestrator: `experiments/run_sf_verify_phase5_matrix.ps1`.
Runtimes: 17–45 min/arm (reasoner extraction dominates). Registry registration still skipped by
the malformed `experiments/registry.jsonl:63` (artifacts written regardless).
