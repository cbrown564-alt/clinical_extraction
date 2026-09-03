# Results: Candidate-set recall for Gemini cells 3 and 5 on Gan `test450`

Date: 2026-09-03
Protocol: [protocol](gan_candidate_set_recall_test450_protocol_2026-09-03.md)
Artifact: [aggregates](gan_candidate_set_recall_test450_2026-09-03.json)
Split: `test450` aggregate-only. Zero model calls. No row inspection.

## Answer

Shared Gemini extract record (`gan_llm_extract`), Purist candidate-set
recall:

| Pool | Purist | Pragmatic |
| --- | ---: | ---: |
| **Extract record (primary)** | **381**/450 (**0.8467**) | 392/450 (0.8711) |
| Events only | 292/450 (0.6489) | 311/450 (0.6911) |
| Provisional alone | 355/450 (0.7889) | 365/450 (0.8111) |
| Encode pool (Hybrid decide input) | 380/450 (0.8444) | 391/450 (0.8689) |

Gates: cell 3 select **387**/450 and cell 5 select **383**/450 both
reproduced. Extract and encode parse failures **0**.

## Versus decide stops

| Cell | Decide Purist | vs extract-record pool |
| --- | ---: | --- |
| **3 Hybrid** | **387**/450 (0.8600) | Net **+6**; on 63 errors: **21** headroom / **42** recall-gap |
| **5 LLM-only** | **383**/450 (0.8511) | Net **+2**; on 67 errors: **24** headroom / **43** recall-gap |

Encode-pool residuals versus cell 3: **20** headroom / **43**
recall-gap on the same 63 wrong letters.

## Reading

- Stage-1 recall on holdout is **0.85** (381/450): gold is in the
  extract record most of the time.
- Events-only (0.65) understates that figure because event
  `raw_value` is source-near; the provisional codebook label often
  carries the Purist-correct form.
- Both decide executors sit at or slightly above the extract-record
  pool in aggregate. Residual headroom is small (**21** Hybrid,
  **24** LLM-only); recall gap dominates the remaining errors.
- This replaces the “candidate recall left to future work” gap with a
  measured stage-1 number. It is not a new Table 1 score.

## Claim boundary

Holdout aggregate-only stage-1 measurement for the shared Gemini
extract versus cited cells 3 and 5. No holdout row inspection. Not
permission to retune extract or decide from these residuals.
