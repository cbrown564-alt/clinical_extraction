# Promising But Guarded Avenues From Predecessor Repos

Date: 2026-06-27

Purpose: list ideas that may still be useful for `clinical_extraction/`, but only under fresh protocols and current evidence boundaries. These are not authorized tasks. They are backlog/future-work candidates with the historical evidence needed to understand why they are tempting and why they are risky.

## Current Boundary Before Any Avenue

Current `clinical_extraction/PROJECT_STATUS.md` states:

- no open Gan or ExECTv2 development task is authorized;
- ExECTv2 `clinical_headline` recovery is primary;
- strict benchmark/CUI results are diagnostic;
- Gan `test450` row-level inspection and post-test tuning are blocked;
- ExECTv2 full-200/holdout row-level inspection is blocked for development;
- review-routing promotion is blocked by failed aggregate validation and any retry needs dev140-only redesign plus fresh predeclaration.

Therefore every avenue below must start as future work, a validation/dev-only predeclaration, or a manuscript caveat. None should be implemented by quietly mining frozen holdout or full-200 row-level failures.

## A1. Post-Hoc Evidence Resolver For Compact Or Local Pipelines

Historical source: `dissertation-recursive/docs/60_final_clarification_results_report.md`

Evidence record:

- Date: 2026-05-13.
- Matrix: final clarification conditions over 40 ExECTv2 documents.
- Compact frontier baseline `FC01` (`gpt_5_4_mini`, clinician-facing H6fs):
  - medication-name F1 `0.904`;
  - seizure-type F1 `0.434`;
  - diagnosis accuracy `0.800`;
  - quote presence `0.000`.
- Evidence-resolved version `FC11` applied a resolver after `FC01` projection:
  - medication-name F1 stayed `0.904`;
  - seizure-type F1 stayed `0.434`;
  - collapsed seizure-type F1 stayed `0.598`;
  - diagnosis accuracy stayed `0.800`;
  - quote presence rose from `0.000` to `0.981`;
  - quote validity was `1.000`;
  - `152/157` values were resolved deterministically;
  - only `2` fallback model calls were needed;
  - `3` values remained ungrounded.
- Local `FC12` similarly preserved the `FC04` local accuracy profile while increasing quote presence to `0.980`.

Why it is promising:

It separates first-pass clinical selection from auditability. Earlier H7/D3 quote-rich architectures often harmed extraction; this result suggests grounding can be added later with less accuracy cost.

Why it is risky:

The predecessor result used a 40-document validation-style slice and old harness contracts. Current `clinical_extraction/` has its own evidence, clinical headline, and provenance architecture. A naive port could blur prediction-bearing selection with evidence recovery.

Safe protocol shape:

- dev/validation only;
- first-pass prediction frozen before resolver;
- resolver forbidden to change selected clinical facts unless explicitly tested as a separate semantic repair family;
- report quote presence, exact quote validity, support quality, unresolved rate, and fallback-call rate separately from extraction F1.

## A2. ExECTv2 Frequency Surface Repair, Not Direct Gan Port

Historical source: `dspy-extraction/docs/archive/experiments/synthesis/pre_component_pivot/prior_best_vs_current_best_reanalysis_20260521.md`

Evidence record:

- The reanalysis compared older best-config results with newer pipeline results.
- Older ExECT frequency values were weak: Qwen `0.342`, Gemini `0.237`.
- Later ExECT S4 frequency improved to GPT `45.7%` and Qwen `50.0%`.
- The report warned that ExECT frequency residuals are not the same as Gan residuals. ExECT frequency requires audited surfaces such as explicit rates, qualitative co-labels (`frequency increased`, `frequency decreased`, `infrequent`, `seizure free`), zero-rate labels, and retention of coexisting frequency facts.
- It recommended an ExECT-specific S4 frequency label-surface repair rather than a direct port of Gan temporal-candidate logic.

Why it is promising:

Seizure frequency is the cross-dataset bridge between Gan and ExECTv2, but the surface forms differ. A narrow surface repair could improve ExECTv2 frequency without reworking the whole clinical headline architecture.

Why it is risky:

Frequency repair can easily become benchmark-format engineering, semantic override, or frozen full-200 tuning. It also risks claiming transfer from Gan where the historical evidence says the error modes differ.

Safe protocol shape:

- dev140 or validation-only;
- predeclared frequency-heavy slice or hard-case panel;
- no full-200/holdout row-level inspection;
- fixed non-frequency fields with no material regression;
- explicit classification of every rule as format-only, clinical epilepsy, seizure-frequency, benchmark-formatting, or dataset-specific.

## A3. Canonical Format Port Onto Gan Temporal Candidates

Historical source: `dspy-extraction/docs/archive/experiments/synthesis/pre_component_pivot/prior_best_vs_current_best_reanalysis_20260521.md`

Evidence record:

- Older Gan v3 reported relaxed match `0.646`, strict `0.592`, and completed-doc relaxed `0.815`, but was timeout-confounded.
- Current temporal-candidates verify-repair architecture had stronger category metrics: Qwen monthly `65.8%`, Purist `75.5%`, Pragmatic `82.6`; GPT monthly `65.1%`, Purist `76.5%`, Pragmatic `84.2`.
- However, normalized-label exact remained lower: Qwen `0.554`, GPT `0.523`.
- The reanalysis suggested a controlled port: keep temporal candidates and LLM adjudication fixed, then reintroduce older v3/v5-style canonical format examples and guardrails.

Why it is promising:

It targets a narrow residual: exact/canonical label surface fidelity, not the whole clinical category decision. It also respects the lesson that temporal candidate architecture was useful.

Why it is risky:

The current Gan holdout is frozen. Any exact-label work must not learn from locked `test450`. Also, canonical-format pressure can reduce clinical category robustness if it makes the model overfit surface strings.

Safe protocol shape:

- validation-only cap-25 then 50/250 ladder;
- current temporal-candidates skeleton fixed;
- primary metric remains monthly/category performance or a predeclared exact residual metric;
- promote only if exact improves without Purist/Pragmatic/evidence regression;
- no locked-test row-level analysis.

## A4. Hard-Case Panels Instead Of More Broad Aggregate Runs

Historical sources:

- `dissertation-experiments/docs/gan_frequency_v3_error_analysis.md`
- `clinical_extraction/docs/design/gan2026_split_protocol.md`

Evidence record:

The Gan v3 error analysis produced a structured taxonomy of 104 misses from a validation run:

- `60/104` were timeouts, masking model quality;
- about `12` cases involved medication withdrawal or clusters where explicit "stable/no further events" text overrode the 6-month rule;
- `3` cases involved "year to date" phrases where January/February clinic dates meant the denominator was 1-2 months, not a year;
- `3` cluster-format cases kept one component but lost the full "cluster per period, seizures per cluster" form;
- `2` diary-counting cases summed only the most recent month rather than the full described window;
- `5` calendar-event cases defaulted to unknown despite enough month/event information for arithmetic;
- some "unknown" disagreements were clinically defensible because the gold used dataset-specific conventions such as `multiple = 3`.

Current Gan split protocol says broad validation250 aggregate runs are low-information near saturation unless they answer a predeclared targeted question. It recommends hard cases, validation hard slices, robustness panels, component stress, selective-action analysis, or frozen test generalization.

Why it is promising:

The failure taxonomy is much more actionable than another aggregate F1 run. Hard panels can test specific capabilities: calendar arithmetic, year-to-date windows, cluster assembly, evidence support, and 6-month threshold behavior.

Why it is risky:

Hard panels can become overfit if they are repeatedly tuned without a stop rule.

Safe protocol shape:

- panel categories fixed before model/prompt change;
- one or two examples per category used for design, held-out examples for evaluation;
- report category-level pass/fail, not only aggregate score;
- stop after a predeclared number of design cycles.

## A5. Model-Specific Prompt Profiles

Historical sources:

- `dissertation-experiments/docs/schema_ladder_sweep_findings.md`
- `dissertation-recursive/docs/50_synthesis_report.md`
- `dissertation-recursive/docs/53_multi_agent_phase_synthesis_gaps.md`

Evidence record:

- Schema ladder: no single model dominated all fields. Gemini led diagnosis at one step; GPT-5.4-mini showed normalization/temporality weaknesses; Qwen was consistent but slower; GPT-4.1-mini was configuration-sensitive in that sweep.
- The recursive synthesis found that few-shot examples had model-specific effects. H6fs improved qwen3.5:9b seizure F1 by `+6.1pp` but harmed gemma4:e4b by `-3.2pp`. At 27B scale, H6fs harmed Qwen3.6:27B medication by `-4.7pp`; Qwen3.6:35B tolerated it.
- The multi-agent gaps document warned that schema-rich specialist prompts would likely fail on models with schema-extension aversion, such as Gemma variants.

Why it is promising:

The final system could be more reliable if prompts and schema richness are matched to model behavior rather than treating one prompt as universal.

Why it is risky:

Model-specific prompts increase maintenance burden and can hide overfitting. They also make claims harder to compare unless the reason for each profile is explicit.

Safe protocol shape:

- choose one target field family and one model-specific failure mode;
- hold scorer, data slice, and projection fixed;
- compare minimal profile versus enriched profile for that model only;
- report model-specificity as a result, not as a generic improvement.

## A6. Retrieval Highlighting As Attention Priming

Historical sources:

- `dissertation-recursive/docs/50_synthesis_report.md`
- `dissertation-recursive/docs/53_multi_agent_phase_synthesis_gaps.md`
- `dissertation-recursive/docs/60_final_clarification_results_report.md`

Evidence record:

- Recursive synthesis reported Gan retrieval highlight with GPT-5.5 at Pragmatic F1 `0.840` on 50 documents, about one point below a `0.85` target and above non-retrieval baselines in that phase.
- The multi-agent gaps document emphasized that retrieval-highlight worked as attention priming, not replacement: retrieval-only scored `0.520`, far below retrieval-highlight.
- The final clarification matrix found retrieval highlighting did not improve the ExECT frontier on that 40-document slice: `FC20` matched `FC01` on medication-name F1 (`0.904`) but had lower seizure-type F1 (`0.416` versus `0.434`) and slightly lower benchmark quality (`0.707` versus `0.713`).

Why it is promising:

Retrieval highlighting may help span-salience tasks such as seizure frequency, temporality, or evidence localization, especially when the full letter remains available.

Why it is risky:

The ExECT final clarification result did not support retrieval highlighting as a general extraction improvement. Using retrieved spans instead of the full letter is especially risky.

Safe protocol shape:

- retrieval augments the full source, never replaces it;
- test on a targeted hard-slice where salience is the hypothesized bottleneck;
- include retrieval-only ablation to prove the instruction still matters;
- report evidence-support and extraction metrics separately.

## A7. One Fair ExECT Optimizer Baseline

Historical source: `dspy-extraction/docs/workstreams/optimizer/dspy_optimizer_vs_manual_engineering_audit_20260520.md`

Evidence record:

- The optimizer audit found that Gan had optimizer experiments, but ExECT had no optimizer infrastructure despite being the broader, harder task.
- It recommended wiring a minimal ExECT compile path only as a bounded probe: hosted GPT, LabeledFewShot with small `k`, fixed frozen bridges, and no validation re-tuning.
- It explicitly advised against resuming large GEPA or optimizer tuning by default.

Why it is promising:

A single fair optimizer baseline could close an ablation gap in the story: "manual policy/bridges were chosen because they were interpretable and effective, but was a simple optimizer baseline ever tried on ExECT?"

Why it is risky:

It could reopen an optimizer loop after the project has already reached closing evidence. It also risks optimizing to benchmark quirks unless the metric and bridge boundary are fixed.

Safe protocol shape:

- only if needed for dissertation-method completeness;
- no holdout/full-200 row-level inspection;
- compare to a frozen zero-shot or manually engineered validation control;
- stop after one bounded compile rung unless predeclared criteria justify more.

## A8. Agent-Assisted Review As A Controlled Process, Not A Source Of Truth

Historical sources:

- `dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_final_value_report_20260525.md`
- `dspy-extraction-cursor-pilot-artifacts/20260524T082000Z_mutation_test_report.md`

Evidence record:

- Cursor SDK final report concluded the SDK was useful for checklists, source maps, contradiction-finding, and focused leads, then retired it as an active dependency.
- Mutation pilot improved an enriched slice from `23/25` to `25/25` while leaving residual slice `24/30`; all `49/49` tests passed; the diff was rolled back and not promoted.

Why it is promising:

Parallel agent review can discover narrow leads, stale assumptions, and missing source links.

Why it is risky:

It creates plausible but unverified prose, can miss diffs, and can report runner success without substantive output.

Safe protocol shape:

- agent review produces a lead list only;
- every promoted claim must point to a primary artifact;
- mutation requires disposable worktree, clean state, tests, diff capture, and rollback;
- no direct edits to final manuscript or frozen protocols from generated drafts.

## A9. Clinical-Utility Companion Views For Strict-Benchmark Gaps

Historical sources:

- `dissertation-recursive/docs/33_gold_audit_synthesis.md`
- `dissertation-experiments/docs/primary_sweep_error_analysis.md`
- current `clinical_extraction/PROJECT_STATUS.md`

Evidence record:

- Gold audits showed strict benchmark metrics can penalize clinically reasonable behavior: split-dose prescriptions, temporally flat seizure-type annotations, CUI under-specification, and Gan seizure-free threshold inconsistency.
- Primary sweep error analysis showed ILAE-specific seizure labels were often clinically reasonable but benchmark-wrong; remapping coarse focal labels improved F1 by `+0.099` to `+0.140`.
- Current project status already names `clinical_headline` recovery as primary and strict benchmark/CUI as diagnostic.

Why it is promising:

Clinical-utility views can explain why a strict benchmark score is low without claiming the model failed clinically. They can also make deterministic projection/provenance more transparent.

Why it is risky:

Clinical companion views can be mistaken for benchmark wins. They must not be used to evade strict benchmark limitations.

Safe protocol shape:

- always pair strict metric with clinical view and evidence boundary;
- define exactly which disagreements are considered clinically acceptable;
- preserve examples as synthetic/paraphrased or artifact-linked, avoiding protected row-level holdout inspection;
- state that companion views support interpretation, not published-benchmark replacement.

## Current Absorption Status (2026-06-27)

Some of these avenues are already partly built in `clinical_extraction/`. This column prevents the packet from re-recommending shipped work or reading as more open than it is. Grounded against current modules, tests, and `PROJECT_STATUS.md`.

| Avenue | Status in `clinical_extraction/` (2026-06-27) |
| --- | --- |
| A1 Post-hoc evidence resolver | Partial — `core/evidence_validity_audit.py` and `experiments/reconcile_evidence_groundedness_registry.py` cover validity/groundedness; a dev-only resolver audit separating first-pass selection from grounding is the open part. |
| A2 ExECTv2 frequency surface repair | Open — locked surfaces; dev140-only and predeclared if reopened. |
| A3 Gan canonical-format port | Open — `test450` frozen; exact-label work must not learn from locked test. |
| A4 Hard-case panels | Partial — Gan generalization/adversary battery and the split protocol already favor hard slices over broad reruns. |
| A5 Model-specific prompt profiles | Open — not built; maintenance/overfit risk noted. |
| A6 Retrieval highlighting | Open — predecessor evidence already negative on the ExECT frontier; low priority. |
| A7 One fair ExECT optimizer baseline | Partial — GEPA from-scratch was run on ExECTv2 (`exectv2/gepa/`) as a bounded probe (negative-on-goal + length-penalty win), so "was an optimizer ever tried on the harder task?" is now partly answered. |
| A8 Agent-assisted review as controlled process | Absorbed as discipline — leads-only, primary-artifact promotion required. |
| A9 Clinical-utility companion views | Absorbed — `clinical_headline` primary plus clinical-utility companion docs already operationalize this. |

## Prioritization For A Future Backlog

If work reopens, the safest high-yield order is:

1. Documentation-only: use this packet to sharpen manuscript caveats and future work language.
2. Dev-only evidence resolver audit for compact/local outputs, if auditability remains a gap.
3. Dev-only ExECT frequency surface repair, only with a predeclared hard slice.
4. Validation-only Gan canonical-format port, only if exact-label residuals are still a meaningful paper gap.
5. One bounded ExECT optimizer baseline, only for dissertation-method closure.

Avoid:

- broad aggregate reruns after saturation;
- locked-test or full-200 row-level tuning;
- new multi-stage architectures without conditional error analysis;
- new agent/process infrastructure that does not reduce claim risk.
