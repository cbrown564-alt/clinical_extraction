# Pipeline assumption audit — Phase 1 scorer fixes (result)

Date: 2026-07-02. Owner: ExECTv2 workstream.
Plan: `docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md` (Phase 1).
Phase 0 inventory: `docs/research/exectv2_pipeline_assumption_audit_2026-07-02.md`.

All measurements are dev140 re-scores of the cached predictions for
`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` (zero new LLM calls).
The replay harness reproduces every previously-cited number exactly before any
fix, validating the instrument: Prescription `clinical_headline` 0.8766,
Investigations 0.8583, SF `clinical_headline` 0.5921 / `state_profile` 0.7127,
Diagnosis raw 0.6617.

## Fixes landed (three of four Phase 1 measurement bugs)

| Bug | File | Before → After | Δ | Character |
| --- | --- | --- | --- | --- |
| **P1/P2/P3** clause-scope future/weight | `scoring/prescription.py` | Rx `clinical_headline` 0.8766 → **0.9073** | **+0.0307** | precision-driven (0.8529→0.9118, fp 30→18) |
| **SF-1** zero-count precedence | `scoring/seizure_frequency.py` | SF `clinical_headline` 0.5921 → **0.5982**; `state_profile` 0.7127 → **0.7200** | +0.0061 / +0.0073 | one variable-rate fact re-routed |
| **I1** modality text-fallback gate | `scoring/investigations.py` | Inv `clinical_headline` 0.8583 → **0.8583** | 0 (latent) | removes an FP *class*, no TP lost |

### P1/P2/P3 — prescription clause-scoping (the seed bug)

`_is_future_medication`/`_is_weight_based_dosing` matched the whole
`annotation.text`, so any gold span bundling a current dose with titration
("75mg bd (to reduce and stop)") or a weight-normalized restatement
("1500mg bd (60mg/kg/day)") was nulled from `clinical_headline`. Inspection of
all 14 gate-excluded gold facts showed **every one carries the current dose in
its structured `DrugDose`/`DoseUnit`/`Frequency` attributes** (not the future
target), and 12/14 matched a model prediction that was consequently mis-scored
as a false positive. The fix truncates the span at the first future/weight cue
and keeps the fact when its current dose survives in that head clause — exactly
the semantics the deterministic convention layer already used
(`deterministic/conventions/prescription.py:266-268`), reconciling the
scorer↔projection scope disagreement the audit flagged. After the fix,
`clinical_headline` (0.9073) matches the `complete` diagnostic (0.9163),
resolving the scorer's internal contradiction (`complete` counted these facts
while `ordinary_complete`/`clinical_headline` dropped them).

Kill criterion (`rx_future_medication_regex_scope_bug_2026-07-02`): met. No new
false positives (fp fell), and `future_medication`/`weight_based_dosing`
diagnostics emptied because no genuine future/weight-only fact exists in dev140 —
so nothing was wrongly kept.

### SF-1 — zero-count precedence

`_frequency_state` tested `any(count == "0")` *before* the positive-count test,
so a variable rate `Lower=0/Upper=3` (EA0121) was labelled `seizure-free`. The
identical bug lived in the twin `frequency_state_faithful` (used by
`state_profile`). Both now route through a shared `_count_based_state` helper
that gives positive counts precedence. Kill criterion
(`sf_zero_count_precedence_2026-07-02`): met — `seizure_free` TP held at 34 (no
genuine seizure-free fact reclassified); only the 0/3 range moved to
`active-rate`, where it matched the model.

### I1 — Investigations modality text-fallback

`_investigation_modality_key` emitted a `(modality, None, None)` headline key
from a bare modality word with no attribute. Because gold Investigations are
always attributed, such a key is structurally FP-only. Gating the fallback on
`≥1 attribute` removes that FP class. This run's predictions contain no
bare-word-only modality spans, so F1 is unchanged — a defensive correctness fix,
not a score mover here. Kill criterion (`inv_text_fallback_fp_only_key_2026-07-02`):
met — no TP lost.

## Held for a decision: D1 (Diagnosis specificity-collapse)

D1 is the fourth Phase-1 measurement bug and the most consequential:
`collapse_diagnoses_to_most_specific` runs independently per side before
intersecting, so gold `[epilepsy]` vs pred `[epilepsy, focal epilepsy]` scores
F1=0 despite the model emitting `epilepsy` verbatim (34/140 dev letters carry a
gold parent+child pair). The audit established that fixing it can only *lower*
Diagnosis's genuine-model-error share — i.e. it reinforces the manuscript's
"85.2% gold-artifact" finding rather than threatening it. But it changes the
matching semantics of the most populous family, which underpins that headline
Diagnosis evidence (adjusted F1 0.6617→0.9501), so it is held pending an explicit
go-ahead and its own predeclared hierarchy-aware-match design rather than folded
in silently. Hypothesis: `dx_specificity_collapse_cross_contamination_2026-07-02`
(OPEN).

## Blast radius (broader than the plan anticipated)

The plan framed Phase 1's downstream impact as "update the Prescription F1
citation." The replay revealed it is larger: the **frontend reliability
scorecard is live-computed from the scorer**, so the prescription fix ripples
into ~100 derived reliability numbers (scoring cells 1706→1719, calibration
proxy ECE/Brier, review-routing, cross-model agreement). Those numbers were all
computed on the buggy scorer too. This splits the affected artifacts into two
kinds:

1. **Derived caches** — regenerate: `frontend/public/mock-data/exectv2/reliability-scorecard.json`
   (sanctioned regenerator: `scripts/build_exectv2_reliability_scorecard_data.py`;
   the `test_static_frontend_scorecard_matches_builder_contract` test is
   currently red *by design*, forcing this regeneration) and the four ledger
   dossiers (`render_dossier.py`). These hold live-computed values, not
   historical citations — regenerating is the intended workflow.
2. **Historical citations** — decide policy: the run's own recorded metric and
   the manuscript/PROJECT_STATUS numbers (Prescription `clinical_headline`
   0.8766, and any reliability figures that move). Overwriting silently is
   exactly what the plan forbids; the choice between *overwrite-with-disclosure*
   (the corrected number becomes the number, old one footnoted as a scorer-bug
   correction) and *annotate-only* (preserve the as-scored number, add a
   re-score layer) is the open decision governing all four fixes.

## Corrected so far (overwrite-with-disclose applied)

- `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` (the primary
  canonical run — manuscript §4.2, three dossiers, frontend snapshot): Prescription
  0.8766→0.9073, SF 0.5921→0.5982, overall 0.7313→0.7416. Registry
  `primary_metrics` + `claim_language_notes` disclosure updated.
- `exectv2_gepa_sf_verify_gpt41mini_20260628` (cited in the SF dossier F1 ladder):
  clinical_headline 0.5971→0.6029, state_profile 0.7413→0.7483. Registry updated.

## Tracked: remaining cited runs to re-score (Phase 4 "all cited runs" sweep)

The Prescription/SF fixes affect *every* run's `clinical_headline` scoring, not
just the two above. These registered runs carry affected metrics and cached
predictions (`.jsonl`) but have **not** yet been re-scored — a bounded, zero-LLM
mechanical sweep left for the Phase 4 completeness pass (each needs the same
`primary_metrics` update + disclosure). Listed with their as-scored (pre-fix)
values so the sweep is auditable:

- `exectv2_gepa_dedup_gpt41mini_h2mb8_20260628` (Rx 0.8498, SF 0.5396)
- `exectv2_gepa_dedup_qwen3p6_35b_h2mb8_20260629` (Rx 0.7591, SF 0.3909)
- `exectv2_gepa_investigations_lane_deepseekreasoner_20260630` (Rx 0.8856, SF 0.4488)
- `exectv2_gepa_multifamily_dedup_qwen3p6_35b_h2mb8_20260629` (Rx 0.7303, SF 0.5056)
- `exectv2_gepa_multistage_dedup_gpt41mini_20260628` (Rx 0.8514, SF 0.55)
- `exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701` (Rx 0.886, SF 0.6006)
- `exectv2_gepa_sf_verify_p5_reasoner_mini_ex_20260629` (SF 0.608 / sp 0.7661)
- `exectv2_gepa_sf_verify_p5_reasoner_mini_fb_20260629` (SF 0.5873 / sp 0.7661)
- `exectv2_gepa_sf_verify_p5_reasoner_reasoner_ex_20260629` (SF 0.5861 / sp 0.7839)
- `exectv2_gepa_sf_verify_p5_reasoner_reasoner_fb_20260629` (SF 0.56 / sp 0.7434)
- `exectv2_gepa_sf_verify_v2_deepseekchat_20260629` (SF 0.534 / sp 0.7021)
- `exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624`
  (overall clinical_headline 0.8502) — **full-200; re-score is aggregate-only and
  must respect the holdout no-row-inspection protocol.**

Four further runs (`exectv2_2call_no_sf_adjudicator_*`) carry affected metrics but
have **no cached predictions** (`.jsonl` absent), so they can only be
disclosure-annotated as stale, not re-scored.

## Test status

- Prescription / SF / Investigations scorer unit tests: **pass** (117 SF+Inv,
  3 Rx projection pilot, 248 in the broader scoring selection).
- `test_static_frontend_scorecard_matches_builder_contract`: **red by design** —
  the frozen frontend cache no longer matches the corrected builder output.
  Regenerating the snapshot is pending the citation-policy decision above (it
  re-freezes the ~100 rippled reliability numbers).
- Two pre-existing collection errors (`tests/test_doc_hygiene.py` missing
  `scripts.check_doc_hygiene`; a gan2026 registry import) are unrelated to this
  work.
