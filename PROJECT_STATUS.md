# Project Status

Last updated: 2026-07-14

## Current outcome

The repository contains a defensible modular clinical-extraction contribution.
The classified closed Gan and ExECT source candidates are now removed, but the
document, artifact, quality-gate, and fresh-checkout phases of repository
surgery remain open before new model experiments.

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

Earlier surgery batches are on `main`. The CI reduction and retained ExECT
replay-closure repair are implemented and verified in the current working tree:

| Area | Current result |
| --- | --- |
| Evidence boundaries | Removed row-level Gan locked-test reports and generators; corrected ExECT full200 to development-inclusive audit; retained split barriers and aggregate-only claim rules |
| Retained evidence | Rebuilt the two-task × three-family manifest with present paths, hashes, closure, and six passing no-call replays; restored and selected the four hybrid producer outputs accidentally removed by the broad artifact prune |
| Product scope | Removed the frontend and Observatory; the repository now targets the Python extraction package, retained evidence, and paper |
| Broken support machinery | Removed report/catalog builders tied to absent artifacts, the line-count allowlist, one-shot migration tools, orphaned supervisor runtime, and stale six-job CI; CI is now one install plus full-pytest job |
| Closed ExECT candidates | Removed generation-selection, all four verifier families, closed GEPA variants and launchers, completed SF diagnostic drivers, one-shot analysis tools, and superseded model-swap configs outside the retained closures |
| Closed Gan candidates | Removed the entire closed agentic runtime and candidate tests; retained only the saved aggregate V12 ceiling evidence named by the evidence manifest |
| Retained helper cleanup | Moved the few still-used helper functions out of deleted candidate packages and into their actual retained owners |

Verification on the current deletion batch:

- `python -m pytest -q`: 1,145 passed in the repository environment;
- `python -m mypy src`: clean across 270 source files;
- retained manifest and hashes pass; all six no-call reference cells replay at
  their recorded metrics;
- `git diff --check`: clean;
- registry audit: all path-bearing fields resolve across 15 rows;
- repository-wide Ruff still fails with 120 `E501` and two `I001` findings.

These checks verify the current reduced working tree. The simplified workflow
has not run on GitHub yet, and these checks do not complete the fresh-checkout
reproducibility closeout.

## Findings and pitfalls

- **Dependency closure decides deletion.** A rejected registry decision or a
  candidate-like filename is not enough. Retained modules imported private
  helpers from closed verifier and Gan candidates. Those helpers had to move
  before their former owners could be deleted.
- **Replay inputs are retained evidence.** The broad artifact prune deleted four
  producer outputs named by the selected ExECT hybrid config. The manifest now
  records their paths, hashes, and sizes, and a test compares the config inputs
  with the selected artifact set.
- **CI job lists rot with deleted scope.** The failing workflow still built the
  removed frontend and named deleted gates and candidate tests. One full-suite
  job is the temporary surgery contract; lint and typing remain local gates
  until the reduced tree is ready to add them back.
- **Saved replay and executable research are different needs.** The six
  reference cells can replay without model calls, but the planned ExECT
  six-model comparison still needs the structured extractor, Diagnosis
  decomposer, and SF union runtime. Do not delete those modules merely because
  the retained v08 score replays from saved lane artifacts.
- **Historical text is not always a live dependency.** Producer labels and
  `supersedes` fields may accurately describe how a retained artifact was made.
  Preserve truthful provenance strings while removing executable imports,
  broken paths, and registry records for closed candidates.
- **Registries are evidence leads, not authorities.** Initial inspection found
  records that named absent archive files and builders whose defaults pointed
  to missing artifacts. Validate every path before treating a registry row as
  retained evidence.
- **Prompt removal can affect unrelated paths.** Generic prompt and runner
  packages were shared by retained code. Every prompt-bearing deletion must run
  retained prompt snapshots as well as focused tests.
- **Test counts fall during valid deletion.** The suite decreased because tests
  for removed behavior were deleted. Completion evidence is the passing full
  suite plus retained manifest/replay checks, not preservation of the old test
  count.
- **Large artifacts remain unresolved.** Hashing retained files makes the
  evidence graph trustworthy, but it does not solve the repository-size
  problem. Immutable external storage with retrieval instructions is still
  required before broad artifact deletion.

## In progress

1. Reduce the document and artifact estate to canonical owners plus retained proof.
2. Close the 122 remaining Ruff findings on the reduced tree.
3. Run the fresh-checkout install, replay, hash, path, and split-barrier closeout.

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

1. Reduce documents, registries, and artifacts to canonical owners and retained
   proof, after the external retained-artifact location is defined.
2. Make repository-wide Ruff green, simplify oversized retained tests, and run
   the full suite without allowlists.
3. Complete the paper evidence studies on the frozen reduced architecture,
   then perform the fresh-checkout closeout.

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
