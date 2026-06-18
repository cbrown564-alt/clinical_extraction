# Gan 2026 Current Pipeline Results Report

Date: 2026-06-01

This report summarizes the current best-performing deterministic and LLM-first
Gan 2026 seizure-frequency extraction pipelines. It is a development research
report, not a benchmark-comparison claim. Validation results are development
surface results under `gan2026_split_v1`; the deterministic test result is the
one locked holdout evaluation for frozen V1, and no test row-level failures were
used for tuning.

## Executive Summary

The current evidence supports three conclusions:

1. The frozen deterministic V1 pipeline is the strongest transparent validation
   comparator, reaching 0.9293 Purist micro F1/accuracy and 0.9387 Pragmatic on
   the 750-row validation split with exact selected-evidence substrings for all
   rows.
2. Clean structured LLM attribution remains materially below the project
   threshold: on the 650-row saved-output replay, raw structured LLM selection
   reaches 0.6062 Purist, and raw plus frozen clean scorer-facing normalization
   reaches 0.6738 Purist.
3. The highest-scoring structured LLM line reaches the 0.9000 Purist validation
   threshold only after a substantial deterministic post-processing stack. It
   should currently be described as a repair-heavy hybrid diagnostic, not as a
   clean LLM-first result.

The deterministic V1 holdout result, 0.7600 Purist and 0.7867 Pragmatic on the
450-row locked test split, is the major caution. It shows that high validation
performance can coexist with validation-surface overfit and brittle rule
accumulation. The LLM-first work has better architectural potential for
inspectable clinical reasoning, but its current score is best understood as a
ladder: model selection, clean scorer-facing normalization, a bridge into
broader label repair, selected-evidence deterministic derivation, then
contextual temporal/event-state modules. The largest single jump comes from
selected-evidence deterministic derivation, not from raw model selection.

## High-Level Results

| Pipeline | Surface | Purist | Pragmatic | Evidence | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| Deterministic V1 frozen comparator | validation, 750 rows | 0.9293, 697/750 | 0.9387 | 750/750 | Best transparent validation result |
| Deterministic V1 frozen comparator | locked test, 450 rows | 0.7600 | 0.7867 | 450/450 | Strong rules-only baseline, but validation overfit |
| Structured LLM v0.5 full stack | validation, 750 rows | 0.9000, 675/750 | 0.9200, 690/750 | 714/750 | Hits target as a repair-heavy hybrid |
| Clean LLM attribution ladder | first 50 validation rows | raw 0.6800; strict 0.8200; clean 0.8600 | raw 0.7200; strict 0.8600; clean 0.9200 | 50/50 | Useful signal, below threshold as clean LLM-first |
| Grouped attribution/repair ladder | 650 saved-output rows | clean 0.6738; hybrid full stack 0.9046 | clean 0.7308; hybrid full stack 0.9200 | 619/650 | Shows where the clean path ends and hybrid repair begins |

The deterministic validation result is excellent, but the locked test drop from
0.9293 to 0.7600 is decisive evidence against claiming broad generalization.
The exact evidence-span behavior remains a strength and supports transparency,
but it does not rescue the generalization claim.

The structured LLM v0.5 750-row validation completion had no call failures and no
parse/schema/label issues, but it recorded 481 deterministic repair notes. The
repair audit therefore classifies the result as GPT-4.1 mini structured
extraction plus Gan-specific deterministic post-processing.

The 650-row grouped attribution ladder is now the clearest research summary of
the LLM line. It separates clean LLM-first attribution from hybrid deterministic
post-processing:

| Group | Claim class | Purist | Delta vs previous group | Pragmatic | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Raw structured LLM selection | clean attribution baseline | 0.6062, 394/650 | baseline | 0.6338 | Model-selected final label before downstream repair |
| Clean scorer-facing normalization | clean attribution | 0.6738, 438/650 | +44 rows | 0.7308 | Strict format repair plus frozen scorer-facing Gan policy |
| Broad basic label repair bridge | hybrid bridge | 0.7092, 461/650 | +23 rows | 0.7369 | Crosses clean boundary via semantic fallback and vague-quantity remapping |
| Selected-evidence deterministic derivation | hybrid repair module | 0.8400, 546/650 | +85 rows | 0.8554 | Largest jump; deterministic derivation over model-selected evidence |
| Contextual temporal and event-state modules | hybrid repair modules | 0.9046, 588/650 | +42 rows | 0.9200 | Diary, interval, breakthrough, dated-sequence, and elapsed-anchor reasoning |

## Deterministic V1 Error Categories

On validation, deterministic V1 had 53 Purist-incorrect rows, plus 81
scorer-correct semantic mismatches.

| Error type | Count |
| --- | ---: |
| Correct | 616 |
| Scorer-correct semantic mismatch | 81 |
| Wrong frequency bucket | 44 |
| Overpredicted frequency | 6 |
| Missed seizure-free evidence | 3 |

The likely failed operations were concentrated in semantic state mapping and
temporal selection.

| Operation | Count |
| --- | ---: |
| Semantic state mapping | 82 |
| Temporal selection | 38 |
| Assertion classification | 9 |
| Candidate extraction | 3 |
| Cluster normalization | 1 |
| Seizure type selection | 1 |

The clinical slices most associated with incorrect rows were medication/status
context, ranges, uncertainty, historical-current distinctions, clusters,
multiple seizure types, relative dates, and negation. In practice, V1 is strong
when a source phrase maps cleanly to a frequency or seizure-free duration, but it
is brittle when the note requires deciding which temporal state, semiology, or
uncertain statement should count.

## LLM Error Categories

The LLM line has two different error stories.

First, the clean LLM-first path is still weak at raw final selection. On the
650-row saved-output replay, raw model selection was 394/650 Purist with 140
parse/schema/label failures. Strict format repair and the frozen clean
scorer-facing policy reduced parse/schema/label failures to 65 and improved the
score to 438/650 Purist, but this remains far below the project threshold.

Second, the full v0.5 score is driven by deterministic post-LLM repair. On the
audited 650-row surface, the earlier row-transition audit found:

| Repair transition | Count |
| --- | ---: |
| Raw correct to final correct | 455 |
| Raw wrong to final correct | 126 |
| Raw wrong to final wrong | 63 |
| Raw correct to final wrong | 6 |

The repair taxonomy was:

| Repair class | Count |
| --- | ---: |
| Format/unit canonicalization | 86 |
| Frequency to different frequency | 105 |
| Frequency to sentinel/unknown | 83 |
| Seizure-free to frequency | 29 |
| Sentinel to frequency | 15 |
| Other repair | 112 |

This is the central attribution issue. Some repairs are benign Gan grammar
cleanup. Many others change the semantic answer: diary arithmetic, cluster
reconstruction, dated-sequence reasoning, breakthrough-after-seizure-free logic,
elapsed-anchor conversion, or unknown/no-reference overrides.

The grouped ladder refines that audit into a more useful interpretation. Clean
scorer-facing normalization adds 44 Purist-correct rows over raw selection. The
broad basic label repair bridge adds 23 more rows, but already crosses the clean
boundary. Selected-evidence deterministic derivation then adds 85 rows, making it
the dominant source of performance gain. The remaining temporal and event-state
modules add 42 rows as a bundle. Individually, many of those contextual modules
are small; collectively, they are what moves the system from a promising hybrid
at 0.8400 to the threshold-passing full stack at 0.9046.

## Deterministic Ablation Findings

The deterministic V1 ablation table shows which rule families carry validation
performance.

| Disabled group | Purist | Delta vs 0.9293 |
| --- | ---: | ---: |
| none | 0.9293 | baseline |
| date duration utilities | 0.9293 | 0.0000 |
| portable rate expressions | 0.7627 | -0.1666 |
| seizure-free/no-event assertions | 0.8107 | -0.1186 |
| cluster arithmetic | 0.8600 | -0.0693 |
| diary log aggregation | 0.8507 | -0.0786 |
| temporal selection | 0.7787 | -0.1506 |
| Gan shorthand | 0.9027 | -0.0266 |
| benchmark repair | 0.9293 | 0.0000 |

The score is not coming from one narrow pattern. It depends heavily on portable
rate expressions, temporal selection, seizure-free/no-event assertions, diary
aggregation, and cluster arithmetic. This makes V1 scientifically useful as an
ablatable rule taxonomy even though its locked-test generalization is not yet
strong enough.

## LLM Attribution And Repair Findings

The structured LLM v0.5 attribution ladder is best read in grouped form rather
than as a long list of tiny repair switches.

| Group | Purist | What it means |
| --- | ---: | --- |
| Raw structured LLM selection | 0.6062 | The model's own selected final label before repair |
| Clean scorer-facing normalization | 0.6738 | The clean LLM-first attribution endpoint |
| Broad basic label repair bridge | 0.7092 | First hybrid step; includes semantic fallback and vague-quantity remapping |
| Selected-evidence deterministic derivation | 0.8400 | Main deterministic contribution; derives labels from selected evidence |
| Contextual temporal and event-state modules | 0.9046 | Full hybrid stack; adds diary, interval, breakthrough, dated-sequence, and elapsed-anchor rules |

This grouping is more interpretable than the full 14-condition ladder. It
preserves the clean/hybrid boundary while avoiding over-reading small increments
from individual temporal modules. The clean endpoint is 0.6738 Purist. The
threshold-passing endpoint is 0.9046 Purist. The 0.2308 absolute gap between
those endpoints is the measurable hybrid deterministic-postprocessing
contribution on the 650-row saved-output replay.

The LLM remains valuable because it extracts structured events, chooses evidence,
and gives inspectable intermediate state. But the present high metric is not
primarily raw model clinical selection. It is a hybrid architecture in which
model-selected evidence becomes substrate for deterministic derivation and
temporal/event-state repair.

## Overall Synthesis

The strongest current scientific result is not that LLMs beat deterministic
rules, or that deterministic rules solve the task. It is that Gan 2026
seizure-frequency extraction requires explicit temporal, semantic-state, and
benchmark-normalization machinery, and the project now has tools to expose where
that machinery lives.

Deterministic V1 proves that transparent rules can reach very high validation
performance with perfect selected-evidence substrings, but the locked test
result shows brittle validation overfit. V1 should remain frozen as a comparator
and diagnostic source, not be expanded casually.

Structured LLM v0.5 proves that a model can produce useful source-near event
structure and evidence traces, but the clean attribution score remains below the
threshold. The grouped ladder makes the architecture boundary explicit: clean
LLM-first attribution ends at 0.6738 Purist on the 650-row saved-output replay,
while the full hybrid stack reaches 0.9046. The 0.9000 validation result is
therefore better described as model extraction plus deterministic clinical and
benchmark repair.

This is not a negative result. It is a clearer decomposition of the work. The
LLM appears useful as a clinical evidence locator and source-near structuring
component. Deterministic code appears useful for explicit, testable temporal and
benchmark-facing transformations. The research risk is not that either side is
unhelpful; the risk is attribution drift. If deterministic derivation over
selected evidence is doing the largest share of metric movement, the paper-facing
claim should name that module family rather than treating it as incidental
normalization.

The most promising interpretation is a controlled hybrid thesis: source-near LLM
extraction creates transparent intermediate claims or events, while deterministic
modules perform named, ablated transformations for scorer compatibility,
temporal reconstruction, diary arithmetic, and event-state resolution. That
claim is stronger and more reproducible than saying the LLM solved the task
after post-processing.

The next best research direction is the section-and-claim-table architecture
selected in ``.
That branch should force the model to expose multiple source-near claims,
sections, temporality, assertion status, and selected claim IDs before the
Gan-facing answer. This keeps prediction-bearing reasoning on the model side
while preserving enough intermediate state to debug temporal conflicts,
competing semiologies, diary windows, seizure-free intervals, and
no-reference/unknown distinctions.

## Source Artifacts

- `PROJECT_STATUS.md`
- `experiments/gan2026_v1_validation_ablation_2026-05-31.md`
- `experiments/gan2026_v1_validation_error_analysis_2026-05-31.md`
- `experiments/gan2026_v1_test_holdout_2026-05-31.md`
- `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.md`
- `experiments/gan2026_llm_structured_validation750_v05_repair_audit_2026-06-01.md`
- `experiments/gan2026_llm_structured_validation750_v05_repair_ablation_2026-06-01.md`
- `experiments/gan2026_llm_structured_validation750_v05_basic_split_repair_ablation_2026-06-01.md`
- `experiments/gan2026_clean_attribution_format50_v0_2026-06-01.md`
- `experiments/gan2026_clean_policy_freeze_ladder_v0_2026-06-01.md`
- `experiments/gan2026_clean_policy_freeze_ladder650_v0_2026-06-01.md`
- `experiments/gan2026_combined_attribution_repair_ladder650_v0_2026-06-01.md`
- `experiments/gan2026_grouped_attribution_repair_ladder650_v0_2026-06-01.md`
- ``
- ``
