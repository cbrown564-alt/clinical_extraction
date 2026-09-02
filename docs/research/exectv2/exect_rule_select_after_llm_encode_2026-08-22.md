# ExECT rule-select-after-LLM-encode

Date: 2026-08-22
Revised: 2026-08-23 (inventory find and inventory Select)
Status: promoted into the cited ExECT five-cell table
Owner: [protocol](exect_gemini_inventory_cells_3_5_protocol_2026-08-23.md)
Artifact: `experiments/exectv2_rule_select_after_llm_encode_20260823/{split}/comparison.json`
Promoted copy: `paper_experiments/exect/exect_rule_select_after_llm_encode/gemini37flash/{split}/comparison.json`

## Paper table

ExECT uses the same five role rows as Gan. Each of find, encode,
and select is rules, LLM, or both. The cited score is the 4-family
micro F1 select stop. This study is **cell 4** (LLM / LLM / rules): saved
`exect_llm_extract`, later-stage `exect_llm_encode`, then inventory
Select. On this find it is **not** the peak Gemini inventory
row. The peak is cell 3 (`exect_llm_extract`, inventory Select).
Later-stage encode and select stay Gemini only. The Compact/headline
2026-08-22 totals (encode 0.8059 → select 0.8173) are retired.

## Answer

ExECT cell 4 exists on the inventory find. On the saved Gemini
later-stage encode ledger, inventory Select changes 4-family micro F1
from **0.8598 to 0.8585** on `dev140` and from **0.8649 to
0.8636** on locked `test60`. That holdout select stop is above
later-stage LLM select (**0.853**) and below cell 3 inventory
Select (**0.8674**).

No new model calls. Holdout rows were not inspected.

## Protocol

Gemini 3.7 Flash. Find is saved `exect_llm_extract`. Encode is
saved `exect_llm_encode`. Select is `INVENTORY_SELECT_RULE_IDS` on
those encoded mentions, using find mentions as the source
ledger.

## Component result

Exact 4-family micro F1 (`clinical_inventory_unit_keys`).

| Split | Encode stop | Cell 4 select | Select actions |
| --- | ---: | ---: | ---: |
| `dev140` | 0.8598 | **0.8585** | 6 |
| `test60` | 0.8649 | **0.8636** | 3 |

Locked `test60` family F1, encode → select: Diagnosis 0.81 → 0.81;
Investigations 0.92 → 0.92; Prescription 0.93 → 0.93;
SeizureFrequency 0.86 → 0.86.

Cited Gemini `test60` select stops on this find: cell 3
**0.8674**, cell 4 **0.8636**, cell 5 **0.853**.

## Claim boundary

Holdout evidence for this frozen replay. Aggregate only. Promoted as
cell 4 in the cited five role rows (select stop **0.86**). Not the
six-model roster row (cell 3). Not a six-model result. Do not inspect
`test60` rows. Do not retune Select rules from this total.

## Next

Done: `claims.md`, `README.md`, and
`paper_experiments/exect/five_cell_grid/gemini37flash/test60/comparison.json`
cite this stop.
