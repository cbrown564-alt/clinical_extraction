# Gan 2026 Generalization-First Boundary And Benchmark Solution Design

Date: 2026-06-05

Status: research design note for the next hypothesis cycle. This is not a
benchmark-comparable claim and does not authorize locked-test row-level tuning.

## Position

The H1 aggregate readout should change the project strategy even though it does
not fully explain the validation-test gap. Seizure-free duration and benchmark
format convention have materially larger within-family gaps than the aggregate
surface:

- `seizure_free_duration`: validation 0.8960, test 0.6529, gap 0.2431.
- `benchmark_format_convention`: validation 0.9036, test 0.6667, gap 0.2369.
- overall selected surface: validation 0.9440, test 0.7800, gap 0.1640.

The right goal is not to preserve the highest validation score. A candidate that
drops validation from roughly 0.94 to 0.80 can still be a better research
candidate if it replaces brittle validation-fit behavior with source-grounded,
clinically coherent mechanisms that plausibly transfer and can be audited on a
frozen holdout.

## Research Control Principle

Accept validation-score sacrifice only when all of these are true:

- the change is predeclared before the readout;
- the mechanism is stated at the clinical-subproblem level;
- changed rows have exact evidence or a documented reason evidence is not
  applicable;
- deterministic benchmark-format behavior is separated from clinical semantic
  selection;
- regressions are concentrated in known benchmark-convention or underdetermined
  rows, not broad easy controls;
- the candidate improves synthetic/adversarial robustness or validation
  hard-slice mechanism metrics;
- any holdout readout is frozen and aggregate/predeclared-slice only.

Do not accept validation loss when it is caused by unclear ownership, missing
evidence, unbounded projection changes, vague prompt drift, or scorer-format
noise.

## Problem 1: Seizure-Free Duration

The core failure is not just rendering `seizure free for X month`. The system
must distinguish at least five source-near states:

| State | Meaning | Preferred action |
| --- | --- | --- |
| `asserted_seizure_free_interval` | The note explicitly states no seizures/events over a duration or since a date. | Candidate event with duration fields and exact evidence. |
| `last_event_only` | A last seizure date is stated, but no recurring frequency or explicit seizure-free assertion is given. | Preserve as last-event-only; project to seizure-free only under a frozen policy. |
| `conditional_or_trigger_only` | Events occur only with a trigger or in uncertain context. | Usually unknown or unresolved, not seizure-free. |
| `non_epileptic_current_events` | Current events are described as non-epileptic or not seizures. | Keep a separate non-epileptic evidence flag before mapping to Gan label. |
| `residual_seizure_activity` | Seizure-free claim coexists with current seizures of another type. | Select by semiology/task target; do not collapse to global seizure-free. |

### Proposed Mechanism

Build a typed `seizure_free_boundary_event_v0` component with explicit state and
projection ownership:

```text
{
  boundary_state:
    asserted_seizure_free_interval |
    last_event_only |
    conditional_or_trigger_only |
    non_epileptic_current_events |
    residual_seizure_activity |
    no_boundary_evidence,
  duration_text,
  duration_low,
  duration_high,
  duration_unit,
  last_event_date_text,
  anchor_date_text,
  applies_to,
  contradictory_current_event_evidence,
  evidence_text,
  evidence_exact,
  projection_policy
}
```

The component should not directly optimize final Gan label exactness. It should
first prove that it classifies the boundary state correctly on synthetic
minimal pairs and validation hard slices.

### Promotion Signals

- Boundary-state classification is stable across paraphrases.
- `last_event_only` is not automatically converted into seizure-free unless the
  projection policy says so explicitly.
- Non-epileptic current-event evidence is not confused with no-reference.
- Residual active semiology prevents global seizure-free projection.
- H6 controls and easy frequency controls are preserved.

## Problem 2: Benchmark Format Convention

Benchmark convention rows mix genuine clinical extraction with scorer-specific
formatting. Treating them as ordinary clinical mistakes causes overfitting.

Examples from the existing RQ10 audit include:

- unresolved cluster labels such as `1 cluster per 4 to 5 week, multiple per
  cluster`;
- last-event-only evidence where Gan gold may be `unknown` rather than
  seizure-free;
- non-epileptic current-event convention where Gan gold may prefer
  seizure-free over no-reference;
- vague `multiple` labels that collapse through Gan scorer sentinels.

### Proposed Mechanism

Build a separate `benchmark_convention_renderer_v0` that consumes typed clinical
events and emits two outputs:

1. `clinical_final_state`: the clinically meaningful state selected by the
   extraction system.
2. `gan_rendered_label`: the scorer-facing label under a named benchmark policy.

The renderer must never silently change clinical state. Every benchmark-only
change should be marked:

```text
benchmark_policy_id
benchmark_format_rule_id
clinical_state_preserved: true | false
format_only_change: true | false
scorer_sentinel_used: true | false
```

### Promotion Signals

- Format-only changes are distinguishable from clinical semantic changes.
- Cluster and vague-multiple rendering are deterministic and fixture-tested.
- Unknown/no-reference sentinel collapse is visible in artifacts.
- Benchmark-format wins are reported separately from clinical extraction wins.
- The mechanism may lower validation exact-label score if it avoids
  clinically incoherent convention chasing.

## Immediate Hypothesis Plan

### H3: Candidate Exposure

Question: does the system expose the right typed candidate before projection?

First panels:

- seizure-free duration versus last-event-only;
- seizure-free claim plus residual active semiology;
- non-epileptic current events versus no-reference;
- unresolved cluster burden with `multiple per cluster`;
- vague `multiple` frequency convention.

Metrics:

- gold-relevant typed candidate present;
- exact evidence present;
- unsupported candidate rate;
- metadata completeness;
- projection-ready fields present;
- clinical-state candidate versus Gan-rendered label disagreement.

### H7: Template Brittleness

Question: does a superficial wording or ordering change flip the mechanism?

Minimal-pair axes:

- "no seizures since January" versus "last seizure was in January";
- seizure-free statement before versus after a recent frequency statement;
- seizure-free for one semiology while another semiology remains active;
- non-epileptic events currently present versus no seizure-frequency reference;
- cluster cadence stated before versus after events-per-cluster burden;
- vague multiple count as gold convention versus clinically unresolved state.

Metrics:

- boundary-state consistency within pair;
- candidate-exposure consistency within pair;
- renderer-only differences versus clinical-state differences;
- H6 easy-control preservation.

## Recommended Architecture Direction

Prefer a typed event representation with explicit projection ownership over a
direct label switch layer.

The next candidate should look like:

```text
source note
  -> typed clinical events
  -> boundary and convention classifiers
  -> clinical final state
  -> benchmark renderer
  -> selective safety floor / abstain-review policy
```

This may reduce validation exact-label score because the candidate will stop
chasing some Gan-specific conventions as if they were clinical truth. That is
acceptable if the mechanism improves robustness on hard panels and creates a
clean frozen audit plan.

## Stop Rules

Reject the mechanism if:

- it changes clinical state inside the benchmark renderer;
- it releases last-event-only rows as seizure-free without an explicit policy;
- it hides unknown/no-reference sentinel collapse;
- it improves validation only through benchmark-specific label hacks;
- it damages H6 controls or easy current-frequency controls;
- changed rows lack exact evidence or projection-ready metadata.

## Next Action

Build a small H3/H7 seed panel for seizure-free duration and benchmark-format
convention. The panel should be synthetic or validation-only, include matched
controls, and score typed candidate exposure plus pair consistency before any
final-label promotion.
