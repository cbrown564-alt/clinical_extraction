> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ1/RQ2 Component-Control Fundamentals Analysis

Date: 2026-06-04

Status: validation-development fundamentals analysis. This is not a locked-test,
benchmark-comparable, or F1-maximization claim.

Source artifact:
`experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.jsonl`

Summary report:
`experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.md`

## Essential Answer

The fundamental result is not that one prompt "wins." The result is that the
model is reliable when the task is extractive and source-local, less reliable
when the task asks it to maintain a complete candidate set, and unreliable as a
direct benchmark-state projector or all-in-one architecture.

Best component primitive:
`candidate_conditioned_evidence_only`.

Best broad evidence locator:
`gold_query_evidence_only`.

Best candidate-discovery role:
`candidate_only`, but only as a selective rescue and ambiguity-exposure surface.

Best paired condition:
`evidence_plus_projection` for evidence preservation only; not as proof of
projection quality, because projection labels are usually omitted.

Rejected architecture shape:
`candidate_plus_evidence_plus_projection` as a broad one-prompt replacement.

Rejected component role:
unconstrained LLM projection as direct final-label rendering.

## What Good Means Here

Because this study is not chasing F1, each condition needs its own standard.

| Condition family | What good means | What would be bad even if final F1 looked fine |
| --- | --- | --- |
| Candidate generation | Exposes clinically plausible current, recent, competing, uncertain, seizure-free, cluster, and no-reference facts with exact evidence and manageable candidate burden. | Hiding ambiguity, emitting unsupported candidates, exploding candidate burden, or prematurely choosing the benchmark answer. |
| Evidence selection | Selects exact source substrings with valid source ids, classifies decisive/context/conflict/temporality, and exposes missing operands. | Selecting plausible but non-exact text, losing source ids, or calling incomplete evidence decisive without missing operands. |
| Projection | Given fixed candidate/evidence state, chooses the benchmark-relevant current state, preserves uncertainty, and renders or abstains consistently. | Collapsing unknown to no-reference, overcalling seizure freedom, omitting labels for ordinary frequencies, or mixing clinical interpretation with benchmark formatting. |
| Paired overload | Shows what is lost when two or three subtasks are combined, while preserving the isolated-task contract as much as possible. | Treating a paired prompt as preferred merely because it parses, or letting final-answer pressure reduce candidate/evidence completeness. |

The evaluation gates are therefore:

- schema contract: does the output satisfy the frozen component schema, not just
  JSON parsing;
- source grounding: exact evidence and valid source ids where evidence is
  selected;
- burden: candidates and spans per row should be useful, not maximal;
- ambiguity preservation: uncertain or competing states must remain visible;
- compositional stability: adding another subtask should not degrade the prior
  subtask;
- projection discipline: final-label rendering must be separated from clinical
  fact/evidence selection.

## Component Verdicts

### 1. Candidate-Conditioned Evidence Is The Cleanest Primitive

`candidate_conditioned_evidence_only` is the strongest fundamental component.

It asks a narrow question: given a candidate/state, can the model find and
classify the supporting, contradicting, or incomplete evidence? On the completed
matrix it gives:

- balanced panel: 50/50 schema-valid, 47/50 exact evidence;
- hard panel: 75/75 schema-valid, 73/75 exact evidence;
- low burden: about one evidence span per row on both panels;
- valid source ids on the new hard-panel run.

Why it works:

- the task is local and extractive;
- the candidate anchors attention;
- the model can say "incomplete" instead of forcing a label;
- the output contract does not require benchmark policy.

What it does not solve:

- it cannot discover a missing candidate by itself;
- it can validate the wrong supplied candidate if the upstream selector is
  wrong;
- it does not decide final Gan syntax.

Decision: keep this as the main RQ2 primitive. It is the best evidence gate for
any candidate/state proposed by deterministic code, LLM candidate rescue, or a
future schema experiment.

### 2. Gold-Query Evidence Is A Good Broad Locator, But Higher Burden

`gold_query_evidence_only` is the best broad evidence locator.

It gives:

- balanced panel: 50/50 schema-valid, 47/50 exact evidence;
- hard panel: 74/75 schema-valid, 69/75 exact evidence;
- broader context exposure than candidate-conditioned evidence;
- more spans per row: 2.52 mean on balanced and 3.21 mean on hard rows.

Why it works:

- the task is still extractive;
- the model can include supporting, historical, and future/planned context;
- it does not have to choose the final benchmark state.

Why it is less clean than candidate-conditioned evidence:

- higher evidence burden can make downstream selection harder;
- broad query prompts collect context that may be clinically useful but not
  decision-bearing;
- exact text can be present while count, denominator, currentness, cluster axis,
  or seizure-free boundary remain unresolved.

Decision: use this when the candidate set is uncertain or when we need a broad
evidence packet for review. Prefer candidate-conditioned evidence when a fixed
candidate/state already exists.

### 3. Candidate Generation Has Selective Value, Not Broad Authority

`candidate_only` is useful, but not as an autonomous answer selector.

It gives:

- balanced panel: 42/50 schema-valid, 47/50 exact or checked-exact evidence;
- hard panel: 63/75 schema-valid, 67/75 exact or checked-exact evidence;
- manageable burden: mean 1.20 candidates on balanced and 1.68 on hard;
- more candidate diversity on hard rows, including frequency, cluster,
  seizure-free, last-event, unknown, and no-reference candidates.

Why it works:

- it exposes alternative clinical states without forcing projection;
- hard rows naturally need multiple candidates;
- candidate burden is not explosive.

Why it is weaker than evidence selection:

- schema drift appears more often, especially extra fields and raw-output
  fallbacks;
- not-checked rows frequently correspond to malformed or raw packets;
- candidate generation still needs a downstream evidence gate and selector.

Decision: keep LLM candidate generation as a selective rescue and ambiguity
exposure component. It should propose facts for later evidence validation, not
decide the final label.

### 4. Evidence Plus Projection Preserves Evidence, But Does Not Prove Projection

`evidence_plus_projection` looks excellent on exact evidence:

- balanced panel: 50/50 exact evidence;
- hard panel: 74/75 exact evidence;
- 50/50 and 75/75 schema-valid.

But this condition usually omits `seizure_frequency_label` in the projection
decision:

- balanced panel: 40/50 projection decisions missing a label;
- hard panel: 62/75 projection decisions missing a label.

This is a useful warning. The model can select exact evidence and classify a
decision kind, but when the projection must become a benchmark label it often
retreats into uncertainty or explanation instead of rendering.

Decision: treat `evidence_plus_projection` as evidence plus provisional state
classification, not as final projection. It is promising only if followed by a
deterministic compiler/policy layer.

### 5. Full Bundling Creates Overload

`candidate_plus_evidence_plus_projection` is the clearest negative architecture
signal.

It parses, but exact-evidence quality drops:

- balanced panel: 35/50 exact evidence;
- hard panel: 52/75 exact evidence.

It also loses the component contract:

- balanced panel: 44/50 schema-valid;
- hard panel: 63/75 schema-valid;
- 14 balanced rows and 18 hard rows had no instrumented source ids;
- many projection decisions omit labels;
- some ambiguous or unresolved rows produce zero candidates and zero evidence
  while still making a projection-like decision.

Why it fails:

- the prompt asks the model to discover, ground, arbitrate, and render at once;
- final-answer pressure competes with candidate recall and evidence exactness;
- ambiguity preservation is weaker when the model must also decide;
- schema adherence decays as the output gets wider.

Decision: reject full bundling as a preferred architecture. Keep it as a stress
test for overload and failure analysis.

### 6. Projection Is The Bottleneck

Projection-only is not a trustworthy final-label component.

Balanced panel:

- 50/50 schema-valid;
- 4/50 exact canonical labels;
- 33/50 broad decision-kind matches;
- unknown rows: 0/8 broad kind matches;
- unresolved-multiple rows: 1/8 broad kind matches.

Hard panel:

- 75/75 schema-valid;
- 0/75 exact canonical labels;
- 29/75 broad decision-kind matches;
- unknown rows: 0/22 broad kind matches;
- seizure-free-duration family: 0/27 broad projection matches;
- unknown-boundary family: 0/20 broad projection matches.

The model often recognizes ordinary frequency and some broad seizure-free
states, but it cannot be trusted to handle policy boundaries:

- unknown versus no-reference;
- seizure-free overreach when there are conditional or competing event states;
- unresolved multiple states;
- benchmark-format conventions;
- current versus historical or denominator/window interpretation.

Decision: projection must remain deterministic, gated, or policy-mediated. LLM
projection can produce diagnostic notes or provisional state hints, but not the
final label.

## The Debate

### Argument For Candidate Generation

Candidate generation is the only component that can expose a missing clinical
state before the system knows what evidence to ask for. On hard rows it expands
the space in useful ways: cluster, seizure-free, unknown, last-event, and
competing frequency candidates appear together. This is exactly what deterministic
rules often miss.

Counterargument:

Candidate generation is also where schema drift and unsupported breadth enter.
If promoted broadly, it creates a selector problem and can bury the gold-relevant
state among plausible alternatives.

Resolution:

Use it selectively for rescue, boundary, and ambiguity cases, then pass every
candidate through candidate-conditioned evidence validation.

### Argument For Evidence Selection

Evidence selection is the most reliable LLM-owned capability. It is extractive,
auditable, source-grounded, and decomposes well. The hard panel shows this is not
only an easy-row phenomenon.

Counterargument:

Evidence selection alone does not solve currentness, denominator, cluster
aggregation, seizure-free duration, or benchmark policy. Exact text can still be
the wrong fact or an incomplete operand set.

Resolution:

Treat evidence selection as the grounding layer, not the decision layer.

### Argument For Projection

Projection seems like the place where clinical reasoning should help: it can
read context, preserve uncertainty, and avoid brittle rules.

Counterargument:

The data says the opposite for this benchmark. Projection is where the model
confuses policy states, overcalls seizure freedom, omits labels, and collapses
unknown or unresolved rows. The task is not just clinical reasoning; it is a
benchmark-policy mapping problem with exact formatting consequences.

Resolution:

Use explicit projection policies and deterministic rendering. Let the model
provide selected facts, evidence, and uncertainty annotations, but do not let it
own final projection.

### Argument For Paired Prompts

Paired prompts might preserve local context and reduce interface loss between
components. `evidence_plus_projection` supports this partially: evidence remains
excellent when the candidate is fixed.

Counterargument:

The full bundle shows that adding candidate discovery and projection together
degrades evidence exactness and schema compliance. The model starts optimizing a
whole answer instead of preserving subproblem outputs.

Resolution:

Use paired prompts only when the upstream state is fixed and the paired task is
still narrow. Do not collapse candidate discovery, evidence selection, and
projection into one prompt.

## Principled Architecture View

The best architecture is staged:

1. Deterministic/state-graph substrate proposes the ordinary candidate set and
   remains the safety floor.
2. LLM candidate generation is called selectively on ambiguity, boundary,
   seizure-free, cluster, and deterministic-miss slices.
3. Candidate-conditioned LLM evidence selection validates proposed candidates
   with exact spans and valid source ids.
4. Broad gold-query evidence selection is used for review, missing-candidate
   diagnostics, or rows where candidate coverage is uncertain.
5. A typed state representation carries currentness, seizure type, denominator,
   cluster axis, seizure-free duration, and uncertainty.
6. Deterministic projection/policy/rendering maps the selected state to Gan
   syntax.
7. Full bundled prompts are retained only as overload diagnostics.

## Decision

For RQ1/RQ2 fundamentals, the preferred LLM-owned components are:

1. `candidate_conditioned_evidence_only`;
2. `gold_query_evidence_only`;
3. selective `candidate_only`.

The rejected LLM-owned components are:

1. direct `projection_only` final rendering;
2. broad `candidate_plus_evidence_plus_projection` replacement;
3. any paired condition interpreted through final-label correctness without
   component gates.

The next research move should not be another broad F1 run. It should be a schema
and policy experiment that asks:

```text
Can we carry LLM-selected candidate/evidence facts into a typed state that a
deterministic projection policy can render without losing ambiguity?
```

That is the right bridge into RQ3.
