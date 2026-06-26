# Gan 2026 Multi-Component Assembly Experiment Log

Date: 2026-06-05

Objective: continue the multi-component staged hybrid assembly toward a
freezeable validation artifact and eventual locked-test audit, while preserving
`gan2026_split_v1` discipline and no benchmark-comparable claim language.

## Experiment Unit: Last-Event Duration Policy V0

Hypothesis: the residual last-event review rows can be made more auditable by
deriving explicit event-to-reference durations and conflict blockers, but they
should not become prediction-bearing unless the candidate-level promotion gate
confirms no deterministic-correct regression, exact evidence, and valid source
ids.

Minimal change:

- promoted the previous date instrumentation into
  `last_event_duration_policy_v0` fields;
- parsed full event dates and source reference dates;
- derived elapsed duration labels for auditable full-date rows;
- emitted conflict flags and release blockers;
- kept `automatic_release_ready` false for all rows.

Surface and policy:

- split: validation;
- split manifest: `gan2026_split_v1`;
- row policy: the 8 predeclared `date_policy_needed` rows from the residual
  non-prediction pressure review;
- scorer/mapping policy: unchanged Gan-compatible Purist/Pragmatic accounting;
- locked test: not inspected.

Commands:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_component_last_event_date_instrumentation.py
python -m pytest tests/test_gan2026_staged_hybrid_assembly.py \
  tests/test_gan2026_component_staged_decision_policy.py \
  tests/test_gan2026_component_trigger_context_release_rule.py \
  tests/test_gan2026_component_last_event_date_instrumentation.py
python -m clinical_extraction.tasks.seizure_frequency.gan2026.hybrid.staged_hybrid_assembly --mode validation750
```

Results:

- focused last-event tests: 4 passed;
- staged assembly related tests: 16 passed;
- rebuilt validation750 artifacts successfully;
- last-event policy artifact:
  `experiments/gan2026_staged_hybrid_last_event_date_instrumentation_2026-06-04.json`;
- rows reviewed: 8;
- reference-date anchors: 8;
- duration-auditable rows: 1;
- automatic release-ready rows: 0;
- blocker counts: 1 `protective_block_validation_accounting`, 3
  `partial_date_missing_year`, 4 `no_explicit_date_in_selected_evidence`.

Interpretation:

The full-date row (`11216`) derives exactly to `seizure free for 4 month`, but
it remains blocked because validation accounting marks the blocked candidate as
a protective block rather than a safe coverage gain. The last-event policy is
therefore useful as an audit component, not as a behavior-changing release rule.

Decision: revise/continue. Keep last-event automatic release blocked. The next
assembly work should build the candidate-level row contract and component
evidence matrix, then evaluate whether trigger-context release alone can be
promoted. No test audit is authorized yet.

## Experiment Unit: Component Evidence Matrix V0

Hypothesis: the staged hybrid assembly can satisfy the predeclared component
evidence-matrix gate without changing predictions, by flattening the current
validation750 assembly, conservative decision layer, trigger proposal, and
last-event duration-policy readout into one row per source row.

Minimal change:

- added `component_evidence_matrix_v0` as a reusable component;
- added candidate version/stem constants for
  `hybrid_multi_component_staged_assembly_v0`;
- wired validation750 materialization to emit the component matrix CSV, summary
  JSON, and report;
- kept the conservative decision layer as the current candidate decision;
- carried trigger-context and last-event policy fields as proposal/gate evidence,
  not silent prediction overrides.

Surface and policy:

- split: validation;
- split manifest: `gan2026_split_v1`;
- row policy: 750 validation rows, exactly once each;
- scorer/mapping policy: unchanged;
- locked test: not inspected.

Commands:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_component_evidence_matrix.py
python -m clinical_extraction.tasks.seizure_frequency.gan2026.hybrid.staged_hybrid_assembly --mode validation750
python -m ruff check \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/components/component_evidence_matrix.py \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/staged_hybrid_assembly.py \
  tests/test_gan2026_component_evidence_matrix.py
python -m pytest tests/test_gan2026_component_evidence_matrix.py \
  tests/test_gan2026_staged_hybrid_assembly.py \
  tests/test_gan2026_component_staged_decision_policy.py \
  tests/test_gan2026_component_trigger_context_release_rule.py \
  tests/test_gan2026_component_last_event_date_instrumentation.py
```

Results:

- focused component-matrix tests: 3 passed;
- related assembly/component tests: 19 passed;
- Ruff: passed;
- matrix artifact:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv`;
- matrix rows: 750;
- unique source rows: 750;
- contract issues: 0;
- prediction-bearing rows: 716;
- non-prediction rows: 34;
- selected-evidence exact false rows: 0;
- selected-source-id missing rows: 0;
- parse/evidence/schema issue rows: 0/0/0;
- verifier rows used: 0;
- trigger release proposal rows: 1;
- last-event duration-auditable rows: 1.

Comparator transition summary for the conservative decision layer:

- 678 `C_to_C`;
- 38 `W_to_W`;
- 17 `C_to_abstain`;
- 9 `W_to_abstain`;
- 2 `C_to_review`;
- 6 `W_to_review`.

Interpretation:

The component-evidence matrix gate is now satisfied for the conservative
validation-development candidate: row coverage, split manifest, verifier
non-use, selected evidence/source-id checks, and parse/evidence/schema issue
counters are all auditable. The matrix also exposes the remaining behavior
decision cleanly: trigger-context release remains a 1-row proposal, and
last-event release remains blocked despite one auditable duration row.

Decision: continue. The next experiment should run a frozen validation
promotion readout for accepting or rejecting the trigger-context release, then
materialize the candidate-level validation report/freeze gate. No test audit is
authorized until that freeze decision is recorded.

## Aggregate Diagnostic: Test Router Applicability Check

Question: can the existing RQ9 selective-action router, applied mechanically to
the already-frozen test450 source artifact without row-level inspection, plausibly
close the target gap?

Surface:

- split: test;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`;
- inspection policy: aggregate counts only, no test row-level failure review;
- status: diagnostic only, not a candidate freeze or tuning surface.

Command:

```bash
source .venv/bin/activate
python - <<'PY'
from pathlib import Path
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import rq9_selective_action_router as router
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import load_jsonl_rows
source = load_jsonl_rows(Path("experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl"))
rows, meta = router.build_selective_action_router_rows(source, [], [])
print(meta["metrics"])
print(meta["action_counts"])
print(meta["reason_counts"])
PY
```

Results:

- eligible rows: 450;
- predict / abstain / review: 449 / 1 / 0;
- selective Purist accuracy over predicted rows: 0.7617;
- full-row Purist proxy when the one abstention is non-correct: 0.7600;
- reason counts: 289 `plain_predictable_frequency`, 110
  `plain_no_reference`, 50 `plain_predictable_seizure_free`, 1
  `trigger_conditioned_frequency`.

Interpretation:

The router alone does not solve the generalisation gap. On test it mostly
predicts rather than abstains, and the aggregate Purist proxy remains near the
known deterministic/test ceiling. This should not be tuned from row-level test
failures; the next development work must return to validation or synthetic hard
panels to find a mechanism that genuinely improves locked-test generalisation.

## Experiment Unit: Trigger Release Promotion Gate

Hypothesis: the 1-row trigger-context release proposal can be promoted only if
the component matrix confirms the predeclared gate: release rows are W->C, no
C->W is introduced, selected evidence is exact, and source ids are present.

Minimal change:

- added `trigger_release_promotion_analysis_v0`;
- wired validation750 materialization to emit a trigger promotion JSON/report;
- enforced the original W->C / 0 C->W promotion gate against the component
  matrix instead of relying only on the trigger proposal artifact.

Surface and policy:

- split: validation;
- split manifest: `gan2026_split_v1`;
- locked test: not inspected;
- scorer/gold policy: unchanged.

Commands:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_component_trigger_release_promotion_analysis.py
python -m clinical_extraction.tasks.seizure_frequency.gan2026.hybrid.staged_hybrid_assembly --mode validation750
python -m ruff check \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/components/component_evidence_matrix.py \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/components/trigger_release_promotion_analysis.py \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/staged_hybrid_assembly.py \
  tests/test_gan2026_component_evidence_matrix.py \
  tests/test_gan2026_component_trigger_release_promotion_analysis.py
python -m pytest tests/test_gan2026_component_trigger_release_promotion_analysis.py \
  tests/test_gan2026_component_evidence_matrix.py \
  tests/test_gan2026_staged_hybrid_assembly.py \
  tests/test_gan2026_component_staged_decision_policy.py \
  tests/test_gan2026_component_trigger_context_release_rule.py \
  tests/test_gan2026_component_last_event_date_instrumentation.py
```

Results:

- focused trigger-promotion tests: 3 passed;
- related assembly/component tests: 22 passed;
- Ruff: passed;
- promotion artifact:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_trigger_release_promotion_2026-06-04.json`;
- release rows: 1;
- W->C rows: 0;
- C->W rows: 0;
- category-correct not exact-label rows: 1;
- decision: `reject`;
- issue:
  `promotion_gate_expected_all_releases_w_to_c_and_zero_c_to_w`.

Interpretation:

The trigger release proposal should not be promoted into the frozen validation
variant. The released row (`5977`) is category-correct under local Purist
scoring, but the component matrix shows it as `C_to_abstain` before release and
`C_to_C` after release, with gold label `unknown` and proposed label
`multiple per 6 week`. This is not the predeclared 1 W->C / 0 C->W behavior.

Decision: reject trigger-context release promotion for
`hybrid_multi_component_staged_assembly_v0`. The current honest variant remains
the conservative 716-prediction / 34-nonprediction validation candidate. The
next mechanism search must target true held-out generalisation, likely through
validation/synthetic hard panels focused on the deterministic test ceiling,
not through trigger or last-event release.

## Experiment Unit: Failure Recoverability And Oracle Upper Bound

Hypothesis: some conservative assembly validation failures may already have
correct alternatives in saved component candidates, and an oracle recoverability
analysis can identify which component should be targeted by a real selector
ablation.

Minimal change:

- added `assembly_failure_recoverability_v0`;
- joined the staged assembly component matrix to the RQ1 candidate-discovery
  matrix;
- analyzed only conservative assembly W-failure rows (`W_to_W`,
  `W_to_abstain`, `W_to_review`);
- separated exact-label candidates, Purist-category candidates, semantic-state
  only recalls, source/evidence issues, and no-recall rows;
- computed oracle validation upper bounds for exact-label and all actionable
  candidate alternatives.

Surface and policy:

- split: validation;
- split manifest: `gan2026_split_v1`;
- locked test: not inspected;
- scorer/gold policy: unchanged;
- status: validation-development oracle ablation, not a promotable selector.

Commands:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_component_assembly_failure_recoverability.py
python -m ruff check \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/components/assembly_failure_recoverability.py \
  tests/test_gan2026_component_assembly_failure_recoverability.py
python -m pytest tests/test_gan2026_component_assembly_failure_recoverability.py \
  tests/test_gan2026_component_trigger_release_promotion_analysis.py \
  tests/test_gan2026_component_evidence_matrix.py \
  tests/test_gan2026_staged_hybrid_assembly.py \
  tests/test_gan2026_component_staged_decision_policy.py \
  tests/test_gan2026_component_trigger_context_release_rule.py \
  tests/test_gan2026_component_last_event_date_instrumentation.py
```

Results:

- focused recoverability tests: 3 passed;
- related assembly/component tests: 25 passed;
- Ruff: passed;
- recoverability artifact:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_failure_recoverability_2026-06-05.json`;
- failure rows analyzed: 53;
- failure transitions: 38 `W_to_W`, 9 `W_to_abstain`, 6 `W_to_review`;
- actionable candidate rows: 21;
- exact-label actionable rows: 16;
- Purist-category actionable rows: 5;
- semantic-state-only rows: 17;
- no recalled candidate rows: 14;
- one additional row has a candidate with evidence/source issue;
- conservative full-row correct baseline: 678/750;
- exact-label oracle upper bound: 694/750 = 0.9253;
- all-actionable oracle upper bound: 699/750 = 0.9320.

Interpretation:

The validation failure rows contain real recoverable headroom, but it is not
yet an implementable selector. Exact-label alternatives are the strongest signal
and should be the next ablation target. The largest actionable source is split
between `llm_candidate_selector_raw` and `deterministic_candidates_all`; the
former contributes 11 actionable rows, the latter 10. Semantic-state-only rows
are a prompt/projection design target, not a safe direct override.

Decision: continue with a validation-only selector ablation that proposes
non-gold features for choosing exact-label alternatives on the 16 exact-label
recoverable rows. Do not promote the oracle ablation and do not use locked-test
row-level failures.

## Experiment Unit: Exact-Label Selector Ablation V0

Hypothesis: some recoverable validation failures can be selected by non-gold
candidate features, but any selector must be tested across all 750 validation
rows so deterministic-correct damage is visible.

Minimal change:

- added `exact_label_selector_ablation_v0`;
- applied selector predicates across the full component matrix, not only known
  failure rows;
- used only non-gold candidate features for selection;
- used `gold_match_status` only after selection for W->C/C->W accounting;
- added narrow non-prediction LLM-unknown policies after the broad policies
  proved destructive.

Surface and policy:

- split: validation;
- split manifest: `gan2026_split_v1`;
- source artifacts: component matrix plus RQ1 candidate-discovery matrix;
- locked test: not inspected during selector design;
- scorer/gold policy: unchanged.

Commands:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_component_exact_label_selector_ablation.py
python -m ruff check \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/components/exact_label_selector_ablation.py \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/staged_hybrid_assembly.py \
  tests/test_gan2026_component_exact_label_selector_ablation.py
python -m clinical_extraction.tasks.seizure_frequency.gan2026.hybrid.staged_hybrid_assembly --mode validation750
```

Results:

- focused selector tests: 4 passed;
- Ruff: passed;
- ablation artifact:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_exact_label_selector_ablation_2026-06-05.json`;
- conservative base full-row Purist proxy: 678/750 = 0.9040;
- broad deterministic/window selectors: rejected, with 97-116 C->W rows;
- broad LLM unknown selectors: rejected, with 49-122 C->W rows;
- `nonprediction_llm_unknown_current_v0`: 9 selected, 9 W->C, 0 C->W,
  projected 687/750 = 0.9160;
- `nonprediction_llm_unknown_any_v0`: 13 selected, 13 W->C, 0 C->W,
  projected 691/750 = 0.9213.

Interpretation:

The validation-positive selector must be narrow. Broad replacement is unsafe
because it touches many already-correct prediction-bearing rows. The useful
signal is specific to current non-predictions where an exact/source-valid raw
LLM `unknown` candidate exists; those rows already receive no full-row credit
from the conservative candidate.

Decision: freeze `nonprediction_llm_unknown_any_v0` only as a validation
ablation candidate, then run an aggregate-only locked-test audit before making
any promotion claim. Do not inspect test row-level failures.

## Frozen Aggregate Audit: Test450 Nonprediction Selector

Question: does the validation-positive non-prediction selector have enough
surface on the locked holdout to move toward the >=0.9 target?

Surface:

- split: test;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`;
- inspection policy: aggregate counts only, no test row-level failure review;
- candidate-discovery rows were built in memory and not written as a row-level
  selector artifact.

Results:

- aggregate artifact:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_test450_nonprediction_selector_aggregate_audit_2026-06-05.json`;
- base full-row Purist proxy: 342/450 = 0.7600;
- router actions: 449 predict, 1 abstain;
- `nonprediction_llm_unknown_current_v0`: selected 0 rows, projected 0.7600;
- `nonprediction_llm_unknown_any_v0`: selected 0 rows, projected 0.7600;
- broad selectors were damaging on aggregate, projecting 0.6578-0.7044.

Interpretation:

The validation-positive selector does not transfer because the frozen test
router leaves almost no non-prediction surface. This branch explains a
validation recovery mechanism but cannot close the holdout gap.

Decision: reject the nonprediction selector as a path to the locked-test target.
Return to validation/synthetic hard-panel work on a prediction-bearing
selection mechanism.

## Error Analysis: Candidate-Union Selection Headroom

Question: does the existing candidate-union/selected-state branch expose a
better next mechanism than label replacement?

Sources:

- candidate union:
  `experiments/gan2026_candidate_union_saved_artifact_2026-06-04.json`;
- selected-state replay:
  `experiments/gan2026_selected_state_union_replay_v3_2026-06-04.json`;
- selective boundary candidate v3:
  `experiments/gan2026_selective_boundary_candidate_experiment_v3_2026-06-04.json`.

Findings:

- saved candidate union hard panel: 75 rows, union verified recall 47 rows,
  deterministic recall lost rows 0, LLM recall rescue rows 22;
- selected-state union replay: comparator correct 37/75, primary v3 projection
  correct 16/22 scorable rows, safety floor 37/75 with 0 W->C and 0 C->W;
- among the 38 comparator-miss hard-panel rows, 16 have a Purist-correct union
  candidate available;
- naive candidate selectors are destructive:
  `first_union` would project 21/75, and `first_live` would introduce 6 C->W
  rows with 0 W->C.

Interpretation:

The union branch has candidate recall headroom but not a safe selector. The
next architecture step should be a candidate-ranking/verifier component over
small union candidate sets, with validation hard-panel W->C/C->W accounting
before any full-validation or holdout use.

Decision: keep candidate union as the next mechanism branch. Do not spend more
test audits on router packaging or broad LLM candidate replacement.

## Experiment Unit: Candidate-Union Ranker Ablation V0

Hypothesis: the selected-state union has enough candidate recall for a
downstream ranker to recover some comparator misses, but broad candidate ranking
will still be unsafe unless C->W damage is explicitly measured.

Minimal change:

- added `candidate_union_ranker_ablation_v0`;
- evaluated rankers over the existing 75-row selected-state union hard panel;
- used only non-gold candidate features for ranking;
- kept gold labels for post-selection W->C/C->W accounting only;
- included an oracle recoverability count to bound the selector problem.

Surface and policy:

- split: validation hard panel;
- split manifest: `gan2026_split_v1`;
- source artifact:
  `experiments/gan2026_selected_state_union_replay_v3_2026-06-04.jsonl`;
- locked test: not inspected;
- scorer/gold policy: unchanged;
- status: component-ranker ablation, not a whole-pipeline candidate.

Commands:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_component_candidate_union_ranker_ablation.py
python -m ruff check \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/components/candidate_union_ranker_ablation.py \
  tests/test_gan2026_component_candidate_union_ranker_ablation.py
python - <<'PY'
from pathlib import Path
from clinical_extraction.tasks.seizure_frequency.gan2026.components import candidate_union_ranker_ablation as ablation
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import load_jsonl_rows
rows = load_jsonl_rows(Path("experiments/gan2026_selected_state_union_replay_v3_2026-06-04.jsonl"))
ablation_rows = ablation.build_ranker_ablation_rows(rows)
summary = ablation.summarize_ranker_ablation_rows(ablation_rows, rows)
ablation.write_csv_rows(ablation_rows, Path("experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.csv"))
ablation.write_summary_json(summary, Path("experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.json"))
ablation.write_report(
    summary,
    Path("experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.md"),
    csv_path=Path("experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.csv"),
    json_path=Path("experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.json"),
)
PY
```

Results:

- focused ranker tests: 3 passed;
- Ruff: passed;
- ranker artifact:
  `experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.json`;
- hard-panel base comparator: 37/75 = 0.4933;
- oracle recoverable comparator misses: 16; oracle upper bound 53/75 = 0.7067;
- `diary_log_only_v0`: selected 3 rows, 3 W->C, 0 C->W, projected 40/75 =
  0.5333;
- `comparator_absent_quality_rank_v0`: selected 37 rows, 13 W->C, 5 C->W,
  projected 45/75 = 0.6000;
- `unknown_or_cluster_frequency_rank_v0`: selected 17 rows, 3 W->C, 7 C->W,
  projected 33/75 = 0.4400.

Error analysis:

- Clean diary/log recoveries:
  - row `4368`: `diary.date_list`, `5 per 2 month`;
  - row `9496`: `diary.monthly_count_log`, `2 per 5 month`;
  - row `15986`: `diary.sleep_awake_month_summary`, `11 per 3 month`.
- The broader quality ranker gets real extra W->C rows, but its 5 C->W rows are
  all live boundary cluster candidates overriding already-correct comparator
  labels (`338`, `1707`, `6501`, `10618`, `15593`).
- The unknown/cluster frequency ranker is rejected because it repeats the old
  over-selection failure mode: lower-quality frequency candidates beat correct
  cluster/unknown comparator labels.

Interpretation:

Candidate-union selection can move the hard-panel comparator, but only narrow
families are currently safe. Diary/log extraction is the first clean
deterministic subfamily, while live boundary cluster candidates need a verifier
or negative gate before they can affect labels. The hard-panel oracle confirms
there is additional headroom, but the selector is still the bottleneck.

Decision: promote `diary_log_only_v0` only to the next validation-development
stage: full-validation materialization and negative-test expansion. Do not run
locked test, because this is a hard-panel-only ablation without a full
validation750 implementation or freeze gate.

## Experiment Unit: Diary/Log Full-Validation Audit V0

Hypothesis: the clean hard-panel diary/log ranker may survive full-validation
negative exposure if the selected rule ids are frozen narrowly and rejected
diary variants remain visible.

Minimal change:

- added `diary_log_full_validation_audit_v0`;
- froze selected diary rules to `diary.date_list`,
  `diary.monthly_count_log`, and `diary.sleep_awake_month_summary`;
- rejected other `diary.*` rules rather than silently dropping them;
- materialized the audit against all 750 validation rows using the existing
  component matrix as the base assembly surface.

Surface and policy:

- split: validation;
- split manifest: `gan2026_split_v1`;
- source artifacts:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv`
  and `data/Gan (2026)/synthetic_data_subset_1500.json`;
- locked test: not inspected during development;
- scorer/gold policy: unchanged.

Commands:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_component_diary_log_full_validation_audit.py
python -m ruff check \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/components/diary_log_full_validation_audit.py \
  tests/test_gan2026_component_diary_log_full_validation_audit.py
python - <<'PY'
import csv
from pathlib import Path
from clinical_extraction.tasks.seizure_frequency.gan2026.components import diary_log_full_validation_audit as audit
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split, DEFAULT_DATA_PATH, DEFAULT_SPLIT_MANIFEST_PATH
matrix_rows = list(csv.DictReader(open("experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv")))
records = load_records_for_split("validation", data_path=DEFAULT_DATA_PATH, manifest_path=DEFAULT_SPLIT_MANIFEST_PATH)
rows = audit.build_diary_log_audit_rows(matrix_rows, records)
summary = audit.summarize_diary_log_audit_rows(rows, matrix_rows)
audit.write_csv_rows(rows, Path("experiments/gan2026_diary_log_full_validation_audit_2026-06-05.csv"))
audit.write_summary_json(summary, Path("experiments/gan2026_diary_log_full_validation_audit_2026-06-05.json"))
audit.write_report(
    rows,
    summary,
    Path("experiments/gan2026_diary_log_full_validation_audit_2026-06-05.md"),
    csv_path=Path("experiments/gan2026_diary_log_full_validation_audit_2026-06-05.csv"),
    json_path=Path("experiments/gan2026_diary_log_full_validation_audit_2026-06-05.json"),
)
PY
```

Results:

- focused diary/log tests: 3 passed;
- Ruff: passed;
- full-validation artifact:
  `experiments/gan2026_diary_log_full_validation_audit_2026-06-05.json`;
- base full-row Purist proxy: 678/750 = 0.9040;
- selected diary/log rows: 2;
- selected transitions: 2 W->C, 0 C->W;
- projected full-row Purist proxy: 680/750 = 0.9067;
- rejected diary/log rows: 3;
- rejected rules: `diary.increasing_monthly_count` x2 and
  `diary.seizure_day_log` x1.

Interpretation:

The selected diary/log subset is clean on full validation, but tiny. The
negative exposure matters: `diary.increasing_monthly_count` is a real regression
risk and must stay excluded.

Decision: freeze the selected diary/log rule ids for one aggregate-only
locked-test audit. Do not inspect or write test row-level failure artifacts.

## Frozen Aggregate Audit: Diary/Log Test450

Question: does the validation-frozen diary/log rule subset transfer to the
locked test surface and move the candidate toward the >=0.9 target?

Surface:

- split: test;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`;
- inspection policy: aggregate counts only, no row-level test failure review or
  row-level output artifact;
- scorer/gold/split policy: unchanged.

Results:

- aggregate artifact:
  `experiments/gan2026_diary_log_test450_aggregate_audit_2026-06-05.json`;
- base full-row Purist proxy: 342/450 = 0.7600;
- selected diary/log rows: 0;
- rejected diary/log rows: 0;
- projected full-row Purist proxy: 342/450 = 0.7600.

Interpretation:

The full-validation-clean diary/log subset has no holdout effect on this test
surface because it selects 0 rows. It is safe but not useful for reaching the
>=0.9 holdout target.

Decision: reject diary/log selection as a target-moving mechanism. Return to
the larger candidate-union selector/verifier problem; the next mechanism must
affect prediction-bearing rows without the live-boundary cluster C->W failures
seen in the hard-panel ablation.

## Experiment Unit: Structural-Guard Candidate-Union Ranker V0

Hypothesis: the broader candidate-union ranker can be made safe if it keeps the
non-gold `comparator_absent` condition but adds structural negative gates learned
from validation hard-panel C->W analysis: suppress live boundary cluster
candidates, suppress seizure-free replacements, and require cluster-shaped
replacements when the comparator is already cluster-shaped.

Minimal change:

- extended `candidate_union_ranker_ablation_v0` with
  `comparator_absent_structural_guard_rank_v0`;
- added tests for comparator-present abstention, live boundary cluster
  suppression, seizure-free suppression, and cluster-shape preservation;
- regenerated the 75-row selected-state union hard-panel ablation artifact.

Surface:

- split: validation hard panel;
- split manifest: `gan2026_split_v1`;
- source artifact:
  `experiments/gan2026_selected_state_union_replay_v3_2026-06-04.jsonl`;
- locked test: not inspected;
- scorer/gold policy: unchanged.

Results:

- hard-panel artifact:
  `experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.json`;
- base hard-panel proxy: 37/75 = 0.4933;
- `comparator_absent_quality_rank_v0`: 13 W->C, 5 C->W, projected 45/75;
- `comparator_absent_structural_guard_rank_v0`: 10 W->C, 0 C->W, 4 C->C,
  10 W->W, projected 47/75 = 0.6267;
- `diary_log_only_v0`: 3 W->C, 0 C->W, projected 40/75;
- `unknown_or_cluster_frequency_rank_v0`: rejected, 3 W->C and 7 C->W.

Interpretation:

The live-boundary negative gates explain the hard-panel C->W failures and make
the broader ranker clean on the hard panel, though at the cost of 3 possible
rescues. This is worth full-validation expansion, but only as a frozen
validation-development policy.

Decision: promote `comparator_absent_structural_guard_rank_v0` to full
validation materialization before any holdout use.

## Experiment Unit: Structural-Guard Full-Validation Audit V0

Hypothesis: the hard-panel-clean structural guard will remain clean on all 750
validation rows when applied to deterministic candidate replay over the
conservative assembly component matrix.

Minimal change:

- added `structural_guard_full_validation_audit_v0`;
- reused the hard-panel ranker policy rather than duplicating selection logic;
- materialized validation row-level audit artifacts only on the validation
  split.

Surface:

- split: validation;
- split manifest: `gan2026_split_v1`;
- base matrix:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv`;
- locked test: not inspected;
- scorer/gold policy: unchanged.

Results:

- full-validation artifact:
  `experiments/gan2026_structural_guard_full_validation_audit_2026-06-05.json`;
- base full-row Purist proxy: 678/750 = 0.9040;
- selected rows: 34;
- transitions: 21 W->C, 0 C->W, 4 C->C, 9 W->W;
- projected full-row Purist proxy: 699/750 = 0.9320;
- decision: `freeze_candidate_for_aggregate_audit`.

Interpretation:

The structural guard is validation-clean and reaches the same 699/750 validation
ceiling as the all-actionable oracle from failure recoverability, but this
improvement is dominated by validation nonprediction repair. It needs a frozen
aggregate-only holdout audit before any target claim.

Decision: freeze the exact policy for one aggregate-only locked-test audit. Do
not inspect or write test row-level failures.

## Frozen Aggregate Audit: Structural-Guard Test450

Question: does the validation-frozen comparator-absent structural guard transfer
to the locked test surface and reach the >=0.9 Purist target?

Surface:

- split: test;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`;
- base score layer: `hybrid_adjudicator_raw`, matching the prior 342/450
  aggregate proxy;
- inspection policy: aggregate counts only, no row-level test failure review or
  row-level output artifact;
- scorer/gold/split policy: unchanged.

Results:

- aggregate artifact:
  `experiments/gan2026_structural_guard_test450_aggregate_audit_2026-06-05.json`;
- base full-row Purist proxy: 342/450 = 0.7600;
- selected rows: 9;
- transitions: 1 W->C, 0 C->W, 7 C->C, 1 W->W;
- projected full-row Purist proxy: 343/450 = 0.7622.

Interpretation:

The structural guard generalizes as high precision but not high coverage: it
does not damage holdout rows, but it selects too few useful rows to move toward
the >=0.9 target. The validation gain came largely from nonprediction repair
opportunities that are not present on this holdout surface.

Decision: reject structural-guard selection as a target-reaching mechanism. Do
not tune from holdout row identities. Return to validation-only mechanism design
focused on prediction-bearing row improvements, not more nonprediction repair.

## Experiment Unit: GPT-4.1 Prediction-Bearing Hard-Slice Smoke

Hypothesis: the current hybrid parallel state candidate reasoner may become
useful on prediction-bearing misses if run with a stronger hosted model, because
the previous validation-clean deterministic gates mostly repaired
nonprediction rows and did not transfer to holdout.

Minimal change:

- no prompt/code behavior change;
- reused `hybrid_parallel_state_candidate_reasoner_v0`;
- switched live model from prior `openai/gpt-4.1-mini` surfaces to
  `openai/gpt-4.1`;
- ran a validation-only hard-slice smoke of 20 prediction-bearing validation
  misses plus 20 prediction-bearing validation controls.

Surface:

- split: validation;
- split manifest: `gan2026_split_v1`;
- row policy: validation hard slice, row-level review allowed;
- locked test: not touched;
- scorer/gold/split policy: unchanged.

Results:

- artifacts:
  `experiments/gan2026_parallel_reasoner_gpt41_prediction_bearing_hardslice40_validation_2026-06-05.jsonl`
  and
  `experiments/gan2026_parallel_reasoner_gpt41_prediction_bearing_hardslice40_validation_2026-06-05.md`;
- rows: 40;
- call failures: 0;
- structured LLM candidate records: 39/40;
- structured adjudicator records: 40/40;
- parse/schema failures: 1;
- selected evidence exact: 40/40;
- selected source ids valid: 40/40;
- deterministic top Purist: 20/40;
- hybrid adjudicator raw Purist: 13/40;
- hybrid adjudicator with adapters Purist: 20/40;
- adapter-only sidecar Purist: 20/40;
- deterministic-correct regressions: 0 because the safety/adapters collapsed
  back to deterministic behavior;
- adapter changed rows: 8, but net hard-slice Purist did not improve.

Interpretation:

The stronger model is operational and structurally clean enough to run, but the
current full-replacement adjudicator prompt shape is not the missing mechanism.
Raw adjudication regressed badly on the hard slice, and the safety/adapted
layers preserved the deterministic baseline rather than rescuing misses.

Decision: reject scaling this prompt shape. The next model-backed experiment
should be a change-only verifier over candidate alternatives with an explicit
default-to-current-label policy, not another full-label adjudicator.

## Experiment Unit: Change-Only Candidate Verifier V0

Hypothesis: a model-backed verifier may be useful if it is not asked to solve
the full row. Instead, it should compare the current candidate label with one
proposed alternative and default to the current label unless the proposed
alternative is clearly supported, clearly the best current/recent answer, and
the current label has a material clinical error.

Minimal change:

- added `change_only_candidate_verifier_v0`;
- enforced a conservative switch gate in code:
  - recommendation must be `switch_to_proposed`;
  - proposed evidence must support the proposed label;
  - proposed label must be the best current/recent answer;
  - current label must have a material error;
  - confidence must be high;
  - evidence quotes must be exact substrings;
  - proposed label must parse as a Gan-compatible label;
- added focused unit tests for strict switching, exact quote requirements, and
  parseable proposed-label requirements.

Focused verification:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_component_change_only_candidate_verifier.py
python -m ruff check \
  src/clinical_extraction/tasks/seizure_frequency/gan2026/components/change_only_candidate_verifier.py \
  tests/test_gan2026_component_change_only_candidate_verifier.py
```

Result: 5 tests passed; Ruff passed.

### Calibration Panel

Surface:

- split: validation;
- panel: 12 prediction-bearing recoverable misses plus 12 validation-correct
  controls with plausible differing alternatives;
- model: `openai/gpt-4.1`;
- locked test: not inspected;
- gold labels: used only for panel construction and post-selection accounting,
  not in model input.

Artifacts:

- panel:
  `experiments/gan2026_change_only_verifier_calibration_panel_2026-06-05.jsonl`;
- live run:
  `experiments/gan2026_change_only_verifier_calibration_gpt41_2026-06-05.json`;
- same-raw-output reparse:
  `experiments/gan2026_change_only_verifier_calibration_gpt41_reparse_2026-06-05.json`.

Results:

- initial live run: 10 W->C, 2 C->W, 2 W->W, 10 C->C;
- C->W analysis showed both regressions were Gan-format paraphrases
  (`every 6 days`, `every 2 days`) of already-correct current labels;
- after the parseable proposed-label gate, same raw outputs reparse to 10 W->C,
  0 C->W, 2 W->W, 12 C->C, projected 22/24 = 0.9167.

Decision: the task shape is promising, but only after deterministic
Gan-compatible switch gating. Expand calibration before any production selector
or holdout use.

### Expanded Calibration Panel

Surface:

- split: validation;
- panel: all 15 identified prediction-bearing recoverable misses plus 45
  validation-correct controls;
- model: `openai/gpt-4.1`;
- raw-output reuse: 24 rows reused from the first calibration, 35 new model-call
  rows;
- locked test: not inspected.

Artifacts:

- panel:
  `experiments/gan2026_change_only_verifier_expanded_calibration_panel_2026-06-05.jsonl`;
- live/reuse run:
  `experiments/gan2026_change_only_verifier_expanded_calibration_gpt41_2026-06-05.json`.

Results:

- base panel proxy: 45/60 = 0.7500;
- projected proxy: 57/60 = 0.9500;
- transitions: 12 W->C, 0 C->W, 3 W->W, 45 C->C;
- call OK rows: 59/60;
- parse OK rows: 59/60;
- exact quote rows: 51/60;
- changed-label precision: 1.000 on this constructed panel.

Decision: promote only as a calibration signal. This does not yet prove a
deployable proposal generator, because the positive rows were selected using
validation gold for panel construction.

### Full Family Audit: Seizure-Free Current Label vs LLM Unknown Alternative

Question: can the change-only verifier safely filter a non-gold proposal family
that is dangerous when blindly switched?

Surface:

- split: validation;
- family: prediction-bearing current label starts with `seizure free`, and a
  saved LLM candidate proposes parseable `unknown`;
- rows: 38;
- model: `openai/gpt-4.1`;
- raw-output reuse: 7 rows reused, 31 new model-call rows;
- locked test: not inspected.

Artifact:

- `experiments/gan2026_change_only_verifier_sf_unknown_family_gpt41_2026-06-05.json`.

Results:

- base family proxy: 31/38 = 0.8158;
- projected proxy: 26/38 = 0.6842;
- transitions: 5 W->C, 10 C->W, 2 W->W, 21 C->C;
- changed-label precision: 0.3333;
- decision: reject.

Error analysis:

The verifier over-switches when the current label is a seizure-free label with
over-broad duration wording. It often recommends `unknown` because the note
supports only `seizure free for multiple month` rather than `seizure free for
multiple year`, but the benchmark Purist mapping still treats those rows as
seizure-free-correct. This is a benchmark-convention/duration-specific failure,
not a useful current seizure-frequency correction.

Decision: reject the broad seizure-free-to-unknown proposal family. The next
version must add a non-gold duration-preservation gate: `unknown` may not
override a seizure-free current label merely because duration is imprecise; it
needs clear active current seizure evidence.

## Same-Output Reparse: Seizure-Free/Unknown Active-Event Gate

Hypothesis: the rejected seizure-free-to-unknown family can be made safe if
`unknown` is allowed to override a seizure-free current label only when the
model output names active current seizure-like evidence, rather than merely
objecting to imprecise seizure-free duration.

Minimal change:

- extended `change_only_candidate_verifier_v0` with an active-event
  duration-preserving gate for `seizure free*` current labels versus `unknown`
  proposed labels;
- added tests for duration-only blocking and active-event switching;
- reparsed the saved validation family raw outputs with no new model calls.

Surface:

- split: validation;
- source artifact:
  `experiments/gan2026_change_only_verifier_sf_unknown_family_gpt41_2026-06-05.jsonl`;
- model output: reused same raw `openai/gpt-4.1` outputs;
- locked test: not inspected.

Results:

- reparse artifact:
  `experiments/gan2026_change_only_verifier_sf_unknown_family_gpt41_reparse_2026-06-05.json`;
- rows: 38;
- transitions after gate: 7 W->C, 0 C->W, 31 C->C;
- projected family proxy: 38/38 = 1.0000;
- changed-label precision: 1.0000;
- new model calls: 0.

Decision: freeze this family policy for one aggregate-only locked-test audit.
Do not write test row-level raw outputs or failure rows.

## Frozen Aggregate Audit: Seizure-Free/Unknown Test450

Question: does the validation-frozen active-event gate for seizure-free current
labels versus LLM `unknown` alternatives transfer to locked test and move the
candidate toward the >=0.9 target?

Surface:

- split: test;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`;
- base score layer: `hybrid_adjudicator_raw`;
- inspection policy: aggregate counts only, no row-level test failure review or
  row-level output artifact;
- model: `openai/gpt-4.1`;
- scorer/gold/split policy: unchanged.

Results:

- aggregate artifact:
  `experiments/gan2026_change_only_verifier_sf_unknown_test450_aggregate_audit_2026-06-05.json`;
- eligible rows: 16;
- eligible transitions: 13 C->C, 3 W->W;
- base full-row Purist proxy: 342/450 = 0.7600;
- projected full-row Purist proxy: 342/450 = 0.7600.

Interpretation:

The active-event gate generalizes as non-destructive on this holdout family, but
it finds no W->C holdout corrections. The family is therefore safe but not a
target-moving mechanism for the >=0.9 holdout goal.

Decision: reject seizure-free-to-unknown as the next target path. Continue
validation-only mechanism search on higher-coverage prediction-bearing failure
families.

## Change-Only Verifier: Deterministic/State Exact Alternatives

Question: can the change-only verifier safely filter deterministic/state exact
frequency or cluster alternatives that are dangerous when blindly switched?

### Calibration And Error Analysis

Surface:

- split: validation;
- panel: 6 known deterministic/state exact-alternative positives plus 55
  validation-correct controls;
- model: `openai/gpt-4.1`;
- locked test: not inspected.

Artifacts:

- panel:
  `experiments/gan2026_change_only_verifier_det_state_alt_calibration_panel_2026-06-05.jsonl`;
- live run:
  `experiments/gan2026_change_only_verifier_det_state_alt_calibration_gpt41_2026-06-05.json`;
- same-output reparse:
  `experiments/gan2026_change_only_verifier_det_state_alt_calibration_gpt41_reparse_2026-06-05.json`.

Initial result: 6 W->C, 5 C->W, 50 C->C. Error analysis showed recurring
benchmark-convention failures: subtype narrowing to absence or tonic-clonic
events, uncertain seizure-free override, and partial-window narrowing.

Minimal change:

- added benchmark-convention gates to the change-only verifier for subtype
  narrowing, uncertain seizure-free override, partial-window/year-to-date
  narrowing, named-semiology narrowing, single-event unknown-to-rate conversion,
  imprecise cluster candidates when exact per-cluster count is available, and
  obvious arithmetic contradictions;
- added focused tests for these switch-blocking families.

Reparse result: 6 W->C, 0 C->W, 55 C->C, projected panel 61/61 = 1.0000.

Decision: expand to the full validation family before any holdout use.

### Full Validation Family

Surface:

- split: validation;
- family: one non-gold deterministic/state exact `frequency_rate` or
  `cluster_frequency` alternative per staged-assembly row, ranked
  deterministic before state graph and frequency before cluster;
- rows: 149;
- model: `openai/gpt-4.1`;
- raw-output reuse: 148 saved outputs reused after the convention gates, 1 new
  retry for a transient previous 503 row;
- locked test: not inspected.

Artifact:

- `experiments/gan2026_change_only_verifier_det_state_alt_full_family_gpt41_2026-06-05.json`.

Results:

- family base proxy: 138/149 = 0.9262;
- family projected proxy: 142/149 = 0.9530;
- whole-validation staged proxy: 697/750 -> 701/750 = 0.9347;
- transitions: 4 W->C, 0 C->W, 7 W->W, 138 C->C;
- changed-label precision: 1.0000;
- exact quote rows: 141/149.

Decision: promote only to a frozen aggregate-only locked-test audit. The
validation gain is clean but small, so this branch cannot plausibly reach the
0.9 holdout target by itself.

### Frozen Aggregate Audit: Deterministic/State Test450

Surface:

- split: test;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`;
- base score layer: `hybrid_adjudicator_raw`;
- proposal policy: same non-gold deterministic/state exact-alternative ranker
  as validation;
- inspection policy: aggregate counts only; no test row ids, raw model outputs,
  clinical text, or row-level failures written;
- model: `openai/gpt-4.1`.

Artifact:

- `experiments/gan2026_change_only_verifier_det_state_alt_test450_aggregate_audit_2026-06-05.json`.

Results:

- eligible rows: 92/450;
- transitions: 9 W->C, 1 C->W, 7 W->W, 75 C->C;
- changed-label precision: 0.9000;
- base full-row Purist proxy: 342/450 = 0.7600;
- projected full-row Purist proxy: 350/450 = 0.7778.

Interpretation:

The branch transfers better than prior tiny selectors but remains far below the
requested Purist F1 >= 0.9 test target. Because the test audit exposed only
aggregate counts and no row-level failures, follow-up tuning must return to
validation-only family discovery rather than exploiting holdout errors.

Decision: retain as a small positive component candidate but reject it as a
goal-achieving architecture variant.

## Change-Only Verifier: LLM-Selector Exact Alternatives

Question: can the change-only verifier safely filter higher-recall exact
alternatives from `llm_candidate_selector_raw`?

### Calibration Panel

Surface:

- split: validation;
- ranker: one exact `llm_candidate_selector_raw` alternative per row, ranked
  `frequency_rate` before `unknown_frequency` before `cluster_frequency` before
  `last_event_only`;
- panel: 13 recoverable positives plus 75 regression controls sampled across
  candidate kinds;
- model: `openai/gpt-4.1`;
- locked test: not inspected.

Artifacts:

- panel:
  `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_panel_2026-06-05.jsonl`;
- initial live/reuse run:
  `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_gpt41_2026-06-05.json`;
- stricter same-output reparse:
  `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_gpt41_reparse_2026-06-05.json`.

Initial result: 7 W->C, 9 C->W, 6 W->W, 66 C->C; changed-label precision
0.4375. Error analysis showed history-only `unknown` overrides, subtype
narrowing to clinically emphasized events, recent-month diary narrowing,
interval/rate misread, and exact-label reformulations.

Minimal change:

- extended `change_only_candidate_verifier_v0` with conservative gates for
  history-only unknown overrides, clinically-more-significant subtype
  narrowing, recent-month/this-month/year-to-date narrowing, uncertain-reporting
  overrides, exact-label reformulation, and composite `then seizure free`
  labels;
- added focused tests for the new gates.

Calibration reparse: 7 W->C, 0 C->W, 6 W->W, 75 C->C; projected panel
82/88 = 0.9318. Decision: expand to full validation family before any holdout
use.

### Full Validation Family

Surface:

- split: validation;
- family: all 281 rows with a non-current exact LLM-selector alternative under
  the frozen frequency-first ranker;
- raw-output policy: saved full-family outputs reused after gate changes;
- locked test: not inspected.

Artifacts:

- full-family run:
  `experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_2026-06-05.json`;
- first reparse:
  `experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_reparse_2026-06-05.json`;
- final reparse:
  `experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_reparse2_2026-06-05.json`.

Final validation result:

- family base proxy: 260/281 = 0.9253;
- family projected proxy: 267/281 = 0.9502;
- whole-validation staged proxy: 697/750 -> 704/750 = 0.9387;
- transitions: 7 W->C, 0 C->W, 14 W->W, 260 C->C;
- changed-label precision: 1.0000;
- exact quote rows: 269/281.

Decision: promote only to a frozen aggregate-only locked-test audit. The branch
is validation-clean but still too small to plausibly reach 0.9 by itself.

### Frozen Aggregate Audit: LLM-Selector Test450

Surface:

- split: test;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`;
- base score layer: `hybrid_adjudicator_raw`;
- proposal policy: same exact LLM-selector ranker and verifier gates as
  validation;
- inspection policy: aggregate counts only; no test row ids, raw model outputs,
  clinical text, or row-level failures written;
- model: `openai/gpt-4.1`.

Artifact:

- `experiments/gan2026_change_only_verifier_llm_selector_exact_test450_aggregate_audit_2026-06-05.json`.

Results:

- eligible rows: 161/450;
- call OK rows: 159/161;
- transitions: 7 W->C, 2 C->W, 34 W->W, 118 C->C;
- changed-label precision: 0.7778;
- base full-row Purist proxy: 342/450 = 0.7600;
- projected full-row Purist proxy: 347/450 = 0.7711.

Interpretation:

The branch is validation-clean after conservative gates, but the frozen
aggregate-only holdout audit again shows poor transfer and far too little net
movement for the requested Purist F1 >= 0.9 target. Because the test audit
stored only aggregate counts, no follow-up tuning can use holdout row details.

Decision: reject exact LLM-selector switching as a goal-achieving path. Continue
with validation-only mechanism search; likely next directions are new
candidate-generation coverage or a different architecture, not another gate on
the same exact-alternative selector.

## Combined Change-Only Switch Layer

Question: if the validation-clean deterministic/state and LLM-selector
change-only switch families are composed into one scorer-facing switch layer,
does the combined architecture variant transfer better than either family
alone?

Policy:

- base label: staged reasoner scorer-facing label, matching prior
  `hybrid_adjudicator_raw` aggregate audits;
- family priority: `det_state_exact`, then `llm_selector_exact`, then
  `keep_current`;
- deterministic/state and LLM-selector family gates are exactly the validation
  gates frozen above;
- structural-guard and diary/log branches are excluded from this composition
  because their validation baseline is the conservative nonprediction component
  matrix, not the same scorer-facing current-label surface.

### Validation Composition

Artifacts:

- row JSONL:
  `experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.jsonl`;
- summary:
  `experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.json`;
- report:
  `experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.md`.

Results:

- base full-row Purist proxy: 697/750 = 0.9293;
- projected full-row Purist proxy: 708/750 = 0.9440;
- changed rows: 34;
- transitions: 11 W->C, 0 C->W, 42 W->W, 697 C->C;
- selected-family counts: 9 deterministic/state, 25 LLM-selector.

Decision: validation-clean; freeze this exact composition for one
aggregate-only holdout audit.

### Frozen Aggregate Audit: Combined Test450

Surface:

- split: test;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`;
- model: `openai/gpt-4.1`;
- inspection policy: aggregate counts only; no test row ids, raw model outputs,
  clinical text, or row-level failures written.

Artifact:

- `experiments/gan2026_combined_change_only_switch_layer_test450_aggregate_audit_2026-06-05.json`.

Results:

- call OK rows: 446/450;
- changed rows: 31;
- selected-family counts: 10 deterministic/state, 21 LLM-selector;
- transitions: 13 W->C, 1 C->W, 95 W->W, 341 C->C;
- changed-label precision: 0.9286;
- base full-row Purist proxy: 342/450 = 0.7600;
- projected full-row Purist proxy: 354/450 = 0.7867.

Interpretation:

This is the best frozen aggregate holdout movement from the switch-layer family
so far, but it is still far below the requested Purist F1 >= 0.9. The result
strongly suggests that validation-clean switching among already-saved exact
alternatives is not enough; the next mechanism needs new candidate-generation
coverage or a more fundamental architecture change, not more gates over the
same candidate pool.

Decision: reject the combined switch layer as a goal-achieving architecture
variant. Keep it as a positive component ablation and move mechanism search
beyond saved exact-alternative switching.

## Direct-Labeler Candidate Generation And Targeted Switch

Question: can a stronger direct labeler create new alternatives for rows where
the saved candidate pool has no exact recoverable option, and can the
change-only verifier gate those alternatives without regressing current-correct
validation rows?

### Hard Failure Slice

Surface:

- split: validation;
- slice: 31 current assembly failures, limited to 14
  `no_recalled_candidate` and 17 `semantic_state_only` rows;
- model: `openai/gpt-4.1`;
- current label: combined switch-layer validation label where available.

Artifacts:

- `experiments/gan2026_direct_labeler_unrecalled_failure_slice_gpt41_2026-06-05.jsonl`;
- `experiments/gan2026_direct_labeler_unrecalled_failure_slice_gpt41_2026-06-05.json`;
- `experiments/gan2026_direct_labeler_unrecalled_failure_slice_gpt41_2026-06-05.md`.

Results after schema-alias repair:

- calls OK: 31/31;
- direct correct rows: 21/31;
- exact evidence rows: 28/31;
- direct-label transitions against the current label: 21 W->C, 0 C->W, 10 W->W;
- oracle targeted projection if all direct-correct slice rows switched:
  729/750 = 0.9720.

Interpretation:

Direct extraction is a real new candidate source on unrecalled and
semantic-state-only validation failures. It is not, by itself, a safe broad
replacement policy.

### Current-Correct Control Slice

Surface:

- split: validation;
- slice: 31 deterministic current-correct controls from the component matrix;
- model and prompt: same as hard failure slice.

Artifacts:

- `experiments/gan2026_direct_labeler_current_correct_control31_gpt41_2026-06-05.jsonl`;
- `experiments/gan2026_direct_labeler_current_correct_control31_gpt41_2026-06-05.json`;
- `experiments/gan2026_direct_labeler_current_correct_control31_gpt41_2026-06-05.md`.

Results:

- calls OK: 31/31;
- direct correct rows: 21/31;
- direct-label transitions: 21 C->C, 10 C->W.

Interpretation:

The control slice confirms high regression pressure. Direct labels must be
treated only as alternatives behind a gate, not as replacement predictions.

### Full Validation Direct Candidate Surface

Surface:

- split: validation750;
- current label: combined switch-layer validation label;
- model: `openai/gpt-4.1`;
- policy: direct labeler proposes a candidate for every row; validation gold is
  used only for accounting.

Artifacts:

- `experiments/gan2026_direct_labeler_full_validation750_over_combined_current_gpt41_2026-06-05.jsonl`;
- `experiments/gan2026_direct_labeler_full_validation750_over_combined_current_gpt41_2026-06-05.json`;
- `experiments/gan2026_direct_labeler_full_validation750_over_combined_current_gpt41_2026-06-05.md`.

Results:

- calls OK: 750/750;
- raw direct correct rows: 405/750 = 0.5400;
- exact evidence rows: 485/750;
- direct replacement transitions: 26 W->C, 329 C->W.

Interpretation:

The full surface confirms the direct labeler is useful only as a noisy
candidate generator. Broad replacement is destructive.

### Full Validation Change-Only Verifier

Surface:

- exact-evidence direct alternatives that differ from the combined current
  label: 225 rows;
- model: `openai/gpt-4.1`;
- gate: `gan2026_change_only_candidate_verifier_v0`.

Artifacts:

- `experiments/gan2026_direct_labeler_full_validation750_change_only_verifier_gpt41_2026-06-05.jsonl`;
- `experiments/gan2026_direct_labeler_full_validation750_change_only_verifier_gpt41_2026-06-05.json`;
- `experiments/gan2026_direct_labeler_full_validation750_change_only_verifier_gpt41_2026-06-05.md`.

Results:

- verifier panel transitions: 11 W->C, 25 C->W, 19 W->W, 170 C->C;
- projected full-validation score: 694/750 = 0.9253;
- changed-label precision: 0.3056.

Interpretation:

The broad verifier gate is not sufficient for direct-labeler alternatives.
Regression rows are dominated by seizure-free recency traps, partial-window
rewrites, and count-window narrowing.

### Targeted Direct Switch V0

Policy:

- start from the combined switch-layer validation label;
- require the change-only verifier to choose `switch_to_proposed`;
- allow only these non-gold feature families:
  `direct_unknown_from_current_seizure_free`,
  `direct_cluster_per_cluster_completion`, and
  `direct_daily_upgrade_from_non_daily_current`.

Artifacts:

- `experiments/gan2026_direct_labeler_targeted_switch_validation750_2026-06-05.jsonl`;
- `experiments/gan2026_direct_labeler_targeted_switch_validation750_2026-06-05.json`;
- `experiments/gan2026_direct_labeler_targeted_switch_validation750_2026-06-05.md`.

Results:

- selected rows: 20;
- transitions: 9 W->C, 0 C->W, 7 W->W, 4 C->C;
- base combined switch-layer validation score: 708/750 = 0.9440;
- projected validation score: 717/750 = 0.9560;
- changed-label precision: 1.0000.

Decision:

Freeze `gan2026_direct_labeler_targeted_switch_v0` for a locked-test
aggregate-only audit. No test row-level inspection is authorized.

### Frozen Aggregate Audit: Targeted Direct Switch Test450

Surface:

- split: test;
- source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`;
- current label: recomputed combined switch-layer label;
- direct candidate generator: `gan2026_llm_only_direct_labeler_v0.1`;
- targeted policy: `gan2026_direct_labeler_targeted_switch_v0`;
- model: `openai/gpt-4.1`;
- inspection policy: aggregate counts only; no test row ids, raw model outputs,
  clinical text, or row-level failures written.

Artifacts:

- `experiments/gan2026_direct_labeler_targeted_switch_test450_aggregate_audit_2026-06-05.json`;
- `experiments/gan2026_direct_labeler_targeted_switch_test450_aggregate_audit_2026-06-05.md`.

Results:

- raw base Purist proxy: 342/450 = 0.7600;
- recomputed combined current Purist proxy: 353/450 = 0.7844;
- targeted final Purist proxy: 354/450 = 0.7867;
- direct calls OK: 450/450;
- direct exact-evidence rows: 282/450;
- targeted selected rows: 4;
- targeted transitions: 1 W->C, 0 C->W, 96 W->W, 353 C->C;
- targeted changed-label precision: 1.0000.

Interpretation:

The targeted direct switch transfers safely but with negligible coverage. It
does not improve on the best prior aggregate holdout score and remains far
below the requested Purist F1 >= 0.9 threshold. The validation-to-test mismatch
again suggests that high-precision gates over narrow validation recoverability
families are not enough.

Decision: reject `gan2026_direct_labeler_targeted_switch_v0` as a
goal-achieving architecture variant. Continue with validation-only mechanism
search for materially broader prediction-bearing coverage; no test row-level
follow-up is authorized.

## Train-Exemplar Few-Shot Candidate Generator

Question: can retrieved train-set exemplars give the LLM a broader
prediction-bearing candidate source than direct note-only extraction, while
keeping test split discipline intact?

### Train-Only Lexical Retrieval Smoke

Surface:

- train split: 300 labeled examples;
- validation split: 750 examples;
- method: hand-rolled TF-IDF-like unigram/bigram retrieval with train gold label
  copied from the nearest neighbor;
- no test row-level use.

Result:

- nearest train-exemplar validation Purist proxy: 239/750 = 0.3187;
- naive replacement over the combined current label is destructive.

Decision: reject train-nearest-label replacement. Use retrieval, if at all,
only as LLM context.

### Few-Shot Direct Labeler Hard/Control Panel

Surface:

- split: validation;
- panel: all 42 combined-current validation misses plus 42 deterministic
  current-correct controls;
- retrieved context: top 3 train examples by lexical similarity, including
  train gold label/reference and note excerpt;
- model: `openai/gpt-4.1`;
- parser policy: same direct-labeler parser with schema-alias repairs.

Artifacts:

- `experiments/gan2026_fewshot_train_exemplar_direct_labeler_hard_control84_validation_2026-06-05.jsonl`;
- `experiments/gan2026_fewshot_train_exemplar_direct_labeler_hard_control84_validation_2026-06-05.json`;
- `experiments/gan2026_fewshot_train_exemplar_direct_labeler_hard_control84_validation_2026-06-05.md`.

Results:

- panel current-correct rows: 42/84;
- candidate-correct rows: 61/84;
- transitions: 27 W->C, 8 C->W, 15 W->W, 34 C->C;
- exact evidence rows: 76/84.

Interpretation:

Retrieved train exemplars materially improve hard-slice candidate generation,
but raw switching is unsafe due to 8 current-correct regressions.

### Few-Shot Change-Only Verifier Panel

Surface:

- exact-evidence few-shot alternatives that differed from the current label:
  49 rows;
- verifier: `gan2026_change_only_candidate_verifier_v0`;
- model: `openai/gpt-4.1`.

Artifacts:

- `experiments/gan2026_fewshot_train_exemplar_change_only_verifier_panel49_validation_2026-06-05.jsonl`;
- `experiments/gan2026_fewshot_train_exemplar_change_only_verifier_panel49_validation_2026-06-05.json`;
- `experiments/gan2026_fewshot_train_exemplar_change_only_verifier_panel49_validation_2026-06-05.md`.

Results:

- verifier transitions: 6 W->C, 3 C->W, 27 W->W, 13 C->C;
- verifier action counts: 30 switch, 18 keep, 1 human review;
- evidence exact rows: 49/49.

Interpretation:

The few-shot candidate generator has the broadest validation hard-slice rescue
signal so far, but the current change-only verifier is not sufficient for safe
promotion on this broader candidate family. The 3 C->W rows are concentrated
in no-reference/frequency and seizure-free recency traps; stricter non-gold
filters can make a smaller clean subset, but the clean subset is too narrow to
justify a full-validation freeze yet.

Decision: continue validation-only development. Next promising mechanism is a
few-shot-specific verifier or structured candidate contract that preserves the
27 W->C hard-slice coverage while blocking the observed no-reference and
recency regressions.
