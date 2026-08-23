# Gemini inventory cells 3–5 cite

Date: 2026-08-23
Status: completed 2026-08-23; promoted
Owner: this file
Track: [inventory](exect_llm_inventory_track.md)
Result owner: [cell 4](exect_rule_select_after_llm_encode_2026-08-22.md)

## Primary question

What are the cited Gemini inventory-F1 select stops for ExECT cells
3, 4, and 5 on the living `exect_llm_extract` raw?

## Why it matters

Cells 3–5 now sit on the inventory extract and
`clinical_inventory_unit_keys`. The Compact/headline five-cell numbers
(0.8161 / 0.8173 / 0.7954) are a different extract and scorer. The
paper owners still cite those.

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

Cells 1–2 stay the previous Compact/headline totals until a separate
inventory rescore. Do not mix those with inventory F1 without saying so.

## Candidate and comparator

- Candidate: living Gemini inventory extract, later-stage encode, and
  later-stage select, with inventory Select as the cell-3 and cell-4
  rule stop.
- Comparator: the Compact/headline five-cell grid still on disk.

## Stop rule

Answer when both splits have inventory-F1 select stops for cells 3–5,
those cells are promoted, and the paper owners cite them. Do not
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
