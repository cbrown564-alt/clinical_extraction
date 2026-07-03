# Project Status

Last updated: 2026-07-02

## Active Objective

ExECTv2 is in a reliability/component-evidence phase after the Satellite 13
LLM-only plateau. `clinical_headline` de-duplicated clinical recovery is the
headline surface; strict benchmark/CUI results stay diagnostic. Paper-facing
language and results scaffolding live in `docs/research/`. Resume the
paper/results sprint from `docs/research/paper_manuscript_2026-06-26.md` and the
IEEE LaTeX draft in `literature/IEEE/IEEE-conference-template-062824/`
(markdown is ahead of the LaTeX draft as of 2026-06-30 — the LaTeX has not yet
been re-synced with the 2026-06-30 Diagnosis gold-quality revision below).

## Current Read

Current evidence stack:

- ExECTv2 `clinical_headline` is primary. Full-200 GPT-4.1-mini v08 is `0.8680`
  (was `0.8502`; the 2026-07-02 four-family scorer-correctness sweep moved it to
  `0.8616` first, then the same-day P7 producer fix moved it again — see the
  pipeline-assumption-audit entries under Now/Done Recently, and registry run
  `exectv2_holistic_finding_assembly_v08_full200_p7fix_gpt41mini_20260702`);
  no-verifier `0.8431`; lean 2-call no-SF `0.8356` overall / `0.7525` SF (these
  two are not yet re-scored/re-run under the current-code scorer or P7 fix).
- Same-core full-200 aggregate-only: GPT-4.1-mini `0.8356`; DeepSeek `0.8566`
  overall / `0.7602` SF with `1` accepted Diagnosis caveat; Qwen repair v02
  `0.8197` overall / `0.7020` SF with `0` call/parse failures, structured
  evidence `0.9950`, exact evidence `1.0000`.
- Reliability validation: calibration ECE `0.0432`, Brier `0.2245` vs `0.2387`;
  review routing failed (`0.9661` burden, `0.9037` catch); robustness hard-slice
  F1 `0.8336` across `414` cells; Investigations deterministic replacement is
  not ready (`0.9213` remains strongest with verifier + suppression).
- Component Impact: dev140 one-component-off readout has `16` replay-only rows;
  full200 aggregate-only replay has `9` rows across GPT-4.1-mini, DeepSeek, and
  Qwen repair v02. Full200 deltas are positive for dictionary (`+0.0186` to
  `+0.0290`), residual semantic lens (`+0.0098` to `+0.0117`), and headline
  projection (`+0.0302` to `+0.0350`); report:
  `experiments/exectv2_component_off_replay_full200_20260626.md`.
- Gan holdout evidence is frozen: v0.7 test450 `346/450` Purist, `365/450`
  Pragmatic; consensus/fresh constrained Gate 4 failed (`348/450`, precision
  `0.5909`), while exact-source Gate 4 passed only as frozen aggregate evidence
  (`359/450`, `+16`, precision `0.6000`).
- GEPA workstream closed out (06-28 to 06-30): single-pass GEPA plateaus
  ~0.74 (mini) / ~0.65 (Qwen) on dev140 `clinical_headline`, ~0.17-0.19 below
  the v08 hybrid (`0.9189`, was `0.9155`; corrected 2026-07-02 by the P7
  producer fix propagated through the full assembly — the historical `0.9155`
  was never itself registry-tracked and predates several since-landed scorer
  fixes; registry run
  `exectv2_holistic_finding_assembly_v08_dev140_p7fix_gpt41mini_20260702`);
  root-caused to producer evidence-recall, not verify/arbitrate stages. (The
  mini figure was ~0.73 / 0.7313 before the 2026-07-02 four-family
  scorer-correctness fixes re-scored it to 0.7491 — see the
  pipeline-assumption-audit entry under Now/Done Recently.)
  (`docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`).
  Cross-model close-out: Qwen 3.6 35B underperforms mini on the identical
  architecture and does not clear its own hand-tuned baseline
  (`docs/research/exectv2_gepa_qwen_cross_model_2026-06-30.md`).
- SF "plateau" reframed as a gold-quality ceiling, not a model ceiling
  (SF Phases 1-7, closing in
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`):
  only 15/53 dev140 `state_profile` metric-errors are genuine model mistakes;
  counting only genuine errors the model is clinically defensible on 89.3% of
  letters vs the metric's 62.1%. The same row-adjudication method applied to
  Diagnosis on 2026-06-30 found the identical mechanism, more lopsided: of 209
  dev140 Diagnosis disagreements, 14.8% are genuine model error, 85.2% are gold
  multiplicity/consolidation artifacts (adjusted F1 0.6617 -> 0.9501); see
  `docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md`
  and the manuscript revision notes in `docs/research/paper_drafts/`.

## Active Priorities

1. Treat `clinical_headline` recovery as primary; strict benchmark/CUI stays diagnostic.
2. Keep deterministic validation/projection separate from prediction-bearing facts.
3. Separate Reliability Scorecard from Component Impact by split, scorer, and inspection boundary.

## Work Board

### Now

- 2026-07-03: **Section C cancelled — deterministic Prescription producer
  already wins** (head-to-head feasibility finding,
  `docs/experiments/exectv2/prescription/exectv2_rx_headtohead_feasibility_finding_2026-07-03.md`).
  The planned LLM-vs-deterministic head-to-head + holdout eval was predicated
  on the deterministic producer dropping the LLM probes' recall gains. A free
  scorer-replay probe refutes this: the deterministic producer already emits
  every fact the probes recovered (EA0038 carbamazepine 5/5, EA0021 nocte
  split 2/2) and scores **0.9615** on dev140 Rx `clinical_headline` — *higher
  than the LLM probe combined arm (0.9526)* and far above the GEPA LLM
  canonical (0.9122). The probes compared the LLM against itself (a weak 0.9073
  baseline), never against the deterministic producer v08 actually uses.
  Introducing an LLM producer would regress Rx by -0.0089 at real cost. Both
  Section C hypotheses (`rx_llm_producer_into_v08_2026-07-03`,
  `rx_deterministic_rule_harden_2026-07-03`) REFUTED; C2/C3 cancelled, saving
  ~760 planned LLM calls. This *reinforces* the audit's Prescription finding:
  the deterministic lane is strong precisely because it sidesteps the LLM's
  structural failure modes (current-vs-future conflation, non-AED
  over-extraction).
- 2026-07-03: **SF ledger re-run under the finalized scorer** (rescore-sweep
  discrepancy flag #3; ~280 dev140 gpt-4.1-mini calls, predeclaration
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_rerun_predeclaration_2026-07-03.md`).
  Re-ran the two-stage SF-verify program on dev140 to bring the SF gold case
  ledger onto a current, self-consistent prediction basis. Result: stage-2
  `state_profile` F1 **0.7793** (vs the registered 0.7483 and the documented
  0.7724 06-29 re-run — temp-0 nondeterminism); **stage2 reproduces stored
  jsonl 99/140**, exactly the documented irreducible ceiling (the original
  06-28 completions were never cached, so gpt-4.1-mini temp-0 cross-session
  nondeterminism caps faithful reproduction). Reconciliation: the new re-run's
  disagreement set is nearly identical to the existing ledger's (52/53 letters
  overlap, 0 new disagreements); the only change is **EA0121 now resolved**
  (its 2 `scorer_mechanics_artifact` rows were exactly the SF-1 zero-count
  fix's target — the 0/3 variable range is now correctly `active-rate`).
  Ledger 66->64 rows, 0 unadjudicated, genuine share 28.8%->29.7%. **Two-basis
  condition (deliberate, documented):** the SF dossier's F1 ladder shows the
  registered 0.7483 (live-queried from the registry, the scored surface of
  record); its mechanism table is built on the 0.7793 re-run (the substrate
  the adjudications were authored against). The registered 0.7483 number's
  own row-level substrate cannot be reconstructed (completions gone); it
  keeps its existing disclosure and is not overwritten.
- 2026-07-03: **Re-finalized the Rx/Inv gold case ledger after the scorer-correctness
  sweep** (rescore-sweep discrepancy flag #2). The 07-02 sweep regenerated
  `_cases.json` under the finalized scorer (48->36 Rx, 31->35 Inv), but
  `finalize_rx_inv_canonical.py` joined verdicts to cases by *positional*
  `case_id` — renumbering silently mis-paired Rx and crashed Inv. Two findings:
  (1) the durable fix is content-keying (`letter_id + match_key +
  disagreement_type`) via a git-recovered pre-sweep case-set bridge, which
  recovers verdicts that survive the renumbering; (2) **5 of the 6 rows the
  direct ledger reconciliation had orphaned as `unadjudicated` were already
  adjudicated** under the same content key in the pre-sweep set — the
  reconciliation just failed to match them. Only **EA0114** (carbamazepine
  400/2, whose form flipped from spurious-FP to missed-FN under CUI-unification
  + clause-scope) was genuinely new; it inherits the clinical logic of pre-sweep
  case 24 (`MODEL_DEFENSIBLE`/`scorer_mechanics_artifact` — the model got the
  drug right, the disagreement is a key-construction artifact). Result: 0
  unadjudicated rows. Corrected genuine-error shares under the finalized
  scorer: **Prescription 26/36 = 72.2%** (was 60.4% on the pre-clause-scope
  48-case set; the fix dropped 12 scorer-artifact disagreements, concentrating
  the remainder on genuine errors), **Investigations 23/35 = 65.7%** (was
  67.7% on 31). Dossiers regenerated.
- 2026-07-03: **Re-scored the 5 stale `exectv2_2call_no_sf_adjudicator_*` runs**
  under the finalized scorer (rescore-sweep discrepancy flag #1). The 07-02
  sweep left these out of scope believing their cached predictions absent; they
  are present. Built a committed harness
  (`scripts/rescore_model_swap_runs.py`) that replays the deterministic
  finding-assembly over each run's saved-jsonl producers — zero new LLM calls,
  the exact historical computation path (CUI-projected `concept_only` for Dx).
  dev140: deepseek 0.8596->0.8643, gpt41mini 0.8396->0.8526 (Inv 0.8347->0.8487
  from F2/I1 on the structured-direct lane), qwen36 0.8018->0.8191,
  qwen36_repair_v02 0.8319->0.8423. full200 (qwen36_repair_v02) 0.8197->0.8318
  (overall-only per the aggregate-only mandate). Hypothesis
  `rx_2call_no_sf_rescore_finalization_2026-07-03` CONFIRMED.
- 2026-07-02: **P7 propagated through the full v08 hybrid assembly** (the
  scope note deliberately left open in the parked-items closure below,
  actioned same-day after user go-ahead). Regenerated `prescription_repair_v03`
  with the P7 fix (deterministic, zero new LLM calls) for both dev140 and
  full-200, swapped only that one producer into the existing v08 manifest
  (`dataclasses.replace`, never overwriting an archived artifact in place —
  the dev140 cached file is shared by 5 other manifests, v09/v09b/v09h1-3, not
  touched). Built a same-day baseline (unmodified manifest, today's scorer)
  alongside the treatment for both splits, isolating P7's effect from
  unrelated scorer drift: dev140 baseline `0.9130` -> treatment `0.9189`
  (+0.0059); full-200 baseline `0.8616` (reproduces the earlier rescore-sweep
  number exactly) -> treatment `0.8680` (+0.0064). Both splits: Prescription
  moved (dev140 `0.9386`->`0.9615`, full-200 `0.9033`->`0.9278`),
  Diagnosis/SF/Investigations byte-identical to baseline on both — confirms
  clean isolation, recall-driven, zero precision cost, matches the isolated
  rules-only replay's shape exactly. Two new registry entries
  (`exectv2_holistic_finding_assembly_v08_dev140_p7fix_gpt41mini_20260702`,
  `..._full200_p7fix_gpt41mini_20260702`; the prior full-200 currentcode entry
  marked superseded), a new hypothesis
  (`rx_p7_v08_hybrid_headline_propagation_2026-07-02`, CONFIRMED), dossiers
  regenerated, canon docs (`08_gepa.md`, `10_paper_provenance.md`) and this
  file's own `0.9155`/`0.8502` citations corrected with disclosure. Script:
  `scripts/run_exectv2_v08_p7_prescription_refresh_audit.py`. Not yet
  committed.
- 2026-07-02: **Pipeline assumption audit parked items — all 5 closed** (P6, F2,
  SF-2, P7, SF-5; picked back up same-day after the audit above). None costed
  (zero new LLM calls, all dev140-replay-verified), none touch a currently-cited
  headline number. **P6** (Rx `future_medication`/`weight_based_dosing`
  diagnostic-key clause scope): fixed, zero measurable impact on this run
  (matches its own "no citation at risk" framing), 2 new unit tests. **F2**
  (`scoring/match.py` greedy `_first_overlapping_prediction` → maximum-cardinality
  `_match_gold_to_predictions`): fixed after two design iterations — an
  exact-phrase-priority tie-break was tried and *rejected* (it degraded
  Prescription attribute-agreement by scrambling same-drug repeated-mention
  pairing that greedy preserved by coincidence of document order); switched to
  list-position proximity, which recovers Prescription's old pairing exactly
  while still fixing genuine cardinality loss (SF `source_near` recall
  0.6150→0.6203, `EA0143`, exactly the mechanism the guardrail doc predicted).
  **SF-2** (direction-aware SF state schema + metric): added
  `frequency_state_directional` + a new `state_profile_directional` companion
  metric (additive-only, `clinical_headline`/`state_profile` untouched); dev140
  F1 0.6810 vs `state_profile`'s 0.7200, making the SF Phase-6 "model defaults
  every direction to Same" finding visible as a score delta instead of a manual
  adjudication finding. **P7** (Rx multi-dose weight-context whole-evidence
  bug): the guardrail doc's own "needs re-prediction" classification was
  **wrong** — this producer runs on static gold-letter text, not live LLM
  output, so it was a free replay; fixed, isolated rules-only Prescription
  `clinical_headline` 0.9386→0.9615 (+9 tp/-9 fn). **SF-5** (producer-side SF
  state-definition reconciliation): same wrong-classification pattern as P7
  (both target modules are documented replay layers); `sf_state_projection.py`
  reconciled to the canonical `frequency_state_faithful` (incidentally also
  fixes a pre-SF-1-era zero-count precedence bug in its own local copy), zero
  regressions; `sf_unknown_suppression.py` deliberately **not** reconciled — its
  suppression predicate is keyed on the *old* "unknown" state as a proxy for
  "this FrequencyChange is a false positive," so widening the definition would
  silently disable suppression rather than improve it (a genuine
  predicate-redesign need, not a mechanical swap); neither module feeds any
  currently-cited number (only the retired v01-v05 finding-assembly manifests
  use them, not v08/v09). **Deliberately not attempted:** re-running the full
  v08 hybrid assembly to see whether P7's fix moves the manuscript's cited
  headline numbers (0.9155 dev140 / 0.8502 full-200) — P7's producer does feed
  the live `prescription_repair_v03` v08 lane, so this is a real open question,
  left for an explicit decision rather than done unilaterally given the
  blast-radius difference from the other four (diagnostic-only or
  currently-uncited) fixes. All five hypothesis-registry-recorded (`CONFIRMED`
  except SF-5 `PARTIAL`), dossiers regenerated, 139 tests green across the
  touched suites. Plan:
  `docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md` (status note
  appended). Not yet committed.
- 2026-07-02: **Pipeline assumption audit — COMPLETE, all phases** (holistic
  scorer-correctness re-assessment triggered by the medication follow-ups; the
  remaining phases executed 2026-07-02 with five parallel sub-agents and user
  go-ahead on the costed probes). Plan (now marked COMPLETE):
  `docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md`.
  - Phase 0 (`..._audit_2026-07-02.md`): shared PRF1 reduction provably correct
    (no systemic corruption); the seed defect *class* — a fact's scored
    membership depending on text/facts outside its own scope — recurs in every
    family.
  - Phase 1, all four measurement bugs fixed under gating
    (`..._phase1_2026-07-02.md`, `..._d1_diagnosis_2026-07-02.md`): Prescription
    clause-scoping (0.8766→0.9073), SF zero-count precedence (0.5921→0.5982),
    Investigations text-fallback gate (latent), and **D1 Diagnosis
    hierarchy-aware match now landed** — the `concept_only` `clinical_headline`
    surface `clinical_headline_unit_keys` actually uses moves 0.6617→0.6779 via 5
    true ancestor/descendant recoveries (EA0002/06/07/35/153), zero spurious
    cross-credits, kill criterion met; reinforces (does not threaten) the 85.2%
    gold-artifact finding. `dx_specificity_collapse_cross_contamination_2026-07-02`
    → CONFIRMED.
  - Phase 2 (costed, `docs/experiments/exectv2/prescription/exectv2_rx_extraction_probes_2026-07-02.md`,
    gpt-4.1-mini dev140, ~560 calls): **#2 current-vs-future dose conflation
    CONFIRMED** (+0.0322 vs fresh matched baseline, recall-driven; EA0021
    corrected); **#3 non-AED over-extraction CONFIRMED** (+0.0277,
    precision-driven fp 18→7) with an honestly-recorded recall cost (the naive
    AED-only gate also dropped genuine AEDs — a production version needs a tighter
    gate). Both were dev140 hand-tuned instruction probes, not shipped.
  - Phase 3 (`..._phase3_2026-07-02.md`): drug-lexicon valproate/brand gaps
    (Rx 0.9073→0.9122, EA0093 unification), P4 note-window scope fix
    (headline-neutral, `guideline_defaulted_frequency` diagnostic now functional),
    and a gold-data-issue log stood up (`experiments/gold_data_issues.jsonl`,
    seeded with EA0146 Perampanel/brivaracetam).
  - Phase 4 (`..._phase4_guardrail_2026-07-02.md`): scorer scope-invariant +
    scorer↔projection consistency property tests, an edit-triggers-predeclaration
    gate (`scripts/check_scorer_edit_predeclaration.py` + runbook), the
    mechanism-taxonomy standing lens, and the "all cited runs" re-score sweep
    (`..._rescore_sweep_2026-07-02.md`): 13 dev140 runs + 1 full-200 aggregate
    (0.8502→0.8616, holdout protocol respected) re-scored, all four dossiers +
    frontend scorecard regenerated (contract test green). Parked with rationale:
    P6, SF-2, F2, P7, SF-5 (diagnostic-scoped / need re-prediction or a schema
    change).
  Canonical run overall dev140 `clinical_headline` **0.7313→0.7416→0.7491**
  (overwrite-with-disclosure: registry `primary_metrics` + disclosure, dossiers,
  frontend snapshot, and manuscript §4.2 footnote + Diagnosis gold-quality
  passages all updated). Every audit hypothesis in
  `experiments/hypothesis_registry.jsonl` now carries a final verdict.
- 2026-06-30: applying `docs/research/predecessor_lessons/` to the current
  evidence base (the packet's own absorption tables were stale relative to the
  GEPA/SF work done since 06-28). Five bounded items: (1) registry hygiene
  fixed — 247 artifact paths across 183 entries repaired, one pre-existing
  out-of-scope Gan entry left; (2) Diagnosis canonical row-adjudication (see
  Current Read above) — the highest-value finding, revises the manuscript's
  gap-mechanism claim; (3) evidence support-quality companion audit built
  (`experiments/exectv2_evidence_support_audit.py`), closing the FM1 guardrail
  that was "Partial"; (4) DeepSeek precision prompt profile probe (A5) — small,
  mechanistically clean positive (+0.0146 overall F1, precision +0.026/recall
  flat) on `docs/experiments/exectv2/reliability/exectv2_deepseek_precision_profile_probe_2026-06-30.md`;
  (5) this PROJECT_STATUS update + predecessor-lessons absorption table refresh
  + manuscript revision (in progress). The IEEE LaTeX draft has NOT yet been
  re-synced with the 2026-06-30 manuscript markdown changes — that is the next
  step before any camera-ready pass.
- Manuscript consistency pass (06-26) and the SF/Diagnosis gold-quality
  revisions (06-29, 06-30) are layered on the markdown source; the IEEE draft
  reflects only the 06-26 state. The remaining camera-ready-only items
  (author/affiliation block, acknowledgment, two-column last-page balance) are
  unaffected by the content revisions.

### Next

- **RESOLVED 2026-07-02:** four concrete follow-ups from the gold case ledger's
  Prescription/Investigations row-adjudication (see the pipeline-assumption-audit
  entries under Now / Done Recently and
  `docs/canon/workstreams/PRESCRIPTION_CANONICAL_LEDGER_CANON.md`). **All four are
  now resolved under the audit:** #1 → Phase 1 scorer clause-scope fix
  (Rx 0.8766→0.9073); #2/#3 → Phase 2 costed gpt-4.1-mini probes, both CONFIRMED
  (current-vs-future +0.0322; AED-only +0.0277, with a recorded recall cost);
  #4 → Phase 3 drug-lexicon unification (Rx →0.9122) plus the new gold-data-issue
  log (EA0146). Every corresponding hypothesis in
  `experiments/hypothesis_registry.jsonl` now carries a final verdict. Original
  queue detail retained below for provenance:
  1. **Scorer bug (candidate fix, 11/48 = 22.9% of Prescription's
     disagreements)**: `_is_future_medication`/`_is_weight_based_dosing` in
     `scoring/prescription.py` regex-match the *entire* gold annotation span
     text, so a gold span that bundles a current dose with titration language
     (e.g. "75mg bd, to reduce and stop") gets wrongly excluded from
     `clinical_headline` scoring even when the model's current-dose
     prediction is correct. Fix direction: scope the regex to the clause
     containing the scored dose, not the full span. Needs a dev140 replay
     confirming no regression on the letters this scoping *should* still
     exclude (doses that are genuinely weight-based/future for their whole
     span) before promoting — this retroactively changes historical
     Prescription F1 citations, so treat like any other scorer edit: replay,
     predeclare, don't just ship.
  2. **Current-vs-future dose conflation (candidate model/prompt fix)**: the
     model repeatedly asserts a letter's *proposed target* dose ("increase to
     800mg") as the *current* prescription, dropping the true current dose in
     the process (e.g. EA0021: model emits 800mg-bd, true current is
     700mg-AM + 800mg-nocte). Needs a GEPA or hand-tuned instruction probe
     specifically targeting "current medication" framing vs. titration/target
     language; affects a meaningful share of Prescription's 29 genuine
     errors.
  3. **Non-AED over-extraction (candidate model/prompt fix)**: the model tags
     cardiac/diabetes comorbidity medication (clopidogrel, ramipril,
     metformin) as Prescription facts in letters that conclude a
     non-epileptic cause; gold consistently excludes non-AED medication. An
     explicit "AED-only" scoping instruction is a plausible, low-risk probe.
  4. **Minor, lower-priority, not hypothesis-tracked**: a drug-name
     canonicalization lexicon gap (bare "valproate" doesn't unify with
     brand-derived "sodium valproate" in `contract/drug_lexicon.py`) and one
     gold data-entry bug found in kind (EA0146's gold `DrugName` field says
     "Perampanel" while its own `CUIPhrase`/`CUI` correctly resolve to
     brivaracetam) — worth a lexicon entry and a gold-data correction
     ticket respectively, neither score-moving enough to prioritize alone.
- **NEW 2026-07-01:** audited the whole project against the original
  supervisor brief (training-free multi-agent epilepsy-letter extraction;
  Section/Timeline + Field Extractor + Verification + Aggregator roles;
  single-prompt-vs-multi-agent reliability comparison at matched budget;
  dissertation deliverable). Research substance (evidence gates, structured
  validation, self-consistency, field-level F1, robustness, synthetic +
  de-identified data) is met or exceeded; architecture/vocabulary has
  drifted from the brief's literal framing (three-family rules/LLM-only/
  hybrid comparison instead of single-prompt-vs-multi-agent; no named
  Section/Timeline Agent; no dissertation document, only a paper-length
  manuscript). See
  `docs/research/supervisor_brief_conformance_audit_2026-07-01.md` for the
  full conformance table and
  `docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md` for the
  phased closure plan. Phase A (legibility crosswalk) DONE. Phase C
  (Section/Timeline Agent) DONE — built `exectv2/deterministic/
  section_timeline.py` and ran a dev140 ablation on SeizureFrequency +
  Investigations; **null result** (SeizureFrequency -0.0106, Investigations
  -0.0034, both within/near measurement noise), written up in
  `docs/experiments/exectv2/reliability/exectv2_section_timeline_ablation_2026-07-01.md`.
  Module kept in the codebase, not wired into production v08. Phase D
  (dissertation) confirmed out of scope — actual target is the existing
  5,000-word/8-page IEEE paper, user-owned. **Phase B DONE, revised scope**:
  the user challenged the original "cheap table" framing and it did not
  hold up — the only prior "multi-agent" artifact in this codebase
  (2026-06-12, Gan 2026) was found to hard-code tool calls and fake its
  multi-agent condition (four identical calls, cosmetic role labels).
  Rebuilt from scratch with genuine `dspy.ReAct` tool use and
  structurally-honest specialists (output schema cannot contain a final
  answer) on both tasks. **Gan 2026**
  (`docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md`):
  every new architecture beat single-prompt on a hard panel (Purist
  38%→64%), dynamic orchestration beat static fan-out, neither cleared the
  strict promotion gate at n=50. **ExECTv2 SeizureFrequency**
  (`docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_results_2026-07-01.md`,
  first agentic infrastructure ever built for ExECTv2): the pattern did
  *not* transfer — single-prompt was the best performer, new architectures
  trended mildly negative (small-sample, inconclusive). Cross-task
  divergence is the honest answer to the brief's key research question —
  agentic decomposition is task-dependent, not a universal win. All four
  phases of the gap-closure plan are now complete.
- **DONE 2026-07-01:** fixed the `test60` split-construction gap. The source
  dataset paper (Fonferko-Shadrach et al. 2024, *J Biomed Semantics*, DOI
  10.1186/s13326-024-00316-z) discloses "Four letters were duplicated within
  the set to test for consistency in annotations" — a deliberate, documented
  design choice by the corpus's original authors (confirmed: 4 duplicate
  pairs / 8 of 200 letters, 4%, exactly matching that statement), NOT a
  corpus integrity bug. The genuine, locally-fixable issue was narrower:
  `exectv2_split_v1.json` stratifies only by `has_seizure_frequency_mention`,
  with no identity-awareness, so it did not know to keep the paper's known
  duplicate pairs on one side of the boundary — one pair, `EA0159` (test) /
  `EA0160` (dev), landed across the frozen dev/test split. Fix: cut
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json` (dev unchanged at 140;
  `EA0159` dropped from test, so **test59** going forward), `v1` left
  untouched as historical record. `data.py`'s `DEFAULT_SPLIT_MANIFEST` still
  points at `v1`; cut over the next time a fresh test-split run is planned.
  See `docs/experiments/exectv2/exectv2_test60_split_dedupe_fix_2026-07-01.md`
  for the full audit (including a refinement: 3 of the 4 duplicate pairs show
  substantially different `.ann` annotations — consistent with genuine
  independent re-annotation for the paper's consistency check — while only
  the EA0159/EA0160 pair is near-identical) and
  `docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md`
  for the implementation plan this was Phase 0 of.
- **DONE 2026-07-01:** implemented the exploratory-review's Tier-1 items 1-4
  (`docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md`
  Phases 1-2). Registry hygiene: retroactively registered 7 silently-missing
  GEPA runs (2 distinct root causes — a swallowed load-failure in
  `_register()`, and a standalone launcher family that never had a
  registration path — plus a pre-existing broken artifact-path row that was
  blocking registry validation entirely) — 244 -> 251 rows
  (`docs/research/exectv2_registry_survivorship_bias_2026-07-01.md`, which
  also corrected the item's own framing: mean chain-length-to-publication is
  only 1.12, but 40.7% of the manuscript's own citation graph has no
  registry row at all). Cost-quality table
  (`docs/research/exectv2_cost_quality_matched_split_table_2026-07-01.md`)
  confirmed the 1-2 call delta and the ~9x deterministic-stack claim, but
  found the informally-cited "hybrid +0.2 F1, ~5x split-dependent" figure
  conflates two non-commensurable comparisons (real +0.18-0.20 vs. GEPA at
  dev140-only, untestable for split-dependence; a much smaller +0.015/+0.076
  premium vs. a 2-call baseline that IS split-comparable but not robust to
  baseline-model choice). Mechanical gold-inflation heuristic
  (`docs/research/exectv2_gold_inflation_mechanical_heuristic_2026-07-01.md`)
  recovered Prescription's 7 typo cases cleanly (0 false positives) but does
  NOT generalize to SF/Diagnosis (stem-collision false positives) — a
  calibrated pre-flight rule, not a universal detector. **Verify-stage
  credit-assignment GEPA rerun**
  (`docs/research/exectv2_gepa_verify_stage_credit_assignment_2026-07-01.md`):
  froze S0 + added a stage-local accept/reject/add feedback metric
  (independent of the merged-output diff; selection score unchanged) for the
  multistage generate->verify program. Result: 0.7235 -> **0.7596** dev140
  `clinical_headline` (+0.036, precision-driven), evolved verify instructions
  turned decisively filter-shaped (vs. the prior run's reformatting drift) —
  the review's credit-assignment hypothesis is CONFIRMED qualitatively, but
  the run narrowly MISSES the pre-registered kill-criterion (needed >=
  0.761, got 0.7596, -0.0014). This nuances but does not overturn the
  06-28/06-30 GEPA close-out's "root-caused to producer evidence-recall, not
  verify/arbitrate stages" framing above — a well-credited verify stage
  clearly recovers real value within the single-model plateau, just not
  enough (on this run) to change which architecture family closes the gap
  to the v08 hybrid (0.9155).
- If the Gan consensus/fresh path is revisited for tuning or redesign, start
  from validation-only component-generation work; the holdout aggregate results
  may be cited only as frozen evaluation evidence, not used for row-level
  debugging or tuning.
- Preserve Gan consensus/fresh v0.9 constrained Gate 4 and exact-source Gate 4 as
  frozen aggregate evidence; do not tune gates, prompts, artifacts, rules,
  normalization, scorer, or model choice from them.
- Keep Investigations cost work deferred until a separate predeclaration.
- Build a test-safe UMLS-backed concept normalizer to replace the in-sample
  gold-derived stub in `deterministic/concept_normalizer.py` (acquire a real
  UMLS/MRCONSO resource for the `UmlsConceptNormalizer` placeholder).
  Deprioritized: the 2026-06-28 single-model plateau synthesis
  (`docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`)
  found CUI is not the lever for this benchmark's surface-granularity convention.

### Blocked

- Gan holdout-facing reruns, test row analysis, and post-test tuning remain blocked
  unless separately authorized under a fresh frozen protocol.
- ExECTv2 full-200/holdout row-level inspection remains blocked; current protocols
  authorize aggregate validation outputs only.
- Lower-burden review-routing promotion is blocked by failed aggregate
  validation; any retry needs dev140-only redesign and a fresh predeclaration.

### Done Recently

- 2026-07-02: **Pipeline assumption audit, ALL phases (0–4) complete** (see Now
  for the full entry). Phase 0 four parallel read-only audits confirmed the shared
  PRF1 math is correct but the seed defect class is systemic. Phase 1 landed all
  four scorer-correctness fixes under gating (Prescription clause-scope +0.0307,
  SF zero-count +0.0061, Investigations latent, and — completed in this pass —
  Diagnosis D1 hierarchy match `concept_only` 0.6617→0.6779). Phase 2 (costed,
  user go-ahead) ran two gpt-4.1-mini extraction probes, both CONFIRMED. Phase 3
  added drug-lexicon valproate/brand unification (Rx →0.9122), a headline-neutral
  P4 note-window fix, and a gold-data-issue log. Phase 4 built the anti-recurrence
  guardrail (scope-invariant + scorer↔projection property tests, an
  edit-triggers-predeclaration gate, the mechanism-taxonomy lens) and the "all
  cited runs" re-score sweep (13 dev140 + 1 full-200 aggregate), regenerating the
  registry `primary_metrics` + disclosure, all four dossiers, and the frontend
  scorecard. Canonical overall `clinical_headline` 0.7313→0.7416→0.7491. Executed
  with five parallel sub-agents; every audit hypothesis now carries a final
  verdict. Parked-with-rationale: P6, SF-2, F2, P7, SF-5.
- 2026-07-02: Built the gold case ledger (`experiments/exectv2_ledger/`) — one
  shared mechanism taxonomy + schema replacing four independently-reimplemented
  "is this gold or model" scripts, plus a hypothesis registry
  (`experiments/hypothesis_registry.jsonl`) tracking predeclaration -> verdict
  lifecycle. Backfilled Diagnosis/SF from their existing adjudications (zero
  new cost) and, for the first time, row-adjudicated Prescription and
  Investigations at the actual scored `clinical_headline` layer (previously
  only a narrower `source_near` evidence-recall diagnostic existed for either).
  Answers "why isn't medication F1 at 90%": **Prescription's disagreements are
  60.4% genuine model error** (polypharmacy drug omissions, current-vs-future
  dose conflation, non-AED over-extraction) — the opposite finding from
  Diagnosis (14.8% genuine) and SeizureFrequency (28.8% genuine), where gold-quality
  artifacts dominate. Also surfaced a genuine, previously-undocumented scorer
  bug: the `_is_future_medication`/weight-based-dosing regex in
  `scoring/prescription.py` matches anywhere in a gold annotation's full span
  text, so gold spans that bundle a current dose with titration language get
  wrongly excluded from `clinical_headline` scoring even when the model's
  current-dose prediction is correct (11/48 = 22.9% of Prescription's
  disagreements). Investigations: 67.7% genuine, concentrated in the
  already-known MRI-crowds-out-EEG omission pattern. *(Shares are on the
  pre-07-02-clause-scope 48/31 case sets; see the 2026-07-03 re-finalization
  below for the corrected 36/35 shares under the finalized scorer: Rx 72.2%,
  Inv 65.7%.)* Generated dossiers:
  `docs/canon/workstreams/{DIAGNOSIS,SEIZURE_FREQUENCY,PRESCRIPTION,INVESTIGATIONS}_CANONICAL_LEDGER_CANON.md`
  (regenerate via `uv run python experiments/exectv2_ledger/render_dossier.py`,
  never hand-edit).
- 2026-07-01: Documentation consolidation Path A — added `docs/NAVIGATION.md`,
  `docs/runbooks/documentation_lifecycle.md`, CI doc-hygiene gate; relocated
  evidence-recall case files from root `_sf_ev_recall/` and `_rx_inv_ev_recall/`
  to `docs/research/error_analysis/`; renumbered ADR 0005 JSON-dialect collision
  to `0038`; archived June "Done Recently" entries to
  `docs/research/maintenance/project_status_digest_2026-06.md`.
- 2026-06-30: Applied `docs/research/predecessor_lessons/` to the current evidence
  base. Registry hygiene (247 artifact paths repaired); Diagnosis canonical
  row-adjudication (the GEPA plateau synthesis's self-reopened question,
  answered — 85.2% of Diagnosis disagreements are gold-quality artifacts, not
  genuine model error, mirroring and exceeding the SF finding); evidence
  support-quality companion audit (closes FM1's "Partial" guardrail); DeepSeek
  precision prompt profile probe (A5, small mechanistically-clean positive);
  manuscript revised (§4.1.2, D.2, §6) to give Diagnosis the same
  gold-quality-ceiling treatment SF got on 06-29; predecessor-lessons
  absorption tables refreshed.
- 2026-06-30: ExECTv2 GEPA Qwen 3.6 35B cross-model close-out (bounded
  negative) + registry registration fix (12 malformed records flattened).
- 2026-06-29: ExECTv2 SF Phases 5-7 — feedback+demos LLM-only SF best (0.784,
  gate not cleared); changed-class row adjudication revises Phase 4's "not
  learnable" call; canonical whole-corpus metric row-analysis concludes the SF
  "wall" is a gold-quality ceiling, not a model ceiling (only 15/53 dev140
  metric-errors are genuine model mistakes).
- Earlier June entries: see
  `docs/research/maintenance/project_status_digest_2026-06.md`.

## Guardrails

- Do not describe de-duplicated `clinical_headline` recovery as a strict
  benchmark win or compare it directly to the paper's strict target.
- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development;
  the current reliability-audit protocol authorizes aggregate validation only.
- Keep deterministic projection, hybrid rescue, and verifier rejection
  provenance-stamped and separated in reported score lines.
