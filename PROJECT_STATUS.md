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

RQ3 rich selected-state is now answered for the focused five-row surface and
the 75-row hidden-family hard panel. The result supports the architecture as a
typed fact carrier, not as direct LLM label rendering.
The first deterministic projection-policy replay over the saved hard panel is
complete with no new live model calls: orientation-exact projected labels moved
from 26/75 to 37/75, with 11 wrong-to-right changes, 0 right-to-wrong changes,
and 75/75 parseable revised labels.

The next architecture decision is documented in
`docs/research/gan2026_candidate_union_and_ambiguity_ownership_report_2026-06-04.md`:
test parallel deterministic plus selective LLM candidate proposal with a gated
union, and keep ambiguity primarily inside the rich selected state before
deterministic render/unknown/abstain/review policy. A post-state LLM verifier is
a backup for predeclared suspicious-state slices only.
The candidate-union and ambiguity-ownership protocols are now predeclared; the
next step is saved-artifact implementation, not new live model calls.

## Active Question

Candidate Union And Ambiguity Ownership

Question: should candidate breadth come from parallel deterministic and
selective LLM candidate proposal with a gated union, and should ambiguity live
inside the rich selected state before deterministic render/unknown/abstain/review
policy?

Status: protocols predeclared. RQ3 rich selected-state is answered for
validation-development hard-panel rows and supports the typed fact-carrier path.
The next step is to materialize saved-artifact candidate-union and
suspicious-state artifacts before any new live model calls.

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
- `docs/research/gan2026_rq1_rq2_component_control_fundamentals_analysis_2026-06-04.md`
- `docs/research/gan2026_rq1_rq2_five_letter_pipeline_walkthrough_2026-06-04.md`
- `docs/research/gan2026_rq3_rich_selected_state_protocol_2026-06-04.md`
- `docs/research/gan2026_rq3_rich_selected_state_five_letter_answer_2026-06-04.md`
- `docs/research/gan2026_rq3_rich_selected_state_hard_panel_answer_2026-06-04.md`
- `experiments/gan2026_rich_selected_state_five_letter_2026-06-04.md`
- `experiments/gan2026_rich_selected_state_five_letter_2026-06-04.jsonl`
- `experiments/gan2026_rich_selected_state_hard_panel_2026-06-04.md`
- `experiments/gan2026_rich_selected_state_hard_panel_2026-06-04.jsonl`
- `experiments/gan2026_rich_selected_state_hard_panel_policy_replay_2026-06-04.md`
- `experiments/gan2026_rich_selected_state_hard_panel_policy_replay_2026-06-04.jsonl`
- `docs/research/gan2026_rq5_deterministic_compilation_rendering_answer_2026-06-04.md`
- `docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-04.md`
- `docs/research/gan2026_candidate_union_and_ambiguity_ownership_report_2026-06-04.md`
- `docs/research/gan2026_candidate_union_protocol_2026-06-04.md`
- `docs/research/gan2026_ambiguity_ownership_protocol_2026-06-04.md`

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

- Implement saved-artifact candidate-union analysis: materialize
  `deterministic_candidates`, selective `llm_boundary_candidate_proposals`, and
  `union_verified_candidates` with evidence, source-id, metadata, and burden
  gates before any new live LLM calls.
- Implement deterministic suspicious-state checks over saved rich selected-state
  artifacts, then decide whether a selective LLM verifier is still needed.

### Next

- If saved candidate-union machinery is coherent, predeclare the exact hard
  slice and prompt/schema for any new selective LLM boundary-candidate calls.
- If suspicious-state slices remain unresolved after deterministic routing,
  predeclare a selective verifier run with W->C/C->W accounting.
- Predeclare RQ9 abstention/human-review routing using the RQ10 audit classes.
- Review the validation750 gold/reference ambiguity CSV and replace the
  heuristic `codex_initial_ambiguity_label` with manual adjudication.
- Fill legacy `source_id_status` validation for the 200 earlier
  `balanced_validation50` isolated-control rows that predate recursive source-id
  instrumentation.
- Add consistency checks for suspicious selected states, especially
  `state_kind=frequency` plus conditionality, unresolved cluster cadence, or
  seizure-free blockers that force deterministic abstention.

### Backlog

- Rewrite `llm_only_minimal_evidence_selector.py` under the prompt-language
  audit before any new minimal-evidence calls.
- RQ5 follow-up implementation only if a non-state-graph selected-state surface
  exposes fixed bundles that need rendering audit.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline promotion is blocked until component questions are answered.

### Done Recently

- 2026-06-04: Revised deterministic projection policy against the saved RQ3
  hard-panel rich selected-state JSONL with no new live model calls. The replay
  added cluster cadence/burden rendering, trigger-versus-condition handling,
  cluster-window inference with no-regression gates, and vague-increase
  abstention. Development orientation exactness improved from 26/75 to 37/75;
  changed rows were 11 wrong-to-right and 0 right-to-wrong, with 75/75 parseable
  revised labels. Artifacts:
  `experiments/gan2026_rich_selected_state_hard_panel_policy_replay_2026-06-04.md`
  and
  `experiments/gan2026_rich_selected_state_hard_panel_policy_replay_2026-06-04.jsonl`.
- 2026-06-04: Wrote the candidate-union and ambiguity-ownership architecture
  report. The preferred next path is parallel deterministic plus selective LLM
  candidate proposal, gated union, rich selected-state fact carrying, and
  deterministic render/unknown/abstain/review policy; a post-state LLM verifier
  remains a selective backup for suspicious-state slices only.
- 2026-06-04: Predeclared the candidate-union and ambiguity-ownership protocols.
  Both require saved-artifact analysis first and block new live model calls
  until candidate gates, suspicious-state checks, and W->C/C->W accounting are
  materialized.
- 2026-06-04: Completed the full
  validation750 gold/reference ambiguity review sheet:
  `experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv`
  has 750 rows with manual review columns, 244 initial `clear` screens and 506
  initial `ambiguous` screens. Labels are heuristic worklist flags only.
- 2026-06-04: Completed all 875 RQ1/RQ2 component-control matrix rows across
  `balanced_validation50`, paired-task overload conditions, and
  `hidden_family_hard_panel`. Every condition parsed fully. Single-task
  evidence selection remained strongest
  (`candidate_conditioned_evidence_only`: 47/50 balanced, 73/75 hard exact;
  `gold_query_evidence_only`: 47/50 balanced, 69/75 hard exact). Paired
  `candidate_plus_evidence_plus_projection` dropped to 35/50 balanced and 52/75
  hard exact, supporting overload/stress-surface interpretation rather than a
  preferred architecture.
- 2026-06-04: Wrote the RQ1/RQ2 fundamentals analysis: best LLM-owned primitive
  is `candidate_conditioned_evidence_only`, best broad locator is
  `gold_query_evidence_only`, `candidate_only` has selective rescue value, full
  `candidate_plus_evidence_plus_projection` is an overload/stress surface, and
  unconstrained LLM projection is rejected as direct final-label rendering.
- 2026-06-04: Added a five-letter RQ1/RQ2 pipeline walkthrough over rows 10,
  280, 3356, 10618, and 2748, showing how each experimental setup preserves or
  loses candidates, evidence, ambiguity, and projection policy.
- 2026-06-04: Implemented and smoke-tested the RQ3 rich selected-state surface
  `llm_only_rich_selected_state_reasoner`: five focused validation rows produced
  5/5 structured records, 5/5 exact selected evidence, and 5/5 parseable
  deterministic projected labels after same-output renderer replay. The key
  caveat is that the model overused `state_kind=frequency`, but filled
  conditionality and cluster fields well enough for deterministic projection on
  the focused rows.
- 2026-06-04: Completed the RQ3 rich selected-state hidden-family hard-panel
  run: 75/75 structured selected states, 72/75 clean evidence/trace rows, 75/75
  parseable deterministic projections, and 26/75 orientation-exact projected
  labels. The fundamentals answer is positive for typed fact carrying,
  strongest on unknown/ambiguity boundaries, but renderer policy remains weak
  for cluster cadence, benchmark multiple conventions, diary aggregation, and
  seizure-free/currentness precedence.
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
