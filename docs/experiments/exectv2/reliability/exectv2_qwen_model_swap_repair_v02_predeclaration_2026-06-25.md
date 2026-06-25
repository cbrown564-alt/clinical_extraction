# ExECTv2 Qwen Same-Core Repair v02 Predeclaration

- Predeclared: `2026-06-25`
- Candidate id: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140`
- Baseline comparator: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v01_dev140`
- Model/runtime: `ollama_chat/qwen3.6:35b` / `ollama_chat_think_false`
- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Split/scope: dev140 only
- Row inspection boundary: dev140 row-level inspection allowed; no full-200 or holdout row-level inspection
- Frozen-core rule: live model-owned components remain `structured_key_family_event_ledger` and `diagnosis_decomposer`; deterministic SF projection/unknown suppression/union, Prescription repair, lenses, views, scorer, row count, and gold loader remain unchanged.

## Repair Under Test

This is a Qwen-specific output-contract repair, not a clinical architecture
change. It keeps all v01 repairs and adds two schema-bound adapter repairs:

1. Parser repair may accept format-preserving JSON dialect drift already
   accepted in v01: Python-literal dict/list syntax, literal control characters
   inside strings, top-level list coercion, and DSPy adapter-payload recovery.
2. The Qwen compact prompt profile remains allowed for the structured producer
   and Diagnosis decomposer, with no change to event families, lenses, scorer,
   or deterministic replay components.
3. Structured producer parsing may drop a `clinical_events` item whose `family`
   is outside the declared event-family enum
   (`medication | diagnosis | seizure_frequency | investigation`). This repair
   may not coerce the family or preserve that event's mentions. It must log the
   dropped family, for example `dropped_unknown_event_family: ... family='diabetes'`.
4. Structured producer parsing may blank malformed non-scored `rationale` fields
   when Qwen leaks verbose reasoning that breaks JSON. This repair may not alter
   `family`, `anchor_text`, `evidence`, `event_state`, `mentions`,
   `confidence`, or any scored attribute. It must log
   `json_dialect_repaired: stripped_non_scored_rationale`.

The repair may not introduce clinical facts, reinterpret an out-of-contract
family as an in-contract family, or modify scored event/mention content beyond
existing schema compatibility coercions and evidence validation.

## Promotion Gates

The repaired Qwen dev140 row passes for operational inclusion only if all gates
hold:

- Architecture parity: same frozen core and component graph as the baseline
  model-swap configs.
- Operational stability: `0` call failures and `0` blocking parse/schema
  failures across the completed dev140 assembly row.
- Evidence validity: minimum exact evidence rate remains `>=0.99`.
- Clinical non-regression: overall clinical-headline F1 is at least the
  baseline Qwen `0.8018`, and SeizureFrequency F1 is at least baseline `0.6919`.

If operational stability passes but clinical-headline or SeizureFrequency falls
below baseline, keep the repaired row diagnostic only. If operational stability
fails, keep Qwen diagnostic-only and do not include it in the next full-200
candidate set.

## Reporting

Report:

- call failures and blocking parse/schema failures before and after repair
- counts and examples of dropped unknown event families
- counts of stripped non-scored rationale repairs
- overall and family clinical-headline F1
- whether Qwen is eligible for the next same-core full-200 aggregate-only
  predeclaration
