# Gan 2026 Hybrid Adjudicator V0.2 Saturated-Surface Evaluation Plan

Date: 2026-06-01

This is a validation-development plan for `gan2026_split_v1`. It is not a
holdout result, benchmark claim, or permission to inspect locked-test rows.

## Decision Context

Hybrid rules-candidates LLM adjudicator v0.2 is output-contract clean but not
yet useful as a prediction-bearing selector on broad validation250. The
validation250 surface is saturated: deterministic top reached 246/250 Purist
and 246/250 Pragmatic, raw LLM adjudication reached 245/250 Purist and 246/250
Pragmatic, and conservative gated adjudication reached 244/250 Purist and
245/250 Pragmatic.

The label-change profile is the stronger rejection signal. Raw adjudication made
9 final-label changes with 1 deterministic-wrong to adjudicator-correct
transition and 2 deterministic-correct to adjudicator-wrong transitions. The
conservative gated final made 8 changes, 0 deterministic-wrong corrections, and
2 deterministic-correct regressions. The one useful raw correction was blocked
by the overreach gate.

The next experiment should not ask whether v0.2 can move an aggregate on another
easy prefix. It should ask whether LLM adjudication can make high-precision,
evidence-accountable selective actions on the deterministic stack's dominant
failure modes.

## Saturation Evidence

- Deterministic V1 validation: 0.9293 Purist and 0.9387 Pragmatic on 750
  validation rows.
- Deterministic V1 locked-test result: 0.7600 Purist and 0.7867 Pragmatic on
  the one frozen holdout evaluation.
- V0.2 validation250 deterministic top: 246/250 Purist and Pragmatic.
- V0.2 validation250 gated adjudicator: 244/250 Purist and 245/250 Pragmatic.
- V0.2 validation250 gated changes: 8 changed labels, 0 corrections, 2
  regressions.

This makes another broad validation250 or validation750 run low-information
unless it is tied to a predeclared hard-surface question.

## Hypothesis

V0.2 should be evaluated as a selective semantic reviewer before it is evaluated
as a universal final-label adjudicator.

The candidate is only promising if its high-confidence changes or flags
concentrate in known deterministic failure families:

- temporal selection and current-versus-historical conflict;
- seizure-free or no-event assertion overreach, especially after breakthrough
  events;
- `unknown` versus `no seizure frequency reference` boundary states;
- cluster cadence versus events-per-cluster burden;
- diary or distributed-count aggregation;
- compact Gan shorthand and interval/range expressions;
- candidate-set recall failures where the correct fact is present in the note
  but absent or weak in deterministic candidates.

## Surface 1: Synthetic Hard-Case Panel

Build a small, versioned generated panel before any hosted run:
`experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01.jsonl`.

Each row should include:

- `case_id`;
- `failure_family`;
- source note text;
- expected final label;
- expected answer kind: `frequency`, `unknown`, `no_reference`, or
  `seizure_free`;
- expected evidence substring;
- rationale for why deterministic V1 may fail;
- allowed LLM action: `change`, `flag_only`, or `abstain`.

Minimum panel shape:

| Family | Count | Purpose |
| --- | ---: | --- |
| temporal conflict | 8 | Current rate must beat historical or stale rate. |
| seizure-free boundary | 8 | Absence-of-events language must not erase later breakthrough seizures. |
| unknown/no-reference boundary | 8 | Seizure discussion without convertible frequency must become `unknown`; true absence of usable frequency remains `no seizure frequency reference`. |
| cluster dual-axis | 8 | Preserve cadence and per-cluster burden when both are stated. |
| diary/distributed counts | 8 | Month lists, recent windows, and cumulative counts should aggregate correctly. |
| shorthand/ranges | 8 | `q2-3wk`, inter-seizure intervals, ranges, and maximum burdens should normalize correctly. |
| proxy/distractor context | 8 | Medication, rescue use, safety status, falls, and non-epileptic-like events should not become seizure frequency unless explicit. |

Report deterministic top, raw LLM final, conservative gated final, and
flag-only mode on the same cases. Synthetic results are mechanism probes and
regression tests, not benchmark evidence.

Promotion signal from this surface:

- >= 0.80 changed-label precision on cases where `allowed_action=change`;
- no more than 1 deterministic-correct regression per family;
- exact evidence present for every accepted LLM change;
- rationales name the intended failure family rather than generic uncertainty.

Failure signal:

- frequent scorer-equivalent boundary churn without evidence-accountable
  correction;
- changes outside the deterministic dominant-error family under test;
- inability to abstain on proxy/distractor cases.

## Surface 2: Validation Hard Slices

Create reproducible validation slices aligned to deterministic dominant errors:
`experiments/gan2026_hybrid_adjudicator_v02_validation_hard_slices_2026-06-01.json`.

Slice membership should be generated from validation rows only, using existing
gold metadata, deterministic outputs, ablation deltas, and predeclared textual
triggers. Do not use locked-test rows.

Recommended slices:

| Slice | Membership rule | Primary metric |
| --- | --- | --- |
| deterministic_miss | Deterministic top wrong on validation; gold row is `row_ok=True`. | Wrong-to-correct rate and evidence validity. |
| temporal_conflict | Text has current and historical frequency/date language or deterministic temporal-selection ablation changes the row. | Regression-controlled correction rate. |
| seizure_free_overreach | Deterministic predicts seizure-free/no-event and gold is a rate or unknown, or text contains seizure-free plus breakthrough/event language. | Overreach correction precision. |
| unknown_no_reference_boundary | Deterministic predicts `no seizure frequency reference` while text has seizure/event discussion, or LLM v0.2 changed no-reference to unknown. | Flag precision and scorer-equivalent churn. |
| cluster_or_diary | Gold or text contains cluster, diary, month-list, or distributed-count signals; include rows affected by cluster/diary ablations. | Hard-slice F1 plus correction precision. |
| shorthand_interval_range | Text contains `q`, every-interval, inter-seizure interval, range, or maximum-burden language; include rows affected by shorthand/rate-expression ablations. | Format-normalization correction precision. |
| candidate_absent_or_weak | Deterministic top wrong and candidate-recall oracle indicates no correct candidate or only a weak/header-like candidate. | Flag-only utility, not final-label promotion. |

Each slice artifact should record row ids, reproducible trigger fields, and the
frozen code version used to derive membership. The report should include:

- row count by slice;
- deterministic top Purist/Pragmatic;
- raw LLM and gated final Purist/Pragmatic;
- number of changed labels;
- deterministic-wrong to LLM-correct transitions;
- deterministic-correct to LLM-wrong transitions;
- scorer-equivalent boundary substitutions;
- abstention/fallback rate;
- exact-evidence validity for every proposed LLM action;
- three to five validation examples per slice for development review.

Promotion signal from this surface:

- changed-label precision >= 0.67 overall and >= 0.75 in at least two dominant
  deterministic-miss slices;
- correct-to-wrong regressions no more than one-third of wrong-to-correct
  transitions;
- evidence validity >= 0.98 for accepted changes;
- the adjudicator improves at least one predeclared hard slice without reducing
  broad validation250 replay below deterministic top by more than 1 row.

Failure signal:

- boundary substitutions dominate changed labels;
- correct-to-wrong transitions remain comparable to or greater than
  wrong-to-correct transitions;
- useful changes require post-hoc gate edits or row-level prompt tuning.

## Surface 3: Selective-Action Metrics

Evaluate v0.2 as three outputs, not one:

1. `raw_change`: the raw LLM final label replaces deterministic top.
2. `gated_change`: conservative gates allow the LLM label to replace
   deterministic top.
3. `flag_only`: deterministic top remains the prediction, but the LLM flags the
   row as suspicious for review.

Report these selective-action metrics on synthetic hard cases and validation
hard slices:

- action rate: changed or flagged rows / total rows;
- changed-label precision: changes that convert deterministic-wrong to correct
  / all non-equivalent changes;
- changed-label recall: deterministic misses corrected / deterministic misses
  in the slice;
- regression rate: deterministic-correct to LLM-wrong / deterministic-correct
  rows touched;
- scorer-equivalent churn: changes where Purist and Pragmatic correctness do
  not change, especially `unknown` versus `no seizure frequency reference`;
- abstention/fallback rate;
- evidence-valid action rate;
- confidence calibration by LLM confidence, failure family, gate reason, and
  inside/outside deterministic candidate set.

The adjudicator should be allowed to pass as `flag_only` even if it fails as
`gated_change`, but the claim language must then say it is a review triage
component rather than a prediction-bearing extractor.

## Surface 4: Component-Stress Ablation

Run the same hard panels through named conditions:

- deterministic top;
- deterministic candidate oracle/recall proxy where available;
- raw LLM adjudicator final;
- conservative gated final;
- flag-only triage;
- stricter evidence-required gate;
- inside-candidate-set-only gate;
- boundary-change-only disabled gate.

The ablation question is whether the model's useful signal survives stricter
accountability. If the stricter evidence or inside-candidate gates remove most
corrections, v0.2 remains diagnostic.

## Frozen Test Generalization Audit

A locked-test audit is allowed only after the following are frozen in writing:

- candidate name and version;
- prompt text and model identifier;
- deterministic comparator and candidate-generator version;
- parser, repair, scorer, and normalization policy;
- gate policy and allowed actions;
- synthetic panel definitions;
- validation hard-slice definitions;
- selective-action metric formulas;
- inspection policy;
- stop rule.

Allowed locked-test reads:

- aggregate Purist and Pragmatic;
- predeclared slice aggregates using slice definitions fixed without inspecting
  test row-level failures;
- selective-action summary metrics fixed before the run.

Do not inspect locked-test row-level failures during development. If row-level
test review is needed after the frozen audit, label it post-hoc final-evaluation
analysis and start any fix as a new validation-cycle candidate.

Proceed to frozen test only if validation hard slices show either:

- high-precision prediction-bearing changes: changed-label precision >= 0.67,
  regression rate <= 0.33 of useful corrections, and evidence validity >= 0.98;
  or
- high-precision flag-only triage: flag precision >= 0.75 for deterministic
  misses on at least two dominant hard slices, with no final-label replacement
  claim.

## Stop Rules

Promote as prediction-bearing only if v0.2 makes high-precision,
evidence-valid changes on dominant deterministic failure families and its
regression cost is clearly lower than its correction gain.

Promote as flag-only triage if it reliably identifies deterministic misses but
does not meet final-label replacement thresholds.

Revise if the LLM shows real family-specific signal but gates suppress useful
corrections or allow preventable regressions.

Reject as added complexity if changed-label precision stays low, boundary churn
dominates, or hard-slice behavior is not better than deterministic top plus
manual error review.

## Immediate Implementation Tasks

1. Add JSON/JSONL schemas for synthetic hard cases and validation hard-slice
   membership.
2. Build a validation-only slice generator that records row ids and trigger
   provenance.
3. Add a selective-action report over existing v0.2 JSONL artifacts before
   running new hosted calls.
4. Draft the synthetic hard-case panel and review labels/rationales before
   using it as a regression surface.
5. Run component-stress ablations over hard panels only after the reports can
   separate `raw_change`, `gated_change`, and `flag_only`.

## Source Artifacts

- `PROJECT_STATUS.md`
- `docs/design/gan2026_split_protocol.md`
- `docs/design/gan2026_saturated_validation_protocol.md`
- `experiments/gan2026_v1_deterministic_baseline_2026-05-31.md`
- `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.md`
- `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_live_component_ablation_2026-06-01.md`
- `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_audit_trail_interpretation_2026-06-01.md`
