# ExECTv2 Diagnosis resolution protocol

Date: 2026-07-14  
Status: complete development study; no candidate promoted  
Mode: development study  
Source commit: `6277796a0f4a8ee2afe793e6f1dd33a20c2e5ad2` with an existing dirty tree

## Primary question

Can the completed Diagnosis review be converted into two attributable
improvements without weakening the fixed benchmark contract: explicit
evaluation sensitivity for representation disagreements, and general clinical
extraction fixes for genuine method errors?

## Data and inspection policy

- Dataset: ExECTv2 2025 broad epilepsy phenotyping corpus.
- Development split: `dev140`; all row inspection and candidate development is
  restricted to these 140 letters.
- Test60 must not be read or used for tuning.
- Fixed audit substrate:
  `experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.jsonl`.
- Final completed review overlay source:
  `C:/Users/cbrow/Downloads/exectv2-diagnosis-review-2026-07-14 (1).json`.
- Final overlay SHA-256:
  `8744ca0af51a0c878dac995978502e0e342b619a44b3e555bf9ed4a3419bf7ac`.

The completed review contains 173 representation decisions, 72 extraction
errors, and one uncertain row. Pattern-assisted decisions remain project review
hypotheses rather than independent clinical adjudication.

## Fixed comparators and candidates

| Method | Fixed comparator | Candidate |
| --- | --- | --- |
| Rules only | Current deterministic all-nine dev140 replay | Shared Diagnosis boundary and named-type rules |
| LLM only | Retained GEPA GPT-4.1-mini saved output | One fixed GPT-4.1-mini Diagnosis-decomposer run with no clinical post-model repair |
| LLM with rules | Retained v08 dev140 saved output | Same raw saved output replayed through the shared deterministic candidate |

GEPA optimization remains closed. The LLM-only candidate is one fixed prompt
and model run, not a new optimizer search. If the configured runtime is not
available, the phase records the exact dependency and stops without inventing
results.

## Score and component policy

- Fixed primary score: current Diagnosis `concept_only` clinical-headline
  scorer. Gold and this scorer remain unchanged.
- Fixed secondary views: `concept_negation` and `concept_assertion`.
- New diagnostic views:
  - multiplicity-insensitive presence;
  - reviewed-equivalence sensitivity.
- Representation decisions may affect only the diagnostic sensitivity views.
- Deterministic candidate changes that alter selected clinical meaning are
  `clinical_epilepsy` rules and make a method LLM with rules when applied after
  a model call.
- Schema-only validation and mechanical formatting may remain in LLM only.

## Implementation slices

1. Freeze and merge the final review into a machine-readable mechanism ledger.
2. Implement the two sensitivity views and reproduce the fixed scores before
   interpreting them.
3. Implement shared deterministic clinical-boundary fixes with focused tests,
   replay rules only and v08, and count correct-to-wrong regressions.
4. Audit the rendered Diagnosis prompt, add only missing plain-language
   boundaries, and run the fixed LLM-only candidate if available.
5. Produce a component evidence comparison with score layers, changed-row
   direction, exact evidence, ablations, and a promotion decision.

## Required artifacts

- frozen final review overlay and SHA record;
- one-row-per-review-key mechanism ledger with decision provenance;
- sensitivity summary for all three fixed methods;
- deterministic candidate replay and ablation artifacts;
- LLM-only run record containing model, prompt digest, call mode, parse and call
  failures, and evidence validity;
- component comparison JSON and narrative result.

## Regression and stop rules

- The fixed score must reproduce before any sensitivity result is accepted.
- No candidate advances with an unexplained deterministic-correct to wrong
  regression, invalid changed-row evidence, or missing component ownership.
- Prefer a negative result to a row-specific rule catalogue.
- Stop the LLM phase if credentials, model access, or runtime configuration is
  absent; record the unblock condition and complete every no-call phase.
- Do not inspect test60. A development winner is not promoted or described as
  holdout evidence.

## Claim boundary

A positive result is a development answer for the named dev140 artifacts. It
may show that reviewed representation conventions change the measured
Diagnosis gap and that named components correct named development failures. It
cannot establish corrected gold, clinical validity, test60 performance,
holdout generalization, or a replacement production reference.

## Result

All five slices completed under the predeclared dev140 boundary.

| Architecture | Fixed baseline F1 | Conservative sensitivity F1 | Reviewed interpretation F1 | Candidate F1 | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Rules only | 0.8599 | 0.9344 | 0.9520 | 0.8926 | Keep boundary fixes as a development candidate |
| LLM only | 0.6861 | 0.8499 | 0.9056 | 0.6210 | Reject prompt v0.2 regression |
| LLM with rules | 0.8984 | 0.9789 | 0.9950 | 0.9034 | Keep deterministic fixes as a development candidate |

The rules boundary candidate resolves 21 reviewed rows, including 17 labelled
extraction errors, and creates one new residual. The broader residual
dictionary adds 30 new residuals for only 0.0059 additional F1, so it remains
an opt-in diagnostic and is rejected as the default. The hybrid candidate
resolves all three reviewed extraction errors that it changes and creates no
new residuals. All changed-row evidence is valid in the saved candidate
artifacts.

The one permitted LLM-only call used GPT-4.1-mini at temperature zero. It
completed 140/140 letters with no call or parse failures and evidence validity
1.0, but its fixed primary F1 fell by 0.0652. It used 948,978 tokens and the run
record reports a cost of $0.3352476. There was no tuning, retry, or clinical
post-model repair.

Machine-readable results are in
`experiments/exectv2_diagnosis_resolution_summary_dev140_20260714.json`,
`experiments/exectv2_diagnosis_sensitivity_dev140_20260714.json`, and
`experiments/exectv2_diagnosis_component_comparison_dev140_20260714.json`.
The narrative result is the
[Diagnosis component comparison](exectv2_diagnosis_component_comparison_2026-07-14.md).
Gold and the fixed scorer remain unchanged. Test60 was not read.
