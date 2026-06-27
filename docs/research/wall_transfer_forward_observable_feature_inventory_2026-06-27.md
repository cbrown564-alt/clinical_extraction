# Wall-Transfer Forward-Observable Feature Inventory

Date: 2026-06-27  
Workstream: P3a (closing campaign orchestration plan)  
Status: read-only spec derived from Gan reliability Phase 0–2 artifacts  
Purpose: define the probe to replay on **ExECTv2 SeizureFrequency (SF)** and test whether *The Wall* transfers (confident unknown-vs-rate over-reading with no gold-free abstention signal).

---

## Scope and guardrails

- **Canonical Gan subject:** single GPT structured-event pass on `gpt-4.1-mini`, read from `v0_reference` (decision 0018).
- **Binding residual (wall):** 11 validation rows with **no Purist-correct component** (8/11 `band_unknown`); selector oracle 739/750. On these rows the signal separating *withhold-to-unknown* from *emit-rate* is absent from every forward-observable feature; only hidden gold separates them (closeout Insight #5).
- **Population vs wall:** A feature may rank errors **population-wide** (informative on validation750) yet be **flat at the binding residual** (wall-degenerate). Both columns are reported below.
- **No holdout row reads** in this inventory; test450 ports are noted only as weaker replays.
- **ExECTv2 port:** aggregate validation-side only; join multi-model swap runs by letter id; score against SF **Frequency State Recovery** headline units `(seizure_type, state)`.

Sources: `CONTEXT.md` (Forward-Observable Feature, External Risk Score, Cross-Model Agreement, Semantic Entropy); `docs/experiments/gan2026/reliability/gan2026_reliability_scorecard_and_phased_plan_2026-06-17.md`; P0.2/P0.3/P2.1/P0.8/confidence-elicitation artifacts under `experiments/`; `docs/research/closing_stage_research_critique_2026-06-27.md` §3, §5.

---

## Feature inventory (18 probe features)

| # | Feature | Computation | Gan artifact fields | Targets (families / bands) | Population (val750) | At wall / residual |
|---|---------|-------------|---------------------|----------------------------|---------------------|---------------------|
| 1 | **Cross-model agreement count** | Size of largest identical-label cluster among agent votes ∈ {1,2,3} | `consensus_decision.votes[].final_label` in `gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.jsonl`; join `source_row_index` | All bands; strongest on agent-disagreement rows (mixed over-read vs rate) | **Informative** — leg of External Risk Score; agreement-share AUROC(correct) **0.750** | **Wall-degenerate for unknown↔rate split** — confident unanimous over-reads still score agreement=3; 1/89 errors sits in risk-0 bucket (121 rows) |
| 2 | **Cross-model agreement share** | `agreement_count / 3` → {⅓, ⅔, 1} | Same as #1 | All | **Informative** — ECE **0.080**, Brier **0.102**, AUROC(correct) **0.750** | Same as #1 — calibrated for overall correctness, not withhold-vs-emit on no-correct rows |
| 3 | **External risk score (composite)** | `3×(3−agreement) + source_flag_count + len(ambiguity_reasons)` (higher = riskier) | #1 + `router_packet.boundary_features` in `gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl` + `v0_reference.comparison.purist_correct` | Over-reading families: `last_event_or_seizure_free_overinfer_unknown`, `unknown_over_quantified_rate`, `seizure_free_duration`, cluster-burden | **Informative** — failure AUROC **0.781**; risk–coverage AUC **0.040** (oracle 0.007) | **Partially informative / wall plateau** — sheds recoverable error but **irreducible plateau** at safest tier (selective risk **0.8%** @ 16% coverage); errors leak into low-risk region because over-reading is *confident* |
| 4 | **Two-agent agreement count** (holdout-degraded leg) | Same as #1 but only gpt-4.1-mini + qwen votes | `gan2026_agentic_structured_event_consensus_available_two_agent_exact_test450_2026-06-13.jsonl` | All (test450 only) | **Weaker informative** — test450 failure AUROC **0.648** (< val 0.781) | Not re-measured on binding 11; by construction weaker |
| 5 | **`source_has_last_event_language`** | Boolean source-text flag | `router_packet.boundary_features.source_has_last_event_language` | `last_event→duration`, seizure-free over-inference | Contributes to composite (#3) | **Coarse / wall-degenerate alone** — flags risky *shape* but does not separate withhold-unknown from emit-rate when all components agree on wrong rate |
| 6 | **`source_has_since_anchor`** | Boolean | `…boundary_features.source_has_since_anchor` | Seizure-free duration over-inference (`since …`) | Same | Same |
| 7 | **`source_has_trigger_language`** | Boolean | `…boundary_features.source_has_trigger_language` | Provoked/transient → rate over-read | Same | Same |
| 8 | **`source_has_drop_attack_language`** | Boolean | `…boundary_features.source_has_drop_attack_language` | Drop-attack / semiology confusion | Same | Same |
| 9 | **`source_has_unable_to_quantify`** | Boolean | `…boundary_features.source_has_unable_to_quantify` | Underspecified-rate → quantified frequency | Same | Same |
| 10 | **Source residual flag count** | Count of True among flags #5–#9 (0–5) | Sum of five booleans above | Union of over-reading families | Part of #3 | **Coarse** — raises risk score but **no gold-free unknown↔rate separator** on no-correct rows |
| 11 | **Ambiguity reason count** | `len(boundary_features.ambiguity_reasons)` | `router_packet.boundary_features.ambiguity_reasons` | Cluster-axis ambiguity, frequency-with-count blocking, multi-primary | Part of #3 (0–5 buckets) | **Coarse** — correlates with router `review`/`abstain` pressure, not binding residual discrimination |
| 12 | **Self-confidence (joint)** | Categorical `high` / `medium` / `low` | `structured_record.selection.confidence` in `gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl` | All | **Degenerate** — **99.2%** `high`; failure AUROC **~0.503** (chance) | **Degenerate** — cannot flag confident over-reading |
| 13 | **Reasoner uncertainty** (comparator) | `decision_record.uncertainty` on V12 reasoner path | `gan2026_fresh_evidence_reasoner_validation750_…jsonl` | All | **Degenerate** — **98.5%** one bucket | **Degenerate** |
| 14 | **Evidence valid / grounded** | Boolean: cited span grounded in note (exact or `REPAIRED_*`) | `v0_reference.evidence_valid` (legacy); unified `evidence_grounded` per `docs/reference/evidence_groundedness_metric.md` | Faithfulness axis (all families) | **Weak** — invalid **84.7%** vs valid **88.4%** acc; faithful-but-wrong dominates | **Wall-degenerate** — grounding ≠ clinical correctness; over-reads often **fully grounded** |
| 15 | **Selected evidence exact** | Boolean exact substring (no repair) | `selected_evidence_exact` in rq9 router / evidence contract | All | **Degenerate** — **750/750 True** in router file; deliberately **excluded** from External Risk Score | **Degenerate** |
| 16 | **Parse-repair count** | `len(parse_errors)` on SE path | `parse_errors` in SE-mini validation750 JSONL | Parser-stress / schema edges | **Weak informative** — failure AUROC **0.600**; any-repair **86.0%** vs no-repair **93.2%** | **Not a wall signal** — repairs common (528/750), not concentrated on no-correct residual |
| 17 | **Semantic entropy — Purist label** (P2.1 primary) | Normalized Shannon entropy over k=4 samples at temps {0.3,0.5,0.7,1.0} on `comparison.predicted_purist_category` | P2.1 sample JSONL + `build_gan2026_reliability_p2_1_semantic_entropy.py` | Residual proxy: `band_unknown` ∪ `seizure_free_duration` | **Degenerate** — mean **0.012**; only **4/150** rows non-zero | **Degenerate (H0)** — residual mean **0.018** vs non-residual **0.011**; **`band_unknown` = 0.000** → confident over-reading mechanism |
| 18 | **Semantic entropy — event kind** (P2.1 secondary) | Same samples on `structured_record.selection.final_kind` (`frequency`/`seizure_free`/`unknown`/…) | Same as #17 | Upstream wavering masked by render | **Degenerate** — mean **0.003** | **Degenerate** — residual kind entropy **0.018** on n=23 slice; flat vs non-residual |
| — | **Temp-0 self-agreement** (P0.8; not wall probe) | Majority fraction over k=4 @ temp 0.0 | `gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl` | Hard50 boundary slice only | **Uninformative at temp-0** — AUROC **0.524**; measures reproducibility not consistency | Superseded by #17–18 for wall question |
| — | **Variant C elicited confidence** | Decoupled second pass: P(same purist category) | Confidence-elicitation pilot JSON | All | **Weak** — AUROC **0.611**; spread without discrimination | Residual mean p **0.846** ≈ non-residual **0.866** — **no wall localization** |
| — | **Variant D failure-primed confidence** | Decoupled pass naming over-read failure mode | Same pilot | Over-reading families | **Partial population signal** — AUROC **0.755** (approaches external) | Residual mean p **0.859** vs **0.896** — **does not drop on residual**; high-confidence errors remain |
| — | **External + D rank blend** | Rank-average of #3 and Variant D risk | `gan2026_reliability_blend_external_plus_d_validation750_2026-06-17.md` | All | **Marginal** — AUROC **0.797** (+0.014); CV blend collapses to external alone | Not tested on binding 11; fusion buys nothing honest |

**Feature count for ExECTv2 SF probe spec: 18 numbered features** (#1–#18), plus 4 documented comparators/extensions (P0.8, Variants C/D, blend) that Gan measured but that are **not required** for the cross-task wall-transfer headline.

---

## External Risk Score — frozen composite (P0.2 headline)

```
risk = 3 * (3 - cross_model_agreement_count)
     + source_residual_flag_count          # flags #5–#9
     + ambiguity_reason_count              # #11
```

**Excluded by design:** `selected_evidence_exact` (#15) — degenerate constant.  
**Scored against:** `v0_reference.comparison.purist_correct` (not rq9 hybrid adjudicator).

---

## Semantic entropy protocol (P2.1 — wall falsification)

- **Samples:** k=4 at temperatures **0.3 / 0.5 / 0.7 / 1.0** (never temp-0).
- **Primary:** entropy over rendered Purist category (abstention surface).
- **Secondary:** entropy over `final_kind` (upstream wavering probe).
- **Pre-flight gate:** 25-row degeneracy check — if mean entropy ≈ 0 everywhere, full validation750 spend is optional.
- **Verdict on Gan (150-row residual-enriched tier):** **`H0_confident_over_reading`** — raw prose varies, decisions do not; strongest wall mechanism evidence.

---

## Gan failure families × feature targeting

| Clinical failure cluster | Gold band / family | Features with designed sensitivity |
|--------------------------|-------------------|-----------------------------------|
| Unknown → quantified rate | `band_unknown`, `unknown_over_quantified_rate` | #5–#11 (source shape), #17–18 (entropy — null result) |
| Last-event → seizure-free duration | `seizure_free_duration`, `last_event_or_seizure_free_overinfer_unknown` | #5, #6, #7 |
| Cluster axis / burden dropped | `cluster_burden_component_failure` | #8, #11 (ambiguity reasons) |
| Highest semiology / denominator conflict | `highest_semiology_or_denominator_conflict` | #4–#9 (weak), #1–2 (when agents split) |
| Confident unanimous over-read | 7/11 no-correct **all-three-one-bucket** | #12–#18 all **flat**; #1–3 rank some errors but **not unknown↔rate** |

---

## ExECTv2 SF porting map

| Gan feature | ExECTv2 SF analog | Port effort | Notes |
|-------------|-------------------|-------------|-------|
| #1–2 Cross-model agreement | Compare SF **Frequency State Recovery** units across `exectv2_2call_no_sf_adjudicator_{gpt41mini,deepseek,qwen}_*` runs (join `letter_id`) | **Low** — three model-swap artifacts exist; Qwen row may need parity gate | Strongest expected transferable signal (critique §3) |
| #3 External risk composite | Recompute with ExECT agreement + **ported** source flags | **Medium** — no rq9 router; must rebuild source-shape flags from note text or SF lens diagnostics | Gan formula is predeclared template |
| #5–#11 Source flags + ambiguity | ExECT has **no** `boundary_features` packet; re-implement from note + SF assembly trace or reuse Gan `classify_boundary_families` on dev140 | **Medium–high** | Task-specific; clinical semantics transfer, artifact path does not |
| #12 Self-confidence | SF lens emits `confidence="high"` in residual/dictionary paths; model swap logs may lack variance | **Low to run, expect degenerate** | `assembly/lenses/seizure_frequency.py` hardcodes high on convention paths |
| #14 Evidence grounded | Unified `score_evidence_set` / `evidence_grounded` (M2) | **Low** — cross-task metric now canonical | Model swap reports min evidence rate **1.0000** — may be degenerate on ExECT too |
| #15 Evidence exact | `evidence_exact_rate` sub-metric | **Low** | Likely near-constant at 1.0 on swap runs |
| #16 Parse-repair count | ExECT repair / schema-normalization counters in run metadata | **Medium** — locate analogue in 2-call assembly logs | Weak signal on Gan; optional |
| #17–18 Semantic entropy | Re-sample SF extraction k× at varying T on dev140/full-200 validation split | **High** (model budget) | Methodology transfers; **H0 expected** if wall transfers |

**Scoring surface for ExECT probe:** SF headline unit = `(seizure_type, state)` with states `{active-rate, seizure-free, unknown}`; wrong-state on unknown-gold rows = over-read analogue.

---

## Predicted transfer vs degeneracy on ExECTv2 SF

### Top 3 most likely to **transfer** (remain informative population-wide)

1. **Cross-model agreement count / share (#1–#2)** — Three same-core model-swap runs already exist; SF is the weakest family (0.75–0.76) where agent disagreement should correlate with headline errors the same way Gan’s external leg AUROC **0.75–0.78** did.
2. **External risk score composite (#3)** — Even with rebuilt source-flag leg, the agreement term alone should reproduce a monotone risk–coverage curve on SF errors; the **plateau-at-residual** shape is the wall-transfer headline to confirm.
3. **Evidence groundedness rate (#14)** — Shared `core/evidence.py` implementation; expect the same **faithful-but-wrong** split (grounding validates presence, not clinical withhold-vs-emit), i.e. informative for faithfulness reporting but **not** a wall crack.

### Top 3 most likely to **degenerate** on ExECTv2 SF

1. **Self-confidence (#12)** — Hardcoded `confidence="high"` on SF lens convention paths and uniformly high model-swap evidence rates predict the same **single-bucket** failure as Gan P0.3.
2. **Semantic entropy at SF wall rows (#17–#18)** — Gan P2.1 H0 on `band_unknown` (entropy **0.000**) is the mechanistic prior; ExECT unknown-state over-read should show **temperature-stable confident** decisions if the wall transfers.
3. **Selected evidence exact / near-unity evidence rate (#15, plus swap min evidence 1.0000)** — Exact-span gating is enforced project-wide; expect **constant-or-near-constant** feature useless for abstention ranking, matching Gan’s 750/750 degeneracy.

---

## Probe acceptance criteria (for P3 wall-transfer experiment)

1. **Population:** Report failure-prediction AUROC and risk–coverage AUC for #1–#3 on ExECT SF validation aggregate (dev140 minimum; full-200 if authorized aggregate-only).
2. **Wall slice:** On SF rows where gold state is `unknown` but predicted state is `active-rate` or `seizure-free`, test whether any feature #1–#18 separates withhold-correct from over-read-wrong **without gold** — expect **null** if wall transfers.
3. **Mechanism:** If #17–#18 are run, pre-register H0 (flat entropy on unknown-gold over-reads) vs H1 (elevated entropy).
4. **Cross-task headline:** Wall transfers if (a) SF is weakest family, (b) external agreement ranks SF errors, and (c) binding over-read rows remain low-entropy / high-agreement — same pattern as Gan closeout.

---

## Source artifacts

| Artifact | Role |
|----------|------|
| `experiments/gan2026_reliability_p0_2_risk_coverage_validation750_2026-06-17.md` | External Risk Score curve, AUROC 0.781 |
| `experiments/gan2026_reliability_p0_3_external_calibration_validation750_2026-06-17.md` | Calibration + degeneracy tables |
| `experiments/gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md` | H0 confident over-reading |
| `experiments/build_gan2026_reliability_p0_2_risk_coverage.py` | Frozen composite definition |
| `experiments/build_gan2026_reliability_p2_1_semantic_entropy.py` | Entropy computation |
| `experiments/gan2026_residual_component_diversity_audit_2026-06-15.json` | 11 no-correct row families |
| `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md` | ExECT multi-model SF baselines |
| `docs/research/closing_stage_research_critique_2026-06-27.md` §3, §5 | Wall-transfer rationale |
