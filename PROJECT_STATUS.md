# Project status

Last updated: 2026-07-18 on the working tree after commit `7bc1db7`

## Current outcome

The fixed one-call ExECTv2 comparison is implemented for all six selected
models on `dev140` and has aggregate-only `test60` results for the same six
models. The retained aggregate panel records all six test60 conditions with
equal canonical status; sealed row artifacts remain ignored and uninspectable.

Gan has a matched six-model aggregate-only `test450` panel under prompt v0.7:
all six conditions are recorded in the committed aggregate panel. The separate
v0.5 hosted comparison has complete GPT-4.1-mini, Luna, and Sol conditions.
Sol's previously undocumented continuation completed at 373/450 Purist.
DeepSeek has 350 unique sealed rows and is running the remaining 100.

A user-authorized extension is adding Qwen and Gemma test450 conditions under
the same v0.5 prompt, followed by Qwen validation750. The cancelled Qwen v0.7
validation run stopped at 367/750 rows and is not evidence for the new queue.

These panels are retained paper evidence with aggregate-only holdout limits.
Qwen and Gemma have the same claim status as the four hosted models; their
local routes and no-call aggregate reparse provenance remain explicit caveats.

The requested six-model comparison report is complete. A predeclared no-call
ExECT Seizure Frequency reliability replay also covers all six models on
`dev140`. Its intended unknown-only denominator is empty, so it closes that
cross-task question as unmeasurable from current ExECT gold rather than
substituting empty-gold rows.

The shared paper-facing reliability framework is implemented in the working
tree. Gan and ExECT now have explicit results for the same eight questions,
with task-specific measures, assurance metadata, evidence states,
comparability labels, and gap decisions. The generated machine and human
scorecards do not pool incompatible values or calculate a composite score.

## Fresh evidence

### ExECTv2 fixed one-call comparison

All six `dev140` runs use the decision-0040 model-led family boundary,
decision-0041 single-call architecture, prompt
`exectv2_hybrid_key_family_event_ledger_v0.9.24`, the selected joint bounded
policy, and the internal `clinical_headline` scorer.

| Model | dev140 F1 | test60 F1 | Evidence state |
| --- | ---: | ---: | --- |
| GPT-4.1-mini | 0.8202 | 0.7572 | Committed run and aggregate holdout summary |
| GPT-5.6 Luna | 0.8832 | 0.7950 | Committed run and aggregate holdout summary |
| GPT-5.6 Sol | 0.8920 | 0.8047 | Committed run and aggregate holdout summary |
| DeepSeek V4 Flash, thinking enabled | 0.8767 | 0.7881 | Committed run and aggregate holdout summary |
| Qwen 3.6:35B | 0.8571 | 0.7872 | Retained dev run and aggregate holdout summary |
| Gemma 4 26B | 0.8016 | 0.7169 | Retained dev run and aggregate holdout summary |

Exact evidence is `1.0` after assembly for every model. These are development
results, not the published ExECT benchmark or clinical validation. The
[per-model reports](docs/experiments/exectv2/reliability/) own family-level
scores, attribution, and operational detail.

All six `test60` conditions cover the 59 loadable letters. The four hosted
conditions completed with no call or blocking parse failure. The sanitized
local summaries record zero call failures; Qwen has zero and Gemma six
aggregate parse/schema failures. These are locked internal-scorer results, not
the published benchmark. See the
[hosted protocol](docs/experiments/exectv2/reliability/exectv2_hosted_test60_protocol_2026-07-15.md).

### Gan fixed-prompt comparisons

The matched v0.7 `test450` panel uses one call per note, prompt
`gan2026_hybrid_structured_events_v0.7`, `hybrid_full_stack` repair, and the Gan
Purist and Pragmatic scorers.

| Model | Purist | Pragmatic | Evidence state |
| --- | ---: | ---: | --- |
| GPT-4.1-mini | 353/450 | 371/450 | Committed aggregate summary |
| GPT-5.6 Luna | 352/450 | 365/450 | Committed aggregate summary |
| GPT-5.6 Sol | 358/450 | 376/450 | Committed aggregate summary |
| DeepSeek V4 Flash, thinking enabled | 342/450 | 362/450 | Committed aggregate summary |
| Qwen 3.6:35B | 367/450 | 380/450 | Retained aggregate summary |
| Gemma 4 26B | 343/450 | 367/450 | Retained aggregate summary |

The local summaries record 0 final call/parse/schema/label failures after
deterministic repair and exact evidence for 363/450 Qwen and 437/450 Gemma
rows. The complete panel is aggregate-only evidence on a previously used
holdout, not a pristine one-shot or model-neutral capability ranking.

Under the separate v0.5 protocol, GPT-4.1-mini completed at 361/450 Purist and
379/450 Pragmatic, Luna at 362/450 and 375/450, and Sol at 373/450 and
384/450. DeepSeek has 350 unique rows and remains unscored until all 450 raw
outputs are complete and replayed through today's schema repair. The
[amended hosted protocol](docs/experiments/gan2026/gan2026_matched_v05_test450_protocol_2026-07-16.md)
and [local/replay protocol](docs/experiments/gan2026/gan2026_matched_v05_local_test450_and_qwen_val750_protocol_2026-07-18.md)
own the active runs.

A no-call replay ran all 450 saved GPT-4.1-mini, Luna, and Sol raw outputs
through today's shared schema repair and the unchanged downstream stack. It
changed zero final labels and produced zero Purist or Pragmatic transitions in
all three conditions. The scores therefore remain 361, 362, and 373 Purist.
The [aggregate replay artifact](experiments/gan2026_matched_v05_current_schema_replay_20260718.json)
records source and replay fingerprints.

### Reliability and cross-task comparison

The [six-model comparison report](docs/research/six_model_comparison_report_2026-07-18.md)
synthesizes the fixed panels without pooling their task-specific scores. Sol
leads ExECT test60, Qwen leads Gan test450, and the cross-task model-rank
Spearman correlation is `0.20`.

The [ExECT SF over-inference result](docs/experiments/exectv2/reliability/exectv2_six_model_sf_overinference_2026-07-18.md)
compares the model-structured state set with the final projected/suppressed
state set on all 840 model-letter `dev140` pairs. Final state-profile F1
improves for every model. Across the six panels the fixed deterministic stage
produces 54 wrong-to-correct and one correct-to-wrong transition, with exact
final evidence throughout. These pooled transition counts are descriptive
because each model uses the same 140 letters.

The predeclared primary unknown-only denominator is `0`. The 41 empty-gold
letters remain diagnostic because ExECT annotation omission cannot be treated
as proof that a model prediction is false. Gan-to-ExECT over-reading transfer
therefore remains unsupported and is not measurable from the current gold.

The [shared reliability scorecard](docs/research/shared_reliability_scorecard_2026-07-18.md)
maps all 16 task-by-criterion cells to retained evidence or an explicit gap.
The companion
[ExECT semantic-support protocol](docs/experiments/exectv2/reliability/exectv2_semantic_support_review_substrate_protocol_2026-07-18.md)
selects 48 evidence-valid dev140 findings across six models and four families.
All review fields remain unset; this is a prepared substrate, not semantic-
support evidence or independent clinical validation. No model call or locked
row inspection was used.

## Verification state

Repository-wide checks passed on the shared-framework tree before the current
v0.5 run-control and replay additions:

- **Verified:** all 1,305 pytest tests pass under the repository `.venv`.
- **Verified:** repository-wide Ruff passes.
- **Verified:** mypy passes across 294 source files.
- **Verified:** both deterministic builders reproduce their selected outputs,
  the retained-evidence manifest validates, and all six no-call reference cells
  replay their expected scores.
- **Verified:** the IEEE PDF builds in two passes as a four-page letter-size
  paper. Every rendered page was inspected; no clipping, unreadable table,
  undefined reference, overfull box, or LaTeX warning remains.

For the current additions, the focused replay and v0.5 runner tests pass and
Ruff passes on the new replay files. Repository-wide pytest, Ruff, and mypy
have not yet been rerun, so the earlier broad verification does not cover these
working-tree changes.

This verifies the current implementation, retained hashes, common-panel
invariants, source synchronization, reference replays, and paper render. It is
not independent clinical validation or a new clean-checkout reproduction.

## In progress

- DeepSeek V4 Flash is completing its remaining 100 v0.5 test450 calls on the
  hosted route. Its final 450 raw outputs will be replayed through today's
  shared schema repair before any score is reported.
- The local queue runs Qwen v0.5 test450, Gemma v0.5 test450, then Qwen v0.5
  validation750. Each test condition requires a five-row validation pilot and
  remains aggregate-only.
- The earlier Qwen v0.7 validation750 process was cancelled at 367 rows on the
  user's instruction. Its partial artifact is retained only as an operational
  record and must not be resumed into the v0.5 condition.

## Next

1. Predeclare and run the Gan winning `llm_with_rules` configuration on the
   full permitted `validation750` split for all six fixed models. Retain the
   row-level structured output, deterministic repair trace, evidence, and
   scores needed to make every model inspectable in the Example Explorer.
2. Predeclare and run a matched Gan `llm_only` configuration on the same
   `validation750` rows for all six fixed models. Freeze the model-only
   prediction boundary before execution, retain row-level artifacts, and make
   the six conditions comparable with the winning mode and deterministic-only
   control in the Example Explorer.
3. Complete DeepSeek, Qwen, and Gemma v0.5 test450 aggregates and replay all
   hosted raw outputs through the current schema repair.
4. Complete Qwen v0.5 validation750, then use the matched development outputs
   for the predeclared hard-slice and synthetic mechanism study.
5. Complete independent review of the frozen semantic-support substrate before
   strengthening any faithfulness or clinical-validity claim.

## Blocked or unvalidated

- Independent clinical review remains required before any clinical-validity
  claim. Internal annotation review is not that validation.
- Exact evidence is measured, but semantic support remains unmeasured. The
  48-item ExECT substrate is unreviewed and cannot clear that dependency.
- The selected ExECT joint policy retains three known deterministic
  regressions. The one-call Diagnosis decision also accepts a measured dev140
  quality loss from 0.8727 to 0.8542 Diagnosis F1 versus the two-call ablation.

## Data and claim boundaries

- **Gan `test450`:** locked and aggregate-only. A prior documentation command
  exposed part of a row table; no row was used for tuning. Do not perform
  failure analysis or prompt, repair, or scorer changes from test rows.
  The v0.5 extension and current-schema replays inspect only aggregate counts;
  sealed row details remain unreported and cannot drive tuning.
- **ExECT `dev140`:** development review is permitted.
- **ExECT `test60`:** locked and aggregate-only. During sanitization, embedded
  row details were visible to the agent but were not shown to the user,
  analyzed, or used to change a prompt, policy, scorer, implementation, or
  conclusion. The Qwen and Gemma retained summaries contain only run metadata
  and aggregate scores and counts. Sealed row artifacts remain in ignored local
  storage for provenance and must not be inspected or shared.
- **Scores:** Gan reports Purist and Pragmatic label accuracy. ExECT's
  `clinical_headline` is an internal de-duplicated clinical-fact score, not the
  published benchmark.
- **ExECT SF reliability replay:** row-level `dev140` analysis only; no test60
  row was accessed. The unknown-only denominator is empty, so empty-gold rows
  remain diagnostic and no factuality-prevalence or cross-task-transfer claim
  is active.

## Canonical owners

- Exact retained files, hashes, and replay requirements:
  [retained evidence index](docs/experiments/retained_evidence_manifest.md)
- Permitted paper wording: [paper claim status](docs/canon/10_paper_provenance.md)
- Decisions and run protocols: [documentation navigation](docs/NAVIGATION.md)
- Cross-task six-model synthesis:
  [comparison report](docs/research/six_model_comparison_report_2026-07-18.md)
- Active Gan v0.5 extension and schema replay:
  [protocol](docs/experiments/gan2026/gan2026_matched_v05_local_test450_and_qwen_val750_protocol_2026-07-18.md)
  and [aggregate replay](experiments/gan2026_matched_v05_current_schema_replay_20260718.json)
- Shared eight-criterion synthesis:
  [reliability scorecard](docs/research/shared_reliability_scorecard_2026-07-18.md)
- Detailed work order: [active roadmap](docs/plans/ACTIVE_ROADMAP.md)

Use *implemented*, *verified*, *validated*, and *promoted* precisely.
