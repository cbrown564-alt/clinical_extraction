---
name: gan2026-experiment-loop
description: Run disciplined Gan 2026 seizure-frequency experiments in the clinical-extraction repo. Use when proposing, implementing, evaluating, comparing, recording, or interpreting deterministic baselines, DSPy or LLM pipelines, prompt changes, post-processing repair, ablations, notebooks, error-analysis views, threshold goals, or run artifacts.
---

# Gan 2026 Experiment Loop

Use this skill to make each experiment teach something. State the hypothesis, preserve the evaluation surface, run the harness, inspect errors, and record enough metadata to compare later.

## Environment

Use the `clinical-extraction-env` skill before every experiment command, Python
snippet, notebook command, test run, or scoring run. Experiments must use the
repo `.venv` and the editable package install, not system Python.

## Required Context

Read the relevant current docs before changing experiment behavior:

- `PROJECT_STATUS.md`
- `docs/research/contribution_thesis.md`
- `docs/design/data_contract.md`
- `docs/design/gan2026_split_protocol.md`
- `docs/design/gan2026_saturated_validation_protocol.md` when a comparator or
  candidate is near ceiling on validation or known to have a validation/test gap
- `docs/design/gan2026_pipeline_v1.md`
- `docs/runbooks/gan2026_first_milestone.md`
- `experiments/README.md`

## Workflow

1. Classify the work: data/scoring parity, deterministic baseline, DSPy module, hybrid pipeline, ablation, error analysis, or notebook/reporting.
2. State the experiment unit before implementation:
   - Hypothesis
   - Minimal code/prompt change
   - Data surface and row policy
   - Scorer and metric, defaulting to Gan-compatible Purist F1 until policy changes
   - Expected failure mode or learning value
   - Rule categories affected, when deterministic behavior changes
   - Component ablation needed to support the interpretation
3. Use the locked split manifest for Gan work:
   - Default to `validation` for deterministic-rule iteration, prompt strategy comparisons, ablations, row-level error analysis, and model-choice decisions.
   - Use `train` only for DSPy GEPA or another optimizer that needs training examples.
   - Use `test` only after candidate code, prompts, model identifiers, scorer, and manifest version are frozen.
   - Do not tune prompts, rules, thresholds, normalization, model choice, or repair logic from test performance or test row-level failures.
4. Check for saturated validation before choosing the next surface:
   - If deterministic top, baseline, or candidate is near ceiling on validation
     (roughly >=0.95 on the planned surface), or if the comparator is known to
     have a large validation/test drop, do not default to another broad
     validation250 aggregate.
   - Prefer synthetic hard-case panels, validation hard-slice panels,
     adversarial/paraphrase robustness, component-stress ablations,
     selective-action/calibration analysis, or a frozen test generalization
     audit with a predeclared inspection policy.
   - For hybrid adjudicators, ask whether changed labels are high-precision on
     the deterministic stack's dominant failure modes. Report changed-label
     precision, wrong-to-correct, correct-to-wrong, fallback/abstention, and
     hard-slice performance.
   - A saturated validation aggregate can be run only with a written targeted
     learning goal, named failure mode, comparator, surface, inspection policy,
     and stop rule.
5. Run focused tests during implementation inside `.venv`.
6. Run the evaluation command or notebook cell inside `.venv` to produce comparable metrics.
7. Inspect row-level failures on development surfaces, not only aggregate F1.
8. Save meaningful run artifacts under `experiments/` with metadata when a run is worth comparing later.
9. Update `PROJECT_STATUS.md` or `docs/kanban.md` when priorities, blockers, or promoted direction changes.
10. End with an interpretation: promote, reject, revise, or keep as diagnostic.

## LLM Attribution Gate

For any LLM-first, DSPy-first, or language-model threshold claim, architecture
validity is a hard gate before metric success. Do not promote a run, mark a
threshold goal complete, or describe a score as satisfying an LLM-first
objective until the prediction-bearing source is separated from deterministic
post-processing.

Treat a post-LLM change as a deterministic rule, not normalization, when it
changes semantic kind, Purist/Pragmatic category, selected event, sentinel state
(`unknown`, `no seizure frequency reference`, seizure-free/currently no
seizures), denominator/window policy, cluster interpretation, or benchmark-row
family behavior.

Before promoting an LLM/DSPy artifact, report these same-raw-output scores when
the artifact uses post-processing:

- Raw model-selected final label.
- Format-only repair: JSON/schema compatibility, allowed unit spelling,
  parser-compatible syntax, and arithmetic over an already selected fact.
- Selected-evidence repair only, if used.
- Full stack, with every semantic repair family named.

Also count repair-induced transitions:

- Rows changed by repair.
- Raw-wrong to final-correct changes.
- Raw-correct to final-wrong regressions.
- Purist/Pragmatic category changes.
- Exact normalized-label and semantic-kind changes.

If the metric threshold is reached only by a mixed-provenance artifact, no-call
reparse, or semantic repair stack, call it a hybrid development artifact and run
the attribution ablation before claiming the LLM-first objective is achieved.
An exact-threshold result after repair iteration increases audit priority.

## Experiment Record Minimum

For any saved run, capture:

- Date and git commit or working-tree note.
- Code/prompt change summary.
- Data path, subset policy, and row counts.
- Split name and split manifest version; use `gan2026_split_v1` unless a documented protocol change created a newer manifest.
- Scorer/mapping policy.
- Metrics: Purist F1 first, Pragmatic F1 as side-car when useful.
- Parse/evidence issue counts.
- Rule categories enabled or disabled.
- DSPy stages enabled or disabled.
- Top failure slices and a short interpretation.

## Guardrails

- Do not change evaluator, label mapping, or split policy to improve a candidate score unless the user explicitly requests a contract change.
- Do not run ordinary development experiments on all 1,500 Gan rows; use validation unless the task is explicitly split-policy work.
- Do not inspect test-set row-level errors during development. If a final test exposes a flaw, record it as a final-evaluation finding and start a new validation-cycle candidate.
- Treat local synthetic results as development or replication-proxy results until comparability is established.
- For DSPy or LLM runs, record model, dependency, prompt/program version, cost/latency when available, and call failure rate.
- Keep deterministic baselines as comparators for language-model changes.
- Keep Gan-specific rules distinguishable from general date, epilepsy, seizure-frequency, and benchmark-formatting rules.
- Do not let no-call replay become silent validation optimization. Split repair
  replay into permitted format repair and experimental semantic repair.
- Do not continue adding repair families after a broad-validation tail failure
  without first running a repair-family ablation or explicitly reclassifying the
  run as a hybrid deterministic-plus-LLM candidate.
- Do not keep using broad validation250 aggregates once the planned surface is
  saturated. Treat saturation as a prompt to test hard cases, hard slices,
  robustness, selective action, or frozen generalization.
