# Gan 2026 RQ3 Rich Selected-State Protocol

Date: 2026-06-04

Status: pre-run validation-development protocol and implementation scaffold.

## Question

Can LLM-selected candidate/evidence facts be carried into one typed selected
state with explicit currentness, conditionality, cluster burden, rate time
basis, seizure-free boundary, and ambiguity fields, then rendered by a
deterministic projection policy without losing the clinical state?

This is not an F1 experiment. The primary question is whether the representation
preserves the facts needed for deterministic projection.

## Motivation

The RQ1/RQ2 component-control matrix showed:

- candidate-conditioned evidence is the strongest LLM-owned primitive;
- broad evidence selection is useful when candidate coverage is uncertain;
- candidate generation has selective rescue value;
- direct LLM projection is unsafe;
- full candidate/evidence/projection bundling causes overload.

The five-letter walkthrough identified the missing bridge: selected facts need a
typed state before projection. Exact evidence alone is not enough, because exact
evidence for the wrong boundary can still produce seizure-free overreach,
unknown/no-reference collapse, or unresolved-multiple rendering failure.

## Fixed Surface

Initial development surface:

- split: validation only;
- manifest: `gan2026_split_v1`;
- rows: the five walkthrough rows first, then the completed RQ1/RQ2 hard-panel
  rows if the focused pass is coherent;
- model: one primary model per run, recorded in metadata;
- deterministic comparator role: fixed substrate/safety floor only;
- no locked-test row-level inspection.

Focused rows:

| Row | Mechanism |
| ---: | --- |
| 10 | ordinary quantified rate with cluster context |
| 280 | unresolved multiple-per-day benchmark convention |
| 3356 | conditional events versus seizure-free overreach |
| 10618 | cluster burden with seizure-free distractor |
| 2748 | current summary versus derived year-rate |

## Component Under Test

New surface:
`llm_only_rich_selected_state_reasoner`

Implemented in:
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_rich_selected_state_reasoner.py`

The model owns:

- selecting one clinical state;
- copying exact selected evidence;
- filling typed fields for currentness, assertion status, rate details, cluster
  details, seizure-free boundary, conditionality, ambiguity, and competing
  states.

Deterministic code owns:

- source/evidence validation;
- boundary consistency validation;
- final Gan-compatible rendering through
  `deterministic_project_selected_state`;
- any future projection policy additions.

## What Good Means

Good is not final F1. A row is useful when it satisfies the component contract:

1. `selected_evidence` is an exact note substring.
2. `raw_source_phrase` is contained in `selected_evidence`.
3. Currentness is explicit.
4. Conditional events are not rendered as seizure freedom.
5. Cluster burden is preserved even when cluster cadence is unknown.
6. Multiple-event wording is preserved without inventing a numeric count.
7. Seizure-free claims specify whether they apply to all seizure types and
   whether recent events or conditions block them.
8. The deterministic renderer can either emit a safe Gan-compatible label or
   intentionally return `unknown`/`no seizure frequency reference`.

## Initial Deterministic Rendering Policies

The scaffold implements these first policies:

- multiple events with known time unit -> `multiple per <unit>`;
- cluster burden without cadence -> `unknown, <count/range> per cluster`;
- conditional state without rate basis -> `unknown`;
- seizure-free state with recent events or conditional blockers -> `unknown`;
- seizure-free state applying to all seizure types and with duration ->
  `seizure free for <duration> <unit>`;
- ordinary rate with count and time unit -> `<count/range> per <unit>`.

These policies are intentionally narrow. They should be expanded only after a
row-level error analysis names the missing field or boundary.

## Metrics

Primary component metrics:

- schema-valid selected states;
- exact selected evidence;
- selected-state trace validity;
- boundary validation failures;
- deterministic-renderable rows;
- rows where deterministic rendering preserves the selected state;
- rows where rendering intentionally abstains to `unknown`.

Secondary readouts:

- comparison to gold label for orientation only;
- hidden-family behavior;
- candidate/evidence source lineage when the state came from an RQ1/RQ2 control
  row.

Do not use final F1 as the decision metric for this protocol.

## Stop Rule

The five-row focused pass is enough to proceed to a hard-panel run only if:

- all five rows produce schema-valid selected states;
- all selected evidence is exact;
- the renderer handles rows 280, 3356, 10618, and 2748 according to the intended
  boundary policies;
- failures are clearly attributable to missing typed fields rather than broad
  prompt confusion.

If this fails, revise the schema or field descriptions before any broader run.

## Current Implementation Status

Implemented and tested:

- rich selected-state Pydantic schema;
- plain-language model-facing payload builder;
- evidence/trace/boundary validation;
- deterministic selected-state renderer;
- focused unit tests for:
  - multiple-per-day convention;
  - conditional unknown;
  - cluster burden without cadence;
  - seizure-free blocker;
  - current monthly summary rendering;
  - prompt hygiene.

Verification:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_llm_only_rich_selected_state_reasoner.py tests/test_gan2026_llm_prompt_hygiene.py
```

Result on 2026-06-04: 27 passed.

## Next Action

Run a five-row live prompt pass for `llm_only_rich_selected_state_reasoner`.
Do not broaden to the hard panel until the five-row pass shows whether the
schema actually carries the facts needed for deterministic projection.
