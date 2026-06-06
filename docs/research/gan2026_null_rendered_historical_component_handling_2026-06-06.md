# Gan 2026 Null-Rendered Rows: Historical Component Handling

Date: 2026-06-06

Question: how did the pre-reset staged architecture handle the 234 validation750 rows that are null-rendered in the GPT-4.1-mini clinical-assessment reset pass?

This is validation-development archaeology. It compares the reset null-render surface against the 2026-06-04 readiness decision and saved staged-hybrid artifacts. It does not make a benchmark-comparable claim.

## Inputs

- Reset null-render analysis: `experiments/gan2026_validation750_null_rendered_row_error_analysis_gpt41mini_v0_2026-06-06.jsonl`
- Readiness decision: `docs/research/gan2026_architecture_assembly_readiness_decision_2026-06-04.md`
- Old decision layer: `experiments/gan2026_staged_hybrid_decision_layer_validation750_no_call_2026-06-04.jsonl`
- Old component matrix: `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv`
- RQ4/RQ5/RQ6/RQ7/RQ9 component answers under `docs/research/gan2026_rq*_2026-06-04.md`

## Bottom Line

The old architecture did not treat these rows as a single verifier problem. It split them across several components:

- deterministic/state-graph substrate and benchmark repair for parseable labels;
- ACD projection policies for known benchmark conventions;
- rich selected state and suspicious-state flags for ambiguity boundaries;
- selective boundary candidates for hard missing states;
- selective safety floor for no-regression label changes;
- RQ9 action routing for abstain/review/monitoring.

On the exact 234 current null-rendered rows, the old staged decision layer did this:

| Old action | Rows |
| --- | ---: |
| `predict` | 215 |
| `abstain` | 14 |
| `human_review` | 5 |

Old development accounting on those rows:

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 201 |
| `W_to_abstain` | 5 |
| `C_to_abstain` | 9 |
| `W_to_W` | 14 |
| `W_to_review` | 5 |

So the old system recovered many currently-null rows, but not cleanly: it predicted on 215/234 and had 14 prediction-bearing Purist-wrong rows in development accounting. The useful thing to recover is the component logic, not the whole assembly as-is.

## Theme Crosswalk

| Current null-render theme | Rows | Old predict | Old abstain | Old review | Old predicted-correct | Old predicted-wrong | Historical handling | Port-forward recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `additive_mixed_window_or_vague` | 24 | 24 | 0 | 0 | 19 | 5 | Old assembly usually predicted via hybrid adjudicator plus adapters, but this was not a mature solved component; RQ3/RQ4 called competing semiologies and denominator/window policy a remaining projection-policy burden. | Do not resurrect broad additive behavior. Reuse suspicious-state flags and require same-window parsed operands; otherwise route to verifier/review. |
| `cluster_axis_gap` | 12 | 11 | 1 | 0 | 9 | 2 | Old components had cluster convention support and repair rules, but RQ3/RQ7 still marked cluster cadence vs per-cluster burden as residual risk needing explicit policy/monitoring. | Port cluster label repair and benchmark renderer fixture logic, but keep unresolved cluster-axis rows routed until cadence and burden axes are explicit. |
| `cyclic_window_without_count` | 5 | 1 | 4 | 0 | 1 | 0 | ACD-004 and RQ9 trigger-context policies projected conditional-only trigger/cyclic windows to unknown or abstain, not numeric rates. | Keep this conservative behavior. The reset route is right; add explicit ACD unknown/abstain rationale rather than trying to render. |
| `frequency_operands_gap` | 77 | 69 | 8 | 0 | 64 | 5 | Handled by benchmark repair, selected-evidence-derived label repair, ACD policies for vague denominator, relative trend, diary/date listings, and summary-rate priority. Trigger-only or missing-anchor rows were routed by RQ9. | Port parser/repair rules for hourly, vague-with-denominator, diary/date lists, explicit summary rates, and selected-evidence label derivation. Keep trigger-only and trend-only rows non-rendered or unknown. |
| `seizure_free_duration_gap` | 114 | 108 | 1 | 5 | 106 | 2 | Handled by graph-gated month-bucket duration, boundary-state priority, last-event instrumentation, and safety floor. Many rows rendered as seizure-free duration labels; last-event/date-policy rows went to review. | Port back duration/date instrumentation and graph-gated month-bucket projection, but keep last-event review and all-type scope blockers explicit. |
| `seizure_free_proxy_overreach` | 1 | 1 | 0 | 0 | 1 | 0 | Suspicious-state and RQ9 policies treated seizure-free overreach as a boundary/review risk; ACD-007 only allowed seizure-free projection for non-epileptic triage with exact support. | Keep blocked unless evidence proves direct all-type seizure freedom or non-epileptic triage policy fires. |
| `unresolved_multiple` | 1 | 1 | 0 | 0 | 1 | 0 | Old safety-floor/action policy could preserve a comparator/source label, but RQ9 and suspicious-state work said unresolved competing facts need review/verifier policy. | Do not auto-pick in the reset. Use as first LLM-verifier/action-policy test case. |

## What Was Actually Mature

### 1. Seizure-Free Duration Was A Named Projection Slice

The old system had more than one seizure-free mechanism:

- `graph_gated_month_bucket_duration`: accepted in RQ4 as a narrow duration gate with 18 target corrections and 0 C->W on its regression panel.
- `boundary_state_priority`: accepted in RQ4 for boundary/unresolved states.
- last-event date instrumentation: extracted full/partial date signals but did not automatically release labels.
- suspicious-state flags: `seizure_free_with_recent_event_blocker` and `seizure_free_non_all_type_scope_with_current_events` routed unsafe cases.

This explains rows like 2907, 2932, 2938, 2965, 2992, 3015, 4992, and 8794: the reset has source phrases but no duration operands; the old system had duration/date policy and sometimes a comparator/safety-floor label.

Caution: old assembly often collapsed vague seizure freedom to `seizure free for multiple year`, which was scorer-correct for many rows but not semantically clean. Port the duration instrumentation and bucket policy, not that broad fallback.

### 2. Frequency Operand Gaps Were Mostly Normalization/Repair, Not Verification

The old code had benchmark repair and selected-evidence repair paths that handled examples now null-rendered:

- hourly shorthand: `9 per hour` and `4/h` -> `multiple per day`;
- vague rate with denominator: `several ... last month` -> `multiple per month`;
- diary/date list aggregation: explicit event dates -> count over calendar span;
- explicit current summary rate overriding long-period average;
- selected evidence derivation when raw prediction was underformatted.

This explains rows like 2609, 4345, 4368, and some EEG/hourly rows. However, old handling was not universally safe: rows 4690, 5534, 9888, 13209, and 15986 were wrong under old prediction-bearing development accounting.

### 3. Additive And Competing Semiology Were Not Really Solved

The old assembly predicted on all 24 current additive null rows and was correct on 19, wrong on 5. RQ3/RQ4/RQ7 repeatedly identified competing semiologies, denominator/window mismatches, and current-vs-historical priority as projection-policy burdens. This should not come back as broad `additive_same_window` rendering.

### 4. Cluster Had Useful Renderer Fixtures But Remained A Risk Family

The old repair policy knew Gan cluster syntax such as `2 cluster per month, 5 per cluster`, and boundary benchmark fixtures covered cluster convention. But RQ3/RQ7 still called cluster cadence vs per-cluster burden unresolved. On our current 12 cluster-axis null rows, old prediction was correct on 9 and wrong on 2, with 1 abstain. That is useful but not clean enough for blind automatic restoration.

### 5. Trigger/Cyclic Windows Were Intentionally Non-Rendered

ACD-004 and RQ9 trigger-context narrowing are aligned with the reset verifier route: conditional-only or cyclic vulnerability without a count should be `unknown`, abstain, or review, not rendered as a rate. The reset is doing the right thing for these rows; it just needs the older rationale/action labels.

## What Got Lost In The Reset

1. Policy-mediated state nodes. The reset clinical assessment has `source_normalized_phrase`, but does not materialize ACD/state-graph policy nodes such as previous-month-active-rate, diary-date-list, conditional-only-trigger, or explicit-summary-rate.

2. Selected-evidence-derived label repair. The reset strict projector refuses phrases that the old selected-evidence repair path could normalize.

3. Duration/date instrumentation. The reset captures many seizure-free phrases but does not compute duration buckets from dates or reference anchors.

4. Suspicious-state flags as first-class action inputs. The reset route only sees projection/render issues; the old rich selected state had flags for conditionality, diary window mismatch, cluster ambiguity, seizure-free blockers, and trend-only evidence.

5. Safety-floor accounting. The old assembly made predictions only with comparator transitions and no-regression gates. The reset correctly avoids hidden fallback, but now needs a clean way to compare any ported policy against deterministic V0.

## Recommended Port-Forward Plan

1. Reintroduce ACD policy nodes as explicit projection candidates, not hidden repairs.

2. Add a deterministic assessment repair layer before projection:

- dedupe candidate roles;
- copy parseable operands from selected candidates;
- parse duration/date anchors into seizure-free duration buckets;
- parse selected evidence with the existing benchmark repair rules.

3. Keep route/action boundaries from the reset:

- projection can produce a proposed label;
- route decides risk;
- deterministic VerificationDecision or future LLM verifier decides action;
- no component silently invents replacement scorer-facing labels.

4. Evaluate ported policies against the 234-row null surface with old accounting:

- rendered rows recovered;
- exact evidence/source-id validity;
- W->C/C->W versus deterministic comparator;
- action counts by route family;
- rows still requiring LLM verifier.

5. Do not port broad hybrid adjudicator behavior. It is the part that made the assembly feel Frankenstein: useful recoveries mixed with wrong seizure-free overreach, stale labels, and broad fallback.

## Practical Answer To The 234 Rows

The old system would probably have recovered about 200 of these rows as prediction-bearing under validation-development accounting, but about 14 of those old predictions were wrong. The clean recovery target is smaller and more principled:

- restore seizure-free duration/date projection for rows with explicit duration/date evidence;
- restore selected-evidence/benchmark repair for parseable frequency phrases;
- keep cyclic/trigger-only and seizure-free proxy cases routed;
- treat additive/cluster/unresolved-multiple as verifier or explicit-policy surfaces rather than automatic rendering.
