# Gan 2026 Hybrid Parallel State Candidate Reasoner Test450 Generalisation Report

- Date: 2026-06-03
- Candidate: `hybrid_parallel_state_candidate_reasoner`
- Prompt/version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Model: `openai/gpt-4.1-mini`
- Split manifest: `gan2026_split_v1`
- Locked-test artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.md`
- Full-validation comparator: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.md`
- Prior hybrid comparators:
  - `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation750_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.md`
  - `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.md`
  - `experiments/gan2026_arch2_validation750_gpt41mini_v01_schema_replay2_2026-06-01.md`
  - `experiments/gan2026_architecture_validation250_component_ablation_2026-06-01.md`

This is a frozen locked-test generalisation audit. It is not a benchmark claim,
not an LLM-first claim, and not a basis for row-level test tuning. The allowed
readout here is aggregate/component behavior and predeclared comparison against
prior hybrid systems.

## Executive Summary

The frozen test run rejects the promoted validation interpretation as a
generalising hybrid improvement.

The validation750 safety-floor candidate reached `697/750` Purist (`0.9293`)
and `704/750` Pragmatic (`0.9387`). On locked test450 it reached only `343/450`
Purist (`0.7622`) and `354/450` Pragmatic (`0.7867`). The absolute
validation-test gap is therefore:

| Metric | Validation750 | Test450 | Absolute gap |
| --- | ---: | ---: | ---: |
| Purist | 697/750 = 0.9293 | 343/450 = 0.7622 | -0.1671 |
| Pragmatic | 704/750 = 0.9387 | 354/450 = 0.7867 | -0.1520 |

The result is especially sobering because the final safety-floor layer ties the
deterministic top candidate exactly on locked test:

| Test450 layer | Purist | Pragmatic |
| --- | ---: | ---: |
| `deterministic_top_candidate` | 343/450 = 0.7622 | 354/450 = 0.7867 |
| `hybrid_adjudicator_with_adapters` | 343/450 = 0.7622 | 354/450 = 0.7867 |
| `adapter_only_sidecar_from_adjudicator_selection` | 343/450 = 0.7622 | 354/450 = 0.7867 |

The deterministic safety floor did its narrow job: it prevented
deterministic-correct regressions. It did not create a generalising hybrid
extractor. The final prediction-bearing behavior is effectively the
deterministic top candidate under holdout pressure.

## Artifact Hygiene

The test artifact originally reported:

```text
Run gate outcome: validation250_development_result
```

That was a reporting-label bug caused by classifying run gates from row count
without preserving the split role. The corrected label is:

```text
Run gate outcome: locked_test_generalization_audit_result
```

The claim-language line in the saved test Markdown has also been corrected from
validation-development wording to frozen locked-test audit wording.

## Main Test Result

The test run had good output-contract and audit-trace behavior:

| Contract measure | Test450 result |
| --- | ---: |
| Structured LLM candidates | 443/450 |
| Structured adjudicator records | 450/450 |
| Parse/schema failures | 7 |
| Selected evidence exact | 450/450 |
| Selected source ids valid | 450/450 |
| Candidate-recall rescue rows | 0 |
| Graph-representability rescue rows | 11 |
| Deterministic-correct regressions | 0 |
| Adapter-changed rows | 1 |

These are strong audit numbers. They mean the failure is not primarily a broken
JSON, evidence-substring, or source-id problem. The failure is semantic
generalisation: the components are producing accountable answers, but the
answers do not match the locked-test clinical-state distribution.

## Layer Attribution

The layer table shows that no non-deterministic component is a reliable
prediction-bearing improvement on test450:

| Layer | Validation750 Purist | Test450 Purist | Test450 interpretation |
| --- | ---: | ---: | --- |
| `deterministic_top_candidate` | 697/750 = 0.9293 | 343/450 = 0.7622 | Transparent comparator and effective final floor. |
| `state_graph_projection` | 655/750 = 0.8733 | 333/450 = 0.7400 | Below deterministic on both full validation and test. |
| `llm_candidate_selector_raw` | 107/750 = 0.1427 | 75/450 = 0.1667 | Not scorer-compatible enough to be prediction-bearing. |
| `hybrid_adjudicator_raw` | 693/750 = 0.9240 | 342/450 = 0.7600 | Slightly below deterministic on test. |
| `hybrid_adjudicator_with_adapters` | 697/750 = 0.9293 | 343/450 = 0.7622 | Ties deterministic because of the safety floor. |

The LLM and graph components remain useful as diagnostics and trace sidecars.
They do not yet justify final-label ownership.

## Comparison With Previous Hybrid Systems

The current result continues the same validation-test pattern seen in earlier
hybrid families.

| System | Validation surface | Validation Purist | Test surface | Test Purist | Gap | Decision |
| --- | --- | ---: | --- | ---: | ---: | --- |
| Arch2 LLM adjudicator v0.1 | validation750 | 680/750 = 0.9067 | reported locked test | 342/450 = 0.7600 | -0.1467 | Diagnostic only. |
| Hybrid v0.2 `cluster_diary_candidate_recall` gated | validation750 | 677/750 = 0.9027 | test450 | 343/450 = 0.7622 | -0.1405 | Ties deterministic on test; no promotion. |
| Hybrid parallel reasoner conservative validation250 | validation250 | 245/250 = 0.9800 | test450 safety-floor | 343/450 = 0.7622 | -0.2178 | Validation250 was saturated and misleading. |
| Hybrid parallel reasoner safety-floor v2 | validation750 | 697/750 = 0.9293 | test450 | 343/450 = 0.7622 | -0.1671 | Reject as generalising hybrid improvement. |

The current system has the highest full-validation Purist score among these
hybrid adjudicator-style candidates, but that is because the final policy
reverts to the deterministic top candidate when needed. On locked test, that
same safety policy also caps the system at the deterministic top candidate.

## What Changed Relative To Hybrid V0.2

Hybrid v0.2 was an LLM adjudicator over deterministic candidates with
conservative overreach gates. On validation750 it scored `677/750` Purist
(`0.9027`), below deterministic top (`697/750`). On test450 it scored
`343/450` Purist (`0.7622`), exactly tying deterministic top, with `9`
wrong-to-correct and `9` correct-to-wrong changed-label transitions.

The parallel reasoner added independent LLM candidate extraction and a state
graph sidecar, then introduced a deterministic safety-floor final policy. That
improved validation safety:

| Variant | Validation750 deterministic regressions | Validation750 final Purist |
| --- | ---: | ---: |
| Hybrid v0.2 gated | 25 correct-to-wrong adjudicator changes | 677/750 = 0.9027 |
| Parallel reasoner safety-floor v2 | 0 deterministic-correct regressions | 697/750 = 0.9293 |

But on test it did not improve the prediction:

| Variant | Test450 final Purist | Test450 final Pragmatic | Net over deterministic |
| --- | ---: | ---: | ---: |
| Hybrid v0.2 gated | 343/450 = 0.7622 | 353/450 = 0.7844 | Purist tie, Pragmatic -1 row |
| Parallel reasoner safety-floor | 343/450 = 0.7622 | 354/450 = 0.7867 | Exact tie |

The safety floor is better engineering, but it is not better extraction.

## Mechanistic Interpretation

### 1. Validation saturation masked the true ceiling

The validation250 surface was especially saturated:

| Candidate/layer | Validation250 Purist |
| --- | ---: |
| Deterministic top | 246/250 = 0.9840 |
| Parallel reasoner with adapters | 245/250 = 0.9800 |
| Hybrid v0.2 gated | 244/250 = 0.9760 |

Those numbers gave little information about broad generalisation. A 250-row
validation prefix where deterministic top misses only four rows cannot
distinguish a robust hybrid from a high-variance system that mostly inherits an
easy comparator.

### 2. The safety floor converts the final layer into deterministic inheritance

The safety floor was introduced to prevent the adjudicator and adapter stack
from turning deterministic-correct rows into wrong final labels. It succeeded:
the test artifact reports zero deterministic-correct regressions.

However, the price is attribution. When the final policy bypasses or repairs
adjudicator disagreement back to deterministic top, the final score is no longer
evidence that the LLM adjudicator solved the hard rows. It is evidence that the
deterministic candidate remains the accountable prediction source.

### 3. The new components do not rescue the locked-test bottleneck

The test artifact reports:

- candidate-recall rescue rows: `0`;
- graph-representability rescue rows: `11`;
- state graph projection Purist: `333/450`;
- raw LLM candidate selector Purist: `75/450`;
- raw hybrid adjudicator Purist: `342/450`.

The graph can represent some rows missed by deterministic top, but its default
projection is not precise enough to improve the aggregate. The LLM candidate
selector is source-near but not scorer-compatible. The adjudicator is close to
deterministic but not better.

### 4. The validation-test gap is not an output-contract failure

Selected evidence and source IDs remain perfect on test. This makes the result
more valuable diagnostically: the audit trail is clean enough to trust the
failure. The system is not failing because it cannot emit a reportable answer;
it is failing because its clinical-state selection still inherits brittle
rules, broad deterministic candidate limits, and scorer-facing label
conversion errors.

### 5. Prior hybrid conclusions still hold

Earlier reports concluded that LLM adjudicators add semantic dissent and useful
review rationales, but not reliable final-label selection. This audit reinforces
that conclusion. The current architecture produces a cleaner trace and fewer
regressions, but it does not turn LLM dissent into high-precision correction.

## Claim-Language Assessment

Safe claims:

- The run is a frozen locked-test generalisation audit under `gan2026_split_v1`.
- The final safety-floor candidate scores `343/450` Purist and `354/450`
  Pragmatic on test450.
- The final safety-floor candidate ties deterministic top on both Purist and
  Pragmatic test metrics.
- The system preserves audit-grade selected evidence and source-id validity on
  test450.
- The safety floor prevents deterministic-correct regressions in this audit.
- The result is diagnostic evidence that the current hybrid additions do not
  generalise beyond deterministic top.

Unsafe claims:

- Do not call this a benchmark result.
- Do not describe it as an LLM-first or LLM-heavy success.
- Do not claim the parallel state graph or LLM candidate selector improves
  locked-test accuracy.
- Do not tune prompts, gates, adapters, rules, or repair policy from row-level
  locked-test failures.
- Do not cite validation250 performance as representative of expected holdout
  behavior.

## Decision

Reject the current `hybrid_parallel_state_candidate_reasoner` safety-floor
candidate as a promoted generalising hybrid extractor.

Keep it as a diagnostic and reporting baseline:

- It is the cleanest current demonstration that deterministic safety floors can
  preserve auditability and prevent regressions.
- It provides a useful component-stress artifact for state graph and LLM
  candidate sidecars.
- It should not be used as evidence that LLM/graph components improve final
  Gan 2026 extraction.

The next research step should not be another broad validation aggregate. The
useful next step is a validation-only selective-action or hard-slice design that
asks a narrower question: when, if ever, can an LLM or graph component make
high-precision changes on deterministic-top misses without damaging
deterministic-correct rows?

## Recommended Follow-Up

1. Freeze this audit as the current negative holdout result.
2. Keep `rules_only_v1`, hybrid v0.2, and this safety-floor candidate as
   comparators.
3. Build validation hard slices from known deterministic failure families:
   seizure-free boundary states, unknown versus no-reference, current versus
   historical conflict, cluster notation, vague recurrence, and multiple
   semiology burden.
4. Evaluate candidate components as selective actions rather than full final
   labels:
   - changed-label rate;
   - wrong-to-correct;
   - correct-to-wrong;
   - scorer-equivalent boundary substitutions;
   - evidence exactness for changed rows;
   - source-id validity for changed rows.
5. Promote a hybrid component only if it demonstrates high changed-label
   precision on validation hard slices before any future locked-test audit.

