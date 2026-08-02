# Active roadmap

Last updated: 2026-08-02

[Project status](../../PROJECT_STATUS.md) owns current evidence and checks.
[Paper claim status](../canon/10_paper_provenance.md) owns claim strength.

## Objective

Implement [Decision 0048](../decisions/0048-comprehension-and-handoff-refactor.md):
make the verified two-task, three-method research system clear and immediately
useful for supervisor review while preserving live generation, frontend
development workflows, exact selected-result replay, essential decision
evidence, and readiness for restricted external validation.

The cleanup is behavior-preserving by default. Historical material must be
reviewed for value and regeneration status before deletion. The final gate is
not a polished document alone: the selected live and replay paths, frontend,
generated outputs, canonical results report, and internal links must all be
verified.

## Active comprehension and handoff work

1. **Complete:** freeze `c3a6fbb7` as the baseline and record working-tree,
   Git-history, Git-LFS, regeneration, and replay ownership in
   [REGENERATION.md](../REGENERATION.md).
2. **Implemented and verified:** promote all three Gan methods to `rules`,
   `llm`, and `llm_with_rules`, with explicit legacy identity boundaries and
   no-call parity. The final canonical parity repair is `7ddc116a`.
3. **Implemented and verified:** the ExECT `rules`, `llm`, and `llm_with_rules`
   vertical slices now cover runtime, split/CLI, API, registry, trace/frontend,
   teaching material, generated architecture, locked-split rejection,
   distinct active/replay identities, and exact permitted-development parity.
   Sol's final reviews found no remaining actionable issue for `rules` at
   `bee48c6c` or `llm` at `c93c80b4`. The hybrid migration is implemented by
   `31103533` and `76d0dbcd`, with final replay-content, immutability, and
   parity closure at `6fd70834`. The full backend, architecture, replay,
   frontend, Ruff, and mypy gates pass.
4. **Source-to-shipped closure current; host/unaided checks open:** the
   README-led supervisor path exposes the five-stage orientation, generated
   six-path walkthrough, deliberate failure/recovery example, frontend
   startup, canonical results/limits, and exact no-call replay commands. The
   standalone handoff tree and ZIP were rebuilt from active source; source-to-
   shipped closure and the non-mutating checker pass. Supervisor-host
   verification and unaided README review remain open. Owner:
   [handoff plan](supervisor_local_extraction_handoff_plan.md).
5. **Retention wave advanced (2026-08-02):** retain selected architecture,
   evidence, replay, component-attribution, safety, and validation owners.
   Completed slices: run-note mock fixtures removed; pipeline-flow HTML
   prototype removed; three candidate-only prompt draft notes removed; ExECT
   candidate configs kept (5); frontend `mock-data/artifacts/` kept;
   `experiments/archive/` classified **keep** (three Gan reference Markdown
   companions hashed in the retained-evidence manifest); stale
   fresh-evidence validation750 mock-registry entry removed. Owners:
   [REGENERATION.md](../REGENERATION.md) and
   `docs/research/maintenance/retention_slice_*_2026-08-02.md`.
6. **Template complete; gate open:** the
   [restricted external-validation readiness template](../runbooks/external_validation_readiness.md)
   is linked. Run the strict Decision 0048 completion gate only after
   supervisor-host and unaided review checks pass.
7. **Label-leftover blockers (before 0048 status flip):** delete
   `comparison_mode` (group on active method only); rename architecture stage
   IDs `*.hybrid.*` → active-method namespaces and regenerate docs; remove the
   ExECT component-ablation supervisor surface (historical mock only); retag
   the Gan ablation three-way columns as selected active methods with plain
   labels. Keep API `split: validation750` with prose `dev750`. Owner:
   [Decision 0048](../decisions/0048-comprehension-and-handoff-refactor.md)
   completion gate; glossary terms in [CONTEXT.md](../../CONTEXT.md).
8. **Broader corpus retention triage advanced (2026-08-02):** deleted unserved
   ExECT mocks (~2.3 MB), five orphan/superseded docs, and seven tier-1
   experiment orphans; fixed REGENERATION retention-slice links; deferred
   scoring-lane JSONL batch and stale mock-registry path metadata. Records:
   `docs/research/maintenance/retention_slice_{unserved_exect_mock,orphan_docs,experiments_orphans}_2026-08-02.md`
   and [REGENERATION.md](../REGENERATION.md).

Gan test450 remains aggregate-only. ExECT full200 combines development and
held-out rows, so it is not an independent holdout.

## Completed foundation

1. **Repository reduced.** Historical documents, saved outputs, unused
   candidates, reporting machinery, and the secondary UI were removed.
2. **Engineering checks restored.** Ruff, mypy, full pytest, prompt snapshots,
   retained-evidence validation, and all six reference replays pass. CI runs
   the three repository-wide checks.
3. **Pipeline fixed for new evidence.** Retained evidence index v3 records source
   commit `6c6df72c`, Python and dependency versions, the six reference runs,
   and the exact prompt, scorer, split, repair, model, runbook, and CI policies.
4. **Clean checkout and paper checked.** A separate Python 3.11 checkout
   retrieved the Git LFS evidence, checked hashes and split restrictions,
   replayed all six runs, passed the full suite, and reproduced the tables. The
   Markdown and IEEE sources now use only selected evidence and state what each
   result can support.
5. **Gan efficiency closed with a bounded result.** On saved test450 aggregates,
   V12 gains 15 Purist-correct rows while requiring three cold model passes per
   note rather than one. Matched token, cost, latency, hardware, and cache
   telemetry was not retained, so those claims were removed instead of
   reconstructed from incompatible runs.
6. **ExECT published-metric development closed.** A no-call rules-only dev140
   replay now reports normalized-phrase, CUI, and all-feature scores for all
   nine entity types. Macro item F1 is 0.5687, 0.7144, and 0.6020 respectively;
   this is a development metric-family result, not reproduction of the paper's
   original system or 0.87/0.90 validation scores.
7. **ExECT Diagnosis review and implementation closed.** All 246 dev140 review
   rows were resolved into 173 representation issues, 72 extraction errors,
   and one uncertain row. Sensitivity views were added without changing gold
   or the fixed scorer. Shared deterministic fixes improved the rules-only and
   hybrid development scores; the one fixed LLM prompt candidate regressed and
   was rejected. Test60 was not inspected and no candidate was promoted.
8. **ExECT comparison architecture corrected.** Saved full200 outputs showed
   that the historical Prescription lane was deterministic-only and the
   Seizure Frequency lane included an independent extractor union.
   [Decision 0040](../decisions/0040-final-exect-llm-with-rules-family-ownership.md)
   records the corrected model-led family contract. Durable configurations and
   a no-call Git-blob replay now reproduce the corrected aggregates and add SF
   `state_profile`, exact-evidence, attribution, schema/parse, fact-origin, and
   deterministic-regression accounting. Nonzero correct-to-wrong counts keep
   the historical model rows unpromoted.
9. **Model-reported confidence closed with a negative result.** A protocol was
   frozen before a no-call replay separated dev140 from aggregate-only test60.
   Test60 failure AUROC was 0.5394 for GPT-4.1-mini, 0.5503 for historical
   DeepSeek, and 0.4895 for Qwen. Neither fixed review rule met the catch-rate
   and burden gates, so no confidence-based review policy was adopted.
10. **Model-led deterministic regressions characterized on dev140.** A
    predeclared no-call study filtered saved producer blobs to the permitted 140
    development identifiers before assembly. Across 319 changed model/family
    rows, the family-local view records 160 rescues, 41 regressions, and 118
    changed-still-wrong outcomes, all with exact evidence. Seizure Frequency is
    retained; Diagnosis and Prescription need a bounded policy candidate.
11. **Annotation evidence consolidated.** A generated 584-record taxonomy
    hash-checks 13 retained sources, maps all 57 explicitly cited letters, and
    links direct defects, conventions, ambiguity, multiplicity, scorer effects,
    handling, sensitivity, and review status. Ten historical Diagnosis concept
    rows remain aggregate-only, and independent clinical review remains open.
12. **First model-preserving policy bundle rejected.** The predeclared dev140
    replay reduced correct-to-wrong changes from 41 to 9 but retained only 143
    of 160 comparator rescues. The 17 lost rescues exceeded the allowed ten;
    aggregate F1 improvement did not override the row-retention gate.
13. **Prescription residual-removal candidate rejected.** Local selected-text
    frequency precedence fixed the shared-evidence rescue-scope defect, but
    removing all Prescription residual additions made four comparator-correct
    exact-evidence rows wrong. The residual group contains demonstrated
    missing-regimen recovery and cannot be removed wholesale.
14. **Bounded Prescription policy stopped after one candidate.** The combined
    dev140 candidate removed all 23 model-correct regressions, produced 46
    rescues, retained 40/41 comparator rescues and all four demonstrated
    missing-regimen rows, but made EA0141/Qwen wrong from a comparator-correct
    result. Its zero-regression gate failed; no second Prescription candidate
    will be tuned.
15. **Diagnosis guards evaluated separately.** The combined subsumption and
    absence-preservation guards produced 88 rescues, three regressions, and
    retained 75/81 comparator rescues. They preserved EA0156 and confined lost
    rescues to EA0082/EA0126, but left the EA0117 synonym-residual regression
    under all three models. The predeclared mechanism gate failed.
16. **Implemented fallback selected with its limitation visible.** Further rule
    iteration is closed. The user selected the implemented model-preserving
    bundle for the next comparison despite its original 143/160 rescue-retention
    failure. This policy choice does not convert either negative study into
    promotion evidence.
17. **Joint bounded policy selected over the previous fallback (later demoted).**
    A frozen dev140 replay composed the bounded Prescription and combined
    Diagnosis components with exact row-level identity and no SF or
    Investigations change. It produces 172 rescues, 3 regressions, and 153/160
    rescue retention versus 161, 9, and 143/160 for the previous fallback.
    **Superseded for active use by decision 0045 (2026-07-31):** live ExECT
    comparison uses `default`/`default`; joint/`combined` is archived after
    matched six-model gains proved marginal for the complexity.
18. **Single-call tradeoff selected and split defect contained.** A
    predeclared no-call GPT-4.1-mini replay filtered retained
    full200 blobs to the manifest dev140 IDs before assembly. Replacing the
    dedicated Diagnosis decomposer with the structured four-family output
    reduced final Diagnosis F1 from `0.8727` to `0.8542`, with 3 rescues and 11
    regressions. The study also found that the first six-model runner selected
    the first 140 sorted letters, only 94 of which were manifest dev rows.
    Affected runs were stopped; the runner now uses the manifest and rejects
    contaminated resume artifacts. The candidate failed its experimental gate,
    but decision 0041 selects it for the final comparison because the small
    final-F1 difference does not justify a second model pass.
19. **Six-model panels retained.** GPT-4.1-mini, Luna, Sol, DeepSeek,
    Qwen, and Gemma are hash-selected for ExECT dev140 and aggregate-only
    test60. The same six models are retained for the selected Gan v0.5
    test450 panel. Qwen and
    Gemma have the same canonical claim status as the hosted conditions;
    hosted/local route and local no-call-reparse differences remain caveats.
20. **Six-model comparison report completed.** The retained ExECT and Gan
    panels are synthesized with task-specific scores, component attribution,
    operational caveats, and no pooled capability ranking. Sol leads both
    selected test panels, and their cross-task rank correlation is `0.61`.
    Matched six-model Gan v0.5 dev750 coverage is complete; the complete v0.7
    development panel is quarantined as a historical diagnostic.
21. **ExECT SF over-inference analogue closed as diagnostic.** A predeclared
    no-call replay covers all six models and 840 model-letter dev140 pairs. The
    deterministic SF stage improves state-profile F1 for every model, with 54
    wrong-to-correct and one correct-to-wrong transition, but the gold
    unknown-only denominator is zero. Empty-gold letters were not substituted,
    so Gan-to-ExECT over-reading transfer remains unsupported.
22. **Shared reliability framework implemented and verified.** Decision 0044 and the
    canonical design define eight shared questions with task-specific measures,
    assurance gates, evidence states, and comparability rules. Generated machine
    and human scorecards map all 16 task-by-criterion cells without numerical
    pooling or a composite score. A 48-item ExECT dev140 semantic-support sample
    is prepared but remains unreviewed.
23. **All six-model dataset panels completed.** ExECT has all six fixed one-call
    conditions on dev140 and aggregate-only test60. Gan has all six models on
    aggregate-only test450 and all twelve model-by-method conditions on
    dev750. Retained artifacts use the legacy identifier `validation750`.
    Every Gan development condition has 750 unique manifest rows
    and 750 valid row traces. The generated no-call summary records hashes,
    aggregate scores, evidence counts, failures, and matched transitions.
24. **Gan post-panel replay, attribution, and retention completed.** The bounded
    schema policy recovers 11 development records across the twelve conditions
    while changing zero existing selected answers. The retained 9,000-row audit
    separates score layers, format/schema repair, clinical semantic repair,
    evidence, first failure, matched method transitions, and rules-control
    regressions. The result supports a bounded development comparison, not
    promotion over the deterministic rules control.
25. **Independent semantic-support review workflow prepared.** The simplified
    first-round rubric records one required clinical-support judgment
    (`supported`, `unsupported`, or `unclear`) plus optional notes. Two-reviewer
    blinding and third-reviewer adjudication remain frozen. The local ExECT
    review route serves the 48-item dev140 sample with highlighted full-letter
    context, reviewer-separated revisioned decisions, and JSON export. Prior
    trial decisions were cleared for this revision; review conclusions remain
    uncollected.

## Ordered evidence work

The completed eight-criterion cross-task reliability framework is specified in the
[shared reliability framework plan](reliability_framework_implementation_plan_2026-07-18.md).
Its remaining semantic-support dependency requires independent review; the
framework did not authorize model calls or locked-row inspection.

1. Give two independent clinicians separate reviewer IDs and have each finish
   all 48 items without viewing the other reviewer's decisions.
2. Adjudicate every field-level disagreement with a third named clinician while
   retaining both original decisions and their revisions.
3. Validate and export the completed review package, then update the shared
   reliability result and paper claim owner within the protocol's limits.

## Active development research (separate from paper holdout)

### DeepSeek unknown-competence (open)

Author-collaboration track: local DeepSeek; product arms **LLM-only** and
**LLM-with-rules** only (no rules-only). Tune on `dev750` unknown slices;
design for Real(300)-like unknown prevalence; never tune on Real(300) or
sealed `test450`.

Phase 0 hosted baseline fails collaboration gates. Phase 2 candidate U
(`v0.8_deepseek_unknown`) was piloted on the gold UNK slice (170): **+2**
final Purist vs A, LLM-only UNK accuracy worse. **Full-750 scale-up aborted**
as not worth the cost. Do not resume U. Local DeepSeek still deferred.
Thread remains open only if a sharper next component is chosen.

Owners:
[thread](../research/gan2026_deepseek_unknown_competence_thread_2026-07-31.md),
[pilot compare](../../experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json),
[protocol](../experiments/gan2026/gan2026_deepseek_unknown_competence_protocol_2026-07-31.md),
[baseline](../../experiments/gan2026_deepseek_unknown_competence_baseline_dev750_20260731.json).

### Closed recent Gan / ExECT tracks

Gan LLM-with-rules ruleset finalized 2026-07-31. The Luna prompt-variant /
residual / floor thread that produced it is closed for further rule tuning
unless a new predeclared study reopens it.
Owners: [six-model comparison](../research/six_model_comparison_report_2026-07-18.md),
[dated-count / guards](../research/gan2026_luna_dated_count_competing_rate_report_2026-07-31.md),
[final-ruleset replay](../../experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json),
[Luna summary](../research/gan2026_luna_prompt_variants_report_2026-07-30.md).
Do not inspect sealed `test450` rows for tuning.

ExECT active Diagnosis/Prescription policy is `default`/`default`
([decision 0045](../decisions/0045-exect-default-policy-not-joint-combined.md)).
Joint/`combined` is archived (opt-in replay only). Luna prompt-variant A/B/C is
answered under default repair; C moves SF most on holdout (`+5` SF letters;
SF F1 `0.5693 → 0.6260`). Dx/Rx residual-addition rule reopening remains out of
scope.
Owners: [archive index](../experiments/exectv2/reliability/archive/exectv2_joint_policy_archive_README.md),
[Luna dev140](../experiments/exectv2/reliability/exectv2_luna_prompt_variants_dev140_2026-07-31.md),
[Luna test60](../experiments/exectv2/reliability/exectv2_luna_prompt_variants_test60_2026-07-31.md).

Cross-track residual-floor audit (2026-07-31): plain-English synthesis of why
~85–90% Gan and ~0.8 ExECT ceilings persist after prompt and rule work. Next
levers are selection architecture, multi-layer scoring, explicit gold policy,
and hard-case review — not another open-ended prompt/rule pass.
Owners: [error-floor audit](../research/why_the_error_floor_persists_2026-07-31.md),
[policy catalog](../research/clinical_selection_policy_catalog_2026-07-31.md).

## Architecture recovery (phases 1-4 complete, 2026-07-31)

The four documentation phases proposed by the
[pipeline understandability review](../reviews/pipeline-understandability-review-2026-07-30.md)
are implemented. No prediction-bearing code changed and no score moved.

- **Phase 1 — stage manifests.** Six machine-readable manifests, one per
  selected task-method pair, in `src/clinical_extraction/architecture/manifests/`.
  Every stage declares its owner, whether it may change clinical meaning, its
  implementation path and callable, its governing test, and the trace fields
  that prove it ran. `validate_all()` resolves every callable and test, so a
  manifest cannot describe code that does not exist.
- **Phase 2 — executable teaching cases.** One Gan letter and one ExECT letter
  through all three methods each, built by running the real implementations
  with fixture model outputs and no model calls. The Gan case shows the model
  selecting a year-to-date total and the deterministic layer correcting it;
  the rescue is attributed to one named repair family by a walk that refuses to
  publish an attribution it cannot reproduce.
- **Phase 3 — six method cards.** One-sentence, sixty-second, stage table,
  stage walkthrough, code map, and the five recall questions, generated per
  method under [`docs/architecture/method_cards/`](../architecture/method_cards).
- **Phase 4 — diagrams.** Overview, ownership matrix, two detailed hybrid stage
  diagrams, and a result-attribution origin view, all generated from the
  manifests. `python scripts/build_architecture_docs.py --check` fails on drift
  and runs under `pytest`.

Also closed: the `syn_014` trace fixture attributed Gan current-event selection
to a deterministic component (review finding 5). It now shows the model
returning `selected_event_ids` and a `final_label`, with deterministic code
resolving and optionally repairing that selection. The trace contract gained an
`owner_kind` on `OperationOwner` because it previously could not express a
model-owned clinical change at all.

**Closed by decision 0047.** The selected methods have task-local canonical
entry points, active wrappers delegate to them, and the selected-development,
locked-aggregate, retained-evidence, architecture, and clean-checkout gates
pass.
Finding 7's method-identity decision is closed by decision 0046: the primary
ExECT comparison uses matched Sol one-call peers, while `v08` and GEPA are
historical or negative comparators.

## Canonical orchestrator refactor (complete)

[Decision 0047](../decisions/0047-full-canonical-pipeline-orchestrator-refactor.md)
owns the implementation plan, guardrails, parity evidence, stop rules, and
method-by-method migration order. Typed orchestrators, selected-policy guards,
delegation, one-call ExECT sharing, focused legacy parity, full permitted-
development replay, retained six-cell replay, aggregate-only locked-split
safety checks, architecture drift checks, and repository checks are complete.
A fresh checkout of commit `46fec88a` passes 1,488 tests, Ruff, mypy, and the
documented no-call evidence checks.

No model calls or locked-row inspection are authorized merely to establish
parity or restore historical evidence. The selected live-run paths remain
supported under decision 0048. Any semantic difference stops the cleanup until
it is repaired or handled as a separate, versioned decision.

## Limits

- GEPA optimization is closed; one saved LLM-only run remains as a negative
  comparison.
- The source for the Gan multi-model comparator (`V12`) was removed; its
  aggregate report remains.
- No cross-task ExECT over-reading claim is active. The selected diagnostic
  replay has zero gold unknown-only letters, so the current ExECT annotations
  cannot estimate the predeclared measure.
- MLflow and Observatory remain outside the retained deliverables. The
  frontend is retained as the selected system's live and saved-run
  demonstration and development workflow.
- The five largest selected ExECT replay files are immutable Git LFS objects;
  the retained evidence index records their identities and retrieval details.
- Fixing the pipeline does not authorize model calls or locked-row inspection
  for evidence repair or tuning. New live experiments require their own
  protocol and run-readiness record.
- Internal annotation review does not establish clinical validity; that claim
  still requires independent clinical review.

## Verification commands

```sh
uv sync --python 3.11 --frozen --extra dev
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
python scripts/check_exectv2_model_led_audit.py
python scripts/analyze_exectv2_model_led_dev140_regressions.py
python -m pytest
python -m ruff check .
python -m mypy src
```
