# Gemini inventory cells 3–5 cite

Date: 2026-08-23
Status: completed 2026-08-23; promoted
Owner: this file
Track: [inventory](exect_llm_inventory_track.md)
Result owner: [cell 4](exect_rule_select_after_llm_encode_2026-08-22.md)

## Primary question

What are the cited Gemini 4-family micro F1 select stops for ExECT
cells 3, 4, and 5 on the living `exect_llm_extract` raw?

## Why it matters

Cells 3–5 sit on the living extract and
`clinical_inventory_unit_keys` (4-family micro F1). Retired Compact/
headline select stops (0.8161 / 0.8173 / 0.7954) used
`exect_llm_extract_filtered` and `clinical_headline_unit_keys`. Do not
cite them as the paper grid.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Model | Gemini 3.7 Flash, living low |
| Extract | saved `exect_llm_extract` |
| Cell 3 | inventory Select (`INVENTORY_SELECT_RULE_IDS`) on that extract |
| Cell 4 | saved `exect_llm_encode`, then the same inventory Select |
| Cell 5 | saved `exect_llm_select` |
| Development | `dev140`, review permitted |
| Holdout | `test60`, aggregate only. Do not inspect rows. |
| Calls | none |
| Scorer | exact `clinical_inventory_unit_keys` |

Cells 1–2 cited totals are 4-family micro F1 in
[cells 1–2](exect_four_family_micro_f1_cells_1_2_protocol_2026-08-23.md)
(cell 1) and
[both-extract on inventory](exect_both_extract_on_inventory_protocol_2026-08-23.md)
(cell 2). Do not mix headline-collapse scores with this scorer.

## Candidate and comparator

- Candidate: living Gemini inventory extract, later-stage encode, and
  later-stage select, with inventory Select as the cell-3 and cell-4
  rule stop.
- Comparator: retired Compact/headline grid on disk (different extract
  and scorer).

## Stop rule

Answer when both splits have 4-family micro F1 select stops for cells
3–5, those cells are promoted, and the paper owners cite them. Do not
retune from holdout.

## Answer

No new calls. Cited Gemini inventory select stops:

| Cell | `dev140` | `test60` |
| --- | ---: | ---: |
| 3 inventory Select | 0.8877 | **0.8674** |
| 4 inventory Select after encode | 0.8585 | **0.8636** |
| 5 later-stage LLM select | 0.8527 | **0.853** |

Cell 3 extract is 0.8273 / 0.8491. Cell 4 encode is 0.8598 / 0.8649.
Cell 3 is the Gemini inventory peak.
