# Gan 2026 Unknown-Frequency Ambiguity Panel

Date: 2026-06-15

This validation-only panel encodes six supervisor-discussed ambiguity cases as a parser/safety-gate contract. It makes no model calls, reads no locked test rows, and does not change the scorer.

## Summary

- Prompt version under development: `gan2026_fresh_evidence_reasoner_v0_6`
- Safety gate: `gan2026_fresh_evidence_safety_gate_v0_9`
- Panel pass: `6/6`
- Final labels: `{'2 per 2 month': 1, '2 per 5 month': 1, 'unknown': 4}`
- Ambiguity classes: `{'explicit_count_window': 2, 'last_event_only_unknown': 1, 'unknown_count_or_window': 3}`

## Cases

| Row | Supervisor label | Expected label | Ambiguity class | Passed | Policy reading |
| ---: | --- | --- | --- | --- | --- |
| 11272 | `unknown` | `unknown` | `last_event_only_unknown` | `True` | Last-event-only evidence should remain unknown. |
| 14454 | `2 per 2 month` | `2 per 2 month` | `explicit_count_window` | `True` | Explicit count plus usable follow-up can be frequency. |
| 14029 | `unknown` | `unknown` | `unknown_count_or_window` | `True` | Open-ended since-diet evidence lacks a denominator. |
| 13267 | `2 per 5 month` | `2 per 5 month` | `explicit_count_window` | `True` | Explicit period plus reported events can be frequency. |
| 14137 | `unknown` | `unknown` | `unknown_count_or_window` | `True` | Open-ended since-medication evidence lacks a denominator. |
| 11337 | `unknown` | `unknown` | `unknown_count_or_window` | `True` | Single provoked breakthrough event has unclear period. |

## Decision

The ambiguity-classification contract passes on the supervisor panel. This does not promote a holdout candidate; it gives the next validation-only live prompt run a hard-negative panel to satisfy before broad validation replay or any future frozen audit request.
