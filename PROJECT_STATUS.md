# Project Status

Last updated: 2026-07-14

## Current outcome

The repository contains a defensible modular clinical-extraction contribution,
but the active tree is not yet a maintainable or fully reproducible expression
of it. Repository surgery is in progress before new model experiments.

The retained contribution must show:

- one shared, stage-owned architecture evaluated on Gan seizure frequency and
  ExECT broad phenotyping;
- deterministic, LLM-only, and hybrid reference configurations on both tasks;
- explicit evidence extraction, normalization, projection, schema validation,
  and evidence verification with component attribution;
- reproducible scoring, reliability, efficiency, and annotation-quality evidence;
- conservative split and claim boundaries.

The acceptance matrix and current claim strength live in
[`docs/canon/10_paper_provenance.md`](docs/canon/10_paper_provenance.md).
Execution order lives in
[`docs/plans/ACTIVE_ROADMAP.md`](docs/plans/ACTIVE_ROADMAP.md).

## Current evidence

### Task and split boundaries

- **Gan 2026:** `test450` is an author-uninspected locked holdout. Only frozen
  aggregate results may be cited; row-level test output is not a development
  surface.
- **ExECTv2:** `dev140` is the row-inspectable development surface. `full200`
  contains dev140 plus held-out test60 and is a development-inclusive aggregate
  audit, not an independent holdout. Test60 row-level development remains barred.
- **Primary scores:** Gan uses Purist/Pragmatic label accuracy. ExECT uses
  de-duplicated `clinical_headline` recovery across Diagnosis,
  SeizureFrequency, Prescription, and Investigations; strict phrase/CUI/full
  attribute-bundle scoring remains the paper-comparability surface.

### Retained architecture evidence

| Task | Deterministic | LLM-only | Hybrid / operational control | Current boundary |
| --- | --- | --- | --- | --- |
| Gan seizure frequency | Canonical deterministic comparator | Canonical single-call comparator | Single structured-event pass is operational; V12 multi-trace is a ceiling comparator | Six-cell validation reference replays from saved outputs; holdout aggregate remains frozen |
| ExECT broad phenotyping | Current all-9 deterministic reference | GEPA negative comparator | Holistic finding assembly v08 | All three dev140 cells replay from current code/saved outputs; not independent holdout evidence |

This table records the scientific cells that must survive. It does not authorize
retention of every historical candidate within a cell. Exact paths, hashes,
closures, and replay expectations live in
[`docs/experiments/retained_evidence_manifest.json`](docs/experiments/retained_evidence_manifest.json).

### Paper-facing results that currently survive

- Gan operational structured-event pass: `364/450` Purist on frozen `test450`;
  multi-trace V12 ceiling comparator: `379/450`. A matched cost/latency table is
  still missing.
- ExECT v08 current-code/P7 treatment: `0.9189` dev140 and `0.8680` full200
  `clinical_headline`. Full200 is aggregate-only and development-inclusive.
- ExECT same-core model swap currently covers GPT-4.1-mini, DeepSeek, and Qwen
  3.6:35b. The requested six-model panel has not been run.
- Component replay shows positive normalization and projection effects; evidence
  validation is score-inert on the representative Gan validation and ExECT
  dev140 replays. Schema/evidence gates therefore also require rejection and
  repair challenge tests, not only F1 deltas.
- The 2026-07-07 calibration redesign is an internal scoring-rule result:
  full200 aggregate Brier `0.2225` versus base rate `0.2340`, ECE `0.0587`.
  Model-reported confidence is not used, and no low-burden review policy is promoted.
- Gold-quality evidence exists in the four generated family ledgers and
  `experiments/gold_data_issues.jsonl`, but the cited defect, convention,
  scorer-artifact, and ambiguity evidence is not yet consolidated into one
  paper-facing ledger.

## Surgery state

Implemented in the current working tree:

- row-level Gan locked-test reports and connected generators have been removed;
- the separate frontend and Observatory products have been removed; the
  repository now targets the extraction package, evidence, and paper;
- ExECT full200 terminology has been corrected to development-inclusive audit;
- the run registry no longer points at the removed locked-row reports;
- the retained paper story has an exact two-task × three-family evidence matrix;
- every reference cell has a validated artifact hash, source/config/scorer/test
  closure, and passing no-call replay;
- broken report/catalog builders tied to missing historical artifacts have been
  removed with their scripts and tests.

Verification before the current deletion batch:

- all six reference cells replayed successfully;
- 35 focused manifest, replay, deterministic-reference, Ruff, and mypy checks passed;
- the full backend suite had 2,511 passed, 20 failed, and 2 skipped before the
  broken report/catalog and UI slices were removed;
- repository-wide Ruff and mypy were not green on the unreduced tree.

These checks are evidence for the first boundary-protection slice only. They do
not verify the full surgery.

## In progress

1. Re-run the backend suite after the UI/report deletion batch and remove any
   orphaned imports or stale quality-gate entries.
2. Remove closed candidates as complete vertical slices before repairing broad
   static-quality debt.
3. Reduce the document and artifact estate to canonical owners plus retained proof.
4. Recount repository-wide Ruff/mypy debt on the smaller tree and close it.

## Open research and validation work

- **Gan efficiency:** add a matched quality/call/token/cost/latency comparison
  for the operational pass and multi-trace ceiling.
- **ExECT benchmark reproduction:** implement deterministic normalized-phrase,
  CUI, and full attribute-bundle engineering and evaluate it on the
  paper-comparable surface.
- **Broad confidence calibration:** evaluate model-reported confidence out of
  sample; preserve a negative result if confidence remains degenerate.
- **Annotation evidence:** consolidate every cited under-annotation,
  multiplicity, ambiguity, concrete defect, and scorer artifact with its
  handling and sensitivity effect. Unqualified clinical-validity language still
  requires independent domain review.
- **Six-model comparison:** after the reduced architecture is frozen, run the
  same prompt/program/scorer with the six exact runtime models and conclude from
  the result rather than assuming a size/reasoning ordering.

## Blocked boundaries

- Gan holdout-facing reruns, row analysis, and post-test tuning require a fresh
  frozen protocol and explicit authorization.
- ExECT test60 row inspection is not permitted for development. Full200 work is
  aggregate-only.
- No benchmark-reproduction, calibrated-confidence, six-model, or external
  gold-validity claim is complete until its named evidence exists.

## Next

1. Generate the current registry/path/hash audit and propose the retained manifest.
2. Trace the two operational controls and six reference cells through source,
   configuration, artifacts, reports, and tests.
3. Delete or repair the first complete broken ExECT report/catalog feature.
4. Re-run the full backend suite and recount Ruff/mypy on the smaller tree.
5. Continue vertical deletion until no closed candidate remains installed.
6. Complete the four research follow-ups on the frozen reduced architecture.
7. Verify a fresh checkout can install, replay both tasks, rebuild every
   surviving paper table, verify hashes, and enforce split barriers.

## Guardrails

- Never inspect Gan `test450` or ExECT test60 row-level failures for development.
- Never describe ExECT full200 as an independent holdout.
- Never describe `clinical_headline` as a reproduction of the strict published benchmark.
- Keep raw model output, format repair, deterministic semantic repair,
  projection, verification, and scoring separately attributable.
- Delete source, configs, prompts, artifacts, registries, UI adapters, documents,
  and tests together for a closed candidate.
- Do not move bulk history into another tracked archive or add compatibility
  shims for removed internal paths.
- Use *implemented*, *verified*, *validated*, and *promoted* precisely.
