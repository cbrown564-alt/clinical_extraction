# ExECTv2 matched-split, cross-architecture cost-quality table

Status: **DONE.** Date: 2026-07-01. Owner: ExECTv2 workstream.

Companions:
- `docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md`
  (Item 3, Phase 1 — the plan this doc implements)
- `docs/research/exploratory_research_directions_multiagent_review_2026-07-01.md`
  (the review whose "hybrid is worth +0.2 F1, split-dependent by roughly 5x"
  claim this doc checks and corrects)
- `experiments/exectv2_cost_quality_matched_split_table.py` (the zero-LLM
  script this doc's numbers come from) and its output artifact
  `experiments/exectv2_cost_quality_matched_split_table_20260701.json`
- `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`
  (source of the 1/2/3-call full200 ladder)
- `experiments/exectv2_component_off_replay_full200_20260626.md` (source of
  the deterministic post-processing stack delta)

## Method

Zero-LLM, read-only over `experiments/registry.jsonl` via
`clinical_extraction.core.registry.load_run_registry`. No model calls, no
registry edits, no git operations. The script filters to the full 23-value
ExECTv2 `pipeline_family` set (22 `exectv2_*`-prefixed values plus
`gepa_from_scratch` — GEPA rows are registered under this task-agnostic name,
**not** an `exectv2_*`-prefixed one, and a substring filter would silently
drop all 4 of them). 64 registered rows match this family set.

Two things needed hand annotation because they are not registry fields, and
both are recorded with an inline basis quote (in the script, and summarized
below) rather than silently guessed:

- **LLM-call-count per family** — read from each family's `model_role` /
  `claim_language_notes` text.
- **Representative primary F1 metric per row** — rows are not metric-uniform
  (`clinical_headline_f1`, `overall_f1`, two-model-bundled
  `<model>_clinical_headline_f1` pairs, and an older pre-`clinical_headline`
  `sf_benchmark_per_item_f1` / `benchmark_per_item_f1` / `semantic_per_item_f1`
  surface all appear). The script auto-selects one key per row via a
  documented priority list (`METRIC_PRIORITY`) and records every `*_f1` field
  actually present alongside the pick, so nothing is hidden by the selection.

The registry does not use the literal strings `dev140` / `dev25` / `full200`
anywhere — `split` is `"dev"` with `row_count` 25 or 140, or one of three
`full200_*` variants (`full200_aggregate`, `full200_audit`,
`full200_overall_audit` — the latter two are older Phase 6/7 SF-only or
all-entity-only audits on the pre-`clinical_headline` metric surface). The
table below normalizes these to `dev25` / `dev140` / `full200` while keeping
the raw split string so that surface difference is not hidden.

## LLM-call-count annotation, per family (basis)

| pipeline_family | calls/letter | basis |
| --- | --- | --- |
| `exectv2_deterministic` | 0 (rules only) | `model='(model-independent)'`, `mode='deterministic'` |
| `exectv2_deterministic_all9` | 0 (rules only) | `model='(model-independent)'` |
| `exectv2_diag_sf_verifier_residual_iteration` | ~3 total (1 upstream v0.5 draft from a separate run + 2 marginal: Dx verifier + SF verifier) | model_role: "Residual-led Diagnosis verifier v0.6 and SeizureFrequency verifier v0.4 over the v0.5 single structured key-entity draft" |
| `exectv2_holistic_finding_assembly` | hybrid, multi-call, not fixed (v08: 3 focused LLM lanes + 1 deterministic-only lane) | model_role + `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md` producer table |
| `exectv2_hybrid` | 1 marginal/letter (candidate-assessment or arbitration stage; upstream candidates are deterministic or from a separate 9-call/letter per-entity run) | model_role per row |
| `exectv2_hybrid_benchmark_overall` | 0 marginal (pure aggregation of already-run outputs) | `mode='analysis_only'` |
| `exectv2_hybrid_diagnosis_acceptance_gate` | 1/letter (Dx-only accept/reject gate) | model_role: "The model only accepts or rejects candidate IDs" |
| `exectv2_hybrid_diagnosis_decomposer` | 1/letter (Dx-only decomposer) | model_role text |
| `exectv2_hybrid_diagnosis_reconciler` | 1/letter (Dx-only reconciler) | model_role text |
| `exectv2_hybrid_sf_state_adjudicator` | 1/letter (SF-only adjudicator) | model_role text |
| `exectv2_key_entities_clinical_error_ledger` | 0 (analysis-only) | `model='none'`, `mode='analysis-only'` |
| `exectv2_key_entities_transfer_readout` | 0 marginal (a readout re-presenting other rows' numbers, despite `mode='live'`) | claim_language_notes: "Transfer readout combining ... dev140 runs" |
| `exectv2_llm_diagnosis_verifier` | 1/letter (Dx-only verifier) | model_role text |
| `exectv2_llm_investigations_verifier` | 1/letter (Inv-only verifier) | model_role text |
| `exectv2_llm_med_inv_verifier` | 1/letter (combined Rx+Inv verifier) | model_role text |
| `exectv2_llm_only_all_entities` | 1/letter (all 9 entities) | model_role: "one call per letter, all nine entities" |
| `exectv2_llm_only_key_entities_structured` | 1/letter (4 key families) | model_role text |
| `exectv2_llm_only_per_entity` | 1/letter as registered (SF- or Dx-scoped); architecturally up to 9/letter for full 9-entity coverage | model_role: "one focused call per entity type per letter" |
| `exectv2_llm_only_single_pass` | 1/letter (SF scope in registered runs) | model_role text |
| `exectv2_llm_sf_verifier` | 1/letter (SF-only verifier) | model_role text |
| `exectv2_robustness_validation_audit` | 0 (explicitly no live model calls) | model_role: "...aggregate...; no live model calls." |
| `exectv2_same_core_model_swap` | **2**/letter (the frozen `exectv2_2call_no_sf_adjudicator` core) | run_id prefix + model_role text |
| `gepa_from_scratch` | **1**/letter for `*_dedup_*` run_ids (monolith); **4**/letter for `*_multifamily_*` run_ids (one evolved signature per family) | run_id substring; corroborated by `final_instruction_tokens` (490 monolith vs 1736 multifamily) |

## Unified table (all 64 registered rows)

Full per-row data (all `*_f1` fields, not just the auto-picked one) is in
`experiments/exectv2_cost_quality_matched_split_table_20260701.json`. This is
the auto-picked representative metric per row (`METRIC_PRIORITY`-selected;
"—" = no `*_f1` field in `primary_metrics`):

| pipeline_family | run_id | split | rows | model | calls | metric = value |
| --- | --- | --- | ---: | --- | --- | --- |
| exectv2_deterministic | exectv2_audit_rules_full200_modelindependent_20260611 | full200 | 200 | (model-independent) | 0 | sf_benchmark_per_item_f1=0.3211 |
| exectv2_deterministic_all9 | exectv2_deterministic_all9_dev_20260617 | dev140 | 140 | (model-independent) | 0 | benchmark_per_item_f1=0.3625 |
| exectv2_diag_sf_verifier_residual_iteration | exectv2_diag_sf_verifier_v06_v04_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | ~3 (2 marginal) | diagnosis_f1=0.651 |
| exectv2_holistic_finding_assembly | exectv2_v09_single_gpt_simplification_study_dev140_20260621 | dev140 | 140 | gpt-4.1-mini | hybrid | v08_dev140_comparator_f1=0.9152 |
| exectv2_holistic_finding_assembly | exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624 | full200 | 200 | gpt-4.1-mini | hybrid | clinical_headline_f1=0.8502 |
| exectv2_hybrid | exectv2_hybrid_dev140_gpt41mini_20260611 | dev140 | 140 | gpt-4.1-mini | 1 | sf_benchmark_per_item_f1=0.327 |
| exectv2_hybrid | exectv2_hybrid_dev140_qwen3635b_20260611 | dev140 | 140 | qwen3.6:35b | 1 | sf_benchmark_per_item_f1=0.228 |
| exectv2_hybrid | exectv2_arbitration_v02_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | — |
| exectv2_hybrid | exectv2_audit_hybrid_full200_gpt41mini_20260611 | full200 | 200 | gpt-4.1-mini | 1 | sf_benchmark_per_item_f1=0.2458 |
| exectv2_hybrid_benchmark_overall | exectv2_hybrid_benchmark_overall_dev_20260618 | dev140 | 140 | gpt-4.1-mini+det. | 0 | benchmark_per_item_f1=0.3877 |
| exectv2_hybrid_diagnosis_acceptance_gate | exectv2_hybrid_diagnosis_acceptance_gate_v01_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | diagnosis_f1=0.625 |
| exectv2_hybrid_diagnosis_decomposer | exectv2_hybrid_diagnosis_decomposer_v01_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | diagnosis_f1=0.642 |
| exectv2_hybrid_diagnosis_decomposer | exectv2_hybrid_diagnosis_decomposer_v01_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | diagnosis_f1=0.814 |
| exectv2_hybrid_diagnosis_reconciler | exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | diagnosis_f1=0.658 |
| exectv2_hybrid_diagnosis_reconciler | exectv2_hybrid_diagnosis_reconciler_v02_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | diagnosis_f1=0.647 |
| exectv2_hybrid_diagnosis_reconciler | exectv2_hybrid_diagnosis_reconciler_v01_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | diagnosis_f1=0.833 |
| exectv2_hybrid_diagnosis_reconciler | exectv2_hybrid_diagnosis_reconciler_v02_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | diagnosis_f1=0.844 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v01_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | active_rate_f1=0.726 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v02_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | active_rate_f1=0.725 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v03_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | active_rate_f1=0.722 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v04_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | active_rate_f1=0.746 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v05_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | active_rate_f1=0.762 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v01_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | seizure_frequency_f1=0.921 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v02_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | seizure_frequency_f1=0.951 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v03_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | seizure_frequency_f1=0.921 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v04_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | seizure_frequency_f1=0.935 |
| exectv2_hybrid_sf_state_adjudicator | exectv2_hybrid_sf_state_adjudicator_v05_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | seizure_frequency_f1=0.918 |
| exectv2_key_entities_clinical_error_ledger | exectv2_key_entities_clinical_error_ledger_dev140_20260618 | dev140 | 140 | none | 0 | diagnosis_f1=0.616 |
| exectv2_key_entities_clinical_error_ledger | exectv2_key_entities_clinical_error_ledger_diagv06_sfv04_dev140_20260618 | dev140 | 140 | none | 0 | diagnosis_f1=0.651 |
| exectv2_key_entities_transfer_readout | exectv2_key_entities_dev140_transfer_readout_20260618 | dev140 | 140 | gpt-4.1-mini | 0 marginal | diagnosis_verifier_f1=0.616 |
| exectv2_llm_diagnosis_verifier | exectv2_llm_diagnosis_verifier_v01_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | diagnosis_clinical_headline_f1=0.592 |
| exectv2_llm_diagnosis_verifier | exectv2_llm_diagnosis_verifier_v02_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | diagnosis_clinical_headline_f1=0.619 |
| exectv2_llm_diagnosis_verifier | exectv2_llm_diagnosis_verifier_v03_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | diagnosis_clinical_headline_f1=0.701 |
| exectv2_llm_diagnosis_verifier | exectv2_llm_diagnosis_verifier_v04_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | diagnosis_clinical_headline_f1=0.768 |
| exectv2_llm_diagnosis_verifier | exectv2_llm_diagnosis_verifier_v05_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | diagnosis_clinical_headline_f1=0.837 |
| exectv2_llm_investigations_verifier | exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | investigations_f1=0.872 |
| exectv2_llm_med_inv_verifier | exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618 | dev140 | 140 | gpt-4.1-mini | 1 | investigations_f1=0.496 |
| exectv2_llm_only_all_entities | exectv2_llm_only_all_entities_dev140_gpt41mini_20260612 | dev140 | 140 | gpt-4.1-mini | 1 | benchmark_per_item_f1=0.0 |
| exectv2_llm_only_all_entities | exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612 | full200 | 200 | gpt-4.1-mini | 1 | benchmark_per_item_f1=0.0 |
| exectv2_llm_only_key_entities_structured | exectv2_llm_only_key_entities_structured_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | benchmark_per_item_f1=0.158 |
| exectv2_llm_only_key_entities_structured | exectv2_llm_only_key_entities_structured_v02_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | benchmark_per_item_f1=0.22 |
| exectv2_llm_only_key_entities_structured | exectv2_llm_only_key_entities_structured_v03_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | benchmark_per_item_f1=0.235 |
| exectv2_llm_only_key_entities_structured | exectv2_llm_only_key_entities_structured_v04_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | benchmark_per_item_f1=0.256 |
| exectv2_llm_only_key_entities_structured | exectv2_llm_only_key_entities_structured_v05_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | benchmark_per_item_f1=0.274 |
| exectv2_llm_only_per_entity | exectv2_llm_only_per_entity_dev140_gpt41mini_20260610 | dev140 | 140 | gpt-4.1-mini | 1 (9 max) | sf_benchmark_per_item_f1=0.0 |
| exectv2_llm_only_per_entity | exectv2_llm_only_per_entity_dev140_qwen3635b_20260610 | dev140 | 140 | qwen3.6:35b | 1 (9 max) | sf_benchmark_per_item_f1=0.0 |
| exectv2_llm_only_per_entity | exectv2_llm_only_per_entity_diagnosis_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 (9 max) | diagnosis_clinical_headline_f1=0.282 |
| exectv2_llm_only_per_entity | exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611 | full200 | 200 | gpt-4.1-mini | 1 (9 max) | sf_benchmark_per_item_f1=0.0 |
| exectv2_llm_only_single_pass | exectv2_llm_only_single_pass_dev140_gpt41mini_20260610 | dev140 | 140 | gpt-4.1-mini | 1 | sf_benchmark_per_item_f1=0.0 |
| exectv2_llm_only_single_pass | exectv2_llm_only_single_pass_dev140_qwen3635b_20260610 | dev140 | 140 | qwen3.6:35b | 1 | sf_benchmark_per_item_f1=0.0 |
| exectv2_llm_sf_verifier | exectv2_llm_sf_verifier_v01_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | seizure_frequency_clinical_headline_f1=0.667 |
| exectv2_llm_sf_verifier | exectv2_llm_sf_verifier_v02_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | seizure_frequency_clinical_headline_f1=0.788 |
| exectv2_llm_sf_verifier | exectv2_llm_sf_verifier_v03_dev25_gpt41mini_20260618 | dev25 | 25 | gpt-4.1-mini | 1 | seizure_frequency_clinical_headline_f1=0.831 |
| exectv2_robustness_validation_audit | exectv2_robustness_validation_audit_2026-06-25 | full200 | 200 | gpt-4.1-mini | 0 | overall_f1=0.8503 |
| exectv2_same_core_model_swap | exectv2_2call_no_sf_adjudicator_deepseek_dev140 | dev140 | 140 | deepseek-chat | 2 | clinical_headline_f1=0.8596 |
| exectv2_same_core_model_swap | exectv2_2call_no_sf_adjudicator_gpt41mini_dev140 | dev140 | 140 | gpt-4.1-mini | 2 | clinical_headline_f1=0.8396 |
| exectv2_same_core_model_swap | exectv2_2call_no_sf_adjudicator_qwen36_dev140 | dev140 | 140 | qwen3.6:35b | 2 | clinical_headline_f1=0.8018 |
| exectv2_same_core_model_swap | exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140 | dev140 | 140 | qwen3.6:35b | 2 | clinical_headline_f1=0.8319 |
| exectv2_same_core_model_swap | exectv2_same_core_model_swap_full200_20260625 | full200 | 200 | gpt-4.1-mini + deepseek | 2 | gpt41mini_clinical_headline_f1=0.8356 (deepseek_clinical_headline_f1=0.8566) |
| exectv2_same_core_model_swap | exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200 | full200 | 200 | qwen3.6:35b | 2 | clinical_headline_f1=0.8197 |
| gepa_from_scratch | exectv2_gepa_dedup_gpt41mini_h2mb8_20260628 | dev140 | 140 | gpt-4.1-mini | 1 | clinical_headline_overall_f1=0.7194 |
| gepa_from_scratch | exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628 | dev140 | 140 | gpt-4.1-mini | 4 | clinical_headline_overall_f1=0.7313 |
| gepa_from_scratch | exectv2_gepa_dedup_qwen3p6_35b_h2mb8_20260629 | dev140 | 140 | qwen3.6:35b | 1 | clinical_headline_overall_f1=0.6065 |
| gepa_from_scratch | exectv2_gepa_multifamily_dedup_qwen3p6_35b_h2mb8_20260629 | dev140 | 140 | qwen3.6:35b | 4 | clinical_headline_overall_f1=0.654 |

64/64 registered rows accounted for. 32 (family, normalized-split) cells have
a usable `*_f1` field; the pivot is in the JSON artifact
(`data["pivot"]`).

## Derived number 1 — the 1-to-2-call delta

Already-verified inputs (cited, not recomputed):

- 2-call full200 (gpt-4.1-mini): **0.8356**. Source:
  `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md:19-23`,
  candidate `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`.
  **Registry corroboration:** run_id `exectv2_same_core_model_swap_full200_20260625`,
  field `gpt41mini_clinical_headline_f1` = **0.8356** — exact match, same
  architecture, independently registered.
- 1-call full200 candidates (frontier doc only; these exact candidate labels
  are **not** separately registered under matching run_ids — only the
  underlying JSON artifact `experiments/exectv2_gpt41mini_simplification_frontier_20260624.json`
  exists):
  - `exectv2_gpt41mini_simplification_1call_structured_only` = **0.7571**
  - `exectv2_gpt41mini_simplification_1call_structured_direct_plus_deterministic_prescription` = **0.7730**

**Delta, stated explicitly:**

- 2-call vs pure 1-call: 0.8356 − 0.7571 = **+0.0785**
- 2-call vs 1-call + free deterministic prescription repair: 0.8356 − 0.7730 = **+0.0626**

**Confirmed**, not corrected: both land inside the plan's predicted
"+0.063 to +0.083" window (they *are* that window's exact endpoints).

Secondary, independent dev140 corroboration (different specific configs, not
a repeat of the same measurement): registry run_id
`exectv2_v09_single_gpt_simplification_study_dev140_20260621`, field
`gpt_only_dictionary_clinical_headline_f1` = 0.7552 (single GPT pass + a
standard dictionary, dev140) vs run_id
`exectv2_2call_no_sf_adjudicator_gpt41mini_dev140`, field
`clinical_headline_f1` = 0.8396 (2-call, same split) → delta **+0.0844**.
Same direction, same order of magnitude, slightly above the full200 window's
upper bound — consistent with, not identical to, the full200 measurement
(different exact 1-call config: single-pass-with-dictionary vs
structured-only).

## Derived number 2 — hybrid premium by split

This is the number the review's "hybrid is worth +0.2 F1, split-dependent by
roughly 5x (full200 hybrid premium ~+0.0076 vs. dev140 ~+0.076)" claim was
checking. **It does not exist as a single number in the registry — it turns
out to conflate two different, non-commensurable comparisons.** Both are
computed fresh below, each fully cited.

### 2a. Hybrid vs the deterministic-augmented "2-call" baseline (matched split, model held constant)

The only family pair with registered rows for the SAME architecture at BOTH
`full200` and `dev140`, gpt-4.1-mini held constant:

| | full200 | dev140 | run_id (full200) | run_id (dev140) |
| --- | ---: | ---: | --- | --- |
| Hybrid (`exectv2_holistic_finding_assembly`, v08-shaped) | 0.8502 | 0.9152 | `exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624` | `exectv2_v09_single_gpt_simplification_study_dev140_20260621` (field `v08_dev140_comparator_f1`) |
| Baseline (`exectv2_same_core_model_swap`, "2-call") | 0.8356 | 0.8396 | `exectv2_same_core_model_swap_full200_20260625` (field `gpt41mini_clinical_headline_f1`) | `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140` |
| **Premium (hybrid − baseline)** | **+0.0146** | **+0.0756** | | |

Ratio: 0.0756 / 0.0146 = **5.18x**. The full200 hybrid number is corroborated
independently by run_id `exectv2_robustness_validation_audit_2026-06-25`
(field `overall_f1` = 0.8503, "the current-code v08-shaped full-200
artifact" — same underlying artifact, different analysis pass). The dev140
hybrid number (0.9152) is **not itself an independently registered run_id**
— it is embedded as a field inside the v09 study row, sourced originally from
`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`'s
`clinical_headline` score view. A ~0.0003-level rounding variant of the same
artifact (0.9155) is the number actually repeated across ~15 other docs
(e.g. `docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md:25`)
but **is not itself a registry `primary_metrics` value under any run_id**.
Using 0.9155 instead of 0.9152 moves the dev140 premium to +0.0759 and the
ratio to 5.20x — no material difference.

**Verdict on this framing:** the ~5x split-dependence ratio the review cited
**is corroborated** (5.18–5.20x vs. the claimed "~5x"), and the dev140
magnitude (+0.0756/+0.0759) closely matches the claimed "~0.076". The
**full200 magnitude does not match**: this computation gives **+0.0146**, not
the claimed "+0.0076" — about 2x larger than what was informally cited. No
full200 row combination in the registry reproduces +0.0076 exactly.

### 2b. The same comparison is not robust to which baseline model is used

`exectv2_same_core_model_swap` also has a DeepSeek row at both splits, and
DeepSeek is the *stronger* baseline at both:

| | full200 | dev140 | run_id |
| --- | ---: | ---: | --- |
| Baseline, DeepSeek | 0.8566 | 0.8596 | `exectv2_same_core_model_swap_full200_20260625` (field `deepseek_clinical_headline_f1`) / `exectv2_2call_no_sf_adjudicator_deepseek_dev140` |
| Hybrid (gpt-4.1-mini only — **no DeepSeek hybrid row exists at either split**) | 0.8502 | 0.9152 | (as above) |
| **Premium (hybrid − DeepSeek baseline)** | **−0.0064** | **+0.0556** | |

Once the strongest *available* non-hybrid baseline is used instead of holding
the model constant, the full200 "hybrid premium" **goes negative** — the
2-call DeepSeek baseline slightly outperforms the only registered full200
hybrid row. This is flagged, not resolved: no DeepSeek-hybrid full200 run
exists to separate "hybrid architecture helps" from "gpt-4.1-mini vs DeepSeek
as the hybrid's base model" as the driver. At minimum, this shows the
"hybrid is worth +0.2 F1" framing cannot be read as robust across model
choice at full200 scale.

### 2c. Where the "+0.2 F1" figure most likely actually comes from — and why it isn't a split-dependence measurement at all

`gepa_from_scratch` has **zero full200 rows** — all 4 registered GEPA rows
are `split="dev", row_count=140`. This is exactly the "no full200 GEPA row
exists" case the plan's instructions anticipated; it is stated here
explicitly rather than forced into a comparison.

At dev140 only:

| | dev140 F1 | run_id |
| --- | ---: | --- |
| Hybrid (v08) | 0.9152 (0.9155 widely-cited variant) | see 2a |
| GEPA per-family, gpt-4.1-mini, 4 calls/letter | 0.7313 | `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` |
| GEPA monolith, gpt-4.1-mini, 1 call/letter | 0.7194 | `exectv2_gepa_dedup_gpt41mini_h2mb8_20260628` |

- Hybrid − GEPA per-family: 0.9152 − 0.7313 = **+0.1839**
- Hybrid (widely-cited 0.9155) − GEPA monolith: 0.9155 − 0.7194 = **+0.1961**

Both land almost exactly on "+0.2". This — hybrid vs. GEPA's
instruction-tuning ceiling, **entirely at dev140** — is the comparison
already on record elsewhere (`docs/research/exectv2_gepa_qwen_cross_model_2026-06-30.md`
line 29: "v08 multi-stage hybrid | GPT-4.1-mini | 0.9155"; project memory:
"single-pass GEPA PLATEAUS ~0.73, ~0.18 below hybrid 0.9155"). It is **not**
a full200-vs-dev140 split comparison — it cannot be, since GEPA has no
full200 row — and it uses a *different, much weaker* baseline (GEPA's
best instruction-tuned single/multi-signature prompt) than the "2-call"
deterministic-augmented baseline used in 2a/2b.

### Correction, stated plainly

The review's single claim — "hybrid is worth +0.2 F1, split-dependent by
roughly 5x (full200 +0.0076 vs. dev140 +0.076)" — **conflates two different,
non-commensurable comparisons that happen to share a rough order of
magnitude at dev140**:

1. **Hybrid vs. GEPA (instruction-tuning ceiling), dev140 only: real, ≈+0.18
   to +0.20 F1.** Cannot be tested for split-dependence — no full200 GEPA row
   exists in the registry, full stop.
2. **Hybrid vs. the 2-call deterministic-augmented baseline, matched at both
   splits, gpt-4.1-mini held constant: real, +0.0146 full200 / +0.0756
   dev140, ratio 5.18x.** This is the only piece of the original claim that
   is genuinely split-comparable from registered rows — and even it is not
   robust to baseline-model choice (2b: goes negative at full200 against the
   stronger available DeepSeek baseline, for lack of a DeepSeek-hybrid row to
   control for the model confound).

Neither comparison alone supports "the hybrid is worth +0.2 F1,
split-dependent by ~5x" as a single, internally consistent statement — the
"+0.2" belongs to comparison 1 (dev140-only, no split-dependence
computable), and the "~5x split-dependent" ratio belongs to comparison 2
(real, but against a ~+0.015–0.076 premium, not a +0.2 one, and its full200
sign is baseline-model-dependent).

## F1-per-cost ranking

Full200, gpt-4.1-mini (the clean single-model call-count ladder):

| calls/letter | architecture | full200 F1 | source |
| --- | --- | ---: | --- |
| 1 | structured-only single pass | 0.7571 | frontier doc |
| 1 + free deterministic Rx repair | structured + deterministic prescription | 0.7730 | frontier doc |
| 2, **without** deterministic stack | same-core, no SF adjudicator, dictionary/lens/projection removed | 0.7736 | `experiments/exectv2_component_off_replay_full200_20260626.md:35-37` |
| 2, **with** deterministic stack | same-core, no SF adjudicator (the registered 2-call number) | 0.8356 | registry + frontier doc (exact match) |
| 3 | + Dx decomposer + SF adjudicator | 0.8426 | frontier doc |
| hybrid (multi-call, not on this axis) | v08, 4-lane | 0.8502 (0.8503 corroboration) | registry |

The "with/without deterministic stack" pair isolates a *component-off
replay* on the frozen 2-call base, not a separate call-count step: removing
`standard_dictionary` (+0.0186), `residual_semantic_lens` (+0.0117), and
`headline_projection` (+0.0317) from the registered 0.8356 result drops it to
0.7736 — sum of contributions **+0.0620**, for **0 marginal LLM calls**
(`experiments/exectv2_component_off_replay_full200_20260626.md:35-37`,
gpt41mini row).

**Re-verifying the review's "~9x" claim:** deterministic-stack gain
(+0.0620, 0 marginal calls) ÷ 3rd-call marginal gain (+0.0070, at 1.5x call
budget) = **8.86x**. Confirmed — "~9x" is the correct rounding of the exact
figure.

**Cost-inefficiency of the 3rd call, made explicit:** going from 2 calls to 3
calls (+50% budget) buys +0.0070 F1 at full200
(`docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md:19-23`)
— the worst marginal $/F1 of any step on this ladder, and roughly 9x worse
than a purely deterministic, zero-marginal-call post-processing pass over
the *same* 2-call base.

**GEPA's calls do not buy hybrid-grade cost efficiency either.** At dev140,
GEPA's 4-calls/letter per-family program (0.7313) is *beaten* by the
1-call/letter hand-tuned "GPT-only + standard dictionary" config (0.7552,
run_id `exectv2_v09_single_gpt_simplification_study_dev140_20260621`, field
`gpt_only_dictionary_clinical_headline_f1`) — more calls, worse F1, when the
extra calls are spent on raw per-family instruction tuning rather than an
architecturally different (deterministic-augmented, verify/arbitrate) shape.
Reinforces the already-closed finding that pipeline *shape*, not raw call
count, is what buys F1 past ~0.75–0.84 (`docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`).

## What is explicitly not computable from the current registry

- **A full200 GEPA row does not exist** — 0 of 4 `gepa_from_scratch` rows use
  a full200-normalized split; all are `dev`, `row_count=140`. Any
  GEPA-vs-hybrid comparison is therefore dev140-only and cannot be checked
  for split-dependence without a new full200 GEPA run (out of scope for this
  zero-LLM item; flagged, not run).
- **No hybrid row exists for any model other than gpt-4.1-mini**, at either
  split. Section 2b's negative-premium-at-full200 result cannot be
  attributed to "hybrid architecture" vs. "gpt-4.1-mini vs. DeepSeek as base
  model" without a DeepSeek-hybrid run.
- **The frontier doc's 1-call and 3-call full200 candidates are not
  independently registered** under matching run_ids (only the underlying
  `experiments/exectv2_gpt41mini_simplification_frontier_20260624.json`
  artifact exists) — Derived number 1 above is stated from that doc directly,
  cross-checked against the one registry row (`exectv2_same_core_model_swap_full200_20260625`)
  that is the same architecture as its 2-call candidate.

## Definition of done

- `experiments/exectv2_cost_quality_matched_split_table.py` written, runs
  clean (`uv run python experiments/exectv2_cost_quality_matched_split_table.py`),
  zero LLM calls, covers all 64 registered rows across the full 23-family
  set including `gepa_from_scratch`.
- `experiments/exectv2_cost_quality_matched_split_table_20260701.json`
  written (full per-row `*_f1` fields, pivot, and derived numbers).
- 1-to-2-call delta: **confirmed** (+0.0626 to +0.0785, matching the plan's
  predicted window exactly).
- Hybrid-premium-by-split: **computed fresh, not found pre-existing** — real
  but conflated in the reviewed claim; corrected above (section "Correction,
  stated plainly").
