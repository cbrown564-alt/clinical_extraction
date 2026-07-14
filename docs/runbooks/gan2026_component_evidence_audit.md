# Auditing which Gan component changed a result

Last updated: 2026-07-14

Use this procedure before adopting a Gan method, comparing methods, or claiming
that a model decision outperforms deterministic rules.

## Required inputs

- candidate JSONL or a saved-output replay;
- comparison JSONL or rules-based result;
- data split and split version;
- output steps to compare;
- fields that prove selected evidence and source identifiers are valid.

## Procedure

1. Before running, record the candidate, comparison, data, output steps,
   evidence requirement, allowed deterministic formatting, and stop rule. Stop
   if locked holdout rules have not been satisfied.
2. Preserve each available output: rules comparison, raw model decision,
   deterministic formatting, later clinical selection, and final answer. Record
   missing instrumentation instead of merging the steps.
3. Assign each decision to a clinical subproblem from
   [component attribution](../design/component_evidence_attribution_architecture.md).
   Credit the component that changed clinical meaning.
4. Count exact selected evidence, valid source IDs, complete operands,
   rules-correct regressions, parse failures, and missing evidence.
5. Compare the candidate with rules: changed rows, wrong-to-correct,
   correct-to-wrong, net gain, and model-change precision. Repeat by clinical
   subproblem and clinically meaningful case type.
6. Describe a model decision as better only when the model owns the clinical
   selection, evidence satisfies the stated rule, deterministic calculation is
   traceable to model-selected operands, regressions are zero or explicitly
   accepted, and the effect survives the named case breakdown.

## Report

State the candidate and comparison; split and version; each output step; results
by component and clinical subproblem; model changes; evidence status;
regressions; first failure; permitted claim; excluded claim; and next action.

After a meaningful audit, update the selected report or run record first, then
update `PROJECT_STATUS.md`. Never use holdout language unless the holdout
protocol was followed.
