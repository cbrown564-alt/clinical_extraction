# Retention candidate table (2026-08-16)

Ledger owner: [REGENERATION.md](../../REGENERATION.md).
Taxonomy: [hierarchical matrix](retention_slice_hierarchical_retention_matrix_2026-08-16.md).
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md).

Status: **inventory complete for every slot**.
ExECT current-hybrid prompt slots are assigned in
[prompt variant slots](../exectv2/prompt_variant_slots_2026-08-16.md).
Unused ExECT prompt-zoo dumps and abandoned LLM lanes are pruned.
No model calls. No locked-row inspection.

This table is step 2 of the planned review. It is not a deletion list
for retained slots. The 2026-08-16 living-stack freeze and the
docs/scripts confident cut are landed. Keep-set and leftovers:
[retention keep and leftovers](retention_keep_and_leftovers_2026-08-16.md).

## Parallel-track rule

| Family | Now | After ExECT close |
| --- | --- | --- |
| Architecture slots 1–3 | Assign and keep | Unchanged unless a new architecture appears |
| Gan prompt slots 1–3 | Assign | Unchanged |
| Deterministic-rules slots 1–3 | Assign | Unchanged |
| ExECT prompt slots 1–3 | `v0.9.24`, cheap stack, mention-unit v2 | Zoo / SI / MU v1 pruned; slots unchanged |
| ExECT `v08` reference cell | Keep outside the current-hybrid prompt cap | Unchanged |
| Model-generation comparisons | Outside the prompt cap | Unchanged |
| Duplicate collapse | Non-ExECT-iteration families only | Optional further non-slot cull |

## Architecture / pipeline (`llm_with_rules`)

| Slot | Variant | Status | Protocol | Result | Machine artifact | Closure | Claim | Retain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Current one-call structured hybrid | Selected | [0041](../../decisions/0041-single-call-exect-model-comparison.md), [0047](../../decisions/0047-full-canonical-pipeline-orchestrator-refactor.md), [0050](../../decisions/0050-current-stack-hybrid-primary-fills.md), [current-stack runbook](../../runbooks/current_stack_six_model_replay.md) | [fills.json](../../../experiments/current_stack/latest/fills.json); [six-model report](../shared/six_model_comparison_report_2026-07-18.md) | [SOURCES.json](../../../experiments/current_stack/SOURCES.json) and named sidecars; Gan LFS rows under `experiments/gan2026_six_model_validation_20260718/` | Architecture manifests; `scripts/verify_reference_evidence.py`; `scripts/run_current_stack.py` | Selected production hybrid for both tasks | Keep. Six reference cells remain the minimum matrix; ExECT hybrid reference is historical `v08`, not this architecture |
| 2 | GEPA dedup LLM-only program | Negative comparator | [Canon 08](../../canon/08_gepa.md); launcher `experiments/gepa_h2_minibatch_exectv2.py` | `experiments/exectv2_gepa_dedup_gpt41mini_h2mb8_20260628.md` | `experiments/exectv2_gepa_dedup_gpt41mini_h2mb8_20260628.jsonl` (tracked; not LFS) | `src/.../exectv2/gepa/{run_gepa,program,metric,dedup_adapter}.py` | Optimizer-only development negative (`clinical_headline` 0.7393); not hybrid parity | Keep this one run. Verify-stage GEPA is report-only; `program_multistage.py` is missing |
| 3 | Agentic / multi-agent ceiling | Negative comparator | Predeclaration missing on disk (`docs/experiments/gan2026/agentic/...`) | [Canon 11](../../canon/11_agentic_exploration.md); [redo results](../gan2026/gan2026_agentic_redo_results_2026-07-01.md) | **Missing.** `experiments/gan2026_agentic_redo_battery_hard50_results.jsonl` pruned in `021a95cf` | Source `.../gan2026/agentic/` missing; Git lineage `b2b1e3f3` / `da53aa3d` | Decomposition gained on Gan hard50 but failed the promotion gate | Keep the restored reports and canon. Restoring jsonl is optional and is not required to close the slot |

`v08` holistic assembly is the ExECT hybrid **reference cell**. It is
not a current-hybrid prompt slot and not a fourth architecture.
Two-call swap configs are Decision 0040 supporting evidence, not a
slot. Joint/`combined` is a policy (Decision 0045), not a pipeline
graph.

## Gan 2026 prompt family

| Slot | Variant | Status | Protocol | Result | Machine artifact | Closure | Claim | Retain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `gan2026_hybrid_structured_events_v0.5` | Selected | [0043](../../decisions/0043-gan-hosted-comparison-uses-v05-prompt.md); [dev750 protocol](../../experiments/gan2026/gan2026_matched_v05_dev750_protocol_2026-07-27.md) | [dev750 panel](../../experiments/gan2026/gan2026_matched_v05_dev750_panel_2026-07-27.md) | `experiments/gan2026_matched_v05_dev750_panel_20260727.json` | `configs/gan2026/six_model_v05_dev750_20260727.json`; snapshot `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.5.txt` | Shared six-model hybrid instruction | Keep. Do not collapse into v0.7 or current-stack readouts |
| 2 | Luna prompt variants | Diagnostic; not selected | [protocol](../../experiments/gan2026/gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md) | [report](../gan2026/luna_prompt_variants_report_2026-07-30.md) | `experiments/gan2026_luna_prompt_variants_dev750_20260730/panel.json` | `configs/gan2026/luna_prompt_variants_dev750_20260730.json`; `exemplar_pack.json` | Luna-only A/B/C ablation under frozen schema | Keep one slot. Collapse sibling Luna markdown into this owner later |
| 3 | DeepSeek Unknown (`v0.8_deepseek_unknown`) | Rejected / stopped | [protocol](../../experiments/gan2026/gan2026_deepseek_unknown_prompt_dev750_protocol_2026-07-31.md) | [thread](../gan2026/deepseek_unknown_competence_thread_2026-07-31.md) | `experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json` (170-row pilot) | `configs/gan2026/deepseek_unknown_prompt_dev750_20260731.json` | Model-adaptation prompt failed UNK-slice gates; full-750 aborted | Keep as the negative prompt occupant. Do not resume U to 750 for retention |

REGENERATION.md previously listed Gemini 3.7 Flash beside DeepSeek as
slot 3. That is wrong. Gemini reuses `v0.5` (Gan) and `v0.9.24`
(ExECT). It is a roster / model-generation comparison (Decisions
0051 / 0052), outside the prompt cap. Decision 0053 `final` is
lineage-only (Luna `dev750` −3/750, not selected).

Living Gemini owners:
[successor protocol](../shared/six_model_gemini37flash_successor_protocol_2026-08-13.md),
[successor report](../shared/six_model_gemini37flash_successor_2026-08-13.md),
`experiments/gemini37flash_holdout_20260813.json`.

## ExECT prompt family

| Slot | Variant | Status | Protocol | Result | Machine artifact | Claim | Retain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `exectv2_hybrid_key_family_event_ledger_v0.9.24` | Selected live baseline | [0046](../../decisions/0046-exect-primary-method-comparison-boundary.md); [0050](../../decisions/0050-current-stack-hybrid-primary-fills.md) | Living fills; prune answers under [THREAD_MAP](../../THREAD_MAP.md#exect-v0924-leave-one-out-prune) | Current-stack sidecars; prompt identity in `src/.../key_entities_structured/constants.py` | Six-model and replay identity | Keep. Default stays `v0.9.24` |
| 2 | Cheap stack `v0.9.44_cheap_stack_further_prunes` | Retained cheap variant; not selected | [slot-2 `dev140`](../exectv2/v0924_cheap_slot2_dev140_protocol_2026-08-17.md) | [stacked `dev20`](../exectv2/v0924_cheap_further_prune_stacked_luna_dev20_2026-08-17.md) | `experiments/exectv2_v0924_cheap_further_prune_stacked_luna_dev20_20260817/comparison.json` | Stacked further prune; three-model `dev140` remasure in progress | Keep as the cheap slot. Do not promote. |
| 3 | `exectv2_mention_unit_v2` | Retained representation alternative; not selected | [v2 `dev20` protocol](../exectv2/mention_unit_v2_fork_a_luna_dev20_protocol_2026-08-16.md) | [v2 `dev20`](../exectv2/mention_unit_v2_fork_a_luna_dev20_2026-08-16.md); later catalogs on the [Fork A door](../../THREAD_MAP.md#exect-llm-representation-fork-a) | `experiments/exectv2_mention_unit_v2_luna_dev20_20260816/comparison.json` | Mention-unit prompt; encoder pairing still open | Keep the prompt identity. Default encoder stays `landed`. |

Assignment owner:
[prompt variant slots](../exectv2/prompt_variant_slots_2026-08-16.md).
`v08` remains the reference-cell bundle outside this table.

## Deterministic rules and projection

| Slot | Variant | Status | Protocol | Result | Machine artifact | Closure | Claim | Retain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Production `rules_only` | Selected | [E5](../exectv2/rules_only_campaign_e5_remeasure_2026-08-15.md); [G5](../gan2026/rules_only_campaign_g5_remeasure_2026-08-15.md) | [E5](../exectv2/rules_only_campaign_e5_remeasure_2026-08-15.md); [G5](../gan2026/rules_only_campaign_g5_remeasure_2026-08-15.md) | `experiments/exectv2_rules_only_campaign_e5_remeasure_20260815.json`; Gan cell `experiments/gan2026_rules_only_canonical_validation750_20260810.jsonl` | ExECT `deterministic/`; Gan `runners/deterministic_canonical.py` | Standalone deterministic floor: ExECT 0.9042 / 0.7937; Gan 329/450 | Keep both task owners. Nine-entity `20260714` JSON is a secondary paper-metric subject, not the Decision 0046 fill |
| 2 | Hybrid state projection and bounded repair | Selected attached rules | [ExECT stage ablation](../exectv2/hybrid_stage_ablation_2026-08-06.md); [Gan stage ablation](../gan2026/hybrid_stage_ablation_2026-08-06.md); [SF v0.14 door](../../THREAD_MAP.md#exect-seizurefrequency-projection-v014) | Same reports | `experiments/exectv2_hybrid_stage_ablation_20260806.json`; `experiments/gan2026_hybrid_stage_ablation_20260806.json` | `sf_state_projection.py` v0.14; Gan hybrid assembly / repair | Deterministic layers that change hybrid answers | Keep the two peer ablation packages. Dated SF predicate study notes are pruned; live over-read guard remains |
| 3 | Attribution and component ablation | Diagnostic | [Gan post-panel](../../experiments/gan2026/gan2026_six_model_post_panel_replay_protocol_2026-07-20.md); [Qwen/Sol](../../experiments/gan2026/gan2026_qwen_sol_rule_benefit_audit_protocol_2026-07-20.md); ExECT component audit 2026-07-14 | Matching 2026-07-20 / 2026-07-14 reports | `experiments/gan2026_six_model_post_panel_attribution_20260720.json`; `experiments/gan2026_qwen_sol_rule_benefit_audit_20260720.json`; `experiments/exectv2_llm_with_rules_component_audit_full200_20260714.json` | `scripts/analyze_gan2026_six_model_post_panel.py`; ExECT `component_ablation/definitions.yaml` | Rescue provenance and component-off harm | Keep these three named packages. Cross-task ablation is closure, not a fourth slot |

## Outside the prompt cap

| Component | Status | Owner | Action |
| --- | --- | --- | --- |
| DeepSeek V4 Flash 0731 matched comparison | Closed model-generation | [report](../shared/deepseek_v4_flash_0731_matched_comparison_report_2026-08-03.md); `experiments/deepseek_v4_flash_0731_matched_comparison_20260803.json` | Keep outside prompt slots |
| Gemini 3.7 Flash roster | Closed model-generation | Decisions 0051 / 0052; successor report above | Keep outside prompt slots |
| Qwen 3.8 27B | Reserved local successor | [protocol](../shared/qwen38_27b_candidate_protocol_2026-08-14.md) | Keep outside prompt slots; not a Decision 0051 swap |
| Gan `final` prompt | Lineage; not selected | [0053](../../decisions/0053-gan-structured-events-final-prompt.md) | Lineage summary, not a fourth Gan prompt |

## Named path corrections

REGENERATION.md used shorthand filenames. Living replacements:

| Named in ledger | Living path |
| --- | --- |
| `six_model_v05_dev750_20260727.json` | config `configs/gan2026/six_model_v05_dev750_20260727.json`; panel `experiments/gan2026_matched_v05_dev750_panel_20260727.json` |
| `luna_prompt_variants_dev750_20260730.json` | `experiments/gan2026_luna_prompt_variants_dev750_20260730/panel.json` |
| `deepseek_unknown_prompt_dev750_20260731.json` | config under `configs/gan2026/`; machine compare is the UNK-slice JSON above |
| `six_model_successor_gemini37flash_20260813.json` | config `configs/gan2026/six_model_successor_gemini37flash_20260813.json`; results are roster artifacts, not a prompt JSON |

## Collapse candidates (non-ExECT-iteration only)

The 2026-08-16 experiments dump prune removed non-owner dumps (diagnosis
campaigns, joint policy, v19 SF studies, superseded six-model forests,
calibration/gemma probes, and dated panel trees not named by
`SOURCES.json` / Decision 0050 / the retained manifest). The follow-on
campaign-notes prune removed closed uncited protocol+report pairs
(rules-only E0–E4 intermediates, family-lens, Luna siblings,
cluster-burden, structured-prompt bloat/convention-migration notes, and
similar). Living owners above stay. Remaining optional collapses:

1. ~~Luna variant sibling markdown that only restates the 2026-07-30 panel.~~
   Done in the campaign-notes prune (dated-count / residual companions
   removed; Luna report remains).
2. Pre-E5 four-family `20260801` headline JSONs and `20260806` letter-score
   dumps removed 2026-08-16 (not named by SOURCES / retained manifest /
   Decision 0050 / slot or retention keep tables). Decision 0046 still
   names the living `test60` `20260815` headline JSON.
3. Living-stack freeze 2026-08-16 rebound reference cells onto
   `SOURCES.json` / `latest/fills.json` / E5 and removed the 11 Aug
   hashed forests (2-call, `v08` producers, July 18 v0.7, 13 Aug
   explorer, mini 0039, pre-0731, historical sidecars). `runs/20260815/`
   was a `latest/` duplicate and is gone. `runs/20260813/` remains.
4. Protocol docs outside the machine manifest that have no focused
   evidence thread (deferred cull from 2026-08-02).
5. Optional further `*_sf_state_projection_combined.jsonl` review for
   **closed** SF campaign lanes only (`.md` allowlist companions kept).
6. `ACTIVE_ROADMAP` completed-link thinning (deferred 2026-08-03).

Not collapse candidates: the three assigned ExECT prompt slots, their
Markdown prune answers, mention-unit v2 artifacts, retained manifest
paths, `gan2026_six_model_current_stack_dev750_replay_20260813/` (trace
explorer replay), or paper-cited companions.

## Next on this track

1. Dependency-map remaining non-slot collapse candidates above
   (callers, manifest, registry, tests).
2. Collapse one safe non-ExECT family after that map.
3. Do not restore pruned ExECT zoo drafts as live slots.
