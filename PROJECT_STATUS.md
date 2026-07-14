# Project Status

Last updated: 2026-07-14

## Current outcome

The four cleanup phases are complete:

1. the document and artifact estate was reduced to the retained system;
2. engineering quality gates were restored around retained behavior;
3. the reduced reference architecture was frozen; and
4. a separate clean checkout reproduced the retained evidence, after which the
   Markdown manuscript and IEEE paper were synchronized to that evidence.

The repository now targets three deliverables: the Python extraction package,
the machine-readable retained evidence, and the paper. New work is research and
validation on the frozen architecture, not further repository surgery.

The paper acceptance matrix and claim strength live in
[`docs/canon/10_paper_provenance.md`](docs/canon/10_paper_provenance.md).
Execution order lives in
[`docs/plans/ACTIVE_ROADMAP.md`](docs/plans/ACTIVE_ROADMAP.md).

## Evidence boundaries

- **Gan 2026:** `test450` is an author-uninspected locked holdout. Only frozen
  aggregate results may be cited; row-level test output is not a development
  surface.
- **ExECTv2:** `dev140` is row-inspectable development data. `full200` combines
  dev140 with held-out test60 and is a development-inclusive aggregate audit,
  not an independent holdout. Test60 row-level development remains barred.
- **Scoring:** Gan uses Purist/Pragmatic label accuracy. ExECT's retained
  research-control surface is de-duplicated `clinical_headline` recovery.
  Phrase, CUI, evidence-valid, and full-attribute companions remain separate;
  `clinical_headline` is not the strict published ExECT benchmark.

## Retained results

| Task | Rules only | LLM only | Hybrid | Boundary |
| --- | ---: | ---: | ---: | --- |
| ExECT dev140 | 0.3548 strict item F1 | 0.7393 headline F1 | 0.9189 headline F1 | Development references; scores do not share one strict benchmark surface |
| Gan validation750 | 697/750 Purist | 581/750 Purist | 661/748 rendered Purist | Development and replay references |

Additional paper-facing evidence:

- Gan locked `test450`: operational single-pass structured-event system
  `364/450` Purist; V12 multi-trace ceiling `379/450`.
- ExECT full200 same-core aggregate: DeepSeek `0.8566`, GPT-4.1-mini `0.8356`,
  and Qwen 3.6:35B `0.8197` headline F1. The three retained conditions are
  asymmetric, so this is bounded portability evidence, not the requested
  strict six-model comparison.
- Saved-output normalization contribution: `+0.0389` ExECT dev140 and
  `+0.0293` Gan validation750. Evidence validation is score-inert on these
  selected replays; rejection and repair tests carry its separate evidence.
- ExECT full200 internal calibration: Brier `0.2225`, base-rate Brier `0.2340`,
  ECE `0.0587`. No low-burden review policy is promoted.

Exact paths, hashes, policy fingerprints, closures, and replay expectations
live in
[`docs/experiments/retained_evidence_manifest.json`](docs/experiments/retained_evidence_manifest.json).

## Cleanup closeout

| Phase | Completed result |
| --- | --- |
| Document and artifact reduction | Removed historical tool state, stale notebooks, closed reports and candidates, the frontend and Observatory; selected immutable replay artifacts use Git LFS |
| Engineering cleanup | Repository-wide Ruff and mypy are clean; seven oversized tests were split by invariant; CI enforces Ruff, mypy, and full pytest |
| Architecture freeze | Manifest v3 pins the reduced graph, all six reference cells, Python/dependency policy, and exact prompt, scorer, split, repair, model, runbook, and CI fingerprints |
| Fresh-checkout and paper closeout | Clean Python 3.11 install, hashes, split barriers, six no-call replays, full quality gates, synchronized paper sources, and a visually checked three-page IEEE PDF |

Fresh-checkout verification used a separate clone with Git LFS objects
retrieved and Python 3.11 explicitly selected. The first unconstrained `uv sync`
selected Python 3.12; the documented install now pins Python 3.11 before any
result is interpreted. The final retained suite contains 1,157 tests.

The surgery rationale and lessons remain as a historical record in
[`docs/research/maintenance/repository_surgery_assessment_2026-07-14.md`](docs/research/maintenance/repository_surgery_assessment_2026-07-14.md).

## Open research and validation work

1. **Gan efficiency:** add a matched quality/call/token/cost/latency comparison
   for the operational pass and multi-trace ceiling.
2. **ExECT benchmark reproduction:** implement deterministic normalized-phrase,
   CUI, and full attribute-bundle engineering on the paper-comparable surface.
3. **Confidence:** evaluate model-reported confidence out of sample and retain a
   negative result if confidence remains degenerate.
4. **Annotation evidence:** consolidate cited defect, convention, ambiguity,
   multiplicity, scorer-artifact, handling, and sensitivity evidence. External
   clinical-validity language still requires independent domain review.
5. **Six-model comparison:** predeclare the three missing exact runtime
   conditions, then run the frozen component graph and scorer.

## Guardrails

- Never inspect Gan `test450` or ExECT test60 row-level failures for development.
- Never describe ExECT full200 as an independent holdout.
- Never describe `clinical_headline` as reproduction of the strict published benchmark.
- Keep raw model output, format repair, semantic repair, projection,
  verification, and scoring separately attributable.
- A frozen architecture does not authorize a model call; live work still needs
  a predeclared question, runtime condition, and permitted split.
- Use *implemented*, *verified*, *validated*, and *promoted* precisely.
