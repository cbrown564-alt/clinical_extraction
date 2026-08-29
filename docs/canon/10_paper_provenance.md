# 10 — Paper claims and supporting evidence

Last updated: 2026-08-28

Living paper scores are the Gemini 3.7 Flash five-cell grids
([Gan](../research/gan2026/gan_five_cell_grid_2026-08-22.md),
[claims](../paper/claims.md)). Sol, current-stack hybrid fills, and
decision 0050 numbers in this file are historical. Do not cite them
as selected results.

This file states how strongly the paper may make each claim. The
[retained evidence index](../experiments/retained_evidence_manifest.md) records
the exact files and hashes. The [manuscript](../research/paper/manuscript_2026-06-26.md)
must not make a stronger claim than either source supports.

## Required paper statements

| ID | Statement | Current evidence | State |
| --- | --- | --- | --- |
| S1 | One modular package is evaluated on Gan and ExECT | Six selected runs replay from retained code and outputs | Partial |
| S2 | Rules, LLM, and mixed role rows have attributable results on both tasks | The selected comparison is the Gemini 3.7 Flash five-cell grid (rules, LLM, or both at find / encode / select); the cited score is the select stop. Sol-matched 2×3 and decision 0050 hybrid fills are historical | Bounded development answer |
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
| C10 | On the historical current-stack ExECT test60 hybrid panel, Gemini 3.7 Flash scored 0.8459, DeepSeek 0.8292, Sol 0.8289, Luna 0.8156, Qwen 0.7970, and Gemma 0.7415 clinical fact F1 | Aggregate test evidence | Internal scorer, 59 loadable test letters, no row inspection; 14 Aug no-call remasure through SF projection v0.14 (decision 0050); Gemini is the living successor cell (decision 0052); DeepSeek uses the selected 0731 raws; Sol is the historical Decision 0046 method-identity row; GPT-4.1-mini 0.7668 is historical 0039; not the published benchmark or clinical validation |
| C11 | On the historical matched Gan v0.5 test450 panel under the prior `hybrid_full_stack`, Sol scored 373/450, Luna and Qwen 362/450, GPT-4.1-mini 361/450, Gemma 355/450, and DeepSeek 344/450 Purist | Frozen aggregate evidence | Same v0.5 prompt and scorers; historical repair before the 2026-07-31 final ruleset; provider transport and temperature differ; some conditions use aggregate-only current-schema replay of sealed outputs |
| C12 | The fixed deterministic ExECT SF projection/suppression stage improves dev140 state-profile F1 for all six model conditions, with 54 wrong-to-correct and one correct-to-wrong transition across the six panels | Development component evidence | The same 140 letters are repeated for each model; the unknown-only denominator is zero, so this does not establish cross-task over-inference transfer or factuality prevalence |
| C13 | Gan 2026 and ExECTv2 are assessed with the same eight reliability questions using task-specific measures, explicit evidence states, and explicit comparability labels | Strong for the generated framework and selected retained evidence | The tasks do not share one metric; criterion evidence is uneven; construct-only and not-comparable values are not compared numerically; no composite score or clinical-validity claim |
| C14 | The historical v0.7 Gan dev750 panel shows a model-by-method interaction and supports component diagnostics, but it is not the selected primary six-model `llm_with_rules` result | Quarantined development diagnostic from twelve retained 750-row traces and a no-call replay | The selected v0.5 six-model dev750 panel is now complete; do not merge v0.7 rows or scores into its ranking, development-to-test comparison, or paper headline |
| C15 | On the historical matched Gan v0.5 dev750 panel under the prior `hybrid_full_stack`, GPT-4.1-mini scored 668/750, Qwen 660/750, Sol 656/750, Luna 646/750, Gemma 643/750, and DeepSeek 619/750 Purist | Reproduced development evidence from 4,500 unique row traces and a companion attribution artifact | Named models, routes, v0.5 prompt, historical repair, Gan scorers, and `gan2026_split_v1` validation rows only; not clinical validation, a model-neutral ranking, method promotion, or new holdout evidence |
| C16 | The selected Gan comparison is the Gemini 3.7 Flash five-cell on locked `test450` (select stop, Purist): rules 329/450 (0.73); both / rules / rules 368/450 (0.82); LLM / rules / rules 373/450 (0.83); LLM / LLM / rules 368/450 (0.82); LLM / LLM / LLM 357/450 (0.79). The 15 Aug current-stack panel (Sol 381, Gemini 374, Luna 366, DeepSeek 366, Qwen 361, Gemma 360) is historical. | Aggregate-only five-cell | Owner: `paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`. Do not cite Sol. `gan_llm_only` is not a results column. Not clinical validation. |
| C17 | The selected ExECT comparison is the Gemini 3.7 Flash five-cell on locked `test60` (select stop, 4-family inventory micro F1): rules 0.8018; both / rules / rules 0.8592; LLM / rules / rules 0.8674; LLM / LLM / rules 0.8636; LLM / LLM / LLM 0.853. Sol-matched 2×3 rows are historical. | Aggregate-only five-cell | Owner: `docs/paper/claims.md` and the Gemini inventory five-cell. Not the published ExECT benchmark. Not clinical validation. |
| C18 | On retained Gan and ExECT development hybrid surfaces, named deterministic stages account for the bulk of first label or inventory changes under ordered no-call replay: Gan evidence reconcile (`selected_evidence`); ExECT Diagnosis lens and SeizureFrequency `project_and_gate` | Bounded development answer | First-changer attribution on development ledgers only; not leave-one-stage-out necessity; not holdout generalization; does not rewrite C16 or Decision 0046 fills. Owners: 2026-08-06 Gan/ExECT stage ablations and cross-task synthesis |
| C19 | Deterministic correction is component-specific: Gan `repair.breakthrough` on unknown gold recovers under leave-one-family-out but costs full-ledger Purist; the prior ExECT v09 Prescription lens contained two harmful, dev-fitted rules whose removal produced v10 and improved aggregate-only test59 Prescription exactness `0.6591 → 0.7472` and micro-F1 `0.8286 → 0.8748` | Bounded holdout-confirmed simplification plus development residual evidence | The ExECT confirmation covers one frozen v09→v10 deletion bundle, six models, and aggregate-only test59; GPT-4.1-mini was marginally worse. It does not establish that all deterministic correction is harmful or revise C16 / C17 primary fills. Owners: Gan unknown-harm and breakthrough LOO; [ExECT decomposition](../research/exectv2/prescription_lens_rule_decomposition_2026-08-10.md); [ExECT holdout confirmation](../research/exectv2/prescription_lens_v10_holdout_confirmation_2026-08-10.md) |

## Selected headline results

| Task and method | Result |
| --- | ---: |
| Gan Gemini five-cell, test450, rules / rules / rules | 329/450 = 0.73 Purist (select stop) |
| Gan Gemini five-cell, test450, both / rules / rules | 368/450 = 0.82 Purist |
| Gan Gemini five-cell, test450, LLM / rules / rules | 373/450 = 0.83 Purist (cited cell 3) |
| Gan Gemini five-cell, test450, LLM / LLM / rules | 368/450 = 0.82 Purist |
| Gan Gemini five-cell, test450, LLM / LLM / LLM | 357/450 = 0.79 Purist |
| ExECT Gemini five-cell, test60, rules / rules / rules | 0.8018 4-family inventory micro F1 |
| ExECT Gemini five-cell, test60, both / rules / rules | 0.8592 |
| ExECT Gemini five-cell, test60, LLM / rules / rules | 0.8674 (cited cell 3) |
| ExECT Gemini five-cell, test60, LLM / LLM / rules | 0.8636 |
| ExECT Gemini five-cell, test60, LLM / LLM / LLM | 0.853 |
| Gan single-pass system, test450 (historical) | 364/450 Purist |
| Gan multi-model comparison, test450 | 379/450 Purist |
| ExECT rules only, dev140 | paper-derived macro item F1: phrase 0.5687, CUI 0.7144, all features 0.6020; strict micro item F1 0.3548 |
| ExECT historical Sol-matched rules-only, dev140 | clinical fact F1 0.8982 (2026-08-15 Investigations result-binding remasure); historical 2026-08-01 fill 0.8160 |
| ExECT historical Sol-matched rules-only, test60 | clinical fact F1 0.7918 (2026-08-15 Investigations result-binding remasure, aggregate-only); historical Decision 0046 fill 0.7154; 0.7123 post-commit 5e04dd61 temporal alignment (2026-08-11) |
| ExECT historical Sol LLM-only, `raw_lane_score`, dev140 | F1 0.8097 |
| ExECT historical Sol LLM-with-rules, one-call, dev140 | clinical fact F1 0.9032 |
| ExECT historical Sol LLM-with-rules, one-call, test60 | clinical fact F1 0.8289; aggregate-only |
| ExECT GEPA LLM only, dev140 | clinical fact F1 0.7393; historical/negative comparator |
| ExECT historical LLM with rules (`v08`), dev140 | clinical fact F1 0.9202 (superseded value 0.9189, pre the disclosed Diagnosis subsumption-guard fix, commit 41165adc, 2026-08-11); secondary development control, not the final decision-0040/0041 architecture |
| ExECT GPT / Qwen historical full200 rows | 0.8356 / 0.8197 clinical fact F1 |
| ExECT fixed six-model panel, test60 | Gemini 3.7 Flash 0.8459; DeepSeek 0.8292; Sol 0.8289; Luna 0.8156; Qwen 0.7970; Gemma 0.7415 clinical fact F1 |
| Gan matched six-model v0.5 panel, dev750 (prior repair) | GPT-4.1-mini 668/750; Luna 646/750; Sol 656/750; DeepSeek 619/750; Qwen 660/750; Gemma 643/750 Purist |
| Gan matched six-model v0.5 panel, test450 (prior repair) | GPT-4.1-mini 361/450; Luna 362/450; Sol 373/450; DeepSeek 344/450; Qwen 362/450; Gemma 355/450 Purist |
| Gan final LLM-with-rules no-call replay, dev750 | GPT-4.1-mini 677/750; Luna 660/750; Sol 660/750; Qwen 657/750; Gemma 647/750; DeepSeek 627/750 Purist |
| Gan historical current-stack LLM-with-rules panel, test450 | Sol 381/450; Gemini 3.7 Flash 374/450; Luna 366/450; DeepSeek 366/450 (0731 raws); Qwen 361/450; Gemma 360/450 Purist |
| Gan rules only (portable ruleset), test450 | 329/450 = 0.7311 Purist; 341/450 = 0.7578 Pragmatic; aggregate-only, zero model calls |

The historical DeepSeek full200 aggregate is `0.8566`, but its runtime metadata
is incomplete. It is retained for audit only and excluded from the paper-facing
model table.

## Wording the paper must avoid

- Do not describe ExECT full200 as an independent test split.
- Do not describe clinical fact recovery (`clinical_headline`) as the published
  strict benchmark.
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
  `v08` beside the Gemini five-cell rows as if they were the
  same experiment. They are secondary or historical evidence.
- Do not treat the 2026-08-06 hybrid mechanism ladder as a rewrite of C16
  Purist fills or Decision 0046 / C17 primary method numbers.
- Do not cite Sol, decision 0050 current-stack fills, the 1 Aug ExECT
  stage-panel Sol 0.8047, or Gan Sol 380/450 or 381/450 as living paper
  scores. The selected comparison is the Gemini 3.7 Flash five-cell.
- Do not claim leave-one-stage-out necessity from first-changer attribution
  alone, or generalize the confirmed v09→v10 Prescription deletion bundle to
  the current primary C16/C17 headlines. The test59 result is a bounded
  component confirmation, not a universal rule-removal claim.
- Do not present development category or stage effects as sealed holdout row
  competence; Gan a_priori holdout bucket scores remain blocked without
  sealed ledgers.

## Open work

1. Keep the six-model claim bounded to the named fixed pipelines, aggregate
   test readouts, and recorded route differences.
2. Complete independent clinical review before any semantic-support or
   clinical-validity claim.
3. Companion mechanism wording for C18/C19 is packaged in
   [claim-boundary packaging](../research/shared/paper_claim_boundary_hybrid_mechanism_c16_0046_2026-08-06.md);
   optional manuscript paste remains a later editing pass.
