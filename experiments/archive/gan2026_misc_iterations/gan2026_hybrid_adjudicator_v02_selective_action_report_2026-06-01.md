# Gan 2026 Hybrid Adjudicator V0.2 Selective-Action Report

This is a validation-development artifact over saved v0.2 rows. It is not a holdout result, benchmark claim, or permission to inspect locked-test rows.

- Candidate: `hybrid_rules_candidates_llm_adjudicator_v0.2`
- Split: `validation`
- Split manifest: `gan2026_split_v1`
- Rows: 250
- Source artifact: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.jsonl`

## Selective-Action Summary

| Mode | Action rate | Actions | Wrong-to-correct | Correct-to-wrong | Precision | Recall | Boundary churn | Evidence-valid changes | Fallback/abstain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_change | 0.0360 | 9 | 1 | 2 | 0.3333 | 0.2500 | 6 | 2 | 7 |
| gated_change | 0.0320 | 8 | 0 | 2 | 0.0000 | 0.0000 | 6 | 2 | 0 |
| flag_only | 0.0400 | 10 | 0 | 0 |  | 0.0000 | 0 | 0 | 0 |

## Validation Hard Slices

| Slice | Rows | Raw precision | Raw W->C | Raw C->W | Gated precision | Gated W->C | Gated C->W | Flag precision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| deterministic_miss | 4 | 1.0000 | 1 | 0 |  | 0 | 0 | 1.0000 |
| temporal_conflict | 209 | 0.0000 | 0 | 1 | 0.0000 | 0 | 1 | 0.0000 |
| seizure_free_overreach | 71 | 1.0000 | 1 | 0 |  | 0 | 0 | 0.1250 |
| unknown_no_reference_boundary | 27 |  | 0 | 0 |  | 0 | 0 | 0.0000 |
| cluster_or_diary | 219 | 0.3333 | 1 | 2 | 0.0000 | 0 | 2 | 0.1111 |
| shorthand_interval_range | 59 |  | 0 | 0 |  | 0 | 0 | 0.0000 |
| candidate_absent_or_weak | 4 | 1.0000 | 1 | 0 |  | 0 | 0 | 1.0000 |

## Slice Definitions

### deterministic_miss

- Rows: 4
- Membership: Artifact row is validation, gold row_ok=True, and deterministic top is Purist-wrong.
- Primary metric: wrong-to-correct rate and evidence validity

### temporal_conflict

- Rows: 209
- Membership: Validation note contains current/recent/now language plus historical/previous/stale frequency language.
- Primary metric: regression-controlled correction rate

### seizure_free_overreach

- Rows: 71
- Membership: Deterministic top predicts seizure-free/no-event while gold is not seizure-free, or text combines seizure-free language with breakthrough/event language.
- Primary metric: overreach correction precision

### unknown_no_reference_boundary

- Rows: 27
- Membership: Deterministic top predicts no seizure frequency reference while seizure/event discussion is present, or the LLM changes no-reference to unknown.
- Primary metric: flag precision and scorer-equivalent churn

### cluster_or_diary

- Rows: 219
- Membership: Gold label or text contains cluster, diary, month-list, calendar, cumulative count, or distributed-count signals.
- Primary metric: hard-slice F1 plus correction precision

### shorthand_interval_range

- Rows: 59
- Membership: Text contains q-interval shorthand, every-interval, inter-seizure interval, range, or maximum-burden language.
- Primary metric: format-normalization correction precision

### candidate_absent_or_weak

- Rows: 4
- Membership: Deterministic top is Purist-wrong and the candidate-recall proxy does not recall the gold Purist category.
- Primary metric: flag-only utility, not final-label promotion

## Interpretation

The gated final still regresses more deterministic-correct rows than it fixes. Keep v0.2 out of prediction-bearing promotion and inspect hard-slice behavior.

Stop rule: Promote only if changed-label precision is high on dominant deterministic-miss families with evidence-valid accepted changes and low regression cost; otherwise revise, keep diagnostic, or reject added complexity.
