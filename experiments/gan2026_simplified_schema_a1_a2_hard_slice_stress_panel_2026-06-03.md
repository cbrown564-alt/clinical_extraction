# Gan 2026 Simplified-Schema A1/A2 Hard-Slice Stress Panel

Date: `2026-06-03`

This is a validation-cycle predeclaration for the simplified-schema lane. It fixes
the next stress surface before any broad validation50 comparison, model call, or
row-level tuning.

- JSON manifest:
  `experiments/gan2026_simplified_schema_a1_a2_hard_slice_stress_panel_2026-06-03.json`
- Split: `validation`
- Split manifest: `gan2026_split_v1`
- Candidate context: A1 `llm_only_simplified_selected_state_reasoner` versus A2
  `llm_only_sparse_operands_selected_state_reasoner` v1 boundary fix
- Claim language: validation-development stress-panel planning only; not a
  benchmark, holdout, production-policy, or broad validation result

## Decision

Run a fixed hard-slice stress panel before the A1 versus A2 validation50
comparison.

Rationale: A1 and A2 v1 both reached 23/25 on validation25. The remaining misses
are not random broad-surface noise: row 187 is interval/window selection, and row
278 is unresolved `multiple` handling. A2 v1 also specifically repaired boundary
behavior for rows 190 and 280. The next useful surface is therefore a fixed panel
that tests those mechanisms and adjacent known-risk families before spending a
broader validation50 pass.

Escalation gate: run validation50 only after the panel result names the specific
hypothesis being decided, such as "A2 operands improve compact high-rate parsing
without new unresolved-multiple regressions" or "A1 is safer on proxy/trigger
unknowns and A2 should be revised before broad escalation."

## Metrics

- `selected_evidence_exact`
- `selected_evidence_arithmetic_purist`
- `sparse_operand_adapter_purist`
- `selected_evidence_correct_to_sparse_operand_wrong`
- `boundary_failure_count`
- `structured_record_count`

## Slices

| Slice | Rows | Purpose | Failure to watch |
| --- | ---: | --- | --- |
| `interval_window_selection` | 3 | Select the current cadence/window phrase rather than an interval narrative or unrelated event count. | Evidence omits the cadence window or chooses interval/event-count wording that cannot be normalized. |
| `unresolved_multiple` | 3 | Preserve unresolved `multiple` wording when the evidence does not license a concrete count. | Adapter narrows `multiple` to one or another concrete count without textual permission. |
| `cluster_frequency_wording` | 3 | Keep cluster cadence separate from per-cluster seizure load. | Sparse operands over-numericize cluster cadence or promote vague cluster timing to a concrete seizure frequency. |
| `medication_or_proxy_rate` | 5 | Treat dose changes, adherence, triggers, and proxy percentages as context unless they directly state seizure-frequency rate. | Model converts medication dose, percent change, missed-dose trigger, or illness trigger into a seizure-frequency label. |
| `perimenstrual_only_window` | 4 | Keep perimenstrual-only windows unknown unless the text states an actual seizure count or cadence. | Model converts a bounded menstrual-risk window into a month/week seizure rate. |
| `compact_rate_notation` | 4 | Parse compact shorthand and high-rate notation when the seizure target is explicit. | Model misses compact notation such as `xfour/wk`, `qtwo-threewk`, or approximately `9/h`. |

## Rows

| Row | Gold | Reference | Slices | Why included |
| ---: | --- | --- | --- | --- |
| 187 | `1 per 7 to 9 day` | `every seven to nine days` | `interval_window_selection` | Known A1/A2 validation25 miss: selected an interval event count instead of the current cadence. |
| 278 | `multiple per week` | `multiple times in past week` | `unresolved_multiple` | Known A1/A2 validation25 miss: selected-evidence arithmetic narrowed unresolved `multiple` wording to `1 per week`. |
| 190 | `1 per 4 week` | `every 4 weeks` | `cluster_frequency_wording` | A2 v1 boundary-fix anchor for cluster cadence without per-cluster burden. |
| 280 | `multiple per day` | `multiple seizures in past day` | `unresolved_multiple` | A2 v1 boundary-fix anchor for unresolved `multiple` wording over a 24-hour window. |
| 338 | `multiple per month` | `many convulsions in past month` | `unresolved_multiple` | Validation25 A1 selected-evidence miss; tests many/multiple wording over a month window. |
| 4092 | `1 per 2 to 3 week` | `qtwo - threewk` | `interval_window_selection`, `compact_rate_notation` | Compact interval notation with a current frequency estimate. |
| 2245 | `7 to 8 per 3 week` | `about 7 to 8 seizures in the last three weeks` | `interval_window_selection` | Windowed interval count with range; tests count/window preservation. |
| 1706 | `multiple cluster per month, multiple per cluster` | `several focal seizures last month` | `cluster_frequency_wording` | Cluster-burden wording where the schema must keep cluster cadence and per-cluster load distinct. |
| 4771 | `unknown` | `clusters during certain weeks` | `cluster_frequency_wording` | Vague cluster timing should stay unknown rather than becoming a concrete rate. |
| 3507 | `unknown` | `Frequency reduced by 0.3 after dose increase` | `medication_or_proxy_rate` | Medication-response proxy value is not an absolute seizure-frequency rate. |
| 3512 | `unknown` | `Frequency increased by approx 20% after dose increase` | `medication_or_proxy_rate` | Percent change after medication dose increase should not become a frequency label. |
| 3532 | `unknown` | `Frequency increased by approx 20% after dose increase` | `medication_or_proxy_rate` | Diary/proxy percent-change wording with confounding night shifts; not an absolute rate. |
| 5996 | `unknown` | `Seizures with missed ASM doses` | `medication_or_proxy_rate` | Trigger/adherence context should not be normalized as a frequency. |
| 6029 | `unknown` | `Seizures during intercurrent illness` | `medication_or_proxy_rate` | Illness-trigger context should remain unknown without a rate. |
| 3468 | `unknown` | `Seizures happen when perimenstrual only (days -2 to +2)` | `perimenstrual_only_window` | Bounded risk window without count/cadence. |
| 3469 | `unknown` | `Seizures happen when perimenstrual only (days -3 to +3)` | `perimenstrual_only_window` | Perimenstrual-only window with peer corroboration but no actual rate. |
| 3482 | `unknown` | `Seizures happen when perimenstrual only (days -3 to +3)` | `perimenstrual_only_window` | Cyclical window language should not be treated as monthly seizure frequency. |
| 3493 | `unknown` | `Seizures happen when perimenstrual only (days -3 to +3)` | `perimenstrual_only_window` | Perimenstrual-only target for current-vs-trigger distinction. |
| 3940 | `4 per week` | `sz xfour/wk` | `compact_rate_notation` | Compact shorthand should parse to four per week when tied to current seizure burden. |
| 3949 | `4 per week` | `sz Xfour/wk` | `compact_rate_notation`, `perimenstrual_only_window` | Compact rate appears alongside perimenstrual exacerbation; selected state should preserve the explicit average rate. |
| 9815 | `multiple per day` | `Electrographic focal clonic frequent on EEG (approx 9/h)` | `compact_rate_notation` | Approximately 9 per hour is a compact high-rate notation tied to electrographic focal clonic events. |

## Next Experiment Unit

The next model-call unit should run A1 and A2 v1 over exactly these rows first,
recording each score layer separately. Do not use panel behavior to tune locked
test or to claim benchmark-comparable performance. If A2 introduces any
selected-evidence-correct to sparse-operand-wrong regression on this panel,
revise the sparse operand boundary policy before validation50.
