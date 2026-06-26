# Gan 2026 Generalization Gap Research Report

Date: 2026-06-02

This is a research analysis over completed Gan 2026 artifacts in
`clinical-extraction`. It compares validation, locked-test, hard-case, and
component-ablation evidence across the major pipeline variants used so far:
rules-only V1, structured-events LLM, claim-table selectors, hybrid
rules-candidates adjudicators, and the named hybrid v0.2
`cluster_diary_candidate_recall` revision.

Locked-test policy: this report uses aggregate and slice-level locked-test
statistics only. It does not inspect locked-test note text or row-level failure
examples. Any future fix suggested here must start as a new validation-cycle
candidate.

2026-06-05 continuation: this report now feeds the frozen validation-test gap
program rather than another whole-pipeline iteration. The Phase 0 protocol,
artifact inventory, hypothesis registry, aggregate-only surface map, and first
validation-only gap matrix have been materialized:

- ``
- `experiments/gan2026_validation_test_gap_artifact_inventory_2026-06-05.json`
- `experiments/gan2026_validation_test_gap_hypothesis_registry_2026-06-05.json`
- `experiments/gan2026_validation_test_surface_map_v0_2026-06-05.md`
- `experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.md`

The first matrix is deliberately validation row-level only. It expands the
staged assembly component seed into 1,534 score-layer rows: 750 deterministic
comparator rows, 750 final-policy rows, and 34 abstain/review monitor rows.
Locked-test row-level artifacts remain unused. This turns the recommendation
below into an executable next step: analyze component-owner and hidden-family
strata on validation first, then choose no more than three controlled mechanism
hypotheses before any new architecture change.

## Executive Summary

The generalization gap is persistent across architecture families.

| Variant | Development surface | Development Purist | Test surface | Test Purist | Gap | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Rules-only V1 | validation750 | 697/750 = 0.9293 | test450 | 343/450 = 0.7622 by rerun; 0.7600 in original report | about 0.17 | Excellent evidence validity, brittle clinical/semantic coverage. |
| Claim-table v5 clean | validation250 | 227/250 = 0.9080 | test450 | 301/450 = 0.6689 | 0.2391 | LLM claim decomposition improves some misses but loses many more elsewhere. |
| Hybrid v0.2 cluster/diary gated | validation750 | 677/750 = 0.9027 | test450 | 343/450 = 0.7622 | 0.1405 | Ties deterministic on test, but only by equal corrections and regressions. |

For validation-only variants, the same pattern appears as prefix-to-full
validation collapse:

| Variant | Earlier surface | Earlier Purist | Later surface | Later Purist | Drop | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Structured-events v0.5 full stack | validation250 | 0.9640 on v04 current replay | validation750 | 675/750 = 0.9000 | about 0.064 | Metric survives only with heavy deterministic repair. |
| Claim-table v4 clean | validation250 | 231/250 = 0.9240 | validation750 | 528/750 = 0.7040 | 0.2200 | Prefix was not representative; cluster and boundary behavior collapsed. |
| Hybrid v0.1 adjudicator | validation250 | 243/250 = 0.9720 | validation750 | 680/750 = 0.9067 | 0.0653 | Adjudicator corrected some misses but regressed many deterministic-correct rows. |
| Hybrid v0.2 gated | validation250 | 244/250 = 0.9760 | validation750 cluster/diary | 677/750 = 0.9027 | about 0.0733 | Conservative gates did not create enough high-precision action. |

The short version: changing the surface form of the architecture did not change
the main failure. The models and rules are still being asked to emit a brittle
benchmark label from a note family that has hidden template/semantic subfamilies.
Validation saturation is masking that brittleness because many validation rows
are easy, repeatedly matched, or scorer-collapsed.

## Major Results

### Rules-Only V1

Rules-only V1 remains the most transparent comparator:

| Split | Purist | Pragmatic | Evidence exact |
| --- | ---: | ---: | ---: |
| validation750 | 697/750 = 0.9293 | 704/750 = 0.9387 | 750/750 |
| test450 | 343/450 = 0.7622 by rerun; original holdout report 0.7600 | 354/450 = 0.7867 | 450/450 |

Per-gold-kind Purist:

| Gold kind | Validation | Test |
| --- | ---: | ---: |
| frequency | 445/468 = 0.9509 | 225/281 = 0.8007 |
| seizure_free | 109/112 = 0.9732 | 38/67 = 0.5672 |
| unknown | 79/100 = 0.7900 | 45/60 = 0.7500 |
| unresolved_multiple | 37/43 = 0.8605 | 19/26 = 0.7308 |
| no_reference | 27/27 = 1.0000 | 16/16 = 1.0000 |

The largest semantic shock is not evidence validity. Evidence remains exact. The
shock is clinical state mapping and coverage: seizure-free, frequency, and
unresolved-multiple behavior all drop, while no-reference stays easy.

### Hybrid V0.2 `cluster_diary_candidate_recall`

The named candidate-recall revision fixed the synthetic cluster/diary target,
but broad validation/test behavior did not improve over deterministic V1.

| Split | Condition | Purist | Pragmatic | Changed labels | Wrong to correct | Correct to wrong |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| validation750 | deterministic top | 697/750 | 704/750 | 0 | 0 | 0 |
| validation750 | raw adjudicator | 674/750 | 683/750 | 48 | 5 | 28 |
| validation750 | gated final | 677/750 | 686/750 | 45 | 5 | 25 |
| test450 | deterministic top | 343/450 | 354/450 | 0 | 0 | 0 |
| test450 | raw adjudicator | 349/448 decisions | 359/448 decisions | 38 | 15 | 9 |
| test450 | gated final | 343/450 | 353/450 | 29 | 9 | 9 |

Candidate recall shows the generator bottleneck very clearly:

| Split | Candidate Purist recall | No-recall rows | No-recall rows correct after gated final |
| --- | ---: | ---: | ---: |
| validation750 | 707/750 = 0.9427 | 43 | 0 |
| test450 | 359/450 = 0.7978 | 91 | 0 |

When the gold Purist category is absent from the candidate set, the adjudicator
cannot recover. The cluster/diary branch improved the synthetic hard-case panel,
but it did not move the broad validation/test candidate-recall ceiling because
the missing test phenomena are wider than the targeted branch.

Per-gold-kind behavior for gated final:

| Gold kind | Validation gated | Test gated | Main note |
| --- | ---: | ---: | --- |
| frequency | 425/468 = 0.9081 | 221/281 = 0.7865 | Gated LLM hurts frequency selection on validation. |
| seizure_free | 109/112 = 0.9732 | 42/67 = 0.6269 | LLM helps seizure-free on test but not enough. |
| unknown | 79/100 = 0.7900 | 45/60 = 0.7500 | Mostly inherited from deterministic. |
| unresolved_multiple | 37/43 = 0.8605 | 19/26 = 0.7308 | Mostly inherited from deterministic. |
| no_reference | 27/27 = 1.0000 | 16/16 = 1.0000 | Easy sentinel state. |

The gate profile is also telling. On validation, only three overreach gates fire.
On test, eleven gates fire, including five boundary-demotion blocks and two
missing/invalid adjudicator outputs. The model is less contract-stable and less
semantically supported on test, even under the same prompt and candidate policy.

### Claim-Table Selectors

Claim-table variants attempted a more LLM-native decomposition: segment the note,
extract claims, then answer the final query from a structured claim table.

V4 looked promising on validation250 after schema replay, then collapsed on full
validation:

| Variant | Surface | Raw Purist | Strict Purist | Clean Purist | Parse/schema issues | Rows changed by repair |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| claim-table v4 | validation250 | 228/250 = 0.9120 | 230/250 = 0.9200 | 231/250 = 0.9240 | 0 | not primary |
| claim-table v4 | validation750 | 512/750 = 0.6827 | 516/750 = 0.6880 | 528/750 = 0.7040 | 3 | 108 |

V5 improved the schema and selector fields, but the validation-to-test gap
remained severe:

| Surface | Raw Purist | Strict Purist | Clean Purist | Structured records | Parse/schema issues |
| --- | ---: | ---: | ---: | ---: | ---: |
| validation250 | 223/250 = 0.8920 | 224/250 = 0.8960 | 227/250 = 0.9080 | 248/250 | 2 |
| test450 | 293/450 = 0.6511 | 294/450 = 0.6533 | 301/450 = 0.6689 | 445/450 | 5 |

Component failures rose sharply on test:

| Component | Validation250 | Test450 |
| --- | ---: | ---: |
| segmentation_sectioning | 15/250 = 0.0600 | 41/450 = 0.0911 |
| claim_extraction | 9/250 = 0.0360 | 61/450 = 0.1356 |
| final_query | 4/250 = 0.0160 | 32/450 = 0.0711 |
| scorer_format | 8/250 = 0.0320 | 39/450 = 0.0867 |
| temporality_conflict | 1/250 = 0.0040 | 8/450 = 0.0178 |
| parse_schema | 2/250 = 0.0080 | 5/450 = 0.0111 |

Evidence validity also dropped:

| Evidence measure | Validation250 | Test450 |
| --- | ---: | ---: |
| Claim evidence exact | 567/574 = 0.9878 | 1145/1188 = 0.9638 |
| Selected final evidence exact | 246/250 = 0.9840 | 418/450 = 0.9289 |

Claim-table v5 has useful complementarity with deterministic V1, but it is not
yet a reliable replacement. On test, claim-table v5 correctly classifies 61 rows
that deterministic V1 misses, while deterministic V1 correctly classifies 103
rows that claim-table v5 misses. A naive ensemble would have signal to exploit,
but the current hybrid design is not exploiting this signal.

### Structured-Events LLM V0.5

Structured-events v0.5 reached the active validation threshold only as a
repair-heavy hybrid diagnostic:

| Condition | Purist | Pragmatic | Interpretation |
| --- | ---: | ---: | --- |
| Raw LLM final label only | 0.6062 | 0.6338 | Clean model attribution is poor. |
| Format-preserving basic repair | 0.5954 | 0.6231 | Even format-only repair is not reliably beneficial. |
| Full basic Gan label repair | 0.7092 | 0.7369 | Includes semantic fallback and vague-quantity remapping. |
| Selected-evidence repair | 0.8400 | 0.8554 | Deterministic evidence-derived label replacement. |
| Full current stack | 0.9046 on replay surface; 675/750 = 0.9000 in completion5 report | 0.9200 | Hybrid post-processing, not LLM-first. |

The full validation report had 481 deterministic repair notes and 714/750 exact
selection-evidence substrings. This architecture is valuable as a stress test of
semantic repair families, but it does not prove the model has learned the
generalizable clinical mapping. Most of the metric lift is deterministic
post-selection behavior.

### Hybrid V0.1

Hybrid v0.1 confirms the same selective-action problem before the v0.2 gates:

| Surface | Deterministic top | Adjudicator | Wrong to correct | Correct to wrong |
| --- | ---: | ---: | ---: | ---: |
| validation250 | not primary here | 243/250 = 0.9720 | diagnostic only | diagnostic only |
| validation750 | 697/750 = 0.9293 | 680/750 = 0.9067 | 7 | 24 |

The LLM can sometimes correct deterministic overreach, but its action precision
is too low on broad surfaces. V0.2 gates reduced some unsupported actions, but
they did not turn the adjudicator into a net-improving prediction-bearing layer.

## Cross-Architecture Error Analysis

### 1. Split label mix is similar, but hidden subfamilies are not

The validation and test Purist category distributions are not wildly different:

| Category | Validation count | Test count |
| --- | ---: | ---: |
| seizure_freq_unknown | 170 | 102 |
| seizure_freq_more1week_less1day | 164 | 98 |
| currently_no_seizure | 112 | 67 |
| seizure_freq_more1mon_less1week | 106 | 62 |
| seizure_freq_more1per6mon_less1mon | 76 | 52 |
| seizure_freq_1ormore_daily | 63 | 36 |

The gap is therefore unlikely to be explained by high-level label imbalance
alone. The harder shift is inside categories: phrasing, temporal anchoring,
cluster notation, seizure-free boundary language, and distributed count patterns.
The current split stratifies by gold kind and row quality, not by note template,
lexical family, arithmetic pattern, or clinical-state ambiguity.

### 2. Candidate recall is a hard upper bound for rules-candidate hybrids

Hybrid candidate recall drops from 707/750 on validation to 359/450 on test.
Every no-recall row is wrong after the gated final on both surfaces.

This makes the hybrid adjudicator structurally unable to escape the gap. If the
correct Purist category is absent, the LLM adjudicator is constrained to choose
among wrong candidates or fall back.

### 3. Selector/action precision is too low

Across hybrid adjudicator variants:

| Variant | Surface | Changed labels | Wrong to correct | Correct to wrong | Net |
| --- | --- | ---: | ---: | ---: | ---: |
| v0.1 | validation750 | 43 | 7 | 24 | -17 |
| v0.2 cluster/diary raw | validation750 | 48 | 5 | 28 | -23 |
| v0.2 cluster/diary gated | validation750 | 45 | 5 | 25 | -20 |
| v0.2 cluster/diary raw | test450 | 38 | 15 | 9 | +6 before gates |
| v0.2 cluster/diary gated | test450 | 29 | 9 | 9 | 0 |

The adjudicator is not useless. Raw test behavior has signal. But current gates
are blunt: they block unsupported outputs, but they also remove some useful
corrections and do not identify all harmful supported changes.

### 4. Repair stacks can buy validation score without buying attribution

Structured-events v0.5 and claim-table variants show that repair layers often
help score, but the most helpful repairs are semantic. They derive labels from
selected evidence, resolve temporal anchors, reinterpret seizure-free boundary
states, or coerce vague quantities. Those are real prediction-bearing rules.

This explains why the apparent architecture diversity has been less diverse
than it looks. Many variants eventually depend on the same deterministic
benchmark-facing post-processing logic, even when the upstream representation is
LLM-generated.

### 5. Evidence exactness is necessary but not sufficient

Rules-only V1 has exact evidence on every validation and test row. Claim-table
v5 has high evidence exactness. Structured-events v0.5 has high selection
evidence exactness. Yet all exhibit a gap.

The hard operation is not merely finding a substring. It is converting a local
span into the benchmark-facing clinical state under competing windows,
semiologies, clusters, negation, seizure-free assertions, and underdetermined
frequency language.

### 6. Complementarity exists, but the current hybrid does not exploit it

On test:

| Outcome across deterministic, hybrid gated, claim-table v5 | Rows |
| --- | ---: |
| all three correct | 240 |
| all three wrong | 43 |
| deterministic and hybrid correct, claim wrong | 94 |
| claim correct, deterministic and hybrid wrong | 55 |
| claim and hybrid correct, deterministic wrong | 6 |
| deterministic correct, hybrid and claim wrong | 9 |
| hybrid correct only | 3 |

Claim-table v5 fixes 61 deterministic misses, but deterministic fixes 103
claim-table misses. This argues against declaring any current pipeline family
dead. It argues for a different arbitration architecture with calibrated
condition-specific expertise, not another single global selector prompt.

## Why The Generalization Gap Persists

1. The task is not a single extraction task. It is a bundle of latent sub-tasks:
event detection, seizure-vs-non-seizure targeting, temporality, current-window
selection, semiology aggregation, cluster arithmetic, seizure-free boundary
logic, unknown/no-reference separation, and Gan label formatting. Broad Purist
accuracy hides which sub-task is actually being tested.

2. Validation saturation is partly scorer saturation. Unknown, no-reference,
and unresolved states collapse in ways that can make semantically different
predictions look good. The validation error analysis already found many
`scorer_correct_semantic_mismatch` rows. This trains our intuition toward the
wrong success signal.

3. The architectures are different at the surface, but not different enough at
the causal level. Most still use one of two bottlenecks: a deterministic
candidate set, or a direct benchmark-facing label parser. Both bottlenecks
force complex clinical reasoning into a small label before uncertainty has been
represented.

4. The split likely contains hidden template-family shift. Stratifying by label
kind and row quality protects high-level balance, but not note grammar, synthetic
letter family, diary/cluster phrasing, shorthand, temporal anchors, or boundary
state expression. The fact that candidate recall drops from 0.9427 to 0.7978
while label mix remains similar is strong evidence for hidden family shift.

5. LLMs are being used in roles where their natural uncertainty is compressed.
The prompt asks for one final answer. Even when the model notices ambiguity, the
evaluation rewards a single Gan label. Current reports capture rationale, but
the score path does not use calibrated uncertainty or competing hypotheses.

6. Post-processing became a shadow model. Repairs are no longer just formatting;
they encode clinical and benchmark policy. That can recover validation cases,
but it also means the true architecture is a mixed deterministic-repair system
whose invariants were not designed from first principles.

## Proposed Radical Architecture

I would stop building new final-label pipelines for a cycle and build a
counterfactual semantic-state architecture.

Working name: **Clinical Frequency State Graph with Counterfactual Invariance**.

### Core idea

Do not ask any component to predict the Gan label directly. Instead, build a
canonical latent graph:

- seizure/event targets and semiologies;
- assertion status and negation;
- current, historical, future, and hypothetical windows;
- counts, intervals, clusters, events-per-cluster, and denominators;
- seizure-free intervals and breakthrough events;
- source spans for every atomic claim;
- uncertainty and missing-variable flags;
- competing hypotheses when evidence conflicts.

Then use a deterministic solver to project the graph into Gan labels. The solver
is explicit, ablated, and auditable. The model is not rewarded for memorizing
Gan label strings; it is rewarded for building the same clinical state under
paraphrase, ordering, and template changes.

### Components

1. **High-recall span harvester**

   Use deterministic patterns and a permissive LLM extractor to collect every
   possible frequency, seizure-free, cluster, date, and boundary-state claim.
   This component is allowed to be noisy. Its metric is oracle coverage, not
   final F1.

2. **Entailment-constrained graph builder**

   An LLM fills the graph, but every atomic field must point to exact evidence.
   A verifier checks whether the evidence entails the field. Non-entailed fields
   stay uncertain instead of being silently coerced.

3. **Temporal and arithmetic solver**

   Use deterministic code or a small constraint solver for windows, clusters,
   elapsed dates, and count aggregation. This removes arithmetic from prompt
   behavior and makes every arithmetic rule ablatable.

4. **Competing-hypothesis adjudicator**

   Instead of selecting one label directly, the model ranks graph hypotheses and
   gives a reason for rejecting alternatives. If two hypotheses remain plausible,
   the system emits an uncertainty state that can be analyzed before forcing a
   benchmark projection.

5. **Counterfactual paraphrase harness**

   For every validation hard case, generate controlled paraphrases that preserve
   the latent graph while changing surface form, note order, section headings,
   shorthand, and distractors. The primary metric is graph invariance across
   paraphrases, not only Gan F1.

6. **Family-aware evaluation**

   Cluster rows by template and semantic phenomenon using only validation and
   development surfaces. Create leave-family-out validation splits. If a system
   cannot hold out a template family, it is not ready for locked test.

### Why this might escape the gap

It attacks the hidden variable directly. Current pipelines try to learn a
mapping from note text to label. The proposed system learns and audits a mapping
from note text to a clinical state graph, then separately audits projection from
graph to benchmark label.

It also creates new diagnostics that current comparisons cannot answer:

- Was the seizure-frequency fact absent from the harvested spans?
- Was it present but not represented in the graph?
- Was it represented but projected incorrectly?
- Was the projection correct clinically but mismatched to Gan policy?
- Does the same graph survive paraphrase and template shift?
- Which template families are truly out of distribution?
- Which uncertainty states should abstain rather than pretend to know?

### First validation-cycle experiments

1. **Oracle coverage study**: run the high-recall harvester on validation and
synthetic hard cases. Report whether the gold Purist category is representable
in the harvested graph. This isolates recall from selection.

2. **Projection-only ablation**: manually or programmatically build gold-like
graphs for a validation hard slice and test the deterministic Gan projection
solver. This tells us whether benchmark projection itself is a major source of
error.

3. **Graph invariance panel**: build 50 validation-derived counterfactual pairs
that preserve the latent state while changing wording. Score graph consistency
before final-label accuracy.

4. **Leave-family-out validation**: cluster validation rows by surface family
using non-test data, then evaluate rules-only, claim-table, and graph-based
systems with a family held out. This should reveal whether the current
validation/test gap is mostly hidden template shift.

5. **Selective arbitration on graph features**: train or prompt a router only
after graph diagnostics exist. The router decides which component owns which
sub-task, not which final label to trust globally.

## Recommended Next Decision

Do not tune v0.2 gates from the test run. The locked-test result should be
recorded as a final generalization audit for that frozen candidate.

The most informative next work is now the validation-only gap-matrix analysis
cycle:

- freeze current rules-only V1, claim-table v5, and hybrid v0.2 cluster/diary as
comparators;
- use `validation_test_gap_matrix_v0` to identify component-owner and
 hidden-family strata with real validation leverage;
- choose at most three controlled hypotheses from H1-H10, with current priority
 on H2 component ownership, H4 evidence-versus-projection/rendering, and H6
 selective action transfer;
- build oracle span and graph coverage diagnostics on validation and synthetic
 hard panels only after the matrix identifies the first-failure owners worth
 stressing;
- add a family-aware validation split or hard-slice protocol before any
 holdout-facing audit;
- report whether remaining errors are span absence, graph construction,
 projection policy, selective action, or benchmark convention.

The goal should shift from "which architecture gets the highest next F1?" to
"which architecture tells us where the hidden variable is?" Once that hidden
variable is visible, a later frozen test audit will be much less like throwing a
well-dressed dart into the dark.
