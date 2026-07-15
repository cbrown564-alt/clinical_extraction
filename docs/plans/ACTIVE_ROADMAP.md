# Active roadmap

Last updated: 2026-07-15

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
   commit `46562134`, Python and dependency versions, the six reference runs,
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

## Ordered evidence work

1. Predeclare a Prescription candidate that retains demonstrated
   missing-regimen rescues, applies local rescue scope and the explicit-current
   guard, and ablates residual additions by rule group rather than wholesale.
2. Predeclare a separate Diagnosis candidate for residual subsumption and
   absence-phenotype preservation with row-identity rescue retention.
3. Freeze the accepted decision-0040 policy, then predeclare and run the fixed
   six-model roster with the same corrected
   model-led pipeline and scorer: GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol,
   hosted DeepSeek V4 Flash, local Qwen 3.6:35B, and local Gemma 4 26B. Resolve
   whether the historical `deepseek/deepseek-chat` artifact proves that
   thinking was enabled before counting it as complete. Otherwise rerun that
   API model with thinking enabled and report it as DeepSeek V4 Flash.

## Limits

- GEPA optimization is closed; one saved LLM-only run remains as a negative
  comparison.
- The source for the Gan multi-model comparator (`V12`) was removed; its
  aggregate report remains.
- No cross-task ExECT over-reading claim is active because no selected report
  supports it.
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
