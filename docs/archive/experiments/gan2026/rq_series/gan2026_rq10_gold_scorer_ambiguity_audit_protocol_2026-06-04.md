> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ10 Gold/Scorer Ambiguity Audit Protocol

Date: 2026-06-04

## Question

RQ10 asks how much residual validation error reflects true extraction failure
versus benchmark convention, underdetermined notes, clinically defensible
alternatives, or possible gold-label weakness.

This audit is a validation-development, no-new-call scorer/gold study. It does
not change labels, parser policy, deterministic rules, prompts, projection
policy, or holdout claims.

## Surface

Primary surface:

- split: `gan2026_split_v1` validation only;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`;
- primary layer: `hybrid_adjudicator_with_adapters`;
- row set: Purist-wrong rows from the source artifact, plus the saved score
  layers and component diagnostics needed to identify all-system-fail and
  exact-evidence-but-scorer-wrong patterns.

Supporting context:

- `docs/design/data_contract.md`;
- `docs/design/gan2026_normalization_semantics.md`;
- `docs/design/gan2026_split_protocol.md`;
- ``;
- ``;
- `experiments/gan2026_validation_53_purist_misses_component_stress_2026-06-03.md`.

Locked test rows must not be inspected or used for policy changes.

## Deterministic Baseline Role

`rules_only_v1` / the saved deterministic safety-floor layer is a comparator
and miss-slice source only. It is not the answer to RQ10. RQ10 classifies the
meaning of residual misses, including cases where all saved systems agree with
a clinically plausible non-gold state.

## Row Schema

The machine-readable audit artifact must contain one row per audited
`source_row_index` with:

- split, artifact name, primary layer, source row index;
- gold label, gold semantic kind, gold reference, row quality flags;
- primary predicted label, deterministic label, graph projection label, LLM raw
  label, and correctness flags when available;
- selected evidence and exact/source-id status;
- hidden-family tags and first-failure owner from saved diagnostics;
- RQ10 ambiguity class;
- benchmark-convention flags;
- all-system-fail flag;
- exact-evidence-but-scorer-wrong flag;
- clinically defensible alternative flag;
- likely gold-defect flag;
- adjudication rationale.

## RQ10 Classes

Use the first applicable class below. These classes are diagnostic and do not
authorize label changes by themselves.

| Class | Meaning |
| --- | --- |
| `true_extraction_failure` | The saved system selected the wrong clinical fact or frequency; the gold/reference appears clear enough for development scoring. |
| `benchmark_convention_dominated` | The miss is mainly caused by Gan-specific label grammar, bucket convention, sentinel collapse, cluster formatting, vague-count convention, or duration collapse. |
| `underdetermined_note` | The note does not give enough source-grounded information for one clearly dominant scorer label. |
| `clinically_defensible_alternative` | The non-gold prediction has exact/source-near support and would be defensible to a clinical reviewer, even if Gan gold chooses another convention. |
| `possible_gold_weakness` | The gold label or gold reference appears internally inconsistent with the note or with similar validation annotations. |
| `instrumentation_gap` | Saved artifacts do not preserve enough evidence, layer state, or source trace to adjudicate. |

## Metrics

Report at least:

- hard-row ambiguity rate:
  rows in any non-`true_extraction_failure` RQ10 class / audited rows;
- all-system-fail rows:
  deterministic, graph, LLM raw/adjudicator, and primary layer are all Purist
  wrong or unscorable;
- exact-evidence-but-scorer-wrong rows:
  selected evidence is exact/source-id valid and the predicted fact is
  clinically plausible, but scorer/gold class is wrong;
- clinically defensible alternative labels;
- benchmark convention dominated rows;
- likely gold defects;
- class counts by hidden family and first-failure owner.

## Stop Rule

This RQ10 pass is answered for saved validation replay when:

- every Purist-wrong primary-layer validation row has a machine-readable RQ10
  class;
- the report gives row-level examples for each substantial class;
- uncertainty remains visible as `instrumentation_gap` rather than hidden by
  policy repair;
- no scorer or gold-policy code is changed.

If manual adjudication is insufficient or source evidence is missing, stop with
`instrumentation_gap` and define the next instrumentation task.

## Claim Boundary

The result is a development-control answer for saved validation replay only. It
may guide future abstention, scorer-facing normalization, or human-review
experiments, but it is not a benchmark-comparable claim and must not trigger
locked-test tuning.
