# Project status

Last updated: 2026-08-02 after Decision 0049 Waves 3–4 pytest scoreboard

## Current handoff objective

[Decision 0048](docs/decisions/0048-comprehension-and-handoff-refactor.md)
sets the active priority: turn the verified research system into a clean,
immediately useful handoff package without removing the live-run capability
needed for new experiments and external validation.

[Decision 0049](docs/decisions/0049-pytest-research-validity-firewall.md)
is complete through Wave 4: plain `pytest` is the always-on research-validity
firewall and collects **243** tests (**verified 2026-08-02**, all passed,
~40s). Architecture manifests name short governing owners; the deep allowlist
is empty. Supervisor handoff still traces
`tests/test_clinical_extraction_local_parity.py`.

The retained operational boundary is the selected six-model × three-method ×
two-task system, its frontend development workflows, saved/fixture and live
demonstrations, exact no-call replay, essential decision evidence, and a
restricted research-validation workflow. Historical and supporting material is
being triaged for value and regeneration status. This cleanup is behavior-
preserving by default; any clinical, scoring, split, prompt, routing, or
evidence-policy change requires a separate predeclared study.

Completion requires a supervisor to navigate from the README to the frontend,
the six-path teaching case, the canonical results report, evidence and limits,
and reproduction commands without agent assistance. Engineering verification,
research evidence, independent clinical review, and clinical validation remain
separate claims.

The bounded README-led supervisor milestone is implemented on `main`. It
changes the README, navigation, generated walkthrough,
roadmap, and focused documentation tests; it does not change clinical behavior.
Focused architecture, link, and no-call checks pass. The standalone handoff
tree and ZIP are rebuilt from active source and pass source-to-shipped
closure. Decision 0048 remains open for supervisor-host verification and
unaided README review. The [handoff plan](docs/plans/supervisor_local_extraction_handoff_plan.md)
owns those checks.

## Decision 0048 current point

The regeneration/LFS ledger and restricted external-validation readiness
template are complete. The active Gan method names are now `rules`, `llm`, and
`llm_with_rules` across the runtime, compatibility boundary, API/frontend
surfaces, teaching material, and generated architecture. Historical filenames,
run IDs, prompt versions, manifests, replay metadata, and explicit inbound
aliases remain unchanged.

Label-leftover blockers from the 2026-08-02 grill are implemented in the
working tree (not yet committed): `comparison_mode` removed in favor of active
method grouping; architecture stage IDs renamed to `*.llm_with_rules.*`; ExECT
component-ablation removed from the supervisor path; Gan ablation three-way
columns retagged as selected active methods. Focused architecture, trace-
explorer, and frontend checks pass.

Broader corpus retention triage is advanced in the same working tree: unserved
ExECT mocks deleted; five orphan docs removed (rejected-policy protocols kept
for negative replay); seven tier-1 experiment orphans removed; ~99 MB
scoring-lane/two-call orphans removed; five stale mock-registry paths
retargeted to served artifacts. Retained-evidence manifest still valid.
Supervisor-host and unaided README review remain open before the Decision 0048
status flip.

The ExECT `rules`, `llm`, and `llm_with_rules` vertical slices are implemented and verified
through runtime, split/CLI, API, registry, trace/frontend, teaching material,
generated architecture, and exact permitted-development parity. Active, saved
frontend, retained-evidence, and historical manifest identities remain
separate. Sol's final `llm` review found no actionable finding at `c93c80b4`,
and the slice is merged into `main` at `e177482d`. The hybrid implementation
and fail-closed repair are `31103533` and `76d0dbcd`; `6fd70834` closes the
remaining replay-content, deep-immutability, and full-parity review gates.
The selected hybrid keeps one structured producer, `default/default` assembly,
Sol-only active identity, exact checkpoint provenance, and historical replay
identities without model calls or locked-row inspection during migration.

Sol's strict review found two compatibility-helper defects; `7d9c4000` fixes
both. Gan parity now permits only the explicit absence-to-`llm_with_rules`
identity transition, and ExECT alias resolution accepts only real string IDs.

`main` now contains the Gan and ExECT three-method migrations, canonical parity
repairs, the first safe retention deletion, the bounded README-led milestone,
a non-mutating source-to-shipped closure checker, and a rebuilt standalone
handoff package whose source-to-shipped closure is current. Supervisor-host
and unaided README checks remain open.

## Current outcome

Decision 0046 locks the paper's primary ExECT three-method comparison on
Sol-matched four-family `clinical_headline`, demoting `v08` and GEPA from the
primary method rows. The A→B→C evidence protocol is complete. Primary fills:
rules-only four-family `0.8160` (`dev140`) / `0.7154` (`test60`); Sol LLM-only
`0.8097` / `0.7771`; Sol hybrid `0.8920` / `0.8047`. Canon and manuscript
method rows still need updating to match. Phase 5 / finding 1 remains open.
Owners: [decision 0046](docs/decisions/0046-exect-primary-method-comparison-boundary.md),
[protocol](docs/experiments/exectv2/reliability/exectv2_primary_method_comparison_surface_protocol_2026-08-01.md),
[stage panel](experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json),
[rules-only dev140](experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json),
[rules-only test60](experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json).

Decision 0047 is implemented and verified. All six selected methods now use
task-local typed canonical entry points, and active research, replay, and
operational wrappers delegate to them. The permitted-development replay passes
for all six task-method pairs; all six retained historical reference cells
reproduce; four public locked-split aggregate artifacts pass the no-row-content
safety check; and all 15 generated architecture documents match current code.
A fresh checkout of commit `46fec88a` passes 1,488 tests, Ruff, and mypy over
350 source files. This verifies implementation parity and reproducibility; it
does not add clinical validation or authorize model calls or locked-row
inspection. Owner:
[decision 0047 parity](docs/experiments/canonical_orchestrator_parity_0047.md),
[machine artifact](experiments/canonical_orchestrator_parity_0047.json).

The fixed one-call ExECTv2 comparison is implemented for all six selected
models on `dev140` and has aggregate-only `test60` results for the same six
models. The retained aggregate panel records all six test60 conditions with
equal canonical status; sealed row artifacts remain ignored and uninspectable.

A plain-English residual-floor synthesis now joins the retained Gan and ExECT
mechanism evidence. It concludes that the remaining ~10–20% gap is mostly
forced clinical selection under annotation conventions (competing rates,
uncertainty vs coded rates, multi-state profiles, diagnosis inventory), not
missing quotes or forgotten instructions; scoring/dialect and rule
over/under-correction are a meaningful minority; further prompt or rule
tuning is a marginal lever. Owner:
[why the error floor persists](docs/research/why_the_error_floor_persists_2026-07-31.md).

A companion policy catalog names the active selection, repair, assembly, and
scoring conventions with implications, a help case, a hurt case, and where
each lives (gold, prompt, fixed code, scorer, or architecture). Owner:
[clinical selection policy catalog](docs/research/clinical_selection_policy_catalog_2026-07-31.md).

An explanatory architecture layer states, for each of the six selected
task-method pairs, how a record moves through it and who owns each change.
Six machine-readable stage manifests drive generated method cards, diagrams,
two executable teaching cases, and the generated six-path walkthrough; a CI
drift gate fails if the published explanation stops matching the code. The
teaching cases use real implementation for prediction-bearing stages and
post-model gates, while the ExECT score entry is an explicitly unscored
scorer-boundary illustration. The 0047 refactor keeps
prediction outputs and scores unchanged in the no-call characterization. Owner:
[architecture layer](docs/architecture/README.md).

A bounded Gan **DeepSeek unknown-competence** thread is open for author
collaboration (local DeepSeek; LLM-only and LLM-with-rules only). Phase 0
hosted V4 Flash `dev750` unknown-slice baselines fail the predeclared
collaboration gates. Real(300) and sealed `test450` remain off-limits for
tuning.

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

The requested six-model comparison report is complete. It now also includes
external Artificial Analysis Intelligence and Healthcare & Medical Index
context for all six roster models, clearly labelled list-price / AA latency
illustrations (not matched run telemetry), and a development error-pattern
synthesis from Gan `dev750` attribution plus ExECT family/SF tables. Machine
owner:
[external capability/cost snapshot](experiments/six_model_external_capability_cost_snapshot_20260731.json).

A predeclared no-call ExECT Seizure Frequency reliability replay also covers
all six models on `dev140`. Its intended unknown-only denominator is empty, so
it closes that cross-task question as unmeasurable from current ExECT gold
rather than substituting empty-gold rows.

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
`exectv2_hybrid_key_family_event_ledger_v0.9.24`, Diagnosis/Prescription
**`default`/`default`** ([decision 0045](docs/decisions/0045-exect-default-policy-not-joint-combined.md)),
and the internal `clinical_headline` scorer. Joint (`combined`/`combined`) is
archived development evidence only.

| Model | dev140 F1 | test60 F1 | Evidence state |
| --- | ---: | ---: | --- |
| GPT-4.1-mini | 0.8202 | 0.7572 | Committed run and aggregate test summary |
| GPT-5.6 Luna | 0.8832 | 0.7950 | Committed run and aggregate test summary |
| GPT-5.6 Sol | 0.8920 | 0.8047 | Committed run and aggregate test summary |
| DeepSeek V4 Flash | 0.8767 | 0.7881 | Committed run and aggregate test summary |
| Qwen 3.6:35B | 0.8571 | 0.7872 | Retained dev run and aggregate test summary |
| Gemma 4 26B | 0.8016 | 0.7169 | Retained dev run and aggregate test summary |

A same-stack no-cache DeepSeek `deepseek-v4-flash` re-run after the
2026-07-31 provider update (`DeepSeek-V4-Flash-0731`) scores **0.8994**
clinical_headline on `dev140`. Against a no-call **current-rules** replay of
the frozen 2026-07-15 DeepSeek structured outputs (also 0.8767; post-July-15
deterministic changes do not move that cell), the delta is **+0.0227**, with
the largest family gain in Seizure Frequency (+0.0672). Row-level: 59 changed
letters (38 rescue / 11 regression / 10 prediction-only). This is development
provider-update evidence and does **not** replace the retained six-model panel
cell or test60 figure above. Owners:
[protocol](docs/experiments/exectv2/reliability/exectv2_deepseek_v4_flash_0731_dev140_protocol_2026-07-31.md),
[report](docs/experiments/exectv2/reliability/exectv2_deepseek_v4_flash_0731_dev140_2026-07-31.md),
[ruleset-matched baseline](experiments/exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_20260731.json),
[diff](experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_vs_20260715_current_rules.json).

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

A matched six-model **LLM-only** `test450` panel
(`gan2026_llm_only_canonical_pipeline_v0.8`) is also complete as of 2026-08-01
under
[protocol](docs/experiments/gan2026/gan2026_six_model_llm_only_test450_protocol_2026-08-01.md)
and
[panel aggregate](experiments/gan2026_six_model_llm_only_test450_20260801/panel_aggregate.json).
Purist leaders: Sol 335/450, DeepSeek 332/450, mini 330/450. This does **not**
replace the frozen hybrid v0.5 LLM-with-rules panel; hosted vs local routes
remain disclosed; readout is aggregate-only.

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

The [Luna prompt A/B/C panel](docs/experiments/exectv2/reliability/exectv2_luna_prompt_variants_dev140_2026-07-31.md)
is complete on `dev140` under **default** Diagnosis/Prescription repair
(decision 0045). Both B and C improve model-owned SF letter correctness versus
A (`+2` / `+4`); B leads overall F1 (`0.8871`) and SF final letters (`+6`),
while C leads the SF hard slice (`+8` model-owned) but loses two Dx final
letters and ends at `0.8839` overall.

The [aggregate-only test60 transfer](docs/experiments/exectv2/reliability/exectv2_luna_prompt_variants_test60_2026-07-31.md)
is also complete under default repair. A matches the frozen six-model Luna cell
(`0.7950`). B and C both reach `0.8030` overall; C moves SF most (`+5` SF
letters; SF F1 `0.5693 → 0.6260`). Sealed rows were not inspected. Prior joint
(`combined`) Luna readouts are archived beside the variant artifacts as
`*_joint_archived.*`.

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

The supervisor source handoff exists in the active working tree, and the
standalone `handoff/supervisor/` tree plus ZIP were rebuilt from that source
on 2026-08-02. Source-to-shipped closure passes for the public package and
every traced internal runtime file. The package exposes readable Python source
for the selected Gan v0.5 current-frequency and one-call ExECT four-family
workflows, a direct OpenAI-compatible endpoint client, strict input
validation, concise and trace outputs, partial success, synced recovery,
resume identity checks, privacy-safe errors, synthetic examples, and an
explicit hashed source manifest. The transfer archive contains no required
`.pyz`, benchmark-result files, private configuration, or research reports.
An eager Gan `llm` package import that previously pulled
`reports/base.py` into the traced closure was removed. Exact supervisor
endpoint, host, and unaided-usability checks have not occurred; this is not
clinical validation. The
[handoff plan](docs/plans/supervisor_local_extraction_handoff_plan.md) owns
the remaining acceptance checks.

## Verification state

Current working-tree backend verification is green for tracked project files:

- **Verified on 2026-08-02 after the supervisor handoff rebuild:** source-to-
  shipped closure and the non-mutating closure checker pass. Focused handoff
  tests cover package shape, manifest hashes, traced-runtime exclusion of
  research `reports/`, and clean-copy synthetic validation. These checks
  verify engineering packaging, not supervisor-host usability or clinical
  validation.

- **Verified on 2026-08-02 after the ExECT hybrid merge gate:** `main` passes
  1,562 pytest tests. Ruff passes and mypy reports no issues across 358 source
  files. All 15 generated architecture documents match, the retained-evidence
  manifest validates, and all six selected no-call reference replays
  reproduce. The frontend passes 73 Jest tests, lint, `tsc --noEmit`, and a
  Next.js production build. Focused hybrid tests bind checkpoints to exact
  replay content, reject malformed output before deterministic assembly,
  preserve producer failure provenance, freeze nested producer values, and
  compare the permitted dev140 result against the pinned pre-migration oracle
  and governing stage manifest. These checks verify engineering and replay
  behavior, not clinical validation.

- **Verified on 2026-08-02 after the ExECT `llm` merge:** merged `main` then
  passed 1,542 pytest tests with one expected strict `xfail` for the still-
  stale standalone handoff package at that moment (cleared later the same day
  by the handoff rebuild verification above). Ruff, mypy across 358 source
  files, all 15 generated architecture checks, the retained-evidence manifest,
  all six selected no-call reference replays, locked-artifact safety, 71
  frontend Jest tests, TypeScript, focused source lint, and the Next.js
  production build passed. Sol's final synthetic split, provenance,
  alias-collision, and base-parity probes found no remaining actionable issue
  in the ExECT `llm` slice. The combined gate also caught and fixed a
  test-fixture TypeScript widening defect. These checks verify engineering and
  replay behavior, not clinical validation.

- **Verified on 2026-08-02:** at merged commit `716b6de8`, all 1,512 pytest
  tests, Ruff, mypy across 352 source files, 14 architecture-document checks,
  the retained-evidence manifest, six selected no-call reference replays, 68
  frontend Jest tests, source lint, and the Next.js production build passed.
  After the review fixes in `7d9c4000`, the 16 affected parity/frontend tests,
  focused Ruff, and Sol's independent negative-case checks passed; the full
  suite was not rerun after the final legacy-side guard was tightened. These
  checks verify engineering and replay behavior, not clinical validation.

- **Verified on 2026-07-28 after CI repair:** all 1,397 pytest tests pass with a
  fresh workspace-local base temp directory. Repository-wide Ruff passes after
  excluding ignored workspace-local `.tmp` test fixtures, and mypy passes
  across 335 source files. Pytest reports one cache-write warning because the
  sandbox cannot write `.pytest_cache`; no test is skipped or failed.
- **Historical handoff snapshot checks:** 26 focused source API,
  input/privacy, endpoint request, format-retry, recovery, five-fixture parity,
  archive, manifest, and clean-command tests passed under the repository
  `.venv`. The builder also ran the shipped tests from a clean extracted
  archive. These checks describe the historical package snapshot and do not
  certify the stale archive against the active source.
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

The historical handoff checks verify that snapshot's implementation, source
manifest, synthetic stage parity, recovery behavior, and clean extracted
execution. They do not verify the active source-to-shipped closure, supervisor
endpoint, host setup, private-data performance, clinical correctness, retained
research hashes, or a new clean-checkout reproduction.

## In progress

- **Decision 0048 has completed the Gan and ExECT method migrations and rebuilt
  the standalone handoff.** All six selected task-method paths use the plain
  active names and preserve historical replay identities. Source-to-shipped
  closure is current. Supervisor-host and unaided README review are not
  complete.

- **DeepSeek unknown-competence thread (U stopped).** Hosted Phase 2 candidate
  U piloted on the gold UNK slice (170): +2 final Purist vs A; LLM-only UNK
  accuracy did not improve. Full-750 scale-up aborted. Do not resume U.
  Local DeepSeek still deferred. Owners:
  [thread](docs/research/gan2026_deepseek_unknown_competence_thread_2026-07-31.md),
  [pilot compare](experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json).
- [Decision 0045](docs/decisions/0045-exect-default-policy-not-joint-combined.md)
  demotes ExECT joint/`combined` assembly: active comparison and Luna A/B/C
  use `default`/`default`. Joint materials are archived and opt-in only.
  Owners: [archive index](docs/experiments/exectv2/reliability/archive/exectv2_joint_policy_archive_README.md),
  [Luna dev140](docs/experiments/exectv2/reliability/exectv2_luna_prompt_variants_dev140_2026-07-31.md),
  [Luna test60](docs/experiments/exectv2/reliability/exectv2_luna_prompt_variants_test60_2026-07-31.md).
- Independent review of the 48-item ExECT semantic-support substrate remains
  the next paper evidence dependency. The rubric, reviewer separation, and
  adjudication rule are frozen; the review interface is ready.
- Supervisor endpoint/host checks and unaided README verification remain the
  next handoff dependency; no private data is needed to perform them.
- Six-model Gan LLM-with-rules ruleset remains finalized (2026-07-31) for the
  matched comparison. The unknown-competence thread may add a *named*
  DeepSeek candidate (prompt and/or narrow unknown-preserving gate) under its
  own protocol without reopening broad hybrid tuning from sealed rows.

## Next

1. Verify the rebuilt supervisor handoff on the intended host/endpoint and
   perform unaided README review. Source-to-shipped closure is already current.
2. Retention cleanup for the named Decision 0048 candidates is complete. The
   2026-08-02 wave removed the pipeline-flow HTML prototype, three superseded
   prompt draft notes, and the stale fresh-evidence validation750 mock-registry
   entry; audited and kept ExECT candidate configs,
   `frontend/public/mock-data/artifacts/`, and all three
   `experiments/archive/` Gan reference Markdown companions. Records:
   `docs/research/maintenance/retention_slice_*_2026-08-02.md`.
3. Run the Decision 0048 strict completion gate and update its status only
   after supervisor-host, unaided review, selected live/fixture/replay,
   frontend, generated-document, and internal-link paths pass.
4. Keep the separate research and validation dependencies intact: do not resume
   DeepSeek U to 750; defer local-route parity until its runtime exists; retain
   independent clinical review and supervisor-host verification as unvalidated
   work; and never tune from sealed `test450`, Real(300), or ExECT `test60`.

## Blocked or unvalidated

- Independent clinical review remains required before any clinical-validity
  claim. Internal annotation review is not that validation.
- Exact evidence is measured, but semantic support remains unmeasured. The
  48-item ExECT substrate is unreviewed and cannot clear that dependency.
- The archived ExECT joint policy retained three known deterministic
  regressions; it is not active. The one-call Diagnosis decision also accepts a
  measured dev140 quality loss from 0.8727 to 0.8542 Diagnosis F1 versus the
  two-call ablation.
- The bounded README-led slice and standalone source-to-shipped handoff rebuild
  are implemented and focused-checked. Exact endpoint/host setup and unaided
  use remain open. Those checks, not private-note testing, clear the
  operational dependency.

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
- DeepSeek unknown-competence (open):
  [protocol](docs/experiments/gan2026/gan2026_deepseek_unknown_competence_protocol_2026-07-31.md),
  [thread](docs/research/gan2026_deepseek_unknown_competence_thread_2026-07-31.md),
  and [Phase 0 baseline](experiments/gan2026_deepseek_unknown_competence_baseline_dev750_20260731.json)
- Shared eight-criterion synthesis:
  [reliability scorecard](docs/research/shared_reliability_scorecard_2026-07-18.md)
- Independent semantic-support review:
  [protocol](docs/experiments/exectv2/reliability/exectv2_semantic_support_review_substrate_protocol_2026-07-18.md)
  and local route `http://127.0.0.1:3000/clinical-review`
- ExECT Luna prompt-variant A/B/C (`dev140` + aggregate-only `test60`):
  [dev140 report](docs/experiments/exectv2/reliability/exectv2_luna_prompt_variants_dev140_2026-07-31.md),
  [test60 report](docs/experiments/exectv2/reliability/exectv2_luna_prompt_variants_test60_2026-07-31.md),
  [test60 panel](experiments/exectv2_luna_prompt_variants_test60_20260731/panel.json),
  and [residual map](docs/experiments/exectv2/reliability/exectv2_luna_single_call_dev140_residual_map_2026-07-31.md)
- Detailed work order: [active roadmap](docs/plans/ACTIVE_ROADMAP.md)

Use *implemented*, *verified*, *validated*, and *promoted* precisely.
