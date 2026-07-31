# Active roadmap

Last updated: 2026-07-31

[Project status](../../PROJECT_STATUS.md) owns current evidence and checks.
[Paper claim status](../canon/10_paper_provenance.md) owns claim strength.

## Objective

Close the paper's named evidence gaps without changing the verified pipeline,
data splits, or limits on what each result supports.

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
    Matched six-model Gan v0.5 dev750 coverage remains pending; the complete
    v0.7 development panel is quarantined as a historical diagnostic.
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

## Limits

- GEPA optimization is closed; one saved LLM-only run remains as a negative
  comparison.
- The source for the Gan multi-model comparator (`V12`) was removed; its
  aggregate report remains.
- No cross-task ExECT over-reading claim is active. The selected diagnostic
  replay has zero gold unknown-only letters, so the current ExECT annotations
  cannot estimate the predeclared measure.
- MLflow, the frontend, and Observatory are outside the retained deliverables.
- The five largest selected ExECT replay files are immutable Git LFS objects;
  the retained evidence index records their identities and retrieval details.
- Fixing the pipeline does not authorize model calls or locked-row inspection.
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
