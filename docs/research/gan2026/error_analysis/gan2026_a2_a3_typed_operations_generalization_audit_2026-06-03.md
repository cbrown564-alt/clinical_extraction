# Gan 2026 A2/A3/Typed-Operations Generalization Audit

Date: `2026-06-03`

## Scope

This audit reviews `llm_only_sparse_operands_selected_state_reasoner` A2,
the proposed but not implemented A3 boundary-tags direction, and
`llm_only_typed_operations_reasoner` / `typed_operations_v0`.

It focuses on prompt wording, schema shape, deterministic adapter logic,
score-layer attribution, validation-ladder behavior, and row-level failure
families. It does not inspect or tune locked-test row failures.

## Verdict

Research drift is present in the simplified LLM-only lane. The code and reports
now correctly mark `typed_operations_v0` as paused, and `PROJECT_STATUS.md`
correctly records the A2 validation750 collapse. The failure mode is not mainly
schema validity, evidence exactness, or token budget. It is over-specific local
repair: prompt/schema/rule changes optimized against visible validation-prefix
and hand-built stress-panel failures, then generalized poorly when hidden
families appeared later in the validation split.

The short version:

- A2 learned the first 250 validation rows and the fixed stress panel better
  than it learned the task.
- A3 is not a runnable candidate; it exists only as a previously proposed
  boundary-tag idea. There is therefore no A3 evidence to promote, reject, or
  compare.
- `typed_operations_v0` failed for the same underlying reason in a deeper
  form: duplicated decision ownership let deterministic graph projection
  overrule correct selected-evidence outcomes.

## Primary Evidence

### A2 Validation Ladder

From existing artifacts:

| Surface | Selected-evidence arithmetic | Sparse operand adapter | Interpretation |
| --- | ---: | ---: | --- |
| validation25 replay | 23/25 | 23/25 | Smoke evidence only. |
| validation50 live | 47/50 | 48/50 | Strong prefix, but already shaped by boundary-deferral fixes. |
| validation250 live | 232/250 | 232/250 | Looked promotable but only covered the cleaner prefix. |
| validation750 live | 569/750 | 551/750 | Collapse: adapter under selected-evidence arithmetic. |

In the validation750 artifact, the first 250 rows still show 232/250
selected-evidence arithmetic and 231/250 sparse-adapter correctness. The later
500 rows drop to 337/500 selected-evidence arithmetic and 320/500 sparse-adapter
correctness.

Adapter transitions in validation750:

| Transition | First 250 | Later 500 | Total |
| --- | ---: | ---: | ---: |
| selected-evidence correct -> sparse adapter wrong | 5 | 32 | 37 |
| selected-evidence wrong -> sparse adapter correct | 4 | 15 | 19 |

This means the sparse adapter adds negative net value on the full surface,
despite looking stable on validation50 and validation250.

### A2 Failure Families

The validation750 misses concentrate in clinically meaningful hidden families:

| Bucket | First 250 misses | Later 500 misses | What it shows |
| --- | ---: | ---: | --- |
| Long month/year windows | 13 | 135 | The model binds period operands to the wrong window, often collapsing multi-month totals to per-month/year forms. |
| Unknown/no-reference boundary | 9 | 75 | The model selects or renders tempting numeric context despite sentinel/unknown gold states. |
| Unresolved multiple | 9 | 73 | "multiple/several/few" remains unstable under sparse numeric operands. |
| Seizure-free boundary | 4 | 66 | Seizure-free statements are selected over residual frequency or converted to concrete durations incorrectly. |
| Cluster | 3 | 45 | Cluster cadence and per-cluster burden remain confounded. |
| Compact/hour/shorthand | 11 | 47 | The blacklist catches known notations but misses broader unit-binding errors. |
| Trigger/proxy/medication context | 1 | 16 | Proxy frequencies and medication/rescue use leak into seizure-frequency labels. |

Representative A2 adapter regressions from validation750:

| Row | Gold | Selected-evidence layer | Sparse adapter | Failure |
| ---: | --- | --- | --- | --- |
| 212 | `1 per 3 to 4 week` | `1 per 3 to 4 week` | `3 to 4 per 1 week` | Interval count/window inversion. |
| 3681 | `9 per month` | `9 per month` | `9 per 3 month` | Wrong denominator binding. |
| 6180 | `multiple per week` | `multiple per week` | `3 to 7 per 1 week` | Unresolved multiple over-numericized. |
| 6209 | `multiple per day` | `multiple per day` | `2 to 3 per 1 month` | Wrong unit and over-numericization. |
| 9496 | `6 per 12 month` | `6 per 12 month` | `0 to 2 per 1 month` | Long-window total collapsed to local monthly operand. |
| 10677 | `1 cluster per month, multiple per cluster` | same | `1 per 1 month` | Cluster structure flattened. |
| 12823 | `9 per month` | `9 per month` | `9 per 1 year` | Period-unit drift. |

### A2 Prompt/Rule Smell

A2's prompt is now heavily corrective:

- exact evidence and one selected state;
- sparse operands only when directly stated;
- abstain for unsafe, proxy-only, historical, medication-use text;
- do not numericize vague `multiple`;
- keep cluster cadence separate from per-cluster seizure load;
- keep unknown/no-reference operands null.

Those are good clinical instructions, but the adapter then adds a local
blacklist: defer on `bimonthly`, menstrual/cyclical, `every other`, `q...`
shorthand, and hour or `/h` notation. This is the generalization failure in
miniature. The system is learning trap phrases from recent rows rather than
learning a portable permission rule such as "operands may render only when
count, denominator, and target state are all source-supported and not in a
boundary/trigger/sentinel state."

The tests mirror this local repair style. They protect rows like cluster cadence
without per-cluster load and unresolved `multiple`, but they do not test broad
window binding, long-window totals, period-unit drift, seizure-free versus
residual-frequency competition, or proxy/trigger leakage at scale.

### A3 Status

There is no implemented A3 candidate in the current repo. The only durable
reference found is the earlier status note saying A2 should not escalate until
boundary/permission logic is fixed or "A3 boundary tags" are tested.

Therefore:

- A3 has no prompt to review.
- A3 has no adapter implementation to audit.
- A3 has no validation artifact or score layer.
- A3 should be treated as an unimplemented hypothesis, not as evidence.

The useful A3 idea is still salvageable, but only if it is predeclared as a
new ablation: explicit boundary tags/permissions for rendering, measured
against A2 with the same raw selected-state outputs where possible. It should
not become another phrase blacklist.

### Typed Operations

`typed_operations_v0` was intended to expose transparent operations, operands,
selection, and a graph projection sidecar. The intention was sound: the LLM
would own clinical selection while deterministic code rendered mechanical
labels. The implementation overdid the schema:

- `operations` contains evidence, raw phrase, operands, temporality, assertion,
  certainty, and clinical label;
- `selection` repeats selected ids, state, evidence, strategy, and flags;
- `final_answer` repeats final label, selected evidence, selected ids, operands,
  and rationales.

This duplicates the same clinical decision across multiple fields. The graph
then builds nodes from operations and uses deterministic projection over those
nodes. On validation250:

| Layer | Purist |
| --- | ---: |
| selected-evidence arithmetic | 216/250 |
| typed-operation graph projection | 208/250 |

Transition table:

| Selected evidence | Graph projection | Rows |
| --- | --- | ---: |
| Correct | Correct | 201 |
| Correct | Wrong | 15 |
| Wrong | Correct | 7 |
| Wrong | Wrong | 27 |

The graph's net effect is -8 Purist rows. This is not a token-budget problem:
the max10000 run still had 3 parse/schema failures, 15 invalid selected-evidence
rows, one trace mismatch, and negative graph delta.

Typed-operation graph regressions cluster in the same families:

- unknown/unresolved state overwritten by numeric operands;
- hour-rate or compact-rate operands projected with wrong units;
- medication/rescue-use context converted into seizure frequency;
- competing selected operations where graph projection prefers a cleaner but
  clinically wrong numeric node;
- cluster windows quantified as stable rates.

Representative regressions:

| Row | Gold | Selected-evidence layer | Graph projection | Failure |
| ---: | --- | --- | --- | --- |
| 744 | `multiple per week` | `no seizure frequency reference` category-correct | `1 per 8 week` | Secondary tonic-clonic count overrides unresolved frequent absences. |
| 1317 | `unknown, multiple per cluster` | `unknown` | `2 per day` | One-day cluster quantified as stable daily rate. |
| 3482 | `unknown` | `unknown` | `1 per month` | Perimenstrual-only clustering treated as monthly frequency. |
| 4690 | `multiple per day` | category-correct sentinel | `10 per week` | Per-hour evidence projected with wrong unit. |
| 5476 | `unknown` | `unknown` | `1 per month` | Monthly rescue-medication use treated as seizure frequency. |
| 5551 | `multiple per day` | `multiple per day` | `1 per week` | Lower-burden competing event selected. |

## Root Causes

### 1. Prefix Surfaces Were Treated As More Representative Than They Were

A2 was called "decisive" after validation50 and "confirmed superior" after
validation250. The full validation750 later showed that the first 250 rows are
a cleaner subset for this schema. The validation ladder was followed
procedurally, but the interpretation did not sufficiently account for hidden
families in the later validation rows.

### 2. Stress Panels Became Local Patch Validators

The hard-slice panel was useful, but the post-fix conclusion overreached. A2
reached 100% on the panel because the panel matched recently named boundary
risks: row 187, row 278, row 190, row 280, `qtwo`, perimenstrual windows,
hour notation, and cluster cadence. Passing that panel showed those local
patches worked. It did not prove the permission model generalized.

### 3. Prompt Wording Became A Policy Patch Surface

The prompt now mixes clinical reasoning instructions with dataset-shaped
rendering examples and boundary warnings. This can reduce obvious errors on
known patterns, but it also asks the model to internalize a growing list of
exceptions. That is fragile for local LLMs and hidden validation subfamilies.

### 4. Deterministic Adapters Cross From Mechanical Rendering Into Semantic Rescue

A2 claims no graph projection, but `selected_evidence_arithmetic` and
`sparse_operand_adapter` are still prediction-bearing when they turn model text
or operands into the final scored label. In typed operations, graph projection
is explicitly a deterministic semantic sidecar. These layers must remain
separately ablated and should not be credited as clean LLM-only reasoning.

### 5. Duplicated Decision Ownership Creates Drift

Typed operations repeats selected evidence, ids, labels, operands, and state
across `operations`, `selection`, and `final_answer`. The graph can then select
among inconsistent traces. This makes the system look transparent while making
ownership less clear.

### 6. Existing Tests Are Too Example-Specific

The focused tests successfully prevent known regressions. They do not yet
encode the higher-level invariant: do not render numeric operands unless all
required semantic permissions are present and mutually consistent. The later
500 rows exploited exactly that gap.

## Recommendations

### Immediate Stop Rules

1. Do not escalate A2 as an LLM-only candidate.
2. Do not implement in-place A2 phrase blacklist patches for the validation750
   misses.
3. Do not revive `typed_operations_v0` with local graph repairs.
4. Do not call A3 a candidate until a runnable schema, prompt, tests, and
   predeclared evaluation plan exist.

### A3 Redesign Contract

If A3 is opened, it should be a boundary-permission schema, not A2 plus more
exceptions.

Required fields:

- one selected clinical state;
- exact selected evidence;
- source-near raw phrase;
- normalized clinical label proposal;
- sparse operands;
- explicit `render_permission` enum:
  `render_allowed`, `defer_uncertain`, `defer_boundary_state`,
  `defer_proxy_or_trigger`, `defer_competing_event`, `defer_cluster_ambiguous`;
- explicit `permission_evidence` copied from the selected evidence;
- no graph projection in the primary layer.

Promotion criterion:

- compare A2 and A3 on the same validation250/750 surfaces;
- report selected-evidence arithmetic separately from operand rendering;
- report selected-evidence-correct to adapter-wrong regressions;
- require net non-negative adapter delta before broader escalation;
- use hard slices for mechanism diagnosis, not promotion by themselves.

### Test Redesign

Add invariant tests and fixture panels for:

- long-window totals: `6 per 12 month`, `9 per 6 month`, `17 per 4 month`;
- period-unit binding: prevent `9 per month` -> `9 per year`;
- interval inversion: prevent `1 per 3 to 4 week` -> `3 to 4 per week`;
- unknown/no-reference with tempting numeric context;
- seizure-free statement competing with residual current frequency;
- rescue-medication/proxy use frequency;
- perimenstrual-only and illness/trigger-only windows;
- cluster cadence plus unknown/multiple per-cluster load;
- high-rate/hour evidence and compact notation with unit preservation.

Each test should assert not only final labels but also whether the adapter is
allowed to render from operands.

### Reporting Discipline

Future reports should avoid language like "decisive," "confirmed," or "ready
to escalate" from validation50 or a fixed stress panel. Use:

- validation25/50: contract and early-signal evidence;
- validation250: candidate revise/reject/promote-to-targeted-broader-validation;
- validation750: broad development result only if predeclared;
- locked test: frozen generalization audit only.

For A2-like lanes, every report should include:

- prefix versus later-slice breakdown;
- selected-evidence arithmetic vs operand-adapter transition table;
- correct-to-wrong adapter regressions by family;
- evidence-valid and trace-valid counts;
- claim language that states the result is not LLM-only if deterministic
  adapters make prediction-bearing semantic decisions.

## Restoration Plan

1. Keep `typed_operations_v0` paused.
2. Treat A2 as a useful sidecar source of selected evidence/operands, not as a
   standalone LLM-only candidate.
3. If pursuing A3, predeclare it as a permission-tag ablation with one decision
   owner and no graph projection primary layer.
4. Build a generalized hard-slice suite from validation750 failure families,
   not only the first 250-row misses.
5. Integrate any LLM-selected evidence signal into the hybrid safety-floor only
   under Decision 0008 component-evidence accounting: changed rows, exact
   evidence, deterministic-correct regressions, and first-failure owner.

## Residual Risk

This audit used existing validation artifacts and source code. It did not rerun
models and did not inspect locked-test failures. The family counts use lexical
failure tags over stored labels/evidence and should be treated as diagnostic,
not as a final taxonomy. A promotion-quality component matrix still needs a
dedicated implementation if A3 or an A2 sidecar is revived.
