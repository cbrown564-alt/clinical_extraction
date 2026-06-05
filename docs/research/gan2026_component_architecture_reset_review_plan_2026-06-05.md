# Gan 2026 Component Architecture Reset Review Plan

Date: 2026-06-05

Status: planning document for a validation250 mechanics reset. This document
does not authorize new holdout work, benchmark-comparable claims, or row-level
locked-test review.

## Why This Reset Exists

The `hybrid_multi_component_staged_assembly_v1` program produced useful
artifacts, but the assembly did not function as the intended clear hybrid
architecture. The current system is too hard to explain and too easy to
misinterpret:

- the raw adjudicator can collapse to the deterministic top label without making
  a transparent selection decision;
- label repair, normalization, projection, and benchmark rendering are not
  cleanly separated in the artifacts;
- multiple components perform similar safety, fallback, selection, or projection
  roles under different names;
- fields such as `safety_floor`, `h6_regression`, `adapter_layer`,
  `selected_state`, `projection_gate`, and `release_lane` are useful audit
  fragments but do not describe a coherent user-facing pipeline;
- the component ownership story is muddy: deterministic rules sometimes provide
  the fact, sometimes the fallback, sometimes the projection, and sometimes the
  final label;
- LLM outputs that should have been normalized or projected as source facts
  were often treated as directly scorable labels, making the LLM look worse and
  obscuring whether the clinical fact was correct.

The reset objective is not to squeeze more score out of the current artifact. It
is to make the pipeline mechanically intelligible, inspectable, and faithful to
the intended division of labor before any further full-validation or holdout
work.

## Intended Architecture

The target architecture is:

```text
Extract -> Select -> Normalise -> Project -> Verify -> Render/Score
```

Each stage must have one clear job, one clear schema, and one clear provenance
contract.

### Extract

Goal: identify a broad set of candidate seizure-frequency facts with rich
metadata.

Allowed sources:

- deterministic rules;
- state graph nodes derived from deterministic extractions;
- LLM-generated candidate facts;
- retrieved-example or few-shot candidate proposals, if explicitly enabled.

The extract stage should not decide the final answer. It should emit candidate
facts such as:

- event type or semiology;
- count;
- period or duration;
- temporality and currentness;
- assertion status;
- evidence span;
- source id;
- uncertainty flags;
- whether the fact is directly computable, partially specified, or qualitative.

### Select

Goal: choose the clinically relevant candidate or candidate set from the
extracted facts.

Expected LLM role:

- reason over the rich candidate object;
- identify which candidate or combination represents the clinical current state;
- preserve ambiguity, contradiction, and incompleteness;
- cite source ids and exact evidence;
- return a selected fact object, not a benchmark-facing label.

The selector should not be rewarded for copying the deterministic top label. If
it chooses the deterministic candidate, the artifact must say why: for example
because it is the most current explicit frequency, because competing candidates
are historical, or because an LLM candidate is unsupported.

### Normalise

Goal: convert extracted or selected source-near facts into standard internal
forms without changing clinical meaning.

Examples:

- `daily`, `every day`, and `once per day` become the same normalized rate;
- `two seizures weekly` becomes count `2`, period `week`;
- `seizure-free for nine months` becomes state `seizure_free`, duration
  `9 months`;
- `fewer on light shifts` remains a qualitative or incomplete fact, not a fake
  count.

Normalization is deterministic. It may parse, canonicalize, and validate. It
must not silently choose among competing clinical interpretations.

### Project

Goal: apply task-specific benchmark policy to a selected normalized clinical
state.

Projection answers questions such as:

- how to aggregate multiple semiologies;
- whether to prefer current month, prior month, or a clinician summary;
- how to handle seizure-free intervals with breakthrough events;
- how to represent cluster frequency versus per-cluster burden;
- how to map ambiguity or insufficient denominator information;
- how to render a clinically meaningful state into a Gan-compatible label.

Projection is deterministic and policy-versioned. Projection can be wrong, so
it must be ablatable and attributed separately from extraction or selection.

### Verify

Goal: route hard or risky cases to a verifier that can affirm, reject, abstain,
or require human review.

Verifier candidates include:

- multiple competing current events;
- ambiguous frequency or denominator;
- uncertain seizure validity;
- conflict between seizure-free claims and active-event evidence;
- cluster/per-cluster ambiguity;
- source facts whose projection would change a comparator-correct label.

The verifier is not a broad second selector. It should be invoked only by
predeclared routing rules and should emit a clear action:

- `affirm`;
- `reject`;
- `abstain`;
- `human_review`.

## Immediate Clarification From The GPT-4.1 Mini Holdout Source Run

The GPT-4.1 mini source run exposed a design failure:

- the raw adjudicator matched the deterministic top label on all 450 test rows;
- the adapter layer changed 0 rows;
- the LLM candidate selector often emitted clinically suggestive but
  scorer-unparseable labels;
- applying a frozen selective safety-floor replay to the same source artifact
  produced aggregate gains, but that does not mean the assembled architecture is
  conceptually healthy.

Interpretation:

The system currently lets deterministic rules dominate final selection. LLM
outputs are present, but the assembly does not consistently convert them into
selected normalized clinical facts before projection. The LLM is therefore often
treated either as an ignored evidence sidecar or as a raw label generator, both
of which are wrong for the intended architecture.

## Core Review Questions

Every existing component must answer these questions before it remains in the
architecture.

### Role

- Is this component extract, select, normalise, project, verify, render, score,
  or report?
- Is it doing more than one of those jobs?
- If it is doing more than one job, should it be split?
- If another component already does the same job, which one should survive?

### Input Contract

- What schema does this component consume?
- Does it consume raw text, candidates, selected facts, normalized facts,
  projected facts, or scorer-facing labels?
- Does the input contain the evidence and source ids needed for the component's
  decision?
- Is the component relying on hidden row-level context that is not represented
  in its schema?

### Output Contract

- What schema does this component emit?
- Is the output a fact, a selected fact, a normalized fact, a projected decision,
  an action, or a scorer-facing label?
- Does the output preserve uncertainty, contradiction, and incompleteness?
- Does the output include component owner, policy id, evidence ids, and issue
  flags?

### Attribution

- Which source supplied the clinical fact?
- Which source selected the fact?
- Which deterministic policy normalized it?
- Which deterministic policy projected it?
- Which verifier, if any, approved or blocked it?
- Which final component owns the scorer-facing label?

### Failure Mode

- What kinds of errors can this component create?
- Can it create C->W regressions?
- Can it hide a model error behind deterministic repair?
- Can it hide a deterministic projection error behind an LLM selection label?
- Can it turn ambiguity into false precision?

### Evaluation

- What is the correct validation250 test for this component?
- What metrics matter besides full-row score?
- What row-level examples must be inspected on validation250?
- What aggregate counters must be emitted for validation750 later?
- What would make this component rejected, narrowed, or renamed?

## Component Inventory To Rationalise

This inventory is deliberately uncomfortable. It should be reduced, renamed, or
split during the review.

| Current Name Or Family | Suspected Role | Review Concern |
| --- | --- | --- |
| deterministic candidates | extract/normalise | usually useful, but sometimes implicitly selects highest burden |
| deterministic top candidate | select/project/render | overloaded; may be too dominant as default final answer |
| state graph nodes | extract/normalise | useful fact graph, but broad projection regressed badly |
| state graph projection | project/render | broad replacement unsafe; keep only gated policies |
| LLM candidate selector raw | extract/select mixed | emits useful facts but labels are often unnormalized/unscorable |
| hybrid adjudicator raw | select/render mixed | in latest run copied deterministic top on every row |
| adapter layer | normalise/repair/render | changed 0 rows in latest run; role unclear |
| H5 repair policy | normalise/repair | must separate format repair from semantic repair |
| selective safety floor | verify/action/project guard | useful but should be reframed as verifier or safety gate |
| projection boundary gate | project/verify | promising narrow policy; should become named projection rule |
| boundary/renderer typed-event layer | extract/project/render | useful rare component, but name hides intended schema |
| untagged nonprediction release | action fallback | useful validation guardrail; not core clinical selection |
| staged action policy | verify/action | should be part of Verify stage, not mixed with projection |
| H6/H9/H10 sidecars | report/audit | useful instrumentation, not conceptual pipeline stages |
| component evidence matrix | report/provenance | should be redesigned around target stage schemas |

## Validation250 Review Program

All row-level review happens on validation250. Locked test remains untouched for
development.

### Phase 0: Freeze The Review Surface

Deliverables:

- define the exact validation250 row set;
- record source artifacts currently used by each component;
- forbid score-driven changes outside validation250 during this mechanics
  review;
- create a review ledger with one entry per component decision.

Questions:

- Is validation250 the first 250 validation rows, an existing saved validation250
  artifact, or a stratified validation250 panel?
- Which previously saved artifacts are allowed as inputs?
- Are live model calls allowed on validation250, or only saved replays?

Exit gate:

- one manifest names rows, source artifacts, model routes, prompt versions, and
  allowed outputs.

### Phase 1: Rebuild The Schema From First Principles

Deliverables:

- `ExtractedCandidate`;
- `CandidateSet`;
- `SelectedClinicalFact`;
- `NormalizedClinicalState`;
- `ProjectionDecision`;
- `VerificationDecision`;
- `FinalRenderedLabel`;
- `PipelineTrace`.

Each schema must include:

- component owner;
- source ids;
- exact evidence spans;
- uncertainty flags;
- contradiction flags;
- parse/normalization/projection issue lists;
- whether the object is clinical, benchmark-policy, or scorer-facing.

Hard questions:

- What is the smallest internal representation that can express rate,
  seizure-free duration, no-reference, unknown, unresolved multiple, clusters,
  and qualitative ambiguity?
- Should cluster burden be represented as a separate axis rather than a label
  string?
- Should seizure-free duration be a state with interval metadata rather than a
  label string?
- Which fields are clinical truth and which fields are Gan convention?

Exit gate:

- every current artifact field maps to a new schema field, a deprecated field,
  or an explicit "do not carry forward" decision.

### Phase 2: Extract Review

Inputs:

- deterministic candidate extraction;
- state graph node extraction;
- LLM candidate generation;
- any few-shot/retrieval candidate generation.

Validation250 tasks:

- count candidate recall by gold kind and hidden family;
- count candidate burden per row;
- inspect whether LLM candidates contain clinically correct facts even when
  labels are unscorable;
- separate missing candidate failures from downstream selection/projection
  failures.

Hard questions:

- Are deterministic candidates too narrow, too broad, or too selector-like?
- Does LLM extraction add new clinical facts not found by deterministic rules?
- Are LLM candidates failing because facts are wrong or because label strings
  are not normalized?
- Should LLM extraction emit structured facts only, never scorer labels?

Exit gate:

- extract stage produces a candidate set that is broad enough to support the
  selector without forcing deterministic dominance.

### Phase 3: Select Review

Inputs:

- candidate sets from Phase 2;
- exact evidence and source ids;
- explicit instructions for currentness, major/minor semiology, ambiguity,
  clusters, and seizure-free conflicts.

Validation250 tasks:

- run or replay LLM selection over candidate sets;
- compare selected source ids against deterministic top source ids;
- count when the selector agrees with deterministic top and why;
- count when the selector chooses an LLM-only candidate, a deterministic
  candidate, a graph candidate, or abstains;
- evaluate selection correctness before normalization/projection when possible.

Hard questions:

- Is the selector actually selecting, or just copying the deterministic top?
- Does the prompt over-anchor on deterministic candidates because they are shown
  first or framed as authoritative?
- Should deterministic top be hidden, demoted, or represented as one candidate
  among many?
- Should the selector select one fact, multiple facts, or a structured conflict
  object?

Exit gate:

- selected clinical facts are understandable without looking at final labels.

### Phase 4: Normalisation Review

Inputs:

- selected source-near facts;
- raw candidate facts from LLM and deterministic extraction.

Validation250 tasks:

- normalize common rate expressions;
- normalize seizure-free duration expressions;
- normalize no-reference and unknown states;
- preserve incomplete qualitative facts without inventing false precision;
- record normalization failures separately from clinical selection errors.

Hard questions:

- Why did strings such as `seizure_free`, `cluster_frequency`, `daily`, and
  `no-reference` become unscorable instead of normalized internal states?
- Which label repairs are format-only and which are semantic?
- When should normalization fail and force projection/verifier abstention?
- Are we using scorer-facing label strings too early?

Exit gate:

- LLM-selected facts are normalized into internal states before projection;
  unscorable raw strings are no longer treated as final labels.

### Phase 5: Projection Review

Inputs:

- normalized clinical states;
- ambiguity and contradiction flags;
- projection policy decisions from ACD logs and prior RQ experiments.

Validation250 tasks:

- apply projection rules one at a time;
- report W->C, C->W, exact-label changes, and semantic-state changes;
- keep broad graph projection rejected unless a narrow policy justifies it;
- separate clinical state from benchmark-rendered label.

Hard questions:

- Which projection policies are truly benchmark-specific rather than clinical
  extraction?
- Which projection rules are narrow enough to transfer?
- Do any projection rules depend on validation-specific examples?
- Should projection produce multiple alternatives plus a verifier route rather
  than a single label?

Exit gate:

- every scorer-facing label has a projection policy id and a clinical-state
  input trace.

### Phase 6: Verify And Action Review

Inputs:

- projection decisions;
- risk flags;
- candidate conflict objects;
- safety-floor predicates.

Validation250 tasks:

- define verifier routes for hard cases;
- test deterministic route precision;
- test LLM verifier decisions only on routed subsets;
- distinguish `abstain`, `human_review`, and `monitor`;
- remove "safety floor" language where a clearer verifier/action name exists.

Hard questions:

- Is the safety floor a verifier, a fallback policy, or a projection guard?
- When should a comparator-correct label be preserved?
- When should a risky LLM-selected fact be rejected versus sent to human review?
- Can the verifier affirm a selected fact without rendering a final label?

Exit gate:

- action policy is no longer mixed into extraction, selection, normalization, or
  projection.

### Phase 7: Trace And Explainability Review

Deliverables:

- one validation250 trace artifact;
- one compact component evidence table;
- one row walkthrough template;
- one architecture diagram using target stage names.

For each validation250 row, the trace must answer:

1. What candidates were extracted?
2. Which candidate or fact was selected?
3. How was it normalized?
4. Which projection policy rendered it?
5. Was a verifier invoked?
6. What final action and label were emitted?
7. Which stage owns any error?

Exit gate:

- a human reviewer can explain ten sampled rows without knowing legacy component
  names.

### Phase 8: Rationalise Or Delete Legacy Components

For every legacy component, choose exactly one disposition:

- keep unchanged;
- keep but rename;
- split into multiple stages;
- merge into another component;
- demote to diagnostic-only;
- delete from the assembly path.

Required decisions:

- whether `hybrid_adjudicator_raw` survives as a selector;
- whether `adapter_layer` survives as a distinct component;
- whether `selective_safety_floor_gate_v0` is renamed into verifier/action
  policy language;
- whether `state_graph_projection` survives only as narrow named projection
  policies;
- whether LLM candidate labels are removed from scorer-facing paths until after
  normalization/projection.

Exit gate:

- a new assembly architecture exists with fewer, clearer stage names and no
  duplicate hidden jobs.

## Proposed New Artifact Names

Use names that describe stage and role rather than experiment history.

| Stage | Proposed Artifact |
| --- | --- |
| Extract | `gan2026_validation250_candidate_set_v0` |
| Select | `gan2026_validation250_selected_fact_v0` |
| Normalise | `gan2026_validation250_normalized_state_v0` |
| Project | `gan2026_validation250_projection_decision_v0` |
| Verify | `gan2026_validation250_verification_action_v0` |
| Trace | `gan2026_validation250_pipeline_trace_v0` |
| Review ledger | `gan2026_component_architecture_reset_ledger_v0` |

Legacy hypothesis names such as H5, H6, H9, and H10 may remain in provenance
notes, but they should not be primary architecture names.

## Minimum Validation250 Reports

The reset should produce these reports before returning to validation750:

1. Candidate recall and burden report.
2. Selection behavior report.
3. Normalization failure and repair taxonomy.
4. Projection policy ablation report.
5. Verification routing and action report.
6. End-to-end trace review over validation250.
7. Legacy component disposition ledger.
8. Revised architecture diagram and schema contract.

## Explicit Non-Goals

- No new locked-test development.
- No benchmark-comparable claim.
- No score-first optimization before schema mechanics are clear.
- No hidden semantic repair under "normalization".
- No LLM output treated as a final scorer label before deterministic
  normalization and projection.
- No final assembly whose stages cannot be explained in Extract, Select,
  Normalise, Project, Verify terms.

## First Concrete Next Step

Create the Phase 0 validation250 manifest and review ledger.

The first review meeting or work session should answer only:

1. What exact validation250 rows are in scope?
2. Which saved artifacts are allowed inputs?
3. Are live GPT-4.1 mini and Qwen calls allowed on validation250, or do we use
   saved replays only?
4. What is the initial `ExtractedCandidate` schema?
5. Which legacy components are temporarily frozen while the reset proceeds?

Only after those answers are recorded should implementation resume.
