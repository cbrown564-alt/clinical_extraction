# Gan 2026 Research Question Retrospective

Date: 2026-06-03

Scope: retrospective reframing of Gan 2026 seizure-frequency work after
`literature/gan2026_critical_analysis_pathways_forward.pdf`, the full research
retrospective, hidden-family atlas, component-evidence contract, selective
safety-floor audit, and simplified-schema generalization audit.

This is a research-control report, not a benchmark claim. Its purpose is to
stop broad architecture proliferation and convert the existing experiment base
into a sequence of clean questions that can be answered one at a time.

## Correction After RQ1/RQ2/RQ4 Diagnostic Reports

The first pass at RQ1, RQ2, and RQ4 fell into a subtler version of the same
validation trap this retrospective was meant to avoid. The reports correctly
stopped chasing whole-pipeline F1, but they still allowed the validation-tuned
deterministic rule set to win the component question by default:

- RQ1 concluded that the deterministic candidate set was the best broad
  candidate substrate.
- RQ2 concluded that deterministic top evidence was the safest default
  evidence-bearing substrate.
- RQ4 concluded that deterministic top was the best broad projection substrate.

Those are not meaningful research answers. The deterministic rules were
hand-crafted through validation development, showed a large generalization gap
on the locked test surface, and are expected to be brittle on genuinely new
clinical distributions. Reconfirming that they perform well on the validation
surface mostly measures our prior tuning, not the mechanics of the task.

Those three reports should therefore be treated as diagnostic baseline audits,
not completed research-question answers. Their useful content is the row-level
evidence about where LLM components expose, select, or project useful clinical
state, especially when they diverge from deterministic behavior. Their
deterministic-default conclusions should not move the project forward to RQ5.

The reset objective is:

```text
Take deterministic candidate selection and deterministic precedence decisions
off the table as answers. Use them only as frozen comparators, safety floors, or
failure-slice definers. Answer the RQs by studying LLM component mechanics:
what each LLM component tried to do, which rows it helped or harmed, and why.
```

## Executive Position

The project has enough architectural diversity and experiment evidence to stop
asking "which whole pipeline maximizes validation F1?" as the primary question.
That question is now actively low-information. High aggregate validation scores
have been achieved by deterministic comparators and hybrid safety-floor policies,
while LLM-only and typed-schema lanes show strong component signals but weak or
unstable end-to-end generalization.

The next phase should answer LLM component questions under strict attribution:

- candidate discovery;
- evidence selection;
- clinical state representation;
- projection;
- deterministic compilation/rendering;
- selective LLM value;
- generalization by hidden family;
- efficiency;
- abstention and ambiguity;
- gold/scorer validity.

The end-to-end assembly problem and deterministic/LLM blending problem should
be postponed. The project should first build high confidence about which LLM
component is most useful at each clinical subproblem, under which evidence
constraints, with what regression risk, on which distribution. A later assembly
phase can decide how to combine those LLM components with the frozen
deterministic comparator or safety floor.

## Why The Focus Must Change

The experiment record shows a repeated pattern:

1. A new architecture or schema performs well on a validation prefix or targeted
   stress panel.
2. A broader surface exposes hidden families that were underrepresented in the
   prefix.
3. The system adds local prompt or adapter repairs.
4. Attribution becomes harder because multiple components now share the same
   clinical decision.
5. End-to-end F1 moves less cleanly than the component signal suggests.

This is not wasted work. It revealed the true task structure. Seizure-frequency
extraction is construction and projection of an auditable clinical frequency
state, not direct label prediction. But the current research discipline must now
match that structure.

The immediate objective is no longer:

```text
Find a new architecture that improves total validation F1.
```

It is:

```text
Answer one named LLM component question deeply enough that future architecture
assembly can rely on it.
```

The question is also no longer:

```text
Does the full deterministic rule set still perform best on validation?
```

That answer is already known and low-information. Deterministic artifacts may
define baseline rows, regression risk, and comparison surfaces, but they cannot
be promoted as the answer to RQ1, RQ2, RQ3, or RQ4 unless the active question is
explicitly about deterministic rules.

## Retrospective Against The PDF Pathways

The critical-analysis PDF proposed several major pathways and reframings. Their
implementation and answer status are uneven.

| Pathway | Implementation status | Answer status | Interpretation |
| --- | --- | --- | --- |
| Hidden-family atlas | Substantially implemented | Partly answered | We now have a first atlas over saved validation artifacts, but it needs to become the default stratification layer for every question. |
| Causal first-failure attribution | Partially implemented | Partly answered | First-failure ownership exists for selected artifacts, but not yet as a complete per-question matrix across all relevant components. |
| State graph as intermediate representation | Partially implemented | Not answered | The graph is a strong diagnostic substrate; superiority as a final or generalizing IR is not proven. |
| Projection benchmark | Partially implemented | Not answered | Projection failures are visible, but deterministic, LLM, pairwise, oracle, and abstaining projection have not been compared as a formal benchmark. |
| LLM missing-candidate generation | Mostly unimplemented | Not answered | Constrained adjudication showed candidate-recall ceilings, but LLM proposer-with-verifier has not had a clean component test. |
| Selective complementarity | Substantially implemented | Mostly answered for one candidate | `selective_safety_floor_gate_v0` shows evidence-valid, zero-regression selective gains, but only for a hybrid safety-floor claim. |
| Abstention as first-class output | Mostly unimplemented | Not answered | Unknown/no-reference and ambiguity are tracked as labels/families, but coverage-accuracy and review-routing behavior are not yet studied. |
| Gold/scorer audit | Mostly unimplemented | Not answered | The need is clear; hard-row adjudication has not been performed as a formal study. |
| Typed LLM reasoning | Implemented and audited | Partly answered negatively | Current typed/sparse schemas expose useful selected-evidence signal, but deeper operands/graph projection regressed under broad validation. |

The most important meta-answer is that implementation has outpaced certainty.
Several research instruments now exist, but only a few questions have mature
answers.

## Current Strong Opinions

These are defensible working conclusions from the current evidence.

### 1. End-to-end validation F1 is saturated as a development guide

Validation750 can be cleared by a hybrid deterministic-safety-floor policy, and
incremental aggregate improvements can hide whether the LLM, graph projection,
adapter, or safety floor did the clinical work. Broad validation reruns should
not be the default next step.

### 2. Candidate recall remains a hard ceiling

Constrained adjudication cannot recover a missing candidate. Candidate discovery
must be studied directly, including whether LLMs can propose missing
exact-evidence candidates without exploding false positives.

### 3. LLMs are better at source-near selection than final Gan label ownership

Multiple LLM-heavy runs show selected-evidence or selected-state signal that is
much stronger than raw final-label output. That supports testing LLMs as
evidence selectors, candidate proposers, state describers, and rankers rather
than final scorer-label emitters.

### 4. More schema is not automatically better

`typed_operations_v0` and A2 sparse operands showed that richer schemas can
duplicate decision ownership and give deterministic sidecars more ways to
override correct selected evidence. Schema quality must be judged by component
performance, token cost, parse reliability, and downstream projection stability,
not by apparent expressiveness.

### 5. Projection is probably the central unsolved bottleneck

The system often can find or represent useful evidence, but selecting the
current, benchmark-relevant state remains brittle across hidden families:
current versus historical, competing semiologies, seizure-free boundaries,
unknown boundaries, cluster burden, and denominator/window binding.

### 6. Selective action is more credible than replacement

The strongest frozen-audit evidence comes from small, gated changes with exact
evidence and no deterministic-correct regressions. This suggests that LLM value
should be measured first as selective high-precision intervention, not as whole
pipeline replacement.

### 7. Hidden families must become the unit of generalization

Validation prefixes were repeatedly overoptimistic. Future claims should name
which hidden families improved, which regressed, and whether the result held
outside the rows that motivated the change.

## Research Discipline For The Next Phase

### Rule 1: One Active Question

Only one research question may be active at a time. Work may gather background
for later questions, but implementation, experiments, and status updates should
name one primary question.

### Rule 2: No New Whole-Pipeline F1 Chasing

Do not start a new architecture or broad validation run whose main purpose is to
raise total Purist or Pragmatic F1. Broad validation is allowed only when a
predeclared component answer requires a larger distribution check.

### Rule 3: LLM Component Metrics First

Each question must define component-level outcomes before any run:

- recall, precision, and exact-evidence rate for candidate discovery;
- selected-evidence accuracy for evidence selection;
- schema validity, sparsity, contradiction rate, and representability for state
  representation;
- projection accuracy given fixed candidates/states;
- rendering accuracy given a fixed selected state;
- changed-label precision and correct-to-wrong rate for selective LLM action;
- cost, latency, parse failure, token budget, and retry rate for efficiency.

For RQ1-RQ4, the primary table must compare LLM components or LLM schemas. The
deterministic system is allowed only as a frozen comparator, safety floor,
failure-slice source, or oracle-gap reference. "The deterministic selector is
best" is not a valid stop rule.

### Rule 4: Fixed Surfaces And Paired Comparisons

Prefer same-row and same-raw-output comparisons. Use validation prefixes only as
smoke tests. Use hard slices, hidden-family panels, saved-output replay, and
component-stress panels for mechanism evidence.

### Rule 5: No Architecture Promotion Without A Question Answer

An experiment can be useful even if it lowers end-to-end F1. It is promotable
only if it answers the active question with a clear claim boundary.

### Rule 6: Every Answer Must State Residual Uncertainty

Each question should end in one of four states:

- answered;
- answered for a named distribution only;
- negative result;
- blocked by missing instrumentation or data.

### Rule 7: Row-Level Mechanism Before Aggregates

An RQ1-RQ4 answer must include row-level mechanism analysis before any aggregate
decision. The report must inspect representative wins, losses, and ambiguous
cases for each LLM component and explain:

- what the LLM appeared to attend to;
- whether the selected evidence was clinically decisive or merely substring
  present;
- which state attribute was right or wrong;
- whether the failure was generation, evidence selection, state representation,
  projection, rendering, or scoring;
- whether the behavior looks like a transferable mechanism or a validation
  artifact.

Aggregate counts are supporting evidence. They are not the answer.

## The Research Questions

### RQ1. Candidate Discovery

Question: Which LLM component or schema produces the most useful
seizure-frequency candidates: high gold-state recall, exact evidence, rich
useful metadata, bounded candidate count, and row-level mechanisms that plausibly
transfer beyond the validation-shaped deterministic rules?

Why it matters: if the correct state is absent, selection, projection, and
rendering cannot recover it.

LLM candidate components to compare:

- LLM source-near event extraction;
- LLM missing-candidate proposer over deterministic misses;
- raw LLM candidate selector;
- LLM selected-state or selected-evidence candidates;
- claim-table candidate extraction;
- graph boundary-node builders;
- union candidates with verifier gates.

Frozen deterministic candidates are the comparator and miss-slice source, not a
candidate answer.

Primary metrics:

- gold-state candidate recall;
- exact evidence rate;
- candidate precision or false-positive burden;
- candidates per note;
- hidden-family recall;
- metadata completeness for temporality, certainty, assertion, status, type,
  relation, denominator/window, cluster burden, seizure-free duration, and
  evidence.

Evidence surfaces:

- saved validation artifacts;
- validation hard slices for known candidate misses;
- synthetic stress panel for missing-candidate phenomena;
- later, frozen/blinded audit only after the component protocol is fixed.

Current answer: reset to not answered. The first-pass RQ1 report is a useful
diagnostic baseline audit, but it answered "does the validation-tuned
deterministic candidate set remain strong?" rather than "which LLM candidate
generator is mechanistically useful?"

Recommended next action: re-run RQ1 as an LLM candidate-mechanics analysis over
same-row artifacts and selected failure slices. Lead with row examples where LLM
candidate generation wins, loses, or creates burden, then summarize by hidden
family.

### RQ2. Evidence Selection

Question: Given the note and/or a fixed candidate set, which LLM component best
selects prediction-bearing evidence, and why does that evidence help or fail
when projected into a clinical frequency state?

Why it matters: many LLM runs show selected-evidence signal even when final
labels fail. This should be isolated from rendering and projection.

LLM evidence components to compare:

- LLM selected evidence from simplified selected-state schemas;
- typed-operation selected evidence;
- claim-table evidence;
- hybrid sidecar selected evidence.

Deterministic selected evidence is the frozen baseline and evidence-shape
contrast, not the default answer.

Primary metrics:

- exact selected evidence rate;
- source id validity;
- selected-evidence arithmetic correctness;
- evidence support for gold hidden family;
- evidence precision on changed rows;
- evidence invalid/missing failure rate.

Current answer: reset to not answered. The first-pass RQ2 report showed that
some LLM layers can produce exact/source-traced evidence, but it collapsed the
answer back into deterministic label safety. The open question is which LLM
evidence selector finds clinically decisive evidence by hidden family and which
attribute errors prevent that evidence from becoming a correct state.

### RQ3. Clinical State Representation

Question: What intermediate schema best represents the clinical frequency state
for downstream reasoning?

Why it matters: final labels collapse important distinctions. But richer schemas
can increase token cost, parse failures, contradictions, and duplicated decision
ownership.

Candidate schemas:

- selected evidence only;
- selected state with sparse operands;
- typed operations;
- claim table;
- state graph;
- minimal boundary-tag schema.

Primary metrics:

- schema validity;
- exact traceability;
- representability of gold state;
- sparsity/candidate count;
- contradiction rate;
- token/cost/latency;
- downstream projection stability;
- adapter regression rate.

Current answer: partly answered negatively. A2 and typed operations show that
more structured operands/graphs can hurt broad generalization when ownership is
duplicated. The best positive schema is not yet known.

### RQ4. Projection

Question: Given fixed LLM-produced candidates, evidence, or state objects, which
LLM or graph-assisted projection policy best selects the current
benchmark-relevant state, and on which row mechanisms does it succeed or fail?

Why it matters: projection is now one of the clearest bottlenecks. Graph
representability is insufficient if the projection policy cannot choose the
right state without oracle help.

LLM/projection components to compare:

- graph projection;
- LLM projection over fixed exact-evidence nodes;
- pairwise ranking/tournament;
- selective projection with abstention;
- oracle projection upper bound.

Deterministic precedence is the frozen comparator and regression-risk baseline,
not an eligible projection answer.

Primary metrics:

- projection accuracy given fixed candidates;
- wrong-to-correct and correct-to-wrong deltas versus deterministic baseline;
- projection precision on hidden families;
- abstention coverage and accuracy;
- contradiction sensitivity;
- oracle gap.

Current answer: reset to not answered. The first-pass RQ4 report rejected broad
graph replacement and reselected deterministic top. That is a baseline-safety
finding, not an LLM projection answer. RQ4 remains open until it explains which
LLM or graph-assisted projection mechanisms handle current-versus-historical,
competing semiology, boundary, duration, denominator, and cluster rows.

### RQ5. Deterministic Compilation And Rendering

Question: Once the correct clinical state is selected, what deterministic
compiler renders it into Gan-compatible labels without semantic drift?

Why it matters: arithmetic and benchmark grammar should be mechanical whenever
the selected clinical fact is fixed. But adapters have repeatedly crossed into
semantic rescue or semantic regression.

Primary metrics:

- rendering accuracy given fixed selected state/evidence;
- selected-evidence-correct to adapter-wrong regressions;
- adapter wrong-to-correct rescues;
- traceability of operands to selected evidence;
- benchmark-format-only changes versus semantic changes;
- per-family rendering errors.

Current answer: partly answered. Selected-evidence arithmetic is often strong;
sparse operands and typed graph projection introduced avoidable regressions.

### RQ6. Selective LLM Value

Question: Where does the LLM add reliable value over deterministic rules under
exact-evidence and no-regression constraints?

Why it matters: replacement-style LLM results are weak, but selective
LLM-assisted changes can be credible and clinically useful.

Primary metrics:

- changed-label precision;
- wrong-to-correct count;
- correct-to-wrong count;
- deterministic-correct regression count;
- exact changed-row evidence;
- hidden-family distribution of changes;
- sidecar-only versus projection-only contribution.

Current answer: mostly answered for `selective_safety_floor_gate_v0`, not
globally. The sidecar contributes real, evidence-valid selective gains, but the
final candidate is hybrid and safety-floor dependent.

### RQ7. Generalization By Hidden Family

Question: Which component gains transfer across hidden families, validation
prefixes, later validation rows, hard slices, and frozen audit surfaces?

Why it matters: prefix optimism has misled several decisions. The unit of
generalization should be hidden family, not aggregate validation prefix.

Primary metrics:

- per-family candidate recall;
- per-family evidence selection;
- per-family projection accuracy;
- per-family adapter regression;
- first-failure owner by family;
- prefix versus later-validation performance;
- fresh/blinded audit agreement when available.

Current answer: partly answered. The hidden-family atlas exists, but it has not
yet become the governing table for every component question.

### RQ8. Efficiency And Operational Reliability

Question: What schema/component design gives the best performance per token,
cost, latency, parse reliability, and implementation complexity?

Why it matters: a high-performing schema that requires huge token budgets,
fragile parsing, or multiple retries may not be usable, especially for local LLM
transfer.

Primary metrics:

- prompt and completion tokens;
- wall-clock latency;
- cost per 1,000 notes;
- parse/schema failure rate;
- retry rate;
- model sensitivity;
- metadata yield per token;
- correctness per cost.

Current answer: not answered. Evidence suggests typed operations were too
complex, but there is no formal efficiency comparison across schemas.

### RQ9. Abstention And Human Review

Question: Can the system identify underdetermined, conflicting, stale-only, or
ambiguous cases instead of forcing a brittle label?

Why it matters: clinical usefulness may come from trustworthy evidence and
uncertainty routing, not forced label coverage.

Primary metrics:

- coverage-accuracy curve;
- abstention precision;
- review burden;
- unsafe forced-label reduction;
- hidden-family abstention distribution;
- corrected accuracy after human review.

Current answer: not answered. Unknown/no-reference boundaries are tracked, but
abstention has not been studied as an endpoint.

### RQ10. Gold And Scorer Validity

Question: How much residual error reflects true extraction failure versus
benchmark convention, underdetermined notes, clinically defensible alternatives,
or possible gold-label weakness?

Why it matters: without this, hard-row failures may push the system toward
benchmark-specific overfitting.

Primary metrics:

- hard-row ambiguity rate;
- all-system-fail rows;
- exact-evidence-but-scorer-wrong rows;
- clinically defensible alternative labels;
- benchmark convention dominated rows;
- likely gold defects.

Current answer: not answered. This should follow after RQ1-RQ4 identify the
most persistent hard-row families.

## Recommended Question Order

1. RQ1 LLM Candidate Discovery.
2. RQ2 LLM Evidence Selection.
3. RQ4 LLM/Graph-Assisted Projection.
4. RQ3 LLM Clinical State Representation.
5. RQ5 Deterministic Compilation And Rendering.
6. RQ6 Selective LLM Value.
7. RQ7 Generalization By Hidden Family.
8. RQ8 Efficiency And Operational Reliability.
9. RQ9 Abstention And Human Review.
10. RQ10 Gold And Scorer Validity.

RQ7 should be reported inside every question, but it is also listed separately
because a final generalization synthesis will be needed after the first several
component questions are answered.

## Restart Protocol: RQ1 LLM Candidate Discovery

The next active research question should return to RQ1, but with deterministic
candidate selection off the table as an answer.

Predeclared claim boundary:

```text
We are not evaluating end-to-end F1, and we are not asking whether the
validation-tuned deterministic candidate set is strong. We are evaluating which
LLM component exposes the gold-relevant clinical state as an evidence-valid
candidate with useful metadata, acceptable burden, and a row-level mechanism
that plausibly transfers.
```

Minimum report table:

| LLM component | Surface | Gold-state recall | Exact evidence | Candidate burden | Metadata completeness | Mechanism summary | Hidden-family failures |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |

Minimum row-level fields:

- source row index;
- gold label;
- hidden-family tags;
- LLM component or schema;
- candidate id;
- candidate evidence;
- evidence exact/source-near/invalid/missing;
- candidate semantic kind;
- temporality;
- assertion/status;
- certainty;
- seizure type or event family;
- count/window/denominator;
- cluster fields;
- seizure-free duration fields;
- whether candidate matches gold state under the active policy;
- first missing attribute if it does not;
- deterministic baseline status for context only;
- row-level mechanism note explaining what the LLM tried to do and why it was
  useful, harmful, or ambiguous.

Acceptable experiments:

- artifact replay over saved validation outputs;
- hard-slice candidate-recall analysis where deterministic misses define the
  slice but cannot win the answer;
- a small LLM missing-candidate proposer test on predeclared deterministic-miss
  rows with exact-evidence verifier gates;
- same-row comparison among LLM sidecar, selected-state, selected-evidence, and
  claim-table candidate views;
- synthetic stress rows only to test specific candidate-discovery mechanisms.

Disallowed experiments for RQ1:

- new whole-pipeline architecture;
- broad validation750 final-label run;
- prompt patches judged mainly by total Purist F1;
- concluding that deterministic candidates are the best candidate generator;
- any locked-test row-level tuning.

Completion criterion:

RQ1 is answered when the report can state which LLM candidate generator has the
best recall/precision/metadata/candidate-burden trade-off by hidden family,
backed by row-level examples that explain the mechanism. If no LLM generator is
useful enough, the answer is a negative result about LLM candidate generation,
not a promotion of deterministic candidates.

## Implications For The Repo

The project status should no longer present "build a pipeline above 0.9000
Purist F1" as the active objective. That objective was useful, but it now pulls
the work toward aggregate optimization. The active objective should become:

```text
Answer the Gan 2026 LLM component research questions one at a time, restarting
with LLM candidate discovery, under exact-evidence, row-level mechanism,
attribution, hidden-family, and split-discipline constraints.
```

Every future experiment artifact should name:

- active research question;
- component under test;
- comparison component;
- fixed input surface;
- component metric;
- hidden-family stratification;
- deterministic baseline role, limited to comparator, safety floor, miss-slice
  source, or oracle-gap reference;
- row-level mechanism examples;
- whether the experiment is diagnostic, development evidence, or promotion
  evidence.

## Bottom Line

The project is ready to become more scientific by becoming narrower. The next
phase should deliberately ignore overall F1 unless a specific component question
requires it as a secondary sanity check. It should also stop asking the
deterministic rule set to prove itself on the validation surface. The correct
research move is to build a library of high-certainty LLM component answers:

- who finds the right candidates;
- who selects the right evidence;
- what schema carries the right state;
- who projects the right state;
- who renders it safely;
- when the LLM is worth trusting;
- where the result transfers;
- when the system should abstain.

Once those answers exist, architecture assembly becomes a much cleaner problem.
