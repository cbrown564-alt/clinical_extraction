# Project status

Last updated: 2026-07-14

## Current outcome

The cleanup, verification, and Gan efficiency phases are complete. The
repository has three deliverables: the Python package, selected
machine-readable evidence, and the paper. The Gan result supports a saved
quality-versus-model-pass comparison, not measured token, cost, or latency
efficiency. The next executable phase is ExECT published-metric reproduction.

[Paper claim status](docs/canon/10_paper_provenance.md) records what the paper
may say. [The active roadmap](docs/plans/ACTIVE_ROADMAP.md) gives the work order.

## Data and scoring limits

- **Gan 2026:** `test450` is a locked holdout whose rows have not been inspected
  by the authors. Only the saved aggregate results may be cited or reviewed.
- **ExECTv2:** `dev140` permits row review. `full200` combines dev140 with the
  held-out test60 rows, so it is not an independent holdout. Test60 rows must
  not be inspected during development.
- **Scoring:** Gan uses Purist and Pragmatic label accuracy. ExECT's primary
  internal score is de-duplicated clinical fact recovery (`clinical_headline`).
  Phrase, CUI, evidence-valid, and full-attribute scores remain separate. The
  internal score is not the published ExECT benchmark.

## Selected results

| Task | Rules only | LLM only | LLM with rules | Scope |
| --- | ---: | ---: | ---: | --- |
| ExECT dev140 | 0.3548 strict item F1 | 0.7393 clinical fact F1 | 0.9189 clinical fact F1 | Development results; the first score uses a stricter metric |
| Gan validation750 | 697/750 Purist | 581/750 Purist | 661/748 rendered Purist | Development and replay results |

Other paper evidence:

- Gan locked test450: the single-pass event extractor scored `364/450` Purist;
  the saved multi-model comparator scored `379/450`.
- The multi-model comparator gains 15 rows (3.33 percentage points) but needs
  three cold model passes per note rather than one. Its final audit replayed
  two upstream traces, so token, cost, latency, hardware, and cache claims
  remain unsupported rather than estimated.
- ExECT full200 using the same main pipeline: DeepSeek `0.8566`, GPT-4.1-mini
  `0.8356`, and Qwen 3.6:35B `0.8197` clinical fact F1. Runtime and prompt
  differences limit this to a three-model comparison, not the planned strict
  six-model study.
- Normalizing saved outputs improved ExECT dev140 by `0.0389` and Gan
  validation750 by `0.0293`. The exact-evidence check did not change these
  replay scores; rejection and repair tests provide its separate evidence.
- ExECT full200 internal calibration: Brier `0.2225`, base-rate Brier `0.2340`,
  ECE `0.0587`. No review policy has been adopted from this result.

Exact files, hashes, versions, and replay expectations are in the
[retained evidence index](docs/experiments/retained_evidence_manifest.json).

## Completed work

| Work | Verified result |
| --- | --- |
| Repository reduction | Removed stale documents, notebooks, reports, candidates, the frontend, and Observatory; large selected replay files use Git LFS |
| Engineering checks | Ruff and mypy pass; seven oversized tests were split by invariant; CI runs Ruff, mypy, and full pytest |
| Fixed reference pipeline | Retained evidence index v3 records the source commit, six reference runs, Python and dependency versions, prompts, scorers, splits, repairs, models, runbooks, and CI policy |
| Clean-checkout and paper check | A separate Python 3.11 checkout retrieved Git LFS files, checked hashes and split restrictions, replayed six runs, passed all checks, reproduced the tables, and produced a visually checked three-page IEEE PDF |
| Gan efficiency | Aggregate-only audit reproduced `364/450` versus `379/450`, one versus three cold model passes, the V12 cache asymmetry, and the absence of matched telemetry; it also corrected an earlier validation-to-test provenance transfer |

The current suite contains 1,159 tests. On 2026-07-14, all tests, Ruff, mypy,
the retained-evidence check, all six no-call reference replays, and a two-pass
IEEE build passed. All three PDF pages were rendered and visually checked. The
cleanup history is in the
[repository cleanup record](docs/research/maintenance/repository_surgery_assessment_2026-07-14.md).

## Open research and validation work

1. **ExECT benchmark reproduction:** implement normalized phrase, CUI, and full
   attribute-bundle scoring using the published metrics.
2. **Confidence:** evaluate model-reported confidence out of sample and keep a
   negative result if the values remain uninformative.
3. **Annotation evidence:** combine the cited defect, convention, ambiguity,
   multiplicity, scoring, handling, and sensitivity evidence. Claims of
   clinical validity still require independent clinical review.
4. **Six-model comparison:** specify the three missing runtime conditions, then
   run the same pipeline and scorer for all six models.

## Rules that protect the evidence

- Never inspect Gan test450 or ExECT test60 row-level failures during development.
- Never describe ExECT full200 as an independent holdout.
- Never describe `clinical_headline` as the published strict benchmark.
- Never translate the Gan one-versus-three model-pass comparison into measured
  token, dollar, energy, hardware, or latency efficiency.
- Keep raw model output, format repair, clinical repair, final formatting,
  evidence checking, and scoring separately attributable.
- A fixed pipeline does not authorize a model call. Live work still needs a
  stated question, runtime condition, and permitted data split.
- Use *implemented*, *verified*, *validated*, and *promoted* precisely.
