# 10 — Paper claims and supporting evidence

Last updated: 2026-08-01

This file states how strongly the paper may make each claim. The
[retained evidence index](../experiments/retained_evidence_manifest.md) records
the exact files and hashes. The [manuscript](../research/paper_manuscript_2026-06-26.md)
must not make a stronger claim than either source supports.

## Required paper statements

| ID | Statement | Current evidence | State |
| --- | --- | --- | --- |
| S1 | One modular package is evaluated on Gan and ExECT | Six selected runs replay from retained code and outputs | Partial |
| S2 | Rules-only, LLM-only, and LLM-with-rules methods have attributable results on both tasks | Gan has one selected run per method; ExECT's primary comparison is the Sol-matched four-family rules-only, raw LLM-only, and one-call hybrid surface defined by decision 0046; `v08` and GEPA remain historical/secondary controls | Bounded development answer |
| S3 | The Gan multi-model method adds modest quality with three model passes rather than one | Saved test quality, run metadata, and aggregate input availability | Bounded |
| S4 | Six exact models run on one fixed ExECT pipeline | All six completed matched dev140 and aggregate-only test60 conditions; the retained panel gives local Qwen and Gemma the same claim status as the four hosted models | Confirmed |
| S5 | Unknown-versus-rate overconfidence appears across models and tasks | Gan evidence exists; the predeclared six-model ExECT dev140 analogue has zero unknown-only gold letters, so transfer is not measurable from current gold | Unsupported |
| S6 | Extraction, normalization, final formatting, schema, and evidence steps are explicit and tested | Step-specific tests, cross-task replay, and a 9,000-row Gan saved-output audit separate format/schema recovery, selected-answer identity, deterministic semantic changes, evidence, and scoring | Bounded development answer |
| S7 | ExECT reports paper-derived normalized-phrase, CUI, and full-attribute metrics | No-call rules-only dev140 replay covers all nine entities; original 0.87/0.90 scores are not reproduced | Development answer |
| S8 | Both tasks are assessed with the same eight reliability questions and task-specific measures with stated limits | Generated machine and human scorecards cover all 16 task-by-criterion cells; Gan and ExECT retained packages supply the named results and explicit gaps | Confirmed for framework coverage; evidence strength remains criterion-specific |
| S9 | Annotation defects, conventions, ambiguity, multiplicity, scoring effects, handling, and sensitivity have transparent provenance | Generated 584-record taxonomy hash-checks 13 retained sources and maps all 57 explicitly cited letters; ten historical Diagnosis concept rows remain aggregate-only | Bounded |

## Current claims

| ID | Claim | Strength | Evidence limit |
| --- | --- | --- | --- |
| C1 | Some ExECT Diagnosis and Seizure Frequency disagreements concern annotation multiplicity, representation, convention, or ambiguity | Bounded internal evidence | Completed 246-row Diagnosis review plus historical 53-letter Seizure Frequency review; mixed manual, pattern-assisted, and internal LLM-review provenance; not independently clinically validated and not a prevalence estimate |
| C2 | Normalization improves both tasks; the exact-evidence check is score-neutral on selected replays | Strong for the named replays | Development data only |
| C3 | Gan unknown-versus-rate behavior transfers to ExECT | Unsupported | Do not claim |
| C4 | The historical ExECT component graph ran with GPT-4.1-mini, DeepSeek, and Qwen | Strong for execution of that graph, not for a consistent model-led comparison | Full200 development-inclusive aggregate; Prescription was deterministic-only and SF included an independent extractor union |
| C5 | Split and evaluation rules are enforced | Strong for selected paths | Engineering verification, not external validation |
| C6 | Gan V12 gains 15/450 Purist-correct rows while requiring a three-pass cold architecture rather than one pass | Strong for saved quality and architecture structure | Tokens, cost, latency, and hardware were not measured in a matched run |
| C7 | The ExECT rules-only system scores 0.5687 phrase, 0.7144 CUI, and 0.6020 all-features macro item F1 | Strong for the named no-call dev140 replay | Paper-derived metric implementation on development data; not reproduction of the original system or reported scores |
| C8 | The recorded ExECT model rows do not implement one consistent model-led method across all four families | Strong for the saved-output ownership audit and verified corrected architecture replay | Full200 aggregate-only evidence; corrected scores remain unpromoted because deterministic correct-to-wrong counts are nonzero |
| C9 | Model-reported confidence does not support either predeclared review rule for the three saved ExECT model outputs | Aggregate out-of-sample negative evidence | Test60 aggregate only; historical outputs with incomplete runtime metadata, and no deployment or six-model claim |
| C10 | On the fixed six-model ExECT test60 panel, Sol scored 0.8047, Luna 0.7950, DeepSeek 0.7881, Qwen 0.7872, GPT-4.1-mini 0.7572, and Gemma 0.7169 clinical-headline F1 | Aggregate test evidence | Internal scorer, 59 loadable test letters, no row inspection; not the published benchmark or clinical validation; hosted and local runtime routes differ |
| C11 | On the selected matched Gan v0.5 test450 panel under the prior `hybrid_full_stack`, Sol scored 373/450, Luna and Qwen 362/450, GPT-4.1-mini 361/450, Gemma 355/450, and DeepSeek 344/450 Purist | Frozen aggregate evidence | Same v0.5 prompt and scorers; historical repair before the 2026-07-31 final ruleset; provider transport and temperature differ; some conditions use aggregate-only current-schema replay of sealed outputs |
| C12 | The fixed deterministic ExECT SF projection/suppression stage improves dev140 state-profile F1 for all six model conditions, with 54 wrong-to-correct and one correct-to-wrong transition across the six panels | Development component evidence | The same 140 letters are repeated for each model; the unknown-only denominator is zero, so this does not establish cross-task over-inference transfer or factuality prevalence |
| C13 | Gan 2026 and ExECTv2 are assessed with the same eight reliability questions using task-specific measures, explicit evidence states, and explicit comparability labels | Strong for the generated framework and selected retained evidence | The tasks do not share one metric; criterion evidence is uneven; construct-only and not-comparable values are not compared numerically; no composite score or clinical-validity claim |
| C14 | The historical v0.7 Gan dev750 panel shows a model-by-method interaction and supports component diagnostics, but it is not the selected primary six-model `llm_with_rules` result | Quarantined development diagnostic from twelve retained 750-row traces and a no-call replay | The selected v0.5 six-model dev750 panel is now complete; do not merge v0.7 rows or scores into its ranking, development-to-test comparison, or paper headline |
| C15 | On the selected matched Gan v0.5 dev750 panel under the prior `hybrid_full_stack`, GPT-4.1-mini scored 668/750, Qwen 660/750, Sol 656/750, Luna 646/750, Gemma 643/750, and DeepSeek 619/750 Purist | Reproduced development evidence from 4,500 unique row traces and a companion attribution artifact | Named models, routes, v0.5 prompt, historical repair, Gan scorers, and `gan2026_split_v1` validation rows only; not clinical validation, a model-neutral ranking, method promotion, or new holdout evidence |
| C16 | The Gan LLM-with-rules ruleset is finalized as of 2026-07-31 as working-tree `hybrid_full_stack` with projection/anti-regression, dated-count, competing-rate floors, and narrow cross-model guards; no-call replay of the same saved raws yields `dev750` Purist mini 677, Luna/Sol 660, Qwen 657, Gemma 647, DeepSeek 627, and `test450` Purist Sol 381, mini 369, Luna 364, Qwen 360, Gemma 356, DeepSeek 348 | Development / aggregate-only final-ruleset replay | Same saved model outputs as the matched panel; not a fresh held-out call campaign; local Qwen/Gemma routes retained; not clinical validation or model-neutral ranking |
| C17 | The primary ExECT three-method comparison is Sol-matched across four families: rules-only, Sol LLM-only from `raw_lane_score`, and Sol one-call LLM-with-rules from final `clinical_headline` | Strong for the named dev140 and aggregate-only test60 comparison surface | Decision 0046 and its A→B→C protocol; rules-only test60 is aggregate-only, the surface is not the published ExECT benchmark, and it is not clinical validation |

## Selected headline results

| Task and method | Result |
| --- | ---: |
| Gan single-pass system, test450 | 364/450 Purist |
| Gan multi-model comparison, test450 | 379/450 Purist |
| ExECT rules only, dev140 | paper-derived macro item F1: phrase 0.5687, CUI 0.7144, all features 0.6020; strict micro item F1 0.3548 |
| ExECT primary rules-only, four-family Sol-matched, dev140 | clinical_headline F1 0.8160 |
| ExECT primary LLM-only, Sol `raw_lane_score`, dev140 | F1 0.8097 |
| ExECT primary LLM-with-rules, Sol one-call hybrid, dev140 | clinical_headline F1 0.8920 |
| ExECT GEPA LLM only, dev140 | clinical fact F1 0.7393; historical/negative comparator |
| ExECT historical LLM with rules (`v08`), dev140 | clinical fact F1 0.9189; secondary development control, not the final decision-0040/0041 architecture |
| ExECT GPT / Qwen historical full200 rows | 0.8356 / 0.8197 clinical fact F1 |
| ExECT fixed six-model panel, test60 | GPT-4.1-mini 0.7572; Luna 0.7950; Sol 0.8047; DeepSeek 0.7881; Qwen 0.7872; Gemma 0.7169 clinical-headline F1 |
| Gan matched six-model v0.5 panel, dev750 (prior repair) | GPT-4.1-mini 668/750; Luna 646/750; Sol 656/750; DeepSeek 619/750; Qwen 660/750; Gemma 643/750 Purist |
| Gan matched six-model v0.5 panel, test450 (prior repair) | GPT-4.1-mini 361/450; Luna 362/450; Sol 373/450; DeepSeek 344/450; Qwen 362/450; Gemma 355/450 Purist |
| Gan final LLM-with-rules no-call replay, dev750 | GPT-4.1-mini 677/750; Luna 660/750; Sol 660/750; Qwen 657/750; Gemma 647/750; DeepSeek 627/750 Purist |
| Gan final LLM-with-rules no-call replay, test450 | Sol 381/450; GPT-4.1-mini 369/450; Luna 364/450; Qwen 360/450; Gemma 356/450; DeepSeek 348/450 Purist |

The historical DeepSeek full200 aggregate is `0.8566`, but its runtime metadata
is incomplete. It is retained for audit only and excluded from the paper-facing
model table.

## Wording the paper must avoid

- Do not describe ExECT full200 as an independent test split.
- Do not describe `clinical_headline` as the published strict benchmark.
- Do not describe the paper-derived development replay as reproduction of the
  original ExECT system or its 0.87/0.90 validation scores.
- Do not present internal annotation review as independent clinical validation.
- Do not claim cross-task transfer without a selected ExECT study.
- Do not present the GEPA run as a production reference.
- Do not erase hosted-versus-local route and reparse differences when describing the six-model panels.
- Do not describe the historical ExECT Prescription or Seizure Frequency
  columns as model-to-model results.
- Do not describe `v08` as satisfying the final model-led family contract.
- Do not promote the corrected aggregate candidates as final model rows. The
  architecture checks now exist, but deterministic correct-to-wrong counts are
  nonzero and the historical DeepSeek runtime metadata is incomplete.
- Do not turn Gan model-pass counts into measured token, dollar, energy, or
  latency savings.
- Do not describe the eight-criterion framework as one shared reliability
  metric or calculate a composite reliability score.
- Do not present the prepared ExECT semantic-support sample as reviewed
  evidence; all 48 review conclusions remain unset pending independent review.
- Do not describe the Gan matched-method development result as promotion over
  the rules-only comparator; the component audit retains substantial rules-
  correct regressions and incomplete changed-row evidence.
- Do not use prompt v0.7 for a primary Gan `llm_with_rules` score, ranking,
  reliability cell, development-to-test comparison, or paper claim. It is
  retained only as a historical prompt-interaction diagnostic.
- Do not mix prior-repair matched-panel scores with final-ruleset no-call
  replay scores in one ranking without naming both ruleset identities.
- Do not reopen Gan LLM-with-rules tuning for this comparison without a new
  predeclared study; the 2026-07-31 ruleset is final for current claims.
- Do not place ExECT all-nine rules-only metrics, GEPA LLM-only, or historical
  `v08` beside the Sol-matched primary three-method rows as if they were the
  same experiment. They are secondary or historical evidence.

## Open work

1. Keep the six-model claim bounded to the named fixed pipelines, aggregate
   test readouts, and recorded route differences.
2. Complete independent clinical review before any semantic-support or
   clinical-validity claim.
