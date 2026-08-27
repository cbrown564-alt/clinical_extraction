# ExECT rules-only inventory retune

Date: 2026-08-27
Status: accepted on development; cited holdout unchanged
Owner: this file
Report: [inventory retune](exect_rules_only_inventory_retune_2026-08-27.md)
Prior audit: [inventory retune audit](exect_rules_only_inventory_retune_audit_2026-08-27.md)

## Primary question

Can a recall-first extract plus the existing encode and inventory Select
rules raise standalone ExECT rules on `dev140` 4-family inventory F1
without regressing a letter/family the current extract gets exactly
right?

This matters because the cited rules cell still uses extract-then-dedupe
built for Compact collapse. Cell 3 already has the later-stage program.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Split | `dev140` only |
| Holdout | not loaded; cited `test60` 0.7725 unchanged |
| Calls | none |
| Comparator | current `extract_deterministic_all9` inventory score |
| Candidate | recall-first extract, then `apply_format_stack`, then inventory Select |
| Scorer | `clinical_inventory_unit_keys` |

## Independently switchable moves

1. Stop Investigations same-result collapse at extract. Keep the collapse
   as `selection.investigation_same_result_dedupe` (off in the accepted
   rules-only set).
2. Recognise heading aliases and qualifier-bearing Diagnosis surfaces,
   then run encode (`encoding.diagnosis_standard_name`) and inventory
   Select (`keep_source`, weak-episode drop, Rx rules).
3. Optionally emit rate-less SF anchors at extract and drop them at
   Select. Accept only if inventory SeizureFrequency does not fall.

## Stop rule

Accept a move when isolated inventory F1 rises, no exact letter/family
set regresses, and every action has source evidence. Reject a move that
harms an exact family or only redistributes FP/FN. Do not rewrite the
cited holdout cell.

## Claim boundary

Development mechanism only. Not a five-cell replacement.
