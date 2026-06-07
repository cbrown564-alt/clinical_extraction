# Gan 2026 Overfitting Reduction and Generalization Hypotheses Synthesis

Date: 2026-06-07
Author: Antigravity

Status: Living research synthesis. Documents the successful reduction of validation-test gap under the reset-native composable pipeline and establishes clean, non-overfitting hypotheses for future accuracy improvements.

---

## 1. Executive Summary

A comparison of the newly completed **Reset ClinicalAssessment Pipeline** (`validation750_gpt41mini_v0` vs. `test450_gpt41mini_v0`) against historical baselines confirms major progress in eliminating validation-specific overfitting:

* **Validation-Test Gap Collapse**: The Purist accuracy gap between validation and test has collapsed from **17.47%** (under the previous full-repair ladder) to just **5.55%** (84.14% validation vs. 78.59% test).
* **Holdout Score Stabilization**: Despite stripping away high-yield validation-tuned adapters, the holdout test score remained stable at **78.59% Purist / 82.11% Pragmatic**, indicating that we removed metric inflation without degrading true generalization performance.
* **Paradigm Shift**: Future gains must be achieved by resolving fundamental clinical and temporal anchoring limits rather than expanding post-hoc semantic repairs.

---

## 2. Mechanical Analysis of Overfitting Reduction

The previous architecture suffered from a **semantic-repair policy failure (H5)**, where deterministic adapter layers translated raw LLM selections to align with validation annotations:

```text
[Raw LLM Candidate] -> [Deterministic Semantic Repair (Tuned to Val Examples)] -> [Artificially Inflated Val Score]
```

This propped up validation performance (adding **+23.20%** accuracy) but failed to transfer to the locked test set (adding only **+3.33%**).

By transitioning to the **Reset-Native Composable Pipeline**, we restructured the logic into stage-owned, explicit projection and rendering rules:

1. **Isolation of Fallbacks**: We removed broad sentinel demotions and undocumented label-switching rules.
2. **Explicit Null/Route Visibility**: Non-renderable or ambiguous states are routed transparently to nulls or routed-abstain paths, exposing the true accuracy of the underlying extractor rather than masking errors through complex patching.
3. **Metric Alignment**: The validation score naturally declined to reflect the real clinical-state representation, matching the test set’s behavior and closing the generalization gap.

---

## 3. Generalization Hypotheses (Non-Overfitting Pathways)

To improve overall scores for both validation and test sets without falling back into the overfitting trap, we must focus on **structural inputs** and **clinical representation rules** that are independent of individual validation rows. 

The following four hypotheses target the largest error clusters identified in the recent run:

### Hypothesis G1: Date-Anchored Temporal Arithmetic (YTD Calibration)
* **Underlying Error**: 54 errors (58.7% of scored errors) are due to Rate/Denominator mismatches. Most occur when "this year so far" is projected literally as "per year" instead of resolving the fraction of the year elapsed based on the clinic date (e.g. 6 events by April should project as `6 per 4 month`).
* **Mechanism**: In the projection stage, when a candidate indicates YTD temporality, dynamically compute the delta in months between January 1st of the clinic year and the clinic date month. Normalize the denominator by this delta.
* **Why it avoids overfitting**: It relies on universal calendar math anchored to the document's metadata rather than hardcoded phrase maps.

### Hypothesis G2: Explicit Default Cluster Cadence mapping
* **Underlying Error**: 22 errors (23.9% of scored errors) are due to Missed Cluster Semantics. The pipeline currently projects clusters without explicit sizes (e.g., "two clusters over three weeks") as a simple rate (`2 per 3 week`). The gold standard expects these to default to `multiple per cluster` (e.g., `2 cluster per 3 week, multiple per cluster`).
* **Mechanism**: Update `cluster_cadence_as_event_rate_when_size_absent_v0` to render clusters with unspecified event counts as `X cluster per Y period, multiple per cluster`.
* **Why it avoids overfitting**: It establishes a consistent clinical default matching the annotation protocol, rather than tuning on a case-by-case basis.

### Hypothesis G3: Multi-Encounter Anchor Linking for Seizure Freedom
* **Underlying Error**: 75 null renders (44.1% of nulls) occur under `seizure_free_duration_required_v0` due to relative anchors (e.g. "since last visit" or "since last appointment") that cannot be resolved. 39 of these have the gold label `seizure free for multiple month`.
* **Mechanism**: Map relative visit anchor phrases to the date of the prior encounter in `candidate_set.row_context.prior_encounter` (if available), and compute the month delta between the prior encounter date and the current clinic date.
* **Why it avoids overfitting**: It uses explicit cross-encounter metadata rather than manual heuristics to calculate duration.

### Hypothesis G4: Standardized Representation for Catamenial and Sleep Patterns
* **Underlying Error**: 18 null renders (10.6% of nulls) occur under `cluster_cadence_values_required_v0` due to incomplete menstrual/sleep patterns (e.g., "perimenstrual clustering").
* **Mechanism**: Route catamenial and sleep-restricted patterns to dedicated high-precision sentinel representation classes or map them to structured cadence ranges instead of raising value-incomplete errors.
* **Why it avoids overfitting**: It expands the schema's expressiveness systematically for cyclic variants rather than writing custom exceptions for individual phrases.

---

## 4. Verification and Guardrail Protocol

Every hypothesis must be tested using the following multi-tiered validation approach:

1. **Template Consistency Check**: Run the synthetic minimal-pair stress panel to verify that changes do not introduce template brittleness or language-sensitivity.
2. **H6 Control Verification**: Ensure that the selective-action control arm maintains zero regressions on previously verified rows.
3. **Frozen Generalization Audit**: After validation hard-slice and validation750 gates are passed, freeze the candidate and run test450 only as an aggregate holdout audit, verifying that improvements remain balanced and the validation-test gap stays $\le 8\%$ without using test row-level failures for tuning.

---

## 5. Implementation Plan

This section converts the hypotheses above into a controlled implementation plan. The goal is not to recover validation rows by reintroducing a hidden repair ladder. The goal is to add a small number of stage-owned, source-backed, ablatable components that improve the reset-native ClinicalAssessment pipeline while preserving the collapse of the validation-test gap.

### 5.1 Controlling Objective

Implement the four generalization hypotheses as bounded reset-stage components:

1. **G1 YTD temporal arithmetic**: calendar-aware denominator windows for explicit year-to-date burden statements.
2. **G2 cluster-without-size convention**: explicit handling of cluster cadence when the number of events per cluster is absent.
3. **G3 relative encounter anchoring**: source-backed prior-encounter duration support where row context already carries a safe prior date or interval.
4. **G4 cyclic/sleep pattern representation**: explicit routing or representation for catamenial and sleep-restricted patterns without inventing unsupported numeric cadence.

The implementation is successful only if the resulting behavior remains:

- stage-owned in `Extract -> Select / Clinical Assessment -> Normalize -> Project -> Verify -> Render / Score`;
- source-backed by selected candidate evidence, row context, or explicit metadata;
- visible in projection/render instrumentation and route families;
- controlled by named ablation switches;
- evaluated first on validation diagnostics and hard slices, not tuned from locked-test row-level failures.

### 5.2 Scope Boundaries

**In scope**

- Editing reset-native projection/render, normalization, route, and artifact-analysis code under `src/clinical_extraction/tasks/seizure_frequency/gan2026/`.
- Adding or updating focused unit tests in `tests/test_gan2026_clinical_assessment_projection_render.py`, `tests/test_gan2026_candidate_set_contract.py`, and any existing hard-panel tests that already exercise reset-stage boundary behavior.
- Adding named ablation switches and report fields so each hypothesis can be disabled independently.
- Producing validation-only diagnostics, hard-slice reports, synthetic/minimal-pair panels, and one-family-off tables.
- Updating project research/status docs after each durable decision.

**Out of scope unless explicitly reauthorized**

- Manual inspection of locked-test row-level failures for development.
- Any rule that maps a single validation row, row id, or Gan-specific synthetic wording directly to a desired label.
- Any broad fallback that changes clinical meaning after the LLM-selected candidate without a named rule id, route trace, and ablation switch.
- Treating `unknown`, `no reference`, seizure-free duration, cluster cadence, and benchmark-format strings as interchangeable scorer conveniences.
- Using aggregate Purist/Pragmatic improvement alone as sufficient evidence for promotion.
- Blending the reset-native ClinicalAssessment pipeline with the separate June 5 frozen holdout protocol.

**Allowed locked-test use**

- A locked test450 run is allowed only as a frozen aggregate generalization audit after candidate code, switches, scorer, model, split manifest, slice definitions, and inspection policy are fixed.
- Allowed reads are aggregate Purist/Pragmatic, predeclared slice aggregates, rendered/null/routed counts, and predeclared policy summaries.
- Row-level test review remains post-hoc final-evaluation analysis only. Any fix informed by test rows starts a new validation-cycle candidate and cannot be counted as the same frozen evaluation.

### 5.3 Rule Portability Classification

Each component must be declared before implementation:

| Hypothesis | Primary owner | Portability category | Why |
| --- | --- | --- | --- |
| G1 YTD temporal arithmetic | Projection / temporal arithmetic | `general` plus `seizure_frequency` | Calendar math is general; applying it to seizure burden denominators is task-specific. |
| G2 cluster-without-size convention | Cluster projection policy | `seizure_frequency` plus `benchmark_format` | Cluster burden is clinically meaningful, but the final string convention is benchmark-facing. |
| G3 prior-encounter anchoring | Row context plus seizure-free projection | `general` plus `seizure_frequency` | Encounter dates are general clinical context; seizure-free rendering is task-specific. |
| G4 cyclic/sleep representation | Boundary projection / route policy | `clinical_epilepsy` plus `seizure_frequency` | Catamenial and sleep-related patterns transfer across epilepsy notes, but must not become Gan-specific label rescue. |

Any proposed marker that is mostly a synthetic-letter artifact must be marked `gan2026_specific` and excluded from paper-facing generalization claims unless separately tested on robustness panels.

---

## 6. Global Implementation Guidelines

### 6.1 Stage Ownership

- **Candidate extraction / ClinicalAssessment** may select the clinical fact and evidence.
- **Normalize** may parse values, dates, units, vague counts, and explicit row context into structured burden fields.
- **Project** may convert structured burden into a benchmark-renderable clinical representation when all operands are source-backed.
- **Verify / Route** must expose policy-sensitive, unsupported, or provenance-sensitive outputs instead of silently rendering them as final labels.
- **Render / Score** may format accepted labels and run scorer audits, but must not choose a different clinical fact.

### 6.2 Trace Requirements

Every new behavior must write all of the following into artifacts:

- `projection_rule_id` or equivalent named rule id;
- `projection_basis` or route family showing the reason for rendering or abstaining;
- `normalization_issues` / instrumentation issue showing what was inferred;
- source phrase, selected candidate id, or row-context source field used;
- ablation switch name;
- component portability category.

If a behavior cannot provide those fields, it should remain diagnostic rather than promoted into the reset pipeline.

### 6.3 Test-First Requirements

Each hypothesis should begin with focused tests before implementation:

- at least one positive renderable case;
- at least one negative/no-overreach case;
- at least one paraphrase/minimal-pair case;
- one ablation-off case proving the switch controls the behavior;
- one route/trace assertion proving the behavior is visible in artifacts.

The focused reset-path suite must pass before running any validation replay. Full-suite status should be recorded if the change affects shared normalization, candidate context, or route logic.

### 6.4 Artifact Requirements

Each hypothesis must produce or update:

- a predeclared mini-plan or section in this document;
- focused unit tests;
- a validation hard-slice or synthetic panel artifact;
- a one-family-off or switch-off replay artifact when it reaches validation;
- a short read/report under `docs/research/` if the result changes a durable decision.

---

## 7. Hypothesis Workstreams

### 7.1 G1: Date-Anchored Temporal Arithmetic

**Implementation intent**

When the selected candidate explicitly says the burden is year-to-date, this-year-so-far, since January, or equivalent, the projection stage should use the clinic/reference date to compute the elapsed denominator. For example, `6 seizures so far this year` in an April clinic note should project from a 4-month observation window, not a full year, if no more specific denominator is present.

**Boundary**

- Allowed: explicit YTD phrases tied to a selected current seizure-frequency candidate and a source-backed reference date.
- Allowed: deterministic calendar math from January 1 of the reference year to the reference month.
- Not allowed: assuming any annual-looking phrase is YTD.
- Not allowed: overriding a more specific selected burden such as `monthly`, `over 7 months`, `since March`, or explicit date-span evidence.
- Not allowed: using gold labels to decide which annual expressions should be reinterpreted.

**Candidate implementation points**

- Extend reset-stage projection/normalization around `clinical_assessment_projection_render.py`, where current-summary annual/YTD policy tests already exist.
- Add a named rule id such as `date_anchored_ytd_denominator_v0`.
- Add an ablation switch such as `project_date_anchored_ytd_denominator`.
- Record instrumentation fields:
  - `ytd_anchor_start`: `YYYY-01-01`;
  - `ytd_reference_date`;
  - `elapsed_months`;
  - `source_phrase`;
  - `candidate_id`;
  - `projection_rule_id`.

**Implementation steps**

1. Write unit tests for January, April, December, and missing-reference-date cases.
2. Add a negative test where an explicit `per year` rate remains annual.
3. Add a negative test where an explicit `over N months` denominator wins over YTD wording.
4. Implement the smallest parser/normalizer needed to mark selected candidates as explicit YTD.
5. Implement projection arithmetic behind the ablation switch.
6. Add route/report accounting for rows touched by `date_anchored_ytd_denominator_v0`.
7. Run focused tests and a validation hard-slice replay over YTD-trigger rows.

**Gate to validation hard slice**

- All focused tests pass.
- No YTD behavior fires without a reference date.
- No behavior fires on plain `yearly`, `per year`, or `over the last year`.
- The ablation switch restores previous output on the synthetic panel.

**Success indicators**

- YTD hard-slice wrong-to-correct transitions exceed correct-to-wrong transitions.
- No increase in unsupported nulls from reference-date parsing.
- Rendered labels carry the expected denominator trace.
- Improvement is visible on rate/denominator mismatch rows, not scattered across unrelated labels.

**Stop / reject conditions**

- The rule changes non-YTD annual rates.
- The rule depends on validation-specific wording lists that do not survive paraphrase tests.
- The rule improves aggregate score while worsening the targeted YTD hard slice or trace validity.

**Results & Replay Evaluation (2026-06-07)**
- **Status**: `promoted_component`
- **validation750 Replay Metrics**:
  - Scored rows: 539 (baseline 498, +41 resolved null renders)
  - Purist correct: 462 (baseline 427, +35)
  - Pragmatic correct: 494 (baseline 456, +38)
  - Exact normalized matches: 403 (baseline 372, +31)
  - Purist accuracy on scored: 85.71% (baseline 85.74%, high precision maintained)
  - Pragmatic accuracy on scored: 91.65% (baseline 91.57%)

### 7.2 G2: Explicit Default Cluster Cadence Mapping


**Implementation intent**

Cluster cadence without an explicit event count per cluster should not be hidden as an ordinary event rate unless that is the predeclared convention. The current hypothesis proposes rendering `X cluster per Y period, multiple per cluster` when the text supports cluster count/cadence but omits event count per cluster.

**Boundary**

- Allowed: cluster-count plus cluster-period expressions where the selected candidate explicitly represents clusters.
- Allowed: rendering unspecified per-cluster burden as `multiple per cluster` only if the annotation/scorer contract accepts that convention.
- Not allowed: converting vague cyclic-window phrases into numeric cluster cadence.
- Not allowed: treating medication cadence or non-seizure temporal context as cluster cadence.
- Not allowed: using this rule to rescue rows where cluster count or period operands are missing.

**Candidate implementation points**

- Current behavior lives around `cluster_cadence_as_event_rate_when_size_absent_v0` in `clinical_assessment_projection_render.py`.
- Existing tests include `test_project_and_render_cluster_cadence_without_size_as_simple_rate`; this should either be replaced by a new convention test or preserved under an ablation/legacy expectation.
- Add a new rule id such as `cluster_cadence_default_multiple_per_cluster_v0`.
- Add an ablation switch such as `project_cluster_cadence_default_multiple_per_cluster`.

**Implementation steps**

1. Confirm accepted label grammar supports `X cluster per Y period, multiple per cluster`.
2. Write positive tests for `2 clusters over 3 weeks`, `1 cluster monthly`, and range-style cluster counts if supported.
3. Write negative tests for missing period, missing cluster count, medication cadence, and vague cyclic windows.
4. Change projection rendering behind a new switch rather than silently changing the old rule id.
5. Update route classification so unresolved cluster-cadence families remain visible when operands are incomplete.
6. Run a validation cluster hard-slice replay using the existing cluster-family reports as the membership seed.

**Gate to validation hard slice**

- Accepted label parser/scorer round-trips the new rendered form.
- Existing unresolved-cluster route families do not collapse into unsupported rendered labels.
- Switch-off replay restores prior simple-rate behavior.

**Success indicators**

- Cluster-without-size hard-slice improves with low regression cost.
- Route counts for genuinely incomplete cluster cadence do not disappear.
- Correctness changes are concentrated in `cluster_cadence_without_size` rows.
- The report can separate `cluster_count_period_size_absent` from `cluster_operands_incomplete`.

**Stop / reject conditions**

- The scorer rejects the new label format or maps it unpredictably.
- The rule renders cyclic/sleep/catamenial phrases without count and period operands.
- Correct-to-wrong transitions exceed wrong-to-correct transitions on the cluster hard slice.

### 7.3 G3: Multi-Encounter Anchor Linking For Seizure Freedom

**Implementation intent**

Resolve seizure-free statements such as `since last visit` only when row context provides a source-backed prior encounter date or explicit relative interval. This pathway already exists in part: prior-encounter context and policy-sensitive traces are present in tests and V5 diagnostics. The workstream should finish the evidence, coverage, and reporting path rather than loosening the anchor policy.

**Boundary**

- Allowed: `candidate_set.row_context.prior_encounter` with date, precision, source phrase, and issue trace.
- Allowed: explicit prior-encounter relative intervals such as `last review three months ago`.
- Not allowed: inferring a prior encounter date from bare `since last visit` when no separate date or interval exists.
- Not allowed: treatment/surgery/dose-change anchors unless a separate event-date context is implemented.
- Not allowed: tuning from locked-test examples of relative anchors.

**Candidate implementation points**

- Existing context and tests are visible around prior-encounter extraction and projection/render instrumentation.
- Use existing trace language where possible:
  - `seizure_free_anchor_from_prior_encounter_context`;
  - `prior_encounter_derived_seizure_free_duration`;
  - route family `rendered_label_supported_but_policy_sensitive`.
- Add or confirm an ablation switch such as `normalize_seizure_free_prior_encounter_anchor`.

**Implementation steps**

1. Audit existing prior-encounter tests and V5/V6 behavior to identify only missing coverage.
2. Add tests for bare `since last visit` with no row context remaining unresolved.
3. Add tests for explicit relative prior encounter intervals rendering with a policy-sensitive trace.
4. Add tests for treatment anchors staying unresolved without event-date context.
5. Add validation reporting that distinguishes:
   - prior encounter present and rendered;
   - prior encounter present but blocked;
   - bare prior encounter phrase with missing context;
   - treatment/event anchor requiring a future event-date component.
6. If gaps remain in row-context extraction, implement only the missing source-backed context extraction.
7. Run a validation since-anchor hard-slice replay.

**Gate to validation hard slice**

- Prior-encounter behavior remains source-backed and policy-sensitive.
- Bare `since last visit/review` without context stays unresolved.
- Existing prior-encounter-derived rows include trace and route visibility.

**Success indicators**

- Increased transparency and correct rendering for source-backed prior-encounter cases.
- No broad reduction in unresolved since-anchor rows through unsupported inference.
- Validation report shows exactly which remaining rows need event-date context rather than prior-encounter context.

**Stop / reject conditions**

- The implementation infers dates from current clinic date alone.
- It treats `last notification period` or administrative contact periods as clinical encounter anchors without explicit policy.
- It silently converts treatment/surgery anchors into seizure-free duration.

**Results & Replay Evaluation (2026-06-07)**
- **Status**: `promoted_component`
- **validation750 Replay Metrics**:
  - Scored rows: 539 (baseline 538, +1 resolved null render)
  - Purist correct: 462 (baseline 461, +1)
  - Pragmatic correct: 494 (baseline 493, +1)
  - Exact normalized matches: 403 (baseline 402, +1)
  - Purist accuracy on scored: 85.71%
  - Pragmatic accuracy on scored: 91.65%
  - Switch `normalize_seizure_free_prior_encounter_anchor` successfully verified via one-family-off validation750 replay (triggering on 5 prior encounter rows when enabled).


### 7.4 G4: Standardized Representation For Catamenial And Sleep Patterns

**Implementation intent**

Catamenial and sleep-restricted patterns should be represented explicitly when clinically meaningful, but they must not be converted into invented numeric cadence. The safest first implementation is likely a route/representation component, not a score-seeking renderer.

**Boundary**

- Allowed: detecting source-backed cyclic or sleep-restricted seizure patterns and routing them to explicit representation classes or policy-sensitive states.
- Allowed: preserving a numeric burden if the candidate also supplies explicit count and period operands.
- Not allowed: mapping `perimenstrual`, `catamenial`, `from sleep`, `on waking`, or `sleep deprivation` to monthly/daily rates by assumption.
- Not allowed: converting trigger-only statements into seizure-free duration.
- Not allowed: changing the final label when a separate ordinary current burden is already selected and supported.

**Candidate implementation points**

- Current helper logic already detects cyclic windows around catamenial phrases and routes incomplete cluster cadence.
- Existing tests already assert conditional sleep-trigger-only phrases stay unrendered.
- Add rule ids such as:
  - `cyclic_window_pattern_routed_v0`;
  - `sleep_restricted_pattern_routed_v0`;
  - `cyclic_pattern_with_explicit_operands_rendered_v0` if a renderable operand case exists.
- Add switches such as `route_cyclic_window_patterns` and `route_sleep_restricted_patterns`.

**Implementation steps**

1. Build a small synthetic hard panel for catamenial-only, catamenial-with-count, sleep-trigger-only, sleep-window-with-count, and ordinary current-rate-with-trigger-context cases.
2. Add tests ensuring trigger-only/cyclic-only cases remain `unknown`, routed, or unresolved rather than numeric.
3. Add tests ensuring explicit count/period operands still render when clinically supported.
4. Add a representation field or route family that distinguishes cyclic/sleep pattern debt from generic `cluster_cadence_values_required_v0`.
5. Update reports so null/rendered rows are split by cyclic-window, sleep-restricted, trigger-only, and explicit-cadence cases.
6. Run the synthetic panel first, then a validation hard slice seeded from existing null-rendered reports.

**Gate to validation hard slice**

- No trigger-only pattern renders as a numeric rate.
- Explicit operand cases render only when count and period are present.
- Route families preserve cyclic/sleep semantics instead of collapsing into generic incomplete-value buckets.

**Success indicators**

- Better failure taxonomy and route precision for cyclic/sleep rows.
- No regression in existing conditional sleep-trigger tests.
- If any rows become rendered, they are explainable by explicit operands rather than pattern defaults.
- The hard-slice report can support a paper-facing claim about transparency even if aggregate score does not improve.

**Stop / reject conditions**

- Catamenial phrases become a hidden `1 per month` shortcut.
- Sleep-trigger language becomes a seizure-free or no-reference shortcut.
- Route precision improves only by hiding rows from the main evaluation surface.

---

## 8. Experiment Gates

### Gate 0: Pre-Implementation Design Gate

Before writing production behavior for a hypothesis:

- Declare the rule id, owner stage, portability category, ablation switch, expected artifact fields, and hard-slice membership rule.
- Identify which existing tests must change and which must remain invariant.
- Confirm whether the behavior is render-producing, route-producing, or instrumentation-only.

Exit criteria:

- The component can be disabled independently.
- The expected behavior can be tested without using gold labels.
- The proposed implementation does not require locked-test row review.

### Gate 1: Focused Unit / Synthetic Panel Gate

Run focused tests and synthetic/minimal-pair panels.

Exit criteria:

- Positive, negative, paraphrase, and ablation-off tests pass.
- No unsupported schema/parse failures.
- Trace fields are present and specific.
- Existing guardrail tests for conditional sleep, prior encounter, and cluster operands remain green.

### Gate 2: Validation Hard-Slice Gate

Run the candidate only on predeclared validation hard slices, not a broad aggregate first.

Required report fields:

- slice definition and row count;
- baseline output;
- candidate output;
- ablation-off output;
- wrong-to-correct and correct-to-wrong counts;
- newly rendered, newly null, newly routed counts;
- route family transitions;
- evidence/provenance validity;
- examples from validation only.

Exit criteria:

- The named failure family improves or becomes more transparent.
- Regression cost is acceptable and localized.
- The result explains a mechanism, not just an aggregate bump.

### Gate 3: Validation750 Replay Gate

Run validation750 only when the hard-slice result changes a project decision or produces a durable comparison artifact.

Exit criteria:

- Full validation replay is predeclared with reason, switches, comparator, and stop rule.
- Render/null/route counts are stable and explainable.
- Purist/Pragmatic change is reported alongside hard-slice and ablation evidence.
- The validation-test gap hypothesis remains plausible without looking at test rows.

### Gate 4: Frozen Generalization Audit Gate

Run test450 only if the user explicitly authorizes a frozen aggregate audit.

Exit criteria:

- Candidate code, model, scorer, split manifest, switches, and analysis plan are frozen.
- Slice definitions are fixed from validation/synthetic criteria only.
- No row-level test failures are inspected for development.
- Any post-hoc test row analysis is documented as final-evaluation analysis and does not feed back into the same candidate.

---

## 9. Success Indicators

### Component-Level Success

- Each hypothesis has a named rule id, switch, route/trace fields, and tests.
- One-family-off replay shows the expected behavior disappears when disabled.
- Hard-slice wrong-to-correct transitions exceed correct-to-wrong transitions, or route taxonomy improves without claiming accuracy improvement.
- Evidence and selected-candidate provenance remain valid.
- The change is explainable in a paper table as a controlled component, not an incidental repair.

### Pipeline-Level Success

- Validation rendered/null/routed changes are explainable by named families.
- Validation Purist and Pragmatic improve or stay stable while transparency improves.
- The validation-test gap remains at or below the current acceptable ceiling of `<= 8%` under a frozen aggregate audit.
- No hypothesis increases hidden semantic repair or reduces audit visibility.
- Reset-stage focused tests and the broader suite remain green.

### Research-Claim Success

- The plan supports the claim that gains came from structural clinical representation and calendar/context reasoning, not validation memorization.
- Rule-category ablations can separate general date/context logic from seizure-frequency logic and benchmark-format rendering.
- The resulting reports can become paper-facing component ablation and failure-taxonomy tables.

---

## 10. Reporting Checklist

Every completed workstream should leave behind:

- implementation notes with rule id, owner, switch, and portability category;
- focused test names and results;
- hard-slice artifact path and summary;
- one-family-off artifact path and summary;
- validation750 replay path if run;
- frozen test aggregate audit path if explicitly authorized and run;
- interpretation language stating whether the result is promoted, diagnostic, rejected, or deferred.

Recommended status labels:

- `promoted_component`: passed unit, hard-slice, trace, and validation replay gates.
- `diagnostic_only`: useful mechanism evidence, not safe for pipeline promotion.
- `route_only`: improves transparency/failure taxonomy without rendering new labels.
- `deferred_contract`: needs a broader context schema such as event-date extraction.
- `rejected_overreach`: failed because it inferred unsupported clinical facts.

---

## 11. Immediate Execution Order

The safest order is:

1. **G1 YTD temporal arithmetic**, because it is clean calendar math with a narrow trigger and a large named rate/denominator error family.
2. **G3 prior-encounter anchoring audit/finish**, because part of the infrastructure exists and the next step is mostly coverage/reporting discipline.
3. **G2 cluster-without-size convention**, because it may require scorer grammar confirmation and could affect benchmark-facing label semantics.
4. **G4 cyclic/sleep representation**, because the safest first outcome may be better routing rather than accuracy improvement.

Do not batch all four into one validation replay. Each should pass its own Gate 0-2 sequence first. A combined validation750 replay is appropriate only after individual hard-slice results are understood and switches make one-family-off attribution possible.
