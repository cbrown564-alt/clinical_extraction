# Gan 2026 Component Architecture Reset Completed Tasks

Date: 2026-06-05

Status: completed-task and decision record for validation250 mechanics work.
The active outstanding plan now lives in
`docs/research/gan2026_component_architecture_reset_review_plan_2026-06-05.md`.
This document preserves historical decisions, generated artifacts, row reviews,
and verification notes. It does not authorize new holdout work,
benchmark-comparable claims, or row-level locked-test review.

## Validation750 Reset Addendum On 2026-06-06

The reset thread later moved beyond the original validation250 verifier/action
boundary. This addendum records the durable validation750 update so the
completed-tasks document does not stop at the older 5-row route surface.

### Validation750 V6 Mechanics State

- Fresh no-call replay `context_repair_v6` reached all 750 validation rows
  under locked split discipline.
- Rendered-label rows increased to 580 and true null renders fell to 170.
- Scored rendered rows reached 488/580 Purist-correct on the
  validation-development surface.
- The verifier route surface expanded sharply to 276 rows, but this was not a
  simple growth in clinical ambiguity. The new route load is dominated by
  provenance-sensitive families led by
  `selected_evidence_missing_exact_trace` plus
  `selected_source_id_invalid`.
- The resulting interpretation is that reset reporting must now separate:
  clinical/policy ambiguity routes, upstream parser/policy debt, and
  provenance-only audit routes.

### Post-V5 Ports And Contract Decisions Preserved

- Ported mature old behavior into reset-stage ownership without broad fallback:
  selected-evidence frequency repair, vague period rates, diary date-list
  recovery, seizure-free duration/date instrumentation, current-vs-historical
  policy nodes, major recent relapse priority, and provenance route families.
- Standardized reset-stage issue language around plain-language `values`.
  Parsed quantities remain deterministic stage-owned data, but artifact wording
  is no longer parser-jargon heavy.
- Added explicit cluster route ownership: when cadence remains unresolved but
  per-cluster burden is renderable, the route family is
  `unresolved_cluster_cadence_with_per_cluster_burden`.
- Preserved the guardrail that provenance families are report/verification
  concerns, not silent promotion triggers and not evidence to collapse into the
  first verifier success/failure table.

### Documentation Artifacts Added

- `docs/research/gan2026_validation750_context_repair_v6_read_2026-06-06.md`
- `docs/research/gan2026_validation750_route_bucket_split_v6_2026-06-06.md`
- `docs/research/gan2026_validation750_cluster_family_pass_v6_2026-06-06.md`
- `docs/research/gan2026_validation750_verifier_candidate_surface_v6_2026-06-06.md`
- `docs/research/gan2026_validation750_null_action_taxonomy_v6_2026-06-06.md`
- `docs/research/gan2026_validation750_first_verifier_report_predeclaration_v6_2026-06-06.md`
- `experiments/gan2026_reset_stage_component_inventory_v0_2026-06-06.md`

### Resume Boundary After The Addendum

- Do not treat the full 276 routed rows as the first verifier score table.
- Keep the 220 provenance-only routed rows in audit/instrumentation appendices.
- Use the reset-stage component inventory to define the first component-level
  ablation report surface before any broader verifier promotion language.

## Work Completed On 2026-06-05

### Phase 0 Surface

- Defined `validation250` as the first 250 rows from the `validation` split in
  `gan2026_split_v1`.
- Recorded the Phase 0 surface in
  `docs/research/gan2026_component_architecture_reset_phase0_manifest_2026-06-05.md`.
- Allowed only validation-row-level artifacts needed to reconstruct component
  mechanics. Locked-test row-level artifacts remain excluded; locked-test
  aggregate summaries may only motivate.
- Froze legacy behavior for `hybrid_adjudicator_raw`, `adapter_layer`, `H5
  repair policy`, `selective_safety_floor_gate_v0`, `state_graph_projection`,
  `boundary/renderer typed-event layer`, `untagged_nonprediction_release`,
  `staged_action_policy`, `H6/H9/H10 sidecars`, and
  `component_evidence_matrix`.

### Candidate Schema Decisions

- `ExtractedCandidate` is a source-near member of a row-level `CandidateSet`,
  emitted after extraction and before select/normalise/project/verify/render.
- Candidate kinds are `frequency_rate`, `cluster_frequency`, `seizure_free`,
  `last_event_only`, `unknown_frequency`, and `no_reference`.
- `event_type` is one of `seizure`, `seizure_like_event`,
  `non_epileptic_event`, or `unclear_event`; `event_subtype` remains
  source-near text or null.
- `temporality` is a single field: `current`, `recent`, `historical`, or
  `unclear`.
- `certainty` is binary: `certain` or `uncertain`. Uncertain candidates require
  a fixed-list `certainty_reason`: `vague_count`, `unclear_time_period`,
  `approximate_wording`, `conditional_statement`, or `other`.
- `assertion_status` remains provisional: `asserted`, `negated`, `uncertain`,
  or `conditional`. Phase 1/2 should assess whether it actually affects
  downstream selection or verification.
- Kind-specific detail objects are retained, but LLM-owned fields stay
  source-near. Deterministic normalization owns parsed counts, ranges, time
  periods, intervals, durations, and canonical operands.
- `cluster_details` is the distinctive cluster object:
  `cluster_frequency`, `events_per_cluster`, `cluster_count`, and
  `cluster_period`.
- For ordinary frequency, seizure-free, last-event-only, unknown, and
  no-reference candidates, the LLM should primarily provide `source_phrase`;
  parser-like fields are filled later by deterministic normalization.
- `source_artifact`, ids, row index, spans, source ids, and other known
  provenance fields are generated by deterministic assembly, not selected by the
  model.
- `evidence_span.text` is the canonical copied evidence text.
  `evidence_span.start_char` and `evidence_span.end_char` are populated
  deterministically. `raw_text` is redundant and should not be carried forward in
  `ExtractedCandidate`.
- Row-level ambiguity and conflict are deferred to router/verifier review over
  the full candidate set, not encoded as per-candidate contradiction flags.

### Schema Smoke And LLM Probe

- Created the saved-artifact schema smoke report:
  `docs/research/gan2026_extracted_candidate_schema_mapping_smoke_2026-06-05.md`.
- Added a fresh LLM schema probe component:
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_extracted_candidate_schema_probe.py`.
- Registered the probe in
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/llm_pipeline_cli.py`
  as `--pipeline llm_extracted_candidate_schema_probe`.
- Ran iterative validation probes from v0 through v5. Earlier versions showed
  that asking the LLM to parse operands caused brittle range/interval handling,
  duplicate repeated values, and exact-copy issues.
- Final probe version `gan2026_extracted_candidate_schema_probe_v5` uses a
  source-near LLM draft schema, deterministic assembly, deterministic evidence
  repair, and deterministic trigger-only cluster filtering.
- The v5 15-row live run completed with 15/15 candidate sets, 21 candidates, 0
  call failures, 0 parse/validation failures, 0 evidence errors, 0 source-phrase
  errors, and 1 intended assembly issue for a skipped trigger-only cluster
  draft.
- Key v5 artifact:
  `experiments/gan2026_extracted_candidate_schema_probe_validation15_gpt41mini_v5_2026-06-05.md`.

### Implementation Notes

- Added a neutral copy-artifact repair case for another malformed
  less-than-or-equal variant in `src/clinical_extraction/core/evidence.py`.
- Added the corresponding focused test case in
  `tests/test_gan2026_llm_only_typed_operations_reasoner.py`.
- Verification used focused tests plus prompt-only and live probe runs; the last
  focused test command passed with 14 tests.

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
- temporality;
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
- how to map ambiguity or insufficient time-period information;
- how to render a clinically meaningful state into a Gan-compatible label.

Projection is deterministic and policy-versioned. Projection can be wrong, so
it must be ablatable and attributed separately from extraction or selection.

### Verify

Goal: route hard or risky cases to a verifier that can affirm, reject, abstain,
or require human review.

Verifier candidates include:

- multiple competing current events;
- ambiguous frequency or time period;
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
  artifact, or a stratified validation250 panel? Answer: first 250 validation
  rows from `gan2026_split_v1`, recorded in
  `docs/research/gan2026_component_architecture_reset_phase0_manifest_2026-06-05.md`.
- Which previously saved artifacts are allowed as inputs? Answer: validation
  row-level artifacts needed to reconstruct component mechanics are allowed;
  locked-test row-level artifacts are excluded. Locked-test aggregate summaries
  may be cited only as motivation.
- Are live model calls allowed on validation250, or only saved replays? Answer:
  saved replays only for Phase 0 and schema reconstruction. Live calls require a
  later frozen schema contract, named route/prompt/cache policy, and
  predeclared mechanics question.

Exit gate:

- one manifest names rows, source artifacts, model routes, prompt versions, and
  allowed outputs.

### Phase 1: Rebuild The Schema From First Principles

Deliverables:

- `ExtractedCandidate`;
- `CandidateSet`;
- `SelectedCandidateDecision`;
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

LLM-owned extraction fields should stay source-near. The LLM may identify the
candidate statement and broad kind, but parser-like operands such as counts,
ranges, intervals, durations, ids, spans, and source artifacts are generated or
expanded deterministically.

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
- Should LLM extraction stop at source-near phrases, with deterministic
  normalization handling parsed frequency operands? Current answer: yes.

Exit gate:

- extract stage produces a candidate set that is broad enough to support the
  selector without forcing deterministic dominance.

### Phase 3: Select Review

Inputs:

- candidate sets from Phase 2;
- exact evidence and source ids;
- explicit instructions for temporality, major/minor semiology, ambiguity,
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

## Where To Resume Next Session

Phase 0 and the initial Extract schema probe were complete enough to continue.
The 2026-06-05 continuation started Phase 1/2 implementation rather than more
schema brainstorming.

## Continuation On 2026-06-05

### Stable CandidateSet Contract

- Promoted the v5 source-near `ExtractedCandidate` / `CandidateSet` shape into
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/candidate_set.py`.
- Refactored
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_extracted_candidate_schema_probe.py`
  so the LLM probe imports the shared contract instead of owning a private copy.
- Kept `CandidateDraft` as model-owned prompt/runtime schema only; ids,
  provenance, source artifacts, spans, source ids, and stage bookkeeping remain
  deterministic assembly fields.
- Recorded the resolved language in `CONTEXT.md`: deterministic candidate
  labels are extraction provenance for later normalization/projection, not
  selected clinical facts or final scorer answers.

### Deterministic CandidateSet Replay

- Added a deterministic validation250 candidate-set replay builder:
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/candidate_set_replay.py`.
- Generated the named Phase 1/2 artifact family:
  - `experiments/gan2026_validation250_candidate_set_v0.jsonl`
  - `experiments/gan2026_validation250_candidate_set_v0.json`
  - `experiments/gan2026_validation250_candidate_set_v0.md`
- Replay summary over validation250:
  - rows: 250;
  - candidate sets: 250;
  - total candidates: 370;
  - rows with no candidates: 27;
  - mean candidates per row: 1.48;
  - max candidates per row: 5;
  - candidate kinds: 271 `frequency_rate`, 79 `seizure_free`, 13
    `cluster_frequency`, 7 `unknown_frequency`;
  - source-phrase missing candidates: 0;
  - assembly issue rows: 0.
- Added focused tests in `tests/test_gan2026_candidate_set_contract.py`.
- Verification:
  `PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/test_gan2026_candidate_set_contract.py tests/test_gan2026_llm_pipeline_cli.py -q`
  passed with 8 tests.

### Next Decision To Grill

The next unresolved branch is whether the LLM v5 extractor should be promoted
from schema probe to validation250 candidate-source replay. Recommended answer:
not yet as a full validation250 live run. First inspect the deterministic
candidate-set replay failures and candidate burden, then predeclare a narrow
LLM extraction question such as deterministic-miss rows, no-candidate rows, or
cluster/seizure-free boundary rows.

### CandidateSet Diagnostics

- Added extract-stage diagnostics:
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/candidate_set_diagnostics.py`.
- Generated the diagnostic artifact family:
  - `experiments/gan2026_validation250_candidate_set_diagnostics_v0.jsonl`
  - `experiments/gan2026_validation250_candidate_set_diagnostics_v0.json`
  - `experiments/gan2026_validation250_candidate_set_diagnostics_v0.md`
- Added focused tests in `tests/test_gan2026_candidate_set_diagnostics.py`.
- Defined `Compatible-Kind Coverage` in `CONTEXT.md` as an extract-stage
  diagnostic, not normalized-label recall or benchmark performance.
- Validation250 diagnostic summary:
  - compatible-kind coverage: 209/250 rows, 0.836;
  - rows with no candidates: 27;
  - high-burden rows, using threshold >=4 candidates: 8;
  - incompatible or empty rows: 41.
- Coverage by gold candidate kind:
  - `frequency_rate`: 161/161, 1.000;
  - `seizure_free`: 38/38, 1.000;
  - `cluster_frequency`: 6/7, 0.857;
  - `unknown_frequency`: 4/44, 0.091.
- Interpretation:
  - deterministic extraction is broad enough for ordinary frequency and
    seizure-free extraction review;
  - high burden is narrow and inspectable, not a general blocker;
  - the main extract-stage gap is unknown or unresolved multiple wording;
  - one cluster row with gold `unknown, multiple per cluster` lacks a compatible
    extracted cluster candidate.
- Superseded recommendation: at this point the proposed next step was to avoid
  a blanket validation250 live LLM extractor and predeclare only a narrow LLM
  extraction replay over deterministic no-candidate rows plus unknown-frequency
  incompatible rows. The subsequent user correction below replaced this with a
  full validation250 LLM extractor evaluation.
- Verification:
  `PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/test_gan2026_candidate_set_contract.py tests/test_gan2026_candidate_set_diagnostics.py tests/test_gan2026_llm_pipeline_cli.py -q`
  passed with 9 tests.

### Full LLM CandidateSet Validation250

User correction: the extract review must evaluate both deterministic and LLM
candidate sources all the way through the same validation250 mechanics surface.
The earlier narrow-slice recommendation was too fast.

- Ran the full validation250 LLM extractor:
  `llm_extracted_candidate_schema_probe` / `gan2026_extracted_candidate_schema_probe_v5`.
- Generated the LLM candidate-set artifact family:
  - `experiments/gan2026_validation250_llm_candidate_set_v0.jsonl`
  - `experiments/gan2026_validation250_llm_candidate_set_v0.md`
- LLM schema/run summary:
  - rows: 250;
  - candidate sets: 248/250;
  - total candidates: 358;
  - call failures: 2;
  - parse/validation failure rows: 18;
  - evidence error rows: 8;
  - source-phrase error rows: 15;
  - rows with no candidates: 6;
  - candidate kinds: 252 `frequency_rate`, 44 `seizure_free`, 36
    `cluster_frequency`, 22 `last_event_only`, 2 `unknown_frequency`, 2
    `no_reference`.
- Ran the same diagnostics over LLM candidate sets:
  - `experiments/gan2026_validation250_llm_candidate_set_diagnostics_v0.jsonl`
  - `experiments/gan2026_validation250_llm_candidate_set_diagnostics_v0.json`
  - `experiments/gan2026_validation250_llm_candidate_set_diagnostics_v0.md`
- LLM compatible-kind coverage:
  - overall: 196/250, 0.784;
  - `frequency_rate`: 155/161, 0.963;
  - `seizure_free`: 33/38, 0.868;
  - `cluster_frequency`: 6/7, 0.857;
  - `unknown_frequency`: 2/44, 0.045.
- Added deterministic-vs-LLM comparison:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/candidate_set_comparison.py`
  - `tests/test_gan2026_candidate_set_comparison.py`
  - `experiments/gan2026_validation250_candidate_set_comparison_v0.jsonl`
  - `experiments/gan2026_validation250_candidate_set_comparison_v0.json`
  - `experiments/gan2026_validation250_candidate_set_comparison_v0.md`
- Comparison summary:
  - deterministic compatible rows: 209/250, 0.836;
  - LLM compatible rows: 196/250, 0.784;
  - union compatible rows: 212/250, 0.848;
  - both compatible rows: 193;
  - deterministic-only rows: 16;
  - LLM-only rows: 3;
  - neither rows: 38;
  - LLM diagnostic issue rows: 18;
  - LLM missing candidate-set rows: 2.
- Union by gold candidate kind:
  - `frequency_rate`: 161/161, 1.000;
  - `seizure_free`: 38/38, 1.000;
  - `cluster_frequency`: 7/7, 1.000;
  - `unknown_frequency`: 6/44, 0.136.
- Interpretation:
  - deterministic remains the stronger standalone extractor on this
    compatible-kind diagnostic;
  - LLM is not redundant: it contributes three deterministic-miss rows and
    completes cluster compatible-kind coverage in union;
  - LLM extraction has operational/schema risks that deterministic extraction
    does not: 2 call failures and 18 diagnostic issue rows;
  - unknown/unresolved-multiple wording remains the major extract-stage gap for
    both candidate sources.
- Revised recommendation: build `gan2026_validation250_candidate_set_v1` as a
  deterministic+LLM union candidate set with explicit source provenance,
  deduplication, and issue flags. Do not promote LLM-only extraction, and do not
  move to selector design until the union artifact distinguishes LLM rescues,
  deterministic-only rows, neither rows, and LLM evidence/schema failures.
- Verification:
  `PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/test_gan2026_candidate_set_diagnostics.py tests/test_gan2026_candidate_set_comparison.py -q`
  passed with 3 tests.

### CandidateSet Union V1

- Added deterministic+LLM union builder:
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/candidate_set_union.py`.
- Added focused tests:
  `tests/test_gan2026_candidate_set_union.py`.
- Generated the union artifact family:
  - `experiments/gan2026_validation250_candidate_set_v1.jsonl`
  - `experiments/gan2026_validation250_candidate_set_v1.json`
  - `experiments/gan2026_validation250_candidate_set_v1.md`
- Union rules:
  - deterministic candidates are the stable base;
  - LLM candidates are added unless an exact duplicate exists by
    candidate-kind, evidence text, and source phrase;
  - duplicate LLM candidates are merged into the retained candidate's source ids
    and extraction issues;
  - LLM call errors, missing candidate sets, parse/validation errors, evidence
    errors, and source-phrase errors are preserved as union assembly issues;
  - no gold labels, scorer-facing labels, selection, normalization, projection,
    or locked-test data are used.
- Union v1 summary:
  - rows: 250;
  - total candidates: 703;
  - source types: 370 `deterministic_candidate`, 333 `llm_candidate`;
  - candidate kinds: 502 `frequency_rate`, 119 `seizure_free`, 49
    `cluster_frequency`, 22 `last_event_only`, 9 `unknown_frequency`, 2
    `no_reference`;
  - exact duplicate candidates merged: 25;
  - rows with no candidates: 4;
  - mean candidates per row: 2.812;
  - max candidates per row: 10;
  - rows with union assembly issues: 84;
  - LLM missing candidate-set rows: 2;
  - LLM call-error rows: 2;
  - LLM parse/validation issue rows: 18.
- Generated v1 diagnostics:
  - `experiments/gan2026_validation250_candidate_set_v1_diagnostics.jsonl`
  - `experiments/gan2026_validation250_candidate_set_v1_diagnostics.json`
  - `experiments/gan2026_validation250_candidate_set_v1_diagnostics.md`
- v1 compatible-kind coverage:
  - overall: 212/250, 0.848;
  - `frequency_rate`: 161/161, 1.000;
  - `seizure_free`: 38/38, 1.000;
  - `cluster_frequency`: 7/7, 1.000;
  - `unknown_frequency`: 6/44, 0.136.
- v1 candidate burden:
  - high-burden rows at threshold >=4 candidates: 58;
  - rows with no candidates: 4;
  - remaining incompatible or empty rows: 38, dominated by
    `unknown_frequency`.
- Interpretation:
  - v1 is the best extract-stage substrate so far by compatible-kind coverage;
  - v1 also materially increases selector burden and carries LLM reliability
    issues, so selector design must use source provenance and issue flags;
  - the major remaining extract-stage weakness is unresolved/unknown frequency
    wording, not ordinary frequency, seizure-free, or cluster coverage.
- Verification:
  `PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/test_gan2026_candidate_set_union.py tests/test_gan2026_candidate_set_contract.py tests/test_gan2026_candidate_set_diagnostics.py -q`
  passed with 7 tests.

### High-Recall Extract Cycle

User direction: candidate burden is acceptable for now and can be tested as an
experimental variable later. The immediate Extract objective is to improve
candidate recall through both deterministic and LLM candidate sources, then
evaluate which component choices work better after the rest of the pipeline is
built out.

- Added deterministic high-recall unknown-frequency extraction for vague
  quantified current-frequency wording such as:
  - `a few events in the preceding month`;
  - `brief absences occurring on most weekdays`;
  - `several focal seizures last week`.
- Added focused deterministic tests:
  `tests/test_gan2026_deterministic_unknown_candidate_recall.py`.
- Updated the LLM extractor prompt to
  `gan2026_extracted_candidate_schema_probe_v6` with explicit high-recall
  unknown-frequency instructions for vague quantity words such as `multiple`,
  `several`, `many`, `a few`, `handful`, `couple`, and `most weekdays`.
- Added artifact-name parameters to candidate-set replay and union builders so
  the high-recall cycle can be recorded without overwriting the earlier cycle.

#### Deterministic CandidateSet V1

- Generated:
  - `experiments/gan2026_validation250_deterministic_candidate_set_v1.jsonl`
  - `experiments/gan2026_validation250_deterministic_candidate_set_v1.json`
  - `experiments/gan2026_validation250_deterministic_candidate_set_v1.md`
  - `experiments/gan2026_validation250_deterministic_candidate_set_v1_diagnostics.jsonl`
  - `experiments/gan2026_validation250_deterministic_candidate_set_v1_diagnostics.json`
  - `experiments/gan2026_validation250_deterministic_candidate_set_v1_diagnostics.md`
- Summary:
  - total candidates: 377, up from 370;
  - `unknown_frequency` candidates: 14, up from 7;
  - rows with no candidates: 24, down from 27;
  - mean candidates per row: 1.508, up from 1.48;
  - high-burden rows: 8, unchanged;
  - compatible-kind coverage: 216/250, 0.864, up from 209/250, 0.836;
  - `unknown_frequency` compatible-kind coverage: 11/44, 0.250, up from
    4/44, 0.091.

#### LLM CandidateSet V1 / V6

- Ran the full validation250 LLM candidate extractor with v6 prompt.
- Generated:
  - `experiments/gan2026_validation250_llm_candidate_set_v1_v6.jsonl`
  - `experiments/gan2026_validation250_llm_candidate_set_v1_v6.md`
  - `experiments/gan2026_validation250_llm_candidate_set_v1_v6_diagnostics.jsonl`
  - `experiments/gan2026_validation250_llm_candidate_set_v1_v6_diagnostics.json`
  - `experiments/gan2026_validation250_llm_candidate_set_v1_v6_diagnostics.md`
- Summary:
  - candidate sets: 249/250, up from 248/250;
  - total candidates: 383, up from 358;
  - call failures: 1, down from 2;
  - parse/validation issue rows: 12, down from 18;
  - evidence error rows: 9, up from 8;
  - source-phrase error rows: 10, down from 15;
  - rows with no candidates: 4, down from 6;
  - `unknown_frequency` candidates: 67, up from 2;
  - compatible-kind coverage: 218/250, 0.872, up from 196/250, 0.784;
  - `unknown_frequency` compatible-kind coverage: 25/44, 0.568, up from
    2/44, 0.045.

#### High-Recall Component Comparison

- Generated:
  - `experiments/gan2026_validation250_candidate_set_high_recall_comparison_v1.jsonl`
  - `experiments/gan2026_validation250_candidate_set_high_recall_comparison_v1.json`
  - `experiments/gan2026_validation250_candidate_set_high_recall_comparison_v1.md`
- Summary:
  - deterministic compatible rows: 216/250, 0.864;
  - LLM compatible rows: 218/250, 0.872;
  - union compatible rows: 235/250, 0.940;
  - both compatible rows: 199;
  - deterministic-only rows: 17;
  - LLM-only rows: 19;
  - neither rows: 15.
- Union by gold candidate kind:
  - `frequency_rate`: 161/161, 1.000;
  - `seizure_free`: 38/38, 1.000;
  - `cluster_frequency`: 7/7, 1.000;
  - `unknown_frequency`: 29/44, 0.659.

#### CandidateSet Union V2 High Recall

- Generated:
  - `experiments/gan2026_validation250_candidate_set_v2_high_recall.jsonl`
  - `experiments/gan2026_validation250_candidate_set_v2_high_recall.json`
  - `experiments/gan2026_validation250_candidate_set_v2_high_recall.md`
  - `experiments/gan2026_validation250_candidate_set_v2_high_recall_diagnostics.jsonl`
  - `experiments/gan2026_validation250_candidate_set_v2_high_recall_diagnostics.json`
  - `experiments/gan2026_validation250_candidate_set_v2_high_recall_diagnostics.md`
- Summary:
  - total candidates: 735, up from v1's 703;
  - source types: 377 deterministic, 358 LLM;
  - rows with no candidates: 3, down from 4;
  - mean candidates per row: 2.94, up from 2.812;
  - max candidates per row: 10, unchanged;
  - high-burden rows: 69, up from 58;
  - union assembly issue rows: 68, down from 84;
  - compatible-kind coverage: 235/250, 0.940, up from v1's 212/250, 0.848;
  - remaining incompatible or empty rows: 15, all outside ordinary
    frequency/seizure-free/cluster coverage.
- Interpretation:
  - high-recall extract mode materially improves recall while increasing burden
    only moderately at the row level;
  - LLM v6 becomes the stronger standalone compatible-kind extractor, but still
    carries runtime/schema/evidence issues;
  - deterministic high-recall rules provide cheap, stable unknown-frequency
    gains without increasing high-burden rows;
  - v2 high-recall union should be the next selector substrate unless the
    selector proves too sensitive to burden.
- Important caution:
  - expanded recall may harm precision and create downstream confusion,
    especially for `unknown_frequency`;
  - it may be better to judge unknown by the absence of good usable frequency
    evidence rather than by the presence of vague or low-quality evidence;
  - an alternative downstream strategy is to reconstruct unknown from
    uncertain, incomplete, absent, or contradictory candidate signals, or rely on
    a verifier/action route to catch unknown cases;
  - therefore v2 high-recall should be treated as one experimental substrate,
    not as a settled extract design.
- Verification:
  `PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/test_gan2026_deterministic_unknown_candidate_recall.py tests/test_gan2026_candidate_set_contract.py tests/test_gan2026_llm_pipeline_cli.py -q`
  passed with 11 tests before full artifact generation.

### SelectedCandidateDecision Contract V0

- Added:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/selected_fact.py`
  - `tests/test_gan2026_selected_fact_contract.py`
- Schema version:
  - `gan2026_selected_candidate_decision_v0`.
- Contract boundary:
  - `SelectedCandidateDecision` is a minimal selector output before
    normalization, aggregation derivation, projection, verification, rendering,
    or scoring;
  - the model owns only `selected_candidate_ids`, `selection_mode`, and
    `rationale`;
  - candidate kind, evidence, source phrases, temporality, certainty, source
    ids, and non-selected candidate sets are passed through or derived
    deterministically from the source `CandidateSet`;
  - related-event aggregation is represented by selecting multiple candidate
    ids with `selection_mode="related_candidate_group"`, not by asking the
    model to emit operands or a benchmark-facing label.
- Validation rules:
  - `single_candidate` requires exactly one selected candidate id;
  - `related_candidate_group` requires two or more selected candidate ids;
  - `no_reliable_candidate`, `ambiguous`, and `conflict` must not select
    candidate ids;
  - selected candidate ids must be unique.
- Verification:
  `PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/test_gan2026_selected_fact_contract.py tests/test_gan2026_llm_candidate_set_selector_schema_probe.py tests/test_gan2026_llm_pipeline_cli.py -q`
  passed with 17 tests.

### CandidateSet Selector Schema Probe V0/V1/V2

- Added:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_selector_schema_probe.py`
  - `tests/test_gan2026_llm_candidate_set_selector_schema_probe.py`
- Registered the routine LLM CLI pipeline:
  - `llm_candidate_set_selector_schema_probe`
- Prompt/schema versions:
  - validation250 v0 run used
    `gan2026_candidate_set_selector_schema_probe_v0`;
  - v1 removed internal-facing wording from the prompt;
  - current code is bumped to
    `gan2026_candidate_set_selector_schema_probe_v2` with the minimal
    `SelectedCandidateDecision` output.
- Default selector substrate:
  - `experiments/gan2026_validation250_candidate_set_v2_high_recall.jsonl`.
- Probe boundary:
  - consumes a row-level `CandidateSet`;
  - model emits only `selected_candidate_ids`, `selection_mode`, and
    `rationale`;
  - deterministic assembly fills row index, component owner, schema
    bookkeeping, and candidate-id validation;
  - output is `SelectedCandidateDecision`, not a normalized clinical state or
    scorer-facing answer.
- Unknown-frequency comparison preserved:
  - prompt tells the selector to prefer explicit current frequency,
    seizure-free, or cluster-frequency candidates over vague unknown-frequency
    candidates;
  - prompt allows selected `unknown_frequency` only when the extracted unknown
    candidate is the best clinical fact;
  - prompt allows `no_reliable_candidate` with unknown-by-absence when absence
    of reliable usable evidence is the better explanation.
- Current status:
  - schema probe and prompt-only path are implemented;
  - validation25 live run on v2 completed with 25/25 selected facts and 0
    parse/validation failures after treating model-mangled evidence-text copies
    as selection issues rather than assembly failures;
  - validation250 live run on v2 completed as
    `experiments/gan2026_validation250_selected_fact_v0_v2_high_recall.jsonl`
    and
    `experiments/gan2026_validation250_selected_fact_v0_v2_high_recall.md`.
- Validation250 v0 selector summary:
  - rows: 250;
  - call failures: 0;
  - selected fact rows: 248/250;
  - parse/validation failure rows: 2;
  - selection statuses: 240 `selected`, 8 `no_reliable_candidate`, 2 failed;
  - selection bases: 239 `direct_candidate_selection`, 8
    `absence_of_evidence`, 1 `candidate_combination`;
  - selected fact kinds: 170 `frequency_rate`, 41 `seizure_free`, 23
    `cluster_frequency`, 7 `unknown_frequency`, 2 `last_event_only`;
  - unknown basis: 8 `absence_of_usable_frequency_evidence`, 4
    `extracted_unknown_candidate`, 36 `not_applicable`.
- v0 selector contract failures:
  - row 2427: model returned `ambiguous` while also selecting candidate ids;
  - row 3528: model selected `unknown_frequency` without explicit
    `unknown_basis`.
- Important v0 prompt-language caveat:
  - the first selector prompt included internal-facing terms such as
    `benchmark label` and `scorer-facing answer`;
  - these terms are not appropriate model-facing clinical task language and may
    distract the selector from the actual job.
- Prompt revision for next run:
  - bumped prompt version to `gan2026_candidate_set_selector_schema_probe_v1`;
  - replaced internal-facing instruction language with direct clinical wording:
    choose the best current seizure-frequency statement, say when no reliable
    candidate is available, do not calculate or standardize a new answer, and
    distinguish vague unknown-frequency candidates from unknown-by-absence;
  - added a regression test banning `benchmark`, `scorer`, and `pipeline` from
    model-facing task instructions.
- v2 schema/prompt revision:
  - slimmed the model output to selected candidate ids, selection mode, and
    rationale;
  - removed model-owned clinical fact kind, evidence copies, rejected ids,
    unknown basis, support ids, source ids, temporality, certainty, and
    selection status/basis fields;
  - changed the first instruction to: "Review the set of candidate facts
    extracted from the clinical note and choose the fact(s) that best describe
    the patient's current seizure frequency burden.";
  - added `related_candidate_group` so the selector can group multiple related
    current-window candidate facts before downstream deterministic
    normalization/aggregation derivation.
- Validation250 v2 selector run:
  - generated
    `experiments/gan2026_validation250_selected_candidate_decision_v2_v2_high_recall.jsonl`
    and
    `experiments/gan2026_validation250_selected_candidate_decision_v2_v2_high_recall.md`;
  - rows: 250;
  - call failures: 0;
  - parse/validation failure rows: 0;
  - selected decision rows: 250/250;
  - selection modes: 226 `single_candidate`, 21 `related_candidate_group`,
    and 3 `no_reliable_candidate`.
- Added selector diagnostics:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/selected_candidate_decision_diagnostics.py`;
  - `tests/test_gan2026_selected_candidate_decision_diagnostics.py`;
  - `experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.jsonl`;
  - `experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.json`;
  - `experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.md`.
- v2 selector diagnostics summary:
  - invalid selected-reference rows: 0;
  - high-burden rows: 69, all with selected decisions;
  - selected candidate source composition: 200 `llm_only`, 44
    `deterministic_only`, 3 `mixed`, 3 `none`;
  - selected source types by candidate: 222 `llm_candidate`, 48
    `deterministic_candidate`;
  - selected candidate kinds: 175 `frequency_rate`, 48 `seizure_free`, 26
    `cluster_frequency`, 18 `unknown_frequency`, and 3 `last_event_only`;
  - related candidate groups: 21;
  - related groups with heuristic coherence flags: 14;
  - related groups with mixed candidate kind: 13;
  - related groups with mixed temporality: 4;
  - related groups without cluster or shared-kind signal: 3.
- v0/v2 selector comparison:
  - v0 had 2 parse/validation failures; v2 has 0;
  - mapped v0 modes were 217 `single_candidate`, 23
    `related_candidate_group`, 8 `no_reliable_candidate`, and 2 failed;
  - v2 modes are 226 `single_candidate`, 21 `related_candidate_group`, and
    3 `no_reliable_candidate`;
  - only one v0 related-candidate-group row remained a v2 related group; v2
    therefore changes selector behavior, not only schema bookkeeping.
- Interpretation:
  - the minimal selector contract is mechanically healthy and traceable;
  - v2 related groups are an important review surface before normalization:
    some appear to capture same-window aggregation, while others combine active
    frequency with seizure-free context or mix frequency/unknown candidates in
    ways that may need verifier or downstream policy rather than aggregation;
  - do not move directly to scorer-facing rendering from v2 decisions.
- Next run:
  - inspect or diagnose the 21 `related_candidate_group` rows before building
    deterministic normalization/aggregation derivation;
  - then decide whether to revise grouping prompt language, route some
    mixed-kind groups to verifier/defer policy, or proceed with normalization
    that can handle selected candidate groups explicitly.
- Verification:
  `PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/test_gan2026_llm_candidate_set_selector_schema_probe.py tests/test_gan2026_selected_fact_contract.py tests/test_gan2026_llm_pipeline_cli.py -q`
  passed with 15 tests.
  `PYTHONPATH=src .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_selector_schema_probe.py tests/test_gan2026_llm_candidate_set_selector_schema_probe.py src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/llm_pipeline_cli.py tests/test_gan2026_llm_pipeline_cli.py`
  passed.

### Related Candidate Group Review V0

- Continued selector evaluation from the 21 validation250
  `related_candidate_group` rows in
  `experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.jsonl`.
- Added pre-normalization related-group policy diagnostics to:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/selected_candidate_decision_diagnostics.py`;
  - `tests/test_gan2026_selected_candidate_decision_diagnostics.py`;
  - `experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.jsonl`;
  - `experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.json`;
  - `experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.md`.
- These labels are review diagnostics only. They do not normalize, project,
  render, score, or mutate the selector decisions.
- Related-group policy action counts:
  - `aggregate_selected_candidates`: 4;
  - `preserve_as_cluster_axis`: 1;
  - `preserve_as_cluster_modifier_context`: 7;
  - `preserve_as_corrob_seizure_free`: 2;
  - `split_primary_with_context`: 4;
  - `route_to_verifier_before_normalization`: 3.
- Policy interpretation before normalization:
  - same-kind same-window `frequency_rate` groups can be treated as aggregation
    candidates when they do not carry mixed-temporality flags;
  - same-kind `seizure_free` groups are corroborating evidence, not additive
    seizure-free duration;
  - cluster candidates should be preserved as a separate cluster axis or as
    cluster-modifier context, not summed into ordinary frequency rates;
  - cluster plus seizure-free, and frequency plus seizure-free, should become a
    primary selected burden plus contextual seizure-free statement rather than a
    single normalized count;
  - frequency plus unknown-frequency groups without cluster signal should route
    to verifier/defer handling before normalization;
  - same-kind frequency groups with mixed temporality also route to
    verifier/defer handling before normalization, because they may combine a
    total count with a subtype/subcount rather than additive evidence.
- Rows that currently look like straightforward aggregation candidates:
  744, 1591, 1880, and 3774.
- Rows that should not be collapsed into one ordinary frequency rate without
  additional policy:
  338, 466, 1046, 1165, 1573, 3468, 3469, 3643, 3827, 3949, 4026, 4478, 4771,
  4842, 4951, 5476, and 5551.
- Immediate normalization design implication:
  `NormalizedClinicalState` should support selected candidate groups with
  separate primary burden, aggregation inputs, cluster modifiers,
  seizure-free/context statements, and verifier-route flags. It should not
  assume every `related_candidate_group` means arithmetic aggregation.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_selected_candidate_decision_diagnostics.py -q`
  passed with 4 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/selected_candidate_decision_diagnostics.py tests/test_gan2026_selected_candidate_decision_diagnostics.py`
  passed.

### Merged Clinical Assessment Probe V0

User direction: selecting, normalizing, and aggregating candidate facts may be
one clinical reasoning problem rather than three cleanly separable stages. The
new experimental middle stage is therefore:

```text
Extract -> ClinicalAssessment -> Project/Verify/Render
```

- Added `ClinicalAssessment` and `NormalizedBurden`:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/clinical_assessment.py`;
  - `tests/test_gan2026_clinical_assessment_contract.py`.
- Added a new CandidateSet-to-assessment LLM probe:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py`;
  - `tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py`.
- Registered the routine CLI pipeline:
  `llm_candidate_set_clinical_assessment_probe`.
- Contract intent:
  - the LLM owns one overarching clinical assessment of current seizure burden;
  - `primary_candidate_ids` identify the facts that determine the burden;
  - `supporting_candidate_ids` retain corroborating, trigger, pattern,
    seizure-free-outside-window, or other non-additive context;
  - `rejected_candidate_ids` retain historical, subtype/subcount, duplicate, or
    unsafe candidates;
  - `normalized_burden` carries source-near operands and a short clinical phrase;
  - deterministic code still owns later projection, verification, and rendering.
- Prompt examples are general policy examples, not copied problematic rows.
  They cover:
  - additive same-window event types;
  - total count plus subtype/subcount;
  - frequency plus cluster modifier;
  - cluster cadence plus per-cluster burden;
  - seizure-free outside a pattern window;
  - precise count plus vague bursts.
- Prompt-language cleanup:
  - model-facing instructions avoid `benchmark`, `scorer`, `gold`,
    `external evaluator`, and `final label` language;
  - tests scan the full model-facing input payload for these terms.
- Prompt-only validation25 smoke:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_prompt_only_validation25_v0.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_prompt_only_validation25_v0.md`.
- Live validation25 smoke after prompt cleanup:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v0.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v0.md`;
  - rows: 25;
  - clinical assessment rows: 25/25;
  - call failures: 0;
  - parse/validation failures: 0;
  - assessment kinds: 21 `frequency_rate`, 2 `cluster_frequency`, and 2
    `unknown_frequency`;
  - aggregation policies: 15 `single_fact` and 10 `primary_with_context`.
- Initial interpretation:
  - the merged assessment contract is mechanically healthier than the minimal
    selector contract because it gives the model separate primary, supporting,
    and rejected candidate roles;
  - row 466 now selects the monthly frequency as primary and keeps clustering
    as supporting context, which is the behavior the earlier selector lacked;
  - row 338 now carries vague high monthly burden as primary and cluster timing
    as context, rather than grouping both as selected facts;
  - the probe still needs diagnostics before validation250 because some rows
    place duplicate corroborating candidates in `primary_candidate_ids`, and at
    least one inspected row blends historical cluster context into
    `normalized_burden`;
  - therefore v0 is a promising contract smoke, not a promoted assessment
    policy.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_contract.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_llm_pipeline_cli.py -q`
  passed with 13 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/clinical_assessment.py src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/llm_pipeline_cli.py tests/test_gan2026_clinical_assessment_contract.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_llm_pipeline_cli.py`
  passed.

### Clinical Assessment Diagnostics V0

- Added repeatable diagnostics for the live validation25 clinical-assessment
  smoke:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_diagnostics.py`;
  - `tests/test_gan2026_clinical_assessment_diagnostics.py`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v0_diagnostics.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v0_diagnostics.json`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v0_diagnostics.md`.
- Diagnostic scope:
  - role usage;
  - invalid candidate references;
  - candidate ids used in multiple roles;
  - duplicate/corroborating candidates placed in primary roles;
  - historical, seizure-free, or cluster context leaking into frequency burden
    operands;
  - comparison against the minimal v2 selector and the richer v0 selector on the
    same rows.
- Summary:
  - rows: 25;
  - clinical assessment rows: 25;
  - missing assessment rows: 0;
  - invalid reference rows: 0;
  - role overlap rows: 0;
  - rows with diagnostic flags: 9.
- Assessment kinds:
  - 21 `frequency_rate`;
  - 2 `cluster_frequency`;
  - 2 `unknown_frequency`.
- Aggregation policies:
  - 15 `single_fact`;
  - 10 `primary_with_context`;
  - 0 `additive_same_window`;
  - 0 `cluster_axis`.
- Primary candidate count distribution:
  - one primary candidate: 17;
  - two primary candidates: 6;
  - three primary candidates: 1;
  - four primary candidates: 1.
- Diagnostic flags:
  - `multi_primary_nonadditive_policy`: 8;
  - `single_fact_multiple_primary_candidates`: 5;
  - `cluster_context_leak_in_frequency_burden`: 1;
  - `historical_context_phrase_in_burden`: 1;
  - `seizure_free_context_leak_in_frequency_burden`: 1.
- Selector comparison:
  - minimal v2 relation to assessment primary ids: 11 same, 8 assessment
    supersets, 2 assessment subsets, 4 different;
  - rich v0 relation to assessment primary ids: 11 same, 8 assessment
    supersets, 1 assessment subset, 5 different.
- Interpretation:
  - schema mechanics are strong: no call failures, parse failures, invalid
    references, or role overlaps;
  - the merged assessment contract materially improves the earlier grouped-row
    failure mode by giving the model primary/supporting/rejected roles;
  - the dominant issue is primary-role inflation, where duplicate deterministic
    and LLM candidates that express the same fact are both marked primary under
    `single_fact` or `primary_with_context`;
  - this is mostly an attribution/provenance problem, not necessarily a wrong
    clinical assessment, but it will complicate deterministic projection unless
    fixed;
  - two stronger prompt/schema issues remain:
    - row 198 uses seizure-free duration fields to carry last-event context;
    - row 409 leaks historical cluster context into current frequency burden
      operands;
  - v0 should be revised before validation50/validation250. The likely next
    revision is to clarify that primary ids should be the minimal evidence set
    needed for the assessment, while corroborating duplicate candidates belong
    in supporting ids, and to separate last-event/context timing from
    seizure-free duration fields.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_diagnostics.py -q`
  passed with 3 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_diagnostics.py tests/test_gan2026_clinical_assessment_diagnostics.py`
  passed.

### CandidateSet Nested Evidence Dedupe V3

- Added deterministic nested-evidence dedupe to
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/candidate_set_union.py`.
- Policy:
  - exact normalized duplicate candidates are still merged first;
  - same-kind, same-event candidates with nested spans are merged;
  - same-kind, same-event candidates with overlapping spans and contained
    evidence text are merged;
  - the retained candidate is the most detailed evidence span;
  - far-apart repeated references to the same burden are not merged
    deterministically and remain available as model-facing corroboration.
- Added tests in `tests/test_gan2026_candidate_set_union.py` for:
  - preserving the fuller phrase over a terse nested phrase;
  - merging overlapping contained evidence text;
  - merging one broad candidate against multiple retained nested fragments;
  - preserving separate mentions.
- Generated:
  - `experiments/gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`;
  - `experiments/gan2026_validation250_candidate_set_v3_nested_dedupe.json`;
  - `experiments/gan2026_validation250_candidate_set_v3_nested_dedupe.md`;
  - `experiments/gan2026_validation250_candidate_set_v3_nested_dedupe_diagnostics.jsonl`;
  - `experiments/gan2026_validation250_candidate_set_v3_nested_dedupe_diagnostics.json`;
  - `experiments/gan2026_validation250_candidate_set_v3_nested_dedupe_diagnostics.md`.
- Summary versus v2 high-recall union:
  - total candidates: 735 -> 514;
  - nested duplicate merges: 221;
  - changed rows: 154;
  - compatible-kind coverage remains 235/250 (0.940);
  - rows with no candidates remain 3;
  - diagnostic issue rows remain 12.
- Representative behavior:
  - `9 per month` merges into the fuller `Current average frequency is 9 per
    month`;
  - `every four months` merges into the fuller sentence-level current-burden
    statement;
  - multiple nested `every 2 days` fragments collapse into the fuller
    sentence-level burden statement;
  - repeated same-burden mentions in different note locations are preserved
    for the clinical-assessment model to treat as supporting corroboration.
- Updated the clinical-assessment prompt examples to state that repeated
  references to the same current burden should use the most specific
  source-near candidate as primary and put corroborating repeats in
  `supporting_candidate_ids` unless they clearly describe additional
  non-overlapping events.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_candidate_set_union.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py -q`
  passed with 11 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/candidate_set_union.py src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_candidate_set_union.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py`
  passed.

### Clinical Assessment V3-Nested Validation25

- Added a shared CLI `--candidate-set-jsonl` option for CandidateSet-backed
  probes and wired it through the clinical-assessment probe.
- Prompt-only validation25 against v3 nested-dedupe candidates succeeded with
  25/25 rows finding CandidateSets:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_prompt_only_validation25_v3nested_v0.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_prompt_only_validation25_v3nested_v0.md`.
- Live validation25 v3nested v0 artifacts:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v3nested_v0.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v3nested_v0.md`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v0_diagnostics.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v0_diagnostics.json`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v0_diagnostics.md`.
- v3nested v0 summary:
  - clinical assessment rows: 25/25;
  - call failures: 0;
  - parse/validation failures: 0;
  - diagnostic flag rows: 1;
  - primary candidate count distribution: 24 rows with one primary, 1 row
    with two primaries;
  - remaining flag: row 409 historical/cluster context leaked into current
    frequency burden phrase.
- Revised prompt to v1:
  - bumped `PROMPT_VERSION` to
    `gan2026_candidate_set_clinical_assessment_probe_v1`;
  - added an explicit instruction that normalized burden fields and
    `source_normalized_phrase` should describe only the current primary
    burden;
  - added a general historical-comparison example showing that prior burden
    belongs in supporting context or summary, not normalized burden operands.
- Live validation25 v3nested v1 artifacts:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v3nested_v1.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v3nested_v1.md`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v1_diagnostics.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v1_diagnostics.json`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v1_diagnostics.md`.
- v3nested v1 summary:
  - clinical assessment rows: 25/25;
  - call failures: 0;
  - parse/validation failures: 0;
  - invalid reference rows: 0;
  - role overlap rows: 0;
  - diagnostic flag rows: 0;
  - primary candidate count distribution: 25 rows with one primary;
  - assessment kinds: 23 `frequency_rate`, 2 `cluster_frequency`;
  - aggregation policies: 18 `single_fact`, 6 `primary_with_context`,
    1 `cluster_axis`.
- Diagnostic correction:
  - adjusted `clinical_assessment_diagnostics.py` so `cluster_axis` does not
    require multiple primary candidate ids when one cluster candidate supplies
    multiple normalized axes, such as cluster cadence plus cluster duration.
- Interpretation:
  - deterministic nested dedupe plus explicit corroboration guidance resolves
    the earlier primary-role inflation pattern on validation25;
  - the historical-comparison prompt revision resolves the remaining context
    leak observed in row 409;
  - v3nested v1 is now the best candidate middle-stage design to promote to
    validation50.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_llm_pipeline_cli.py tests/test_gan2026_clinical_assessment_diagnostics.py -q`
  passed with 15 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/llm_pipeline_cli.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_diagnostics.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_llm_pipeline_cli.py tests/test_gan2026_clinical_assessment_diagnostics.py`
  passed.

### Clinical Assessment V3-Nested Validation50

- Live validation50 v3nested v1 artifacts:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_gpt41mini_v3nested_v1.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_gpt41mini_v3nested_v1.md`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v1_diagnostics.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v1_diagnostics.json`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v1_diagnostics.md`.
- v3nested v1 validation50 summary:
  - clinical assessment rows: 50/50;
  - call failures: 0;
  - parse/validation failures: 0;
  - invalid reference rows: 0;
  - role overlap rows: 0;
  - diagnostic flag rows: 4.
- v1 validation50 diagnostic flags:
  - row 678: historical cluster candidate used as primary;
  - row 731: cluster context leaked into frequency burden fields;
  - row 744: multiple primary candidates under `primary_with_context`;
  - row 1165: duplicate/corroborating cluster/frequency facts both primary
    under `single_fact`, and later seizure-free interval leaked into normalized
    burden fields.
- Revised prompt to v2:
  - bumped `PROMPT_VERSION` to
    `gan2026_candidate_set_clinical_assessment_probe_v2`;
  - made `single_fact` exactly one primary candidate;
  - made `primary_with_context` use one current burden-defining primary
    candidate, with non-additive context in support;
  - stated that multiple additive primary facts should use
    `additive_same_window`, not `primary_with_context`;
  - prohibited historical candidates as primary when current/recent candidates
    are available;
  - prohibited cluster fields in `frequency_rate` assessments and
    seizure-free duration fields in non-`seizure_free` assessments;
  - added general examples for primary-with-context, historical/current burden
    separation, and later seizure-free interval context.
- Diagnostic expansion:
  - added `seizure_free_context_leak_in_cluster_burden`;
  - retained the corrected cluster-axis single-primary allowance when one
    source candidate provides multiple cluster axes.
- Live validation50 v3nested v2 artifacts:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_gpt41mini_v3nested_v2.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_gpt41mini_v3nested_v2.md`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v2_diagnostics.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v2_diagnostics.json`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v2_diagnostics.md`.
- v3nested v2 validation50 summary:
  - clinical assessment rows: 50/50;
  - call failures: 0;
  - parse/validation failures: 0;
  - invalid reference rows: 0;
  - role overlap rows: 0;
  - diagnostic flag rows: 0;
  - primary candidate count distribution: 49 rows with one primary, 1 row
    with two primaries;
  - assessment kinds: 43 `frequency_rate`, 5 `cluster_frequency`,
    2 `unknown_frequency`;
  - aggregation policies: 40 `single_fact`, 9 `primary_with_context`,
    1 `cluster_axis`.
- Interpretation:
  - validation50 supports the merged clinical-assessment design with v3
    nested-dedupe CandidateSets and the v2 prompt;
  - the remaining one multi-primary row is a permitted cluster-axis case, not
    a role inflation failure;
  - a future deterministic guard could exclude or demote `historical`
    candidates before assessment when current/recent frequency candidates are
    available, with additional logic for edge cases such as historical-only
    notes, relapse context, and seizure-free boundaries;
  - the current prompt-only handling is acceptable for now because v3nested v2
    validation50 diagnostics are clean. Revisit the deterministic guard only
    if validation250 or later projection work shows recurrent historical
    primary selection;
  - validation250 is the next reasonable promotion step, but it should be run
    intentionally as a broader validation-ladder step and followed by the same
    diagnostics before deterministic projection/rendering.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_clinical_assessment_diagnostics.py -q`
  passed with 10 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_diagnostics.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_clinical_assessment_diagnostics.py`
  passed.

### Clinical Assessment V3-Nested Validation250 Close-Out

- Live validation250 v3nested v2 artifacts:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_gpt41mini_v3nested_v2.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_gpt41mini_v3nested_v2.md`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_v3nested_v2_diagnostics.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_v3nested_v2_diagnostics.json`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_v3nested_v2_diagnostics.md`.
- v3nested v2 validation250 summary:
  - rows: 250;
  - clinical assessment rows: 247/250;
  - call failures: 0;
  - parse/validation failure rows: 3;
  - missing candidate-set rows: 0;
  - assessment kinds: 167 `frequency_rate`, 22 `cluster_frequency`, 41
    `seizure_free`, and 17 `unknown_frequency`;
  - aggregation policies: 185 `single_fact`, 41 `primary_with_context`, 14
    `seizure_free_state`, 3 `additive_same_window`, 2 `cluster_axis`, 1
    `no_reference_boundary`, and 1 `unknown_due_to_absence`.
- Diagnostic correction:
  - updated `clinical_assessment_diagnostics.py` so the report claim boundary
    reflects the actual row count rather than the old validation25 wording;
  - narrowed `historical_primary_candidate` so seizure-free "since date" or
    "no events since referral" assessments are not flagged merely because the
    extractor labeled the only available seizure-free candidate as
    `historical`;
  - after this correction, true flagged rows reduced from 8 to 5:
    744, 1363, 3469, 3532, and 5567.
- Remaining v2 diagnostic flags:
  - row 744: `additive_policy_non_frequency_primary`;
  - rows 1363, 3532, and 5567: `assessment_missing` after otherwise
    successful model calls because of role overlap, empty primary ids for a
    `frequency_rate` assessment, or an invented rejected candidate id;
  - row 3469: `seizure_free_context_leak_in_cluster_burden`.
- Revised prompt to v3:
  - bumped `PROMPT_VERSION` to
    `gan2026_candidate_set_clinical_assessment_probe_v3`;
  - explicitly prohibited invented candidate ids and candidate ids appearing
    in more than one role;
  - limited `additive_same_window` to concrete `frequency_rate` primary
    candidates;
  - instructed no-primary cases to return `unknown_frequency` /
    `unknown_due_to_absence` or `no_reference` / `no_reference_boundary`,
    not `frequency_rate` with empty primary ids;
  - added recurring-risk-window guidance so seizure-free outside-window context
    is not copied into non-`seizure_free` normalized burden fields;
  - added examples for vague frequency plus isolated concrete event, no usable
    primary candidate, and seizure-free outside a pattern window.
- Targeted v3 repair check on the 5 true flagged validation250 rows:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_flagged5_gpt41mini_v3nested_v3.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_flagged5_gpt41mini_v3nested_v3.md`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_flagged5_v3nested_v3_diagnostics.jsonl`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_flagged5_v3nested_v3_diagnostics.json`;
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_flagged5_v3nested_v3_diagnostics.md`.
- Targeted v3 flagged-row summary:
  - rows: 5;
  - clinical assessment rows: 5/5;
  - call failures: 0;
  - parse/validation failure rows: 0;
  - invalid reference rows: 0;
  - role overlap rows: 0;
  - diagnostic flag rows: 0.
- Interpretation:
  - validation250 supports the merged `ClinicalAssessment` middle-stage design:
    the v2 prompt completed 247/250 assessments without call failures, and the
    remaining true diagnostic failures were narrow prompt-contract failures;
  - the corrected diagnostics preserve the distinction between actionable
    historical-primary mistakes and acceptable seizure-free "since date"
    evidence whose source candidate was labeled historical upstream;
  - targeted v3 replay resolved all five true flagged rows, so the phase can
    close for architecture-review purposes without claiming a full v3
    validation250 run;
  - before deterministic projection/rendering, treat v3 as the active
    clinical-assessment prompt, but carry forward that full-validation250 clean
    diagnostics exist for v2 only after diagnostic correction plus targeted v3
    repair, not as a full v3 validation250 promotion claim.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_clinical_assessment_diagnostics.py -q`
  passed with 12 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_diagnostics.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_clinical_assessment_diagnostics.py`
  passed.

### Current Resume Point

The v3nested validation250 clinical-assessment phase is now closed for
architecture-review purposes. The next session should resume at the
post-assessment architecture decision: whether to build deterministic
projection/rendering from the `ClinicalAssessment` object, add a narrow
last-event/context timing field first, or run a full v3 validation250 replay if
promotion-grade prompt evidence is required.
The source-near candidate contract, deterministic/LLM candidate-set replay,
high-recall extract variant, union artifact, `SelectedCandidateDecision` contract,
selector schema probe, and related-group policy diagnostics are now
implemented. A merged `ClinicalAssessment` probe now exists as a competing
middle-stage design.

Start next session with:

1. Decide whether `ClinicalAssessment` needs a narrow last-event/context timing
   field before projection/rendering, especially for rows where later
   seizure-free intervals or last-event context should not be represented as
   seizure-free duration operands.
2. If projection/rendering begins, use v3nested CandidateSets and the active
   v3 clinical-assessment contract, and keep projection deterministic and
   policy-versioned.
3. Do not claim a full v3 validation250 promotion unless a future full v3
   validation250 replay is run and diagnosed.
4. Keep the current validation250 conclusion scoped to mechanics: the
   assessment contract is viable enough to close Phase 3 diagnostics and move
   to projection design, not to benchmark-comparable scoring.

Do not draw selector-quality conclusions from
`experiments/gan2026_validation250_selected_fact_v0_v2_high_recall.jsonl`
without carrying the prompt-language caveat forward.

Do not resume with:

- locked-test row-level work;
- benchmark-comparable claims;
- score-first tuning;
- scorer-facing labels from LLM extraction;
- further changes to frozen legacy components before disposition review.

### Deterministic Clinical-Assessment Normalization V0

- Decision at the post-assessment architecture gate: begin with deterministic
  normalization of the active `ClinicalAssessment` contract before building
  projection/rendering.
- Added `normalization_policy_id` and `normalization_issues` to
  `ClinicalAssessment`.
- Updated clinical-assessment assembly so parser-like burden operands are
  filled by `gan2026_clinical_assessment_normalization_v0`, not trusted from
  model output.
- Current deterministic normalization coverage is intentionally conservative:
  exact/range frequency rates, additive same-window frequency arithmetic when
  periods match, simple interval phrasing, cluster cadence, events per cluster,
  cluster duration fragments, seizure-free durations, and unknown/no-reference
  source-near pass-through.
- Parse misses are preserved as normalization issues rather than converted into
  false precision.
- Prompt contract language now asks the model for source-near burden phrasing
  and candidate roles, while deterministic assembly owns counts, ranges,
  periods, intervals, durations, and cluster operands.
- Focused verification passed for the clinical-assessment probe and diagnostics
  tests, plus ruff on the touched files.

Next resume point:

1. Run deterministic-normalization diagnostics on saved validation250 clinical
   assessment artifacts before starting deterministic projection/rendering.
2. Inspect normalization issue families on validation250 and decide whether to
   extend V0 parsing or keep them as verifier/projection abstention inputs.
3. Only then start a deterministic, policy-versioned projection from normalized
   `ClinicalAssessment`; do not claim benchmark-comparable scoring from this
   mechanics step.

### ClinicalAssessment Projection/Render Mechanics V0

- Implemented the first deterministic project/render mechanics layer from saved
  `ClinicalAssessment` rows.
- Added schema contracts:
  - `ProjectionDecision`;
  - `FinalRenderedLabel`.
- Policy ids:
  - `gan2026_clinical_assessment_projection_v0`;
  - `gan2026_final_label_renderer_v0`.
- The mechanics artifact emits both a structured projection decision and a
  nullable scorer-facing rendered label in one row.
- Scoring is explicitly disabled in the artifact.
- Saved validation250 source inputs:
  - `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_gpt41mini_v3nested_v2.jsonl`;
  - `experiments/gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`.
- Generated:
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v0.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v0.json`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v0.md`.
- V0 mechanics summary:
  - rows: 250;
  - projection rows: 247;
  - rendered-label rows: 130;
  - null rendered-label rows: 117;
  - row issue rows: 3.
- Projection kind counts:
  - `frequency_rate`: 167;
  - `cluster_frequency`: 22;
  - `seizure_free`: 41;
  - `unknown_frequency`: 17.
- Policy decisions implemented:
  - unknown-frequency assessments remain a richer internal projection state and
    render to final label `unknown`;
  - no-reference assessments render to `no seizure frequency reference`;
  - seizure-free assessments render only when a duration is parsed; otherwise
    rendered label is null with issue flags;
  - cluster cadence without events-per-cluster renders as a simple rate with
    projection basis `cluster_cadence_without_size`;
  - incomplete or unparsed operands stay null rather than becoming false
    precision.
- Current issue families are expected V0 mechanics outputs, not scoring
  failures. They should guide the next normalization/projection policy review.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py -q`
  passed with 13 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_projection_render.py`
  passed.

Next resume point after projection/render V0:

1. Inspect the 117 null rendered-label rows by issue family before extending
   projection policy.
2. Decide whether V0 should add more deterministic normalization coverage for
   frequent rate phrases, or whether specific issue families should route to
   verifier/human-review instead.
3. Keep score calculation disabled until the projection policy is reviewed as a
   mechanics artifact rather than tuned against validation labels.

### ClinicalAssessment Normalization Reuse Correction V1

- Corrected the deterministic-normalization implementation after review: do not
  grow a parallel source-phrase parser inside the clinical-assessment probe.
- The normalizer now reuses existing deterministic frequency parsing:
  `deterministic_extraction._extract_candidates(...)` supplies canonical
  `RawCandidate.label` values for selected source phrases.
- `prediction_label_from_selected_evidence(...)` remains only a fallback when
  the deterministic extractor emits no label.
- The reset-specific normalizer now only parses canonical Gan-compatible labels
  into `NormalizedBurden` operands; it no longer owns broad free-text parsing.
- Regenerated projection/render mechanics with the corrected implementation:
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v1.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v1.json`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v1.md`.
- V1 mechanics summary:
  - rows: 250;
  - projection rows: 247;
  - rendered-label rows: 198;
  - null rendered-label rows: 49;
  - row issue rows: 3.
- Change from V0:
  - rendered-label rows: 130 -> 198;
  - null rendered-label rows: 117 -> 49.
- Remaining null-label families are now more policy/verifier-shaped:
  - seizure-free since-date or visit-relative statements without numeric
    duration;
  - cluster descriptions without renderable cadence/per-cluster operands;
  - additive vague-plus-concrete mixed-window assessments;
  - known saved v2 assessment-contract failures.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_clinical_assessment_projection_render.py -q`
  passed with 17 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py`
  passed.

Next resume point after V1:

1. Treat V1 as the active mechanics artifact.
2. Inspect the 49 null rendered-label rows before adding any more render policy.
3. Decide explicitly whether since-date seizure-free statements should be
   normalized by date arithmetic, routed to verifier, or left null in this
   mechanics layer.
4. Keep scoring disabled.

### ClinicalAssessment Projection Score Policy V0

- Implemented a separate score-policy artifact over the active V1
  project/render mechanics output.
- Added `RenderedLabelScore` to the projection/render contract family with:
  - schema id `gan2026_rendered_label_scoring_v0`;
  - policy id `gan2026_rendered_label_scoring_policy_v0`.
- The scorer reuses existing Gan scoring surfaces rather than adding a new
  scorer:
  - `label_to_frequency_record(...)` parses and normalizes rendered labels;
  - `GanFrequencyRecord` supplies gold normalized labels and monthly
    frequencies from the existing split loader;
  - `map_purist(...)` and `map_pragmatic(...)` provide the existing category
    comparisons.
- Null rendered labels are explicitly `not_scored_null_rendered_label`, not
  counted as wrong by the scoring policy.
- Unparseable rendered labels are explicitly
  `not_scored_unparseable_rendered_label`, preserving parse failures as score
  issues rather than silently coercing them.
- Generated:
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v0.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v0.json`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v0.md`.
- V0 score-policy summary over the V1 mechanics artifact:
  - rows: 250;
  - scored rows: 198;
  - non-scored rows: 52;
  - non-scored issue counts: 52 `rendered_label_null`;
  - exact normalized-label matches on scored rows: 173/198 (0.8737);
  - purist-correct rows on scored rows: 188/198 (0.9495);
  - pragmatic-correct rows on scored rows: 193/198 (0.9747).
- Claim boundary:
  - this is validation250 mechanics scoring over saved project/render rows only;
  - it is not a benchmark-comparable promotion claim;
  - it does not authorize score-first tuning or locked-test row-level work.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_projection_score.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py -q`
  passed with 21 tests.

Next resume point after scoring V0:

1. Inspect the 52 non-scored rows by projection/render issue family.
2. Inspect the 10 purist-wrong scored rows before changing projection policy.
3. Keep the scorer fixed while deciding whether errors belong to assessment,
   normalization, projection, render, or verifier routing.
4. Do not tune projection/render rules directly against score without a named
   mechanics failure family and artifact evidence.

### Verification Route V0

- Agreed verification boundaries:
  - verification starts only after a structurally valid clinical assessment
    exists;
  - verifier routes are issue/risk-family driven, not score-outcome driven;
  - null rendered labels are symptoms, not automatic verifier routes;
  - date arithmetic for seizure-free since-date statements belongs to
    deterministic normalization/projection, while seizure-free conflict belongs
    to verification;
  - clear cluster operands belong to projection, while cluster-axis ambiguity
    belongs to verification;
  - same-window concrete addition belongs to projection, while mixed-window,
    vague, or scope-uncertain addition belongs to verification or abstention;
  - verifier rejection blocks a projected/rendered outcome but does not invent
    a replacement scorer-facing label;
  - comparator preservation is a separately named action policy, not hidden
    verifier or projection behavior.
- Added glossary terms to `CONTEXT.md` for verification decisions, routes,
  verifier actions, null rendered labels, seizure-free date arithmetic,
  seizure-free conflict, cluster-axis ambiguity, same-window additive
  frequency, verifier rejection, comparator preservation action, route-report
  boundaries, and route score-context boundaries.
- Implemented deterministic route contract and report builder:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/verification_route.py`;
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_verification_route.py`.
- Route V0 consumes the GPT-4.1 mini validation250 scoring artifact because it
  already embeds projection/render objects. Route predicates use only
  structured clinical/projection/render fields and issue names; score fields
  are audit context only.
- Generated:
  - `experiments/gan2026_validation250_verification_route_v0.jsonl`;
  - `experiments/gan2026_validation250_verification_route_v0.json`;
  - `experiments/gan2026_validation250_verification_route_v0.md`.
- V0 route summary:
  - rows: 250;
  - routed rows: 13;
  - unrouted rows: 237;
  - route family counts: 11 `cluster_axis_ambiguity`, 1
    `mixed_window_or_vague_addition`, and 1 `multiple_current_primary_facts`;
  - routed score statuses: 12 `not_scored_null_rendered_label`, 1 `scored`;
  - routed rows: 338, 744, 1317, 1573, 1707, 3468, 3469, 3493, 3534, 4173,
    4480, 5476, and 5551.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_projection_score.py tests/test_gan2026_clinical_assessment_projection_render.py -q`
  passed with 16 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/verification_route.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_verification_route.py`
  passed.

Next resume point after route V0:

1. Inspect the 13 routed rows manually using the route report and decide which
   families should receive an LLM verifier prompt versus deterministic
   abstention or projection-policy refinement.
2. Do not use the 10 purist-wrong rows as route triggers unless a wrong row
   also maps to a predeclared route family.
3. If comparator-preservation is needed, define it as a separate action-policy
   artifact with its own policy id rather than adding it to route V0.

### Concrete Frequency Precedence And Vague Frequency Projection V1

- After row-by-row inspection of the 13 routed rows, implemented a targeted
  deterministic normalization correction:
  - cluster-framed clinical assessments may be promoted to `frequency_rate`
    when a selected or supporting candidate contains renderable concrete
    frequency burden;
  - policy-approved vague frequency phrases such as "many convulsions in past
    month", "multiple days within the past week", "most weekdays", and
    "several episodes per day" now normalize through the shared
    `selected_evidence` parser to `multiple per month`, `multiple per week`, or
    `multiple per day`;
  - promotion is blocked when the existing cluster burden is already renderable,
    preserving true cluster labels such as `2 cluster per month, 4 per cluster`;
  - medication cadence such as patient-led/as-needed clobazam use is not treated
    as seizure frequency.
- Added `Concrete Frequency Precedence` to `CONTEXT.md`.
- Added regression coverage for:
  - concrete frequency beating contextual cluster framing;
  - supporting deterministic frequency beating an unrenderable cluster primary;
  - shared selected-evidence vague frequency parsing;
  - vague multiple-days-in-week normalization;
  - cluster `events_per_cluster` phrases such as "several episodes per day";
  - preserving already-renderable cluster burden;
  - blocking medication-cadence promotion.
- Generated updated artifacts:
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v2.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v2.json`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v2.md`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v1.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v1.json`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v1.md`;
  - `experiments/gan2026_validation250_verification_route_v1.jsonl`;
  - `experiments/gan2026_validation250_verification_route_v1.json`;
  - `experiments/gan2026_validation250_verification_route_v1.md`.
- Projection/render change versus V1:
  - rendered-label rows: 198 -> 204;
  - null rendered-label rows: 49 -> 43;
  - cluster-to-frequency promotions: 6.
- Score-policy change versus V0:
  - scored rows: 198 -> 204;
  - non-scored rows: 52 -> 46;
  - exact normalized-label matches: 173 -> 179;
  - purist-correct scored rows: 188 -> 194;
  - pragmatic-correct scored rows: 193 -> 199.
- Routed-row effects:
  - row 338: null -> `multiple per month`, purist-correct;
  - row 1573: null -> `11 per week`, purist-correct;
  - row 1707: null -> `multiple per week`, purist-correct;
  - row 4173: null -> `1 per 2 week`, purist-correct;
  - row 4480: null -> `3 to 5 per week`, purist-correct;
  - row 5551: null -> `multiple per day`, purist-correct;
  - rows 3261 and 3643 remained correct after narrowing the override to avoid
    renderable-cluster regressions;
  - row 5476 remains null because monthly clobazam use is medication cadence,
    not seizure frequency.
- Verification-route V1 summary:
  - routed rows: 7;
  - route families: 5 `cluster_axis_ambiguity`, 1
    `mixed_window_or_vague_addition`, and 1 `multiple_current_primary_facts`;
  - routed rows: 744, 1317, 3468, 3469, 3493, 3534, and 5476.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_projection_score.py tests/test_gan2026_clinical_assessment_verification_route.py -q`
  passed with 35 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py`
  passed.

Next resume point after concrete-frequency precedence:

1. Inspect the remaining 7 routed rows under route V1.
2. Decide whether row 1317 needs an explicit `unknown cadence, multiple per
   cluster` projection policy or should remain verifier/human-review.
3. Keep row 744 as mixed-window/vague addition unless a named policy is added
   to prefer the dominant vague weekly burden over a low-frequency GTC context.
4. Treat row 5476 as medication-cadence ambiguity, not a projection target.

### Scoring And Projection Ownership Audit

- Applied the same "are we reinventing the wheel?" lens to projection/render
  and scoring after the parser/normalizer review.
- Scoring is mostly correctly reused and attributed:
  - `clinical_assessment_projection_score.py` uses the canonical Gan label
    parser (`label_to_frequency_record`) and the existing purist/pragmatic
    category mappers (`map_purist`, `map_pragmatic`);
  - null or unparseable rendered labels are explicitly non-scored, rather than
    silently repaired inside scoring;
  - the scoring artifact is labelled as score policy and does not claim
    benchmark-comparable promotion.
- Projection/render is the area with real custom policy surface:
  - `clinical_assessment_projection_render.py` hand-renders rate, cluster,
    seizure-free, unknown, and no-reference states from `NormalizedBurden`;
  - this is legitimate glue for the new `ClinicalAssessment` object, but the
    local helpers overlap with already developed Gan parser, scorer-facing
    repair, benchmark-renderer, and projection-owner components;
  - the broad `final_label_renderer` owner name is easy to misread as the
    shared benchmark renderer, even though the implementation currently renders
    only ClinicalAssessment burden fields.
- Existing reusable surfaces:
  - scorer semantics: `contract/label_parser.py` and `labels.py`;
  - scorer-facing label repair: `normalize.py` and
    `contract/benchmark_prediction_repair.py`;
  - selected-evidence label projection: `selected_evidence/final_label_projection.py`;
  - benchmark-only rendering with frozen clinical state:
    `components/benchmark_renderer_fixture.py`;
  - explicit projection-owner taxonomy:
    `components/structured_seed_projection_generator.py` and
    `components/structured_validation_projection_panel.py`.
- Attribution questions:
  - Rate labels generated from typed `count/period` operands should be
    attributed to `rate_projection_policy`, not a generic final renderer.
  - Cluster labels generated from typed cluster cadence and per-cluster burden
    should be attributed to `cluster_projection_policy`.
  - Unknown/no-reference sentinels and Gan-specific cluster sentinels should be
    attributed to `benchmark_renderer` only when clinical state is preserved.
  - Seizure-free boundary changes should remain boundary projection policy,
    not renderer policy.
- Policy questions:
  - The cluster fallback `cluster cadence without size -> simple rate` is a
    substantive projection policy. It should stay only if we are comfortable
    treating cluster cadence as a scorer-facing seizure cadence when
    within-cluster load is missing; otherwise it should render null and route to
    verification.
  - `unknown cadence, multiple per cluster` for row 1317 is not a formatting
    issue. It requires a named cluster projection policy if we choose to emit
    the Gan sentinel.
  - Scorer-facing repair should be used as render-boundary validation/cleanup,
    not as hidden clinical projection. It repairs labels; it should not choose
    the clinical fact.
  - Score policy should continue to parse and compare labels, not rescue
    projection failures.
- Recommended next implementation step:
  - extract shared render primitives from the ClinicalAssessment projection
    helpers, returning both label and `projection_owner`/rule id;
  - validate rendered labels with canonical parser or clean scorer-facing
    repair where appropriate;
  - update artifacts so projection owner distinguishes rate, cluster, boundary,
    and benchmark-only renderer decisions.

### Projection Ownership Split Decision

- Decision: split projection ownership now instead of keeping the broad
  `clinical_assessment_projection` / `final_label_renderer` attribution as the
  conceptual owner.
- Rationale:
  - the current owner names obscure whether a scorer-facing label came from a
    rate policy, cluster policy, boundary policy, or benchmark-only rendering;
  - the split is a schema/provenance correction, not score tuning;
  - row-specific policy decisions such as cluster fallback, unknown-cadence
    cluster sentinels, mixed-window addition, and medication-cadence ambiguity
    should be made only after ownership is explicit.
- Implementation implication:
  - the projection/render artifact may remain the orchestration wrapper, but
    each emitted projection/render decision must carry a specific
    `projection_owner` and rule/policy id.
- Deprecated as conceptual owners:
  - `clinical_assessment_projection`;
  - `final_label_renderer`.
- Canonical conceptual owners for the next implementation pass:
  - `rate_projection_policy`;
  - `cluster_projection_policy`;
  - `boundary_projection_policy`;
  - `benchmark_renderer`.
- Projection/render boundary decision:
  - when a `cluster_frequency` assessment has cluster cadence but lacks
    events-per-cluster burden, emitting a simple rate label is owned by
    `cluster_projection_policy`, not `benchmark_renderer`;
  - rationale: treating cluster cadence as scorer-facing seizure cadence changes
    the benchmark-facing interpretation of an incomplete cluster state. It is a
    substantive projection policy, not label-formatting syntax.
- Cluster fallback policy decision:
  - keep `cluster_cadence_without_size -> simple rate` enabled, but rename and
    narrow it as an explicit cluster projection rule such as
    `cluster_cadence_as_event_rate_when_size_absent_v0`;
  - allowed only when cluster cadence is clear and current, events-per-cluster
    burden is absent rather than contradictory, and the evidence does not
    describe medication cadence or another non-event cadence;
  - block and route ambiguous cluster-axis cases instead of rendering;
  - emit `projection_owner = cluster_projection_policy` and the specific rule
    id on affected rows.
- Row 1317 / unknown-cadence cluster sentinel decision:
  - superseded by the later decision to deliberately allow unknown-cadence
    cluster burden under a named cluster projection policy;
  - original conservative note retained for audit context: the Gan sentinel is
    not formatting-only and must be owned by `cluster_projection_policy`, not
    `benchmark_renderer`.
- Row 744 / mixed-window vague addition decision:
  - do not add a deterministic policy to prefer a dominant vague weekly burden
    over lower-frequency GTC context in this pass;
  - keep row 744 routed as `mixed_window_or_vague_addition` with no
    scorer-facing projection label;
  - rationale: dominant vague burden selection would mix selector and
    projection responsibilities. Mixed-window, vague-plus-concrete, or
    event-scope-uncertain addition remains verifier or abstention territory.
- Row 5476 / medication-cadence ambiguity decision:
  - keep medication-cadence ambiguity blocked from projection;
  - refine the route family away from generic `cluster_axis_ambiguity` toward
    `medication_cadence_ambiguity` or `non_event_cadence_ambiguity`;
  - rationale: cadence evidence may describe clobazam/rescue-medication use
    rather than seizure or seizure-cluster occurrence. Projection must not turn
    medication cadence into seizure frequency.

### Projection Ownership Split Implementation V1

- Implemented owner-aware projection/render contracts:
  - schema version: `gan2026_projection_render_v1`;
  - projection policy id:
    `gan2026_clinical_assessment_projection_owner_split_v1`;
  - render policy id: `gan2026_projection_owner_aware_label_render_v1`.
- `ProjectionDecision` and `FinalRenderedLabel` now carry:
  - explicit `projection_owner`;
  - explicit `projection_rule_id`;
  - component owner aligned to the conceptual projection owner rather than the
    broad wrapper names.
- Owner mapping in the validation250 mechanics artifact:
  - `rate_projection_policy` owns frequency-rate operand projection;
  - `cluster_projection_policy` owns cluster cadence/per-cluster projection and
    the named cluster-cadence fallback;
  - `boundary_projection_policy` owns seizure-free duration projection and
    seizure-free duration-required nulls;
  - `benchmark_renderer` owns unknown-frequency sentinel rendering.
- Named cluster fallback rule:
  - `cluster_cadence_as_event_rate_when_size_absent_v0`;
  - rendered 6 validation250 rows, unchanged from V2 count, now explicitly
    attributed to `cluster_projection_policy`.
- Added deterministic `medication_cadence_ambiguity` projection issue when a
  selected cluster-cadence candidate is actually medication/rescue-use cadence.
- Added route family `medication_cadence_ambiguity`; route V2 now keeps row
  5476 blocked from projection and routes it under the specific medication
  cadence family rather than generic cluster-axis ambiguity.
- Generated:
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v3.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v3.json`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v3.md`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v2.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v2.json`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v2.md`;
  - `experiments/gan2026_validation250_verification_route_v2.jsonl`;
  - `experiments/gan2026_validation250_verification_route_v2.json`;
  - `experiments/gan2026_validation250_verification_route_v2.md`.
- Projection/render V3 summary:
  - rows: 250;
  - projection rows: 247;
  - rendered-label rows: 204;
  - null rendered-label rows: 43;
  - projection owner counts: 173 `rate_projection_policy`, 16
    `cluster_projection_policy`, 41 `boundary_projection_policy`, and 17
    `benchmark_renderer`;
  - new issue count: 1 `medication_cadence_ambiguity`.
- Score-policy V2 over projection/render V3:
  - scored rows: 204;
  - non-scored rows: 46;
  - exact normalized-label matches on scored rows: 179/204 (0.8775);
  - purist-correct scored rows: 194/204 (0.951);
  - pragmatic-correct scored rows: 199/204 (0.9755).
- Verification-route V2 summary:
  - routed rows: 7;
  - route family counts: 4 `cluster_axis_ambiguity`, 1
    `medication_cadence_ambiguity`, 1 `mixed_window_or_vague_addition`, and 1
    `multiple_current_primary_facts`;
  - routed rows: 744, 1317, 3468, 3469, 3493, 3534, and 5476.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_projection_score.py tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py -q`
  passed with 37 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/verification_route.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_verification_route.py`
  passed.

Next resume point after ownership split V1:

1. Inspect the remaining 4 `cluster_axis_ambiguity` rows under route V2:
   1317, 3468, 3469, and 3493.
2. Decide whether row 3534 should remain routed as
   `multiple_current_primary_facts` or receive a named selector/assessment
   refinement.
3. Keep score-policy V2 fixed while making any further mechanics decisions.

### Unknown-Cadence Cluster Burden Decision

- Decision: deliberately allow unknown-cadence cluster burden as a named cluster
  projection policy instead of leaving all such rows routed/null.
- Canonical term: `Unknown-Cadence Cluster Burden`.
- Ownership:
  - `cluster_projection_policy`, not `benchmark_renderer`;
  - the rule must have an explicit rule id before emitting a scorer-facing
    sentinel such as `unknown, multiple per cluster`.
- Initial motivating row:
  - row 1317, where the source supports multiple short episodes inside a
    single-day cluster but does not support recurrence cadence.

### Unknown-Cadence Cluster Burden Implementation V0

- Implemented cluster projection rule:
  `unknown_cadence_multiple_per_cluster_v0`.
- The rule emits scorer-facing label `unknown, multiple per cluster` only when:
  - the selected primary candidate is `cluster_frequency`;
  - event type is `seizure` or `seizure_like_event`;
  - source-near cluster details support vague multiple events per cluster;
  - normalized cluster cadence is absent;
  - the selected evidence is not medication/rescue-use cadence;
  - no competing renderable current frequency-rate candidate is present.
- Guardrail added after inspection:
  - row 1694 already has renderable typed cluster cadence and
    events-per-cluster operands, so it must remain
    `cluster_cadence_with_events_per_cluster_v0` rather than being converted to
    unknown-cadence sentinel.
- Generated:
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v4.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v4.json`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v4.md`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v3.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v3.json`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v3.md`;
  - `experiments/gan2026_validation250_verification_route_v3.jsonl`;
  - `experiments/gan2026_validation250_verification_route_v3.json`;
  - `experiments/gan2026_validation250_verification_route_v3.md`.
- Projection/render V4 effects versus V3:
  - rendered-label rows: 204 -> 205;
  - null rendered-label rows: 43 -> 42;
  - `unknown_cadence_multiple_per_cluster_v0`: 1 row;
  - `cluster_cadence_operands_required_v0`: 5 -> 4;
  - row 1317 now renders `unknown, multiple per cluster`.
- Score-policy V3 over projection/render V4:
  - scored rows: 205;
  - non-scored rows: 45;
  - exact normalized-label matches on scored rows: 180/205 (0.878);
  - purist-correct scored rows: 195/205 (0.9512);
  - pragmatic-correct scored rows: 200/205 (0.9756).
- Verification-route V3:
  - routed rows: 6;
  - route family counts: 3 `cluster_axis_ambiguity`, 1
    `medication_cadence_ambiguity`, 1 `mixed_window_or_vague_addition`, and 1
    `multiple_current_primary_facts`;
  - row 1317 is no longer routed because the named cluster projection policy
    resolved the unknown-cadence burden;
  - remaining `cluster_axis_ambiguity` rows are 3468, 3469, and 3493.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_projection_score.py tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py -q`
  passed with 41 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/verification_route.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_verification_route.py`
  passed.

Next resume point after unknown-cadence cluster rule:

1. Decide whether cyclic/perimenstrual vulnerability-window rows 3468, 3469,
   and 3493 should remain routed/null or receive a separate named policy.
2. Keep the unknown-cadence sentinel rule restricted to supported
   events-per-cluster burden; do not apply it to cyclic windows without event
   counts.

### Cyclic Vulnerability Window Decision

- Decision: keep cyclic/perimenstrual vulnerability-window rows routed/null for
  now rather than adding a projection policy.
- Canonical term: `Cyclic Vulnerability Window`.
- Motivating rows:
  - row 3468: seizures happen perimenstrually only, days -2 to +2;
  - row 3469: seizures happen perimenstrually only, days -3 to +3;
  - row 3493: seizure-like events cluster around menstrual period, roughly
    three days before to three days after.
- Rationale:
  - these statements identify a recurring vulnerability window, not the number
    of events within the window;
  - projecting them to a frequency would invent count/burden precision;
  - they must not use the unknown-cadence cluster sentinel because
    events-per-cluster burden is absent.

### Cyclic Window Route Split V0

- Implemented `cyclic_window_without_event_count` as a specific
  verification-route family.
- Projection/render now emits projection issue
  `cyclic_window_without_event_count` for cyclic/perimenstrual cluster-framed
  rows that lack event count or burden.
- Route priority:
  - `medication_cadence_ambiguity` first;
  - `cyclic_window_without_event_count` second;
  - generic `cluster_axis_ambiguity` only for unresolved cluster-axis gaps that
    do not match a more specific family.
- Generated:
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v5.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v5.json`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v5.md`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v4.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v4.json`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v4.md`;
  - `experiments/gan2026_validation250_verification_route_v4.jsonl`;
  - `experiments/gan2026_validation250_verification_route_v4.json`;
  - `experiments/gan2026_validation250_verification_route_v4.md`.
- Projection/render V5:
  - render counts unchanged from V4;
  - `cyclic_window_without_event_count`: 3 projection issue rows.
- Score-policy V4:
  - unchanged from V3: 205 scored rows and 45 non-scored rows.
- Verification-route V4:
  - routed rows: 6;
  - route family counts: 3 `cyclic_window_without_event_count`, 1
    `medication_cadence_ambiguity`, 1 `mixed_window_or_vague_addition`, and 1
    `multiple_current_primary_facts`;
  - generic `cluster_axis_ambiguity` count is now 0 on validation250 route V4.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_projection_score.py tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py -q`
  passed with 42 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/verification_route.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_verification_route.py`
  passed.

Next resume point after cyclic-window split:

1. Review row 744 `mixed_window_or_vague_addition`.
2. Review row 3534 `multiple_current_primary_facts`.
3. Review row 5476 `medication_cadence_ambiguity` only if we want a verifier
   action policy; projection remains blocked.

### Dominant Vague Current Burden Policy V0

- Decision: add a named policy for row 744 rather than keeping it routed/null.
- Canonical term: `Dominant Vague Current Burden`.
- Rule id: `dominant_vague_current_burden_v0`.
- Ownership:
  - `rate_projection_policy`;
  - not additive arithmetic and not benchmark-renderer formatting.
- Guardrails:
  - applies only to `frequency_rate` assessments with `additive_same_window`
    source policy;
  - candidate evidence must derive a vague high-frequency label such as
    `multiple per week` through the existing selected-evidence derivation
    surface;
  - lower-frequency contextual candidates must also derive parseable labels;
  - the vague label must mechanically dominate the lower-frequency context;
  - medication/rescue-use cadence is excluded;
  - selected/recent or current primary candidates only.
- Implementation detail:
  - selected-evidence derivation input now normalizes dash variants before
    parsing, so `tonic-clonic` and `tonic–clonic` evidence behave the same.
- Generated:
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v6.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v6.json`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v6.md`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v5.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v5.json`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v5.md`;
  - `experiments/gan2026_validation250_verification_route_v5.jsonl`;
  - `experiments/gan2026_validation250_verification_route_v5.json`;
  - `experiments/gan2026_validation250_verification_route_v5.md`.
- Projection/render V6 effects versus V5:
  - rendered-label rows: 205 -> 206;
  - null rendered-label rows: 42 -> 41;
  - `dominant_vague_current_burden_v0`: 1 row;
  - row 744 now renders `multiple per week`.
- Score-policy V5 over projection/render V6:
  - scored rows: 206;
  - non-scored rows: 44;
  - exact normalized-label matches on scored rows: 181/206 (0.8786);
  - purist-correct scored rows: 196/206 (0.9515);
  - pragmatic-correct scored rows: 201/206 (0.9757).
- Verification-route V5:
  - routed rows: 5;
  - route family counts: 3 `cyclic_window_without_event_count`, 1
    `medication_cadence_ambiguity`, and 1 `multiple_current_primary_facts`;
  - `mixed_window_or_vague_addition` count is now 0 on validation250 route V5.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_projection_score.py tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py -q`
  passed with 44 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/verification_route.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_verification_route.py`
  passed.

Next resume point after dominant vague burden policy:

1. Review row 3534 `multiple_current_primary_facts`.
2. Review row 5476 `medication_cadence_ambiguity` only if a verifier/action
   policy is needed; projection remains blocked.

### Seizure-Free Proxy Evidence Overreach Block V0

- Decision: block seizure-free projection when selected evidence is proxy-only
  improvement rather than explicit no-seizure/no-event evidence.
- Canonical term: `Seizure-Free Proxy Evidence Overreach`.
- Rule id: `seizure_free_proxy_evidence_block_v0`.
- Route family: `seizure_free_proxy_evidence_overreach`.
- Ownership:
  - `boundary_projection_policy`;
  - not renderer formatting and not score-triggered repair.
- Guardrails:
  - explicit no-seizure/no-event/seizure-free evidence may still render;
  - proxy-only evidence such as no rescue medication, no injury, no admission,
    better control, or conditional future breakthrough-event planning must not
    render a seizure-free duration;
  - unresolved selected source ids contribute to the overreach block when no
    explicit seizure-free evidence is present.
- Motivating row:
  - row 3534 previously rendered `seizure free for 7 month` from evidence about
    rescue medication/injuries/admissions not being required and conditional
    breakthrough-event planning; gold was `unknown`.
- Generated:
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v7.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v7.json`;
  - `experiments/gan2026_clinical_assessment_projection_render_validation250_v7.md`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v6.jsonl`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v6.json`;
  - `experiments/gan2026_clinical_assessment_projection_score_validation250_v6.md`;
  - `experiments/gan2026_validation250_verification_route_v6.jsonl`;
  - `experiments/gan2026_validation250_verification_route_v6.json`;
  - `experiments/gan2026_validation250_verification_route_v6.md`.
- Projection/render V7 effects versus V6:
  - rendered-label rows: 206 -> 205;
  - null rendered-label rows: 41 -> 42;
  - `seizure_free_proxy_evidence_block_v0`: 1 row;
  - `seizure_free_duration_projection_v0`: 17 -> 16;
  - row 3534 now renders null with issue
    `seizure_free_proxy_evidence_overreach`.
- Score-policy V6 over projection/render V7:
  - scored rows: 205;
  - non-scored rows: 45;
  - exact normalized-label matches on scored rows: 181/205 (0.8829);
  - purist-correct scored rows: 196/205 (0.9561);
  - pragmatic-correct scored rows: 201/205 (0.9805).
- Verification-route V6:
  - routed rows: 5;
  - route family counts: 3 `cyclic_window_without_event_count`, 1
    `medication_cadence_ambiguity`, and 1
    `seizure_free_proxy_evidence_overreach`;
  - `multiple_current_primary_facts` count is now 0 on validation250 route V6;
  - all routed rows are null-rendered risk families.
- Verification:
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m pytest tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_projection_score.py tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py -q`
  passed with 47 tests.
  `$env:PYTHONPATH='src'; .venv/Scripts/python.exe -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_projection_render.py src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/verification_route.py src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_verification_route.py`
  passed.

Next resume point after seizure-free proxy block:

1. Review row 5476 `medication_cadence_ambiguity` only if a verifier/action
   policy is needed; projection remains blocked.
2. Decide whether the remaining cyclic-window rows should simply stay routed
   until a verifier action layer exists.

### Current Resume Point For Next Session

Active mechanics artifacts:

- Projection/render:
  `experiments/gan2026_clinical_assessment_projection_render_validation250_v7.jsonl`
- Score-policy audit:
  `experiments/gan2026_clinical_assessment_projection_score_validation250_v6.jsonl`
- Verification-route report:
  `experiments/gan2026_validation250_verification_route_v6.jsonl`

Current route V6 state:

- routed rows: 5;
- all routed rows are null-rendered risk families;
- no scored wrong routed row remains;
- route families:
  - 3 `cyclic_window_without_event_count` rows: 3468, 3469, 3493;
  - 1 `seizure_free_proxy_evidence_overreach` row: 3534;
  - 1 `medication_cadence_ambiguity` row: 5476.

Resolved since the ownership split:

- row 1317 now renders `unknown, multiple per cluster` through
  `unknown_cadence_multiple_per_cluster_v0`;
- row 744 now renders `multiple per week` through
  `dominant_vague_current_burden_v0`;
- row 3534 no longer renders seizure-free and is blocked by
  `seizure_free_proxy_evidence_block_v0`;
- generic `cluster_axis_ambiguity`, `mixed_window_or_vague_addition`, and
  `multiple_current_primary_facts` are all at 0 on route V6.

Recommended next question:

- Should route V6 remain as a verifier/action backlog, or should any route
  family receive a deterministic action policy now?

Recommended answer:

- Keep projection blocked for all 5 routed rows.
- Do not add more projection rules until a separate verifier/action artifact is
  defined.
- If continuing implementation, define a `VerificationDecision`/action artifact
  over route V6 with actions such as `abstain`, `human_review`, or
  comparator-preservation policy. Do not make the verifier invent replacement
  scorer-facing labels.

### Route V6 Backlog Boundary Decision

- Decision: keep projection blocked for all 5 route V6 rows and treat route V6
  as input to a separate verifier/action artifact.
- Ownership:
  - route V6 remains a `Verification Route` report;
  - the next artifact should emit `VerificationDecision` objects and
    `Verifier Action` values;
  - no route family receives a new deterministic projection rule at this point.
- Guardrail:
  - verifier/action logic must not invent replacement scorer-facing labels;
  - any future comparator-preservation behavior must be a named action policy,
    not hidden verifier repair or projection behavior.
- Remaining route V6 families:
  - 3 `cyclic_window_without_event_count` rows: 3468, 3469, 3493;
  - 1 `seizure_free_proxy_evidence_overreach` row: 3534;
  - 1 `medication_cadence_ambiguity` row: 5476.

Next question:

- What are the allowed `Verifier Action` values for the first
  `VerificationDecision` artifact, and should V0 emit them deterministically
  from route family alone?

### VerificationDecision Action Set V0 Decision

- Decision: the first `VerificationDecision` artifact uses a deliberately small
  action set:
  - `abstain`;
  - `human_review`;
  - `affirm`;
  - `reject`.
- V0 mapping:
  - `cyclic_window_without_event_count` -> `abstain`;
  - `medication_cadence_ambiguity` -> `human_review`;
  - `seizure_free_proxy_evidence_overreach` -> `reject` only when attached to a
    proposed rendered outcome; otherwise `abstain`.
- Current route V6 mapping:
  - rows 3468, 3469, and 3493 -> `abstain`;
  - row 3534 -> `abstain` because route V6 already has a null rendered label
    rather than a proposed seizure-free rendered outcome;
  - row 5476 -> `human_review`.
- Guardrail:
  - `affirm` and `reject` remain schema-allowed for V0, but should only be used
    when there is an existing assessment, projection, render action, or proposed
    outcome to accept or block.

Next question:

- What minimal fields must a `VerificationDecision` V0 object include so future
  readers can distinguish route evidence, verifier action, score context, and
  any future comparator-preservation policy?

### VerificationDecision V0 And LLM Verifier Boundary

- Clarification: `VerificationDecision` V0 is not a replacement for the future
  LLM verifier.
- Decision: build deterministic `VerificationDecision` V0 first as the
  baseline action harness around route V6.
- Intended comparison:
  - `Verification Route` decides whether a row should enter verification;
  - deterministic `VerificationDecision` V0 supplies the safe default action
    from route family and existing projection/render state;
  - a future LLM verifier may be evaluated as a routed component that can
    safely affirm, reject, abstain, or request human review with evidence.
- Guardrail:
  - the future LLM verifier must be compared against the deterministic V0
    action baseline;
  - it must not invent replacement scorer-facing labels or bypass projection
    ownership.

### VerificationDecision V0 Schema Decision

- Decision: `VerificationDecision` V0 is the minimal deterministic baseline
  action object for rows already selected by `Verification Route`.
- Required fields:
  - `source_row_index`;
  - `component_owner`: `verification_decision`;
  - `schema_version`;
  - `verification_policy_id`;
  - `source_route_policy_id`;
  - `route_families`;
  - `route_reasons`;
  - `action`: `abstain`, `human_review`, `affirm`, or `reject`;
  - `action_reason`;
  - `action_basis`;
  - `proposed_rendered_label`;
  - `final_rendered_label`;
  - `score_context`;
  - `claim_boundary`.
- V0 boundaries:
  - `score_context` is audit-only and must not choose the action;
  - `proposed_rendered_label` is nullable and copied only if an upstream
    rendered or proposed outcome exists;
  - `final_rendered_label` remains null for `abstain` and `human_review`;
  - V0 should not include long free-text clinical reinterpretation fields;
  - later LLM verifier artifacts may add evidence-grounded rationale fields and
    compare their actions against this baseline.

Next question:

- Should we implement deterministic `VerificationDecision` V0 now, or finish
  reviewing the remaining verifier/action design questions before code changes?

### VerificationDecision V0 Implementation

- Implemented deterministic `VerificationDecision` V0 as the baseline action
  harness over route V6.
- Added contract:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/verification_decision.py`.
- Added artifact builder:
  - `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_verification_decision.py`.
- Added focused tests:
  - `tests/test_gan2026_clinical_assessment_verification_decision.py`.
- Generated:
  - `experiments/gan2026_validation250_verification_decision_v0.jsonl`;
  - `experiments/gan2026_validation250_verification_decision_v0.json`;
  - `experiments/gan2026_validation250_verification_decision_v0.md`.
- VerificationDecision V0 summary:
  - input route rows: 250;
  - input routed rows: 5;
  - decision rows: 5;
  - action counts: 4 `abstain`, 1 `human_review`;
  - action basis counts: 4 `route_family_policy`, 1
    `manual_review_required`;
  - route family counts: 3 `cyclic_window_without_event_count`, 1
    `medication_cadence_ambiguity`, and 1
    `seizure_free_proxy_evidence_overreach`;
  - decision rows: 3468, 3469, 3493, 3534, and 5476.
- Current V0 row actions:
  - rows 3468, 3469, and 3493 -> `abstain`;
  - row 3534 -> `abstain`;
  - row 5476 -> `human_review`.
- Claim boundary:
  - deterministic validation250 verification-action baseline only;
  - no verifier model call;
  - no manual annotation;
  - no replacement label invention;
  - score context is audit-only.

Next question after implementation:

- Should the future LLM verifier be evaluated only on rows where
  `VerificationDecision` V0 emits `abstain` or `human_review`, or should it also
  replay rows where future V0 policies emit `affirm`/`reject`?

### LLM Verifier Evaluation Surface Decision

- Decision: the first LLM-verifier experiment evaluates only routed rows where
  deterministic `VerificationDecision` V0 emits `abstain` or `human_review`.
- Deferred scope:
  - `affirm`/`reject` replay is deferred until there are real V0
    `affirm`/`reject` rows or a predeclared proposed-outcome slice with
    non-null proposed outcomes.
- Rationale:
  - current route V6 contains 5 routed rows, all null-rendered risk families;
  - current deterministic `VerificationDecision` V0 emits 4 `abstain` actions
    and 1 `human_review` action;
  - evaluating imagined `affirm`/`reject` cases now would blur the boundary
    between verifier action and replacement scorer-facing label generation.
- Guardrail:
  - the first LLM verifier must not review hypothetical proposed labels and
    must not invent scorer-facing labels.

Next question:

- What should the LLM verifier consume?

### LLM Verifier Input Contract Decision

- Decision: the first LLM verifier consumes a row-local full-evidence
  verification case, not only the compact route evidence and not the literal
  full note text.
- Model-visible input should include:
  - the deterministic `VerificationDecision` V0 baseline row and action;
  - the embedded `Verification Route`, including route families, route reasons,
    route evidence, and source candidate ids;
  - clinical-assessment state needed to understand the routed object;
  - projection/render state, including proposed/rendered label state and
    projection or render issues;
  - all candidate evidence texts for the row;
  - candidate ids, source ids, and source spans where available.
- Excluded from verifier action input:
  - gold labels;
  - purist/pragmatic correctness;
  - exact normalized-label match;
  - benchmark outcome fields;
  - score-derived route or action hints;
  - literal full note text by default.
- Rationale:
  - row 3534 shows why compact summaries are insufficient: a clinical
    assessment may overstate proxy evidence as seizure freedom, so the verifier
    needs the candidate evidence that produced and challenged that assessment;
  - row 5476 shows why all candidate evidence matters: medication/rescue-use
    cadence must be compared with surrounding event evidence before deciding
    whether automation can own the case.
- Guardrail:
  - full evidence means all row-local candidate evidence and source spans, not
    gold/score context and not unrestricted note review.

Next question:

- What should the LLM verifier emit?

### LLM Verifier Output Contract Decision

- Decision: the first LLM verifier emits an evidence-grounded verifier action
  object, not a scorer-facing label, not a selected candidate, and not a
  rewritten clinical assessment.
- Allowed actions:
  - `affirm`;
  - `reject`;
  - `abstain`;
  - `human_review`.
- Required output fields should include:
  - `source_row_index`;
  - `component_owner`: `llm_verifier`;
  - `schema_version`;
  - `verifier_policy_id`;
  - deterministic V0 baseline action for comparison;
  - `action`;
  - `action_basis`;
  - cited candidate ids;
  - cited source ids or spans where available;
  - issue flags;
  - concise evidence-grounded rationale;
  - nullable proposed/final/replacement rendered-label fields.
- Guardrails:
  - the LLM verifier must not emit scorer-facing labels;
  - it must not choose among candidates as a second selector;
  - replacement/final rendered-label fields remain null for the first
    experiment unless a separate named action policy explicitly authorizes a
    non-null value;
  - `reject` blocks an existing proposed outcome but does not invent the
    replacement.
- Rationale:
  - row 5476 may justify `human_review` or `abstain`, but not a generated
    `1 per month` label;
  - row 3534 may justify blocking a proposed seizure-free outcome when one
    exists, but current route V6 is already null-rendered and should not be
    converted into a verifier-generated replacement label.

Next question:

- Is a comparator-preservation action policy needed before LLM verifier work?

### Comparator Preservation Deferral Decision

- Decision: no comparator-preservation action policy is needed before the first
  LLM verifier experiment.
- Rationale:
  - current route V6 contains only null-rendered risk rows;
  - there is no non-null proposed rendered outcome for a verifier to reject
    while preserving an existing comparator or baseline output.
- Revisit condition:
  - revisit only when a routed slice contains a non-null proposed rendered
    outcome that a verifier may reject and a named benchmark/action policy
    wants to preserve an existing comparator or baseline output.
- Guardrail:
  - comparator preservation must remain a named action policy, not verifier
    repair, clinical truth, or hidden projection behavior.

Next question:

- What aggregate counters should be predeclared before scaling beyond
  `validation250`?

### Validation750 And Full-Validation Counter Surface Decision

- Decision: predeclare a broad counter surface before scaling beyond
  `validation250`; simplify later only if the first scaled run shows the list
  is operationally too large.
- Route counters:
  - total rows;
  - structurally valid rows;
  - routed row count and routed row rate;
  - route family counts;
  - route family combinations;
  - route family counts by projection owner;
  - route family counts by projection/render issue;
  - null-rendered routed rows vs non-null proposed-outcome routed rows.
- Deterministic V0 baseline action counters:
  - `VerificationDecision` V0 action counts;
  - action counts by route family;
  - action counts by projection owner;
  - `abstain`/`human_review`/`affirm`/`reject` rates;
  - rows where V0 has a non-null `proposed_rendered_label`;
  - rows where V0 has a non-null `final_rendered_label`.
- LLM verifier counters:
  - LLM action counts;
  - LLM action counts by route family;
  - LLM-vs-V0 action delta counts;
  - V0 `abstain` -> LLM `affirm`/`reject`/`human_review`;
  - V0 `human_review` -> LLM `abstain`/`affirm`/`reject`;
  - LLM cited-evidence completeness rate;
  - LLM invalid-output, parse-failure, and schema-failure counts.
- Rendered-label impact counters:
  - rows where verifier action changes rendered-label availability;
  - rows where verifier blocks a proposed rendered label;
  - rows where verifier affirms a proposed rendered label;
  - rows where verifier leaves `final_rendered_label` null;
  - any non-null replacement or final label emitted under a named action
    policy.
- Audit-only score counters:
  - `score_context` presence count;
  - score status counts for routed rows;
  - score status counts by route family.
- Guardrail:
  - score counters are audit-only and must not trigger route or action behavior.

Next question:

- Which old components should be deleted, retained as audit-only, or renamed
  after the reset architecture stabilizes?

### Legacy Component Rationalisation Decision

- Decision: delay physical deletion of legacy components until after the first
  LLM verifier comparison, but classify legacy surfaces now so they no longer
  masquerade as core architecture.
- Keep as core reset architecture:
  - `ExtractedCandidate` and `CandidateSet`;
  - `SelectedClinicalFact` or `SelectedCandidateDecision`;
  - deterministic normalization;
  - projection owner policies;
  - `Verification Route`;
  - deterministic `VerificationDecision` V0;
  - future LLM verifier;
  - `Benchmark Renderer` and `FinalRenderedLabel`;
  - score-policy audit.
- Retain as audit/report-only for now:
  - H6/H9/H10 sidecars;
  - component evidence matrix;
  - legacy score reports;
  - failure review tables;
  - `score_context` envelopes.
- Rename or absorb if still needed:
  - selective safety floor -> verifier/action policy;
  - staged action policy -> `VerificationDecision` or action policy;
  - projection boundary gate -> named projection owner policy or verification
    route family;
  - boundary/renderer typed-event layer -> projection/render policy module if
    it maps cleanly to reset-stage schemas;
  - untagged nonprediction release -> action fallback policy, not extraction or
    selection.
- Deprecate after comparison unless a clean reset-stage role remains:
  - hybrid adjudicator raw as final labeler;
  - adapter layer if it still changes 0 rows or only hides repair;
  - deterministic top candidate as final answer;
  - broad state graph projection as renderer/projector;
  - H5 semantic repair if it changes clinical meaning instead of format.
- Guardrail:
  - no retained legacy component may own scorer-facing behavior unless it maps
    cleanly to an explicit reset-stage schema and owner.

### Outstanding Review Questions Closed

- The outstanding questions from
  `docs/research/gan2026_component_architecture_reset_review_plan_2026-06-05.md`
  have been walked and resolved through the decisions above:
  - LLM verifier evaluation surface;
  - LLM verifier input contract;
  - LLM verifier output contract;
  - comparator preservation policy;
  - validation750/full-validation counters;
  - legacy component rationalisation.
