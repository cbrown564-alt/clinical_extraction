> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ5 Deterministic Compilation/Rendering Answer

Date: 2026-06-04

Status: final validation-development answer for deterministic
compilation/rendering over fixed selected states. This is not a holdout-transfer,
production, or benchmark-comparable claim.

## Answer

RQ5 is answered for saved validation replay and focused ACD fixtures:

```text
Given a fixed selected state and fixed projection-policy decision, the current
deterministic compiler/renderer preserves the selected state, emits parse-valid
Gan-compatible labels, and retains evidence/source-id attribution. The remaining
wrong labels in the saved replay are upstream state/projection problems, not
semantic drift introduced by rendering.
```

The RQ5 matrix has 2,295 compiler/rendering rows over 751 source-row ids:

- 2,250 materialized saved validation-replay rows from state-graph projection
  metadata.
- 45 focused ACD fixture rows covering ACD-003 through ACD-010.
- 0 parse failures.
- 0 evidence-retention failures.
- 0 source-id-retention failures.
- 0 semantic-drift rows for `current_production`, `strict_format`, or
  `evidence_preserving`.
- 6 semantic-drift rows in the `acd_off_ablation`, all caused by removing an
  explicit ACD policy and collapsing the fixed policy-mediated state to
  `unknown`.

Current production rendering has 759 rows, 100% parse validity, 100%
evidence/source-id retention, 0 semantic drift, 0 W->C, and 42 C->W against the
deterministic top comparator. Those 42 C->W rows are not renderer regressions:
the renderer exactly preserves a fixed projection label that was already wrong.

## Claim Boundary

Supporting artifacts:

- ``
- `experiments/gan2026_rq5_deterministic_rendering_matrix_2026-06-04.jsonl`
- `experiments/gan2026_rq5_deterministic_rendering_matrix_2026-06-04.md`
- ``
- ``
- `experiments/gan2026_component_projection_followup_panel_2026-06-04.md`

All materialized replay rows come from saved validation artifacts under
`gan2026_split_v1`. Locked holdout rows were not inspected. The focused ACD
fixtures are development-control checks for named projection policies, not
holdout-transfer evidence.

## Compiler/Renderer Variants

| Variant | Rows | Parse valid | Exact label | Purist correct | Pragmatic correct | Drift | Evidence/source ids |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `current_production` | 759 | 1.000 | 0.650 | 0.875 | 0.887 | 0 | 1.000 / 1.000 |
| `evidence_preserving` | 759 | 1.000 | 0.650 | 0.875 | 0.887 | 0 | 1.000 / 1.000 |
| `strict_format` | 759 | 1.000 | 0.650 | 0.875 | 0.887 | 0 | 1.000 / 1.000 |
| `acd_aware` | 9 | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 1.000 / 1.000 |
| `acd_off_ablation` | 9 | 1.000 | 0.333 | 0.556 | 0.556 | 6 | 1.000 / 1.000 |

The strict-format and evidence-preserving variants do not change outputs from
current production. That is useful negative evidence: the renderer is already
format-valid and attribution-preserving for this fixed-state surface.

The ACD-off ablation is the positive component result. Explicit policy is
required for six families where a faithful fixed state must not be collapsed to
generic uncertainty: projection-compatible vague rates, diary/date aggregation,
non-epileptic seizure-free triage, summary-rate priority,
previous-month/current-month aggregation, and major-semiology relapse priority.

## Deterministic Baseline Role

The deterministic top candidate remains the frozen comparator and safety floor.
It is not the RQ5 answer. RQ5 isolates a later deterministic component:
compilation/rendering after candidate, evidence, selected state, and
projection-policy decisions are fixed.

The 42 C->W rows in current production are therefore regression-risk accounting
against the comparator, not compiler/rendering failures. In the matrix they keep
their upstream first-failure owners, such as `typed_state_representation`,
`projection_policy`, `operand_exposure`, and `llm_clinical_selection`.

## Row-Level Mechanism Examples

`source_row_index=1707`, ACD-003: fixed evidence `several focal seizures last
month` renders as `multiple per month`. ACD-aware/current production preserves
the policy-mediated label; ACD-off collapses it to `unknown`. This shows the
renderer needs the explicit vague-count-with-denominator decision.

`source_row_index=0`, ACD-003 fixture: fixed evidence `occasional events`
renders as `unknown`. ACD-off does not change it because the selected state is
already uncertainty-bearing; this is a correct conservative rendering, not a
lost policy effect.

`source_row_index=3356`, ACD-004: fixed conditional-only evidence `Seizures
happen when perimenstrual only (days -2 to +2)` renders as `unknown` with no
semantic drift. The compiler does not invent a monthly rate from a trigger.

`source_row_index=3528`, ACD-005: fixed relative-trend evidence `Frequency
increased by about 50% after dose reduction` renders as `unknown`. The renderer
preserves the distinction between a trend and an absolute current rate.

`source_row_index=4368`, ACD-006: fixed diary evidence `Seizure events on
03-07, 03-27, 05-15, 05-19, 05-24` renders as `5 per 2 month`. Removing the
ACD policy collapses the state to `unknown`, so diary aggregation must stay
explicit and ablatable.

`source_row_index=3137`, ACD-007: fixed evidence `no definite seizure events`
renders as `seizure free for multiple month` when recent presentations are
triaged as non-epileptic. ACD-off collapses this to `unknown`.

`source_row_index=2748`, ACD-008: fixed evidence `At present, his typical
pattern is a focal seizure monthly` renders as `1 per month`, overriding the
derived long-period average. ACD-off collapses it to `unknown`.

`source_row_index=1695`, ACD-009: fixed evidence `handful of short focal events
during the previous month` renders as `multiple per month` despite a short
current-month-to-date zero window. ACD-off collapses it to `unknown`; Purist
still maps both to an unknown bucket, but exact-label and Pragmatic/Purist
interpretability are worse.

`source_row_index=1363`, ACD-010: fixed evidence `three tonic-clonic seizures
yesterday` renders as `3 per day`, preserving major-semiology relapse priority
over lower-severity interictal rates. ACD-off collapses it to `unknown`.

Two materialized replay examples show why remaining errors are upstream:

- `source_row_index=278`: the fixed projection label is `seizure free for
  multiple year` from evidence about no generalized tonic-clonic seizures, while
  gold is `multiple per week`. Rendering preserves the fixed seizure-free state;
  the failure owner remains `typed_state_representation`.
- `source_row_index=744`: the fixed projection label is `1 per 8 week` from
  `one generalised tonic-clonic seizure in the last eight weeks`, while gold is
  `multiple per week`. Rendering did not lose an operand; the fixed selected
  state is incomplete for the benchmark-relevant burden.

## Hidden-Family Readout

The ACD fixture rows cover the intended policy families:

| ACD | Rows | Drift rows | Interpretation |
| --- | ---: | ---: | --- |
| ACD-003 | 10 | 1 | Vague count with denominator needs explicit projection; vague without denominator stays unknown. |
| ACD-004 | 5 | 0 | Conditional-only trigger already renders conservatively to unknown. |
| ACD-005 | 5 | 0 | Relative-only trend already renders conservatively to unknown. |
| ACD-006 | 14 | 1 | Diary/date-list aggregation depends on explicit policy. |
| ACD-007 | 23 | 1 | Non-epileptic triage needs explicit seizure-free projection policy. |
| ACD-008 | 5 | 1 | Summary-rate priority depends on explicit policy. |
| ACD-009 | 5 | 1 | Previous-month/current-month aggregation depends on explicit policy. |
| ACD-010 | 5 | 1 | Major-semiology priority depends on explicit policy. |

For non-ACD materialized rows, exact-label failures concentrate in the same
families already identified by RQ4: current-vs-historical selection,
competing semiologies, seizure-free overreach, unknown/no-reference boundaries,
cluster/diary representation, and rate-bucket/denominator gaps. RQ5 shows that
those are not caused by final rendering drift once the fixed state exists.

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Reason |
| --- | --- | --- | --- |
| Renderer preserves fixed state labels and attribution on saved validation replay. | High | Moderate | The checks are broad over validation replay, but still validation-derived. |
| ACD policies are required for six policy-mediated rendering families. | High | Low-to-moderate | Fixture mechanism is clean, but broad held-out policy incidence is untested. |
| Remaining saved-replay wrong labels are upstream state/projection failures. | High | Moderate | The matrix directly separates fixed-label preservation from correctness. |
| No current evidence/source-id loss in final rendering. | High | Moderate | Strong on saved artifacts; needs frozen audit before holdout-facing claims. |

Anti-overfit reflection: this is a mechanism result, not just a validation score
rediscovery. The decisive metrics are parse validity, semantic drift,
evidence/source-id retention, and ACD-on/off behavior over fixed states. Broad
validation F1 is intentionally secondary.

## Metadata/Instrumentation Gaps

- The matrix uses materialized state-graph projection metadata. Other selected
  state surfaces, such as claim-table selected states or LLM-heavy selected
  facts, need the same fixed-state bundle before they can support an RQ5 claim.
- ACD-001 and ACD-002 remain interpretation-policy inputs only. They are not in
  the predeclared production ACD fixture set.
- The materialized replay still exposes some fallback no-reference evidence as
  long note prefixes. That is not a final-rendering drift issue, but it is an
  evidence-selection/state-construction instrumentation smell for later work.
- A frozen holdout-facing audit would need predeclared incidence slices,
  unchanged ACD policies, unchanged scorer, and no post-hoc row-level tuning.

## Decision

RQ5 is answered for validation development:

- Accept current deterministic compilation/rendering as faithful over fixed
  materialized state-graph projection labels.
- Keep ACD-003 through ACD-010 as explicit, ablatable projection-policy inputs
  when rendering policy-mediated states.
- Treat ACD-off collapse to `unknown` as evidence that these policies are
  component-relevant, not incidental formatting.
- Do not use current production's saved-replay exact-label failures as renderer
  failures unless a row shows semantic drift from fixed state to rendered label.

## Next Action

Move to RQ3 schema comparison or a narrow RQ5 follow-up only if it adds fixed
selected-state bundles for non-state-graph surfaces. Whole-pipeline promotion
and benchmark-comparable language remain blocked until component questions and
a frozen holdout-facing protocol are complete.
