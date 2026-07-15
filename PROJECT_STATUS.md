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
exist. Their decision-0040 configurations and no-call replay are now retained
and verified; the replay adds `state_profile`, exact-evidence, schema/parse,
fact-origin, and deterministic-regression accounting.
[Decision 0040](docs/decisions/0040-final-exect-llm-with-rules-family-ownership.md)
owns the final family architecture. Nonzero deterministic correct-to-wrong
counts keep the historical rows unpromoted. A frozen no-call test60 replay now
shows that model-reported confidence is not informative enough to route review
for any of the three historical model outputs. The permitted dev140 mechanism
analysis now retains Seizure Frequency and Investigations but finds that
Diagnosis and Prescription need bounded policy candidates. A bundled
model-preserving candidate and a Prescription-only rescue-scope candidate were
both rejected under predeclared row-retention gates. Prescription residual
additions cannot be disabled unconditionally because four exact-evidence rows
depend on deterministic missing-regimen recovery. The next work separates safe
Prescription selection guards from residual rule groups and evaluates the
Diagnosis guards independently, before the fixed six-model comparison. The
annotation evidence is now consolidated into a generated taxonomy with
explicit score, handling, sensitivity, review, and clinical-validity limits.

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
- The durable replay reproduces those aggregates exactly. SF `state_profile`
  F1 is `0.7813` / `0.8085` / `0.7812` for GPT-4.1-mini, historical DeepSeek,
  and Qwen. Minimum exact-evidence rate is `1.0`; the replay retains one
  DeepSeek parse/schema failure. Deterministic corrections still produce
  correct-to-wrong rows, so these are architecture evidence rather than
  promoted final model conditions.
- Normalizing saved outputs improved ExECT dev140 by `0.0389` and Gan
  validation750 by `0.0293`. The exact-evidence check did not change these
  replay scores; rejection and repair tests provide its separate evidence.
- ExECT full200 internal calibration: Brier `0.2225`, base-rate Brier `0.2340`,
  ECE `0.0587`. No review policy has been adopted from this result.
- ExECT aggregate-only test60 model-reported-confidence failure AUROC is
  `0.5503` for historical DeepSeek, `0.5394` for GPT-4.1-mini, and `0.4895`
  for Qwen. Neither predeclared review rule met the frozen catch-rate and
  burden requirements, so no confidence-based review policy was adopted.
- The dev140 deterministic-regression analysis records 319 changed model/family
  rows with exact evidence. The family-local view has 160 wrong-to-correct, 41
  correct-to-wrong, and 118 changed-still-wrong outcomes. Seizure Frequency has
  38 rescues and no local regression; Diagnosis has 18 regressions and
  Prescription has 23.
- The [annotation-evidence synthesis](docs/experiments/exectv2/reliability/exectv2_annotation_evidence_synthesis_2026-07-15.md)
  hash-checks 13 retained sources and combines
  584 overlapping evidence records. It maps all 57 explicitly cited letters,
  separates three open and one fixed mechanical gold issue from conventions,
  ambiguity, multiplicity, scorer effects, and model-error controls, and leaves
  ten historical Diagnosis concept rows aggregate-only. This is internal
  development evidence; independent clinical review remains required for
  clinical-validity claims.

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
| ExECT architecture correction | Added decision-0040 model-led configs, made the runner reject deterministic Prescription substitution and SF extractor union, and added a no-call Git-blob replay. It exactly reproduces the three corrected aggregates plus `state_profile`, attribution, exact-evidence, schema/parse, and deterministic-regression counts. Implemented and verified; the historical model rows are not promoted. |
| ExECT model-reported confidence | Froze the analysis before replay, separated dev140 from aggregate-only test60, and evaluated the historical GPT-4.1-mini, DeepSeek, and Qwen source labels against final family-cell correctness. Test60 AUROC was `0.5394` / `0.5503` / `0.4895`; neither fixed routing rule passed. This is a retained negative result, not deployment calibration. |
| ExECT dev140 deterministic regressions | Filtered historical producer blobs to the declared 140 development IDs before assembly and retained 319 changed-row mechanism records. SF projection/suppression has 38 local rescues and zero regressions; current Diagnosis and Prescription policies remain unpromoted. No model call or test60 inspection occurred. |
| ExECT model-preserving policy candidates | Replayed two predeclared opt-in candidates on saved dev140 outputs. The bundled candidate reduced correct-to-wrong rows from 41 to 9 but lost 17 of 160 comparator rescues and was rejected. The Prescription rescue-scope candidate fixed local frequency scope and retained 37 of 41 Prescription rescues, but made four comparator-correct rows wrong when all residual additions were removed, so it was also rejected. All comparator-candidate changes had exact evidence; no model call or test60 inspection occurred. |
| ExECT annotation evidence | Generated a 584-record taxonomy from 13 hash-checked retained sources, mapped all 57 explicitly cited letters, linked issue class to original scoring, handling, sensitivity, and review status, and retained the independent-clinical-review boundary. Ten historical Diagnosis concept rows remain aggregate-only rather than reconstructed. |

The current suite contains 1,227 tests. On 2026-07-15, all tests, Ruff, mypy,
the retained-evidence check, all six no-call reference replays, and a two-pass
IEEE build passed. All three PDF pages were rendered and visually checked. The
cleanup history is in the
[repository cleanup record](docs/research/maintenance/repository_surgery_assessment_2026-07-14.md).

## Open research and validation work

1. **Bounded deterministic policy separation:** retain the demonstrated
   Prescription missing-regimen rescues, isolate harmful residual rule groups,
   and evaluate local rescue scope plus current-versus-future selection without
   changing candidate generation. Evaluate Diagnosis subsumption and
   absence-phenotype preservation as a separate candidate with rescue-identity
   accounting.
2. **Six-model comparison:** run the decision-0039 roster through the same
   corrected model-led pipeline and scorer. Record exact hosted identifiers and
   local model revisions, quantization, hardware, endpoint, and adapter policy;
   require DeepSeek V4 Flash to use `deepseek/deepseek-v4-flash` i.e. with thinking
   enabled.

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
