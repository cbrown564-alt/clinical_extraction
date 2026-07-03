# ExECTv2 LLM-vs-deterministic Rx comparator — Full-200 aggregate predeclaration

- Date: `2026-07-03`
- Status: frozen predeclaration before the full-200 LLM Rx comparator run
- Worktree at drafting: clean (dev140 comparator + A1-A3/D6-D8 committed)
- Owner: ExECTv2 workstream
- Split/scope: full-200 aggregate-only validation
- Row-inspection boundary: `aggregate_only_no_full200_or_holdout_row_level_inspection`

## Purpose

Produce the full-200 holdout comparator for the paper: run the best-possible
LLM-tuned Prescription extractor (the dev140-confirmed arm: canonical GEPA
instruction + probe #2 current-vs-future + probe #3 AED-only with the
emit-if-unsure safety clause) through the v08 assembly on all 200 letters and
report its aggregate clinical_headline against the deterministic producer.
This is comparison evidence justifying the deterministic Prescription lane
architecture, NOT a promotion attempt.

## Dev140 result (the basis for this run)

| Producer (dev140 Rx clinical_headline, v08 assembly) | F1 | P | R | TP/FP/FN |
| --- | ---: | ---: | ---: | --- |
| Deterministic pre-P7 (archived v08 manifest) | 0.9386 | 0.9502 | 0.9272 | 191/10/15 |
| **LLM-tuned (canonical + probe #2 + probe #3 + emit-if-unsure)** | **0.9526** | 0.9795 | 0.9272 | 191/4/15 |
| **Deterministic P7-fixed (production)** | **0.9615** | 0.9524 | 0.9709 | 200/10/6 |

The LLM-tuned extractor beats the deterministic pre-P7 baseline (+0.0140,
precision-driven: FP 10->4) but the deterministic P7-fixed producer beats the
LLM (+0.0089, recall-driven: TP 191->200). The two fixes target different
failure modes: the LLM fixes non-AED over-extraction (precision); the
deterministic P7 fix fixes multi-dose weight-context over-suppression (recall).

## Frozen contract

| Component | Value |
| --- | --- |
| LLM program | `RxLLMExtractor` (dspy.Predict(PrescriptionFactsSignature) with the tuned instruction) |
| Instruction | canonical GEPA Rx block + DELTA_2_CURRENT_VS_FUTURE + DELTA_3_AED_ONLY_WITH_FIX (emit-if-unsure) |
| Model | `openai/gpt-4.1-mini`, temperature 0.0, max_tokens 12000 |
| Cache | True (dev140 calls cached; full-200 will reuse cache for the 140 dev letters + ~60 fresh test calls) |
| Split | full-200 (`load_letters()`, n=200) |
| Call count | ~60 fresh calls (140 dev letters cached from the dev140 run) |
| Script | `scripts/run_exectv2_v08_rx_llm_vs_deterministic.py full200 --allow-non-dev140 --cache` |

## Frozen architecture (only Prescription differs from baseline)

| Component | Baseline | Treatment |
| --- | --- | --- |
| structured_key_family_event_ledger | 20260624 currentcode | unchanged |
| diagnosis_reconciler_v01 | 20260624 currentcode | unchanged |
| sf_union_arbitration_v08 | 20260624 currentcode | unchanged |
| **prescription_repair_v03** | **20260624 deterministic (pre-P7)** | **LLM-tuned extractor artifact** |
| investigations_arbitration_v02 | 20260624 currentcode | unchanged |

## Allowed aggregate outputs

- overall + per-family `clinical_headline` precision, recall, F1, TP, FP, FN
- call-failure and parse/schema-failure counts
- the LLM-vs-deterministic aggregate delta

## Forbidden outputs

- full-200 row-level failure tables, note text, evidence spans, or rationales
  tied to full-200 row identifiers
- threshold/prompt edits after seeing full-200 metrics
- per-family primary_metrics overwrite in the registry for the full-200 run
  (per the aggregate-only mandate; only the overall delta is reported)

## Acceptance

The full-200 LLM Rx number is reported as aggregate comparator evidence
alongside the deterministic full-200 number (0.8680 overall / 0.9278 Rx
P7-fixed). Both outcomes are publishable: if the LLM matches or beats
deterministic at full-200, that is a finding; if it underperforms, the
comparison quantifies the deterministic advantage.
