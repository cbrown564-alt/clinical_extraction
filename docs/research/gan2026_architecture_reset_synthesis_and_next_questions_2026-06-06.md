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
- Normalise: deterministically parse source-near facts into internal operands
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
- counts, ranges, intervals, durations, and canonical operands are deterministic
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
- `frequency_operands_gap`: 77;
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
   Copy parseable operands from selected candidates and selected evidence when
   the LLM assessment has a source phrase but omitted or malformed operands.

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
only allow `additive_same_window` when operands are parsed and same-window.
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

2. Assessment-to-normalization operand repair.
   When an assessment phrase is present but unparseable, normalization can copy
   parseable operands from selected primary candidates. This currently includes
   frequency operands and explicit seizure-free duration operands, with traces
   such as `frequency_rate_operands_repaired_from_primary_candidate` and
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
null-rendered rows. The role/operand/date repair pass recovered 66 rendered
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
