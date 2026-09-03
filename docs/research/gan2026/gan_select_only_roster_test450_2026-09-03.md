# Results: Six-model rule select without encode on Gan `test450`

Date: 2026-09-03
Protocol: [protocol](gan_select_only_roster_test450_protocol_2026-09-03.md)
Artifact: [aggregates](gan_select_only_roster_test450_2026-09-03.json)
Module: `clinical_extraction.paper.gan_select_only_roster`
Replay: `python scripts/measure_gan_select_only_roster.py`
Tests: `tests/test_gan_select_only_roster.py`
Model calls: 0. Holdout is aggregate-only.

## Question

What does living `llm_select_only` (rule decide, encode off) score on
each roster model's saved codebook extract, and how does that arm
separate encode from decide relative to Hybrid (Table 4) and
same-model LLM select (Table H1)?

## Answer

Rule select without encode **raises every model over find**. Encode's
extra lift at the Hybrid final stop is small for Gemini, Grok, and
DeepSeek (+0.011 to +0.018) and larger for Luna (+0.047) and the local
models (+0.022). Holding encode off, rule select and same-model LLM
select are within 0.002 Purist for Gemini, Grok, and Luna; rule select
is far above LLM select for DeepSeek (+0.035) and the locals (+0.087 /
+0.084).

| Model | Find | Encode stop | Rule select only | Hybrid (F) | LLM select (H) | Select alone | Encode at final | Rule − LLM (no encode) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gemini 3.7 Flash | 0.789 | 0.800 | **0.849** | 0.860 | 0.851 | +0.060 | +0.011 | −0.002 |
| Grok 4.6 | 0.789 | 0.811 | **0.838** | 0.853 | 0.840 | +0.049 | +0.015 | −0.002 |
| GPT-5.6 Luna | 0.693 | 0.738 | **0.742** | 0.789 | 0.744 | +0.049 | +0.047 | −0.002 |
| DeepSeek V4 Flash | 0.742 | 0.758 | **0.802** | 0.820 | 0.767 | +0.060 | +0.018 | +0.035 |
| Qwen 3.8 27B | 0.700 | 0.731 | **0.740** | 0.762 | 0.653 | +0.040 | +0.022 | +0.087 |
| Gemma 4 26B | 0.664 | 0.682 | **0.702** | 0.724 | 0.618 | +0.038 | +0.022 | +0.084 |

Purist micro-F1, n=450. Find / encode / Hybrid from Table 4. LLM select
from Table H1. Rule select only is this replay (`llm_select_only`,
including `last_event_well_since`). Gemini matches living cell 4
(**0.849**; 382/450). Pragmatic select-only: Gemini 0.869, Grok 0.873,
Luna 0.773, DeepSeek 0.838, Qwen 0.782, Gemma 0.751.

## Mechanism reading (aggregate)

1. **Most Hybrid lift is select, not encode**, except Luna, where
   encode supplies about half the Hybrid gain over find
   (+0.049 select-only, +0.047 encode-at-final).
2. **Locals still gain under rule select** (+0.038 / +0.040 vs find).
   Their collapse on Table H1 is an LLM-decide failure, not an extract
   ledger that rules cannot use.
3. **Executor contrast without encode** is near-zero for the three
   strongest extractors (Gemini / Grok / Luna) and large for DeepSeek
   and the laptop models.

## Reproduce

```bash
source .venv/bin/activate
python scripts/measure_gan_select_only_roster.py
python -m pytest tests/test_gan_select_only_roster.py -q
```

## Claim boundary

Repository / transfer decomposition only. Holdout aggregates only.
Not a paper row. Not a six-model roster change. Do not retune Table 1
or Table 4. Local models remain technical feasibility on synthetic
letters.
