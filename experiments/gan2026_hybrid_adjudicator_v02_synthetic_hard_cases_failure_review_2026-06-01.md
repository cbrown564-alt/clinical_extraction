# Gan 2026 Hybrid Adjudicator V0.2 Synthetic Hard-Case Failure Review

This is a row-level review of the synthetic component-stress panel. It is not
validation, holdout, or a benchmark claim.

- Source artifact: `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.jsonl`
- Component summary: `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.md`
- Rows reviewed: 56 synthetic hard cases
- Deterministic top Purist: 39/56
- Raw adjudicator Purist: 44/56
- Conservative gated Purist: 42/56
- Candidate recall: 42/56
- Parse/schema/validation failures: 5/56

## Decision

Choose candidate-generation work for cluster/diary recall as the single next
v0.2 revision target.

Schema repair should be kept as small hygiene, and proxy/boundary gates deserve a
named follow-up ablation, but neither is the dominant limiter in this stress
panel. The largest actionable ceiling is that 14/56 rows do not recall the gold
Purist category at all, including 5/8 cluster dual-axis rows and 3/8 diary
distributed-count rows. When the correct category is absent from the candidate
set, the hybrid adjudicator either cannot choose it or must invent an unsupported
label that the architecture is designed to reject.

## Failure Families

| Family | Rows | Det correct | Raw correct | Gated correct | Parse failures | Recall misses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cluster_dual_axis | 8 | 3 | 3 | 3 | 0 | 5 |
| diary_distributed_counts | 8 | 5 | 5 | 5 | 1 | 3 |
| proxy_distractor_context | 8 | 6 | 7 | 6 | 1 | 2 |
| seizure_free_boundary | 8 | 6 | 6 | 6 | 1 | 2 |
| shorthand_ranges | 8 | 5 | 6 | 6 | 0 | 2 |
| temporal_conflict | 8 | 6 | 8 | 8 | 0 | 0 |
| unknown_no_reference_boundary | 8 | 8 | 6 | 8 | 2 | 0 |

## Schema And Validation Failures

All five failures are output-contract failures, not call failures. The
conservative gate falls back to deterministic output with
`adjudicator_output_missing_or_invalid`.

| Case | Family | Gold | Deterministic/gated | Invalid field pattern | Review |
| --- | --- | --- | --- | --- | --- |
| `v02_seizure_free_boundary_07` | seizure_free_boundary | `2 per 1 month` | `no seizure frequency reference` | `assertion_status: affirmed` | Schema repair would parse the row, but candidate recall is still absent and the model selected no-reference despite the breakthrough count. |
| `v02_unknown_no_reference_boundary_04` | unknown_no_reference_boundary | `unknown` | `no seizure frequency reference` | `assertion_status: present`, `uncertainty: unknown` | Deterministic and gated are already Pragmatic-safe but Purist-wrong. Repairing enums alone would not fix unknown vs no-reference reasoning. |
| `v02_unknown_no_reference_boundary_08` | unknown_no_reference_boundary | `no seizure frequency reference` | `no seizure frequency reference` | `assertion_status: present`, `seizure_or_event_target: seizure frequency`, `uncertainty: false` | The fallback is correct; schema repair would reduce issue count only. |
| `v02_diary_distributed_counts_04` | diary_distributed_counts | `3 per 2 week` | `1 per month` | `temporality: historical and recent` | The model noticed the recent diary fact but could not select it because the candidate set only exposed the historical monthly candidate. |
| `v02_proxy_distractor_context_01` | proxy_distractor_context | `no seizure frequency reference` | `no seizure frequency reference` | `assertion_status: positive`, `seizure_or_event_target: seizure frequency`, `uncertainty: unknown` | The fallback is correct; schema repair would reduce issue count only. |

Recommended schema hygiene: add parser-local aliases for common enum near-misses
only if they remain explicitly non-semantic (`affirmed -> asserted`,
`positive/present -> asserted`, `unknown -> high` for uncertainty when the
rationale says no usable frequency, and reject boolean uncertainty as invalid).
Do not turn this into broad model-output repair.

## Cluster And Diary Candidate Misses

Candidate recall misses account for most unrecoverable rows:

- Cluster dual-axis misses: `v02_cluster_dual_axis_01`, `_02`, `_03`, `_04`,
  `_08`.
- Diary distributed-count misses: `v02_diary_distributed_counts_01`, `_04`,
  `_06`.
- Related non-cluster misses: `v02_seizure_free_boundary_01`, `_07`,
  `v02_shorthand_ranges_03`, `_05`, `v02_proxy_distractor_context_04`, `_06`.

The cluster rows fail before adjudication. The deterministic candidate set often
contains only `no seizure frequency reference` or `unknown`, so the LLM has no
candidate representing labels such as `1 cluster per 2 week, 3 per cluster` or
`1 cluster per month, 6 to 7 per cluster`. The row family therefore argues for a
candidate generator that can emit a dual-axis candidate with cluster cadence and
per-cluster burden as separate inspectable fields before Gan label rendering.

The diary rows show the same retrieval problem in a different form. Month-list
or recent-window counts are not normalized into candidate labels such as
`2 per month`, `3 per 2 week`, or `3 per month`; the adjudicator sees either a
boundary fallback or an older baseline candidate. This is a candidate-generation
gap, not primarily a selection prompt gap.

## Proxy And Boundary Gate Blocks

Two rows show raw model signal blocked by the conservative overreach gate:

| Case | Gold | Deterministic | Raw adjudicator | Gated | Gate |
| --- | --- | --- | --- | --- | --- |
| `v02_proxy_distractor_context_04` | `no seizure frequency reference` | `2 per week` | `no seizure frequency reference` | `2 per week` | `unsupported_boundary_demotion_overreach` |
| `v02_proxy_distractor_context_06` | `no seizure frequency reference` | `3 per week` | `no seizure frequency reference` | `3 per week` | `unsupported_boundary_demotion_overreach` |

These rows are real v0.2 signal: the raw adjudicator correctly demotes
non-epileptic/proxy frequency to no-reference. The gate blocks the correction
because the candidate set does not recall the no-reference category and the
policy treats boundary demotion as unsupported overreach.

This should not be the first revision target because it affects 2/56 rows and
risks reopening the broad validation250 regression problem. If revisited, it
should be a separately named gate ablation: allow boundary demotion only when
the selected deterministic evidence is explicitly non-epileptic, aura-only,
rescue-medication-only, falls/collapses-only, or otherwise marked proxy by a
deterministic candidate feature.

## Where V0.2 Actually Helps

The strongest clean signal is temporal conflict:

- `v02_temporal_conflict_02`: `5 per week` -> `1 per 2 week`
- `v02_temporal_conflict_03`: `3 per week` -> `seizure free for 6 month`

Shorthand range also has one clean correction:

- `v02_shorthand_ranges_06`: `1 per day` -> `1 per 2 day`

These rows have candidate recall and no gate conflict. That supports a narrow
future adjudicator role: choose among recalled candidates when temporality or
surface notation makes deterministic ranking brittle. It does not support asking
the adjudicator to rescue missing cluster/diary candidates.

## Next Revision Target

Implement a candidate-generation branch, outside frozen deterministic V1, for a
named `cluster_diary_candidate_recall` candidate:

1. Emit dual-axis cluster candidates with cadence and per-cluster burden kept
   separately before label rendering.
2. Emit diary/list candidates for distributed counts over explicit month,
   week, or recent windows.
3. Add candidate-recall tests for the eight failed cluster/diary rows above.
4. Re-run this same synthetic component-stress panel with recall, raw, and
   gated metrics reported separately.
5. Keep broad validation and holdout untouched until this candidate-recall
   branch has its own component ablation.

