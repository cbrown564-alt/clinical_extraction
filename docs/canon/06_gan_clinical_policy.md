# 06 — Gan 2026 results and holdout rules

Last updated: 2026-07-14

Gan 2026 asks for one current seizure-frequency label per letter.

- validation750 permits development and replay;
- test450 is locked and aggregate-only;
- a new holdout run requires a fixed protocol and explicit authority;
- test450 rows must not be inspected or used for tuning.

## Development comparison

| Method | Split | Purist result |
| --- | --- | ---: |
| Rules only | validation750 | 697/750 |
| LLM only | validation750 | 581/750 |
| LLM event extraction with deterministic normalization | validation750 | 661/748 rendered |

## Saved holdout results

| Method | Purist result | Limit |
| --- | ---: | --- |
| Single-pass event extractor | 364/450 | Saved aggregate |
| Multi-model comparison (`V12`) | 379/450 | Saved aggregate; source removed |

The multi-model report remains to support a quality-versus-cost comparison.
Calls, tokens, cost, latency, hardware, and cache use still need a matched study.
