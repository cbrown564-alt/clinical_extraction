# Attributing changes to pipeline components

Last updated: 2026-07-14

Every method comparison must answer three questions:

1. Which component solved each clinical subproblem, on which data, and with
   which evidence restriction?
2. Which model decisions outperform the rules-only comparison without a later
   deterministic step replacing their clinical meaning?
3. When the model changes a rules-based answer, how often does it help or hurt?

## Required row record

Store one row per letter, clinical subproblem, component decision, and scored
output. The row must include:

- task, dataset, split definition, and inspected distribution;
- method (`rules_only`, `llm_only`, or `llm_with_rules`) and run ID;
- output step and the component that made the clinical decision;
- clinical subproblem and selected evidence;
- evidence status: exact, source-near, invalid, missing, or not applicable;
- comparison label, candidate label, and normalized gold label;
- whether each label is Purist-correct;
- whether the candidate changed the comparison answer;
- wrong-to-correct and correct-to-wrong flags;
- first component that made an incorrect result unrecoverable;
- clinically meaningful case tags.

## Clinical subproblems

| Name | Question |
| --- | --- |
| `candidate_generation` | Did the pipeline expose the clinically relevant state? |
| `evidence_selection` | Did it select evidence that supports the answer? |
| `temporal_selection` | Did it choose current rather than historical or planned information? |
| `seizure_free_boundary` | Did it distinguish seizure-free, unknown, and residual frequency? |
| `rate_denominator` | Did it identify the count, period, and unit? |
| `cluster_or_diary_aggregation` | Did it combine cluster or diary language correctly? |
| `competing_event_selection` | Did it choose the relevant seizure type? |
| `uncertainty_boundary` | Did it distinguish absent, possible, unknown, and asserted frequency? |
| `adapter_rendering` | Did it format an already selected fact for Gan? |
| `benchmark_formatting` | Did it apply a scoring convention without changing clinical meaning? |

Add a new name here before using it in a paper claim.

## Component ownership

Credit the component that made the clinical decision, not the module that ran
last. Distinguish deterministic clinical rules, model selection, mechanical
formatting, state selection, deterministic fallback, schema-only repair, and
benchmark-only formatting. If deterministic code chooses among competing facts
after a model call, classify that decision as LLM with rules.

## Evidence required for a claim

- Exact selected evidence supports a claim that the decision is grounded in
  the source note.
- Source-near evidence is diagnostic unless the study specified it in advance.
- Exact operands allow a deterministic calculation to be credited as mechanical.
- Replaying the same raw model output isolates the effect of later processing.
- A change policy may be considered safe only when it does not turn a
  rules-correct row into a wrong row on the named data.
- Model-change precision is interpretable only when every changed row has valid
  selected evidence.

Rows that fail these requirements may help debugging but cannot support a claim
that the model is better or that a method may become the new reference.

## Data scale and claim strength

| Data | Use |
| --- | --- |
| Training fixtures | Optimizer and implementation development only |
| 25-row validation sample | Schema, evidence, and severe-regression check |
| 250-row validation sample | Development decision |
| Full validation750 | Rare broad development comparison |
| Named hard cases | Component behavior after aggregate validation stops distinguishing methods |
| Synthetic cases | Controlled mechanism tests, not benchmark performance |
| Locked holdout | Final aggregate evidence under a fixed pre-run protocol |

## Required summary

Each comparison report must include results by clinical subproblem and owner;
scores after each processing step; model changes versus the rules comparison;
first failure by component and case type; evidence status; and a statement of
the split, model, replay mode, scorer, repair policy, and method.

Advance a method only when those records answer all three opening questions.
Otherwise add instrumentation, replay saved outputs, or test named hard cases.
