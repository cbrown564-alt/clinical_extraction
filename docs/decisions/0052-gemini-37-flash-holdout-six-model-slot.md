# 0052: Gemini 3.7 Flash holdout cells replace the mini six-model slot

Date: 2026-08-13
Status: accepted
Amends: six-model hybrid slots implied by
[decision 0050](0050-current-stack-hybrid-primary-fills.md)
and [decision 0051](0051-gemini-37-flash-succeeds-gpt41mini-six-model-slot.md)
Does not change: Decision 0046 Sol method identity; rules-only or LLM-only fills

## Decision

The living six-model hybrid panel uses Gemini 3.7 Flash
(`reasoning_effort=low`) instead of GPT-4.1-mini. Holdout cells are
aggregate-only:

| Cell | Gemini 3.7 Flash hybrid |
| --- | ---: |
| ExECT `dev140` | clinical fact F1 **0.9079** |
| ExECT `test60` | clinical fact F1 **0.8472** |
| Gan `test450` | Purist **373/450 (0.8289)** |

Sol and decision 0050 fills are historical. The living comparison is
the Gemini 3.7 Flash five-cell (Gan `test450` cell 3 **373/450** is
the codebook-then-rules select stop, not a Sol hybrid fill). The
13 Aug Gemini ExECT cells were 0.8952 / 0.8375.

GPT-4.1-mini remains historical Decision 0039 evidence (`selected: false`
in `SOURCES.json`).

## Why

Decision 0051 changed the live roster. These holdout cells complete that
roster on the locked splits without inspecting rows.

## Claim boundary

Internal scorer. 59 loadable ExECT test letters. 450 Gan test rows. No row
inspection. Not the published ExECT benchmark. Not clinical validation.

## Owners

- Protocol:
  [holdout protocol](../research/shared/six_model_gemini37flash_holdout_protocol_2026-08-13.md)
- Historical current-stack fills: `experiments/current_stack/latest/fills.json`
- Sidecars: `experiments/current_stack/sidecars/{gan_test450,exect_test60}/gemini37flash.jsonl`
