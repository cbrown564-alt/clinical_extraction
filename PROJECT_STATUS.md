# Project status

Last updated: 2026-07-31 after finalizing Gan LLM-with-rules ruleset docs

## Current outcome

The fixed one-call ExECTv2 comparison is implemented for all six selected
models on `dev140` and has aggregate-only `test60` results for the same six
models. The retained aggregate panel records all six test60 conditions with
equal canonical status; sealed row artifacts remain ignored and uninspectable.

Gan has complete selected six-model v0.5 `dev750` and aggregate-only `test450`
panels. The development panel contains 4,500 unique row traces with the frozen
prompt, repair policy, scorers, and split. Its companion attribution artifact
retains the raw model boundary, deterministic transitions, selected-evidence
grades, rules-control regressions, first-failure owner, and clinical
subproblem for every model-row pair. Retained Gan filenames and
machine-readable split fields use the legacy identifier `validation750` for
`dev750`.

These panels are retained paper evidence with aggregate-only test limits.
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

The earlier complete six-model Gan `dev750` panel uses prompt v0.7 for
`llm_with_rules`. It is retained only as a historical prompt-interaction and
component diagnostic. Its scores and matched method transitions must not
supply a primary ranking, paper result, reliability cell, or development-to-
test comparison.

The post-panel no-call replay is complete from retained development traces.
Across 9,000 model-condition rows it recovers 11 schema-valid
`llm_with_rules` records and changes zero existing selected answers. The
component audit retains matched rescues, regressions, exact-evidence status,
rules-control regressions, score layers, clinical subproblems, and first-
failure ownership. Because the deterministic rules control remains stronger on
many rows, this is a bounded development answer rather than method promotion.

The Qwen-versus-Sol follow-up audit is also complete on saved `dev750` outputs.
It shows that the reported +102 versus +65 method difference is not a
same-raw-output rule ablation because the methods use different prompts and
prediction structures. Within the event-ledger method, fixed processing has a
larger scorer-defined net effect for Sol (+387) than Qwen (+336). Eight unique
raw-correct-to-final-wrong rows expose deterministic over-rules; one additional
Qwen transition is only scorer-correct because an unsupported vague label maps
to the unknown sentinel. This is development mechanism evidence, not proof for
or against policy-level validation overfitting.

The simplified first-round ExECT semantic-support rubric and adjudication rule
are now frozen. A local review workspace serves the real 48-item `dev140`
sample with the selected conclusion, exact evidence, highlighted full-letter
context, one required clinical-support judgment (`supported`, `unsupported`,
or `unclear`), optional notes, reviewer-specific blinded queues, revision
history, and JSON export. The workflow is implemented and browser-verified;
prior trial decisions were cleared before this protocol revision, so no
clinical review decision has been collected or validated by this work.

## Fresh evidence

### ExECTv2 fixed one-call comparison

All six `dev140` runs use the decision-0040 model-led family boundary,
decision-0041 single-call architecture, prompt
`exectv2_hybrid_key_family_event_ledger_v0.9.24`, the selected joint bounded
policy, and the internal `clinical_headline` scorer.

| Model | dev140 F1 | test60 F1 | Evidence state |
| --- | ---: | ---: | --- |
| GPT-4.1-mini | 0.8202 | 0.7572 | Committed run and aggregate test summary |
| GPT-5.6 Luna | 0.8832 | 0.7950 | Committed run and aggregate test summary |
| GPT-5.6 Sol | 0.8920 | 0.8047 | Committed run and aggregate test summary |
| DeepSeek V4 Flash | 0.8767 | 0.7881 | Committed run and aggregate test summary |
| Qwen 3.6:35B | 0.8571 | 0.7872 | Retained dev run and aggregate test summary |
| Gemma 4 26B | 0.8016 | 0.7169 | Retained dev run and aggregate test summary |

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

### Gan selected v0.5 comparison

All six v0.5 conditions use one structured-event call per note, the Gan Purist
and Pragmatic scorers, and prompt `gan2026_hybrid_structured_events_v0.5`.

**Final LLM-with-rules ruleset (2026-07-31):** working-tree `hybrid_full_stack`
including projection/anti-regression, dated-count, competing-rate floors, and
narrow cross-model guards (singleton-cluster unknown; YTD-gated typical rate;
current-month seizure-free diary override). Further rule tuning for this
comparison is closed unless a new predeclared study reopens it. Owners:
[six-model comparison](docs/research/six_model_comparison_report_2026-07-18.md),
[dated-count / guards](docs/research/gan2026_luna_dated_count_competing_rate_report_2026-07-31.md),
[final-ruleset replay](experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json).

Frozen July matched-panel artifacts remain the historical row-trace record
under the prior repair. Current LLM-with-rules scores are no-call replays of
the same saved raw outputs through the final ruleset.

#### Final ruleset no-call replay

| Model | `dev750` Purist | `dev750` Pragmatic | `test450` Purist | `test450` Pragmatic |
| --- | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 677/750 | 695/750 | 369/450 | 386/450 |
| GPT-5.6 Luna | 660/750 | 687/750 | 364/450 | 378/450 |
| GPT-5.6 Sol | 660/750 | 685/750 | 381/450 | 392/450 |
| DeepSeek V4 Flash | 627/750 | 653/750 | 348/450 | 370/450 |
| Qwen 3.6:35B | 657/750 | 676/750 | 360/450 | 380/450 |
| Gemma 4 26B | 647/750 | 681/750 | 356/450 | 375/450 |

#### Frozen matched panel (historical; prior repair)

| Model | Purist | Pragmatic | Exact evidence |
| --- | ---: | ---: | ---: |
| GPT-4.1-mini | 361/450 | 379/450 | 419/450 |
| GPT-5.6 Luna | 362/450 | 375/450 | 444/450 |
| GPT-5.6 Sol | 373/450 | 384/450 | 450/450 |
| DeepSeek V4 Flash | 344/450 | 366/450 | 433/450 |
| Qwen 3.6:35B | 362/450 | 384/450 | 347/450 |
| Gemma 4 26B | 355/450 | 374/450 | 436/450 |

The [hosted protocol](docs/experiments/gan2026/gan2026_matched_v05_test450_protocol_2026-07-16.md),
[local/replay protocol](docs/experiments/gan2026/gan2026_matched_v05_local_test450_and_qwen_val750_protocol_2026-07-18.md),
and [aggregate artifact](experiments/gan2026_matched_v05_test450_aggregate_20260716.json)
own the frozen test450 panel.

The matched v0.5 six-model `dev750` panel artifacts are complete under
[the development protocol](docs/experiments/gan2026/gan2026_matched_v05_dev750_protocol_2026-07-27.md).

| Model | Frozen Purist | Frozen Pragmatic | Exact evidence | Raw to final W→C / C→W |
| --- | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 668/750 | 686/750 | 692/750 | 314 / 5 |
| GPT-5.6 Luna | 646/750 | 671/750 | 744/750 | 240 / 5 |
| GPT-5.6 Sol | 656/750 | 678/750 | 749/750 | 317 / 6 |
| DeepSeek V4 Flash | 619/750 | 641/750 | 728/750 | 174 / 4 |
| Qwen 3.6:35B | 660/750 | 680/750 | 567/750 | 339 / 4 |
| Gemma 4 26B | 643/750 | 676/750 | 734/750 | 223 / 5 |

Across all 4,500 frozen-panel rows, fixed processing produces 1,607
wrong-to-correct and 29 correct-to-wrong raw-boundary transitions. It also
regresses 514 rows that the independent rules comparator gets correct. Exact
selected evidence is present on 4,214 rows and grounded selected evidence on
4,328. This supports a bounded development comparison and component audit, not
method promotion or a model-neutral ranking. The
[panel report](docs/experiments/gan2026/gan2026_matched_v05_dev750_panel_2026-07-27.md)
and [row attribution](experiments/gan2026_matched_v05_dev750_attribution_20260727.json)
own the frozen detailed evidence.

The historical v0.7 [Qwen-versus-Sol row audit](docs/experiments/gan2026/gan2026_qwen_sol_rule_benefit_audit_2026-07-20.md)
and its [machine artifact](experiments/gan2026_qwen_sol_rule_benefit_audit_20260720.json)
cover all 249 rows where either model is Purist-wrong in either scored method.
They retain both raw prediction boundaries, both final outputs, rule events,
selected evidence, and a comment for every row. Qwen's larger between-method
gain is concentrated in cluster/diary and seizure-free cases, while the true
same-event-ledger raw-to-final net gain is larger for Sol.

The historical v0.7 [architecture-interaction report](docs/research/gan2026_qwen_sol_architecture_interaction_report_2026-07-27.md)
and [750-row machine audit](experiments/gan2026_qwen_sol_architecture_interaction_20260727.json)
show that fixed processing does not preferentially rescue Qwen: the same saved
event-ledger output has net raw-to-final gains of +336 for Qwen and +387 for
Sol. Qwen's final 667-versus-655 lead is the balance of 44 Qwen-only-correct
and 32 Sol-only-correct rows. All 44 Sol failures in the Qwen-only-correct set
are first owned by LLM clinical selection. Qwen's 32 unique losses contain 18
LLM-selection, 10 evidence-selection, three format/schema, and one
deterministic-semantic first failures. This is a model-by-method development
interaction, not evidence that the deterministic stack is fitted to Qwen or
to local or smaller models. These results are quarantined from primary claims.

The historical v0.7 [exact-evidence and repair report](docs/research/gan2026_dev750_exact_evidence_and_repair_report_2026-07-27.md)
and [4,500-row machine audit](experiments/gan2026_dev750_exact_evidence_and_repair_20260727.json)
derive the metrics from code and every retained `llm_with_rules` development
row. Exact selected evidence is a case-sensitive contiguous source substring.
Qwen has 582/750 exact and 672/750 grounded-after-neutral-repair selections;
87 of the non-exact rows are verified bounded-ellipsis citations. Among all
168 non-exact Qwen selections, 148 retain at least one exactly cited selected
event and 139 retain exact evidence for every selected event. Fixed code
changes the Purist category on 92/168. A reported repair-note count is the
number of rows with at least one `final_label_repaired:` event, not the number
of errors or repair events; on dev750 Sol has 597 such rows and 710 events,
while Qwen has 537 rows and 621 events. These are diagnostic v0.7 development
measurements, not primary v0.5 evidence.

A no-call replay ran all 450 saved GPT-4.1-mini, Luna, and Sol raw outputs
through today's shared schema repair and the unchanged downstream stack. It
changed zero final labels and produced zero Purist or Pragmatic transitions in
all three conditions. The scores therefore remain 361, 362, and 373 Purist.
The [aggregate replay artifact](experiments/gan2026_matched_v05_current_schema_replay_20260718.json)
records source and replay fingerprints.

### Reliability and cross-task comparison

The [six-model comparison report](docs/research/six_model_comparison_report_2026-07-18.md)
synthesizes the fixed panels without pooling their task-specific scores and
records the finalized Gan LLM-with-rules ruleset (2026-07-31). Sol leads ExECT
test60 and both the frozen Gan v0.5 test450 panel and the final-ruleset
test450 no-call replay (all six models). The cross-task model-rank Spearman
correlation on the frozen panels is `0.61`.

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
All substrate review fields remain unset. The three semantic-support values,
optional-note policy, two-reviewer blinding, and third-reviewer adjudication
rule are frozen in the protocol. The local `/clinical-review` workspace now
combines separate Correctness review and Semantic support task tabs in the same
evidence-review structure while keeping their decisions separate. This is
still not semantic-support evidence or independent clinical validation. No
model call or locked row inspection was used.

The supervisor source handoff is implemented in the working tree. It exposes
readable Python source for the selected Gan v0.5 current-frequency and one-call
ExECT four-family workflows, a direct OpenAI-compatible endpoint client, strict
input validation, concise and trace outputs, partial success, synced recovery,
resume identity checks, privacy-safe errors, synthetic examples, and an
explicit hashed source manifest. The transfer archive contains no required
`.pyz`, benchmark-result files, private configuration, or research reports.
Focused and clean-extraction checks pass. Exact supervisor endpoint and
unaided-usability checks have not occurred; this is not clinical validation.
The [handoff plan](docs/plans/supervisor_local_extraction_handoff_plan.md) owns
the detailed evidence and remaining acceptance checks.

## Verification state

Current working-tree backend verification is green for tracked project files:

- **Verified on 2026-07-28 after CI repair:** all 1,397 pytest tests pass with a
  fresh workspace-local base temp directory. Repository-wide Ruff passes after
  excluding ignored workspace-local `.tmp` test fixtures, and mypy passes
  across 335 source files. Pytest reports one cache-write warning because the
  sandbox cannot write `.pytest_cache`; no test is skipped or failed.
- **Verified for the handoff:** 26 focused source API, input/privacy, endpoint
  request, format-retry, recovery, five-fixture parity, archive, manifest, and
  clean-command tests pass under the repository `.venv`. The builder also runs
  the shipped tests from a clean extracted archive. Manifest and archive
  integrity checks now ignore runtime bytecode caches, which the builder
  already excludes from shipped output.
- **Verified for the Gan v0.5 dev750 panel:** all six conditions pass strict
  750-row identity checks; the 4,500-row panel and attribution artifacts
  reproduce with `finalize --check`; five focused panel tests and scoped Ruff
  pass.
- **Verified:** the retained-evidence manifest validates. Its dependency
  fingerprint matches the current `pyproject.toml`, and the frozen Gan v0.7
  prompt now has its own versioned snapshot rather than sharing the mutable
  default-prompt snapshot. Both deterministic builders reproduce their
  selected outputs and all six no-call reference cells replay their expected
  scores.
- **Verified:** the semantic-review API suite passes (`11` tests), the frontend
  Jest suite passes (`51` tests), frontend lint passes, and the Next.js
  production build completes with the new route. The entry, evidence, decision,
  exception-note, and responsive flows were inspected in the browser.
- **Previously verified:** the IEEE PDF builds in two passes as a four-page
  letter-size paper with no clipping, unreadable table, undefined reference,
  overfull box, or LaTeX warning. The paper was not rebuilt for these
  implementation and documentation changes.

The fresh handoff checks verify its implementation, source manifest, synthetic
stage parity, recovery behavior, and clean extracted execution. They do not
verify the supervisor endpoint, host setup, private-data performance, clinical
correctness, retained research hashes, or a new clean-checkout reproduction.

## In progress

- Independent review of the 48-item ExECT semantic-support substrate remains
  the next evidence dependency. The rubric, reviewer separation, and
  adjudication rule are frozen; the review interface is ready.
- Supervisor endpoint and unaided README verification remain the next handoff
  dependency; no private data is needed to perform them.
- Gan LLM-with-rules ruleset is finalized (2026-07-31). Luna prompt-variant
  residual work that produced the floors/guards is complete; further rule
  tuning for this comparison is closed unless a new predeclared study
  reopens it. See
  [six-model comparison](docs/research/six_model_comparison_report_2026-07-18.md)
  and [dated-count / guards](docs/research/gan2026_luna_dated_count_competing_rate_report_2026-07-31.md).

## Next

1. On the supervisor's intended Python 3.11 host, run handoff setup, `check`,
   and both bundled synthetic examples against the approved model route; record
   JSON/thinking/retry behavior and unaided README corrections in the handoff
   plan.
2. Assign two independent clinical reviewer IDs and have each reviewer complete
   all 48 items without sharing IDs or reviewing the other's export.
3. Send every field-level disagreement to a third named clinical adjudicator;
   retain both original decisions and every revision.
4. Export the completed reviewer and adjudication artifacts, validate their
   completeness, then update the reliability scorecard and paper claim owner
   within the protocol's development-only limits.
5. Treat Gan LLM-with-rules as finalized; do not reopen rule tuning without a
   new predeclared study. Keep sealed `test450` unused for tuning. Any later
   residual work must separate prompt/selection candidates from the closed
   ruleset.
6. If Gan rule revision resumes, predeclare narrow challenge fixtures for the
   eight audited deterministic regression rows and matched non-regression
   controls; do not tune the frozen six-model panel in place.

## Blocked or unvalidated

- Independent clinical review remains required before any clinical-validity
  claim. Internal annotation review is not that validation.
- Exact evidence is measured, but semantic support remains unmeasured. The
  48-item ExECT substrate is unreviewed and cannot clear that dependency.
- The selected ExECT joint policy retains three known deterministic
  regressions. The one-call Diagnosis decision also accepts a measured dev140
  quality loss from 0.8727 to 0.8542 Diagnosis F1 versus the two-call ablation.
- The handoff is implemented and locally checked but not yet verified against
  the supervisor's exact endpoint or validated for unaided use. Those checks,
  not private-note testing, clear the operational dependency.

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
- Quarantined Gan v0.7 Qwen-versus-Sol rule-benefit mechanism audit:
  [row report](docs/experiments/gan2026/gan2026_qwen_sol_rule_benefit_audit_2026-07-20.md)
  and [machine artifact](experiments/gan2026_qwen_sol_rule_benefit_audit_20260720.json)
- Quarantined Gan v0.7 Qwen-versus-Sol architecture interaction:
  [standalone report](docs/research/gan2026_qwen_sol_architecture_interaction_report_2026-07-27.md)
  and [750-row machine audit](experiments/gan2026_qwen_sol_architecture_interaction_20260727.json)
- Quarantined Gan v0.7 exact-evidence and repair provenance:
  [standalone report](docs/research/gan2026_dev750_exact_evidence_and_repair_report_2026-07-27.md)
  and [4,500-row machine audit](experiments/gan2026_dev750_exact_evidence_and_repair_20260727.json)
- Active Gan v0.5 extension and schema replay:
  [protocol](docs/experiments/gan2026/gan2026_matched_v05_local_test450_and_qwen_val750_protocol_2026-07-18.md)
  and [aggregate replay](experiments/gan2026_matched_v05_current_schema_replay_20260718.json)
- Selected Gan v0.5 development coverage:
  [protocol](docs/experiments/gan2026/gan2026_matched_v05_dev750_protocol_2026-07-27.md)
  [configuration](configs/gan2026/six_model_v05_dev750_20260727.json),
  [panel report](docs/experiments/gan2026/gan2026_matched_v05_dev750_panel_2026-07-27.md),
  [machine panel](experiments/gan2026_matched_v05_dev750_panel_20260727.json),
  and [row attribution](experiments/gan2026_matched_v05_dev750_attribution_20260727.json)
- Gan final LLM-with-rules ruleset (2026-07-31):
  [six-model comparison](docs/research/six_model_comparison_report_2026-07-18.md),
  [dated-count / guards](docs/research/gan2026_luna_dated_count_competing_rate_report_2026-07-31.md),
  [final-ruleset replay](experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json),
  [projection floor](docs/research/gan2026_luna_projection_antiregression_floor_report_2026-07-31.md),
  and Luna thread owners under
  [prompt variants](docs/research/gan2026_luna_prompt_variants_report_2026-07-30.md)
- Shared eight-criterion synthesis:
  [reliability scorecard](docs/research/shared_reliability_scorecard_2026-07-18.md)
- Independent semantic-support review:
  [protocol](docs/experiments/exectv2/reliability/exectv2_semantic_support_review_substrate_protocol_2026-07-18.md)
  and local route `http://127.0.0.1:3000/clinical-review`
- Detailed work order: [active roadmap](docs/plans/ACTIVE_ROADMAP.md)

Use *implemented*, *verified*, *validated*, and *promoted* precisely.
