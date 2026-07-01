> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ1/RQ2 Single-Task Controls Protocol

Date: 2026-06-04

Status: pre-run validation-development protocol. This supersedes treating the
2026-06-04 RQ1/RQ2 mechanism answers as sufficient to move on to RQ3. Those
answers remain useful saved-replay diagnostics, but they do not establish
single-task model ceilings or mixed-task overload.

## Purpose

The next experiment program should answer a cleaner question than the previous
mixed-component reports:

```text
When the model is asked to do only one clinical subtask, with rich instructions
and no pressure to optimize downstream F1, how well can it perform that subtask?
```

The subtasks are:

- candidate generation;
- evidence selection;
- projection from fixed candidate/evidence state;
- paired-task combinations, used only after isolated-task ceilings are known.

The goal is not to maximize Purist or Pragmatic F1. The goal is to remove
confounders, identify model capability limits, and expose which representation
choices make later stages easier or harder.

## Prior Evidence And Gap

The saved RQ1/RQ2/RQ4 component-mechanics reports showed that:

- LLM candidate generation has selective value on boundary, uncertainty,
  seizure-free, and competing-state rows;
- LLM evidence selection is often exact and source-traced;
- broad LLM or graph projection replacement is unsafe under current artifacts;
- projection and typed-state representation remain major first-failure owners.

Those reports are still confounded because the observed behavior often came from
prompts or artifacts that blended candidate selection, evidence selection,
state representation, projection, deterministic adapters, and safety floors.
They answer "what did these saved mixed systems do?" better than "what can the
model do when the task is isolated?"

## Fixed Experimental Controls

All experiments in this protocol must hold these variables fixed unless a later
protocol amendment explicitly changes them:

- Split manifest: `gan2026_split_v1`.
- Development surface: validation only. Locked test row-level inspection is
  excluded.
- Model family: one primary model per round, recorded in every artifact.
- Sampling: deterministic or near-deterministic decoding where the provider
  supports it.
- Row panels: the same source rows across isolated and paired-task conditions.
- Prompt budget: rich task-specific instructions are allowed, but each prompt
  must optimize only its named subtask.
- Scoring: component metrics first; final label correctness is secondary except
  in projection-only experiments.
- Evidence gate: selected evidence must be exact source substring with valid
  source id where the input/source format permits it.
- Deterministic system role: frozen comparator, substrate, oracle-gap reference,
  or safety floor only. It is not eligible as the RQ1/RQ2 answer.

## Row Surfaces

Use two validation-development surfaces before any broader run:

1. **Balanced validation50 control panel.** A fixed 50-row validation panel with
   ordinary rates, unknown/no-reference rows, seizure-free duration rows,
   cluster/diary rows, current-versus-historical rows, denominator/window rows,
   and competing-semiology rows.
2. **Hidden-family hard panel.** A fixed validation hard-slice panel drawn from
   the hidden-family atlas and component-projection follow-up rows, with row ids
   recorded before fresh calls.

The first run may use saved artifacts to build the panels and row metadata, but
fresh model calls for the isolated prompts must be predeclared by prompt name,
model, row panel, schema, and stop rule.

## Experiment A: Candidate Only

Question:

```text
Can the model expose all clinically plausible seizure-frequency candidate facts
without selecting the final answer or projecting to Gan syntax?
```

The prompt should maximize faithful candidate recall, preserve ambiguity, and
avoid downstream scoring pressure.

Inputs:

- note text and stable source ids;
- no gold label;
- no deterministic top label;
- no instruction to choose the final benchmark answer.

Required output fields per candidate:

- candidate id;
- exact evidence span and source id;
- candidate kind;
- currentness and temporality;
- assertion or uncertainty status;
- seizure type or semiology target;
- count, window, unit, denominator, cluster cadence, per-cluster burden, or
  seizure-free duration when present;
- explicit ambiguity flags;
- optional projection hint marked as non-decisive.

Primary metrics:

- gold-relevant candidate coverage using the RQ1 tiered match policy;
- exact-evidence and valid-source-id rate;
- unsupported-candidate rate;
- candidates per note, median and p90;
- metadata completeness by candidate kind;
- hidden-family recall.

Interpretation rule:

Multiple candidates are not a failure unless unsupported candidates, missing
metadata, or a fixed downstream selector shows that multiplicity harms the next
stage.

## Experiment B: Evidence Only

Question:

```text
Given a fixed query or candidate state, can the model select the decisive
evidence and classify its role without choosing or rendering the final label?
```

Run two variants on the same rows:

- `gold_query_evidence_only`: asks for evidence needed to answer the seizure
  frequency question, without giving a deterministic candidate.
- `candidate_conditioned_evidence_only`: gives one fixed candidate/state and
  asks whether the evidence supports, contradicts, or incompletely supports it.

Required output fields:

- selected evidence span and source id;
- evidence role: decisive, supporting context, conflicting, historical,
  future/planned, proxy/non-seizure, ambiguous, or insufficient;
- missing operands;
- conflict notes;
- no final Gan label.

Primary metrics:

- exact-evidence and valid-source-id rate;
- decisive-evidence precision;
- conflict and ambiguity classification accuracy;
- operand completeness for projection;
- hidden-family evidence support;
- rows where an apparent evidence failure is reclassified as projection,
  schema, candidate, or gold/scorer ambiguity.

## Experiment C: Projection Only

Question:

```text
Given fixed candidate facts and exact evidence, can the model choose the
benchmark-relevant current state and render or abstain consistently?
```

Inputs must hold candidate generation and evidence fixed. Compare at least:

- deterministic/state-graph fixed candidates;
- LLM candidate-only output from Experiment A after evidence gating;
- a small manually normalized diagnostic state only when needed to separate
  projection ability from malformed input.

Primary metrics:

- projection correctness by hidden family;
- policy consistency across equivalent phrases;
- W->C and C->W against the frozen deterministic comparator;
- abstention/uncertainty precision;
- rendering-only error rate;
- first-failure owner when projection fails.

Projection-compatible clinical phrases should be credited at representation
time and evaluated here, not forced into candidate/evidence prompts.

## Experiment D: Paired-Task Overload

Question:

```text
What performance or representation quality is lost when the model is asked to
perform multiple subtasks in one prompt?
```

Only run this after Experiments A-C establish isolated-task baselines.

Compare on the same row panels:

- candidate only;
- evidence only;
- projection only;
- candidate plus evidence;
- evidence plus projection;
- candidate plus evidence plus projection.

Primary metrics:

- task-specific delta from the isolated-task ceiling;
- ambiguity preservation loss;
- unsupported fact rate;
- projection consistency loss;
- final label correctness as a secondary readout;
- row-level examples where downstream awareness helps or prematurely collapses
  a clinically faithful representation.

## Representation Comparison

For each experiment, record which representation was used:

- free-text candidate list;
- minimal evidence tuple;
- selected-fact schema;
- claim table;
- state graph node;
- richer typed state with explicit currentness, denominator, cluster,
  uncertainty, and seizure-free fields.

The RQ3 schema question should not proceed until this protocol reports whether
schema failures are model capability limits, prompt overload, or representation
shape problems observed under fixed task conditions.

## Artifact Contract

Each run must produce a machine-readable artifact with one row per source row,
condition, component decision, and candidate/evidence/projection object. Include:

- `source_row_index`, split, distribution, row-panel id;
- prompt name, prompt version, model id, decoding parameters;
- component task and representation type;
- exact evidence/source-id status;
- component output fields;
- deterministic comparator label and correctness where relevant;
- gold label and gold kind;
- hidden-family tags;
- component metric fields;
- first-failure owner;
- row-level notes for wins, losses, ambiguity, and not-judged cases.

The Markdown report is secondary to the JSONL/CSV matrix.

## Stop Rules

This protocol is answered for validation development when the report can state:

- the isolated candidate-generation ceiling and its burden/metadata trade-off;
- the isolated evidence-selection ceiling and whether errors are text-location
  or state/projection problems;
- the isolated projection ceiling over fixed evidence/candidates;
- whether paired prompts degrade, preserve, or improve each subtask relative to
  isolated baselines;
- which representation should be carried into RQ3 and why;
- which claims are validation-only and which require frozen stress or holdout
  audit before transfer language.

If the first validation50 control panel is ambiguous, do not expand to broad
validation750. Instead, refine instrumentation, adjudication labels, or hard
panels under this protocol.

## Immediate Next Actions

1. Materialize the balanced validation50 and hidden-family hard panels.
2. Write prompt/schema stubs for `candidate_only`, `gold_query_evidence_only`,
   `candidate_conditioned_evidence_only`, and `projection_only`.
3. Build the component-control matrix writer before running fresh calls.
4. Run validation50 controls, inspect row-level mechanisms, then decide whether
   a hard-panel run is needed.
