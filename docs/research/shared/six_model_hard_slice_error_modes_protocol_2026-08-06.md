# Protocol: error modes inside six-model hard slices

Date: 2026-08-06  
Status: complete; no-call development analysis  
Parent: [category-cut performance](six_model_category_cut_performance_2026-08-06.md)  
Framework: [task-shape framework](task_shape_framework_2026-08-06.md)

## Primary question

Inside the gold categories that remain hard on development, what **shared
error modes** dominate across the six models—and are those modes selection,
label-shape, abstention, or (for ExECT) empty-gold / state-set problems?

## Why it matters

The category-cut study showed *where* competence collapses. This study asks
*how* it collapses on those floors, without inventing new gold or assuming
rules will be present.

## Surfaces in scope

| Slice | Track | Surface | Why |
| --- | --- | --- | --- |
| `ordinary_point_rate` | Gan `dev750` | `llm` | Strict **z** without rules; largest gold mass |
| `cluster_burden` | Gan `dev750` | `llm` | Strict **z** without rules |
| `cluster_burden` | Gan `dev750` | `llm_with_rules` | Practical floor after rules |
| SeizureFrequency letters | ExECT `dev140` | `llm` and `llm_with_rules` | Practical floor on both surfaces |

Holdout rows stay sealed. No new model calls. No prompt, rule, or scorer edits.

## Prediction sources

Same retained files as the category-cut artifact:

- Gan `llm`: `experiments/gan2026_six_model_validation_20260718/*--llm_only.jsonl`
- Gan `llm_with_rules`: matched v0.5 attribution + current-floors changed-row patch
- ExECT: assembled single-call JSONL; `raw_lane_mentions` (`llm`) and
  `predicted_mentions` (`llm_with_rules`), scored with clinical-headline unit keys

## Error-mode method

1. Restrict to the named gold slice (Gan a_priori bucket, or ExECT SF family
   letter score).
2. Assign one mutually exclusive primary error mode per wrong row / imperfect
   letter from the **scored** predicted label shape (Gan `llm_only`
   `decision_record.final_label`, which is what Purist comparison uses; model-
   boundary raw label kept as a diagnostic field) or unit-key multiset mismatch
   (ExECT).
3. Report per-model mode counts, six-model consensus wrongs, and a small set of
   development exemplars (ids + structured labels only; no note text).
4. For Gan `llm` ordinary rates, also report how often hybrid rescue flips the
   same row to Purist-correct (rules lift on that floor, not a claim that rules
   are free).

### Gan primary modes (wrong Purist only)

Ordinary-rate gold:

| Mode | Rule |
| --- | --- |
| `over_abstain_unknown` | scored pred `unknown` |
| `over_abstain_no_reference` | scored pred `no seizure frequency reference` |
| `false_seizure_free` | scored pred seizure-free |
| `wrong_point_rate_selection` | scored pred ordinary point rate, wrong Purist |
| `false_range` / `false_multiple_word` / `false_cluster_structure` | wrong label family |
| `parse_or_call_failure` / `other_malformed_or_unparsed` | residual |

Cluster gold:

| Mode | Rule |
| --- | --- |
| `incomplete_cluster_grammar` | pred has `cluster` but not `per cluster` |
| `wrong_cluster_parameters` | pred has fullish cluster grammar, still wrong |
| `dropped_to_smooth_rate` | pred is non-cluster rate/range |
| `collapse_to_unknown` / `collapse_to_no_reference` | sentinel collapse |
| `false_seizure_free` | scored pred seizure-free |
| `parse_or_call_failure` / `other_malformed_or_unparsed` | residual |

Secondary flags (non-exclusive): `pragmatic_near_miss` on Gan `llm` when
Pragmatic is correct.

### ExECT SF primary modes (imperfect letter unit-key match)

| Mode | Rule |
| --- | --- |
| `correct_empty` / `correct_nonempty` | perfect multiset match |
| `empty_gold_spurious` | gold SF empty, prediction non-empty |
| `missed_all_sf` | gold SF non-empty, prediction empty |
| `missed_states_only` | only false negatives |
| `extra_states_only` | only false positives |
| `substituted_or_mixed` | both FP and FN |

Also tally coarse state tokens (`active-rate`, `seizure-free`, `unknown`) among
missed and extra keys.

## Required outputs

1. Machine artifact with per-model mode counts, consensus wrong ids, and
   stratified exemplars.
2. Narrative report answering the dominant shared modes for each slice.
3. Handoff update to category-cut “Next”, `PROJECT_STATUS.md`, and short maps.

## Stop rule

- **Answer** if each in-scope slice has regenerable mode counts and a clear
  dominant shared mechanism (or an explicit split between two mechanisms).
- **Blocked** only if retained prediction files cannot reconstruct the same
  development denominators as the category-cut study.

## Claim boundary

- Development mechanism evidence on named hard slices.
- Mode labels are analyst heuristics over saved predictions, not new gold.
- Not holdout category competence, not a Decision 0046 rewrite, and not a
  license to tune prompts/rules from these exemplars beyond ordinary
  development practice.
- DeepSeek Gan `llm` `dev750` remains pre-0731.
