# Gan 2026 Multi-Component Assembly Research Report

Date: 2026-06-05

Status: interim research report at pause point. This is not a benchmark-comparable
claim and does not close the active Purist F1 >= 0.9 locked-test goal.

Primary references:

- ``
- `experiments/gan2026_multi_component_assembly_experiment_log_2026-06-05.md`
- `PROJECT_STATUS.md`

## Executive Summary

The multi-component assembly program has made the system substantially more
auditable, but it has not yet produced a goal-achieving locked-test
architecture. The best frozen aggregate-only holdout result from this phase is
now `357/450 = 0.7933` Purist proxy, far below the requested >=0.9 target.

The central scientific finding is that validation is now saturated enough that
clean validation movement is weak evidence unless it is paired with a
generalization audit or a stronger mechanism-level explanation. Several
branches produced excellent validation W->C / C->W accounting, but transferred
poorly to the locked test because their accepted changes covered too few
holdout rows.

The most promising current validation branch is the retrieved train-exemplar
few-shot candidate generator with a narrow contract:

- current combined-switch validation baseline: `708/750 = 0.9440`;
- raw few-shot proposal: `552/750 = 0.7360`;
- contract-projected validation result: `726/750 = 0.9680`;
- contract transitions: `18 W->C`, `0 C->W`, `24 W->W`, `708 C->C`;
- contract selected rows: 23.

That branch has now been run as a frozen aggregate-only locked-test audit. It
transferred with high precision but negligible coverage: `4 W->C`, `0 C->W`,
and final `357/450 = 0.7933`. It is rejected as a goal-achieving branch. The
evidence points away from narrow switch layers and toward a typed candidate
contract or structured event architecture with broader prediction-bearing
coverage.

## Research Question

Can a modular, auditable hybrid architecture for Gan 2026 seizure-frequency
extraction combine deterministic state/evidence machinery, LLM-generated
candidates, and conservative change gates to reach Purist F1 >= 0.9 on the
locked test set without violating split discipline?

The current answer is: not yet. The work has identified useful components and
failure modes, but the architecture has not crossed the locked-test threshold.

## Evaluation Discipline

All development decisions in this phase used `gan2026_split_v1`:

| Split | Rows | Permitted use |
| --- | ---: | --- |
| train | 300 | Retrieval examples and optimizer-style support only |
| validation | 750 | Development, row-level error analysis, ablations, freeze decisions |
| test | 450 | Frozen aggregate-only audits; no row-level test failure inspection |

The locked-test audits in this phase were aggregate-only. The reports were
designed not to store test row ids, clinical text, raw model outputs, or
row-level failure details. Any candidate that failed on locked test was rejected
or recorded, then development returned to validation.

## Architecture Under Study

The program began with the staged assembly architecture described in the
end-to-end plan:

```text
hybrid staged candidate/evidence/state architecture with deterministic
projection, safety-floor action, and abstention/review policy
```

The architecture was intentionally not described as LLM-first. Deterministic
candidate extraction, state projection, selected-evidence handling, fallback
behavior, abstention/review policy, and benchmark-facing rendering remain
prediction-bearing components.

The later branches added two families of LLM use:

- LLMs as change-only adjudicators over already-generated alternatives.
- LLMs as candidate generators, either direct from the note or conditioned on
  retrieved train examples.

The most important architectural shift is that the final Gan label is treated
as the last projection of a richer decision process, not the only object the
system should represent.

## Major Experiment Families

### 1. Conservative Staged Assembly

The first assembled candidate joined existing full-validation surfaces:

- `hybrid_reasoner_replay`;
- `selective_safety_floor_gate_v0`;
- `rq9_selective_action_router_v3`.

The conservative decision layer predicted only when the router selected
`predict`; `abstain` and `human_review` remained non-predictions.

Validation result:

| Metric | Result |
| --- | ---: |
| rows | 750 |
| prediction-bearing rows | 716 |
| non-predictions | 34 |
| selective Purist accuracy over predicted rows | 0.9469 |
| selective Pragmatic accuracy over predicted rows | 0.9539 |
| verifier rows used | 0 |

This was useful as an auditable assembly surface, but not as a complete answer.
It preserved transparency and abstention discipline while leaving a large
full-row gap.

### 2. Residual Abstention And Release Policies

The 34 non-predictions were audited rather than blindly released:

- 26 abstain rows;
- 8 human-review rows;
- main review families: trigger-conditioned frequency, last-event boundary,
  and missing denominator anchor.

The trigger-context release policy found only one release candidate. The
promotion gate rejected it because it produced `0 W->C` and only a
category-correct-not-exact-label caveat. The last-event duration policy found
one duration-auditable row but zero automatic release-ready rows.

Lesson: the abstention surface was clinically meaningful, but release rules did
not create enough true W->C movement to matter. Keeping the non-prediction rows
honest was the right scientific choice.

### 3. Component Evidence Matrix

The component evidence matrix was materialized as a paper-facing and
debugging-facing artifact:

| Matrix property | Result |
| --- | ---: |
| rows | 750 |
| unique source rows | 750 |
| contract issues | 0 |
| prediction-bearing rows | 716 |
| non-predictions | 34 |
| selected-evidence exact false rows | 0 |
| selected-source-id missing rows | 0 |
| parse/evidence/schema issue rows | 0 |
| verifier rows used | 0 |

This is a real contribution even though it did not solve the metric target: the
architecture now exposes which component owns each action, which rows are
abstained, and which proposed releases remain non-promoted.

### 4. Candidate Recoverability And Selector Bottleneck

Failure recoverability over the conservative assembly showed validation
headroom:

| Quantity | Count |
| --- | ---: |
| conservative assembly W-failure rows | 53 |
| exact-label actionable alternatives | 16 |
| Purist-category actionable alternatives | 5 |
| semantic-state-only rows | 17 |
| no recalled candidate rows | 14 |
| exact-label oracle upper bound | 694/750 = 0.9253 |
| all-actionable oracle upper bound | 699/750 = 0.9320 |

The key result was not the oracle score itself. It was the separation of
candidate recall from candidate selection. The system often had plausible
alternatives, but non-gold selector predicates were either too narrow or
destructive.

### 5. Narrow Candidate-Union Branches

Several narrow branches were safe on validation but too low-coverage on locked
test:

| Branch | Validation result | Locked-test aggregate result | Interpretation |
| --- | ---: | ---: | --- |
| diary/log subset | `2 W->C`, `0 C->W`; projected `680/750 = 0.9067` on conservative surface | selected 0 rows; unchanged `342/450 = 0.7600` | safe but no holdout surface |
| structural guard | `21 W->C`, `0 C->W`; projected `699/750 = 0.9320` | `342 -> 343/450` | high precision, too low coverage |
| deterministic/state exact switch | `4 W->C`, `0 C->W` in validation reparse | `342 -> 350/450` | positive, still far from target |

These experiments taught the same lesson repeatedly: high precision on a small
validation family is not enough.

### 6. Change-Only LLM Selector

The change-only verifier family was designed to default to the current label
unless an alternative passed a strict switch gate.

The exact LLM-selector branch was clean on validation:

- eligible validation family: 281 rows;
- final validation family transitions: `7 W->C`, `0 C->W`, `14 W->W`,
  `260 C->C`;
- whole-validation staged proxy: `697/750 -> 704/750 = 0.9387`.

But the frozen aggregate-only test audit moved only:

- `342/450 = 0.7600` to `347/450 = 0.7711`;
- transitions: `7 W->C`, `2 C->W`, `34 W->W`, `118 C->C`;
- changed-label precision: 0.7778.

The combined change-only switch layer improved this slightly:

| Surface | Result |
| --- | ---: |
| validation | `697/750 -> 708/750 = 0.9440`; `11 W->C`, `0 C->W` |
| locked test | `342/450 -> 354/450 = 0.7867`; `13 W->C`, `1 C->W` |

This is the best frozen aggregate holdout movement from the switch-layer
family, but it remains far below the goal.

### 7. Direct-Labeler Candidate Generation

The direct GPT-4.1 labeler was tested as a new candidate source.

On a hard validation slice of unrecalled or semantic-state-only failures:

- calls OK: 31/31;
- direct correct rows: 21/31;
- transitions: `21 W->C`, `0 C->W`, `10 W->W`.

On current-correct controls:

- direct correct rows: 21/31;
- transitions: `21 C->C`, `10 C->W`.

Full validation confirmed the risk:

- raw direct correct rows: `405/750 = 0.5400`;
- direct replacement transitions: `26 W->C`, `329 C->W`.

The broad change-only verifier was also unsafe:

- panel transitions: `11 W->C`, `25 C->W`, `19 W->W`, `170 C->C`;
- projected full validation: `694/750 = 0.9253`;
- changed-label precision: 0.3056.

A targeted direct switch became validation-clean:

- selected rows: 20;
- transitions: `9 W->C`, `0 C->W`, `7 W->W`, `4 C->C`;
- validation projection: `708/750 -> 717/750 = 0.9560`.

But it transferred with negligible coverage:

- locked-test selected rows: 4;
- transitions: `1 W->C`, `0 C->W`;
- final holdout proxy: `354/450 = 0.7867`.

Lesson: direct generation is a useful source of new alternatives, but direct
labels are too noisy to be final predictions. The acceptance contract is the
hard part.

### 8. Retrieved Train-Exemplar Few-Shot Branch

The few-shot branch tested whether retrieved train examples could improve
candidate generation without using the locked test for tuning.

Nearest-neighbor label copying was rejected immediately:

- train examples: 300;
- validation rows: 750;
- nearest train-label validation proxy: `239/750 = 0.3187`.

Retrieval became useful only as LLM context. On a validation panel of all 42
combined-current misses plus 42 current-correct controls:

- current-correct rows: 42/84;
- candidate-correct rows: 61/84;
- transitions: `27 W->C`, `8 C->W`, `15 W->W`, `34 C->C`;
- exact evidence rows: 76/84.

The existing change-only verifier was not safe enough:

- exact-evidence differing alternatives: 49 rows;
- verifier transitions: `6 W->C`, `3 C->W`, `27 W->W`, `13 C->C`.

A few-shot-specific contract was then replayed over full validation:

| Metric | Result |
| --- | ---: |
| row count | 750 |
| current correct | 708/750 = 0.9440 |
| raw proposed correct | 552/750 = 0.7360 |
| contract projected correct | 726/750 = 0.9680 |
| contract selected rows | 23 |
| contract changed-label precision | 1.0000 |
| contract transitions | `18 W->C`, `0 C->W`, `24 W->W`, `708 C->C` |

Contract-selected families:

| Family | Count |
| --- | ---: |
| cluster per-cluster completion | 9 |
| daily upgrade from non-daily | 5 |
| explicit rate replacement | 3 |
| multiple-daily upgrade from single-daily | 1 |
| seizure-free current to unknown | 5 |

Frozen aggregate-only locked-test audit:

| Metric | Result |
| --- | ---: |
| frozen candidate | `gan2026_fewshot_train_exemplar_contract_v0` |
| model | `openai/gpt-4.1` |
| prompt version | `gan2026_fewshot_train_exemplar_direct_labeler_v0` |
| source artifact | `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl` |
| max tokens | 900 |
| verifier max tokens | 500 |
| raw base correct | 342/450 = 0.7600 |
| combined current correct | 353/450 = 0.7844 |
| final correct | 357/450 = 0.7933 |
| contract selected rows | 4 |
| contract transitions | `4 W->C`, `0 C->W`, `93 W->W`, `353 C->C` |
| contract changed-label precision | 1.0000 |
| few-shot call-ok rows | 448/450 |
| few-shot parse-ok rows | 158/450 |
| exact-evidence rows | 408/450 |

Artifact:
`experiments/gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit_2026-06-05.md`.
The audit wrote no test row ids, clinical text, raw model outputs, row-level
failures, or row-level diagnostics.

Interpretation: this is a clean but too-narrow transfer. The few-shot contract
is rejected as a goal-achieving branch. Its validation strength did not
generalize into enough locked-test prediction-bearing coverage.

## Cross-Experiment Findings

### Finding 1: Validation Is Saturated

The work repeatedly reached validation-clean or near-clean transitions, yet
locked-test transfer stayed weak. Once the validation baseline is in the
0.94-0.97 range, additional validation gains are often measuring compatibility
with known validation families rather than real generalization.

Implication: broad validation F1 should no longer be treated as the main
development signal. Hard-slice coverage, changed-label precision, family
coverage, robustness, and frozen aggregate audits are more informative.

### Finding 2: High Precision Gates Are Too Low-Coverage

The best test movement came from the combined switch layer:

- changed rows: 31/450;
- transitions: `13 W->C`, `1 C->W`;
- final score: `354/450 = 0.7867`.

That is a good component result but not enough. To reach 0.9 on 450 rows, the
system needs roughly 405 correct rows. Starting from the current 342-354 range,
the missing movement is on the order of 51-63 additional correct rows, not a
handful.

Implication: the architecture needs broader candidate-generation coverage or a
different final representation, not just stricter gates over small families.

### Finding 3: Raw LLM Replacement Is Unsafe

Both direct note-only generation and few-shot generation found many true
validation fixes, but raw replacement caused regressions:

- direct labeler full validation: `26 W->C`, `329 C->W`;
- few-shot hard/control panel: `27 W->C`, `8 C->W`.

Implication: LLM outputs are useful as candidates, not unguarded final labels.
The main design problem is an acceptance contract that can preserve broad W->C
coverage while blocking current-correct regressions.

### Finding 4: Evidence Exactness Is Necessary But Not Sufficient

Several unsafe branches had exact evidence. The failure is often not whether the
quoted span exists, but whether it should determine the current Gan label.

Examples of recurring reasoning traps:

- a historical seizure-free statement should not always become `unknown`;
- a partial window should not override a broader correct current label;
- a count for one semiology should not override a label for the overall seizure
  state;
- a cluster description may need per-cluster, per-day, or episode-level
  interpretation;
- a no-reference label may be benchmark-correct even when the note contains
  historical seizure language.

Implication: evidence checks need typed clinical decision contracts, not only
substring validation.

### Finding 5: Schema Repair Matters Operationally

The LLM branches exposed many parse and schema alias issues. Repairing
answer-kind and confidence aliases improved run viability without changing the
underlying clinical decision contract.

Implication: format repair is legitimate infrastructure, but semantic repair
must be named, ablated, and treated as prediction-bearing.

## Error Taxonomy

The dominant failure families are now clearer:

| Failure family | Why it matters | Observed lesson |
| --- | --- | --- |
| seizure-free recency and duration | Current seizure-free labels can be correct even when exact duration is not fully stated | Naive unknown overrides regress correct rows |
| no-reference vs unknown | Gan scoring distinguishes absence of frequency reference from unknown frequency | LLMs often over-read historical mentions |
| partial-window narrowing | A recent month/week/count can be less appropriate than the broader current state | Direct labelers over-select local counts |
| clusters and per-cluster rates | Cluster phrasing can imply event counts, rates, or episode groupings | Some W->C movement exists, but selection must be typed |
| daily/multiple-daily upgrades | LLM candidates can detect stronger daily burden | Narrow contract can recover these safely |
| diary/log aggregation | Deterministic extraction can be precise | Too rare on locked holdout to solve target |
| semantic-state-only recall | Candidate systems may know the state but fail final projection | Requires structured intermediate representation |

## What We Have Learned About The Architecture

The architecture needs three separable capabilities:

1. Broad candidate recall across the actual holdout distribution.
2. A typed acceptance contract that can decide when a candidate should replace
   the current label.
3. Transparent projection into Gan labels with evidence, source ids, and
   component ownership preserved.

The current system has made strong progress on item 3 and partial progress on
item 2. Item 1 remains the largest obstacle. The few-shot train-exemplar branch
attacked candidate recall directly, but the frozen holdout audit showed that
the accepted-contract coverage is still far too narrow.

## Current Best Evidence

| Candidate or branch | Validation evidence | Locked-test evidence | Decision |
| --- | ---: | ---: | --- |
| conservative staged assembly | 716 predict / 34 nonprediction; selective Purist 0.9469 | router packaging diagnostic near 0.7600 | transparent substrate, not enough |
| structural guard | `21 W->C`, `0 C->W`; projected 0.9320 | `342 -> 343/450` | safe but too narrow |
| exact LLM-selector verifier | `697 -> 704/750` | `342 -> 347/450` | positive but too small |
| combined switch layer | `697 -> 708/750` | `342 -> 354/450` | best holdout movement, not goal-achieving |
| targeted direct switch | `708 -> 717/750` | final `354/450` | safe but low coverage |
| few-shot train-exemplar contract | `708 -> 726/750`; `18 W->C`, `0 C->W` | `353 -> 357/450`; `4 W->C`, `0 C->W` | clean but too narrow; reject as goal-achieving |

## Research Claims Supported So Far

The work supports these cautious claims:

- A componentized seizure-frequency architecture can expose evidence, action
  policy, abstention, verifier use, candidate provenance, and transition
  accounting in a way that is much more inspectable than a final-label-only
  system.
- Deterministic rules remain valuable as controlled variables, safety floors,
  and candidate sources, even when they do not generalize enough alone.
- LLMs are useful for candidate generation and adjudication, but raw LLM final
  labels are unsafe under Gan Purist scoring.
- Change-only framing reduces regression risk, but narrow accepted-change
  families do not supply enough locked-test coverage.
- Retrieved train exemplars improve validation hard-slice candidate generation,
  but the frozen accepted-contract holdout coverage is too narrow to reach the
  locked-test target.

The work does not yet support these claims:

- The architecture reaches Purist F1 >= 0.9 on locked test.
- The few-shot contract generalizes enough to reach the locked holdout target.
- Any current LLM branch is a clean LLM-first solution.
- Validation F1 above 0.95 is by itself evidence of benchmark-level success.

## Recommended Resume Plan

When the experiment loop resumes, the next steps should be:

1. Treat `gan2026_fewshot_train_exemplar_contract_v0` as rejected for the
   >=0.9 locked-test goal despite clean changed-label precision.
2. Pivot to a typed candidate contract or structured event architecture that
   raises prediction-bearing coverage, not another narrow switch family.
3. Predeclare explicit coverage targets before any new frozen audit: candidate
   generation should cover at least 150 holdout-like prediction-bearing rows on
   validation hard/control surfaces, accepted changes should target at least
   60 validation W->C opportunities with <=5% C->W on matched controls, and
   parse/evidence contracts should reach >=95% parse-ok and exact-evidence
   rows on validation before holdout use.
4. Keep the locked test aggregate-only. Any new candidate must freeze code,
   prompt, model, scorer, token limits, source artifacts, inspection policy,
   and coverage targets before another holdout audit.

The key stop rule remains unchanged: do not tune from locked-test row-level
failures. A failed aggregate audit is a distribution-level finding, not a
debugging dataset.

## Bottom Line

This phase has not solved the benchmark target, but it has sharply narrowed the
problem. The repo now has a disciplined assembly substrate, component evidence
matrix, switch-layer accounting, direct and few-shot candidate-generation
evidence, and a much clearer map of the regression traps.

The strongest current hypothesis is:

```text
The path to >=0.9 locked-test Purist F1 is not another narrow high-precision
switch, but a broader candidate generator paired with a typed, evidence-grounded
acceptance contract.
```

The few-shot train-exemplar contract was the first serious version of that
hypothesis. Its frozen aggregate audit was clean but far too low-coverage, so
the next version needs a typed candidate contract or structured event layer with
explicit coverage targets before another holdout use.
