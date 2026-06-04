# Project Status

Last updated: 2026-06-04

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions one at a
time under exact-evidence, attribution, hidden-family, and split-discipline
constraints. No holdout or benchmark-comparable claim is authorized.

## Current Strategy

Use saved artifacts as research instruments for clean component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators, safety
floors, and miss-slice definers, not eligible answers for RQ1-RQ4.

RQ10 is now answered for saved validation replay: among 53 residual Purist
misses, 23 are `underdetermined_note`, 19 are `true_extraction_failure`, and 11
are `benchmark_convention_dominated`; 29 rows have exact evidence but remain
scorer/gold-wrong, and 0 are strong likely gold defects. This is a
development-control result only. A full validation750 gold/reference review CSV
now screens all gold labels as `clear` or `ambiguous` for manual adjudication.

RQ1/RQ2 single-task controls remain materialized and should resume after the
current ambiguity/review-routing decision, unless the next priority is RQ9.

## Active Question

RQ10 Gold/Scorer Ambiguity Audit

Question: how much residual validation error reflects true extraction failure
versus benchmark convention, underdetermined notes, clinically defensible
alternatives, or possible gold-label weakness?

Status: answered for saved validation replay only. The next action is to
predeclare RQ9 abstention/human-review routing that separates
`underdetermined_note`, `clinically_defensible_alternative`, and
`benchmark_convention_dominated` rows from true extraction failures.

Core artifacts:

- `docs/research/gan2026_rq10_gold_scorer_ambiguity_audit_protocol_2026-06-04.md`
- `docs/research/gan2026_rq10_gold_scorer_ambiguity_audit_answer_2026-06-04.md`
- `experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.jsonl`
- `experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.json`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/rq10_gold_scorer_ambiguity_audit.py`
- `experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv`
- `experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.json`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/validation_gold_ambiguity_inventory.py`
- `docs/research/gan2026_rq1_rq2_single_task_controls_protocol_2026-06-04.md`
- `docs/research/gan2026_prompt_language_audit_2026-06-04.md`
- `docs/research/gan2026_prompt_contamination_variant_disposition_report_2026-06-04.md`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/experiments/single_task_control_prompts.py`
- `experiments/gan2026_rq1_rq2_single_task_control_panels_2026-06-04.md`
- `experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.md`
- `docs/research/gan2026_rq5_deterministic_compilation_rendering_answer_2026-06-04.md`
- `docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-04.md`

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout;
  locked test is not for row-level tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Do not treat "deterministic top still wins" as an RQ1-RQ4 answer.
- Any holdout-facing use needs a frozen predeclared audit or must keep the claim
  validation-only.
- Do not change scorer/gold policy from RQ10 alone; use it to design abstention,
  review routing, or a separate policy predeclaration.
- Isolated controls must be interpreted before paired-task prompts; final F1 is
  secondary to candidate recall, evidence exactness, projection consistency,
  metadata completeness, ambiguity preservation, and regression accounting.

## Work Board

### Now

- Predeclare RQ9 abstention/human-review routing using the RQ10 audit classes.
- Review the validation750 gold/reference ambiguity CSV and replace the
  heuristic `codex_initial_ambiguity_label` with manual adjudication.
- Decide whether to run RQ1/RQ2 `balanced_validation50` controls before or after
  the RQ9 protocol.

### Next

- Fill `source_id_status` validation for completed RQ1/RQ2 isolated controls.
- Run paired-task overload controls on `balanced_validation50` without changing
  frozen prompt versions.
- Decide from validation50 isolated results whether and how to run the fixed
  `hidden_family_hard_panel`.

### Backlog

- Resume RQ3 schema-comparison protocol after single-task controls identify the
  representation failures that need schema comparison.
- Rewrite `llm_only_minimal_evidence_selector.py` under the prompt-language
  audit before any new minimal-evidence calls.
- Design one clean selected-state successor from the prompt-contamination
  disposition report before any new selected-state live calls.
- RQ5 follow-up implementation only if a non-state-graph selected-state surface
  exposes fixed bundles that need rendering audit.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline promotion is blocked until component questions are answered.

### Done Recently

- 2026-06-04: Completed the full
  validation750 gold/reference ambiguity review sheet:
  `experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv`
  has 750 rows with manual review columns, 244 initial `clear` screens and 506
  initial `ambiguous` screens. Labels are heuristic worklist flags only.
- 2026-06-04: Completed the full
  `gan2026_rq1_rq2_component_control_matrix` analysis for completed
  `balanced_validation50` isolated controls: candidate-only, gold-query
  evidence-only, candidate-conditioned evidence-only, and projection-only each
  parsed 50/50; evidence exactness was 47/50 for the first three surfaces;
  projection had 4/50 exact canonical labels and 33/50 broad kind matches.
  Paired-task overload rows and the hard panel remain unrun.
- 2026-06-04: Completed the RQ10 gold/scorer ambiguity audit for saved
  validation replay: 53 Purist misses classified, hard-row ambiguity rate
  0.641, 29 exact-evidence-but-scorer-wrong rows, 25 clinically defensible
  alternative flags, and 0 strong likely gold defects.
- 2026-06-04: Catalogued prompt-language failures in
  `docs/research/gan2026_prompt_language_audit_2026-06-04.md`, created the
  validated personal skill
  `/Users/cobro/.codex/skills/plain-language-prompt-auditor/SKILL.md`, and
  wrote frozen prompt/schema stubs for the RQ1/RQ2 controls.
- 2026-06-04: Wrote the prompt-contamination variant disposition report:
  preserve existing variants as historical prompt conditions, keep the cleaned
  minimal evidence selector as a narrow baseline, and design one clean
  selected-state successor before further selected-state live calls.
- 2026-06-04: Materialized the fixed RQ1/RQ2 control surfaces:
  `balanced_validation50`, `hidden_family_hard_panel`, and the 875-record
  component-control matrix.
- 2026-06-04: Wrote the RQ5 deterministic compilation/rendering answer:
  saved validation replay and focused ACD fixtures show 0 semantic-drift rows
  and 0 attribution-loss rows in current production; ACD-off ablation creates 6
  policy-removal drifts.
- 2026-06-04: Wrote validation-development component answers for RQ1, RQ2, RQ4,
  and the combined synthesis; these remain diagnostic for reopened single-task
  controls rather than a basis to move to RQ3.
- 2026-06-03: Reset RQ1/RQ2/RQ4 interpretation and added the mechanism
  protocol, synthesis, error analysis, and 195-row mechanism artifact.
