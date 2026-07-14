# Gan 2026 Component Evidence Audit Runbook

Last updated: 2026-06-03

## Purpose

Use this runbook before promoting a Gan 2026 candidate, comparing architectures,
or deciding whether an LLM decision is more robust than deterministic rules.

The output should answer three questions:

1. Which component solved each clinical subproblem, under which evidence gate,
   with what regression risk, and on which distribution?
2. Which LLM-owned clinical decisions beat deterministic rules under
   exact-evidence and no-regression constraints?
3. When the LLM changes the deterministic answer, how often is the change
   correct?

## Inputs

Required:

- Candidate artifact JSONL or saved-output replay source.
- Comparator artifact or deterministic safety-floor layer.
- Split/distribution name and split manifest.
- Score layer names to compare.
- Evidence fields or diagnostics proving exact selected evidence and valid
  source ids.

Recommended existing tools:

- `gan2026-atlas-hard-slice-diagnostic`
- `clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.rq9_router_pressure_points`
- `clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.rq9_abstention_pressure`
- `clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.llm_replacement_postprocessing_ablation`
- hidden-family atlas artifacts under `docs/research/` and `experiments/`

## Step 1: Freeze The Claim

Write down before running anything:

- candidate name;
- comparator name;
- distribution: validation prefix, validation hard slice, synthetic stress
  panel, or locked holdout audit;
- score layers;
- exact evidence gate;
- allowed deterministic adapter families;
- stop rule: promote, revise, or reject.

If the surface is locked holdout, stop unless the frozen-test audit plan has
already been followed exactly.

## Step 2: Build The Score-Layer Ladder

For each row, collect all available layers:

- deterministic comparator or safety floor;
- raw model clinical selection;
- deterministic adapter layer;
- graph projection or sidecar layer;
- final policy layer.

Do not collapse layers into a single final answer. If a layer is unavailable,
record that as an instrumentation gap.

## Step 3: Assign Clinical Subproblem Ownership

Map row-level diagnostics to the subproblem taxonomy in
`docs/design/component_evidence_attribution_architecture.md`:

- candidate generation;
- evidence selection;
- temporal selection;
- seizure-free boundary;
- rate denominator;
- cluster or diary aggregation;
- competing event selection;
- uncertainty boundary;
- adapter rendering;
- benchmark formatting.

Ownership is by decision effect:

- if the LLM selected the clinical fact and evidence, credit
  `llm_clinical_selection`;
- if deterministic code rendered from model-selected operands, credit
  `deterministic_adapter`;
- if deterministic code selected among competing facts, credit
  `graph_projection`, `deterministic_rule`, or `safety_floor`, and classify the
  row as hybrid for that subproblem.

## Step 4: Apply Evidence And Regression Gates

At minimum, report:

- exact selected evidence count;
- valid source id count;
- exact changed-row evidence count;
- selected operand completeness when adapters are used;
- deterministic-correct regressions;
- schema/parse failures;
- evidence invalid or missing rows.

Changed-row claims require all changed rows to have exact selected evidence
unless the report explicitly marks them diagnostic.

## Step 5: Compute LLM Delta Accounting

Against the deterministic comparator:

| Metric | Definition |
| --- | --- |
| `changed` | Candidate label differs from comparator label. |
| `wrong_to_correct` | Comparator Purist-wrong, candidate Purist-correct. |
| `correct_to_wrong` | Comparator Purist-correct, candidate Purist-wrong. |
| `changed_label_precision` | `wrong_to_correct / changed`, reported only when changed rows are evidence-valid. |
| `net_gain` | `wrong_to_correct - correct_to_wrong`. |
| `deterministic_correct_regressions` | Comparator-correct rows made wrong by final policy or candidate layer. |

Also compute the same table by clinical subproblem and hidden family. The
overall result can look clean while a single clinically meaningful family is
unsafe.

## Step 6: Interpret LLM-Superiority Claims

An LLM decision can be described as more robust than deterministic rules only
when all are true:

- the LLM owns the clinical selection being credited;
- selected evidence is exact or the predeclared source-near gate is met;
- deterministic adapters are mechanical and traceable to model-selected
  operands;
- deterministic-correct regressions are zero or explicitly accepted by a
  predeclared tradeoff;
- the distribution is named;
- the improvement survives subproblem and hidden-family breakdowns.

If deterministic projection, safety floor, or benchmark-format repair made the
prediction-bearing clinical decision, call the result hybrid or diagnostic.

## Step 7: Write The Report

A promotion report should include:

- candidate and comparator metadata;
- distribution and split manifest;
- score-layer ladder;
- component evidence matrix;
- LLM delta table overall and by clinical subproblem;
- evidence validity table;
- regression-risk table;
- hidden-family and first-failure-owner breakdown;
- claim language and next action.

Use this claim-language template:

```text
On <distribution> under <split_manifest>, <candidate> is a <family> result.
It improves <comparator> by <net_gain> Purist rows through <component_owner>
decisions on <subproblem(s)>. Changed rows had <exact_changed>/<changed> exact
evidence and <valid_source>/<changed> valid source ids. Correct-to-wrong changes:
<n>. Deterministic-correct regressions: <n>. This supports <claim>; it does not
support <excluded_claim>.
```

## Step 8: Update Project Control

After a meaningful audit:

- write or link the report in `experiments/` or `docs/research/`;
- update `experiments/registry.jsonl` if the run is retained and registry-backed;
- update `PROJECT_STATUS.md` with the next action and claim caveat;
- avoid locked-test language unless the frozen-test protocol was followed.
