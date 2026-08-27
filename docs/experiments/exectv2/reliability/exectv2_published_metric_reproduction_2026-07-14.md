# ExECTv2 published-metric reproduction

Date: 2026-07-14  
Hypothesis: `exectv2_published_metric_reproduction_2026-07-14`  
State: answered on dev140

## Question

Can the repository reproduce the ExECTv2 paper's evaluation views without
conflating a selected text phrase, its UMLS concept, and its complete evaluated
feature bundle?

This matters because the selected internal `clinical_headline` score measures
clinical fact recovery, while the paper reports exact entity-and-feature
agreement. The existing `benchmark` companion also includes the normalized
phrase in the same key as CUI and features, although the paper says ExECTv2 term
matching used CUIs.

## Source-backed scoring contract

The 2024 ExECTv2 paper defines agreement as selecting the same entity and
attributes for a specific term. It reports per-item scores for every entity
mention and per-letter scores when at least one entity with features is correct
in a letter. ExECTv2 validation uses certainty for Diagnosis and Patient History
and negation for Patient History. The discussion says ExECTv2 term matching used
CUIs. Table 1's overall values are the arithmetic mean of its nine
entity F1 values: `0.8722` rounds to the reported `0.87` per item and `0.8989`
rounds to `0.90` per letter.

Primary source: Fonferko-Shadrach et al., *Annotation of epilepsy clinic letters
for natural language processing*, Journal of Biomedical Semantics 15, 17
(2024), DOI `10.1186/s13326-024-00316-z`, especially Methods, Table 1, and the
Discussion.

The implementation will therefore keep three independently scored views:

1. `normalized_phrase`: entity plus normalized selected text;
2. `cui`: entity plus a non-empty CUI;
3. `all_features`: entity plus non-empty CUI and the complete evaluated
   attribute bundle, excluding `CUIPhrase` because it duplicates the concept
   label and excluding attributes the published validation says were unused.

Missing CUIs must not match other missing CUIs. Per-entity counts remain
micro-averaged over mentions or letters. The paper-comparable overall is a macro
mean across the nine entity scores and remains separate from the repository's
existing micro aggregate.

## Data and inspection policy

- Dataset: ExECTv2 synthetic clinic letters.
- Development split: `dev140`; row inspection is permitted.
- Held-out split: `test60`; no row-level inspection or development use.
- This study will not inspect `test60` or score `full200` while defining the
  measurement instrument.
- Row policy: all dev140 letters and all nine published entity families for the
  deterministic reference; the selected four-family LLM-with-rules replay may
  be included only as a clearly labelled partial-coverage diagnostic.

## Candidate, comparator, and component

- Candidate: a paper-derived published-metric scorer and deterministic report
  producer.
- Fixed comparator: the current `phrase_only`, `semantic`, and `benchmark`
  projection scores. Existing scores must not change.
- Component under study: scoring only. No extractor, prompt, normalization,
  evidence, projection, repair, or model output may change.
- Deterministic safety floor: missing CUI values are unmatchable; no concept is
  inferred during scoring.

## Metrics and analysis

- Primary: `all_features` macro per-item F1 across all nine entities.
- Secondary: normalized-phrase and CUI macro per-item F1; all three per-letter
  macro F1 values; per-entity precision, recall, F1, TP, FP, and FN.
- Required ablation: show the successive phrase-to-CUI and CUI-to-all-features
  deltas by entity. The layers are descriptive and need not be monotonic because
  they answer different matching questions.
- Hard slice: every entity is reported separately; missing-CUI counts are
  reported for gold and predictions.
- Regression check: the existing scorer outputs must replay unchanged.

## Artifact and reproducibility

The machine-readable JSON artifact will record the source commit or dirty-tree
state, Python and dependency versions, scorer version, split manifest, row and
entity policy, input mode, no-call status, paper reference values, metric
definitions, macro summaries, per-entity counts, missing-CUI counts, and the
existing-score regression values. The Markdown report will be rendered from
that JSON. No row text or held-out row details will be added.

## Stop rule and claim boundary

- **Answer:** tests pin all three views, the dev140 no-call replay produces the
  JSON and Markdown artifacts, existing scores do not move, and the report
  identifies which representation layer limits the deterministic reference.
- **Negative result:** keep it if full-attribute agreement remains low.
- **Revise:** if the primary paper and retained annotation contract contradict
  one another, retain both readings and do not call the result paper-comparable.
- **Reject:** if the implementation needs semantic inference in the scorer.
- **Blocked:** only if the retained data cannot represent the paper's entity,
  CUI, or feature bundle.

A positive result is a development answer that the repository implements the
documented published metric family. It is not a reproduction of the original
ExECTv2 system's `0.87`/`0.90`, not independent clinical validation, and not
holdout generalization.

## Result

The predeclared no-call replay completed on all 140 permitted development
letters and all nine published entity families. The deterministic all-entity
reference scored:

| View | Macro per-item F1 | Macro per-letter F1 |
| --- | ---: | ---: |
| Normalized phrase | 0.5687 | 0.7518 |
| CUI | 0.7144 | 0.8534 |
| CUI plus all evaluated features | 0.6020 | 0.7922 |

The existing scores did not move: phrase-only micro F1 remains `0.5461`,
semantic micro F1 remains `0.3668`, and the retained strict benchmark micro F1
remains `0.3548`.

Only one gold mention and six predicted mentions lacked CUIs. The main result is
therefore not a missing-CUI coverage failure. CUI matching recovers many
surface-form differences, especially for Prescription (`0.2981` phrase to
`0.8606` CUI) and Seizure Frequency (`0.5089` to `0.7837`). Requiring the full
feature bundle then exposes attribute errors: Diagnosis falls from `0.7332` CUI
F1 to `0.3010` all-features F1. The permitted row mechanism record contains 215
letter/entity cases where a CUI match loses feature agreement, 215 where CUI
identity recovers a phrase mismatch, and 52 where a phrase match has the wrong
CUI.

This confirms the hypothesis as a development answer. The repository now
implements the paper-derived metric family, but the deterministic reference
does not reproduce the original GATE ExECTv2 result. Its all-features macro
per-item F1 is `0.6020`, below the paper's `0.87` full200 reference, and the
comparison is development-only.

Artifacts:

- [machine-readable result](../../../../experiments/exectv2_published_metric_reproduction_deterministic_all9_dev140_20260714.json)
- [rendered result](exectv2_published_metric_reproduction_results_2026-07-14.md)
- scorer: `exectv2_published_metrics_v1`
- source revision: `6277796a0f4a8ee2afe793e6f1dd33a20c2e5ad2`, with the
  implementation recorded as a dirty working tree in the artifact

Decision: retain the negative benchmark result, keep `clinical_headline`
separate, and advance to out-of-sample confidence evaluation. Do not tune the
scorer or deterministic pipeline against test60.
