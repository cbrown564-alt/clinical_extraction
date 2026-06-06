# Gan 2026 Architecture Reset Synthesis And Next Questions

Date: 2026-06-06

Status: validation-development research synthesis. This report summarizes why
we reset the Gan 2026 component architecture, what the reset has achieved, what
we learned from the validation750 GPT-4.1-mini mechanics run, how the older
component work should inform the next iteration, and which questions remain
open before LLM-verifier work or any holdout-facing protocol.

This report does not authorize locked-test row-level review, benchmark-comparable
claims, or promotion of a whole pipeline.

## Source Context

Primary reset documents:

- `docs/research/gan2026_component_architecture_reset_completed_tasks_2026-06-05.md`
- `docs/research/gan2026_component_architecture_reset_review_plan_2026-06-05.md`
- `docs/research/gan2026_architecture_assembly_readiness_decision_2026-06-04.md`

Current validation750 mechanics reads:

- `docs/research/gan2026_validation750_gpt41mini_verifier_read_2026-06-06.md`
- `docs/research/gan2026_validation750_null_rendered_error_analysis_gpt41mini_v0_2026-06-06.md`
- `docs/research/gan2026_null_rendered_historical_component_handling_2026-06-06.md`

Key generated artifacts:

- Candidate set:
  `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.jsonl`
- GPT-4.1-mini clinical assessment:
  `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl`
- Projection/render:
  `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_v0_2026-06-06.jsonl`
- Verification route:
  `experiments/gan2026_validation750_verification_route_gpt41mini_v0_2026-06-06.jsonl`
- VerificationDecision V0:
  `experiments/gan2026_validation750_verification_decision_gpt41mini_v0_2026-06-06.jsonl`

## What We Were Trying To Do

The reset was not primarily a score chase. It was a repair of conceptual
ownership.

The pre-reset staged hybrid assembly had useful parts, but the whole thing was
hard to explain and easy to misread. It mixed extraction, selection,
normalization, projection, repair, safety fallback, action policy, and reporting
inside overlapping components. Several components had real evidence behind
them, but the assembled artifact could hide where a fact came from, who selected
it, who normalized it, who projected it, and why a final scorer-facing label was
allowed.

The reset objective was therefore:

```text
Extract -> Select -> Normalise -> Project -> Verify -> Render/Score
```

Each stage should have one job, one schema, and one provenance contract.

The intended division of labor was:

- Extract: collect broad source-near candidate facts without choosing the final
  answer.
- Select / clinical assessment: synthesize the clinically relevant burden from
  candidates, preserving ambiguity and context.
- Normalise: deterministically parse source-near facts into internal values
  without changing clinical meaning.
- Project: deterministically apply Gan-specific benchmark policy to normalized
  clinical state.
- Verify: route risky projected states to an action decision surface.
- Render/Score: emit scorer-facing labels only when a component with explicit
  ownership is allowed to do so; scoring remains audit-only during mechanics
  work.

The reset also had a negative goal: stop treating LLM outputs as raw
scorer-facing labels and stop letting deterministic fallback or repair hide
model/selection/projection failures.

## What The Old Work Had Already Established

The June 4 readiness decision was not naive. It already found that the right
architecture was a staged hybrid, not LLM-first:

```text
deterministic/state-graph substrate
  + selective LLM boundary candidate proposer
  + candidate-conditioned LLM evidence gate
  + rich selected-state fact carrier
  + deterministic consistency checks
  + gated deterministic projection/rendering
  + selective safety floor
  + abstain/review/monitoring policy
```

The strongest old component lessons were:

- LLMs are useful as selective boundary/candidate proposers, not broad final
  selectors.
- LLM evidence selection is strong when constrained to exact evidence and source
  ids.
- Rich selected state is a better fact carrier than raw label strings.
- Projection works only when narrow, gated, metadata-explicit, and exact-evidence
  backed.
- Broad state-graph projection, broad LLM label replacement, and unconstrained
  LLM selection were rejected because they created C->W regressions.
- Selective safety-floor action was the safest old label-changing pattern,
  because it required exact evidence, valid source ids, and no deterministic
  correct regressions.
- Ambiguous rows need prediction/abstain/review/monitoring decisions, not
  pressure to force every row into a scorer-facing label.

That older assembly became a bit of a Frankenstein not because the components
were shallow, but because too many mature and immature mechanisms were wired
together without a sufficiently clean stage boundary.

## What The Reset Has Achieved

### 1. A Cleaner Candidate Contract

The reset introduced `ExtractedCandidate` and `CandidateSet` as source-near
extract-stage artifacts. Candidate fields intentionally keep the LLM away from
parser-like responsibility:

- candidate kind and source phrase are LLM-appropriate;
- source ids, spans, candidate ids, and provenance are deterministic;
- counts, ranges, intervals, durations, and canonical values are deterministic
  normalization responsibilities;
- ambiguity and conflict are deferred to row-level route/verifier behavior.

This is a major conceptual improvement. The extraction stage now emits facts,
not answers.

### 2. Validation250 Mechanics Reached A Verifier Boundary

On validation250, the reset built the mechanics chain through:

- candidate set;
- clinical assessment;
- projection/render;
- score-policy audit;
- verification route;
- deterministic `VerificationDecision` V0.

The review plan records that route V6 contained 5 routed rows, all
null-rendered risk families. `VerificationDecision` V0 emitted 4 `abstain` and
1 `human_review`, with no replacement scorer-facing labels.

That is the clean boundary we wanted: route decides whether verification is
needed; deterministic V0 provides a baseline action harness; future LLM verifier
work compares against that baseline.

### 3. Validation750 Candidate Union Completed

The validation750 candidate-set artifact contains 750 rows and 1,834 total
candidates, with no LLM missing candidate-set rows and no call-error rows. It
merged 42 duplicate candidates and 625 nested duplicates.

That gave us a broad enough extract-stage surface to test the new clinical
assessment and verifier mechanics at full validation scale without touching
locked test.

### 4. GPT-4.1-mini Clinical Assessment Ran Cleanly Enough For Iteration

The validation750 GPT-4.1-mini clinical-assessment run produced:

- 750 examples;
- 732 valid clinical assessments;
- 0 call failures;
- 18 parse/validation failures;
- 0 missing candidate-set rows.

The 18 failures were all candidate-role hygiene problems:

- duplicate ids within a role: 13;
- primary/supporting overlap: 3;
- supporting/rejected overlap: 2.

This is an implementation-quality signal, not a clinical-reasoning collapse.
It points toward prompt tightening or deterministic role-id repair.

### 5. The Automated Verifier Baseline Is Now Measurable

The validation750 projection/render and route chain produced:

- 732 projection rows;
- 498 rendered-label rows;
- 234 true null-rendered rows;
- 252 non-scored rows including 18 invalid-assessment rows;
- 42 routed verifier rows;
- 42 deterministic V0 `abstain` actions;
- 0 deterministic V0 `affirm`, `reject`, or `human_review` actions.

Route-family counts:

- `mixed_window_or_vague_addition`: 24;
- `cluster_axis_ambiguity`: 12;
- `cyclic_window_without_event_count`: 5;
- `seizure_free_proxy_evidence_overreach`: 1.

This gives the first clean LLM-verifier evaluation surface: 42 routed rows where
V0 abstains and an LLM verifier can be tested for evidence-grounded action
deltas without emitting replacement labels.

## What The Validation750 Null Renders Taught Us

The 234 true null-rendered rows are not one problem. They split into themes:

- `seizure_free_duration_gap`: 114;
- `frequency_values_gap`: 77;
- `additive_mixed_window_or_vague`: 24;
- `cluster_axis_gap`: 12;
- `cyclic_window_without_count`: 5;
- `seizure_free_proxy_overreach`: 1;
- `unresolved_multiple`: 1.

The biggest lesson is that most null renders are upstream
normalization/projection gaps, not verifier failures.

The verifier route sees 42 / 234 null-rendered rows. The other 192 are mostly
cases where a selected clinical fact exists but the reset lacks the old
normalization/projection machinery to turn it into a policy-owned rendered
label.

## What We Learned From Comparing To The Old Assembly

On the exact 234 current null-rendered rows, the old staged decision layer did:

- `predict`: 215;
- `abstain`: 14;
- `human_review`: 5.

Old development accounting on those rows:

- `C_to_C`: 201;
- `W_to_W`: 14;
- `C_to_abstain`: 9;
- `W_to_abstain`: 5;
- `W_to_review`: 5.

That comparison is important but double-edged.

The old assembly recovered many rows that the reset currently leaves
null-rendered. But it also had 14 prediction-bearing Purist-wrong rows on this
same surface. So we should not resurrect the whole assembly. We should port the
mature component logic into the reset's cleaner contracts.

### Mature Old Components To Recover

1. Seizure-free duration/date handling.
   The old system had graph-gated month-bucket duration, boundary-state
   priority, last-event date instrumentation, and seizure-free blocker flags.
   These directly address the largest current null-render family.

2. Selected-evidence and benchmark repair.
   Old repair paths handled hourly rates, vague-with-denominator rates, diary
   date lists, explicit summary rates, cluster syntax, and selected-evidence
   label derivation.

3. ACD projection policy nodes.
   ACD-003 through ACD-010 captured recurring projection decisions:
   vague count with denominator, conditional-only triggers, relative-only
   trends, diary date lists, non-epileptic triage, summary-rate priority,
   previous-month/current-month aggregation, and major-semiology priority.

4. Suspicious-state flags.
   The rich selected-state work had explicit flags for conditionality,
   count-blocking ambiguity, diary window mismatch, unresolved cluster cadence,
   seizure-free blockers, and trend-only evidence.

5. Safety-floor accounting.
   Old label-changing gates required exact evidence, valid source ids, and
   W->C/C->W accounting. That discipline should survive, even if the old
   fallback wiring should not.

### Old Behaviors Not To Port Wholesale

- broad hybrid adjudicator fallback;
- broad additive rendering;
- broad seizure-free fallback to `seizure free for multiple year`;
- automatic cluster/convention prediction without explicit axis policy;
- hidden comparator preservation inside projection or verifier behavior.

## Current Interpretation

The reset succeeded at making the architecture legible. It exposed the actual
failure surface instead of papering over it.

That is good, but it makes the system look worse in the short term because old
policy-mediated projection and repair logic is no longer silently filling gaps.
The 234 null renders are the bill for separating the stages cleanly.

The right next move is not to abandon the reset. It is to reintroduce the best
old mechanisms as explicit, ablatable components in the new stage model.

## What Still Needs To Be Done

### Immediate Implementation Work

1. Add deterministic role-id repair for clinical assessments.
   Fix duplicate ids and role overlaps before strict assembly, while preserving
   an issue trace.

2. Add assessment-to-normalization repair.
   Copy parseable values from selected candidates and selected evidence when
   the LLM assessment has a source phrase but omitted or malformed values.

3. Reintroduce seizure-free duration/date instrumentation.
   Parse explicit durations, since-dates, last-event dates, and reference-date
   anchors into internal duration states before projection.

4. Port selected-evidence/benchmark repair into the new normalization stage.
   This should be explicit normalization, not hidden scorer-facing repair.

5. Reintroduce ACD policy nodes under projection ownership.
   ACD decisions should be named projection rules with evidence/source ids and
   ablation flags.

6. Add suspicious-state flags to the clinical assessment or projection route
   envelope.
   Route should see more than null-render issues; it should see conditionality,
   diary-window, cluster-axis, seizure-free blocker, and trend-only flags.

7. Rerun validation750 mechanics after each ported component.
   Track rendered rows recovered, route-family counts, action counts, and
   W->C/C->W accounting where comparator context is used for audit.

### LLM Verifier Work

The first LLM verifier should be evaluated only on routed rows where V0 emits
`abstain` or `human_review`. For the current validation750 GPT-4.1-mini run,
that means 42 routed V0-abstain rows.

The verifier should consume:

- `VerificationDecision` V0 row;
- embedded route decision;
- projection/render state;
- source candidate ids;
- route evidence;
- exact source evidence where available.

It should not consume gold labels or score correctness as action inputs.

It should emit:

- `affirm`, `reject`, `abstain`, or `human_review`;
- cited evidence ids/spans;
- concise rationale;
- issue flags;
- no scorer-facing replacement label.

### Documentation / Architecture Work

1. Update the reset completed-tasks document with the validation750 read.
2. Record which old components are being ported, renamed, or retired.
3. Keep H6/H9/H10 sidecars and component evidence matrix as audit/reporting
   surfaces unless they map cleanly to new stage schemas.
4. Create a new component inventory table around the reset stages rather than
   historical names.

## Major Open Questions

### 1. How Much Old Projection Policy Should Be Restored Before LLM Verifier Work?

If we build the LLM verifier immediately, it sees only the current 42-row route
surface. But if we first restore seizure-free duration, selected-evidence
repair, and ACD projection nodes, the route surface will change.

Recommendation: restore deterministic normalization/projection components that
are clearly upstream of verification before treating the LLM-verifier surface as
stable. Keep a snapshot of the current 42-row surface as V0 baseline, but do not
assume it is the final verifier training/evaluation surface.

### 2. Should Null Render Mean Abstain, Unknown, Human Review, Or Missing Policy?

The reset currently treats null render as a projection/render failure surface.
The old system sometimes predicted, sometimes abstained, sometimes reviewed.
We need a named action policy that distinguishes:

- clinically unknown and safely renderable as `unknown`;
- underdetermined and should abstain;
- date/last-event boundary requiring human review;
- missing deterministic parser/policy that should be fixed upstream;
- verifier-eligible ambiguity.

### 3. Where Should Comparator Preservation Live?

The old safety-floor behavior preserved many correct deterministic outputs. The
reset deliberately avoids hidden comparator fallback. If comparator preservation
returns, it must be a named action policy, not an implicit projection or verifier
repair.

Open question: after a verifier rejects or abstains on a proposed LLM/projection
state, when is it legitimate to preserve a deterministic comparator label?

### 4. What Is The Right Internal State For Seizure-Free Evidence?

The largest null-render family is seizure-free duration. We need to decide
whether seizure-free should be represented as:

- a direct duration-bearing clinical state;
- a last-event/date-anchor state requiring date arithmetic;
- a no-current-events state that may be too short to render;
- a non-epileptic-current-events triage state;
- a partial-scope statement that must not imply all-type seizure freedom.

The old components had pieces of this answer, but not one clean state schema.

### 5. How Should Additive And Competing Semiology Be Controlled?

The LLM often sees multiple true facts and tries to combine them. The old system
predicted many of these rows but had wrong predictions too. The reset should
only allow `additive_same_window` when values are parsed and same-window.
Mixed semiology, mixed window, cluster burden, and major/minor event priority
need explicit projection policy or verifier action.

### 6. Which Cluster Cases Are Projection, Which Are Verifier?

Cluster handling straddles benchmark convention and real ambiguity. The old
renderer knew some Gan cluster syntax, but RQ3/RQ7 still marked cluster cadence
vs per-cluster burden as risky. We need a clean split:

- render when cadence and per-cluster burden are explicit;
- use benchmark convention policy when the convention is predeclared;
- route when cadence, burden, or axis ownership is unresolved.

### 7. How Do We Evaluate Progress Without Recreating The Frankenstein?

The metric cannot be simply fewer null renders. A bad broad fallback can reduce
nulls and reintroduce C->W regressions.

Every ported component should report:

- rows newly rendered;
- rows newly routed;
- rows remaining null;
- evidence/source-id validity;
- issue counts;
- route-family changes;
- audit-only W->C/C->W against deterministic comparator and gold;
- whether behavior is ablatable by component.

## Proposed Next Sequence

1. Implement clinical-assessment role-id repair and rerun projection/render.
2. Port seizure-free duration/date normalization into the reset path.
3. Port selected-evidence/benchmark repair as explicit normalization.
4. Port ACD projection rules as named projection policies.
5. Add suspicious-state flags into route evidence.
6. Rerun validation750 and regenerate:
   - null-render analysis;
   - historical crosswalk;
   - route report;
   - VerificationDecision V0 baseline.
7. Only then run the first LLM-verifier saved-replay or live comparison over the
   routed V0 `abstain`/`human_review` surface.

## Working Thesis

The reset has done its job: it made the system honest. The old architecture had
more recovery power, but some of that power came from hidden fallback and broad
adjudication. The next architecture should combine the two virtues:

```text
old component wisdom + reset stage boundaries
```

That means porting mature policy and repair components back in, but only as
named, inspectable, ablatable stages with explicit action ownership.

## Implementation Addendum: 2026-06-06 Context/Repair Pass

After this synthesis, we implemented the first reset-stage repairs and a
seizure-free date instrumentation pass. This remains validation mechanics work:
no locked-test row-level review, no model-call rerun, no benchmark-comparable
claim, and score context remains audit-only.

### Implemented Components

1. Clinical-assessment role-id repair.
   Duplicate ids and role overlaps are repaired before strict
   `ClinicalAssessment` assembly, while preserving issue traces such as
   `candidate_role_duplicate_removed:*` and
   `candidate_role_overlap_removed:*`.

2. Assessment-to-normalization value repair.
   When an assessment phrase is present but unparseable, normalization can copy
   parseable values from selected primary candidates. This currently includes
   frequency values and explicit seizure-free duration values, with traces
   such as `frequency_rate_values_repaired_from_primary_candidate` and
   `seizure_free_duration_repaired_from_primary_candidate`.

3. CandidateSet row context.
   `CandidateSet` now carries deterministic row-level reference-date context
   parsed from note headers. The parser covers `Clinic Date: ...` and email
   `Sent: ...` headers. Validation750 context coverage:

   - `note_header`: 682 rows;
   - `email_header`: 66 rows;
   - missing reference date: 2 rows.

4. Seizure-free since-date instrumentation.
   Seizure-free normalization now has an optional
   `seizure_free_instrumentation` object. It computes duration only when there
   is an explicit or policy-owned approximate anchor plus row reference date.
   It leaves prior-visit and broad event anchors unresolved.

### Schema Shape

Candidate-set row context:

```json
{
  "source_row_index": 11118,
  "row_context": {
    "reference_date": {
      "date": "2025-10-02",
      "date_precision": "day",
      "source": "note_header",
      "source_phrase": "Clinic Date: 02 October 2025",
      "source_span": {
        "text": "Clinic Date: 02 October 2025",
        "start_char": 26,
        "end_char": 55
      },
      "issues": []
    },
    "context_issues": []
  }
}
```

Seizure-free since-date instrumentation:

```json
{
  "assessment_kind": "seizure_free",
  "normalized_burden": {
    "source_normalized_phrase": "no seizures since March 2025",
    "seizure_free_duration_low": 15,
    "seizure_free_duration_high": 15,
    "seizure_free_duration_unit": "month"
  },
  "seizure_free_instrumentation": {
    "state_kind": "since_date",
    "anchor_date": {
      "date": "2025-03",
      "date_precision": "month",
      "source": "seizure_free_source_phrase",
      "source_phrase": "since March 2025"
    },
    "reference_date": {
      "date": "2026-06-06",
      "date_precision": "day",
      "source": "candidate_set.row_context.reference_date:note_header"
    },
    "computed_duration": {
      "low": 15,
      "high": 15,
      "unit": "month"
    },
    "instrumentation_issues": []
  },
  "normalization_issues": [
    "seizure_free_duration_instrumented_from_since_date"
  ]
}
```

Approximate anchors are explicitly labelled. Example:

```json
{
  "source_phrase": "no recognized seizures since early summer",
  "anchor_date": {
    "date": "2025-06",
    "date_precision": "month",
    "source": "seizure_free_source_phrase_approximate_anchor_policy",
    "source_phrase": "since early summer"
  },
  "normalization_issues": [
    "seizure_free_duration_instrumented_from_since_date",
    "seizure_free_anchor_year_inferred_from_reference_date",
    "seizure_free_anchor_approximate_start_month_policy"
  ]
}
```

### Date Policies Implemented

Handled:

- explicit `Month Year` anchors, for example `since March 2025`;
- numeric full dates, for example `since 29/09/2017`;
- named full dates, for example `since 13-Nov-2015`;
- month/year anchors, for example `since 06/2017`;
- same-phrase last-event/day-month anchors, for example
  `last event on 31-May`;
- month-without-year anchors, for example `early August`, with year inferred
  from the row reference date;
- approximate anchors, for example `early summer` or `early 2024`, using a
  declared start-month policy.

Still unresolved:

- `since last visit`, `since last review`, `since last appointment`;
- `since surgery`, `since dose titration`, `since starting Levetiracetam`;
- broad same-note `since then` antecedents;
- clipped candidates such as `no episodes since`.

### Validation750 Mechanics Delta

Using the saved GPT-4.1-mini assessment artifact and the context-enriched
candidate-set surface:

- Projection rows: 750.
- Rendered rows: 564.
- Null-rendered rows: 186.
- Since-date instruments: 32.
- Approximate-anchor policy uses: 6.
- Last-event phrase anchors: 3.
- Remaining unresolved since anchors: 23.
- Route rows: 48.
- VerificationDecision V0 actions: 48 `abstain`.

For comparison, the original report recorded 498 rendered rows and 234 true
null-rendered rows. The role/value/date repair pass recovered 66 rendered
rows without broadening the verifier route surface.

Audit-only score context for the final context-repair V2 replay:

- Scored rows: 564.
- Non-scored rows: 186.
- Purist correct on scored rows: 477.
- Pragmatic correct on scored rows: 509.
- Exact normalized-label matches on scored rows: 412.

These score numbers are not a promotion claim. In particular, the approximation
policy recovered rows mechanically but should remain ablatable and visible in
reports because exact-match rate did not improve with every recovery.

### New Artifacts

Context-enriched candidate sets:

- `experiments/gan2026_validation750_candidate_set_deterministic_context_v0_2026-06-06.*`
- `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_context_v0_2026-06-06.*`

Final context-repair V2 replay:

- `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v2_2026-06-06.*`
- `experiments/gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v2_2026-06-06.*`
- `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v2_2026-06-06.*`
- `experiments/gan2026_validation750_verification_decision_gpt41mini_context_repair_v2_2026-06-06.*`

### Tests Run

Focused test suites passed:

- `uv run pytest tests/test_gan2026_candidate_set_contract.py tests/test_gan2026_candidate_set_union.py`
- `uv run pytest tests/test_gan2026_clinical_assessment_contract.py tests/test_gan2026_clinical_assessment_projection_render.py`
- `uv run pytest tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_verification_decision.py`
- `uv run pytest tests/test_gan2026_llm_extracted_candidate_schema_probe.py tests/test_gan2026_llm_candidate_set_selector_schema_probe.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_clinical_assessment_projection_render.py`

### Next Session Handoff

The remaining unresolved since-anchor surface should be treated as a new
decision point, not as a parser TODO list. Candidate next components:

1. Prior-visit context policy.
   Rows such as `since last visit` need a prior visit date. The current
   `row_context.reference_date` is not sufficient.

2. Event-date instrumentation.
   Rows such as `since surgery`, `since dose titration`, or
   `since starting Levetiracetam` need a separate event-date extraction
   contract before duration can be computed.

3. Same-note antecedent resolver.
   Rows such as `since then` sometimes have a nearby explicit date or event,
   but this requires a cautious antecedent resolver with source spans and
   route flags. It should not be hidden inside projection.

Recommendation for the next session: inspect the remaining 23 unresolved
since-anchor rows and choose one explicit, ablatable component. The likely best
candidate is event-date instrumentation, because it generalizes to surgery,
medication changes, and dose titration without pretending that prior visit
dates exist.

## Implementation Addendum: 2026-06-06 Event-Anchor V3 Pass

We continued from the unresolved since-anchor handoff and implemented a narrow
event-anchor instrumentation pass under normalization ownership. This pass does
not broaden projection policy, does not add comparator fallback, and does not
emit verifier replacement labels.

### Implemented Component

Seizure-free instrumentation now searches both the LLM assessment phrase and
the selected primary candidate source/evidence phrases. This matters because
the assessment phrase can be clipped, for example `no further seizures since
starting current regimen`, while the selected candidate contains the full
date-bearing event phrase.

New handled anchor shapes:

- event month/year anchors, for example `Since starting Levetiracetam in March
  2023`;
- titration/regimen event anchors, for example `since titration ... in August
  2023`;
- month-only event anchors with explicit year-inference trace, for example
  `since starting current regimen at end of November`;
- hyphenated approximate month anchors, for example `since mid-January`;
- full last-event anchors with year, for example `last seizure on
  12-Apr-2023`.

The event-anchor policy is trace-labelled with issues such as:

- `seizure_free_anchor_from_event_phrase`;
- `seizure_free_anchor_from_last_event_phrase`;
- `seizure_free_anchor_year_inferred_from_reference_date`;
- `seizure_free_anchor_approximate_start_month_policy`.

During replay we caught and fixed an important mechanics bug: initial event
month matching incorrectly inferred the row year for phrases that already
contained a year, such as `March 2023`. The corrected V3 pass preserves the
explicit year before falling back to month-only inference.

### Validation750 V3 Mechanics Delta

Using the saved GPT-4.1-mini assessment artifact and the context-enriched
candidate-set surface:

- Projection rows: 750.
- Rendered rows: 571.
- Null-rendered rows: 179.
- Since-date instruments: 39.
- Event-anchor instruments: 5.
- Remaining unresolved since anchors: 21.
- Route rows: 48.
- VerificationDecision V0 actions: 48 `abstain`.

Compared with context-repair V2, this recovered 7 additional rendered rows
without changing non-null rendered labels and without widening the verifier
route surface.

Recovered rows:

| Row | V3 rendered label | Anchor source |
| --- | --- | --- |
| 3015 | `seizure free for 12 month` | `last seizure on 12-Apr-2023` |
| 5248 | `seizure free for 31 month` | `Since starting Levetiracetam in March 2023` |
| 7818 | `seizure free for 26 month` | `since titration ... in August 2023` |
| 8180 | `seizure free for 6 month` | `Since our last review in April` |
| 8808 | `seizure free for 11 month` | `Since titrating ... in November 2024` |
| 14383 | `seizure free for 3 month` | `since mid-January` |
| 14635 | `seizure free for 1 month` | `since starting current regimen at end of November` |

Audit-only score context for V3:

- Scored rows: 571.
- Non-scored rows: 179.
- Purist correct on scored rows: 482.
- Pragmatic correct on scored rows: 514.
- Exact normalized-label matches on scored rows: 414.

The score context remains audit-only and is not a benchmark-comparable claim.

### New Artifacts

- `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v3_2026-06-06.*`
- `experiments/gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v3_2026-06-06.*`
- `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v3_2026-06-06.*`
- `experiments/gan2026_validation750_verification_decision_gpt41mini_context_repair_v3_2026-06-06.*`

### Tests Run

- `uv run pytest tests/test_gan2026_clinical_assessment_projection_render.py`

### Next Session Handoff

The remaining unresolved since-anchor rows are now less about directly
date-bearing event phrases and more about genuinely missing context:

1. Prior-visit policy remains unresolved for `since last visit`,
   `since last review`, and related forms. This needs a prior-visit date
   contract, not row-reference inference.
2. Same-note antecedents such as `since then` remain unresolved unless the
   selected phrase itself carries a date or event anchor. A cautious antecedent
   resolver should be a separate ablatable component.
3. Treatment anchors without dates, such as `since titration to current dose`,
   should remain unresolved unless another selected/source-backed phrase
   provides the event date.

## Implementation Addendum: 2026-06-06 Same-Note Antecedent V4 Pass

We then implemented the agreed next component: a cautious same-note antecedent
resolver for seizure-free `since then` phrases. This remains normalization
ownership, not projection ownership.

### Implemented Component

`SeizureFreeInstrumentation` now has an optional `antecedent` object:

```json
{
  "state_kind": "since_date",
  "source_phrase": "She has remained seizure-free since then.",
  "anchor_date": {
    "date": "2019-07-10",
    "date_precision": "day",
    "source": "seizure_free_source_phrase_year_inferred_from_reference_date",
    "source_phrase": "since 10 Jul"
  },
  "antecedent": {
    "source_phrase": "The patient experienced 2 to 3 seizures shortly after discontinuing valproate on 10 Jul, including one triggered by missed medication",
    "anchor_date": {
      "date": "2019-07-10",
      "date_precision": "day",
      "source": "seizure_free_source_phrase_year_inferred_from_reference_date",
      "source_phrase": "since 10 Jul"
    },
    "link_type": "local_since_then_antecedent",
    "source_candidate_ids": ["llm:14187:2"]
  }
}
```

Policy constraints:

- Only selected normalized phrases that explicitly say `since then` or end with
  clipped `since` can use this path.
- The assessment summary / selected evidence must contain exactly one
  date-bearing antecedent.
- Multiple possible antecedent dates remain unresolved.
- Duration phrases such as `seizure-free for over 4 weeks` are not converted
  through this path even if nearby text mentions a previous event date.

During replay, an initial broader version recovered one extra row by looking at
candidate evidence even when the selected normalized phrase did not say
`since then`. We rejected that overreach and tightened the trigger before
keeping V4.

### Validation750 V4 Mechanics Delta

Using the saved GPT-4.1-mini assessment artifact and the context-enriched
candidate-set surface:

- Projection rows: 750.
- Rendered rows: 573.
- Null-rendered rows: 177.
- Since-date instruments: 41.
- Same-note antecedent instruments: 2.
- Remaining unresolved since anchors: 19.
- Route rows: 48.
- VerificationDecision V0 actions: 48 `abstain`.

Compared with V3, this recovered 2 additional rendered rows without changing
the verifier route surface.

Recovered rows:

| Row | V4 rendered label | Antecedent anchor |
| --- | --- | --- |
| 14187 | `seizure free for 1 month` | `10 Jul`, year inferred from reference date |
| 14214 | `seizure free for 0 month` | `early December`, year inferred from reference date |

Audit-only score context for V4:

- Scored rows: 573.
- Non-scored rows: 177.
- Purist correct on scored rows: 482.
- Pragmatic correct on scored rows: 514.
- Exact normalized-label matches on scored rows: 414.

### New Artifacts

- `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v4_2026-06-06.*`
- `experiments/gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v4_2026-06-06.*`
- `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v4_2026-06-06.*`
- `experiments/gan2026_validation750_verification_decision_gpt41mini_context_repair_v4_2026-06-06.*`

### Tests Run

- `uv run pytest tests/test_gan2026_candidate_set_contract.py tests/test_gan2026_candidate_set_union.py tests/test_gan2026_clinical_assessment_contract.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_verification_decision.py`

### Next Conversation Point

The remaining since-anchor rows are now mostly true context gaps:

- prior-visit anchors such as `since last visit/review/appointment`;
- treatment anchors without dates, such as `since titration to current dose`;
- clipped `since` or `since then` rows with multiple/no clear antecedents.

Recommended next choice: do not implement prior-visit inference until a real
prior-visit date contract exists. The safer next component is probably a
diagnostic report over the 19 remaining unresolved anchors, grouped by which
new source contract would be required.

## Implementation Addendum: 2026-06-06 Prior-Encounter V5 and Session Stop

After the V4 diagnostic pass, we accepted relative prior-encounter internals
but routed them as policy-sensitive first. The intent was to make prior-visit
reasoning explicit and reviewable without pretending that a phrase like
`last review` is a direct calendar anchor.

### Diagnostic Report First

Before adding another repair, we produced:

- `docs/research/gan2026_validation750_remaining_since_anchor_diagnostic_v4_2026-06-06.md`

That report grouped the remaining unresolved since-anchor cases into source
contract families. It found that the remaining 19 since-anchor rows were no
longer a clean seizure-free-specific bug. They were mostly missing-context
families:

- relative prior-encounter anchors, such as `since last visit`,
  `since last review`, and `last appointment six months ago`;
- treatment or medication-change anchors without dates;
- clipped `since` / `since then` cases without a unique same-note date-bearing
  antecedent.

This supported the design choice to stop treating the residual cases as
micro-optimisation targets.

### Implemented Component

`RowContext` now supports a `prior_encounter` context derived from explicit
relative prior-encounter intervals. Example schema:

```json
{
  "row_id": 7785,
  "row_context": {
    "reference_date": {
      "date": "2019-06-18",
      "date_precision": "day",
      "source": "row_context"
    },
    "prior_encounter": {
      "interval": {
        "value": 12,
        "unit": "month",
        "direction": "before_reference_date",
        "source_phrase": "last appointment 12 months ago"
      },
      "anchor_date": {
        "date": "2018-06-18",
        "date_precision": "day",
        "source": "explicit_relative_interval"
      }
    }
  }
}
```

The component is intentionally narrow:

- It only accepts explicit relative intervals tied to prior encounters, such
  as appointment/review/clinic/visit language.
- It preserves this context through candidate-set union.
- Seizure-free projection may render a relative duration from this context.
- Verification route treats the resulting issue as
  `rendered_label_supported_but_policy_sensitive`.

Rendered example:

```json
{
  "row_id": 7785,
  "rendered_label": "seizure free for 12 month",
  "instrumentation": {
    "issue_flags": [
      "seizure_free_anchor_from_prior_encounter_context",
      "prior_encounter_derived_seizure_free_duration"
    ]
  },
  "verification_route": {
    "route": "rendered_label_supported_but_policy_sensitive"
  }
}
```

### Validation750 V5 Mechanics Delta

Using the saved GPT-4.1-mini assessment artifact and the V5
context-enriched candidate-set surface:

- Projection rows: 750.
- Prior-encounter contexts present: 8.
- Prior-encounter contexts missing: 742.
- Rendered rows: 573.
- Null-rendered rows: 177.
- Scored rows: 573.
- Non-scored rows: 177.
- Purist correct on scored rows: 482.
- Pragmatic correct on scored rows: 514.
- Exact normalized-label matches on scored rows: 414.
- Route rows: 49.
- VerificationDecision V0 actions: 49 `abstain`.

Compared with V4, V5 changed ownership/routing for one policy-sensitive row
but did not reduce the 177 null-rendered rows. That is the useful result: the
prior-encounter component is clean and generalisable, but it is not the next
high-leverage row-rescue path on this validation surface.

### New Artifacts

- `experiments/gan2026_validation750_candidate_set_deterministic_context_v1_2026-06-06.*`
- `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_context_v1_2026-06-06.*`
- `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v5_2026-06-06.*`
- `experiments/gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v5_2026-06-06.*`
- `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v5_2026-06-06.*`
- `experiments/gan2026_validation750_verification_decision_gpt41mini_context_repair_v5_2026-06-06.*`

### Tests Run

- `uv run pytest tests/test_gan2026_candidate_set_contract.py tests/test_gan2026_candidate_set_union.py tests/test_gan2026_clinical_assessment_contract.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_verification_decision.py`

Result: 66 passed, with 11 DSPy deprecation warnings.

### Session Stop

We should stop this repair thread here. There are still 177 null-rendered rows,
but continuing with small since-anchor optimisations is unlikely to be the
best use of the next session.

The next session should pivot from row-level cleanup to component-family
diagnosis, with the same priorities:

1. Prefer logical, clean components.
2. Prefer generalisable ideas that help close the generalisability gap.
3. Avoid over-engineering residual one-off rows.

Recommended next move:

- Review the 177 null-rendered rows by family, not row by row.
- Choose the next component by count, conceptual cleanliness, and transfer
  value.
- Treat prior-visit dates, event-date inference, and since-anchor leftovers as
  candidates only if they emerge as part of a broader family.
- Keep LLM verifier work pending until the deterministic
  normalization/projection surface is more stable.

Likely larger components to consider next:

- frequency values / selected-evidence benchmark repair;
- ACD projection nodes;
- route and suspicious-flag semantics;
- event-date context only if the 177-row family review shows broad value.

## Implementation Addendum: 2026-06-06 Post-V5 Family Ports And Provenance Work

After the V5 stopping point, we intentionally changed tactics. We stopped
treating the remaining null-rendered rows as a seizure-free cleanup queue and
treated them instead as component families that should be restored from the
older architecture in a reset-native way.

This session did not run a new full validation750 mechanics replay. It was a
code-and-contract port session over the reset path, with focused tests only.
The goal was to recover mature old behavior without bringing back hidden
fallback or broad hybrid adjudication.

### Why We Pivoted

The key interpretation after V5 was:

- seizure-free/date work had recovered real rows already;
- the remaining `177` null renders were no longer dominated by easy
  seizure-free/date mechanics;
- the largest remaining surface was the frequency family, especially
  source-backed frequency text that the reset was not yet normalizing or
  routing clearly enough;
- several old named policy families already existed in the pre-reset work and
  should be ported as explicit reset components rather than rediscovered one
  phrase at a time.

The important design choice was to prefer:

```text
old component wisdom + reset stage boundaries
```

and not:

```text
resume broad fallback until the null-render count drops
```

### Family-Level Interpretation

The working family interpretation we used in this session was:

```json
{
  "remaining_null_render_surface_v5": {
    "frequency_family_is_primary_next_target": true,
    "reason": "seizure-free/date mechanics had become lower-yield, while frequency normalization and policy families still had reusable old logic",
    "avoid": [
      "row-by-row phrase patching as the primary strategy",
      "broad hidden projection fallback",
      "using the verifier to compensate for upstream normalization gaps"
    ]
  }
}
```

### Decision Boundary For Frequency Work

We made one important narrowing decision before implementing anything:

- use plain English names such as `seizure amount` and `time period`;
- keep the first selected-evidence frequency repair narrow;
- do not redesign the internal schema for multiple simultaneous frequency
  facts yet;
- do not let normalization decide additive policy or competing-semiology
  policy.

The rationale was that the current `NormalizedBurden` schema still has room for
only one frequency fact. A true multi-frequency internal state would have been
a broader contract and projection redesign, not a narrow recovery component.

### Narrow Selected-Evidence Frequency Repairs

We first extended reset-side frequency recovery in
`selected_evidence_rate.py` for single clear current-frequency phrases.

Added narrow support included:

- `once per night` -> `1 per day`;
- `one seizure each night` -> `1 per day`;
- `twice per night` / `twice nightly` -> `2 per day`;
- `three seizures nightly` -> `3 per day`;
- vague weekly current burden such as:
  - `several occasions each week`;
  - `most weeks`;
  - `several seizures each week`.

Representative shape:

```json
{
  "source_phrase": "Nocturnal seizures occurring twice per night on average.",
  "normalized_burden": {
    "count_low": 2.0,
    "count_high": 2.0,
    "period_low": 1.0,
    "period_high": 1.0,
    "period_unit": "day"
  },
  "normalization_issues": [
    "frequency_values_recovered_from_selected_evidence"
  ]
}
```

The rationale for staying narrow was deliberate:

- these rows were clearly source-backed and clinically current;
- they did not require additive policy;
- they did not require competing-semiology arbitration;
- they gave us clean recovery without changing route semantics.

### Reuse Decision: Stop One-Off Patching And Port Old Named Families

After a few narrow repairs, we checked the surrounding files and confirmed the
user's intuition: several of the remaining behaviors had already been solved in
older components such as:

- `deterministic_rate_extraction.py`;
- `gold_policy.py`;
- `rq5_rendering_matrix.py`;
- `state_graph/projection.py`;
- `suspicious_state_policy.py`.

The architectural decision was:

- stop accumulating one-off regex patches as the main strategy;
- port old named behavior families into reset ownership;
- make each family explicit, ablatable, and visible in issue traces.

That was the governing rationale for everything that followed in this session.

### Reset-Native Ports Added Under Normalization Ownership

We ported the following families into the reset normalization path.

#### 1. `vague_frequency_with_explicit_time_period`

Examples:

- `several seizures in a typical month` -> `multiple per month`;
- `many events every year` -> `multiple per year`;
- `multiple seizures each week` -> `multiple per week`.

Representative state:

```json
{
  "source_phrase": "Several seizures in a typical month despite treatment.",
  "normalized_burden": {
    "vague_count": "multiple",
    "period_low": 1.0,
    "period_high": 1.0,
    "period_unit": "month"
  },
  "normalization_issues": [
    "vague_frequency_with_explicit_time_period",
    "vague_count"
  ]
}
```

Rationale:

- the old system had both benchmark examples and executable behavior for this
  family;
- these are normalization-owned because the text already states a seizure
  amount category and a time period;
- projection should not have to guess a denominator when the wording already
  supplies it.

#### 2. `relative_only_trend_guard`

Examples:

- `Frequency increased by about 50% after dose reduction.`
- `Frequency reduced by 0.3 after dose increase.`

Representative state:

```json
{
  "source_phrase": "Frequency increased by about 50% after dose reduction.",
  "normalized_burden": {
    "source_normalized_phrase": "Frequency increased by about 50% after dose reduction."
  },
  "normalization_issues": [
    "relative_change_without_current_baseline"
  ]
}
```

Rationale:

- this is not a parse failure in the ordinary sense;
- it is a known clinical-content guard where no absolute current frequency is
  present;
- the right reset behavior is to surface a named issue, not to let the row die
  as an anonymous miss.

#### 3. `conditional_only_trigger_guard`

Examples:

- `Seizures occur only when medication doses are missed.`
- `Seizures occur only after nights of curtailed sleep.`
- `Events occur exclusively during the perimenstrual period.`

Representative state:

```json
{
  "source_phrase": "Seizures occur only when medication doses are missed.",
  "normalized_burden": {
    "source_normalized_phrase": "Seizures occur only when medication doses are missed."
  },
  "normalization_issues": [
    "conditional_only_trigger_without_baseline"
  ]
}
```

Rationale:

- the old system treated this as a known route-to-unknown family;
- it should not be mistaken for a stable baseline seizure rate;
- again, the reset should emit an explicit guard, not a silent parse miss.

#### 4. `diary_date_listing`

Examples:

- `Diary lists seizures on 03-07, 03-27, 05-15, 05-19, 05-24.`
- `Recorded seizures on March 7, March 27, May 15, May 19, and May 24.`

Representative state:

```json
{
  "source_phrase": "Recorded seizures on March 7, March 27, May 15, May 19, and May 24.",
  "rendered_label": "5 per 2 month"
}
```

Rationale:

- old `diary.date_list` behavior already existed;
- the reset had most of the arithmetic but not the full adapter coverage;
- diary/list aggregation belongs upstream of the verifier when the dates are
  explicit enough to count mechanically.

### Reset-Native Ports Added Under Current-Vs-Historical Ownership

We then recovered the old `current_vs_historical` family in two layers.

#### 5. `current_vs_historical`: explicit current summary over long-window average

Examples:

- `Only seven focal impaired-awareness seizures reported so far this year. At present, his typical pattern is a focal seizure monthly.`
- broadened variants such as `Year to date ... Currently ... monthly.`

Representative state:

```json
{
  "source_phrase": "Year to date he has had only two focal seizures. Currently, his typical pattern is a focal seizure monthly.",
  "normalized_burden": {
    "count_low": 1.0,
    "count_high": 1.0,
    "period_low": 1.0,
    "period_high": 1.0,
    "period_unit": "month"
  },
  "normalization_issues": [
    "explicit_summary_rate_over_long_period_average"
  ]
}
```

Rationale:

- the old system already had a broader current-summary preference;
- the reset had a brittle single-phrase version;
- we widened the cue phrases slightly while keeping the family narrow and
  explicit.

#### 6. `current_vs_historical`: previous active month over current month-to-date zero

Examples:

- `There were a handful of short focal events during the previous month. In the current month to date, no events have been recorded.`
- broadened variants such as `Several focal events occurred last month. So far this month there have been no events.`

Representative state:

```json
{
  "source_phrase": "Several focal events occurred last month. So far this month there have been no events.",
  "normalized_burden": {
    "vague_count": "multiple",
    "period_low": 1.0,
    "period_high": 1.0,
    "period_unit": "month"
  },
  "normalization_issues": [
    "previous_month_active_rate_over_current_zero",
    "vague_count"
  ]
}
```

Rationale:

- this is a known projection-policy family, not a free-form paraphrase repair;
- the reset now names the family explicitly instead of leaving it as an
  unparsed row.

### Reset-Native Port Added For Competing Semiology

#### 7. `major_recent_relapse_over_background_frequency`

This was the reset-side recovery of old ACD-010 behavior.

Representative example:

```json
{
  "input_candidates": {
    "candidate_1": "three tonic-clonic seizures yesterday",
    "candidate_2": "interictal brief auras occurring approximately once or twice per week"
  },
  "clinical_assessment": {
    "primary_candidate_ids": ["llm:45:1"],
    "supporting_candidate_ids": ["llm:45:2"],
    "normalized_burden": {
      "count_low": 3.0,
      "count_high": 3.0,
      "period_low": 1.0,
      "period_high": 1.0,
      "period_unit": "day",
      "source_normalized_phrase": "three tonic-clonic seizures yesterday"
    },
    "normalization_issues": [
      "major_recent_relapse_over_background_frequency"
    ]
  },
  "final_rendered_label": "3 per day"
}
```

Rationale:

- the old ACD-010 logic lived in selection/projection priority, not in plain
  rate parsing;
- the right first reset port was therefore a narrow primary-candidate repair,
  not a new parser rule;
- after selecting the dominant convulsive relapse, we also had to realign the
  normalized source phrase to the chosen primary fact, otherwise normalization
  kept re-reading the old mixed summary.

This is a good example of a key reset principle: once one stage changes
ownership, the downstream source phrase must be updated too, or the old mixed
state leaks back in.

### Reset-Native Ports Added Under Verification-Route / Suspicious-State Ownership

We then turned to old suspicious-state families. The design question here was
important: only families whose signal survives into the reset
projection/render artifact should be ported directly into verification route.

That led to the following decisions.

#### 8. `conditional_only_trigger` and `relative_only_trend` route families

These were straightforward because the reset projection already carries:

- `conditional_only_trigger_without_baseline`;
- `relative_change_without_current_baseline`

in `projection_issues`.

Representative route shapes:

```json
{
  "projection_issues": [
    "conditional_only_trigger_without_baseline",
    "frequency_rate_values_incomplete"
  ],
  "verification_route": {
    "route_families": ["conditional_only_trigger"]
  }
}
```

```json
{
  "projection_issues": [
    "relative_change_without_current_baseline",
    "frequency_rate_values_incomplete"
  ],
  "verification_route": {
    "route_families": ["relative_only_trend"]
  }
}
```

Rationale:

- these families were already explicitly named upstream;
- route can consume them honestly from structured issues;
- this strengthens route semantics without inventing new clinical logic there.

### Provenance Work Before Porting Old Evidence-Trace Families

At this point we stopped and asked whether the old provenance family
`selected_evidence_missing_exact_trace` could be ported honestly.

The answer was initially no. Before this session, the reset projection artifact
preserved:

- `source_candidate_ids`;
- `source_ids`;
- `source_normalized_phrase`.

But it did not preserve:

- an explicit `exact_trace` boolean;
- a source-id trace object;
- a provenance status that could distinguish
  `non-exact selected evidence` from `exact evidence but invalid source ids`.

The decision was therefore:

- do not fake this family from weak hints;
- add the stronger provenance fields first;
- then port the old family exactly.

#### 9. Projection provenance block

Projection decisions now carry:

```json
{
  "selected_evidence_status": {
    "exact_trace": true,
    "source_id_status": "valid",
    "source_id_trace": {
      "selected_source_ids": ["note:10:span:0-20"],
      "expected_source_ids": ["note:10:span:0-20"],
      "missing_expected_source_ids": [],
      "unexpected_source_ids": [],
      "trace_basis": "exact_selected_evidence"
    }
  }
}
```

Rationale:

- provenance review families should be grounded in explicit reset-native data,
  not inferred from comparator behavior;
- this made the route layer truthful instead of speculative.

#### 10. `selected_evidence_missing_exact_trace`

Now that the provenance block exists, the old family could be ported by name.

Representative state:

```json
{
  "projection_decision": {
    "selected_evidence_status": {
      "exact_trace": false,
      "source_id_status": "invalid",
      "source_id_trace": {
        "selected_source_ids": ["note:46:span:0-26"],
        "expected_source_ids": [],
        "missing_expected_source_ids": [],
        "unexpected_source_ids": ["note:46:span:0-26"],
        "trace_basis": "non_exact_or_missing_evidence"
      }
    }
  },
  "verification_route": {
    "route_families": ["selected_evidence_missing_exact_trace"]
  }
}
```

Rationale:

- this is a provenance review concern, not a clinical-content concern;
- review is appropriate because the selected evidence may still be clinically
  fine, but the breadcrumb trail is not exact.

#### 11. `selected_source_id_invalid`

Once the provenance block existed, we also ported the companion family:

- exact trace is true;
- but carried source ids are invalid.

Representative state:

```json
{
  "projection_decision": {
    "selected_evidence_status": {
      "exact_trace": true,
      "source_id_status": "invalid",
      "source_id_trace": {
        "selected_source_ids": ["note:47:span:unresolved:0"],
        "expected_source_ids": ["note:47:span:unresolved:0"],
        "missing_expected_source_ids": [],
        "unexpected_source_ids": [],
        "trace_basis": "exact_selected_evidence"
      }
    }
  },
  "verification_route": {
    "route_families": ["selected_source_id_invalid"]
  }
}
```

Rationale:

- this is a distinct failure mode from missing exact trace;
- the old suspicious-state policy already treated that distinction explicitly;
- the reset route now does the same.

#### 12. `denominator_window_mismatch`

This family required one more careful decision.

The old behavior was not simply an issue-code check. It depended on the chosen
phrase itself. For example:

```json
{
  "source_normalized_phrase": "brief absences occur on most weekdays",
  "rendered_label": "multiple per week",
  "verification_route": {
    "route_families": ["denominator_window_mismatch"]
  }
}
```

The key point is that the rendered label is Gan-compatible, but the phrase
describes a windowed cadence rather than a clean denominator phrase. So we
added `source_normalized_phrase` to the projection contract and ported the old
review family from that phrase plus the rendered label.

Rationale:

- route needed access to the chosen wording, not just issue codes;
- this preserves the old caution around benchmark-compatible denominator
  collapsing;
- it keeps the rendered label visible while still flagging it for review.

### Tests And Scope

This session remained focused code-and-contract work. We did not run a new full
validation750 replay after every port. Instead, we used focused tests and
targeted probes.

Focused suites passed throughout the session, ending with:

- `uv run pytest tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_verification_route.py`

Final focused result at session stop:

- `72 passed`

### Why These Decisions Matter

The main architectural rationale across the whole session was:

1. Restore old mature behavior families by name.
2. Put each family under the stage that actually owns it.
3. Add stronger fields first when a family cannot yet be expressed honestly.
4. Stay narrow when the current schema or ownership boundary is not ready for a
   broader redesign.
5. Prefer explicit issue traces and route families over hidden fallback.

In other words, this was not mainly parser polishing. It was a staged recovery
of old architectural memory under reset contracts.

### Updated Next Step

At this point, the next likely component family is
`unresolved_cluster_cadence_with_per_cluster_burden`.

Why that is the strongest next candidate:

- cluster ambiguity remains one of the larger residual policy surfaces;
- the old system already had named risky cluster families;
- we have now recovered enough normalization, projection, and provenance
  discipline that cluster route semantics can be ported cleanly rather than
  smuggled in through broad fallback.

## Implementation Addendum: 2026-06-06 Cluster Value Language And Route Ownership

After the provenance and denominator-route ports, we made two small but
important contract decisions before continuing cluster work.

First, reset-stage clinical assessment, normalization, projection, and
verification-route issue names should use plain-language `values`. Parsed
counts, ranges, periods, durations, and cluster quantities remain deterministic
stage-owned data. The wording is now easier to read in artifacts and route
reports.

Representative issue-name changes:

```json
{
  "projection_issues": [
    "frequency_rate_values_incomplete",
    "cluster_frequency_values_unparsed",
    "cluster_cadence_values_incomplete"
  ],
  "normalization_issues": [
    "frequency_rate_values_repaired_from_primary_candidate",
    "frequency_label_values_unparsed",
    "cluster_label_values_unparsed"
  ]
}
```

Second, we agreed that a Gan-compatible cluster convention label may be
rendered while still being routed for verification when cadence, burden, or
axis ownership remains unresolved. This keeps projection/render mechanically
useful without pretending the clinical state is fully settled.

Representative route shape:

```json
{
  "projection_decision": {
    "projection_kind": "cluster_frequency",
    "projection_basis": "unknown_cadence_cluster_burden",
    "projection_issues": [
      "cluster_frequency_values_unparsed",
      "cluster_cadence_unknown_with_per_cluster_burden"
    ],
    "projected_label_semantics": "unknown, multiple per cluster"
  },
  "final_rendered_label": {
    "rendered_label": "unknown, multiple per cluster",
    "render_issues": []
  },
  "verification_route": {
    "routed": true,
    "route_families": [
      "unresolved_cluster_cadence_with_per_cluster_burden"
    ],
    "route_reasons": [
      "cluster burden is rendered but cadence or cluster axis remains unresolved"
    ]
  }
}
```

This is deliberately not broad cluster review. Explicitly parsed cluster
cadence plus explicit per-cluster burden can still render without this route.
The new route family is for convention-supported or incomplete-axis cases where
the label is representable but the clinical interpretation remains risky.

## Recap After Context Repair V6: What Is Implemented, Answered, Changed, And Still Ahead

This recap consolidates the reset thread after the implementation addenda and
the fresh validation750 no-call replay:

- `docs/research/gan2026_validation750_context_repair_v6_read_2026-06-06.md`
- `gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v6_2026-06-06.*`
- `gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v6_2026-06-06.*`
- `gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.*`
- `gan2026_validation750_verification_decision_gpt41mini_context_repair_v6_2026-06-06.*`

This remains validation-development mechanics only. It does not authorize
locked-test row-level review, benchmark-comparable claims, or promotion of a
whole reset pipeline.

### What We Have Implemented

The reset architecture itself is now executable through the intended staged
contract:

```text
Extract -> Select / Clinical Assessment -> Normalize -> Project -> Verify -> Render / Score
```

The implementation now includes:

1. Candidate-set extraction contracts.
   `ExtractedCandidate` and `CandidateSet` keep source-near facts separate from
   prediction-bearing answers. Candidate ids, source ids, spans, and provenance
   are deterministic responsibilities; the LLM is not asked to behave like a
   parser.

2. GPT-4.1-mini clinical assessment replay over validation750.
   The reset has a saved clinical-assessment surface with 750 examples, 732
   strict valid assessments in the original run, and no model call failures.
   Later repair passes operate by no-call replay over saved outputs.

3. Clinical-assessment role-id repair.
   Duplicate candidate ids and role overlaps are repaired before strict
   assembly, with issue traces preserved.

4. Assessment-to-normalization value repair.
   Normalization can recover deterministic values from selected candidates and
   selected evidence when the assessment phrase is source-backed but omitted or
   malformed values.

5. Seizure-free duration/date instrumentation.
   The reset now handles explicit seizure-free durations, since-date evidence,
   last-event dates, same-note antecedents such as `since then`, approximate
   month/season/year anchors, numeric dates, and selected prior-encounter
   context with policy traces.

6. Frequency-family selected-evidence recovery.
   Narrow current-frequency families were ported, including nightly cadence,
   hourly EEG-style frequency, vague weekly/monthly/yearly burden with explicit
   time period, and diary date lists.

7. Current-vs-historical policy ports.
   Explicit current summary rates can override long-window averages, and
   previous active month evidence can override current month-to-date zero when
   the policy family is named and source-backed.

8. Competing-semiology priority.
   `major_recent_relapse_over_background_frequency` was ported as a narrow
   reset-native family so a dominant recent convulsive relapse can own the
   primary normalized phrase instead of leaking a mixed summary downstream.

9. Guard families for non-renderable clinical content.
   `relative_change_without_current_baseline` and
   `conditional_only_trigger_without_baseline` now surface as named
   normalization/projection issues and route families instead of anonymous
   parse misses.

10. Projection provenance fields.
    Projection decisions now carry `selected_evidence_status`, including
    `exact_trace`, `source_id_status`, and a source-id trace object.

11. Provenance route families.
    `selected_evidence_missing_exact_trace` and `selected_source_id_invalid`
    are now reset-native route families rather than inferred suspicious-state
    side effects.

12. Denominator-window route ownership.
    Projection now carries `source_normalized_phrase` so route can flag
    `denominator_window_mismatch` from the chosen wording plus the rendered
    label.

13. Cluster value-language and route contract.
    Reset-stage issue names now use plain-language `values`, and unresolved
    cadence/per-cluster burden can render a Gan-compatible convention label
    while routing as `unresolved_cluster_cadence_with_per_cluster_burden`.

14. Validation750 V6 replay and report.
    The latest replay reaches all 750 validation rows and produces refreshed
    projection/render, score, route, and deterministic V0 decision artifacts.

15. Test coverage for the reset path.
    Focused reset tests passed during the ports, and the latest project status
    records the full suite passing at `1305 passed`.

### Questions We Have Answered

1. Was the architecture reset worthwhile?
   Yes. It made component ownership legible and exposed failure surfaces that
   the old assembly hid behind fallback, repair, and comparator preservation.
   Short-term null renders increased at first, but the failure surface became
   diagnosable and stage-owned.

2. Should we resurrect the old staged assembly wholesale?
   No. The old assembly had recovery power, but also broad fallback and
   regression risk. The adopted strategy is to port old component wisdom under
   reset boundaries, not restore the Frankenstein wiring.

3. Where should mature old behavior live?
   We have answered this for several families:
   frequency and date arithmetic belong to normalization;
   benchmark-policy rendering belongs to projection/render;
   provenance/exact-trace concerns belong to route/reporting;
   action decisions belong to verification, not hidden projection fallback.

4. Should the first LLM verifier compensate for upstream missing policy?
   No. V6 reinforces that null renders and route expansion need deterministic
   normalization/projection and route-policy adjudication first. LLM verifier
   work remains blocked until the route surface is stable and predeclared.

5. Can null-render reduction alone define progress?
   No. V6 is cleaner because it recovers 7 rows without introducing new nulls,
   but it also expands routing sharply through provenance checks. Progress must
   track recovered rows, remaining nulls, routed rows, issue ownership,
   evidence validity, and audit-only W->C/C->W effects.

6. Can provenance review be represented honestly in the reset?
   Yes, after adding explicit `selected_evidence_status`. We decided not to
   fake provenance families from weak hints; the route layer now has the data it
   needs to distinguish missing exact trace from invalid source ids.

7. Are cluster convention labels always projection failures?
   No. A Gan-compatible cluster convention can be rendered while still routed
   when cadence, burden, convention, or axis ownership remains unresolved.
   Explicit cadence plus explicit per-cluster burden need not route by default.

### How The Outcomes Have Changed

The original validation750 mechanics read exposed:

- 732 projection rows from valid assessments;
- 498 rendered-label rows;
- 234 true null renders;
- 42 routed verifier rows;
- 42 deterministic V0 `abstain` actions.

After context/date repair through V5, the surface improved to:

- 573 rendered rows;
- 177 null renders;
- 49 routed rows.

After the V6 replay, the refreshed surface is:

| Surface | Initial mechanics | V5 | V6 |
| --- | ---: | ---: | ---: |
| rendered rows | 498 | 573 | 580 |
| null renders | 234 | 177 | 170 |
| routed rows | 42 | 49 | 276 |
| V0 `abstain` rows | 42 | 49 | 276 |

V6 recovered 7 rows that were null-rendered in V5, with no new null-render
regressions. All 7 recoveries became Purist-correct scored rows on the
validation-development surface. The recovered families were exactly the intended
frequency ports: nightly cadence, per-hour normalization, and vague burden with
explicit periods.

The less obvious outcome change is the verifier route surface. V6 route
expansion is not mainly new clinical ambiguity. It is mostly provenance
visibility:

- `selected_evidence_missing_exact_trace`: 215 newly routed rows;
- `selected_source_id_invalid`: 9 newly routed rows;
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4 newly routed rows;
- `relative_only_trend`: 2 newly routed rows;
- `conditional_only_trigger`: 1 newly routed row.

The interpretation is therefore:

```text
V6 improves projection/render mechanics, but also reveals a second route class:
clinical/policy ambiguity routes versus provenance/exact-trace audit routes.
```

Those classes must be reported separately before any LLM-verifier experiment.

### Key Milestones Remaining

1. Read the refreshed V6 residual null surface.
   The remaining 170 null renders need a fresh family-level read. The largest
   current issue families are seizure-free duration/date gaps, harder
   frequency value gaps, additive period mismatch, and cluster value gaps.

2. Split route reporting into two buckets.
   Future reports should separate clinical/policy ambiguity routes from
   provenance/exact-trace routes. The 276-row route count should not silently
   become the first LLM-verifier target surface.

3. Adjudicate provenance-route policy.
   Decide whether `selected_evidence_missing_exact_trace` and
   `selected_source_id_invalid` are verifier inputs, instrumentation warnings,
   report-only audit flags, or separate human-review queues.

4. Complete the cluster-family pass.
   Render explicit cadence plus per-cluster burden, and route unresolved
   cadence, burden, convention, or axis ownership. Keep broad cluster fallback
   out of projection.

5. Define the null-render/action taxonomy.
   Separate clinically unknown, safely renderable `unknown`, abstain,
   human-review, missing upstream parser/policy, and verifier-eligible
   ambiguity.

6. Build a reset-stage component inventory.
   For each ported old family, record old name, reset-stage owner, portability
   category, issue/rule id, ablation switch, and status.

7. Add component-level ablation reporting.
   Each ported family should report newly rendered rows, newly routed rows,
   remaining nulls, evidence/source-id validity, route-family changes, and
   audit-only W->C/C->W.

8. Stabilize the route surface before LLM verifier work.
   The first LLM verifier should run only after deterministic
   normalization/projection and route-policy decisions are frozen. It should
   emit action decisions only, cite evidence ids/spans, and never invent a
   replacement scorer-facing label.

9. Keep locked holdout off-limits.
   Reset work remains validation-development mechanics until candidate code,
   prompts, model identifiers, scorer, route policy, inspection policy, and
   stop rule are frozen and explicitly authorized.

### Updated Working Thesis

The architecture reset is no longer just a conceptual cleanup. It has become a
working staged substrate that can recover old mature behavior while making
ownership, provenance, and routing visible.

The main risk has also changed. The danger is no longer only that the reset is
too sparse and leaves too many null renders. The newer danger is that improved
instrumentation can expand review surfaces faster than the team can interpret
them. The next milestone is therefore not just more recovery. It is disciplined
surface management:

```text
recover deterministic gaps,
separate clinical ambiguity from provenance audit,
make every port ablatable,
and only then test an LLM verifier.
```
