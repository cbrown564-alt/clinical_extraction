# ExECTv2 GPT-4.1-mini Simplification Frontier

- Generated: `2026-06-24`
- JSON: `experiments/exectv2_gpt41mini_simplification_frontier_20260624.json`
- Row inspection policy: `aggregate_only_no_full200_failure_ledgers`
- Model calls during this frontier build: `False`
- Claim boundary: Authorized full-200 aggregate-only current-code GPT-4.1-mini simplification frontier. Candidate rows preserve provenance, but promotion decisions use aggregate metrics only.

## Recommendation

- Recommended lean architecture: `exectv2_holistic_finding_assembly_full200_gpt41mini_3call_dxdecomposer_sfadjudicator`
- Calls per letter: `3.0`
- Rationale: lowest-call candidate that satisfies the overall clinical-headline floor and all family guardrails

## Frontier Table

| Candidate | Calls / letter | Full-200 calls | Overall | Dx | SF | Presc | Inv | Pass/fail | Recommended? |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `exectv2_holistic_finding_assembly_full200_gpt41mini_3call_dxdecomposer_sfadjudicator` | 3 | 600 | 0.8426 | 0.8397 | 0.7850 | 0.8926 | 0.8563 | pass | yes |
| `exectv2_gpt41mini_simplification_2call_no_dx_decomposer` | 2 | 400 | 0.8144 | 0.7643 | 0.7850 | 0.8926 | 0.8563 | fail | no |
| `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator` | 2 | 400 | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 | fail | no |
| `exectv2_gpt41mini_simplification_1call_structured_direct_plus_deterministic_prescription` | 1 | 200 | 0.7730 | 0.7597 | 0.6114 | 0.8926 | 0.8563 | fail | no |
| `exectv2_gpt41mini_simplification_1call_structured_only` | 1 | 200 | 0.7571 | 0.7597 | 0.6114 | 0.8219 | 0.8563 | fail | no |

## Interpretation

The frontier treats `clinical_headline` de-duplicated clinical recovery as the primary surface. Strict benchmark/CUI scores stay diagnostic and are not used for the recommendation.

No full-200 row-level failure ledger was generated or inspected. The assembly JSONL files are provenance-preserving candidate outputs, not development error-analysis ledgers.
