# ExECT LLM with rules is the cited hybrid row

Date: 2026-08-17
Status: current
Owner: [paper methods](../methods.md)

## Decision

The paper ExECT methods are ExECT rules, ExECT LLM only, and
ExECT LLM with rules:

| Method | Identity | Cite |
| --- | --- | --- |
| ExECT rules | `exect_rules` | four-family clinical fact F1 |
| ExECT LLM only | `exect_llm_only` | raw F1 |
| ExECT LLM with rules | `exect_llm_with_rules` | hybrid F1 |

The two promoted model methods are ExECT LLM only and ExECT LLM
with rules. They are different requests. The unrepaired output of
ExECT LLM with rules is not ExECT LLM only.

Full ledger (`exect_full_ledger`) is the only comparison/control
method when cited. It is not a headline paper method. Do not present
Full-ledger scores as peer columns. Grok has no Full ledger cell.

## Why

The paper should cite the methods we run. ExECT LLM with rules
keeps one structured call, then family repair. The living request
drops the example zoo and the non-seizure-frequency encoding rules,
and omits `letter_id` and `prompt_version`.

## Consequences

- New writing uses the names ExECT rules, ExECT LLM only, and
  ExECT LLM with rules. Cite hybrid F1 for LLM with rules and raw
  F1 for LLM only.
- Full ledger numbers stay as the named control when cited.
- Do not inspect `test60` rows.
- Do not invent Qwen numbers for either promoted model method.
- Tracked replay files live under `paper_experiments/`.

## Claim boundary

A paper-identity choice. Not clinical validation and not the
published ExECT benchmark. Holdout cells are aggregate-only.
