# Project status

Last updated: 2026-07-15

## Current outcome

The cleanup, verification, and Gan efficiency phases are complete. The
repository has three deliverables: the Python package, selected
machine-readable evidence, and the paper. The Gan result supports a saved
quality-versus-model-pass comparison, not measured token, cost, or latency
efficiency. The ExECT published-metric development phase is also complete. The
ExECT Diagnosis review and development implementation are complete. A full200
component audit found that the recorded three-model Prescription lane is
deterministic-only and the Seizure Frequency lane unions model output with an
independent deterministic extractor. Corrected model-led aggregate candidates
exist, but their configurations have not been retained or promoted.
[Decision 0040](docs/decisions/0040-final-exect-llm-with-rules-family-ownership.md)
now owns the final family architecture. The next executable work is to
materialize that architecture correction, followed by out-of-sample confidence
and selective-action testing.

[Paper claim status](docs/canon/10_paper_provenance.md) records what the paper
may say. [The active roadmap](docs/plans/ACTIVE_ROADMAP.md) gives the work order.

The final ExECT comparison roster is fixed by
[decision 0039](docs/decisions/0039-final-exect-six-model-roster.md):
GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, hosted DeepSeek V4 Flash, local Qwen
3.6:35B, and local Gemma 4 26B. This is three closed-weight and three
open-weight conditions; two open-weight conditions are local. DeepSeek V4
Flash uses the `deepseek/deepseek-chat` API identifier, but the final reported
condition must have thinking enabled. The retained DeepSeek run does not record
that setting, so it does not yet count toward the final panel.

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
| ExECT dev140 | 0.3548 strict item F1 | 0.7393 clinical fact F1 | 0.9189 clinical fact F1 | Historical development results; the first score uses a stricter metric, and `v08` does not meet the final decision-0040 family ownership contract |
| Gan validation750 | 697/750 Purist | 581/750 Purist | 661/748 rendered Purist | Development and replay results |

Other paper evidence:

- The ExECT rules-only no-call dev140 replay reports paper-derived macro item F1
  of `0.5687` for normalized phrase, `0.7144` for CUI, and `0.6020` for all
  features across all nine entity types. These are development results, not a
  reproduction of the paper's original system or its `0.87`/`0.90` scores.
- Gan locked test450: the single-pass event extractor scored `364/450` Purist;
  the saved multi-model comparator scored `379/450`.
- The multi-model comparator gains 15 rows (3.33 percentage points) but needs
  three cold model passes per note rather than one. Its final audit replayed
  two upstream traces, so token, cost, latency, hardware, and cache claims
  remain unsupported rather than estimated.
- The recorded ExECT full200 rows report historical DeepSeek `0.8566`, GPT-4.1-mini
  `0.8356`, and Qwen 3.6:35B `0.8197` clinical fact F1, but they are not a
  consistent model comparison: Prescription is deterministic-only and Seizure
  Frequency includes a deterministic-extractor union. The DeepSeek thinking
  state was not recorded, so `0.8566` is not the final reportable DeepSeek V4
  Flash result.
- An aggregate-only saved-output audit of the intended model-led architecture
  reports historical DeepSeek `0.8543`, GPT-4.1-mini `0.8171`, and Qwen
  `0.8234`. Diagnosis is `0.8789` / `0.8583` / `0.8520`; Prescription is
  `0.9057` / `0.8700` / `0.9220`. These are unpromoted full200
  development-inclusive candidates, not independent holdout results. The
  DeepSeek candidate is audit-only because its thinking state was not recorded.
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
| ExECT published metrics | Added and tested paper-derived normalized-phrase, CUI, and full-attribute scoring; a no-call all-nine-entity dev140 replay reports macro item F1 `0.5687` / `0.7144` / `0.6020` and leaves the existing strict micro replay unchanged at `0.3548` |
| ExECT Diagnosis resolution | Completed all 246 dev140 review decisions: 173 representation issues, 72 extraction errors, and one uncertain row. Diagnostic sensitivity raises fixed F1 to `0.9344`/`0.8499`/`0.9789` for rules/LLM/hybrid under the conservative view. Shared deterministic fixes improve rules from `0.8599` to `0.8926` and hybrid from `0.8984` to `0.9034`; the fixed LLM prompt candidate regresses from `0.6861` to `0.6210` and is rejected. Gold and the fixed scorer are unchanged; test60 was not inspected. |
| ExECT LLM-with-rules ownership audit | Replayed saved full200 outputs without new calls or test60 failure inspection. Diagnosis is model-led with material deterministic rescue; Investigations is model-led; the recorded Prescription and Seizure Frequency paths fail the intended method definition. The corrected aggregate candidate uses each named model's facts plus attributable post-extraction corrections. Per-family recall is entity-agnostic, so family scores are final-output metrics rather than pure component scores. |

The current suite contains 1,194 tests. On 2026-07-14, all tests, Ruff, mypy,
the retained-evidence check, all six no-call reference replays, and a two-pass
IEEE build passed. All three PDF pages were rendered and visually checked. The
cleanup history is in the
[repository cleanup record](docs/research/maintenance/repository_surgery_assessment_2026-07-14.md).

## Open research and validation work

1. **Architecture correction:** implement
   [decision 0040](docs/decisions/0040-final-exect-llm-with-rules-family-ownership.md)
   in durable model-swap configurations that use each named model's
   Prescription output and pre-union Seizure Frequency output. Reproduce the
   aggregate audit, add Seizure Frequency `state_profile`, and pass attribution,
   regression, schema/evidence, and retained-evidence checks.
2. **Confidence:** evaluate model-reported confidence out of sample and keep a
   negative result if the values remain uninformative.
3. **Annotation evidence:** combine the cited defect, convention, ambiguity,
   multiplicity, scoring, handling, and sensitivity evidence. Claims of
   clinical validity still require independent clinical review.
4. **Six-model comparison:** run the decision-0039 roster through the same
   corrected model-led pipeline and scorer. Record exact hosted identifiers and
   local model revisions, quantization, hardware, endpoint, and adapter policy;
   require DeepSeek V4 Flash to use `deepseek/deepseek-chat` with thinking
   enabled and record how thinking was requested.

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
