# Registry Exhaustive Review

Date: 2026-06-26

Scope: current working-tree `experiments/registry.jsonl` (`227` rows). This review
answers whether non-canonical rows should be reconsidered because they are better
model-family prompt variants, useful architecture ladders, holdout anchors, or
important negative/attribution evidence.

## Current Canonical Surface

The only rows currently surfaced as architecture comparators in
`experiments/registry.jsonl` are the six Gan validation750 replay rows:

- `gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07`
- `gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08`
- `gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08`
- `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07`
- `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08`
- `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08`

The deterministic canonical comparator is curated separately as executable
`rules_only` in `run_surfacing.py`, not as a `surface_as_architecture` JSONL row.
For this review, the current canonical comparison surface is therefore seven
comparators: six surfaced replay rows plus the executable deterministic row.

## Registry Hygiene Findings

These are not metric claims, but they affect interpretation.

1. `experiments/RUN_INDEX.md` is stale relative to the current JSONL. It contains
   older ExECTv2 v08/v09 holistic assembly entries that are not present in the
   current `registry.jsonl` grep results. The JSONL should remain authoritative,
   but the stale index makes "canonical" ambiguous for humans.
2. The two surfaced Qwen Gan rows are seeded with no primary metrics:
   `gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08`
   and
   `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08`.
   The metrics exist in
   `gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09`
   and should be backfilled or linked more explicitly.
3. Four ExECTv2 same-core dev140 rows already carry `architecture_family` and
   `comparison_role` metadata but are not surfaced. That is appropriate for the
   Gan Explorer, but these rows should be treated as canonical-adjacent for the
   ExECTv2 reliability/model-swap story.
4. Current-status ExECTv2 artifacts such as v08 full-200, robustness validation,
   v09 simplification, and same-core full-200 are documented outside the JSONL.
   If the registry is intended to be the durable claim-of-record index, those
   rows need backfill.

## Strong Non-Canonical Rows To Consider

### 1. Gan SE v0.6, model-family prompt variants

These are the clearest "better prompt variant for one model family" rows.

| Run | Model | Surface | Key result | Why consider | Boundary |
| --- | --- | --- | --- | --- | --- |
| `gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12` | Qwen 3.6:35b | validation750 | Purist `638/750` (`0.8507`), Pragmatic `656/750`, `4` parse/schema issues | Improves Qwen SE over Phase 1 (`624/746` rendered-correct in the row note). Better Qwen-family prompt variant than the surfaced seeded row. | Validation development only; heavy JSON dialect repair (`746` repairs) and lower exact evidence (`581/750`). |
| `gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12` | DeepSeek | validation750 | Purist `622/750` (`0.8293`), Pragmatic `646/750`, `5` parse/schema issues | Improves DeepSeek SE over Phase 1 (`609/742` rendered-correct). Cleaner than Qwen on JSON dialect/evidence. | Validation development only. |

Recommendation: add these as "best SE v0.6 model-family variants" or a separate
close-off comparison set. Do not silently replace the Phase 1 canonical rows
without naming the prompt-version change.

### 2. Gan Phase 4 frozen test450 architecture report

`gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10` is the strongest
holdout-facing architecture comparator in the registry.

| Architecture | Test rows | Rendered | Purist of rendered | Pragmatic of rendered |
| --- | ---: | ---: | ---: | ---: |
| deterministic canonical pipeline | 450 | 450 | `329` (`0.731`) | `341` (`0.758`) |
| hybrid v5 | 450 | 334 | `269` (`0.805`) | `281` (`0.841`) |
| hybrid structured-events v0.5 | 450 | 448 | `364` (`0.812`) | `381` (`0.850`) |
| LLM-only canonical pipeline v0.5 | 450 | 450 | `326` (`0.724`) | `346` (`0.769`) |

Recommendation: keep this as a separate locked-holdout canonical comparator
table. It is not a development tuning surface and should not be blended with
validation rows, but it is more claim-relevant than many validation-only rows.

### 3. Gan consensus/fresh agreement selector ladder

The consensus/fresh selector family is not a simple architecture replacement;
it is a selective-adjudication ladder over saved components.

Best row: `gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15`

- Deterministic Purist: `697/750`
- Consensus Purist: `708/750`
- Fresh-evidence Purist: `682/750`
- Selected Purist: `733/750`
- Changed labels: `49`
- Wrong to correct: `36`
- Correct to wrong: `0`
- Changed-label precision: `0.7347`

Recommendation: consider it as a high-signal architecture-ladder/selector
candidate, not as a promoted canonical architecture. It is validation-only
no-call replay and needs a frozen hard-slice/robustness/test protocol before
any holdout-facing claim.

### 4. Gan agentic structured-event consensus

`gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13`
is useful because it shows multi-agent value and its regression cost.

- Baseline Purist: `697/750`
- Consensus Purist: `708/750`
- Net Purist gain: `+11`
- Wrong to correct: `27`
- Correct to wrong: `16`
- Changed-label precision: `0.2213`

Recommendation: keep as a ladder rung and design lesson: agents help as a
selector over strong rendered components, but regression filtering is mandatory.
Do not promote as a clean multi-agent superiority claim.

### 5. Gan fresh-evidence reasoner, validation win but holdout warning

This is important because it is both promising and cautionary.

| Run | Surface | Result | Interpretation |
| --- | --- | --- | --- |
| `gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13` | validation750 | Final Purist `682/750`, net `+20` vs v0, `0` call/parse failures | Validation-development promotion; frozen for an explicit aggregate-only test request. |
| `gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15` | test450 | Final Purist `351/450`, net `-14` vs v0, target `383` not reached | Rejected holdout readout; do not promote despite validation signal. |

Recommendation: include in the paper/review as a generalization-gap caution and
as evidence for strict split discipline. It is not a canonical winner.

### 6. Gan state-graph ontology Stage D

`gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15` is valuable as
component-generation evidence.

- Predeclared residual-inclusive slice: `250` rows containing all `11/750`
  no-correct residual rows.
- Graph minted correct components for `7/11` predeclared residual rows.
- P2 corroborated selection posture: `1` wrong-to-correct, `0`
  correct-to-wrong, net `+1`.
- P1 unilateral and P3 unknown-only were strongly negative.

Recommendation: consider as a component ladder and mechanism probe. The graph
generator is promising; the selection posture is still the bottleneck. Not a
holdout-facing candidate.

### 7. Gan reliability scorecards

The reliability rows should not be compared as accuracy candidates, but they are
paper-facing evidence.

- `gan2026_reliability_scorecard_phase0_2026-06-17`: subject Purist
  `0.881` validation / `0.809` test, external failure AUROC `0.781`, ECE
  `0.080`, Brier `0.102`, model render failures `0`, estimated
  `$1.16/1000` notes.
- `gan2026_reliability_scorecard_phase1_2026-06-17`: test450 base error
  `0.191`, agree-only coverage `0.658`, selective risk `0.122`,
  two-agent failure AUROC `0.648`, worst band `band_submonthly@0.695`.

Recommendation: canonicalize as a reliability/scorecard section, not as an
architecture row.

### 8. ExECTv2 same-core model-swap rows

These four current JSONL rows are high-signal despite `surface_as_architecture=false`.

| Run | Model | Surface | Overall clinical-headline F1 | Operational notes |
| --- | --- | --- | ---: | --- |
| `exectv2_2call_no_sf_adjudicator_deepseek_dev140` | DeepSeek | dev140 | `0.8596` | Leads dev140; `1` parse/schema failure. |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140` | GPT-4.1-mini | dev140 | `0.8396` | Clean operational reference. |
| `exectv2_2call_no_sf_adjudicator_qwen36_dev140` | Qwen | dev140 | `0.8018` | `1` call failure and `12` parse/schema failures. |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140` | Qwen repair v02 | dev140 | `0.8319` | Passes dev140 repair gates: `0` call/parse failures, structured evidence `0.9964`. |

Recommendation: keep these as an ExECTv2 same-core model-family comparison. Qwen
repair v02 deserves a fresh full-200 inclusion decision, but not retroactive
promotion into the already-frozen GPT+DeepSeek full-200 protocol.

### 9. ExECTv2 same-core full-200 and v08/v09 docs missing from JSONL

These are outside the current JSONL but should be backfilled if the registry is
the durable experiment index.

- `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`:
  GPT-4.1-mini full200 `0.8356`, DeepSeek full200 `0.8566`, min evidence
  `1.0000`, aggregate-only boundary.
- `docs/experiments/exectv2/reliability/exectv2_robustness_validation_audit_2026-06-25.md`:
  current-code v08-shaped full200 overall `0.8503`, hard-slice `0.8336`,
  schema/evidence `1.0000`.
- `docs/experiments/exectv2/key_entities/exectv2_v09_single_gpt_simplification_study_dev140_20260621.md`:
  single GPT + dictionary `0.7552`; partial hybrid accepted `0.9059`; v08
  comparator `0.9152`.

Recommendation: add registry rows for these rather than relying on a stale
`RUN_INDEX.md`.

### 10. ExECTv2 early SF/model-family prompt effects

These rows are useful for explaining prompt/model interactions:

| Family | GPT-4.1-mini | Qwen 3.6:35b | Read |
| --- | --- | --- | --- |
| single-pass SF | phrase per-letter `0.701`, semantic per-letter `0.197` | phrase per-letter `0.623`, semantic per-letter `0.213` | Qwen single-pass slightly beats GPT on semantic per-letter, despite weaker phrase recall and parse caveats. |
| per-entity SF | phrase per-letter `0.698`, semantic per-letter `0.264` | phrase per-letter `0.642`, semantic per-letter `0.104` | Per-entity prompt helps GPT semantic scoring but hurts Qwen semantic scoring. |
| hybrid SF | GPT phrase per-letter `0.781`, benchmark per-letter `0.578` | Qwen phrase per-letter `0.730`, benchmark per-letter `0.451` | Hybrid candidate+assessment is the strongest SF architecture in this early ExECTv2 ladder. |

Recommendation: cite these as model-family prompt-variant evidence. The per-entity
prompt is not universally better; it is GPT-favorable and Qwen-unfavorable on
semantic SF.

### 11. ExECTv2 focused specialist ladders

These are not canonical full candidates, but they show useful component ladders:

- `exectv2_llm_diagnosis_verifier_v05_dev25_gpt41mini_20260618`: Diagnosis
  clinical-headline F1 `0.837` on dev25, evidence `1.0000`; needs dev140
  confirmation.
- `exectv2_llm_sf_verifier_v03_dev25_gpt41mini_20260618`: SeizureFrequency
  clinical-headline F1 `0.831` on dev25, evidence `1.0000`; needs dev140
  confirmation.
- `exectv2_hybrid_sf_state_adjudicator_v05_dev140_gpt41mini_20260618`: current
  best SF dev140 candidate in that ladder, F1 `0.721`; revise only.
- `exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618`:
  Investigations F1 `0.872`; validates splitting Investigations from medication.
- `exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618`: Prescription
  F1 `0.817` but Investigations regresses to `0.496`; supports split-family
  design.

Recommendation: consider these for a component-evidence appendix or architecture
ladder, not as headline candidates.

## Rows That Should Not Be Promoted

Several high-looking rows are important precisely because they should not be
promoted.

- `gan2026_llm_structured_v05_full_validation_2026-06-01`: `675/750` Purist,
  but rejected as clean LLM-first because deterministic semantic repair became
  prediction-bearing. Keep for attribution-ladder evidence.
- `gan2026_llm_structured_v05_attribution_repair_ladder650_2026-06-01`: useful
  repair-family attribution ladder; full stack `588/650`, raw `394/650`,
  clean policy `438/650`. This is hybrid post-processing evidence, not clean
  LLM-first success.
- `gan2026_claim_table_v4_validation750_2026-06-01`: `528/750` clean Purist;
  rejected after full validation exposed cluster-axis and boundary-state collapse.
- `gan2026_llm_first_direct_extractor_validation750_2026-06-01`: `505/750`
  Purist; direct extraction rejected.
- `gan2026_kg_family_gated_graph_trust_2026-06-16`: rejected because
  corroboration-free family-gated graph trust caused large regressions
  (`p2_5_net_purist_gain=-113`).
- `gan2026_llm_only_direct_labeler_v07_validation750_gpt41mini_2026-06-15`:
  label-binding v0.7 regressed badly (`v07_purist=469` vs v05 `575`).

## Recommended Canonical/Curated Sets

Use multiple curated sets instead of one overloaded "canonical" label.

1. **Gan validation architecture canonical.**
   Current six surfaced rows plus executable deterministic. Backfill Qwen metrics.
   Optionally add SE v0.6 Qwen/DeepSeek as "best model-family SE variants" rather
   than replacing Phase 1 rows silently.
2. **Gan locked-holdout anchors.**
   Phase 4 test450 comparison report, DeepSeek SE v0.6 test row, direct-labeler
   calibration test row, rules-only v1 test holdout, and fresh-evidence negative
   holdout. Keep aggregate-only boundaries explicit.
3. **Gan component/selector ladder.**
   Consensus/fresh v0.9, agentic unanimous consensus, state-graph Stage D, and
   reliability scorecards. These explain mechanism, not headline accuracy.
4. **ExECTv2 architecture/reliability canonical.**
   Backfill v08/v09, robustness validation, same-core full200, and same-core
   dev140/Qwen repair v02 rows into JSONL if the registry is meant to govern
   current project status.
5. **ExECTv2 component-evidence appendix.**
   Early SF single-pass/per-entity/hybrid rows plus specialist Diagnosis/SF/
   Prescription/Investigations ladders.

## Concrete Next Actions

Completion update, 2026-06-26:

1. Done. `experiments/registry.jsonl` is now the source for `experiments/RUN_INDEX.md`;
   the index was regenerated from the typed registry after backfill.
2. Done. The two surfaced Qwen Gan Phase 1 rows now carry primary metrics from
   `gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09`
   and link the report artifacts.
3. Done. Added JSONL rows for current ExECTv2 v08 full-200 current-code aggregate,
   same-core full-200 aggregate, robustness validation, and v09 simplification
   study evidence.
4. Done. Added controlled `registry_roles` support with these values:
   `architecture_comparator`, `model_family_variant`, `holdout_anchor`,
   `component_ladder`, `reliability_scorecard`, `negative_attribution`, and
   `historical_lineage`.
5. Decided. Qwen SE v0.6 and DeepSeek SE v0.6 are tagged as
   `model_family_variant` close-off diagnostics and remain
   `surface_as_architecture=false`; they do not silently replace the Phase 1
   canonical rows.
6. Decided and authorized. Qwen repair v02 has a separate same-core full-200
   aggregate-only predeclaration, now recorded at
   `docs/experiments/exectv2/reliability/exectv2_qwen_repair_v02_full200_predeclaration_2026-06-26.md`.
   This does not retroactively alter the GPT-4.1-mini plus DeepSeek full-200
   protocol.
7. Preserved. Registry notes and the new Qwen predeclaration keep locked-test and
   full-200 artifacts aggregate-only; no holdout/full-200 row-level failures are
   authorized as development or tuning evidence.
