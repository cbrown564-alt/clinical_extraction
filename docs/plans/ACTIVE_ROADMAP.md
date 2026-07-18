# Active roadmap

Last updated: 2026-07-18

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
17. **Joint bounded policy selected over the previous fallback.** A frozen
    dev140 replay composed the bounded Prescription and combined Diagnosis
    components with exact row-level identity and no SF or Investigations change.
    It produces 172 rescues, 3 regressions, and 153/160 rescue retention versus
    161, 9, and 143/160 for the previous fallback. All three saved model scores
    improve and no fallback-correct row becomes wrong. The joint policy is now
    the disclosed policy for the fixed comparison; the known EA0117 and EA0141
    failures remain visible.
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
19. **Six-model panels retained.** GPT-4.1-mini, Luna, Sol, thinking DeepSeek,
    Qwen, and Gemma are hash-selected for ExECT dev140 and aggregate-only
    test60. The same six models are retained for Gan v0.7 test450. Qwen and
    Gemma have the same canonical claim status as the hosted conditions;
    hosted/local route and local no-call-reparse differences remain caveats.
20. **Six-model comparison report completed.** The retained ExECT and Gan
    panels are synthesized with task-specific scores, component attribution,
    operational caveats, and no pooled capability ranking. Sol leads ExECT,
    Qwen leads Gan, and their cross-task rank correlation is `0.20`.
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

## Ordered evidence work

The completed eight-criterion cross-task reliability framework is specified in the
[shared reliability framework plan](reliability_framework_implementation_plan_2026-07-18.md).
Its remaining semantic-support dependency requires independent review; the
framework did not authorize model calls or locked-row inspection.

1. Decision 0043 setup and the authorized call attempt are recorded. The exact
   v0.5 payload matches all 450 retained GPT prompt payloads; the retained
   artifact fails non-prompt reconciliation, so fresh GPT was required. All
   four pilots passed. Fresh GPT and Luna completed (`361/450` and `362/450`
   Purist); Sol and DeepSeek stopped at 350/450 and 150/450 after the combined
   controller timeout. Their partial artifacts are rejected and must not be
   resumed. Write a new dated protocol before any further Sol or DeepSeek
   holdout calls.
2. Complete the Qwen/Gemma Gan validation750 study separately; it is
   development evidence and does not alter the retained test450 panel.

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
