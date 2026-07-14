# 08 — GEPA negative comparator

Last updated: 2026-07-14

The retained ExECT LLM-only cell is one GEPA-optimized GPT-4.1-mini program on
dev140.

| Measure | Result |
| --- | ---: |
| `clinical_headline` F1 | 0.7393 |
| Strict benchmark item F1 | 0.1356 |
| Hybrid v08 headline F1 | 0.9189 |

This is a negative development comparator. It used an optimizer-only development
sub-split and is not a benchmark-cleared or production result.

The retained package contains the exact instruction, predictions, summary,
entry point, metric, adapter, scorer, and tests. Other GEPA variants and their
launchers were removed because they are not needed to replay this cell.

Do not claim that LLM-only matches the hybrid or that the historical GEPA search
establishes a universal model ceiling.

